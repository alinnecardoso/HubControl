"""
Modelo para eventos de Customer Success (CS).
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from ..database.connection import Base
from .base import TimestampMixin

class TipoEventoCS(enum.Enum):
    REUNIAO_KICKOFF = "Reunião de Kickoff"
    FOLLOW_UP = "Follow-up"
    TREINAMENTO = "Treinamento"
    REUNIAO_QBR = "Reunião de QBR"
    OUTRO = "Outro"

class EventoCS(Base, TimestampMixin):
    __tablename__ = "evento_cs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("cliente.id"), nullable=False)
    assessor_id = Column(UUID(as_uuid=True), ForeignKey("assessor.id"), nullable=False)
    
    tipo_evento = Column(SQLAlchemyEnum(TipoEventoCS), nullable=False)
    data_evento = Column(DateTime, nullable=False)
    descricao = Column(Text, nullable=True)

    cliente = relationship("Cliente")
    assessor = relationship("Assessor") # Adicionado relacionamento

    def __repr__(self):
        return f"<EventoCS(cliente_id={self.cliente_id}, tipo='{self.tipo_evento.value}')>"
