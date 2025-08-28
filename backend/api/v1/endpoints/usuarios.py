"""
Endpoints de usuários
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_usuarios():
    """Endpoint de teste para usuários"""
    return {"message": "Usuarios endpoint working"}