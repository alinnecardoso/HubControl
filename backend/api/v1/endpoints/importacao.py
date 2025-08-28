"""
Endpoints de importação de dados
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_importacao():
    """Endpoint de teste para importação"""
    return {"message": "Importacao endpoint working"}