"""
Role-Based Access Control (RBAC) Middleware
"""
from fastapi import HTTPException, status
from functools import wraps
from typing import List, Callable, Dict, Any
import logging

from services.auth_simple_mock import UserRole

logger = logging.getLogger(__name__)

class RBACMiddleware:
    """Middleware para controle de acesso baseado em papéis"""
    
    @staticmethod
    def require_roles(allowed_roles: List[UserRole]):
        """Decorator para exigir papéis específicos"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Buscar current_user nos kwargs (injetado pela dependência)
                current_user = kwargs.get("current_user")
                
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Usuário não autenticado"
                    )
                
                user_role = current_user.get("role")
                allowed_role_values = [role.value for role in allowed_roles]
                
                if user_role not in allowed_role_values:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Acesso negado. Papéis permitidos: {allowed_role_values}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def require_permissions(required_permissions: List[str]):
        """Decorator para exigir permissões específicas"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                current_user = kwargs.get("current_user")
                
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Usuário não autenticado"
                    )
                
                user_permissions = current_user.get("permissions", {})
                user_actions = user_permissions.get("actions", [])
                
                missing_permissions = [perm for perm in required_permissions if perm not in user_actions]
                
                if missing_permissions:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permissões insuficientes. Necessário: {missing_permissions}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def require_module_access(module_name: str):
        """Decorator para exigir acesso a módulo específico"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                current_user = kwargs.get("current_user")
                
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Usuário não autenticado"
                    )
                
                user_permissions = current_user.get("permissions", {})
                allowed_modules = user_permissions.get("modules", [])
                
                if module_name not in allowed_modules:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Acesso negado ao módulo: {module_name}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator

class DataAccessFilter:
    """Filtro de dados baseado no nível de acesso do usuário"""
    
    @staticmethod
    def filter_client_data(data: List[Dict[str, Any]], user_role: str) -> List[Dict[str, Any]]:
        """Filtra dados de clientes baseado no papel do usuário"""
        if user_role == UserRole.ADMIN.value or user_role == UserRole.DIRETORIA.value:
            return data  # Acesso completo
        
        elif user_role == UserRole.CS_CX.value:
            # CS/CX pode ver todos os clientes, mas sem dados financeiros sensíveis
            filtered_data = []
            for client in data:
                filtered_client = client.copy()
                # Remove campos financeiros sensíveis
                filtered_client.pop("receita_total", None)
                filtered_client.pop("margem_lucro", None)
                filtered_data.append(filtered_client)
            return filtered_data
        
        elif user_role == UserRole.VENDAS.value:
            # Vendas vê apenas clientes em pipeline ou prospects
            return [client for client in data if client.get("status") in ["prospect", "pipeline", "ativo"]]
        
        elif user_role == UserRole.FINANCEIRO.value:
            # Financeiro vê todos os dados financeiros mas informações limitadas de contato
            filtered_data = []
            for client in data:
                filtered_client = client.copy()
                # Remove informações pessoais sensíveis
                filtered_client.pop("telefone_pessoal", None)
                filtered_client.pop("observacoes_internas", None)
                filtered_data.append(filtered_client)
            return filtered_data
        
        else:
            # Acesso limitado para outros papéis
            return [{"id": client["id"], "nome": client["nome"], "status": client["status"]} 
                   for client in data]
    
    @staticmethod
    def filter_financial_data(data: List[Dict[str, Any]], user_role: str) -> List[Dict[str, Any]]:
        """Filtra dados financeiros baseado no papel do usuário"""
        if user_role in [UserRole.ADMIN.value, UserRole.DIRETORIA.value, UserRole.FINANCEIRO.value]:
            return data  # Acesso completo a dados financeiros
        
        elif user_role == UserRole.VENDAS.value:
            # Vendas vê apenas valores de contratos, não custos
            filtered_data = []
            for item in data:
                filtered_item = {
                    "id": item["id"],
                    "cliente_id": item["cliente_id"],
                    "valor_contrato": item.get("valor_contrato"),
                    "status": item.get("status")
                }
                filtered_data.append(filtered_item)
            return filtered_data
        
        else:
            # Outros papéis não têm acesso a dados financeiros detalhados
            return []
    
    @staticmethod
    def can_access_ml_operations(user_role: str) -> bool:
        """Verifica se o usuário pode acessar operações de ML"""
        return user_role in [UserRole.ADMIN.value, UserRole.DATAOPS.value, UserRole.DIRETORIA.value]
    
    @staticmethod
    def can_manage_users(user_role: str) -> bool:
        """Verifica se o usuário pode gerenciar outros usuários"""
        return user_role == UserRole.ADMIN.value

# Instâncias dos middlewares
rbac = RBACMiddleware()
data_filter = DataAccessFilter()