"""
Modelo de dados para o Assessor de Customer Success.
"""
import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database.connection import Base
from .base import TimestampMixin, SoftDeleteMixin

class Assessor(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "assessor"

    # Chave primária
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relacionamento com a tabela de usuários
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False, unique=True)
    usuario = relationship("Usuario")

    # Relacionamento com Eventos de CS
    eventos_cs = relationship("EventoCS", back_populates="assessor")

    def __repr__(self):
        return f"<Assessor(id={self.id}, usuario_id={self.usuario_id})>"
