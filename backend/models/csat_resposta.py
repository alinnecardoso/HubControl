"""
Modelo para respostas de pesquisas de satisfação (CSAT).
"""
import uuid
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database.connection import Base
from .base import TimestampMixin

class CSATResposta(Base, TimestampMixin):
    __tablename__ = "csat_resposta"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("cliente.id"), nullable=False)
    # Opcional: a resposta pode estar ligada a um evento específico
    evento_cs_id = Column(UUID(as_uuid=True), ForeignKey("evento_cs.id"), nullable=True)
    
    nota = Column(Integer, nullable=False) # Ex: 1 a 5
    comentario = Column(Text, nullable=True)
    data_resposta = Column(DateTime, nullable=False)

    cliente = relationship("Cliente")
    evento_cs = relationship("EventoCS")

    def __repr__(self):
        return f"<CSATResposta(cliente_id={self.cliente_id}, nota={self.nota})>"
