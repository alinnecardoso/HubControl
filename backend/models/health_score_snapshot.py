"""
Modelo para snapshots do Health Score de um cliente.
"""
import uuid
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database.connection import Base
from .base import TimestampMixin

class HealthScoreSnapshot(Base, TimestampMixin):
    __tablename__ = "health_score_snapshot"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("cliente.id"), nullable=False)
    score = Column(Integer, nullable=False) # Ex: 0 a 100
    data_snapshot = Column(DateTime, nullable=False)

    cliente = relationship("Cliente")

    def __repr__(self):
        return f"<HealthScoreSnapshot(cliente_id={self.cliente_id}, score={self.score})>"
