"""
Endpoints de CSAT
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_csat():
    """Endpoint de teste para CSAT"""
    return {"message": "CSAT endpoint working"}