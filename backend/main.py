import subprocess
import sys
import importlib

def install_package(package):
    try:
        importlib.import_module(package)
        print(f"{package} is already installed.")
    except ImportError:
        print(f"{package} not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            sys.exit(1)

# Check and install required packages
install_package("fastapi")
install_package("uvicorn")

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

from config import settings, CORS_CONFIG
from database.connection import init_db, close_db
from api.v1.api import api_router


# Configuração de logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.log_file) if settings.log_file else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    logger.info("Iniciando aplicação HubControl...")
    await init_db()
    logger.info("Aplicação HubControl iniciada com sucesso!")
    
    yield
    
    # Shutdown
    logger.info("Encerrando aplicação HubControl...")
    await close_db()
    logger.info("Aplicação HubControl encerrada!")


# Criação da aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema integrado de gestão empresarial com módulos de Customer Success e Vendas",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    **CORS_CONFIG
)

# Middleware de hosts confiáveis
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"]
)


# Middleware de logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de requisições"""
    start_time = time.time()
    
    # Log da requisição
    logger.info(f"Requisição: {request.method} {request.url}")
    
    # Processa a requisição
    response = await call_next(request)
    
    # Calcula tempo de resposta
    process_time = time.time() - start_time
    
    # Log da resposta
    logger.info(f"Resposta: {response.status_code} - Tempo: {process_time:.4f}s")
    
    # Adiciona header de tempo de processamento
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Middleware de tratamento de erros
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para exceções HTTP"""
    logger.error(f"Erro HTTP {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para exceções gerais"""
    logger.error(f"Erro interno: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "status_code": 500,
            "path": request.url.path
        }
    )


# Inclui as rotas da API
app.include_router(api_router, prefix="/api/v1")


# Rota de health check
@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "timestamp": time.time()
    }


# Rota raiz
@app.get("/")
async def root():
    """Endpoint raiz da aplicação"""
    return {
        "message": f"Bem-vindo ao {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Documentação não disponível em produção"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 