"""
Modelo de dados para a tabela de Clientes
"""
import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database.connection import Base
from .base import TimestampMixin, SoftDeleteMixin

class Cliente(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "cliente"

    # Chave primária
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    nome = Column(String, nullable=False)
    email = Column(String, nullable=True, unique=True, index=True)
    telefone = Column(String, nullable=True)
    
    # Relacionamento com Vendas (um cliente pode ter várias vendas)
    vendas = relationship("Venda", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente(id={self.id}, nome='{self.nome}')>"
