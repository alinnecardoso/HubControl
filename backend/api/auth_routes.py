"""
Rotas de Autenticação
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import logging

from services.auth_simple_mock import auth_service, UserRole

logger = logging.getLogger(__name__)
security = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Modelos Pydantic
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Optional[str] = "cs_cx"

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class UpdateRoleRequest(BaseModel):
    user_id: str
    new_role: str

# Dependência para autenticação
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Extrai e valida usuário atual do token JWT"""
    token = credentials.credentials
    result = auth_service.verify_token(token)
    
    if not result or not result.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    
    user_data = result["user"]
    return {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "role": user_data["role"],
        "full_name": user_data["full_name"],
        "permissions": user_data["permissions"]
    }

async def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Verifica se o usuário atual é administrador"""
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    return current_user

# Rotas públicas
@router.post("/signup")
async def sign_up(request: SignUpRequest):
    """Registro de novo usuário"""
    try:
        # Validar papel
        valid_roles = [role.value for role in UserRole]
        if request.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Papel inválido. Opções: {valid_roles}"
            )
        
        role = UserRole(request.role)
        result = auth_service.sign_up(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            role=role
        )
        
        if result["success"]:
            return {
                "message": result["message"],
                "user": result["user"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro no signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/signin")
async def sign_in(request: SignInRequest):
    """Login do usuário"""
    try:
        result = auth_service.sign_in(request.email, request.password)
        
        if result["success"]:
            return {
                "access_token": result["access_token"],
                "token_type": result["token_type"],
                "expires_in": result["expires_in"],
                "user": result["user"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no signin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

# Rotas protegidas
@router.get("/me")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Informações do usuário atual"""
    user_profile = auth_service.get_user_profile(current_user["user_id"])
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil não encontrado"
        )
    
    return {
        "user": {
            "id": user_profile["id"],
            "email": user_profile["email"],
            "full_name": user_profile["full_name"],
            "role": user_profile["role"],
            "is_active": user_profile["is_active"],
            "last_login": user_profile.get("last_login"),
            "permissions": auth_service._get_role_permissions(user_profile["role"])
        }
    }

@router.get("/validate-token")
async def validate_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Valida token atual"""
    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "role": current_user["role"]
    }

@router.get("/test-auth")
async def test_auth(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Teste de autenticação"""
    logger.info(f"Test auth endpoint called by: {current_user}")
    return {
        "message": "Authentication working",
        "user": current_user
    }

# Rotas administrativas
@router.get("/users")
async def list_users(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """Lista todos os usuários (apenas admins)"""
    try:
        users = auth_service.list_users()
        return {"users": users}
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar usuários"
        )

@router.put("/users/role")
async def update_user_role(
    request: UpdateRoleRequest,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Atualiza papel do usuário (apenas admins)"""
    try:
        # Validar papel
        valid_roles = [role.value for role in UserRole]
        if request.new_role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Papel inválido. Opções: {valid_roles}"
            )
        
        new_role = UserRole(request.new_role)
        result = auth_service.update_user_role(
            user_id=request.user_id,
            new_role=new_role,
            admin_user_id=admin_user["user_id"]
        )
        
        if result["success"]:
            return {"message": result["message"]}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Desativa usuário (apenas admins)"""
    result = auth_service.deactivate_user(
        user_id=user_id,
        admin_user_id=admin_user["user_id"]
    )
    
    if result["success"]:
        return {"message": result["message"]}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

@router.get("/roles")
async def get_available_roles():
    """Lista papéis disponíveis no sistema"""
    roles = [
        {
            "value": role.value,
            "name": role.value.replace("_", "/").upper(),
            "description": {
                "admin": "Administrador - Acesso total ao sistema",
                "diretoria": "Diretoria - Dashboards executivos e relatórios",
                "cs_cx": "Customer Success/Experience - Gestão de clientes",
                "financeiro": "Financeiro - Contratos e dados financeiros",
                "vendas": "Vendas - Pipeline e oportunidades",
                "dataops": "DataOps - Análises e operações de dados"
            }[role.value]
        }
        for role in UserRole
    ]
    
    return {"roles": roles}