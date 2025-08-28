"""
Modelo de dados para a tabela de Equipes
"""
import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database.connection import Base
from .base import TimestampMixin, SoftDeleteMixin

class Equipe(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "equipe"

    # Chave primária usando UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, nullable=False, unique=True, index=True)
    
    # Relacionamento com Vendedor (uma equipe pode ter vários vendedores)
    vendedores = relationship("Vendedor", back_populates="equipe")

    def __repr__(self):
        return f"<Equipe(id={self.id}, nome='{self.nome}')>"
