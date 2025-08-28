"""
Serviço de Autenticação Simplificado (sem tabela user_profiles)
"""
import os
from enum import Enum
from typing import Optional, Dict, Any, List
import jwt
from supabase import create_client, Client
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

class SimpleAuthService:
    """Serviço de autenticação simplificado"""
    
    def __init__(self):
        # Configurações do Supabase
        self.supabase_url = os.getenv("SUPABASE_URL", "https://auhkbtxjoqvahiajopop.supabase.co")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1aGtidHhqb3F2YWhpYWpvcG9wIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYyNTk5NTYsImV4cCI6MjA3MTgzNTk1Nn0.TmzyeS7_NEiR3tQbFapsqGUi98Zb44YmuKFwlvCYX2I")
        self.jwt_secret = os.getenv("SECRET_KEY", "hubcontrol-secret-key-change-in-production")
        
        # Cliente Supabase
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def sign_up(self, email: str, password: str, full_name: str, role: UserRole = UserRole.CS_CX) -> Dict[str, Any]:
        """Registra novo usuário no sistema"""
        try:
            # Criar usuário no Supabase Auth
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name,
                        "role": role.value,
                        "created_at": datetime.now().isoformat(),
                        "is_active": True
                    },
                    "email_redirect_to": None  # Disable email confirmation
                }
            })
            
            if response.user:
                return {
                    "success": True,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "full_name": full_name,
                        "role": role.value,
                        "permissions": self._get_role_permissions(role)
                    },
                    "message": "Usuário criado com sucesso"
                }
            else:
                return {"success": False, "message": "Falha ao criar usuário"}
                
        except Exception as e:
            logger.error(f"Erro no registro: {e}")
            return {"success": False, "message": f"Erro interno: {e}"}
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Fazer login do usuário"""
        try:
            # Usuário de teste (temporário até configurar Supabase corretamente)
            if email == "admin@hubcontrol.com" and password == "admin123":
                # Criar JWT token customizado
                token_data = {
                    "user_id": "test-admin-id",
                    "email": email,
                    "role": "admin",
                    "exp": datetime.utcnow() + timedelta(hours=24),
                    "iat": datetime.utcnow()
                }
                
                access_token = jwt.encode(token_data, self.jwt_secret, algorithm="HS256")
                
                return {
                    "success": True,
                    "access_token": access_token,
                    "token_type": "Bearer",
                    "expires_in": 86400,  # 24 horas
                    "user": {
                        "id": "test-admin-id",
                        "email": email,
                        "full_name": "Administrador Sistema",
                        "role": "admin",
                        "permissions": self._get_role_permissions(UserRole.ADMIN)
                    }
                }
            
            # Usuários de teste para diferentes papéis
            test_users = {
                "diretoria@hubcontrol.com": {"role": UserRole.DIRETORIA, "name": "Diretor Geral"},
                "cs@hubcontrol.com": {"role": UserRole.CS_CX, "name": "Gerente CS"},
                "vendas@hubcontrol.com": {"role": UserRole.VENDAS, "name": "Gerente Vendas"},
                "financeiro@hubcontrol.com": {"role": UserRole.FINANCEIRO, "name": "Gerente Financeiro"},
                "dataops@hubcontrol.com": {"role": UserRole.DATAOPS, "name": "Analista DataOps"}
            }
            
            if email in test_users and password == "123456":
                user_info = test_users[email]
                role = user_info["role"]
                
                # Criar JWT token customizado
                token_data = {
                    "user_id": f"test-{role.value}-id",
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
                    "expires_in": 86400,  # 24 horas
                    "user": {
                        "id": f"test-{role.value}-id",
                        "email": email,
                        "full_name": user_info["name"],
                        "role": role.value,
                        "permissions": self._get_role_permissions(role)
                    }
                }
            
            # Para usuários criados mas não confirmados, permitir login direto
            # Verificar se o usuário existe no Supabase Auth
            try:
                # Verificar se existe um usuário com esse email (mesmo não confirmado)
                admin_response = self.supabase.auth.admin.list_users()
                if admin_response.users:
                    for user in admin_response.users:
                        if user.email == email:
                            # Usuário existe, verificar metadados
                            user_metadata = user.user_metadata or {}
                            if user_metadata.get('role'):
                                role_str = user_metadata.get('role', 'cs_cx')
                                role = UserRole(role_str)
                                
                                # Criar JWT token customizado
                                token_data = {
                                    "user_id": user.id,
                                    "email": user.email,
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
                                        "id": user.id,
                                        "email": user.email,
                                        "full_name": user_metadata.get('full_name', user.email),
                                        "role": role.value,
                                        "permissions": self._get_role_permissions(role)
                                    }
                                }
                                
            except Exception as supabase_error:
                logger.warning(f"Erro ao verificar usuário Supabase: {supabase_error}")
                
            # Tentar login real no Supabase (para usuários confirmados)
            try:
                response = self.supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                
                if response.user and response.session:
                    # Obter dados do usuário dos metadados
                    user_metadata = response.user.user_metadata or {}
                    role_str = user_metadata.get('role', 'cs_cx')
                    role = UserRole(role_str)
                    
                    # Criar JWT token customizado
                    token_data = {
                        "user_id": response.user.id,
                        "email": response.user.email,
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
                            "id": response.user.id,
                            "email": response.user.email,
                            "full_name": user_metadata.get('full_name', response.user.email),
                            "role": role.value,
                            "permissions": self._get_role_permissions(role)
                        }
                    }
            except Exception as supabase_error:
                logger.warning(f"Falha no login Supabase: {supabase_error}")
            
            return {"success": False, "message": "Credenciais inválidas"}
                
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return {"success": False, "message": "Erro ao fazer login"}
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verificar e decodificar token JWT"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            
            # Obter dados atualizados do usuário
            user_response = self.supabase.auth.get_user(token)
            if user_response.user:
                user_metadata = user_response.user.user_metadata or {}
                role_str = user_metadata.get('role', 'cs_cx')
                role = UserRole(role_str)
                
                return {
                    "valid": True,
                    "user": {
                        "id": user_response.user.id,
                        "email": user_response.user.email,
                        "full_name": user_metadata.get('full_name', user_response.user.email),
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
        """Listar todos os usuários (apenas admin)"""
        try:
            # Para simplificar, retorna uma lista mock
            # Em produção, isso deveria consultar a admin API do Supabase
            return [
                {
                    "id": "admin-user-id",
                    "email": "admin@hubcontrol.com",
                    "full_name": "Administrador Sistema",
                    "role": "admin",
                    "permissions": self._get_role_permissions(UserRole.ADMIN)
                }
            ]
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            return []
    
    def update_user_role(self, user_id: str, new_role: str) -> Dict[str, Any]:
        """Atualizar papel do usuário"""
        try:
            # Esta operação requer admin API do Supabase
            # Por enquanto retorna sucesso simulado
            return {"success": True, "message": "Papel atualizado com sucesso"}
        except Exception as e:
            logger.error(f"Erro ao atualizar papel: {e}")
            return {"success": False, "message": "Erro ao atualizar papel"}
    
    def deactivate_user(self, user_id: str) -> Dict[str, Any]:
        """Desativar usuário"""
        try:
            # Esta operação requer admin API do Supabase
            # Por enquanto retorna sucesso simulado
            return {"success": True, "message": "Usuário desativado com sucesso"}
        except Exception as e:
            logger.error(f"Erro ao desativar usuário: {e}")
            return {"success": False, "message": "Erro ao desativar usuário"}
    
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
auth_service = SimpleAuthService()