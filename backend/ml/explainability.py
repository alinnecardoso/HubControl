"""
Sistema de Explicabilidade para Modelos de Churn
Utiliza SHAP e outras técnicas para interpretar previsões
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
import shap
from sklearn.inspection import permutation_importance
import logging

logger = logging.getLogger(__name__)


class ChurnExplainer:
    """
    Sistema de explicabilidade para modelos de churn
    """
    
    def __init__(self, model, feature_names: List[str], model_type: str = 'tree'):
        """
        Inicializa o explicador
        
        Args:
            model: Modelo treinado
            feature_names: Lista de nomes das features
            model_type: Tipo do modelo ('tree', 'linear', 'neural')
        """
        self.model = model
        self.feature_names = feature_names
        self.model_type = model_type
        self.explainer = None
        self.global_explanations = {}
        
        # Inicializa explicador SHAP baseado no tipo de modelo
        self._initialize_shap_explainer()
    
    def _initialize_shap_explainer(self):
        """Inicializa o explicador SHAP apropriado"""
        try:
            if self.model_type in ['tree', 'forest', 'xgboost', 'lightgbm']:
                self.explainer = shap.TreeExplainer(self.model)
                logger.info("Inicializado TreeExplainer")
                
            elif self.model_type == 'linear':
                self.explainer = shap.LinearExplainer(self.model)
                logger.info("Inicializado LinearExplainer")
                
            elif self.model_type == 'neural':
                # Para redes neurais, usa KernelExplainer (mais lento mas funciona)
                # Cria dataset de background pequeno para eficiência
                self.explainer = None  # Será inicializado quando necessário
                logger.info("KernelExplainer será inicializado quando necessário")
                
            else:
                # Explainer genérico para outros modelos
                self.explainer = None
                logger.warning(f"Tipo de modelo {self.model_type} não suportado diretamente")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar explicador SHAP: {e}")
            self.explainer = None
    
    def explain_instance(self, 
                        X_instance: np.ndarray,
                        background_data: np.ndarray = None) -> Dict[str, Any]:
        """
        Explica uma previsão individual
        
        Args:
            X_instance: Instância para explicar (shape: 1, n_features)
            background_data: Dados de background para KernelExplainer
            
        Returns:
            Explicações da instância
        """
        if X_instance.ndim == 1:
            X_instance = X_instance.reshape(1, -1)
        
        explanations = {
            'shap_values': None,
            'shap_expected_value': None,
            'feature_contributions': {},
            'top_positive_features': [],
            'top_negative_features': [],
            'prediction': None,
            'prediction_proba': None
        }
        
        try:
            # Faz predição
            explanations['prediction'] = self.model.predict(X_instance)[0]
            if hasattr(self.model, 'predict_proba'):
                explanations['prediction_proba'] = self.model.predict_proba(X_instance)[0]
            elif hasattr(self.model, 'decision_function'):
                explanations['prediction_proba'] = self.model.decision_function(X_instance)[0]
            
            # Calcula valores SHAP
            shap_values = self._calculate_shap_values(X_instance, background_data)
            
            if shap_values is not None:
                explanations['shap_values'] = shap_values[0]  # Primeira (e única) instância
                explanations['shap_expected_value'] = self.explainer.expected_value
                
                # Se é classificação binária, pega valores da classe positiva
                if isinstance(shap_values[0], list) or shap_values[0].ndim > 1:
                    if hasattr(self.explainer, 'expected_value') and isinstance(self.explainer.expected_value, (list, np.ndarray)):
                        explanations['shap_expected_value'] = self.explainer.expected_value[1]
                        explanations['shap_values'] = shap_values[0][:, 1] if shap_values[0].ndim > 1 else shap_values[0]
                    else:
                        explanations['shap_values'] = shap_values[0]
                
                # Calcula contribuições por feature
                feature_contributions = {}
                for i, feature_name in enumerate(self.feature_names):
                    if i < len(explanations['shap_values']):
                        feature_contributions[feature_name] = {
                            'shap_value': float(explanations['shap_values'][i]),
                            'feature_value': float(X_instance[0][i]),
                            'contribution_magnitude': abs(float(explanations['shap_values'][i]))
                        }
                
                explanations['feature_contributions'] = feature_contributions
                
                # Ordena features por contribuição
                sorted_contributions = sorted(
                    feature_contributions.items(), 
                    key=lambda x: x[1]['shap_value'], 
                    reverse=True
                )
                
                # Top features positivas (aumentam risco)
                explanations['top_positive_features'] = [
                    {
                        'feature': name,
                        'shap_value': contrib['shap_value'],
                        'feature_value': contrib['feature_value'],
                        'rank': i + 1
                    }
                    for i, (name, contrib) in enumerate(sorted_contributions)
                    if contrib['shap_value'] > 0
                ][:5]
                
                # Top features negativas (diminuem risco)
                explanations['top_negative_features'] = [
                    {
                        'feature': name,
                        'shap_value': contrib['shap_value'],
                        'feature_value': contrib['feature_value'],
                        'rank': i + 1
                    }
                    for i, (name, contrib) in enumerate(reversed(sorted_contributions))
                    if contrib['shap_value'] < 0
                ][:5]
            
        except Exception as e:
            logger.error(f"Erro ao explicar instância: {e}")
        
        return explanations
    
    def _calculate_shap_values(self, 
                              X: np.ndarray, 
                              background_data: np.ndarray = None) -> np.ndarray:
        """Calcula valores SHAP de forma robusta"""
        if self.explainer is None:
            if self.model_type == 'neural' and background_data is not None:
                # Inicializa KernelExplainer para redes neurais
                try:
                    # Usa amostra pequena do background para eficiência
                    bg_sample = background_data[:100] if len(background_data) > 100 else background_data
                    self.explainer = shap.KernelExplainer(self.model.predict_proba, bg_sample)
                    logger.info("KernelExplainer inicializado para rede neural")
                except Exception as e:
                    logger.error(f"Erro ao inicializar KernelExplainer: {e}")
                    return None
            else:
                logger.warning("Explainer não disponível")
                return None
        
        try:
            shap_values = self.explainer.shap_values(X)
            return shap_values
        except Exception as e:
            logger.error(f"Erro ao calcular valores SHAP: {e}")
            return None
    
    def explain_global(self, 
                      X_sample: np.ndarray, 
                      max_features: int = 20) -> Dict[str, Any]:
        """
        Gera explicações globais do modelo
        
        Args:
            X_sample: Amostra de dados para análise global
            max_features: Número máximo de features para mostrar
            
        Returns:
            Explicações globais
        """
        global_explanations = {
            'feature_importance_shap': {},
            'feature_importance_permutation': {},
            'feature_interactions': {},
            'summary_statistics': {}
        }
        
        try:
            # SHAP feature importance
            shap_values = self._calculate_shap_values(X_sample)
            
            if shap_values is not None:
                # Se é classificação binária, pega classe positiva
                if isinstance(shap_values, list):
                    shap_vals_to_use = shap_values[1]
                elif shap_values.ndim == 3:
                    shap_vals_to_use = shap_values[:, :, 1]
                else:
                    shap_vals_to_use = shap_values
                
                # Importância média absoluta
                mean_abs_shap = np.mean(np.abs(shap_vals_to_use), axis=0)
                
                for i, feature_name in enumerate(self.feature_names):
                    if i < len(mean_abs_shap):
                        global_explanations['feature_importance_shap'][feature_name] = float(mean_abs_shap[i])
            
            # Permutation importance (funciona para qualquer modelo)
            try:
                if hasattr(self.model, 'predict_proba'):
                    def scoring_fn(model, X, y):
                        return model.predict_proba(X)[:, 1].mean()
                else:
                    scoring_fn = None
                
                # Cria target dummy para permutation importance
                y_dummy = np.random.randint(0, 2, size=len(X_sample))
                
                perm_importance = permutation_importance(
                    self.model, X_sample, y_dummy, 
                    n_repeats=5, random_state=42,
                    scoring=scoring_fn if scoring_fn else None
                )
                
                for i, feature_name in enumerate(self.feature_names):
                    if i < len(perm_importance.importances_mean):
                        global_explanations['feature_importance_permutation'][feature_name] = float(
                            perm_importance.importances_mean[i]
                        )
                        
            except Exception as e:
                logger.warning(f"Erro no permutation importance: {e}")
            
            # Estatísticas sumárias
            if shap_values is not None:
                global_explanations['summary_statistics'] = {
                    'mean_prediction': float(np.mean(self.model.predict_proba(X_sample)[:, 1])) if hasattr(self.model, 'predict_proba') else None,
                    'total_samples': len(X_sample),
                    'mean_absolute_shap': float(np.mean(np.abs(shap_vals_to_use))),
                    'most_important_feature': max(global_explanations['feature_importance_shap'], 
                                                key=global_explanations['feature_importance_shap'].get) if global_explanations['feature_importance_shap'] else None
                }
            
            # Salva explicações globais
            self.global_explanations = global_explanations
            
        except Exception as e:
            logger.error(f"Erro nas explicações globais: {e}")
        
        return global_explanations
    
    def generate_textual_explanation(self, explanations: Dict[str, Any]) -> str:
        """
        Gera explicação textual amigável
        
        Args:
            explanations: Resultado de explain_instance
            
        Returns:
            Explicação em texto natural
        """
        if not explanations or 'prediction_proba' not in explanations:
            return "Não foi possível gerar explicação para esta previsão."
        
        # Probabilidade de churn
        if isinstance(explanations['prediction_proba'], (list, np.ndarray)):
            churn_prob = explanations['prediction_proba'][1] if len(explanations['prediction_proba']) > 1 else explanations['prediction_proba'][0]
        else:
            churn_prob = explanations['prediction_proba']
        
        churn_percent = churn_prob * 100
        
        # Nível de risco
        if churn_percent < 30:
            risk_level = "baixo"
        elif churn_percent < 60:
            risk_level = "médio"
        elif churn_percent < 80:
            risk_level = "alto"
        else:
            risk_level = "crítico"
        
        # Inicia explicação
        explanation = f"Este cliente tem {churn_percent:.1f}% de probabilidade de churn (risco {risk_level}).\n\n"
        
        # Fatores que aumentam o risco
        if explanations['top_positive_features']:
            explanation += "**Fatores que aumentam o risco de churn:**\n"
            for factor in explanations['top_positive_features']:
                feature_name = self._humanize_feature_name(factor['feature'])
                explanation += f"• {feature_name} (impacto: +{abs(factor['shap_value']):.2f})\n"
            explanation += "\n"
        
        # Fatores que diminuem o risco
        if explanations['top_negative_features']:
            explanation += "**Fatores que diminuem o risco de churn:**\n"
            for factor in explanations['top_negative_features']:
                feature_name = self._humanize_feature_name(factor['feature'])
                explanation += f"• {feature_name} (impacto: {factor['shap_value']:.2f})\n"
            explanation += "\n"
        
        # Recomendações
        explanation += "**Recomendações:**\n"
        explanation += self._generate_recommendations(explanations, risk_level)
        
        return explanation
    
    def _humanize_feature_name(self, feature_name: str) -> str:
        """Converte nome técnico da feature para descrição amigável"""
        
        feature_translations = {
            'health_score_atual': 'Health Score atual',
            'dias_vencimento_proximo': 'Dias até vencimento do contrato',
            'csat_medio': 'Satisfação média (CSAT)',
            'dias_ultima_interacao': 'Dias desde última interação',
            'ltv_valor': 'Valor do Lifetime Value',
            'total_contratos': 'Número total de contratos',
            'valor_mensal_medio': 'Valor mensal médio',
            'percentual_renovacoes': 'Taxa de renovação histórica',
            'tendencia_negativa': 'Tendência negativa recente',
            'inatividade_alta': 'Alta inatividade',
            'risco_vencimento': 'Risco de vencimento próximo',
            'saude_relacionamento': 'Saúde geral do relacionamento',
            'cliente_alto_valor': 'Cliente de alto valor',
            'instabilidade_contratual': 'Instabilidade nos contratos'
        }
        
        return feature_translations.get(feature_name, feature_name.replace('_', ' ').title())
    
    def _generate_recommendations(self, explanations: Dict[str, Any], risk_level: str) -> str:
        """Gera recomendações baseadas nas explicações"""
        
        recommendations = []
        
        # Recomendações baseadas no nível de risco
        if risk_level == 'crítico':
            recommendations.append("Contato imediato necessário - cliente em risco crítico de churn")
            recommendations.append("Escalar para gerente de contas sênior")
        elif risk_level == 'alto':
            recommendations.append("Agendar ligação de retenção nos próximos 2-3 dias")
            recommendations.append("Preparar oferta de retenção personalizada")
        elif risk_level == 'médio':
            recommendations.append("Monitorar closely e agendar check-in de rotina")
            recommendations.append("Considerar ações preventivas")
        else:
            recommendations.append("Cliente estável - manter acompanhamento regular")
        
        # Recomendações baseadas em features específicas
        if explanations['top_positive_features']:
            for factor in explanations['top_positive_features'][:3]:  # Top 3
                feature = factor['feature']
                
                if 'health_score' in feature and factor['shap_value'] > 0.1:
                    recommendations.append("Focar em melhorar o Health Score através de maior engajamento")
                
                if 'dias_vencimento' in feature and factor['shap_value'] > 0.1:
                    recommendations.append("Iniciar processo de renovação antecipada")
                
                if 'csat' in feature and factor['shap_value'] > 0.1:
                    recommendations.append("Investigar problemas de satisfação e implementar plano de melhoria")
                
                if 'ultima_interacao' in feature and factor['shap_value'] > 0.1:
                    recommendations.append("Reativar relacionamento - cliente pode estar sendo negligenciado")
        
        return '\n'.join(f"• {rec}" for rec in recommendations[:5])  # Máximo 5 recomendações
    
    def create_explanation_summary(self, explanations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria resumo estruturado das explicações
        
        Args:
            explanations: Resultado de explain_instance
            
        Returns:
            Resumo estruturado
        """
        summary = {
            'risk_assessment': {},
            'key_drivers': {},
            'recommendations': [],
            'confidence_indicators': {}
        }
        
        if 'prediction_proba' in explanations and explanations['prediction_proba'] is not None:
            # Avaliação de risco
            if isinstance(explanations['prediction_proba'], (list, np.ndarray)):
                churn_prob = explanations['prediction_proba'][1] if len(explanations['prediction_proba']) > 1 else explanations['prediction_proba'][0]
            else:
                churn_prob = explanations['prediction_proba']
            
            summary['risk_assessment'] = {
                'churn_probability': float(churn_prob),
                'risk_level': self._get_risk_level(churn_prob),
                'urgency': self._get_urgency_level(churn_prob)
            }
            
            # Principais direcionadores
            if explanations['top_positive_features']:
                summary['key_drivers']['risk_increasing'] = [
                    {
                        'factor': self._humanize_feature_name(f['feature']),
                        'impact_score': float(f['shap_value']),
                        'current_value': float(f['feature_value'])
                    }
                    for f in explanations['top_positive_features'][:3]
                ]
            
            if explanations['top_negative_features']:
                summary['key_drivers']['risk_decreasing'] = [
                    {
                        'factor': self._humanize_feature_name(f['feature']),
                        'impact_score': float(f['shap_value']),
                        'current_value': float(f['feature_value'])
                    }
                    for f in explanations['top_negative_features'][:3]
                ]
            
            # Indicadores de confiança
            if 'shap_values' in explanations and explanations['shap_values'] is not None:
                shap_magnitude = np.sum(np.abs(explanations['shap_values']))
                summary['confidence_indicators'] = {
                    'explanation_strength': float(shap_magnitude),
                    'prediction_stability': 'high' if shap_magnitude > 0.1 else 'medium' if shap_magnitude > 0.05 else 'low'
                }
        
        return summary
    
    def _get_risk_level(self, probability: float) -> str:
        """Determina nível de risco baseado na probabilidade"""
        if probability < 0.3:
            return 'baixo'
        elif probability < 0.6:
            return 'médio'
        elif probability < 0.8:
            return 'alto'
        else:
            return 'crítico'
    
    def _get_urgency_level(self, probability: float) -> str:
        """Determina nível de urgência baseado na probabilidade"""
        if probability < 0.3:
            return 'baixa'
        elif probability < 0.6:
            return 'média'
        elif probability < 0.8:
            return 'alta'
        else:
            return 'crítica'


class ExplainabilityService:
    """
    Serviço de explicabilidade para múltiplos modelos
    """
    
    def __init__(self):
        self.explainers = {}
    
    def add_model_explainer(self, 
                           model_name: str, 
                           model, 
                           feature_names: List[str], 
                           model_type: str):
        """Adiciona um explicador para um modelo"""
        self.explainers[model_name] = ChurnExplainer(model, feature_names, model_type)
        logger.info(f"Explicador adicionado para modelo: {model_name}")
    
    def explain_prediction(self, 
                          model_name: str, 
                          X_instance: np.ndarray,
                          include_text: bool = True) -> Dict[str, Any]:
        """
        Explica previsão de um modelo específico
        
        Args:
            model_name: Nome do modelo
            X_instance: Instância para explicar
            include_text: Se incluir explicação textual
            
        Returns:
            Explicações completas
        """
        if model_name not in self.explainers:
            return {'error': f'Modelo {model_name} não encontrado'}
        
        explainer = self.explainers[model_name]
        explanations = explainer.explain_instance(X_instance)
        
        # Adiciona resumo estruturado
        explanations['summary'] = explainer.create_explanation_summary(explanations)
        
        # Adiciona explicação textual se solicitado
        if include_text:
            explanations['textual_explanation'] = explainer.generate_textual_explanation(explanations)
        
        return explanations
    
    def compare_model_explanations(self, 
                                  X_instance: np.ndarray,
                                  models_to_compare: List[str] = None) -> Dict[str, Any]:
        """
        Compara explicações entre múltiplos modelos
        
        Args:
            X_instance: Instância para explicar
            models_to_compare: Lista de modelos (None = todos)
            
        Returns:
            Comparação das explicações
        """
        if models_to_compare is None:
            models_to_compare = list(self.explainers.keys())
        
        comparison = {
            'instance_explanations': {},
            'consensus_features': {},
            'disagreement_analysis': {}
        }
        
        # Explica para cada modelo
        all_explanations = {}
        for model_name in models_to_compare:
            if model_name in self.explainers:
                explanations = self.explain_prediction(model_name, X_instance, include_text=False)
                all_explanations[model_name] = explanations
                comparison['instance_explanations'][model_name] = explanations
        
        # Análise de consenso
        if len(all_explanations) > 1:
            comparison['consensus_features'] = self._analyze_feature_consensus(all_explanations)
            comparison['disagreement_analysis'] = self._analyze_disagreements(all_explanations)
        
        return comparison
    
    def _analyze_feature_consensus(self, all_explanations: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa consenso entre modelos sobre importância das features"""
        # Coleta importâncias das features de todos os modelos
        feature_impacts = {}
        
        for model_name, explanations in all_explanations.items():
            if 'feature_contributions' in explanations:
                for feature, contrib in explanations['feature_contributions'].items():
                    if feature not in feature_impacts:
                        feature_impacts[feature] = []
                    feature_impacts[feature].append(contrib['shap_value'])
        
        # Calcula métricas de consenso
        consensus_features = {}
        for feature, impacts in feature_impacts.items():
            if len(impacts) > 1:
                mean_impact = np.mean(impacts)
                std_impact = np.std(impacts)
                consensus_score = 1 - (std_impact / max(abs(mean_impact), 0.001))  # Maior consenso = menor variabilidade
                
                consensus_features[feature] = {
                    'mean_impact': float(mean_impact),
                    'std_impact': float(std_impact),
                    'consensus_score': float(max(0, consensus_score)),
                    'agreement_direction': 'positive' if mean_impact > 0 else 'negative',
                    'models_count': len(impacts)
                }
        
        return consensus_features
    
    def _analyze_disagreements(self, all_explanations: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa desacordos entre modelos"""
        predictions = {}
        
        # Coleta predições
        for model_name, explanations in all_explanations.items():
            if 'prediction_proba' in explanations:
                pred = explanations['prediction_proba']
                if isinstance(pred, (list, np.ndarray)) and len(pred) > 1:
                    predictions[model_name] = pred[1]  # Classe positiva
                else:
                    predictions[model_name] = pred
        
        if len(predictions) < 2:
            return {}
        
        pred_values = list(predictions.values())
        disagreement_analysis = {
            'prediction_variance': float(np.var(pred_values)),
            'prediction_range': float(max(pred_values) - min(pred_values)),
            'models_agreement': 'high' if np.std(pred_values) < 0.1 else 'medium' if np.std(pred_values) < 0.2 else 'low',
            'individual_predictions': {k: float(v) for k, v in predictions.items()}
        }
        
        return disagreement_analysis