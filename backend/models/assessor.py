"""
Modelo de assessor/consultor do sistema
"""
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin


class Assessor(Base, TimestampMixin, SoftDeleteMixin):
    """Modelo de assessor/consultor para o módulo de CS"""
    
    __tablename__ = "assessor"
    
    # Campos de identificação
    usuario_id = Column(ForeignKey("usuario.id"), nullable=True, unique=True)
    nome = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    equipe_id = Column(ForeignKey("equipe.id"), nullable=True, index=True)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="assessor")
    equipe = relationship("Equipe", back_populates="assessores")
    health_scores = relationship("HealthScoreSnapshot", back_populates="assessor")
    csat_respostas = relationship("CSATResposta", back_populates="consultor")
    
    def __repr__(self):
        return f"<Assessor(id={self.id}, nome='{self.nome}', email='{self.email}')>"
    
    @property
    def total_clientes_atendidos(self) -> int:
        """Retorna o total de clientes atendidos pelo assessor"""
        clientes_health_score = set(h.id_cliente for h in self.health_scores)
        clientes_csat = set(c.id_cliente for c in self.csat_respostas)
        return len(clientes_health_score.union(clientes_csat))
    
    @property
    def total_avaliacoes_health_score(self) -> int:
        """Retorna o total de avaliações de Health Score realizadas"""
        return len(self.health_scores)
    
    @property
    def total_avaliacoes_csat(self) -> int:
        """Retorna o total de avaliações CSAT realizadas"""
        return len(self.csat_respostas)
    
    @property
    def media_health_score(self) -> float:
        """Retorna a média dos Health Scores realizados pelo assessor"""
        if not self.health_scores:
            return 0.0
        
        total_score = sum(h.health_score_total for h in self.health_scores)
        return total_score / len(self.health_scores)
    
    @property
    def media_csat(self) -> float:
        """Retorna a média das avaliações CSAT realizadas pelo assessor"""
        if not self.csat_respostas:
            return 0.0
        
        total_score = sum(c.avaliacao_call for c in self.csat_respostas)
        return total_score / len(self.csat_respostas)
    
    @property
    def clientes_risco_alto(self) -> int:
        """Retorna o número de clientes com risco alto ou crítico"""
        return len([
            h for h in self.health_scores 
            if h.nivel_risco in ["alto", "critico"]
        ])
    
    @property
    def clientes_risco_baixo(self) -> int:
        """Retorna o número de clientes com risco baixo"""
        return len([
            h for h in self.health_scores 
            if h.nivel_risco == "baixo"
        ])
    
    def calcular_metricas_periodo(self, data_inicio: str, data_fim: str) -> dict:
        """Calcula métricas do assessor para um período específico"""
        from datetime import datetime
        
        data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        data_fim = datetime.strptime(data_fim, "%Y-%m-%d")
        
        # Filtra Health Scores do período
        health_scores_periodo = [
            h for h in self.health_scores 
            if data_inicio <= h.data_avaliacao <= data_fim
        ]
        
        # Filtra CSAT do período
        csat_periodo = [
            c for c in self.csat_respostas 
            if data_inicio <= c.data_resposta <= data_fim
        ]
        
        # Calcula métricas
        total_health_scores = len(health_scores_periodo)
        total_csat = len(csat_periodo)
        
        media_health_score = 0
        if health_scores_periodo:
            total_score = sum(h.health_score_total for h in health_scores_periodo)
            media_health_score = total_score / total_health_scores
        
        media_csat = 0
        if csat_periodo:
            total_score = sum(c.avaliacao_call for c in csat_periodo)
            media_csat = total_score / total_csat
        
        clientes_risco_alto = len([
            h for h in health_scores_periodo 
            if h.nivel_risco in ["alto", "critico"]
        ])
        
        return {
            "periodo": {
                "data_inicio": data_inicio.strftime("%Y-%m-%d"),
                "data_fim": data_fim.strftime("%Y-%m-%d")
            },
            "health_score": {
                "total_avaliacoes": total_health_scores,
                "media_score": round(media_health_score, 2),
                "clientes_risco_alto": clientes_risco_alto
            },
            "csat": {
                "total_avaliacoes": total_csat,
                "media_avaliacao": round(media_csat, 2)
            }
        }
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Converte o assessor para dicionário"""
        data = super().to_dict()
        
        # Adiciona métricas calculadas
        data["total_clientes_atendidos"] = self.total_clientes_atendidos
        data["total_avaliacoes_health_score"] = self.total_avaliacoes_health_score
        data["total_avaliacoes_csat"] = self.total_avaliacoes_csat
        data["media_health_score"] = round(self.media_health_score, 2)
        data["media_csat"] = round(self.media_csat, 2)
        data["clientes_risco_alto"] = self.clientes_risco_alto
        data["clientes_risco_baixo"] = self.clientes_risco_baixo
        
        if include_relationships:
            data["usuario"] = self.usuario.to_dict() if self.usuario else None
            data["equipe"] = self.equipe.to_dict() if self.equipe else None
            data["health_scores"] = [h.to_dict() for h in self.health_scores]
            data["csat_respostas"] = [c.to_dict() for c in self.csat_respostas]
        
        return data 