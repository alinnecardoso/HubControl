"""
Schemas Pydantic para o sistema de Machine Learning de Churn
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ModelTrainingRequest(BaseModel):
    """Request para treinamento de modelos"""
    
    force_retrain: bool = Field(False, description="Força retreinamento mesmo se modelos existirem")
    validation_split: float = Field(0.2, ge=0.1, le=0.3, description="Percentual para validação")
    use_smote: bool = Field(True, description="Usa SMOTE para balancear dados")
    algorithms: List[str] = Field(
        default=["random_forest", "xgboost", "lightgbm", "neural_network"],
        description="Algoritmos a serem treinados"
    )


class ChurnPredictionRequest(BaseModel):
    """Request para previsão de churn"""
    
    cliente_id: str = Field(..., description="ID do cliente para análise")


class ChurnPredictionResponse(BaseModel):
    """Response com previsão de churn"""
    
    cliente_id: str = Field(..., description="ID do cliente analisado")
    risk_level: str = Field(..., description="Nível de risco (baixo, medio, alto, critico)")
    risk_score: float = Field(..., ge=0, le=1, description="Score de risco (0-1)")
    predictions: Dict[str, float] = Field(..., description="Previsões de cada modelo")
    features_importance: Dict[str, float] = Field(..., description="Importância das features")
    recommendations: List[str] = Field(..., description="Recomendações baseadas no risco")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da previsão")


class ChurnTrainingResponse(BaseModel):
    """Response do treinamento de modelos"""
    
    message: str = Field(..., description="Mensagem sobre o status do treinamento")
    status: str = Field(..., description="Status do treinamento")
    estimated_time: str = Field(..., description="Tempo estimado para conclusão")
    training_id: Optional[str] = Field(None, description="ID do treinamento")


class ChurnInsightsResponse(BaseModel):
    """Response com insights gerais de churn"""
    
    total_clientes: int = Field(..., description="Total de clientes analisados")
    clientes_churn: int = Field(..., description="Número de clientes em churn")
    clientes_ativos: int = Field(..., description="Número de clientes ativos")
    taxa_churn_atual: float = Field(..., description="Taxa de churn atual (%)")
    clientes_risco_alto: int = Field(..., description="Clientes com risco alto de churn")
    clientes_risco_medio: int = Field(..., description="Clientes com risco médio de churn")
    clientes_risco_baixo: int = Field(..., description="Clientes com risco baixo de churn")
    insights_timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp dos insights")


class ModelInfo(BaseModel):
    """Informações sobre um modelo específico"""
    
    name: str = Field(..., description="Nome do modelo")
    type: str = Field(..., description="Tipo do modelo")
    accuracy: Optional[float] = Field(None, description="Acurácia do modelo")
    auc: Optional[float] = Field(None, description="AUC do modelo")
    feature_importance_available: bool = Field(..., description="Se tem importância de features")
    training_date: Optional[datetime] = Field(None, description="Data do treinamento")


class FeatureImportance(BaseModel):
    """Importância de uma feature específica"""
    
    feature_name: str = Field(..., description="Nome da feature")
    importance_score: float = Field(..., description="Score de importância")
    description: str = Field(..., description="Descrição da feature")
    category: str = Field(..., description="Categoria da feature")


class ChurnRiskAnalysis(BaseModel):
    """Análise de risco de churn para um cliente"""
    
    cliente_id: str = Field(..., description="ID do cliente")
    nome: str = Field(..., description="Nome do cliente")
    risk_level: str = Field(..., description="Nível de risco")
    risk_score: float = Field(..., description="Score de risco")
    health_score: float = Field(..., description="Health Score atual")
    dias_vencimento: int = Field(..., description="Dias para próximo vencimento")
    csat_medio: float = Field(..., description="CSAT médio")
    recommendations: List[str] = Field(..., description="Recomendações")
    last_interaction_days: Optional[int] = Field(None, description="Dias desde última interação")


class ChurnPredictionBatch(BaseModel):
    """Request para previsão em lote"""
    
    cliente_ids: List[str] = Field(..., description="Lista de IDs de clientes")
    include_features: bool = Field(True, description="Incluir análise de features")
    include_recommendations: bool = Field(True, description="Incluir recomendações")


class ChurnPredictionBatchResponse(BaseModel):
    """Response para previsão em lote"""
    
    total_processed: int = Field(..., description="Total de clientes processados")
    successful_predictions: int = Field(..., description="Previsões bem-sucedidas")
    failed_predictions: int = Field(..., description="Previsões que falharam")
    predictions: List[ChurnPredictionResponse] = Field(..., description="Lista de previsões")
    processing_time: float = Field(..., description="Tempo de processamento em segundos")


class ModelPerformanceMetrics(BaseModel):
    """Métricas de performance dos modelos"""
    
    model_name: str = Field(..., description="Nome do modelo")
    accuracy: float = Field(..., description="Acurácia")
    precision: float = Field(..., description="Precisão")
    recall: float = Field(..., description="Recall")
    f1_score: float = Field(..., description="F1-Score")
    auc: float = Field(..., description="AUC")
    confusion_matrix: Dict[str, int] = Field(..., description="Matriz de confusão")


class TrainingMetrics(BaseModel):
    """Métricas do treinamento"""
    
    training_id: str = Field(..., description="ID do treinamento")
    start_time: datetime = Field(..., description="Hora de início")
    end_time: Optional[datetime] = Field(None, description="Hora de conclusão")
    duration_minutes: Optional[float] = Field(None, description="Duração em minutos")
    total_samples: int = Field(..., description="Total de amostras")
    training_samples: int = Field(..., description="Amostras de treinamento")
    validation_samples: int = Field(..., description="Amostras de validação")
    models_performance: List[ModelPerformanceMetrics] = Field(..., description="Performance de cada modelo")
    best_model: str = Field(..., description="Nome do melhor modelo")
    overall_accuracy: float = Field(..., description="Acurácia geral")


class ChurnAlert(BaseModel):
    """Alerta de churn para um cliente"""
    
    cliente_id: str = Field(..., description="ID do cliente")
    alert_level: str = Field(..., description="Nível do alerta (baixo, medio, alto, critico)")
    risk_score: float = Field(..., description="Score de risco")
    trigger_factors: List[str] = Field(..., description="Fatores que dispararam o alerta")
    recommended_actions: List[str] = Field(..., description="Ações recomendadas")
    urgency: str = Field(..., description="Urgência (baixa, media, alta, critica)")
    created_at: datetime = Field(default_factory=datetime.now, description="Data de criação do alerta")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração do alerta")


class ChurnPreventionStrategy(BaseModel):
    """Estratégia de prevenção de churn"""
    
    strategy_id: str = Field(..., description="ID da estratégia")
    name: str = Field(..., description="Nome da estratégia")
    description: str = Field(..., description="Descrição da estratégia")
    target_risk_levels: List[str] = Field(..., description="Níveis de risco alvo")
    actions: List[str] = Field(..., description="Ações da estratégia")
    success_metrics: List[str] = Field(..., description="Métricas de sucesso")
    estimated_impact: str = Field(..., description="Impacto estimado")
    implementation_time: str = Field(..., description="Tempo de implementação")
    cost: Optional[str] = Field(None, description="Custo estimado")


class ChurnAnalytics(BaseModel):
    """Analytics avançados de churn"""
    
    period: str = Field(..., description="Período analisado")
    total_clients: int = Field(..., description="Total de clientes")
    churn_rate: float = Field(..., description="Taxa de churn")
    predicted_churn_rate: float = Field(..., description="Taxa de churn prevista")
    accuracy_prediction: float = Field(..., description="Acurácia das previsões")
    top_churn_factors: List[Dict[str, Any]] = Field(..., description="Principais fatores de churn")
    churn_trend: List[Dict[str, Any]] = Field(..., description="Tendência de churn ao longo do tempo")
    segment_analysis: Dict[str, Any] = Field(..., description="Análise por segmentos")
    revenue_impact: Dict[str, float] = Field(..., description="Impacto na receita")
    prevention_opportunities: List[str] = Field(..., description="Oportunidades de prevenção")


class ModelRetrainingSchedule(BaseModel):
    """Agendamento de retreinamento dos modelos"""
    
    schedule_id: str = Field(..., description="ID do agendamento")
    frequency: str = Field(..., description="Frequência (diario, semanal, mensal)")
    next_retraining: datetime = Field(..., description="Próximo retreinamento")
    auto_retrain: bool = Field(..., description="Retreinamento automático")
    min_accuracy_threshold: float = Field(..., description="Threshold mínimo de acurácia")
    data_freshness_days: int = Field(..., description="Dias para considerar dados frescos")
    notification_emails: List[str] = Field(..., description="Emails para notificação")
    active: bool = Field(..., description="Se o agendamento está ativo") 