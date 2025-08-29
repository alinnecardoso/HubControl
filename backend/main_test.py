"""
Aplicação de teste sem banco de dados
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging

# Importar apenas rotas de autenticação
from api.auth_routes import router as auth_router, get_current_user
from services.auth_simple_mock import UserRole
from middleware.rbac import rbac

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criação da aplicação FastAPI
app = FastAPI(
    title="HubControl Test",
    version="1.0.0",
    description="Teste de autenticação e permissões"
)

# Configurar CORS
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
    return {"status": "healthy"}

# Incluir rotas de autenticação
app.include_router(auth_router, prefix="/api/v1")

# Endpoints de teste para cada módulo
@app.get("/api/v1/vendas/dashboard/test")
@rbac.require_module_access("vendas_dashboard")
async def test_vendas_dashboard(current_user: dict = Depends(get_current_user)):
    return {"message": "Dashboard Vendas OK", "user": current_user["email"]}

@app.get("/api/v1/vendas/registro/test")
@rbac.require_module_access("vendas_registro")
async def test_vendas_registro(current_user: dict = Depends(get_current_user)):
    return {"message": "Registro Vendas OK", "user": current_user["email"]}

@app.get("/api/v1/vendas/vendedores/test")
@rbac.require_module_access("vendas_vendedores")
async def test_vendas_vendedores(current_user: dict = Depends(get_current_user)):
    return {"message": "Vendedores OK", "user": current_user["email"]}

@app.get("/api/v1/vendas/dados/test")
@rbac.require_module_access("vendas_dados")
async def test_vendas_dados(current_user: dict = Depends(get_current_user)):
    return {"message": "Dados Vendas OK", "user": current_user["email"]}

@app.get("/api/v1/clientes/test")
@rbac.require_module_access("clientes")
async def test_clientes(current_user: dict = Depends(get_current_user)):
    return {"message": "Clientes OK", "user": current_user["email"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)