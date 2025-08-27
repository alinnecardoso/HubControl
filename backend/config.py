"""
Configurações da aplicação HubControl
"""
from typing import Optional, List
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_csv(value: str | None) -> List[str]:
    if not value or value == "*":
        return ["*"]
    return [x.strip() for x in value.split(",") if x.strip()]

class Settings(BaseSettings):
    """Configurações da aplicação"""

    # Carregar .env e ignorar extras desconhecidos (evita extra_forbidden)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",    # ← chave para não quebrar com variáveis que o modelo não conhece
    )

    # Configurações básicas
    DEBUG: bool = Field(default=False, description="Modo debug")
    LOG_LEVEL: str = Field(default="INFO", description="Nível de log")
    LOG_FILE: str = Field(default="logs/hubcontrol.log", description="Arquivo de log")

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
        default="postgresql://postgres:himmelcorp@123@db.auhkbtxjoqvahiajopop.supabase.co:5432/postgres",
        description="URL de conexão com o banco Supabase"
    )

    # Configurações de segurança
    SECRET_KEY: SecretStr = Field(
        default=..., # This should be set from environment variables
        description="Chave secreta para JWT"
    )
    # Use a plain string for the default value if it's not sensitive and you
    # don't require it to be loaded from env variables specifically as a SecretStr
    # SECRET_KEY: str = Field(
    #     default="hubcontrol-secret-key-change-in-production",
    #    description="Chave secreta para JWT"
    #)
    JWT_ALGORITHM: str = Field(default="HS256", description="Algoritmo JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Expiração do token JWT")

    # Firebase (opcional)
    FIREBASE_PROJECT_ID: Optional[str] = Field(default=None, description="ID do projeto Firebase")
    # Consider using SecretStr for sensitive keys
    FIREBASE_PRIVATE_KEY: Optional[SecretStr] = Field(default=None, description="Chave privada Firebase")
    FIREBASE_CLIENT_EMAIL: Optional[str] = Field(default=None, description="Email do cliente Firebase")
    # Consider using SecretStr for sensitive paths if the content is read from it
    FIREBASE_SERVICE_ACCOUNT_KEY_PATH: Optional[SecretStr] = Field(default=None, description="Path to the Firebase service account key file")

    # Firebase / Google Location (use consistent naming)
    firebase_location: str = Field(default="us-central1", description="Localização dos recursos do Google Cloud (ex: us-central1)") # **não use _location**

    # Google Cloud Platform / BigQuery
    google_project_id: Optional[str] = Field(
        default=None,
        description="ID do projeto Google Cloud (para BigQuery e outros serviços)"
    )
    google_application_credentials: Optional[str] = Field(
        default=None,
        description="Path para o arquivo de credenciais da conta de serviço Google Cloud"
    )
    bigquery_dataset: Optional[str] = Field(
        default=None,
        description="Dataset do BigQuery a ser utilizado"
    )

    # Configurações de email (pode ser SMTP ou outro serviço)
    SMTP_HOST: Optional[str] = Field(default=None, description="Host SMTP")
    SMTP_PORT: int = Field(default=587, description="Porta SMTP")
    SMTP_USER: Optional[str] = Field(default=None, description="Usuário SMTP")
    SMTP_PASSWORD: Optional[SecretStr] = Field(default=None, description="Senha SMTP") # Use SecretStr for passwords
    SMTP_USE_TLS: bool = Field(default=True, description="Usar TLS para SMTP")

    # Duplicate SMTP fields (remove these if they are not intended)
    smtp_server: Optional[str] = Field( # Removed default None as it is redundant with Optional
        description="Servidor SMTP (duplicata?)"
    )
    smtp_username: Optional[str] = Field(
        default=None,
        description="Nome de usuário SMTP (duplicata?)" )
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, description="Webhook do Slack")

    # Configurações de upload
    UPLOAD_DIR: str = Field(default="uploads", description="Diretório de uploads")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, description="Tamanho máximo de arquivo (10MB)")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", description="URL do Redis")

    # Configurações de CORS
    # Changed to a string field to handle CSV from environment variable
    cors_origins: str = "*"  # CSV sem espaços ou *

    def cors_origins_list(self) -> List[str]:
        return _split_csv(self.cors_origins)

    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Limite de requisições por minuto")

    # Health Score thresholds
    HEALTH_SCORE_BAIXO: int = Field(default=40, description="Threshold para Health Score baixo")
    HEALTH_SCORE_MEDIO: int = Field(default=60, description="Threshold para Health Score médio")
    HEALTH_SCORE_ALTO: int = Field(default=80, description="Threshold para Health Score alto")

    # Renovação
    DIAS_ALERTA_VENCIMENTO: int = Field(default=30, description="Dias para alerta de vencimento")
    DIAS_ALERTA_CHURN: int = Field(default=7, description="Dias para alerta de churn")

# Instância global das configurações
settings = Settings()

# Constantes da aplicação
APP_NAME = "HubControl"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Sistema de Gestão de Clientes e Vendas com Machine Learning"

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