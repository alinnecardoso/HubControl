"""
Modelo para o histórico de ciclos de um contrato (ex: renovações).
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database.connection import Base
from .base import TimestampMixin

class HistoricoCicloContrato(Base, TimestampMixin):
    __tablename__ = "historico_ciclo_contrato"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    contrato_id = Column(UUID(as_uuid=True), ForeignKey("contrato.id"), nullable=False)
    ciclo = Column(Integer, nullable=False) # Ex: 1 para o primeiro ciclo, 2 para a primeira renovação, etc.
    data_inicio_ciclo = Column(DateTime, nullable=False)
    data_fim_ciclo = Column(DateTime, nullable=False)
    
    contrato = relationship("Contrato")

    def __repr__(self):
        return f"<HistoricoCicloContrato(contrato_id={self.contrato_id}, ciclo={self.ciclo})>"
