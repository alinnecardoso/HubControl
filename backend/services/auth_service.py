"""
Serviço de Autenticação com Supabase
"""
import os
from enum import Enum
from typing import Optional, Dict, Any
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

class SupabaseAuthService:
    """Serviço de autenticação integrado com Supabase"""
    
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
                    }
                }
            })
            
            if response.user:
                # Adicionar à tabela de perfis de usuário
                profile_data = {
                    "id": response.user.id,
                    "email": email,
                    "full_name": full_name,
                    "role": role.value,
                    "is_active": True,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                # Temporariamente comentado até criar a tabela user_profiles
                # self.supabase.table("user_profiles").insert(profile_data).execute()
                
                return {
                    "success": True,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "full_name": full_name,
                        "role": role.value
                    },
                    "message": "Usuário criado com sucesso"
                }
            else:
                return {"success": False, "message": "Falha ao criar usuário"}
                
        except Exception as e:
            logger.error(f"Erro no registro: {e}")
            return {"success": False, "message": f"Erro interno: {str(e)}"}
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Realiza login do usuário"""
        try:
            # Autenticar com Supabase
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                # Buscar perfil do usuário
                profile_response = self.supabase.table("user_profiles").select("*").eq("id", response.user.id).execute()
                
                if profile_response.data:
                    profile = profile_response.data[0]
                    
                    # Verificar se usuário está ativo
                    if not profile.get("is_active", True):
                        return {"success": False, "message": "Usuário desativado"}
                    
                    # Gerar token JWT customizado
                    token_payload = {
                        "user_id": response.user.id,
                        "email": response.user.email,
                        "full_name": profile.get("full_name"),
                        "role": profile.get("role"),
                        "exp": datetime.utcnow() + timedelta(hours=24),
                        "iat": datetime.utcnow()
                    }
                    
                    access_token = jwt.encode(token_payload, self.jwt_secret, algorithm="HS256")
                    
                    # Atualizar último login
                    self.supabase.table("user_profiles").update({
                        "last_login": datetime.now().isoformat()
                    }).eq("id", response.user.id).execute()
                    
                    return {
                        "success": True,
                        "access_token": access_token,
                        "token_type": "Bearer",
                        "expires_in": 86400,  # 24 horas
                        "user": {
                            "id": response.user.id,
                            "email": response.user.email,
                            "full_name": profile.get("full_name"),
                            "role": profile.get("role"),
                            "permissions": self._get_role_permissions(profile.get("role"))
                        }
                    }
                else:
                    return {"success": False, "message": "Perfil de usuário não encontrado"}
            else:
                return {"success": False, "message": "Credenciais inválidas"}
                
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return {"success": False, "message": "Erro interno"}
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica e decodifica token JWT"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def _get_role_permissions(self, role: str) -> Dict[str, list]:
        """Define permissões baseadas no papel do usuário"""
        permissions_map = {
            UserRole.ADMIN.value: {
                "modules": ["dashboard", "clientes", "vendas", "contratos", "health_score", "csat", "ml_churn", "usuarios", "configuracoes"],
                "actions": ["create", "read", "update", "delete", "export", "import", "manage_users"],
                "data_access": "all"
            },
            UserRole.DIRETORIA.value: {
                "modules": ["dashboard", "clientes", "vendas", "contratos", "health_score", "csat", "ml_churn"],
                "actions": ["read", "export"],
                "data_access": "all_readonly"
            },
            UserRole.CS_CX.value: {
                "modules": ["dashboard", "clientes", "health_score", "csat", "ml_churn"],
                "actions": ["create", "read", "update", "export"],
                "data_access": "cs_data"
            },
            UserRole.FINANCEIRO.value: {
                "modules": ["dashboard", "clientes", "contratos", "vendas"],
                "actions": ["read", "update", "export"],
                "data_access": "financial_data"
            },
            UserRole.VENDAS.value: {
                "modules": ["dashboard", "clientes", "vendas", "ml_churn"],
                "actions": ["create", "read", "update", "export"],
                "data_access": "sales_data"
            },
            UserRole.DATAOPS.value: {
                "modules": ["dashboard", "clientes", "vendas", "contratos", "health_score", "csat", "ml_churn"],
                "actions": ["read", "export", "import", "ml_operations"],
                "data_access": "analytics_data"
            }
        }
        
        return permissions_map.get(role, {
            "modules": ["dashboard"],
            "actions": ["read"],
            "data_access": "limited"
        })
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Busca perfil completo do usuário"""
        try:
            response = self.supabase.table("user_profiles").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar perfil: {e}")
            return None
    
    def update_user_role(self, user_id: str, new_role: UserRole, admin_user_id: str) -> Dict[str, Any]:
        """Atualiza papel do usuário (apenas admins)"""
        try:
            # Verificar se quem está fazendo a alteração é admin
            admin_profile = self.get_user_profile(admin_user_id)
            if not admin_profile or admin_profile.get("role") != UserRole.ADMIN.value:
                return {"success": False, "message": "Apenas administradores podem alterar papéis"}
            
            # Atualizar papel
            self.supabase.table("user_profiles").update({
                "role": new_role.value,
                "updated_at": datetime.now().isoformat()
            }).eq("id", user_id).execute()
            
            return {"success": True, "message": "Papel atualizado com sucesso"}
            
        except Exception as e:
            logger.error(f"Erro ao atualizar papel: {e}")
            return {"success": False, "message": "Erro interno"}
    
    def list_users(self, admin_user_id: str) -> Dict[str, Any]:
        """Lista todos os usuários (apenas admins)"""
        try:
            # Verificar permissão de admin
            admin_profile = self.get_user_profile(admin_user_id)
            if not admin_profile or admin_profile.get("role") != UserRole.ADMIN.value:
                return {"success": False, "message": "Acesso negado"}
            
            response = self.supabase.table("user_profiles").select("*").execute()
            
            return {
                "success": True,
                "users": response.data
            }
            
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            return {"success": False, "message": "Erro interno"}
    
    def deactivate_user(self, user_id: str, admin_user_id: str) -> Dict[str, Any]:
        """Desativa usuário (apenas admins)"""
        try:
            # Verificar permissão de admin
            admin_profile = self.get_user_profile(admin_user_id)
            if not admin_profile or admin_profile.get("role") != UserRole.ADMIN.value:
                return {"success": False, "message": "Acesso negado"}
            
            self.supabase.table("user_profiles").update({
                "is_active": False,
                "updated_at": datetime.now().isoformat()
            }).eq("id", user_id).execute()
            
            return {"success": True, "message": "Usuário desativado com sucesso"}
            
        except Exception as e:
            logger.error(f"Erro ao desativar usuário: {e}")
            return {"success": False, "message": "Erro interno"}

# Instância global do serviço
auth_service = SupabaseAuthService()