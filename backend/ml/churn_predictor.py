"""
Sistema de Machine Learning para Previsão de Churn
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import joblib
import pickle
from pathlib import Path

# Machine Learning
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.utils.class_weight import compute_class_weight

# XGBoost e LightGBM
import xgboost as xgb
import lightgbm as lgb

# Deep Learning
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# Otimização de hiperparâmetros
import optuna

# Interpretabilidade
import shap

# Tratamento de dados desbalanceados
from imbalanced_learn.over_sampling import SMOTE
from imbalanced_learn.under_sampling import RandomUnderSampler

# Firebase
import firebase_admin
from firebase_admin import credentials, firestore

import logging
logger = logging.getLogger(__name__)

# Cache system
from .model_cache import model_cache

# Temporal validation
from .temporal_validation import TemporalCrossValidator, TemporalModelSelector

# Explainability
from .explainability import ExplainabilityService


class ChurnFeatureEngineer:
    """Engenheiro de features para previsão de churn"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def create_features(self, cliente_data: Dict, contrato_data: List[Dict], 
                       health_score_data: List[Dict], csat_data: List[Dict],
                       evento_data: List[Dict]) -> Dict[str, float]:
        """
        Cria features para previsão de churn baseado nos dados do cliente
        """
        features = {}
        
        # Features básicas do cliente
        features.update(self._extract_cliente_features(cliente_data))
        
        # Features de contratos
        features.update(self._extract_contrato_features(contrato_data))
        
        # Features de Health Score
        features.update(self._extract_health_score_features(health_score_data))
        
        # Features de CSAT
        features.update(self._extract_csat_features(csat_data))
        
        # Features de eventos/interações
        features.update(self._extract_evento_features(evento_data))
        
        # Features derivadas e interações
        features.update(self._create_derived_features(features))
        
        return features
    
    def _extract_cliente_features(self, cliente: Dict) -> Dict[str, float]:
        """Extrai features básicas do cliente"""
        features = {}
        
        # LTV e tempo de relacionamento
        features['ltv_meses'] = float(cliente.get('ltv_meses', 0))
        features['ltv_valor'] = float(cliente.get('ltv_valor', 0))
        
        # Tempo desde o início da jornada
        if cliente.get('jornada_iniciada_em'):
            jornada_inicio = datetime.strptime(cliente['jornada_iniciada_em'], '%Y-%m-%d')
            features['dias_jornada'] = (datetime.now() - jornada_inicio).days
        else:
            features['dias_jornada'] = 0
        
        # Status do cliente (encoded)
        status = cliente.get('status_cliente', 'ativo')
        features['status_encoded'] = self._encode_categorical(status, 'status_cliente')
        
        return features
    
    def _extract_contrato_features(self, contratos: List[Dict]) -> Dict[str, float]:
        """Extrai features dos contratos"""
        features = {}
        
        if not contratos:
            # Cliente sem contratos
            features.update({
                'total_contratos': 0,
                'contratos_ativos': 0,
                'contratos_vencidos': 0,
                'valor_mensal_medio': 0,
                'ciclo_medio': 0,
                'dias_vencimento_proximo': 999,
                'percentual_renovacoes': 0,
                'auto_renovacao_ativa': 0
            })
            return features
        
        # Contadores e estatísticas
        total_contratos = len(contratos)
        contratos_ativos = sum(1 for c in contratos if c.get('status_contrato') == 'ativo')
        contratos_vencidos = sum(1 for c in contratos if c.get('status_contrato') == 'vencido')
        
        # Valores e ciclos
        valores_mensais = [float(c.get('valor_mensal', 0)) for c in contratos]
        ciclos = [int(c.get('ciclo_atual', 1)) for c in contratos]
        
        # Dias para vencimento do próximo contrato
        dias_vencimento = []
        for contrato in contratos:
            if contrato.get('data_fim'):
                data_fim = datetime.strptime(contrato['data_fim'], '%Y-%m-%d')
                dias = (data_fim - datetime.now()).days
                dias_vencimento.append(dias)
        
        # Renovações
        renovacoes = sum(1 for c in contratos if c.get('renovacoes'))
        auto_renovacao = sum(1 for c in contratos if c.get('auto_renovacao'))
        
        features.update({
            'total_contratos': total_contratos,
            'contratos_ativos': contratos_ativos,
            'contratos_vencidos': contratos_vencidos,
            'valor_mensal_medio': np.mean(valores_mensais) if valores_mensais else 0,
            'ciclo_medio': np.mean(ciclos) if ciclos else 0,
            'dias_vencimento_proximo': min(dias_vencimento) if dias_vencimento else 999,
            'percentual_renovacoes': (renovacoes / total_contratos) if total_contratos > 0 else 0,
            'auto_renovacao_ativa': auto_renovacao
        })
        
        return features
    
    def _extract_health_score_features(self, health_scores: List[Dict]) -> Dict[str, float]:
        """Extrai features do Health Score"""
        features = {}
        
        if not health_scores:
            # Cliente sem Health Score
            features.update({
                'health_score_atual': 50,  # Valor neutro
                'health_score_tendencia': 0,
                'nivel_risco_encoded': 2,  # Médio
                'componentes_baixos': 0,
                'ultima_avaliacao_dias': 999
            })
            return features
        
        # Última avaliação
        ultima_avaliacao = max(health_scores, key=lambda x: x.get('data_avaliacao', ''))
        
        # Health Score atual
        features['health_score_atual'] = float(ultima_avaliacao.get('health_score_total', 50))
        
        # Nível de risco
        nivel_risco = ultima_avaliacao.get('nivel_risco', 'medio')
        features['nivel_risco_encoded'] = self._encode_categorical(nivel_risco, 'nivel_risco')
        
        # Componentes baixos
        componentes_baixos = len(ultima_avaliacao.get('componentes_baixos', []))
        features['componentes_baixos'] = componentes_baixos
        
        # Dias desde última avaliação
        if ultima_avaliacao.get('data_avaliacao'):
            data_avaliacao = datetime.strptime(ultima_avaliacao['data_avaliacao'], '%Y-%m-%d')
            features['ultima_avaliacao_dias'] = (datetime.now() - data_avaliacao).days
        else:
            features['ultima_avaliacao_dias'] = 999
        
        # Tendência (comparando com avaliação anterior)
        if len(health_scores) > 1:
            penultima_avaliacao = sorted(health_scores, key=lambda x: x.get('data_avaliacao', ''))[-2]
            score_anterior = float(penultima_avaliacao.get('health_score_total', 50))
            features['health_score_tendencia'] = features['health_score_atual'] - score_anterior
        else:
            features['health_score_tendencia'] = 0
        
        return features
    
    def _extract_csat_features(self, csat_data: List[Dict]) -> Dict[str, float]:
        """Extrai features do CSAT"""
        features = {}
        
        if not csat_data:
            # Cliente sem CSAT
            features.update({
                'csat_medio': 3,  # Neutro
                'csat_tendencia': 0,
                'percentual_positivo': 0,
                'ultima_avaliacao_csat_dias': 999,
                'feedback_negativo_count': 0
            })
            return features
        
        # Avaliações
        avaliacoes = [float(c.get('avaliacao_call', 3)) for c in csat_data]
        features['csat_medio'] = np.mean(avaliacoes)
        
        # Percentual de avaliações positivas
        positivas = sum(1 for a in avaliacoes if a >= 4)
        features['percentual_positivo'] = positivas / len(avaliacoes)
        
        # Feedback negativo
        feedback_negativo = sum(1 for c in csat_data if c.get('tem_feedback_negativo', False))
        features['feedback_negativo_count'] = feedback_negativo
        
        # Dias desde última avaliação CSAT
        ultima_csat = max(csat_data, key=lambda x: x.get('data_resposta', ''))
        if ultima_csat.get('data_resposta'):
            data_resposta = datetime.strptime(ultima_csat['data_resposta'], '%Y-%m-%d')
            features['ultima_avaliacao_csat_dias'] = (datetime.now() - data_resposta).days
        else:
            features['ultima_avaliacao_csat_dias'] = 999
        
        # Tendência CSAT
        if len(csat_data) > 1:
            penultima_csat = sorted(csat_data, key=lambda x: x.get('data_resposta', ''))[-2]
            csat_anterior = float(penultima_csat.get('avaliacao_call', 3))
            features['csat_tendencia'] = features['csat_medio'] - csat_anterior
        else:
            features['csat_tendencia'] = 0
        
        return features
    
    def _extract_evento_features(self, eventos: List[Dict]) -> Dict[str, float]:
        """Extrai features dos eventos/interações"""
        features = {}
        
        if not eventos:
            # Cliente sem eventos
            features.update({
                'total_eventos': 0,
                'eventos_ultimos_30_dias': 0,
                'eventos_atrasados': 0,
                'eventos_urgentes': 0,
                'dias_ultima_interacao': 999
            })
            return features
        
        # Contadores
        total_eventos = len(eventos)
        eventos_ultimos_30_dias = sum(1 for e in eventos if e.get('is_recente', False))
        eventos_atrasados = sum(1 for e in eventos if e.get('is_atrasado', False))
        eventos_urgentes = sum(1 for e in eventos if e.get('is_urgente', False))
        
        # Dias desde última interação
        ultimo_evento = max(eventos, key=lambda x: x.get('data_evento', ''))
        if ultimo_evento.get('data_evento'):
            data_evento = datetime.strptime(ultimo_evento['data_evento'], '%Y-%m-%d')
            features['dias_ultima_interacao'] = (datetime.now() - data_evento).days
        else:
            features['dias_ultima_interacao'] = 999
        
        features.update({
            'total_eventos': total_eventos,
            'eventos_ultimos_30_dias': eventos_ultimos_30_dias,
            'eventos_atrasados': eventos_atrasados,
            'eventos_urgentes': eventos_urgentes
        })
        
        return features
    
    def _create_derived_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """Cria features derivadas e interações avançadas"""
        derived = {}
        
        # Interações entre features básicas
        derived['ltv_por_dia'] = features.get('ltv_valor', 0) / max(features.get('dias_jornada', 1), 1)
        derived['health_score_normalizado'] = features.get('health_score_atual', 50) / 100
        
        # Features temporais avançadas
        dias_jornada = features.get('dias_jornada', 0)
        if dias_jornada > 0:
            derived['jornada_anos'] = dias_jornada / 365.25
            derived['jornada_trimestres'] = dias_jornada / 90
            derived['maturidade_cliente'] = min(dias_jornada / 1095, 1.0)  # 3 anos = maturidade máxima
        else:
            derived['jornada_anos'] = 0
            derived['jornada_trimestres'] = 0
            derived['maturidade_cliente'] = 0
        
        # Features de valor financeiro
        valor_mensal = features.get('valor_mensal_medio', 0)
        total_contratos = features.get('total_contratos', 0)
        if total_contratos > 0:
            derived['valor_por_contrato'] = valor_mensal * total_contratos
            derived['densidade_valor'] = valor_mensal / max(total_contratos, 1)
        else:
            derived['valor_por_contrato'] = 0
            derived['densidade_valor'] = 0
        
        # Features de engajamento
        eventos_total = features.get('total_eventos', 0)
        if dias_jornada > 0:
            derived['frequencia_interacao'] = eventos_total / max(dias_jornada / 30, 1)  # eventos por mês
        else:
            derived['frequencia_interacao'] = 0
        
        # Indicador de cliente inativo
        dias_ultima_interacao = features.get('dias_ultima_interacao', 999)
        derived['inatividade_alta'] = 1 if dias_ultima_interacao > 60 else 0
        derived['inatividade_critica'] = 1 if dias_ultima_interacao > 120 else 0
        
        # Features de saúde do relacionamento
        health_score = features.get('health_score_atual', 50)
        csat_medio = features.get('csat_medio', 3)
        derived['saude_relacionamento'] = (health_score / 100 + csat_medio / 5) / 2
        
        # Features de risco temporal
        dias_vencimento = features.get('dias_vencimento_proximo', 999)
        derived['urgencia_renovacao'] = max(0, 1 - (dias_vencimento / 90))  # urgência cresce conforme se aproxima
        derived['risco_vencimento'] = 1 if dias_vencimento <= 30 else 0
        
        # Features de comportamento de pagamento
        auto_renovacao = features.get('auto_renovacao_ativa', 0)
        percentual_renovacoes = features.get('percentual_renovacoes', 0)
        derived['consistencia_renovacao'] = percentual_renovacoes * (1 + auto_renovacao)
        
        # Features de tendências
        health_tendencia = features.get('health_score_tendencia', 0)
        csat_tendencia = features.get('csat_tendencia', 0)
        derived['tendencia_positiva'] = 1 if (health_tendencia > 0 and csat_tendencia >= 0) else 0
        derived['tendencia_negativa'] = 1 if (health_tendencia < 0 and csat_tendencia < 0) else 0
        
        # Features de risco composto avançado
        risco_score = 0
        
        # Peso por Health Score (0-4 pontos)
        if health_score < 30:
            risco_score += 4
        elif health_score < 50:
            risco_score += 3
        elif health_score < 70:
            risco_score += 2
        elif health_score < 85:
            risco_score += 1
        
        # Peso por prazo de vencimento (0-3 pontos)
        if dias_vencimento <= 15:
            risco_score += 3
        elif dias_vencimento <= 30:
            risco_score += 2
        elif dias_vencimento <= 60:
            risco_score += 1
        
        # Peso por CSAT (0-3 pontos)
        if csat_medio < 2:
            risco_score += 3
        elif csat_medio < 3:
            risco_score += 2
        elif csat_medio < 4:
            risco_score += 1
        
        # Peso por inatividade (0-2 pontos)
        if dias_ultima_interacao > 90:
            risco_score += 2
        elif dias_ultima_interacao > 45:
            risco_score += 1
        
        # Peso por tendências negativas (0-2 pontos)
        if derived['tendencia_negativa']:
            risco_score += 2
        
        # Peso por valor (0-1 ponto) - clientes de alto valor têm prioridade
        if valor_mensal > 5000:  # threshold ajustável
            risco_score += 1
        
        derived['risco_composto'] = min(risco_score, 15)  # máximo 15 pontos
        derived['risco_normalizado'] = derived['risco_composto'] / 15
        
        # Features de segmentação
        derived['cliente_alto_valor'] = 1 if valor_mensal > 3000 else 0
        derived['cliente_longo_prazo'] = 1 if dias_jornada > 365 else 0
        derived['cliente_multiplos_contratos'] = 1 if total_contratos > 1 else 0
        
        # Features de satisfação avançadas
        feedback_negativo = features.get('feedback_negativo_count', 0)
        eventos_ultimos_30_dias = features.get('eventos_ultimos_30_dias', 0)
        if eventos_ultimos_30_dias > 0:
            derived['taxa_feedback_negativo'] = feedback_negativo / max(eventos_ultimos_30_dias, 1)
        else:
            derived['taxa_feedback_negativo'] = 0
        
        # Features de estabilidade
        contratos_vencidos = features.get('contratos_vencidos', 0)
        derived['instabilidade_contratual'] = contratos_vencidos / max(total_contratos, 1)
        
        return derived
    
    def _encode_categorical(self, value: str, field: str) -> int:
        """Codifica valores categóricos"""
        if field not in self.label_encoders:
            self.label_encoders[field] = LabelEncoder()
            # Define as categorias conhecidas
            if field == 'status_cliente':
                self.label_encoders[field].fit(['ativo', 'inativo', 'potencial', 'churn'])
            elif field == 'nivel_risco':
                self.label_encoders[field].fit(['baixo', 'medio', 'alto', 'critico'])
        
        try:
            return self.label_encoders[field].transform([value])[0]
        except:
            return 0  # Valor padrão se não reconhecido
    
    def get_feature_names(self) -> List[str]:
        """Retorna a lista de nomes das features"""
        return [
            # Features básicas do cliente
            'ltv_meses', 'ltv_valor', 'dias_jornada', 'status_encoded',
            
            # Features de contratos
            'total_contratos', 'contratos_ativos', 'contratos_vencidos',
            'valor_mensal_medio', 'ciclo_medio', 'dias_vencimento_proximo',
            'percentual_renovacoes', 'auto_renovacao_ativa',
            
            # Features de Health Score
            'health_score_atual', 'health_score_tendencia', 'nivel_risco_encoded',
            'componentes_baixos', 'ultima_avaliacao_dias',
            
            # Features de CSAT
            'csat_medio', 'csat_tendencia', 'percentual_positivo',
            'ultima_avaliacao_csat_dias', 'feedback_negativo_count',
            
            # Features de eventos
            'total_eventos', 'eventos_ultimos_30_dias', 'eventos_atrasados',
            'eventos_urgentes', 'dias_ultima_interacao',
            
            # Features derivadas básicas
            'ltv_por_dia', 'health_score_normalizado', 'risco_composto',
            
            # Features temporais avançadas
            'jornada_anos', 'jornada_trimestres', 'maturidade_cliente',
            
            # Features de valor financeiro
            'valor_por_contrato', 'densidade_valor',
            
            # Features de engajamento
            'frequencia_interacao', 'inatividade_alta', 'inatividade_critica',
            
            # Features de saúde do relacionamento
            'saude_relacionamento', 'urgencia_renovacao', 'risco_vencimento',
            
            # Features de comportamento
            'consistencia_renovacao', 'tendencia_positiva', 'tendencia_negativa',
            
            # Features de risco avançado
            'risco_normalizado',
            
            # Features de segmentação
            'cliente_alto_valor', 'cliente_longo_prazo', 'cliente_multiplos_contratos',
            
            # Features de satisfação avançadas
            'taxa_feedback_negativo', 'instabilidade_contratual'
        ]


class ChurnPredictor:
    """Sistema principal de previsão de churn"""
    
    def __init__(self, model_path: str = None):
        self.feature_engineer = ChurnFeatureEngineer()
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = self.feature_engineer.get_feature_names()
        self.explainability_service = ExplainabilityService()
        self.temporal_validation_results = None
        
        # Carrega modelos pré-treinados se existirem
        if model_path and Path(model_path).exists():
            self.load_models(model_path)
        else:
            self._initialize_models()
    
    def _initialize_models(self):
        """Inicializa os modelos de ML"""
        # Random Forest
        self.models['random_forest'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        # XGBoost
        self.models['xgboost'] = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            scale_pos_weight=1
        )
        
        # LightGBM
        self.models['lightgbm'] = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            class_weight='balanced'
        )
        
        # Neural Network
        self.models['neural_network'] = self._build_neural_network()
        
        # Ensemble será configurado após treinamento
        self.models['ensemble'] = None
    
    def _build_neural_network(self) -> keras.Model:
        """Constrói a rede neural"""
        model = keras.Sequential([
            layers.Dense(64, activation='relu', input_shape=(len(self.feature_names),)),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', 'auc']
        )
        
        return model
    
    def prepare_training_data(self, clientes_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara dados de treinamento"""
        X = []
        y = []
        
        for cliente in clientes_data:
            # Extrai features
            features = self.feature_engineer.create_features(
                cliente_data=cliente,
                contrato_data=cliente.get('contratos', []),
                health_score_data=cliente.get('health_scores', []),
                csat_data=cliente.get('csat_respostas', []),
                evento_data=cliente.get('eventos_cs', [])
            )
            
            # Converte para array
            feature_vector = [features.get(name, 0) for name in self.feature_names]
            X.append(feature_vector)
            
            # Label (1 = churn, 0 = não churn)
            is_churn = 1 if cliente.get('status_cliente') == 'churn' else 0
            y.append(is_churn)
        
        X = np.array(X)
        y = np.array(y)
        
        # Normaliza features
        X = self.scaler.fit_transform(X)
        
        return X, y
    
    def train_models(self, X: np.ndarray, y: np.ndarray, 
                    validation_split: float = 0.2,
                    use_temporal_validation: bool = False,
                    temporal_data: pd.DataFrame = None) -> Dict[str, float]:
        """
        Treina todos os modelos com opção de validação temporal
        
        Args:
            X: Features
            y: Target
            validation_split: Percentual para validação (se não usar temporal)
            use_temporal_validation: Se usar validação temporal
            temporal_data: DataFrame com dados temporais (deve ter coluna 'data_referencia')
        """
        if use_temporal_validation and temporal_data is not None:
            return self._train_with_temporal_validation(X, y, temporal_data)
        else:
            return self._train_with_standard_validation(X, y, validation_split)
    
    def _train_with_standard_validation(self, X: np.ndarray, y: np.ndarray, 
                                       validation_split: float) -> Dict[str, float]:
        """Treinamento com validação padrão"""
        # Split dos dados
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42, stratify=y
        )
        
        # Tratamento de dados desbalanceados
        smote = SMOTE(random_state=42)
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
        
        results = {}
        
        # Treina cada modelo
        for name, model in self.models.items():
            if name == 'ensemble':
                continue  # Será configurado no final
                
            if name == 'neural_network':
                # Treina rede neural
                history = model.fit(
                    X_train_balanced, y_train_balanced,
                    validation_data=(X_val, y_val),
                    epochs=50,
                    batch_size=32,
                    verbose=0
                )
                y_pred_proba = model.predict(X_val)
                if y_pred_proba.ndim > 1:
                    y_pred_proba = y_pred_proba[:, 0]
                y_pred = (y_pred_proba > 0.5).astype(int)
            else:
                # Treina modelos tradicionais
                model.fit(X_train_balanced, y_train_balanced)
                y_pred = model.predict(X_val)
                y_pred_proba = model.predict_proba(X_val)[:, 1]
            
            # Calcula métricas
            accuracy = np.mean(y_pred == y_val)
            auc = roc_auc_score(y_val, y_pred_proba)
            
            results[name] = {
                'accuracy': accuracy,
                'auc': auc,
                'training_samples': len(X_train_balanced),
                'validation_samples': len(X_val)
            }
            
            logger.info(f"Modelo {name}: Accuracy={accuracy:.3f}, AUC={auc:.3f}")
        
        # Configura ensemble
        self._setup_ensemble(X_train_balanced, y_train_balanced)
        
        return results
    
    def _train_with_temporal_validation(self, X: np.ndarray, y: np.ndarray, 
                                       temporal_data: pd.DataFrame) -> Dict[str, float]:
        """Treinamento com validação temporal"""
        logger.info("Iniciando treinamento com validação temporal")
        
        # Cria validador temporal
        temporal_validator = TemporalCrossValidator(
            train_months=6,    # 6 meses para treino
            validation_months=2,  # 2 meses para validação  
            test_months=1,     # 1 mês para teste
            step_months=1      # Passo de 1 mês
        )
        
        # Cria splits temporais
        splits = temporal_validator.create_temporal_splits(
            temporal_data, 
            date_column='data_referencia',
            min_samples_per_fold=50
        )
        
        if not splits:
            logger.warning("Sem splits temporais suficientes, usando validação padrão")
            return self._train_with_standard_validation(X, y, 0.2)
        
        # Seletor de modelos
        model_selector = TemporalModelSelector(temporal_validator)
        
        # Treina e avalia cada modelo
        models_to_test = {name: model for name, model in self.models.items() 
                         if name != 'ensemble'}
        
        comparison_results = model_selector.compare_models(
            models_to_test, X, y, splits
        )
        
        # Extrai melhores resultados para cada modelo
        results = {}
        for model_name, model_results in comparison_results['individual_results'].items():
            results[model_name] = {
                'accuracy': model_results['mean_metrics']['accuracy'],
                'auc': model_results['mean_metrics']['auc'],
                'f1': model_results['mean_metrics']['f1'],
                'precision': model_results['mean_metrics']['precision'],
                'recall': model_results['mean_metrics']['recall'],
                'temporal_stability': model_results['temporal_stability'],
                'training_samples': sum(split['train_size'] for split in splits),
                'validation_samples': sum(split['val_size'] for split in splits)
            }
        
        # Treina modelos finais com todos os dados
        self._train_final_models(X, y)
        
        # Salva resultados da validação temporal
        self.temporal_validation_results = comparison_results
        
        logger.info(f"Melhor modelo (validação temporal): {comparison_results['best_model']}")
        
        return results
    
    def _train_final_models(self, X: np.ndarray, y: np.ndarray):
        """Treina modelos finais com todos os dados"""
        # Balanceamento para treino final
        smote = SMOTE(random_state=42)
        X_balanced, y_balanced = smote.fit_resample(X, y)
        
        # Treina cada modelo com todos os dados
        for name, model in self.models.items():
            if name == 'ensemble':
                continue
                
            if name == 'neural_network':
                # Treina rede neural
                model.fit(
                    X_balanced, y_balanced,
                    epochs=100,  # Mais épocas para treino final
                    batch_size=32,
                    verbose=0,
                    validation_split=0.1
                )
            else:
                # Treina modelos tradicionais
                model.fit(X_balanced, y_balanced)
        
        # Configura ensemble final
        self._setup_ensemble(X_balanced, y_balanced)
        
        # Configura explicabilidade para todos os modelos
        self._setup_explainability()
    
    def _setup_ensemble(self, X_train: np.ndarray, y_train: np.ndarray):
        """Configura o modelo ensemble"""
        # Usa os melhores modelos para o ensemble
        best_models = {}
        for name, model in self.models.items():
            if name != 'ensemble' and model is not None:
                # Para neural networks, cria wrapper
                if name == 'neural_network':
                    from sklearn.base import BaseEstimator, ClassifierMixin
                    
                    class KerasClassifierWrapper(BaseEstimator, ClassifierMixin):
                        def __init__(self, model):
                            self.model = model
                        
                        def fit(self, X, y):
                            return self
                        
                        def predict_proba(self, X):
                            preds = self.model.predict(X)
                            if preds.ndim > 1 and preds.shape[1] == 1:
                                # Binary classification - create both probabilities
                                prob_1 = preds.flatten()
                                prob_0 = 1 - prob_1
                                return np.column_stack([prob_0, prob_1])
                            return preds
                        
                        def predict(self, X):
                            return (self.predict_proba(X)[:, 1] > 0.5).astype(int)
                    
                    best_models[name] = KerasClassifierWrapper(model)
                else:
                    best_models[name] = model
        
        if len(best_models) > 0:
            # Ensemble por votação
            from sklearn.ensemble import VotingClassifier
            estimators = [(name, model) for name, model in best_models.items()]
            self.models['ensemble'] = VotingClassifier(estimators=estimators, voting='soft')
            
            try:
                self.models['ensemble'].fit(X_train, y_train)
            except Exception as e:
                logger.warning(f"Erro ao treinar ensemble: {e}")
                # Fallback: usa apenas Random Forest
                self.models['ensemble'] = self.models.get('random_forest')
    
    def predict_churn(self, cliente_data: Dict, contrato_data: List[Dict],
                     health_score_data: List[Dict], csat_data: List[Dict],
                     evento_data: List[Dict]) -> Dict[str, float]:
        """Faz previsão de churn para um cliente"""
        cliente_id = cliente_data.get('id', 'unknown')
        
        # Verifica cache de features primeiro
        cached_features = model_cache.get_cached_features(cliente_id)
        
        if cached_features is None:
            # Extrai features se não estiver em cache
            features = self.feature_engineer.create_features(
                cliente_data, contrato_data, health_score_data, csat_data, evento_data
            )
            # Cache features para próxima vez
            model_cache.cache_features(cliente_id, features)
        else:
            features = cached_features
            logger.debug(f"Features recuperadas do cache para cliente {cliente_id}")
        
        # Gera hash das features para cache de predição
        features_hash = model_cache.create_features_hash(features)
        
        # Verifica cache de predição
        cached_prediction = model_cache.get_cached_prediction('ensemble', features_hash)
        if cached_prediction is not None:
            logger.debug(f"Predição recuperada do cache para cliente {cliente_id}")
            return cached_prediction
        
        # Se não tem cache, faz a predição
        feature_vector = [features.get(name, 0) for name in self.feature_names]
        X = np.array([feature_vector])
        
        # Normaliza
        X = self.scaler.transform(X)
        
        predictions = {}
        
        # Faz previsão com cada modelo
        for name, model in self.models.items():
            if model is None:
                continue
                
            try:
                if name == 'neural_network':
                    pred_raw = model.predict(X)
                    if pred_raw.ndim > 1:
                        pred = pred_raw[0][0]
                    else:
                        pred = pred_raw[0]
                else:
                    pred_proba = model.predict_proba(X)
                    if pred_proba.shape[1] > 1:
                        pred = pred_proba[0][1]  # Probabilidade da classe positiva
                    else:
                        pred = pred_proba[0][0]
                
                predictions[name] = float(pred)
            except Exception as e:
                logger.warning(f"Erro na predição do modelo {name}: {e}")
                continue
        
        # Média das previsões (ensemble)
        ensemble_pred = np.mean(list(predictions.values()))
        predictions['ensemble'] = ensemble_pred
        
        # Interpreta o resultado
        risk_level = self._interpret_risk(ensemble_pred)
        
        result = {
            'predictions': predictions,
            'risk_level': risk_level,
            'risk_score': ensemble_pred,
            'features_importance': self._get_feature_importance(features),
            'recommendations': self._get_recommendations(ensemble_pred, features)
        }
        
        # Cache o resultado
        model_cache.cache_model_prediction('ensemble', features_hash, result)
        
        return result
    
    def _interpret_risk(self, probability: float) -> str:
        """Interpreta o nível de risco baseado na probabilidade"""
        if probability < 0.3:
            return "baixo"
        elif probability < 0.6:
            return "medio"
        elif probability < 0.8:
            return "alto"
        else:
            return "critico"
    
    def _get_feature_importance(self, features: Dict[str, float]) -> Dict[str, float]:
        """Retorna a importância das features para o cliente"""
        # Usa SHAP para interpretabilidade
        try:
            explainer = shap.TreeExplainer(self.models['random_forest'])
            feature_vector = [features.get(name, 0) for name in self.feature_names]
            X = np.array([feature_vector])
            X = self.scaler.transform(X)
            
            shap_values = explainer.shap_values(X)
            importance = {}
            
            for i, name in enumerate(self.feature_names):
                importance[name] = float(abs(shap_values[1][0][i]))
            
            # Ordena por importância
            importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
            
            return importance
        except:
            # Fallback: importância baseada em correlação
            return {name: 1.0 for name in self.feature_names}
    
    def _get_recommendations(self, risk_probability: float, features: Dict[str, float]) -> List[str]:
        """Gera recomendações baseadas no risco e features"""
        recommendations = []
        
        if risk_probability > 0.7:
            recommendations.append("Cliente em alto risco de churn - ação imediata necessária")
        
        if features.get('health_score_atual', 50) < 40:
            recommendations.append("Health Score baixo - focar em melhorar engajamento")
        
        if features.get('dias_vencimento_proximo', 999) < 30:
            recommendations.append("Contrato vencendo em breve - priorizar renovação")
        
        if features.get('csat_medio', 3) < 3:
            recommendations.append("Satisfação baixa - investigar problemas de atendimento")
        
        if features.get('dias_ultima_interacao', 999) > 30:
            recommendations.append("Sem interação recente - reativar relacionamento")
        
        if features.get('contratos_vencidos', 0) > 0:
            recommendations.append("Contratos vencidos - resolver pendências")
        
        if not recommendations:
            recommendations.append("Cliente estável - manter acompanhamento regular")
        
        return recommendations
    
    def save_models(self, path: str):
        """Salva os modelos treinados"""
        Path(path).mkdir(parents=True, exist_ok=True)
        
        # Salva modelos tradicionais
        for name, model in self.models.items():
            if name != 'neural_network':
                model_path = Path(path) / f"{name}.pkl"
                joblib.dump(model, model_path)
        
        # Salva rede neural
        nn_path = Path(path) / "neural_network"
        self.models['neural_network'].save(nn_path)
        
        # Salva scaler e feature names
        scaler_path = Path(path) / "scaler.pkl"
        joblib.dump(self.scaler, scaler_path)
        
        # Salva feature engineer
        fe_path = Path(path) / "feature_engineer.pkl"
        joblib.dump(self.feature_engineer, fe_path)
        
        logger.info(f"Modelos salvos em: {path}")
    
    def load_models(self, path: str):
        """Carrega modelos salvos"""
        path = Path(path)
        
        # Carrega modelos tradicionais
        for name in ['random_forest', 'xgboost', 'lightgbm']:
            model_path = path / f"{name}.pkl"
            if model_path.exists():
                self.models[name] = joblib.load(model_path)
        
        # Carrega rede neural
        nn_path = path / "neural_network"
        if nn_path.exists():
            self.models['neural_network'] = keras.models.load_model(nn_path)
        
        # Carrega scaler e feature engineer
        scaler_path = path / "scaler.pkl"
        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
        
        fe_path = path / "feature_engineer.pkl"
        if fe_path.exists():
            self.feature_engineer = joblib.load(fe_path)
        
        logger.info(f"Modelos carregados de: {path}")
    
    def clear_client_cache(self, cliente_id: str):
        """Limpa cache para um cliente específico"""
        model_cache.invalidate_client_cache(cliente_id)
        logger.info(f"Cache limpo para cliente: {cliente_id}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do sistema de cache"""
        return model_cache.get_cache_stats()
    
    def _setup_explainability(self):
        """Configura explicabilidade para todos os modelos"""
        try:
            # Mapeia tipos de modelo para explicabilidade
            model_types = {
                'random_forest': 'tree',
                'xgboost': 'xgboost', 
                'lightgbm': 'lightgbm',
                'neural_network': 'neural',
                'ensemble': 'tree'  # VotingClassifier é tratado como tree
            }
            
            for model_name, model in self.models.items():
                if model is not None:
                    model_type = model_types.get(model_name, 'tree')
                    self.explainability_service.add_model_explainer(
                        model_name, model, self.feature_names, model_type
                    )
            
            logger.info("Sistema de explicabilidade configurado para todos os modelos")
            
        except Exception as e:
            logger.error(f"Erro ao configurar explicabilidade: {e}")
    
    def explain_prediction(self, 
                          cliente_data: Dict, 
                          contrato_data: List[Dict],
                          health_score_data: List[Dict], 
                          csat_data: List[Dict],
                          evento_data: List[Dict],
                          model_name: str = 'ensemble') -> Dict[str, Any]:
        """
        Explica uma previsão de churn com detalhes
        
        Args:
            cliente_data: Dados do cliente
            contrato_data: Dados de contratos
            health_score_data: Dados de health score
            csat_data: Dados de CSAT
            evento_data: Dados de eventos
            model_name: Modelo para explicação
            
        Returns:
            Explicação detalhada da previsão
        """
        try:
            # Extrai features
            features = self.feature_engineer.create_features(
                cliente_data, contrato_data, health_score_data, csat_data, evento_data
            )
            
            # Converte para array
            feature_vector = [features.get(name, 0) for name in self.feature_names]
            X = np.array([feature_vector])
            
            # Normaliza
            X_normalized = self.scaler.transform(X)
            
            # Faz previsão normal
            normal_prediction = self.predict_churn(
                cliente_data, contrato_data, health_score_data, csat_data, evento_data
            )
            
            # Explica com SHAP
            explanation = self.explainability_service.explain_prediction(
                model_name, X_normalized, include_text=True
            )
            
            # Combina resultados
            detailed_explanation = {
                'prediction_results': normal_prediction,
                'shap_explanation': explanation,
                'feature_values': features,
                'model_used': model_name,
                'explanation_quality': self._assess_explanation_quality(explanation)
            }
            
            return detailed_explanation
            
        except Exception as e:
            logger.error(f"Erro ao explicar previsão: {e}")
            return {
                'error': f'Erro ao gerar explicação: {str(e)}',
                'prediction_results': self.predict_churn(
                    cliente_data, contrato_data, health_score_data, csat_data, evento_data
                )
            }
    
    def compare_model_explanations(self,
                                  cliente_data: Dict,
                                  contrato_data: List[Dict],
                                  health_score_data: List[Dict], 
                                  csat_data: List[Dict],
                                  evento_data: List[Dict]) -> Dict[str, Any]:
        """
        Compara explicações entre diferentes modelos
        
        Args:
            [mesmo que explain_prediction]
            
        Returns:
            Comparação entre explicações de modelos
        """
        try:
            # Extrai e processa features
            features = self.feature_engineer.create_features(
                cliente_data, contrato_data, health_score_data, csat_data, evento_data
            )
            
            feature_vector = [features.get(name, 0) for name in self.feature_names]
            X_normalized = self.scaler.transform(np.array([feature_vector]))
            
            # Compara explicações entre modelos
            comparison = self.explainability_service.compare_model_explanations(
                X_normalized, models_to_compare=['random_forest', 'xgboost', 'lightgbm', 'ensemble']
            )
            
            # Adiciona contexto adicional
            comparison['feature_values'] = features
            comparison['model_consensus'] = self._analyze_model_consensus(comparison)
            
            return comparison
            
        except Exception as e:
            logger.error(f"Erro na comparação de explicações: {e}")
            return {'error': f'Erro na comparação: {str(e)}'}
    
    def _assess_explanation_quality(self, explanation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia a qualidade da explicação gerada
        
        Args:
            explanation: Resultado da explicação
            
        Returns:
            Métricas de qualidade
        """
        quality_assessment = {
            'has_shap_values': 'shap_values' in explanation and explanation['shap_values'] is not None,
            'has_feature_contributions': 'feature_contributions' in explanation and len(explanation['feature_contributions']) > 0,
            'has_textual_explanation': 'textual_explanation' in explanation and explanation['textual_explanation'],
            'explanation_completeness': 0,
            'confidence_level': 'unknown'
        }
        
        # Calcula completeness score
        completeness_score = 0
        if quality_assessment['has_shap_values']:
            completeness_score += 0.4
        if quality_assessment['has_feature_contributions']:
            completeness_score += 0.3
        if quality_assessment['has_textual_explanation']:
            completeness_score += 0.3
        
        quality_assessment['explanation_completeness'] = completeness_score
        
        # Determina nível de confiança
        if completeness_score >= 0.8:
            quality_assessment['confidence_level'] = 'high'
        elif completeness_score >= 0.5:
            quality_assessment['confidence_level'] = 'medium'
        else:
            quality_assessment['confidence_level'] = 'low'
        
        return quality_assessment
    
    def _analyze_model_consensus(self, comparison: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa consenso entre modelos nas explicações
        
        Args:
            comparison: Resultado da comparação
            
        Returns:
            Análise de consenso
        """
        if 'disagreement_analysis' not in comparison:
            return {}
        
        disagreement = comparison['disagreement_analysis']
        consensus_analysis = {
            'prediction_agreement': disagreement.get('models_agreement', 'unknown'),
            'prediction_variance': disagreement.get('prediction_variance', 0),
            'consensus_strength': 'strong',
            'reliable_prediction': True
        }
        
        # Determina força do consenso
        variance = disagreement.get('prediction_variance', 0)
        if variance > 0.05:  # Alta variância
            consensus_analysis['consensus_strength'] = 'weak'
            consensus_analysis['reliable_prediction'] = False
        elif variance > 0.02:  # Variância média
            consensus_analysis['consensus_strength'] = 'moderate'
        
        return consensus_analysis
    
    def generate_explanation_report(self, explanations: Dict[str, Any]) -> str:
        """
        Gera relatório completo das explicações
        
        Args:
            explanations: Resultado de explain_prediction
            
        Returns:
            Relatório formatado em markdown
        """
        report = []
        
        # Cabeçalho
        report.append("# Relatório de Explicação - Previsão de Churn\n")
        
        # Resumo da previsão
        if 'prediction_results' in explanations:
            pred = explanations['prediction_results']
            report.append("## Resumo da Previsão")
            report.append(f"- **Probabilidade de Churn**: {pred.get('risk_score', 0)*100:.1f}%")
            report.append(f"- **Nível de Risco**: {pred.get('risk_level', 'unknown').upper()}")
            report.append(f"- **Modelo Utilizado**: {explanations.get('model_used', 'ensemble')}")
            report.append("")
        
        # Explicação SHAP
        if 'shap_explanation' in explanations and 'textual_explanation' in explanations['shap_explanation']:
            report.append("## Análise Detalhada")
            report.append(explanations['shap_explanation']['textual_explanation'])
            report.append("")
        
        # Qualidade da explicação
        if 'explanation_quality' in explanations:
            quality = explanations['explanation_quality']
            report.append("## Qualidade da Explicação")
            report.append(f"- **Nível de Confiança**: {quality.get('confidence_level', 'unknown').upper()}")
            report.append(f"- **Completude**: {quality.get('explanation_completeness', 0)*100:.0f}%")
            report.append("")
        
        # Top features
        if ('shap_explanation' in explanations and 
            'top_positive_features' in explanations['shap_explanation']):
            
            report.append("## Principais Fatores de Risco")
            for i, factor in enumerate(explanations['shap_explanation']['top_positive_features'][:5], 1):
                feature_name = factor['feature'].replace('_', ' ').title()
                impact = factor['shap_value']
                report.append(f"{i}. **{feature_name}** (impacto: +{impact:.3f})")
            report.append("")
        
        return '\n'.join(report)


class ChurnMLService:
    """Serviço de ML para integração com a API"""
    
    def __init__(self, model_path: str = "models/churn"):
        self.predictor = ChurnPredictor(model_path)
        self.is_trained = False
        
        # Firebase
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("path/to/serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except:
            logger.warning("Firebase não configurado - usando apenas dados locais")
            self.db = None
    
    def train_from_database(self, db_session) -> Dict[str, float]:
        """Treina modelos com dados do banco"""
        # Busca dados de clientes
        from models.cliente import Cliente
        from models.contrato import Contrato
        from models.health_score_snapshot import HealthScoreSnapshot
        from models.csat_resposta import CSATResposta
        from models.evento_cs import EventoCS
        
        clientes = db_session.query(Cliente).all()
        
        # Prepara dados para treinamento
        training_data = []
        for cliente in clientes:
            cliente_dict = cliente.to_dict(include_relationships=True)
            training_data.append(cliente_dict)
        
        # Treina modelos
        X, y = self.predictor.prepare_training_data(training_data)
        results = self.predictor.train_models(X, y)
        
        self.is_trained = True
        
        # Salva modelos
        self.predictor.save_models("models/churn")
        
        return results
    
    def predict_client_churn(self, cliente_id: str, db_session) -> Dict[str, any]:
        """Preve churn para um cliente específico"""
        if not self.is_trained:
            return {"error": "Modelos não treinados"}
        
        # Busca dados do cliente
        from models.cliente import Cliente
        from models.contrato import Contrato
        from models.health_score_snapshot import HealthScoreSnapshot
        from models.csat_resposta import CSATResposta
        from models.evento_cs import EventoCS
        
        cliente = db_session.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            return {"error": "Cliente não encontrado"}
        
        # Busca dados relacionados
        contratos = db_session.query(Contrato).filter(Contrato.cliente_id == cliente_id).all()
        health_scores = db_session.query(HealthScoreSnapshot).filter(
            HealthScoreSnapshot.id_cliente == cliente_id
        ).all()
        csat_respostas = db_session.query(CSATResposta).filter(
            CSATResposta.id_cliente == cliente_id
        ).all()
        eventos = db_session.query(EventoCS).filter(EventoCS.cliente_id == cliente_id).all()
        
        # Converte para dicionários
        cliente_data = cliente.to_dict()
        contrato_data = [c.to_dict() for c in contratos]
        health_score_data = [h.to_dict() for h in health_scores]
        csat_data = [c.to_dict() for c in csat_respostas]
        evento_data = [e.to_dict() for e in eventos]
        
        # Faz previsão
        prediction = self.predictor.predict_churn(
            cliente_data, contrato_data, health_score_data, csat_data, evento_data
        )
        
        return prediction
    
    def get_churn_insights(self, db_session) -> Dict[str, any]:
        """Retorna insights gerais sobre churn"""
        if not self.is_trained:
            return {"error": "Modelos não treinados"}
        
        # Busca todos os clientes
        from models.cliente import Cliente
        clientes = db_session.query(Cliente).all()
        
        insights = {
            'total_clientes': len(clientes),
            'clientes_churn': sum(1 for c in clientes if c.status_cliente == 'churn'),
            'clientes_ativos': sum(1 for c in clientes if c.status_cliente == 'ativo'),
            'taxa_churn_atual': 0,
            'clientes_risco_alto': 0,
            'clientes_risco_medio': 0,
            'clientes_risco_baixo': 0
        }
        
        # Calcula taxa de churn
        if insights['total_clientes'] > 0:
            insights['taxa_churn_atual'] = (
                insights['clientes_churn'] / insights['total_clientes']
            ) * 100
        
        # Analisa risco dos clientes ativos
        for cliente in clientes:
            if cliente.status_cliente == 'ativo':
                prediction = self.predict_client_churn(cliente.id, db_session)
                if 'risk_level' in prediction:
                    risk = prediction['risk_level']
                    if risk == 'alto' or risk == 'critico':
                        insights['clientes_risco_alto'] += 1
                    elif risk == 'medio':
                        insights['clientes_risco_medio'] += 1
                    else:
                        insights['clientes_risco_baixo'] += 1
        
        return insights 