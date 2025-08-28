"""
Configurações da aplicação HubControl
"""
import os
import logging
import sys
from typing import Optional, List
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Constrói o caminho absoluto para o arquivo .env
# Isso garante que ele seja encontrado, independentemente de onde o script é executado.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_ENV_FILE = os.path.join(_BASE_DIR, '.env')

def _split_csv(value: str | None) -> List[str]:
    if not value or value == "*":
        return ["*"]
    return [x.strip() for x in value.split(",") if x.strip()]

class Settings(BaseSettings):
    """Configurações da aplicação"""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Configurações básicas
    PROJECT_NAME: str = "HubControl"
    API_VERSION: str = "v1"
    API_V1_STR: str = f"/api/{API_VERSION}"
    DEBUG: bool = Field(default=False, description="Modo debug")
    LOG_LEVEL: str = Field(default="INFO", description="Nível de log")
    LOG_FILE: Optional[str] = Field(default=None, description="Arquivo de log (opcional)")
    ALLOWED_HOSTS: Optional[str] = Field(default=None, description="Hosts permitidos (separados por vírgula)")

    # Supabase
    SUPABASE_URL: str = Field(default="https://auhkbtxjoqvahiajopop.supabase.co", description="URL do projeto Supabase")
    SUPABASE_ANON_KEY: str = Field(default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1aGtidHhqb3F2YWhpYWpvcG9wIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYyNTk5NTYsImV4cCI6MjA3MTgzNTk1Nn0.TmzyeS7_NEiR3tQbFapsqGUi98Zb44YmuKFwlvCYX2I", description="Chave anônima do Supabase")
    SUPABASE_SERVICE_ROLE_KEY: Optional[SecretStr] = Field(default=None, description="Chave de serviço do Supabase (para operações admin)")

    # Database (Supabase)
    DATABASE_URL: str = Field(default="postgresql://postgres:himmelcorp@123@db.auhkbtxjoqvahiajopop.supabase.co:5432/postgres", description="URL de conexão com o banco Supabase")

    # Configurações de segurança
    SECRET_KEY: SecretStr = Field(description="Chave secreta para JWT")
    JWT_ALGORITHM: str = Field(default="HS256", description="Algoritmo JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 8, description="Expiração do token JWT (8 dias)")

    # Configurações de CORS
    BACKEND_CORS_ORIGINS: Optional[str] = Field(default="*", description="Origens permitidas para CORS")

# Instância global das configurações
settings = Settings()

# --- Configuração do Logger ---

# Obtém o logger para a aplicação
logger = logging.getLogger(settings.PROJECT_NAME)
logger.setLevel(settings.LOG_LEVEL.upper())

# Formato do log
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
)

# Handler para console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Handler para arquivo (se especificado)
if settings.LOG_FILE:
    # Garante que o diretório de logs exista
    log_dir = os.path.dirname(settings.LOG_FILE)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

logger.info("Logger configurado com sucesso.")
