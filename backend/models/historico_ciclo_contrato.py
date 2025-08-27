"""
Modelo de histórico de ciclo de contrato
"""
from sqlalchemy import Column, Date, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class HistoricoCicloContrato(Base, TimestampMixin):
    """Modelo de histórico de ciclo de contrato"""
    
    __tablename__ = "historico_ciclo_contrato"
    
    # Campos de identificação
    contrato_id = Column(ForeignKey("contrato.id"), nullable=False, index=True)
    
    # Campos do ciclo
    ciclo = Column(Integer, nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    duracao_meses = Column(Integer, nullable=False)
    valor_mensal = Column(Numeric(15, 2), nullable=False)
    
    # Relacionamentos
    contrato = relationship("Contrato", back_populates="historico_ciclos")
    
    def __repr__(self):
        return f"<HistoricoCicloContrato(id={self.id}, contrato_id={self.cliente_id}, ciclo={self.ciclo})>"
    
    @property
    def valor_total_ciclo(self) -> float:
        """Calcula o valor total do ciclo"""
        return float(self.valor_mensal * self.duracao_meses)
    
    @property
    def dias_ciclo(self) -> int:
        """Calcula os dias de duração do ciclo"""
        from datetime import date
        return (self.data_fim - self.data_inicio).days
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Converte o histórico de ciclo para dicionário"""
        data = super().to_dict()
        
        # Adiciona propriedades calculadas
        data["valor_total_ciclo"] = round(self.valor_total_ciclo, 2)
        data["dias_ciclo"] = self.dias_ciclo
        
        if include_relationships:
            data["contrato"] = self.contrato.to_dict() if self.contrato else None
        
        return data 