"""
API Router principal para versão 1
"""
from fastapi import APIRouter
from .endpoints import (
    auth,
    usuarios,
    clientes,
    vendas,
    contratos,
    health_score,
    csat,
    dashboard_cs,
    dashboard_vendas,
    importacao,
    ml_churn
)

api_router = APIRouter()

# Rotas de autenticação e usuários
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuários"])

# Rotas de dados principais
api_router.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
api_router.include_router(vendas.router, prefix="/vendas", tags=["Vendas"])
api_router.include_router(contratos.router, prefix="/contratos", tags=["Contratos"])

# Rotas de Customer Success
api_router.include_router(health_score.router, prefix="/health-score", tags=["Health Score"])
api_router.include_router(csat.router, prefix="/csat", tags=["CSAT"])
api_router.include_router(dashboard_cs.router, prefix="/dashboard-cs", tags=["Dashboard CS"])

# Rotas de Vendas
api_router.include_router(dashboard_vendas.router, prefix="/dashboard-vendas", tags=["Dashboard Vendas"])

# Rotas de importação e integração
api_router.include_router(importacao.router, prefix="/importacao", tags=["Importação"])

# Rotas de Machine Learning
api_router.include_router(ml_churn.router, prefix="/ml/churn", tags=["Machine Learning - Churn"]) 