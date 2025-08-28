"""
Modelo para registrar informações sobre a renovação de um contrato.
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database.connection import Base
from .base import TimestampMixin

class Renovacao(Base, TimestampMixin):
    __tablename__ = "renovacao"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    contrato_id = Column(UUID(as_uuid=True), ForeignKey("contrato.id"), nullable=False)
    data_renovacao = Column(DateTime, nullable=False)
    valor_renovacao = Column(Float, nullable=False)
    renovado_automaticamente = Column(Boolean, default=False)

    contrato = relationship("Contrato")

    def __repr__(self):
        return f"<Renovacao(contrato_id={self.contrato_id}, data_renovacao={self.data_renovacao})>"
