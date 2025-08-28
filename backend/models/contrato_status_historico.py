"""
Modelo para registrar o histórico de status de um contrato.
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Supondo que o status do contrato seja um enum
from .contrato import Contrato # Ajuste se o enum estiver em outro lugar

from ..database.connection import Base
from .base import TimestampMixin

class ContratoStatusHistorico(Base, TimestampMixin):
    __tablename__ = "contrato_status_historico"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    contrato_id = Column(UUID(as_uuid=True), ForeignKey("contrato.id"), nullable=False)
    # O status anterior pode ser nulo (para o primeiro registro)
    status_anterior = Column(String, nullable=True) 
    status_novo = Column(String, nullable=False)
    data_mudanca = Column(DateTime, nullable=False)
    
    contrato = relationship("Contrato")

    def __repr__(self):
        return f"<ContratoStatusHistorico(contrato_id={self.contrato_id}, status_novo='{self.status_novo}')>"
