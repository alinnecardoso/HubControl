"""
Endpoints de health score
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_health_score():
    """Endpoint de teste para health score"""
    return {"message": "Health Score endpoint working"}