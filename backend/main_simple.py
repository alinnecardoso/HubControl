"""
Aplicação simplificada HubControl
"""
from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import logging

# Importar rotas de autenticação e vendas
from api.auth_routes import router as auth_router, get_current_user
from api.sales_routes import router as sales_router
from services.auth_simple_mock import UserRole
from middleware.rbac import rbac, data_filter

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criação da aplicação FastAPI
app = FastAPI(
    title="HubControl",
    version="1.0.0",
    description="Sistema integrado de gestão empresarial com módulos de Customer Success e Vendas"
)

# Configurar CORS de forma simples e direta
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rota de health check
@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "app_name": "HubControl",
        "version": "1.0.0"
    }

# Rota raiz
@app.get("/")
async def root():
    """Endpoint raiz da aplicação"""
    return {
        "message": "Bem-vindo ao HubControl",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Incluir rotas de autenticação e vendas
app.include_router(auth_router, prefix="/api/v1")
app.include_router(sales_router, prefix="/api/v1")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)