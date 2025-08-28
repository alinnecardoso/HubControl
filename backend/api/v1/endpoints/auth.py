"""
Endpoints de autenticação
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_auth():
    """Endpoint de teste para autenticação"""
    return {"message": "Auth endpoint working"}