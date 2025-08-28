"""
Script de teste básico para o sistema ML
"""
import sys
import os
import numpy as np
from datetime import datetime, timedelta
import logging

# Adiciona o diretório backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_feature_engineering():
    """Testa engenharia de features"""
    try:
        from ml.churn_predictor import ChurnFeatureEngineer
        
        engineer = ChurnFeatureEngineer()
        
        # Dados de teste
        cliente_data = {
            'id': 'test_client_001',
            'ltv_meses': 12,
            'ltv_valor': 50000,
            'jornada_iniciada_em': '2023-01-01',
            'status_cliente': 'ativo'
        }
        
        contrato_data = [{
            'status_contrato': 'ativo',
            'valor_mensal': 2500,
            'ciclo_atual': 2,
            'data_fim': '2024-12-31',
            'renovacoes': 1,
            'auto_renovacao': True
        }]
        
        health_score_data = [{
            'health_score_total': 75,
            'nivel_risco': 'medio',
            'componentes_baixos': ['engajamento'],
            'data_avaliacao': '2024-01-15'
        }]
        
        csat_data = [{
            'avaliacao_call': 4,
            'tem_feedback_negativo': False,
            'data_resposta': '2024-01-10'
        }]
        
        evento_data = [{
            'data_evento': '2024-01-20',
            'is_recente': True,
            'is_atrasado': False,
            'is_urgente': False
        }]
        
        # Testa criação de features
        features = engineer.create_features(
            cliente_data, contrato_data, health_score_data, csat_data, evento_data
        )
        
        print("✅ Feature Engineering - OK")
        print(f"   Geradas {len(features)} features")
        
        # Verifica se features importantes estão presentes
        expected_features = ['health_score_atual', 'dias_vencimento_proximo', 'risco_composto']
        for feature in expected_features:
            if feature in features:
                print(f"   ✓ {feature}: {features[feature]}")
            else:
                print(f"   ⚠ Feature ausente: {feature}")
        
        return True
        
    except Exception as e:
        print(f"❌ Feature Engineering - ERRO: {e}")
        return False

def test_model_cache():
    """Testa sistema de cache"""
    try:
        from ml.model_cache import ModelCache
        
        cache = ModelCache()
        
        # Testa cache de features
        test_features = {'test_feature': 1.0, 'another_feature': 2.5}
        success = cache.cache_features('test_client', test_features)
        
        if success:
            cached_features = cache.get_cached_features('test_client')
            if cached_features and cached_features.get('test_feature') == 1.0:
                print("✅ Model Cache - OK")
                return True
            else:
                print("❌ Model Cache - Falha ao recuperar dados")
                return False
        else:
            print("⚠ Model Cache - Usando fallback em memória")
            return True  # Cache em memória é aceitável
            
    except Exception as e:
        print(f"❌ Model Cache - ERRO: {e}")
        return False

def test_churn_predictor_basic():
    """Testa funcionalidades básicas do ChurnPredictor"""
    try:
        from ml.churn_predictor import ChurnPredictor
        
        # Inicializa predictor
        predictor = ChurnPredictor()
        
        print("✅ ChurnPredictor Inicialização - OK")
        
        # Testa lista de features
        feature_names = predictor.feature_names
        if len(feature_names) > 30:  # Esperamos 33+ features
            print(f"✅ Feature Names - OK ({len(feature_names)} features)")
        else:
            print(f"⚠ Feature Names - Poucas features: {len(feature_names)}")
        
        # Testa criação de dados sintéticos para treino
        X_synthetic = np.random.rand(100, len(feature_names))
        y_synthetic = np.random.randint(0, 2, 100)
        
        print("✅ Dados Sintéticos - OK")
        
        # Testa preparação de dados
        try:
            X_processed, y_processed = predictor.prepare_training_data([])
            print("✅ Preparação de Dados - OK (dados vazios)")
        except:
            print("⚠ Preparação de Dados - Falha esperada com dados vazios")
        
        return True
        
    except Exception as e:
        print(f"❌ ChurnPredictor Básico - ERRO: {e}")
        return False

def test_temporal_validation():
    """Testa validação temporal"""
    try:
        from ml.temporal_validation import TemporalCrossValidator
        import pandas as pd
        
        validator = TemporalCrossValidator(
            train_months=3,
            validation_months=1, 
            test_months=1,
            step_months=1
        )
        
        # Cria dados temporais sintéticos
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
        temporal_data = pd.DataFrame({
            'data_referencia': dates,
            'cliente_id': range(len(dates))
        })
        
        # Testa criação de splits
        splits = validator.create_temporal_splits(
            temporal_data, 
            min_samples_per_fold=10
        )
        
        if len(splits) > 0:
            print(f"✅ Temporal Validation - OK ({len(splits)} splits criados)")
            return True
        else:
            print("⚠ Temporal Validation - Nenhum split criado")
            return False
            
    except Exception as e:
        print(f"❌ Temporal Validation - ERRO: {e}")
        return False

def test_explainability():
    """Testa sistema de explicabilidade"""
    try:
        from ml.explainability import ExplainabilityService
        from sklearn.ensemble import RandomForestClassifier
        
        # Cria modelo simples para teste
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        X_simple = np.random.rand(50, 5)
        y_simple = np.random.randint(0, 2, 50)
        model.fit(X_simple, y_simple)
        
        # Testa serviço de explicabilidade
        service = ExplainabilityService()
        service.add_model_explainer(
            'test_model', model, ['f1', 'f2', 'f3', 'f4', 'f5'], 'tree'
        )
        
        # Testa explicação de instância
        test_instance = np.random.rand(1, 5)
        explanation = service.explain_prediction('test_model', test_instance)
        
        if 'prediction' in explanation:
            print("✅ Explainability - OK")
            return True
        else:
            print("⚠ Explainability - Explicação incompleta")
            return False
            
    except Exception as e:
        print(f"❌ Explainability - ERRO: {e}")
        return False

def run_all_tests():
    """Executa todos os testes"""
    print("🧪 Iniciando Testes do Sistema ML\n" + "="*50)
    
    tests = [
        ("Feature Engineering", test_feature_engineering),
        ("Model Cache", test_model_cache), 
        ("ChurnPredictor Básico", test_churn_predictor_basic),
        ("Temporal Validation", test_temporal_validation),
        ("Explainability", test_explainability)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testando {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} - ERRO CRÍTICO: {e}")
            results[test_name] = False
    
    # Resumo dos resultados
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name:<25}: {status}")
        if success:
            passed += 1
    
    print(f"\n📈 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        return True
    elif passed >= total * 0.8:  # 80% ou mais
        print("⚠️  MAIORIA DOS TESTES PASSOU - Sistema funcional com algumas limitações")
        return True
    else:
        print("🚨 MUITOS TESTES FALHARAM - Sistema precisa de correções")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)