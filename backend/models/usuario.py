"""
Modelo de dados para a tabela de Usuários
"""
import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Importa a Base e os Mixins do módulo base
from ..database.connection import Base
from .base import TimestampMixin, SoftDeleteMixin

class Usuario(Base, TimestampMixin, SoftDeleteMixin):
    """
    Modelo SQLAlchemy para representar um usuário no sistema.
    """
    __tablename__ = "usuario"

    # Define a coluna 'id' como chave primária, usando UUID para garantir unicidade.
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    email = Column(String, unique=True, index=True, nullable=False)
    nome = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relacionamento com Vendedor (se aplicável)
    vendedor = relationship("Vendedor", back_populates="usuario", uselist=False)

    def __repr__(self):
        return f"<Usuario(id={self.id}, email='{self.email}')>"
