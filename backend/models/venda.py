"""
Modelo de dados para a tabela de Vendas
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, Float, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from ..database.connection import Base
from .base import TimestampMixin, SoftDeleteMixin

class StatusVenda(enum.Enum):
    PENDENTE = "Pendente"
    EM_NEGOCIACAO = "Em Negociação"
    FECHADA = "Fechada"
    CANCELADA = "Cancelada"

class Venda(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "venda"

    # Chave primária
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    valor = Column(Float, nullable=False)
    data_venda = Column(DateTime, nullable=False)
    status = Column(SQLAlchemyEnum(StatusVenda), nullable=False, default=StatusVenda.PENDENTE)

    # Chaves estrangeiras
    vendedor_id = Column(UUID(as_uuid=True), ForeignKey("vendedor.id"), nullable=False)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("cliente.id"), nullable=False)

    # Relacionamentos
    vendedor = relationship("Vendedor", back_populates="vendas")
    cliente = relationship("Cliente", back_populates="vendas")

    def __repr__(self):
        return f"<Venda(id={self.id}, valor={self.valor}, status='{self.status.value}')>"
