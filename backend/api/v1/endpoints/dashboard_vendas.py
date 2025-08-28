"""
Endpoints do dashboard de Vendas
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_dashboard_vendas():
    """Endpoint de teste para dashboard vendas"""
    return {"message": "Dashboard Vendas endpoint working"}