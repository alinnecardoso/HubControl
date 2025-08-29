"""
Configurações da aplicação HubControl
"""
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Configurações básicas
    debug: bool = Field(default=True, description="Modo debug")
    log_level: str = Field(default="INFO", description="Nível de log") 
    log_file: str = Field(default="logs/hubcontrol.log", description="Arquivo de log")
    app_name: str = Field(default="HubControl", description="Nome da aplicação")
    app_version: str = Field(default="1.0.0", description="Versão da aplicação")
    
    # Supabase
    SUPABASE_URL: str = Field(
        default="https://auhkbtxjoqvahiajopop.supabase.co",
        description="URL do projeto Supabase"
    )
    SUPABASE_ANON_KEY: str = Field(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1aGtidHhqb3F2YWhpYWpvcG9wIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYyNTk5NTYsImV4cCI6MjA3MTgzNTk1Nn0.TmzyeS7_NEiR3tQbFapsqGUi98Zb44YmuKFwlvCYX2I",
        description="Chave anônima do Supabase"
    )
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(
        default=None,
        description="Chave de serviço do Supabase (para operações admin)"
    )
    
    # Database (Supabase)
    DATABASE_URL: str = Field(
        default="postgresql://postgres:himmelcorp123@db.auhkbtxjoqvahiajopop.supabase.co:5432/postgres",
        description="URL de conexão com o banco Supabase"
    )
    
    # Configurações de segurança
    SECRET_KEY: str = Field(
        default="hubcontrol-secret-key-change-in-production",
        description="Chave secreta para JWT"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="Algoritmo JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Expiração do token JWT")
    
    # Firebase (opcional)
    FIREBASE_PROJECT_ID: Optional[str] = Field(default=None, description="ID do projeto Firebase")
    FIREBASE_PRIVATE_KEY: Optional[str] = Field(default=None, description="Chave privada Firebase")
    FIREBASE_CLIENT_EMAIL: Optional[str] = Field(default=None, description="Email do cliente Firebase")
    
    # Configurações de email
    SMTP_HOST: Optional[str] = Field(default=None, description="Host SMTP")
    SMTP_PORT: int = Field(default=587, description="Porta SMTP")
    SMTP_USER: Optional[str] = Field(default=None, description="Usuário SMTP")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="Senha SMTP")
    
    # Configurações do Slack
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, description="Webhook do Slack")
    
    # Configurações de upload
    UPLOAD_DIR: str = Field(default="uploads", description="Diretório de uploads")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, description="Tamanho máximo de arquivo (10MB)")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", description="URL do Redis")
    
    # Configurações de CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Origens permitidas para CORS"
    )
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Limite de requisições por minuto")
    
    # Health Score thresholds
    HEALTH_SCORE_BAIXO: int = Field(default=40, description="Threshold para Health Score baixo")
    HEALTH_SCORE_MEDIO: int = Field(default=60, description="Threshold para Health Score médio")
    HEALTH_SCORE_ALTO: int = Field(default=80, description="Threshold para Health Score alto")
    
    # Renovação
    DIAS_ALERTA_VENCIMENTO: int = Field(default=30, description="Dias para alerta de vencimento")
    DIAS_ALERTA_CHURN: int = Field(default=7, description="Dias para alerta de churn")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Instância global das configurações
settings = Settings()

# Configurações de CORS
CORS_CONFIG = {
    "allow_origins": settings.CORS_ORIGINS,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"]
}

# Configurações de paginação
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Configurações de cache
CACHE_TTL = 300  # 5 minutos
CACHE_MAX_SIZE = 1000

# Configurações de ML
ML_MODEL_PATH = "models/churn"
ML_TRAINING_BATCH_SIZE = 1000
ML_PREDICTION_TIMEOUT = 30

# Configurações de notificação
NOTIFICATION_EMAIL_TEMPLATE = "emails/notification.html"
NOTIFICATION_SLACK_TEMPLATE = "slack/notification.json"

# Configurações de backup
BACKUP_RETENTION_DAYS = 30
BACKUP_SCHEDULE = "0 2 * * *"  # 2 AM diariamente 