// src/services/mlApi.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const mlApi = axios.create({
  baseURL: `${API_BASE_URL}/ml-churn`,
  timeout: 30000, // 30 segundos para operações ML
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar auth token se existir
mlApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para tratar erros globalmente
mlApi.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('ML API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Interfaces TypeScript
export interface TrainingRequest {
  force_retrain?: boolean;
  validation_split?: number;
}

export interface TrainingResponse {
  message: string;
  status: 'training' | 'trained' | 'error';
  estimated_time: string;
  accuracy?: number;
  auc?: number;
  training_samples?: number;
  validation_samples?: number;
}

export interface ChurnPredictionRequest {
  cliente_id: string;
}

export interface ChurnPredictionResponse {
  cliente_id: string;
  risk_level: 'baixo' | 'medio' | 'alto' | 'critico';
  risk_score: number;
  predictions: Record<string, number>;
  features_importance: Record<string, number>;
  recommendations: string[];
}

export interface ChurnInsights {
  total_clientes: number;
  clientes_churn: number;
  clientes_ativos: number;
  taxa_churn_atual: number;
  clientes_risco_alto: number;
  clientes_risco_medio: number;
  clientes_risco_baixo: number;
}

export interface RiskAnalysisResponse {
  total_analyzed: number;
  high_risk_count: number;
  risk_threshold: number;
  high_risk_clients: Array<{
    cliente_id: string;
    nome: string;
    risk_level: string;
    risk_score: number;
    health_score: number;
    dias_vencimento: number;
    csat_medio: number;
    recommendations: string[];
  }>;
  risk_distribution: {
    baixo: number;
    medio: number;
    alto: number;
    critico: number;
  };
}

export interface ModelInfo {
  total_models: number;
  models: Record<string, {
    type: string;
    feature_importance_available: boolean;
    n_features?: number | string;
    architecture?: string;
    layers?: number;
  }>;
  feature_names: string[];
  n_features: number;
  is_trained: boolean;
}

export interface TrainingStatus {
  is_trained: boolean;
  status: 'trained' | 'not_trained' | 'training';
  last_training: string;
}

export interface HealthCheck {
  status: 'healthy' | 'warning' | 'unhealthy';
  ml_service_available: boolean;
  models_trained: boolean;
  total_models: number;
  feature_engineer_available: boolean;
  scaler_available: boolean;
  message?: string;
  error?: string;
}

// Funções da API
export const mlChurnApi = {
  // Treinamento
  async trainModels(request: TrainingRequest = {}): Promise<TrainingResponse> {
    const response = await mlApi.post<TrainingResponse>('/train', request);
    return response.data;
  },

  async getTrainingStatus(): Promise<TrainingStatus> {
    const response = await mlApi.get<TrainingStatus>('/train/status');
    return response.data;
  },

  async forceRetrain(): Promise<TrainingResponse> {
    const response = await mlApi.post<TrainingResponse>('/models/retrain');
    return response.data;
  },

  // Predições
  async predictChurn(request: ChurnPredictionRequest): Promise<ChurnPredictionResponse> {
    const response = await mlApi.post<ChurnPredictionResponse>('/predict', request);
    return response.data;
  },

  // Insights gerais
  async getChurnInsights(): Promise<ChurnInsights> {
    const response = await mlApi.get<ChurnInsights>('/insights');
    return response.data;
  },

  // Análise de risco
  async analyzeAllClientsRisk(
    limit: number = 100,
    riskThreshold: number = 0.5
  ): Promise<RiskAnalysisResponse> {
    const response = await mlApi.get<RiskAnalysisResponse>('/clients/risk-analysis', {
      params: { limit, risk_threshold: riskThreshold },
    });
    return response.data;
  },

  // Informações dos modelos
  async getModelsInfo(): Promise<ModelInfo> {
    const response = await mlApi.get<ModelInfo>('/models/info');
    return response.data;
  },

  // Health check
  async healthCheck(): Promise<HealthCheck> {
    const response = await mlApi.get<HealthCheck>('/health');
    return response.data;
  },
};

// Hook customizado para usar com React Query
export const ML_QUERY_KEYS = {
  trainingStatus: ['ml', 'training', 'status'] as const,
  churnInsights: ['ml', 'churn', 'insights'] as const,
  riskAnalysis: (limit: number, threshold: number) => 
    ['ml', 'risk', 'analysis', limit, threshold] as const,
  modelsInfo: ['ml', 'models', 'info'] as const,
  healthCheck: ['ml', 'health'] as const,
  prediction: (clienteId: string) => ['ml', 'prediction', clienteId] as const,
};

export default mlApi;