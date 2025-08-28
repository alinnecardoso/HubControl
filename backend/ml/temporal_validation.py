"""
Sistema de Validação Cruzada Temporal para Modelos de Churn
"""
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import ParameterGrid
from sklearn.inspection import permutation_importance
import joblib
from pathlib import Path

logger = logging.getLogger(__name__)


class TemporalCrossValidator:
    """
    Implementa validação cruzada temporal específica para dados de churn
    """
    
    def __init__(self, 
                 train_months: int = 12,
                 validation_months: int = 3,
                 test_months: int = 1,
                 step_months: int = 1):
        """
        Inicializa o validador temporal
        
        Args:
            train_months: Meses para treinamento
            validation_months: Meses para validação
            test_months: Meses para teste
            step_months: Passo entre folds (em meses)
        """
        self.train_months = train_months
        self.validation_months = validation_months
        self.test_months = test_months
        self.step_months = step_months
    
    def create_temporal_splits(self, 
                              data: pd.DataFrame, 
                              date_column: str = 'data_referencia',
                              min_samples_per_fold: int = 100) -> List[Dict[str, Any]]:
        """
        Cria splits temporais para validação cruzada
        
        Args:
            data: DataFrame com os dados
            date_column: Nome da coluna de data
            min_samples_per_fold: Mínimo de amostras por fold
            
        Returns:
            Lista de dicionários com índices de train/val/test
        """
        splits = []
        
        # Converte datas se necessário
        if data[date_column].dtype == 'object':
            data[date_column] = pd.to_datetime(data[date_column])
        
        # Ordena por data
        data_sorted = data.sort_values(date_column).reset_index(drop=True)
        
        # Encontra período total dos dados
        start_date = data_sorted[date_column].min()
        end_date = data_sorted[date_column].max()
        
        # Calcula total de meses disponíveis
        total_months = ((end_date.year - start_date.year) * 12 + 
                       (end_date.month - start_date.month))
        
        # Mínimo de meses necessário para um fold
        min_months_needed = self.train_months + self.validation_months + self.test_months
        
        if total_months < min_months_needed:
            raise ValueError(f"Dados insuficientes. Necessário {min_months_needed} meses, "
                           f"disponível {total_months} meses")
        
        # Cria folds temporais
        current_start = start_date
        fold_id = 0
        
        while True:
            # Define períodos do fold atual
            train_start = current_start
            train_end = train_start + pd.DateOffset(months=self.train_months)
            
            val_start = train_end
            val_end = val_start + pd.DateOffset(months=self.validation_months)
            
            test_start = val_end
            test_end = test_start + pd.DateOffset(months=self.test_months)
            
            # Verifica se ainda temos dados suficientes
            if test_end > end_date:
                break
            
            # Filtra dados por período
            train_mask = ((data_sorted[date_column] >= train_start) & 
                         (data_sorted[date_column] < train_end))
            val_mask = ((data_sorted[date_column] >= val_start) & 
                       (data_sorted[date_column] < val_end))
            test_mask = ((data_sorted[date_column] >= test_start) & 
                        (data_sorted[date_column] < test_end))
            
            train_idx = data_sorted[train_mask].index.tolist()
            val_idx = data_sorted[val_mask].index.tolist()
            test_idx = data_sorted[test_mask].index.tolist()
            
            # Verifica se há amostras suficientes
            if (len(train_idx) >= min_samples_per_fold and 
                len(val_idx) >= min_samples_per_fold and 
                len(test_idx) >= min_samples_per_fold):
                
                splits.append({
                    'fold_id': fold_id,
                    'train_idx': train_idx,
                    'val_idx': val_idx,
                    'test_idx': test_idx,
                    'train_period': (train_start, train_end),
                    'val_period': (val_start, val_end),
                    'test_period': (test_start, test_end),
                    'train_size': len(train_idx),
                    'val_size': len(val_idx),
                    'test_size': len(test_idx)
                })
                
                fold_id += 1
            
            # Avança para próximo fold
            current_start = current_start + pd.DateOffset(months=self.step_months)
        
        logger.info(f"Criados {len(splits)} folds temporais")
        return splits
    
    def validate_model(self, 
                      model, 
                      X: np.ndarray, 
                      y: np.ndarray, 
                      splits: List[Dict[str, Any]],
                      fit_params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Executa validação temporal de um modelo
        
        Args:
            model: Modelo scikit-learn
            X: Features
            y: Target
            splits: Splits temporais
            fit_params: Parâmetros para fit
            
        Returns:
            Resultados da validação
        """
        if fit_params is None:
            fit_params = {}
        
        results = {
            'fold_results': [],
            'mean_metrics': {},
            'std_metrics': {},
            'temporal_stability': {}
        }
        
        fold_metrics = []
        fold_predictions = []
        
        for split in splits:
            fold_id = split['fold_id']
            train_idx = split['train_idx']
            val_idx = split['val_idx']
            test_idx = split['test_idx']
            
            # Treina modelo no período de treino
            X_train = X[train_idx]
            y_train = y[train_idx]
            
            # Clona modelo para evitar interferência entre folds
            from sklearn.base import clone
            model_fold = clone(model)
            model_fold.fit(X_train, y_train, **fit_params)
            
            # Avalia no período de validação
            X_val = X[val_idx]
            y_val = y[val_idx]
            
            if hasattr(model_fold, 'predict_proba'):
                y_val_pred_proba = model_fold.predict_proba(X_val)[:, 1]
            else:
                y_val_pred_proba = model_fold.decision_function(X_val)
            
            y_val_pred = model_fold.predict(X_val)
            
            # Calcula métricas
            metrics = {
                'fold_id': fold_id,
                'accuracy': accuracy_score(y_val, y_val_pred),
                'precision': precision_score(y_val, y_val_pred, zero_division=0),
                'recall': recall_score(y_val, y_val_pred, zero_division=0),
                'f1': f1_score(y_val, y_val_pred, zero_division=0),
                'auc': roc_auc_score(y_val, y_val_pred_proba) if len(np.unique(y_val)) > 1 else 0,
                'train_period': split['train_period'],
                'val_period': split['val_period'],
                'train_size': len(train_idx),
                'val_size': len(val_idx),
                'churn_rate_train': y_train.mean(),
                'churn_rate_val': y_val.mean()
            }
            
            fold_metrics.append(metrics)
            fold_predictions.append({
                'fold_id': fold_id,
                'val_idx': val_idx,
                'y_true': y_val,
                'y_pred': y_val_pred,
                'y_pred_proba': y_val_pred_proba
            })
            
            results['fold_results'].append(metrics)
            
            logger.info(f"Fold {fold_id}: AUC={metrics['auc']:.3f}, "
                       f"F1={metrics['f1']:.3f}, Acc={metrics['accuracy']:.3f}")
        
        # Calcula métricas agregadas
        metric_names = ['accuracy', 'precision', 'recall', 'f1', 'auc']
        for metric in metric_names:
            values = [fold[metric] for fold in fold_metrics]
            results['mean_metrics'][metric] = np.mean(values)
            results['std_metrics'][metric] = np.std(values)
        
        # Analisa estabilidade temporal
        results['temporal_stability'] = self._analyze_temporal_stability(fold_metrics)
        
        # Salva predições para análise posterior
        results['predictions'] = fold_predictions
        
        return results
    
    def _analyze_temporal_stability(self, fold_metrics: List[Dict]) -> Dict[str, float]:
        """
        Analisa estabilidade temporal dos modelos
        
        Args:
            fold_metrics: Métricas por fold
            
        Returns:
            Métricas de estabilidade
        """
        # Ordena folds por tempo
        fold_metrics_sorted = sorted(fold_metrics, key=lambda x: x['fold_id'])
        
        # Calcula tendências
        fold_ids = [fold['fold_id'] for fold in fold_metrics_sorted]
        aucs = [fold['auc'] for fold in fold_metrics_sorted]
        f1s = [fold['f1'] for fold in fold_metrics_sorted]
        
        # Correlação com tempo (detecta degradação temporal)
        auc_temporal_corr = np.corrcoef(fold_ids, aucs)[0, 1] if len(aucs) > 1 else 0
        f1_temporal_corr = np.corrcoef(fold_ids, f1s)[0, 1] if len(f1s) > 1 else 0
        
        # Variabilidade (menor é melhor)
        auc_cv = np.std(aucs) / max(np.mean(aucs), 1e-8)  # Coefficient of variation
        f1_cv = np.std(f1s) / max(np.mean(f1s), 1e-8)
        
        # Drift de churn rate entre folds
        churn_rates = [fold['churn_rate_val'] for fold in fold_metrics_sorted]
        churn_rate_drift = max(churn_rates) - min(churn_rates) if churn_rates else 0
        
        return {
            'auc_temporal_correlation': auc_temporal_corr,
            'f1_temporal_correlation': f1_temporal_corr,
            'auc_coefficient_variation': auc_cv,
            'f1_coefficient_variation': f1_cv,
            'churn_rate_drift': churn_rate_drift,
            'performance_decline': -min(auc_temporal_corr, f1_temporal_corr)  # Positivo se há declínio
        }
    
    def hyperparameter_tuning_temporal(self,
                                     model,
                                     param_grid: Dict,
                                     X: np.ndarray,
                                     y: np.ndarray,
                                     splits: List[Dict[str, Any]],
                                     scoring: str = 'auc',
                                     n_jobs: int = 1) -> Dict[str, Any]:
        """
        Otimização de hiperparâmetros com validação temporal
        
        Args:
            model: Modelo base
            param_grid: Grid de parâmetros
            X: Features
            y: Target
            splits: Splits temporais
            scoring: Métrica para otimização
            n_jobs: Jobs paralelos
            
        Returns:
            Melhores parâmetros e resultados
        """
        best_score = -np.inf
        best_params = None
        all_results = []
        
        # Gera combinações de parâmetros
        param_combinations = list(ParameterGrid(param_grid))
        
        logger.info(f"Testando {len(param_combinations)} combinações de parâmetros")
        
        for i, params in enumerate(param_combinations):
            # Configura modelo com parâmetros
            from sklearn.base import clone
            model_test = clone(model)
            model_test.set_params(**params)
            
            # Executa validação temporal
            results = self.validate_model(model_test, X, y, splits)
            
            # Obtém score
            score = results['mean_metrics'][scoring]
            
            result_entry = {
                'params': params,
                'score': score,
                'score_std': results['std_metrics'][scoring],
                'stability': results['temporal_stability'],
                'detailed_results': results
            }
            
            all_results.append(result_entry)
            
            # Atualiza melhor resultado
            if score > best_score:
                best_score = score
                best_params = params
            
            if (i + 1) % 10 == 0:
                logger.info(f"Progresso: {i + 1}/{len(param_combinations)} "
                          f"(melhor {scoring}: {best_score:.3f})")
        
        # Ordena resultados por score
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'all_results': all_results,
            'n_combinations_tested': len(param_combinations)
        }
    
    def save_validation_results(self, 
                               results: Dict[str, Any], 
                               file_path: str):
        """
        Salva resultados da validação temporal
        
        Args:
            results: Resultados da validação
            file_path: Caminho para salvar
        """
        # Remove predictions para economizar espaço
        results_to_save = results.copy()
        if 'predictions' in results_to_save:
            del results_to_save['predictions']
        
        joblib.dump(results_to_save, file_path)
        logger.info(f"Resultados salvos em: {file_path}")
    
    def load_validation_results(self, file_path: str) -> Dict[str, Any]:
        """
        Carrega resultados salvos
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Resultados carregados
        """
        return joblib.load(file_path)


class TemporalModelSelector:
    """
    Seletor de modelos baseado em validação temporal
    """
    
    def __init__(self, temporal_validator: TemporalCrossValidator):
        self.validator = temporal_validator
        self.model_results = {}
    
    def compare_models(self,
                      models: Dict[str, Any],
                      X: np.ndarray,
                      y: np.ndarray,
                      splits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compara múltiplos modelos usando validação temporal
        
        Args:
            models: Dicionário {nome: modelo}
            X: Features
            y: Target
            splits: Splits temporais
            
        Returns:
            Resultados da comparação
        """
        results = {}
        
        for model_name, model in models.items():
            logger.info(f"Avaliando modelo: {model_name}")
            
            model_results = self.validator.validate_model(model, X, y, splits)
            results[model_name] = model_results
            
            # Salva para comparação posterior
            self.model_results[model_name] = model_results
        
        # Cria ranking
        ranking = self._create_model_ranking(results)
        
        return {
            'individual_results': results,
            'ranking': ranking,
            'best_model': ranking[0]['model_name'],
            'summary': self._create_summary(results)
        }
    
    def _create_model_ranking(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Cria ranking de modelos baseado em múltiplas métricas
        """
        ranking_data = []
        
        for model_name, model_results in results.items():
            # Score composto considerando performance e estabilidade
            auc_score = model_results['mean_metrics']['auc']
            f1_score = model_results['mean_metrics']['f1']
            stability_score = (1 - model_results['temporal_stability']['performance_decline'])
            
            # Score composto (70% performance, 30% estabilidade)
            composite_score = (0.7 * (auc_score + f1_score) / 2) + (0.3 * stability_score)
            
            ranking_data.append({
                'model_name': model_name,
                'composite_score': composite_score,
                'auc_mean': auc_score,
                'f1_mean': f1_score,
                'auc_std': model_results['std_metrics']['auc'],
                'f1_std': model_results['std_metrics']['f1'],
                'stability_score': stability_score,
                'performance_decline': model_results['temporal_stability']['performance_decline']
            })
        
        # Ordena por score composto
        ranking_data.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return ranking_data
    
    def _create_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria resumo dos resultados
        """
        summary = {
            'total_models': len(results),
            'best_auc': max(r['mean_metrics']['auc'] for r in results.values()),
            'best_f1': max(r['mean_metrics']['f1'] for r in results.values()),
            'most_stable': None,
            'least_stable': None
        }
        
        # Encontra modelos mais e menos estáveis
        stabilities = {name: r['temporal_stability']['performance_decline'] 
                      for name, r in results.items()}
        
        summary['most_stable'] = min(stabilities, key=stabilities.get)
        summary['least_stable'] = max(stabilities, key=stabilities.get)
        
        return summary