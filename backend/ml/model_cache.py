"""
Sistema de Cache para Modelos de Machine Learning
"""
import json
import pickle
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import redis
from redis import Redis
import hashlib
import numpy as np

logger = logging.getLogger(__name__)


class ModelCache:
    """Sistema de cache inteligente para modelos ML"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", ttl: int = 86400):
        """
        Inicializa o cache de modelos
        
        Args:
            redis_url: URL de conexão Redis
            ttl: Time to live em segundos (padrão: 24 horas)
        """
        self.ttl = ttl
        self.redis_client: Optional[Redis] = None
        
        try:
            self.redis_client = redis.from_url(redis_url)
            # Testa conexão
            self.redis_client.ping()
            logger.info(f"Cache Redis conectado: {redis_url}")
        except Exception as e:
            logger.warning(f"Redis não disponível, usando cache em memória: {e}")
            self.redis_client = None
        
        # Cache em memória como fallback
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
    
    def _get_cache_key(self, prefix: str, identifier: str) -> str:
        """Gera chave de cache consistente"""
        hash_obj = hashlib.md5(identifier.encode())
        return f"ml_cache:{prefix}:{hash_obj.hexdigest()}"
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serializa dados para cache"""
        import numpy as np
        if isinstance(data, (np.ndarray, np.number)):
            # Converte numpy para lista/float para JSON
            if isinstance(data, np.ndarray):
                data = data.tolist()
            else:
                data = float(data)
        
        return pickle.dumps({
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'type': type(data).__name__
        })
    
    def _deserialize_data(self, raw_data: bytes) -> Any:
        """Deserializa dados do cache"""
        cache_entry = pickle.loads(raw_data)
        return cache_entry['data']
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Verifica se entrada do cache expirou"""
        if 'timestamp' not in cache_entry:
            return True
        
        cached_time = datetime.fromisoformat(cache_entry['timestamp'])
        return datetime.now() - cached_time > timedelta(seconds=self.ttl)
    
    def cache_model_prediction(self, model_name: str, features_hash: str, 
                              prediction: Dict[str, Any]) -> bool:
        """
        Armazena previsão de modelo no cache
        
        Args:
            model_name: Nome do modelo
            features_hash: Hash das features usadas
            prediction: Resultado da previsão
        
        Returns:
            True se armazenado com sucesso
        """
        cache_key = self._get_cache_key("prediction", f"{model_name}:{features_hash}")
        
        try:
            if self.redis_client:
                serialized = self._serialize_data(prediction)
                self.redis_client.setex(cache_key, self.ttl, serialized)
            else:
                # Fallback: cache em memória
                self._memory_cache[cache_key] = {
                    'data': prediction,
                    'timestamp': datetime.now().isoformat()
                }
            
            logger.debug(f"Previsão cacheada: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao cachear previsão: {e}")
            return False
    
    def get_cached_prediction(self, model_name: str, features_hash: str) -> Optional[Dict[str, Any]]:
        """
        Recupera previsão do cache
        
        Args:
            model_name: Nome do modelo
            features_hash: Hash das features
            
        Returns:
            Previsão cacheada ou None
        """
        cache_key = self._get_cache_key("prediction", f"{model_name}:{features_hash}")
        
        try:
            if self.redis_client:
                raw_data = self.redis_client.get(cache_key)
                if raw_data:
                    return self._deserialize_data(raw_data)
            else:
                # Fallback: cache em memória
                if cache_key in self._memory_cache:
                    entry = self._memory_cache[cache_key]
                    if not self._is_expired(entry):
                        return entry['data']
                    else:
                        del self._memory_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao recuperar previsão do cache: {e}")
            return None
    
    def cache_features(self, cliente_id: str, features: Dict[str, float]) -> bool:
        """
        Armazena features processadas no cache
        
        Args:
            cliente_id: ID do cliente
            features: Features calculadas
            
        Returns:
            True se armazenado com sucesso
        """
        cache_key = self._get_cache_key("features", cliente_id)
        
        try:
            if self.redis_client:
                serialized = self._serialize_data(features)
                self.redis_client.setex(cache_key, self.ttl, serialized)
            else:
                self._memory_cache[cache_key] = {
                    'data': features,
                    'timestamp': datetime.now().isoformat()
                }
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao cachear features: {e}")
            return False
    
    def get_cached_features(self, cliente_id: str) -> Optional[Dict[str, float]]:
        """
        Recupera features do cache
        
        Args:
            cliente_id: ID do cliente
            
        Returns:
            Features cacheadas ou None
        """
        cache_key = self._get_cache_key("features", cliente_id)
        
        try:
            if self.redis_client:
                raw_data = self.redis_client.get(cache_key)
                if raw_data:
                    return self._deserialize_data(raw_data)
            else:
                if cache_key in self._memory_cache:
                    entry = self._memory_cache[cache_key]
                    if not self._is_expired(entry):
                        return entry['data']
                    else:
                        del self._memory_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao recuperar features do cache: {e}")
            return None
    
    def cache_model_metrics(self, model_name: str, metrics: Dict[str, float]) -> bool:
        """
        Armazena métricas de modelo no cache
        
        Args:
            model_name: Nome do modelo
            metrics: Métricas do modelo
            
        Returns:
            True se armazenado com sucesso
        """
        cache_key = self._get_cache_key("metrics", model_name)
        
        try:
            if self.redis_client:
                serialized = self._serialize_data(metrics)
                # Métricas têm TTL maior (7 dias)
                self.redis_client.setex(cache_key, 7 * 24 * 3600, serialized)
            else:
                self._memory_cache[cache_key] = {
                    'data': metrics,
                    'timestamp': datetime.now().isoformat()
                }
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao cachear métricas: {e}")
            return False
    
    def get_cached_metrics(self, model_name: str) -> Optional[Dict[str, float]]:
        """
        Recupera métricas do cache
        
        Args:
            model_name: Nome do modelo
            
        Returns:
            Métricas cacheadas ou None
        """
        cache_key = self._get_cache_key("metrics", model_name)
        
        try:
            if self.redis_client:
                raw_data = self.redis_client.get(cache_key)
                if raw_data:
                    return self._deserialize_data(raw_data)
            else:
                if cache_key in self._memory_cache:
                    entry = self._memory_cache[cache_key]
                    # Para métricas, TTL de 7 dias
                    if datetime.now() - datetime.fromisoformat(entry['timestamp']) < timedelta(days=7):
                        return entry['data']
                    else:
                        del self._memory_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao recuperar métricas do cache: {e}")
            return None
    
    def invalidate_client_cache(self, cliente_id: str) -> bool:
        """
        Invalida cache relacionado a um cliente específico
        
        Args:
            cliente_id: ID do cliente
            
        Returns:
            True se invalidado com sucesso
        """
        try:
            patterns_to_clear = [
                f"features:{cliente_id}",
                f"prediction:*:{cliente_id}*"
            ]
            
            if self.redis_client:
                for pattern in patterns_to_clear:
                    cache_key = self._get_cache_key("*", pattern)
                    keys = self.redis_client.keys(cache_key.replace("*", ""))
                    if keys:
                        self.redis_client.delete(*keys)
            else:
                # Para cache em memória, remove chaves que contenham o cliente_id
                keys_to_remove = [
                    k for k in self._memory_cache.keys() 
                    if cliente_id in k
                ]
                for key in keys_to_remove:
                    del self._memory_cache[key]
            
            logger.info(f"Cache invalidado para cliente: {cliente_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao invalidar cache: {e}")
            return False
    
    def clear_all_cache(self) -> bool:
        """
        Limpa todo o cache ML
        
        Returns:
            True se limpo com sucesso
        """
        try:
            if self.redis_client:
                keys = self.redis_client.keys("ml_cache:*")
                if keys:
                    self.redis_client.delete(*keys)
            else:
                self._memory_cache.clear()
            
            logger.info("Cache ML limpo completamente")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do cache
        
        Returns:
            Estatísticas do cache
        """
        try:
            stats = {
                'cache_type': 'redis' if self.redis_client else 'memory',
                'ttl_seconds': self.ttl,
                'connected': True
            }
            
            if self.redis_client:
                # Estatísticas do Redis
                info = self.redis_client.info()
                ml_keys = self.redis_client.keys("ml_cache:*")
                
                stats.update({
                    'total_ml_keys': len(ml_keys),
                    'memory_usage': info.get('used_memory_human', 'N/A'),
                    'connected_clients': info.get('connected_clients', 0)
                })
            else:
                # Estatísticas do cache em memória
                stats.update({
                    'total_ml_keys': len(self._memory_cache),
                    'memory_usage': f"{len(str(self._memory_cache))} chars"
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                'cache_type': 'error',
                'connected': False,
                'error': str(e)
            }
    
    def create_features_hash(self, features: Dict[str, float]) -> str:
        """
        Cria hash único para um conjunto de features
        
        Args:
            features: Dicionário de features
            
        Returns:
            Hash MD5 das features
        """
        # Ordena as features para hash consistente
        sorted_features = dict(sorted(features.items()))
        features_str = json.dumps(sorted_features, sort_keys=True)
        return hashlib.md5(features_str.encode()).hexdigest()


# Instância global do cache
model_cache = ModelCache()