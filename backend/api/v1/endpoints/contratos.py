"""
Endpoints de contratos
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_contratos():
    """Endpoint de teste para contratos"""
    return {"message": "Contratos endpoint working"}