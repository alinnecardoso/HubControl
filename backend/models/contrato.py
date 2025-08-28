"""
Modelo de dados para a tabela de Contratos
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database.connection import Base
from .base import TimestampMixin, SoftDeleteMixin

class Contrato(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "contrato"

    # Chave primária
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    titulo = Column(String, nullable=False)
    descricao = Column(Text, nullable=True)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=True)

    # Chave estrangeira para o cliente
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("cliente.id"), nullable=False)
    cliente = relationship("Cliente")

    def __repr__(self):
        return f"<Contrato(id={self.id}, titulo='{self.titulo}')>"
