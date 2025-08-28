"""
Serviço de Autenticação Mock (para testes e demonstração)
"""
import os
from enum import Enum
from typing import Optional, Dict, Any, List
import jwt
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """Níveis de acesso do sistema"""
    ADMIN = "admin"              # Administrador - acesso total
    DIRETORIA = "diretoria"     # Diretoria - dashboards executivos
    CS_CX = "cs_cx"             # Customer Success/Experience
    FINANCEIRO = "financeiro"    # Departamento Financeiro 
    VENDAS = "vendas"           # Equipe de Vendas
    DATAOPS = "dataops"         # Operações de Dados/Analytics

class MockAuthService:
    """Serviço de autenticação mock para demonstração"""
    
    def __init__(self):
        self.jwt_secret = os.getenv("SECRET_KEY", "hubcontrol-secret-key-change-in-production")
        
        # Usuários de demonstração
        self.demo_users = {
            "admin@hubcontrol.com": {
                "password": "admin123",
                "id": "demo-admin-id",
                "full_name": "Administrador Sistema", 
                "role": UserRole.ADMIN
            },
            "diretoria@hubcontrol.com": {
                "password": "123456",
                "id": "demo-diretoria-id",
                "full_name": "Diretor Geral",
                "role": UserRole.DIRETORIA
            },
            "cs@hubcontrol.com": {
                "password": "123456", 
                "id": "demo-cs-id",
                "full_name": "Gerente CS/CX",
                "role": UserRole.CS_CX
            },
            "vendas@hubcontrol.com": {
                "password": "123456",
                "id": "demo-vendas-id", 
                "full_name": "Gerente Vendas",
                "role": UserRole.VENDAS
            },
            "financeiro@hubcontrol.com": {
                "password": "123456",
                "id": "demo-financeiro-id",
                "full_name": "Gerente Financeiro", 
                "role": UserRole.FINANCEIRO
            },
            "dataops@hubcontrol.com": {
                "password": "123456",
                "id": "demo-dataops-id",
                "full_name": "Analista DataOps",
                "role": UserRole.DATAOPS
            }
        }
    
    def sign_up(self, email: str, password: str, full_name: str, role: UserRole = UserRole.CS_CX) -> Dict[str, Any]:
        """Registra novo usuário no sistema"""
        return {
            "success": True,
            "user": {
                "id": "new-user-id",
                "email": email,
                "full_name": full_name,
                "role": role.value,
                "permissions": self._get_role_permissions(role)
            },
            "message": "Usuário criado com sucesso (modo demonstração)"
        }
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Fazer login do usuário"""
        try:
            # Verificar se é um usuário de demonstração
            if email in self.demo_users:
                user_info = self.demo_users[email]
                
                # Verificar senha
                if password == user_info["password"]:
                    role = user_info["role"]
                    
                    # Criar JWT token
                    token_data = {
                        "user_id": user_info["id"],
                        "email": email,
                        "role": role.value,
                        "exp": datetime.utcnow() + timedelta(hours=24),
                        "iat": datetime.utcnow()
                    }
                    
                    access_token = jwt.encode(token_data, self.jwt_secret, algorithm="HS256")
                    
                    return {
                        "success": True,
                        "access_token": access_token,
                        "token_type": "Bearer",
                        "expires_in": 86400,
                        "user": {
                            "id": user_info["id"],
                            "email": email,
                            "full_name": user_info["full_name"],
                            "role": role.value,
                            "permissions": self._get_role_permissions(role)
                        }
                    }
            
            return {"success": False, "message": "Credenciais inválidas"}
                
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return {"success": False, "message": "Erro ao fazer login"}
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verificar e decodificar token JWT"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            
            # Verificar se o usuário ainda existe
            email = payload.get("email")
            if email in self.demo_users:
                user_info = self.demo_users[email]
                role = user_info["role"]
                
                return {
                    "valid": True,
                    "user": {
                        "id": user_info["id"],
                        "email": email,
                        "full_name": user_info["full_name"],
                        "role": role.value,
                        "permissions": self._get_role_permissions(role)
                    }
                }
            else:
                return {"valid": False, "message": "Usuário não encontrado"}
                
        except jwt.ExpiredSignatureError:
            return {"valid": False, "message": "Token expirado"}
        except jwt.InvalidTokenError:
            return {"valid": False, "message": "Token inválido"}
        except Exception as e:
            logger.error(f"Erro ao verificar token: {e}")
            return {"valid": False, "message": "Erro interno"}
    
    def list_users(self) -> List[Dict[str, Any]]:
        """Listar todos os usuários"""
        users = []
        for email, info in self.demo_users.items():
            users.append({
                "id": info["id"],
                "email": email,
                "full_name": info["full_name"],
                "role": info["role"].value,
                "permissions": self._get_role_permissions(info["role"])
            })
        return users
    
    def update_user_role(self, user_id: str, new_role: str) -> Dict[str, Any]:
        """Atualizar papel do usuário"""
        return {"success": True, "message": "Papel atualizado com sucesso (modo demonstração)"}
    
    def deactivate_user(self, user_id: str) -> Dict[str, Any]:
        """Desativar usuário"""
        return {"success": True, "message": "Usuário desativado com sucesso (modo demonstração)"}
    
    def _get_role_permissions(self, role: UserRole) -> Dict[str, Any]:
        """Obter permissões baseadas no papel"""
        permissions_map = {
            UserRole.ADMIN: {
                "modules": ["dashboard", "clientes", "vendas", "contratos", "health_score", "csat", "ml_churn", "usuarios"],
                "actions": ["create", "read", "update", "delete", "manage_users"],
                "data_access": "all"
            },
            UserRole.DIRETORIA: {
                "modules": ["dashboard", "clientes", "vendas", "contratos", "health_score", "csat", "ml_churn"],
                "actions": ["create", "read", "update", "delete"],
                "data_access": "all"
            },
            UserRole.CS_CX: {
                "modules": ["dashboard", "clientes", "health_score", "csat"],
                "actions": ["create", "read", "update"],
                "data_access": "department"
            },
            UserRole.FINANCEIRO: {
                "modules": ["dashboard", "clientes", "contratos"],
                "actions": ["create", "read", "update"],
                "data_access": "department"
            },
            UserRole.VENDAS: {
                "modules": ["dashboard", "clientes", "vendas"],
                "actions": ["create", "read", "update"],
                "data_access": "department"
            },
            UserRole.DATAOPS: {
                "modules": ["dashboard", "ml_churn", "clientes"],
                "actions": ["create", "read", "update"],
                "data_access": "department"
            }
        }
        
        return permissions_map.get(role, {
            "modules": [],
            "actions": [],
            "data_access": "none"
        })

# Instância global do serviço
auth_service = MockAuthService()