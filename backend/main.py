"""
Aplicação principal HubControl
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

# Carrega as variáveis de ambiente
from .config import settings, logger

# Importa as rotas da API
from .api.v1.api import api_router

# Inicializa o logger
log = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Contexto de vida da aplicação para inicialização e finalização de recursos.
    """
    log.info("Iniciando a aplicação HubControl...")
    # Lógica de inicialização (ex: conectar ao banco de dados, carregar modelos de ML)
    yield
    # Lógica de finalização (ex: fechar conexões)
    log.info("Finalizando a aplicação HubControl...")

# Cria a instância da aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para o sistema HubControl - Gestão de clientes e previsão de churn.",
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# --- Middlewares ---

# Middleware para logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Loga o tempo de processamento de cada requisição.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(
        f"Requisição: {request.method} {request.url.path} - Status: {response.status_code} - Duração: {process_time:.4f}s"
    )
    return response

# Middleware para tratamento de exceções globais
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Captura exceções não tratadas e retorna uma resposta JSON padronizada.
    """
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocorreu um erro interno no servidor."},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Tratamento customizado para exceções HTTP.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Configuração de CORS (Cross-Origin Resource Sharing)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Middleware para hosts confiáveis
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS or ["*"]
)

# --- Rotas da API ---

@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Verifica a saúde da aplicação.
    """
    return {"status": "ok"}

# Inclui o roteador da API
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
