"""
Endpoint da API para Machine Learning - Previsão de Churn
"""
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import logging

from database.connection import get_db
from ml.churn_predictor import ChurnMLService
from schemas.ml_churn import (
    ChurnPredictionRequest,
    ChurnPredictionResponse,
    ChurnTrainingResponse,
    ChurnInsightsResponse,
    ModelTrainingRequest
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Instância global do serviço ML
ml_service = ChurnMLService()


@router.post("/train", response_model=ChurnTrainingResponse, summary="Treinar modelos de ML")
async def train_models(
    request: ModelTrainingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Treina os modelos de Machine Learning para previsão de churn.
    
    - **force_retrain**: Força retreinamento mesmo se modelos existirem
    - **validation_split**: Percentual de dados para validação (0.1-0.3)
    """
    try:
        if request.force_retrain or not ml_service.is_trained:
            # Treinamento em background para não bloquear a API
            background_tasks.add_task(ml_service.train_from_database, db)
            
            return ChurnTrainingResponse(
                message="Treinamento iniciado em background",
                status="training",
                estimated_time="5-10 minutos"
            )
        else:
            return ChurnTrainingResponse(
                message="Modelos já treinados",
                status="trained",
                estimated_time="0 minutos"
            )
            
    except Exception as e:
        logger.error(f"Erro ao iniciar treinamento: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao treinar modelos: {str(e)}")


@router.get("/train/status", summary="Status do treinamento")
async def get_training_status():
    """
    Retorna o status atual do treinamento dos modelos.
    """
    return {
        "is_trained": ml_service.is_trained,
        "status": "trained" if ml_service.is_trained else "not_trained",
        "last_training": "N/A"  # TODO: implementar timestamp do último treinamento
    }


@router.post("/predict", response_model=ChurnPredictionResponse, summary="Prever churn de cliente")
async def predict_churn(
    request: ChurnPredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Faz previsão de churn para um cliente específico.
    
    - **cliente_id**: ID do cliente para análise
    """
    try:
        if not ml_service.is_trained:
            raise HTTPException(
                status_code=400, 
                detail="Modelos não treinados. Execute /train primeiro."
            )
        
        # Faz previsão
        prediction = ml_service.predict_client_churn(request.cliente_id, db)
        
        if "error" in prediction:
            raise HTTPException(status_code=400, detail=prediction["error"])
        
        return ChurnPredictionResponse(
            cliente_id=request.cliente_id,
            risk_level=prediction["risk_level"],
            risk_score=prediction["risk_score"],
            predictions=prediction["predictions"],
            features_importance=prediction["features_importance"],
            recommendations=prediction["recommendations"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao prever churn: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao fazer previsão: {str(e)}")


@router.get("/insights", response_model=ChurnInsightsResponse, summary="Insights gerais de churn")
async def get_churn_insights(db: Session = Depends(get_db)):
    """
    Retorna insights gerais sobre churn e risco dos clientes.
    """
    try:
        if not ml_service.is_trained:
            raise HTTPException(
                status_code=400, 
                detail="Modelos não treinados. Execute /train primeiro."
            )
        
        insights = ml_service.get_churn_insights(db)
        
        if "error" in insights:
            raise HTTPException(status_code=400, detail=insights["error"])
        
        return ChurnInsightsResponse(**insights)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter insights: {str(e)}")


@router.get("/clients/risk-analysis", summary="Análise de risco de todos os clientes")
async def analyze_all_clients_risk(
    limit: int = 100,
    risk_threshold: float = 0.5,
    db: Session = Depends(get_db)
):
    """
    Analisa o risco de churn de todos os clientes ativos.
    
    - **limit**: Número máximo de clientes a retornar
    - **risk_threshold**: Threshold para considerar cliente de risco
    """
    try:
        if not ml_service.is_trained:
            raise HTTPException(
                status_code=400, 
                detail="Modelos não treinados. Execute /train primeiro."
            )
        
        from models.cliente import Cliente
        
        # Busca clientes ativos
        clientes_ativos = db.query(Cliente).filter(
            Cliente.status_cliente == "ativo"
        ).limit(limit).all()
        
        risk_analysis = []
        
        for cliente in clientes_ativos:
            try:
                prediction = ml_service.predict_client_churn(cliente.id, db)
                
                if "error" not in prediction:
                    risk_analysis.append({
                        "cliente_id": cliente.id,
                        "nome": cliente.nome_principal,
                        "risk_level": prediction["risk_level"],
                        "risk_score": prediction["risk_score"],
                        "health_score": prediction.get("features", {}).get("health_score_atual", 0),
                        "dias_vencimento": prediction.get("features", {}).get("dias_vencimento_proximo", 999),
                        "csat_medio": prediction.get("features", {}).get("csat_medio", 0),
                        "recommendations": prediction.get("recommendations", [])
                    })
            except Exception as e:
                logger.warning(f"Erro ao analisar cliente {cliente.id}: {str(e)}")
                continue
        
        # Filtra por threshold de risco
        high_risk_clients = [
            c for c in risk_analysis 
            if c["risk_score"] >= risk_threshold
        ]
        
        # Ordena por risco (maior primeiro)
        high_risk_clients.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return {
            "total_analyzed": len(risk_analysis),
            "high_risk_count": len(high_risk_clients),
            "risk_threshold": risk_threshold,
            "high_risk_clients": high_risk_clients[:50],  # Top 50
            "risk_distribution": {
                "baixo": len([c for c in risk_analysis if c["risk_level"] == "baixo"]),
                "medio": len([c for c in risk_analysis if c["risk_level"] == "medio"]),
                "alto": len([c for c in risk_analysis if c["risk_level"] == "alto"]),
                "critico": len([c for c in risk_analysis if c["risk_level"] == "critico"])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na análise de risco: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")


@router.get("/models/info", summary="Informações sobre os modelos")
async def get_models_info():
    """
    Retorna informações sobre os modelos de ML treinados.
    """
    try:
        models_info = {}
        
        for name, model in ml_service.predictor.models.items():
            if hasattr(model, 'feature_importances_'):
                models_info[name] = {
                    "type": "tree_based",
                    "feature_importance_available": True,
                    "n_features": len(model.feature_importances_) if hasattr(model, 'n_features_in_') else "N/A"
                }
            elif hasattr(model, 'coef_'):
                models_info[name] = {
                    "type": "linear",
                    "feature_importance_available": True,
                    "n_features": len(model.coef_[0]) if hasattr(model, 'n_features_in_') else "N/A"
                }
            elif name == 'neural_network':
                models_info[name] = {
                    "type": "neural_network",
                    "feature_importance_available": False,
                    "architecture": "Sequential",
                    "layers": len(model.layers)
                }
            else:
                models_info[name] = {
                    "type": "unknown",
                    "feature_importance_available": False
                }
        
        return {
            "total_models": len(models_info),
            "models": models_info,
            "feature_names": ml_service.predictor.feature_names,
            "n_features": len(ml_service.predictor.feature_names),
            "is_trained": ml_service.is_trained
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter info dos modelos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter informações: {str(e)}")


@router.post("/models/retrain", summary="Forçar retreinamento dos modelos")
async def force_retrain_models(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Força o retreinamento completo dos modelos de ML.
    """
    try:
        # Remove modelos existentes
        ml_service.is_trained = False
        
        # Inicia treinamento em background
        background_tasks.add_task(ml_service.train_from_database, db)
        
        return {
            "message": "Retreinamento forçado iniciado",
            "status": "retraining",
            "estimated_time": "5-10 minutos"
        }
        
    except Exception as e:
        logger.error(f"Erro ao forçar retreinamento: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao retreinar: {str(e)}")


@router.get("/health", summary="Health check do sistema ML")
async def ml_health_check():
    """
    Verifica a saúde do sistema de Machine Learning.
    """
    try:
        health_status = {
            "status": "healthy",
            "ml_service_available": True,
            "models_trained": ml_service.is_trained,
            "total_models": len(ml_service.predictor.models),
            "feature_engineer_available": ml_service.predictor.feature_engineer is not None,
            "scaler_available": ml_service.predictor.scaler is not None
        }
        
        # Verifica se há erros específicos
        if not ml_service.is_trained:
            health_status["status"] = "warning"
            health_status["message"] = "Modelos não treinados"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Erro no health check ML: {str(e)}")
        return {
            "status": "unhealthy",
            "ml_service_available": False,
            "error": str(e)
        }


@router.get("/cache/stats", summary="Estatísticas do cache")
async def get_cache_stats():
    """
    Retorna estatísticas do sistema de cache de ML.
    """
    try:
        stats = ml_service.predictor.get_cache_stats()
        return {
            "cache_stats": stats,
            "timestamp": "2024-01-01T00:00:00Z"  # TODO: usar timestamp real
        }
    except Exception as e:
        logger.error(f"Erro ao obter stats do cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")


@router.delete("/cache/clear", summary="Limpar todo o cache")
async def clear_all_cache():
    """
    Limpa todo o cache de ML.
    """
    try:
        from ml.model_cache import model_cache
        success = model_cache.clear_all_cache()
        
        if success:
            return {
                "message": "Cache limpo com sucesso",
                "cleared": True
            }
        else:
            raise HTTPException(status_code=500, detail="Falha ao limpar cache")
            
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao limpar cache: {str(e)}")


@router.delete("/cache/client/{cliente_id}", summary="Limpar cache de cliente")
async def clear_client_cache(cliente_id: str):
    """
    Limpa cache relacionado a um cliente específico.
    """
    try:
        ml_service.predictor.clear_client_cache(cliente_id)
        
        return {
            "message": f"Cache do cliente {cliente_id} limpo com sucesso",
            "cliente_id": cliente_id,
            "cleared": True
        }
        
    except Exception as e:
        logger.error(f"Erro ao limpar cache do cliente: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao limpar cache: {str(e)}") 