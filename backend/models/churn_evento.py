"""
Modelo para registrar um evento de churn (cancelamento).
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from ..database.connection import Base
from .base import TimestampMixin

class MotivoChurn(enum.Enum):
    PRECO = "Preço"
    CONCORRENCIA = "Concorrência"
    INSATISFACAO_PRODUTO = "Insatisfação com o Produto"
    INSATISFACAO_SUPORTE = "Insatisfação com o Suporte"
    NAO_UTILIZAVA = "Não Utilizava"
    OUTRO = "Outro"

class ChurnEvento(Base, TimestampMixin):
    __tablename__ = "churn_evento"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("cliente.id"), nullable=False)
    contrato_id = Column(UUID(as_uuid=True), ForeignKey("contrato.id"), nullable=True)
    
    data_churn = Column(DateTime, nullable=False)
    motivo = Column(SQLAlchemyEnum(MotivoChurn), nullable=False)
    detalhes = Column(Text, nullable=True)

    cliente = relationship("Cliente")
    contrato = relationship("Contrato")

    def __repr__(self):
        return f"<ChurnEvento(cliente_id={self.cliente_id}, data_churn={self.data_churn})>"
