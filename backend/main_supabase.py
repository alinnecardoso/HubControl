"""
Aplicação HubControl com integração completa ao Supabase
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio

# Importar configurações e database
from config import settings, CORS_CONFIG
from database.connection import init_db, close_db, get_db, check_db_connection

# Importar rotas de autenticação
from api.auth_routes import router as auth_router, get_current_user
from services.auth_simple_mock import UserRole
from middleware.rbac import rbac, data_filter

# Importar endpoints da API v1
from api.v1.endpoints.vendas import router as vendas_router

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criação da aplicação FastAPI
app = FastAPI(
    title="HubControl",
    version="1.0.0",
    description="Sistema integrado de gestão empresarial com módulos de Customer Success e Vendas - Supabase Integration"
)

# Middleware de CORS
app.add_middleware(CORSMiddleware, **CORS_CONFIG)

# Event handlers para inicialização e finalização
@app.on_event("startup")
async def startup_event():
    """Inicialização da aplicação"""
    logger.info("Iniciando HubControl com Supabase...")
    await init_db()
    logger.info("HubControl iniciado com sucesso!")

@app.on_event("shutdown")
async def shutdown_event():
    """Finalização da aplicação"""
    logger.info("Finalizando HubControl...")
    await close_db()
    logger.info("HubControl finalizado!")

# Rota de health check
@app.get("/health")
async def health_check():
    """Endpoint de health check com verificação de banco"""
    db_status = check_db_connection()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "app_name": "HubControl",
        "version": "1.0.0",
        "database": "connected" if db_status else "disconnected",
        "supabase_url": settings.SUPABASE_URL
    }

# Rota raiz
@app.get("/")
async def root():
    """Endpoint raiz da aplicação"""
    return {
        "message": "Bem-vindo ao HubControl - Supabase Edition",
        "version": "1.0.0",
        "docs": "/docs",
        "database": "Supabase PostgreSQL"
    }

# Incluir rotas de autenticação
app.include_router(auth_router, prefix="/api/v1")

# Incluir rotas da API v1 - importante: metricas/gerais deve vir antes de {venda_id}
try:
    app.include_router(vendas_router, prefix="/api/v1/vendas", tags=["vendas"])
    print("✓ Vendas router included successfully")
except Exception as e:
    print(f"✗ Error including vendas router: {e}")
    import traceback
    traceback.print_exc()

# API ML endpoints com autenticação
@app.get("/api/v1/ml/churn/test")
@rbac.require_module_access("ml_churn")
async def test_ml(current_user: dict = Depends(get_current_user)):
    """Endpoint de teste ML"""
    return {"message": "ML endpoint working", "user": current_user["email"]}

@app.get("/api/v1/clientes/test")
@rbac.require_module_access("clientes") 
async def test_clientes(current_user: dict = Depends(get_current_user)):
    """Endpoint de teste clientes"""
    return {"message": "Clientes endpoint working", "user": current_user["email"]}

@app.get("/api/v1/auth/test")
async def test_auth():
    """Endpoint de teste auth"""
    return {"message": "Auth endpoint working"}

@app.get("/api/v1/usuarios/test")
@rbac.require_roles([UserRole.ADMIN])
async def test_usuarios(current_user: dict = Depends(get_current_user)):
    """Endpoint de teste usuários (apenas admins)"""
    return {"message": "Usuarios endpoint working", "user": current_user["email"]}

@app.get("/api/v1/vendas/test")
@rbac.require_module_access("vendas")
async def test_vendas(current_user: dict = Depends(get_current_user)):
    """Endpoint de teste vendas"""
    from sqlalchemy.orm import Session
    from models.venda import Venda
    
    db: Session = next(get_db())
    try:
        total_vendas = db.query(Venda).count()
        return {"message": "Vendas endpoint working", "user": current_user["email"], "total_vendas": total_vendas}
    finally:
        db.close()

@app.get("/api/v1/contratos/test")
@rbac.require_module_access("contratos")
async def test_contratos(current_user: dict = Depends(get_current_user)):
    """Endpoint de teste contratos"""
    return {"message": "Contratos endpoint working", "user": current_user["email"]}

@app.get("/api/v1/health-score/test")
@rbac.require_module_access("health_score")
async def test_health_score(current_user: dict = Depends(get_current_user)):
    """Endpoint de teste health score"""
    return {"message": "Health Score endpoint working", "user": current_user["email"]}

@app.get("/api/v1/csat/test")
@rbac.require_module_access("csat")
async def test_csat(current_user: dict = Depends(get_current_user)):
    """Endpoint de teste CSAT"""
    return {"message": "CSAT endpoint working", "user": current_user["email"]}

@app.get("/api/v1/dashboard-cs/test")
@rbac.require_roles([UserRole.CS_CX, UserRole.ADMIN, UserRole.DIRETORIA])
async def test_dashboard_cs(current_user: dict = Depends(get_current_user)):
    """Endpoint de teste dashboard CS"""
    return {"message": "Dashboard CS endpoint working", "user": current_user["email"]}

@app.get("/api/v1/dashboard-vendas/test")
@rbac.require_roles([UserRole.VENDAS, UserRole.ADMIN, UserRole.DIRETORIA])
async def test_dashboard_vendas(current_user: dict = Depends(get_current_user)):
    """Endpoint de teste dashboard vendas"""
    return {"message": "Dashboard Vendas endpoint working", "user": current_user["email"]}

@app.get("/api/v1/importacao/test")
@rbac.require_roles([UserRole.ADMIN, UserRole.DATAOPS])
async def test_importacao(current_user: dict = Depends(get_current_user)):
    """Endpoint de teste importação"""
    return {"message": "Importacao endpoint working", "user": current_user["email"]}

# Endpoint para informações do banco de dados (apenas para debug)
@app.get("/api/v1/database/info")
async def database_info():
    """Informações sobre o banco de dados (apenas para desenvolvimento)"""
    from database.connection import get_db_info
    return get_db_info()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_supabase:app", host="0.0.0.0", port=8000, reload=True)