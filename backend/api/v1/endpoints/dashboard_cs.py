"""
Endpoints do dashboard de Customer Success
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_dashboard_cs():
    """Endpoint de teste para dashboard CS"""
    return {"message": "Dashboard CS endpoint working"}