"""
Endpoints de clientes
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_clientes():
    """Endpoint de teste para clientes"""
    return {"message": "Clientes endpoint working"}