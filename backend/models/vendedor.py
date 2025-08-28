"""
Modelo de dados para a tabela de Vendedores
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database.connection import Base
from .base import TimestampMixin, SoftDeleteMixin

class Vendedor(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "vendedor"

    # Chave primária
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Chave estrangeira para o usuário associado
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False, unique=True)
    
    # Chave estrangeira para a equipe
    equipe_id = Column(UUID(as_uuid=True), ForeignKey("equipe.id"), nullable=True)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="vendedor")
    equipe = relationship("Equipe", back_populates="vendedores")
    vendas = relationship("Venda", back_populates="vendedor")

    def __repr__(self):
        return f"<Vendedor(id={self.id})>"
