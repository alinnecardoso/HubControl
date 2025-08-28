"""
Modelo de dados para a tabela de Contas (genérico, ex: conta a pagar/receber)
"""
import uuid
import enum
from sqlalchemy import Column, String, ForeignKey, Float, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database.connection import Base
from .base import TimestampMixin, SoftDeleteMixin

class TipoConta(enum.Enum):
    A_PAGAR = "A Pagar"
    A_RECEBER = "A Receber"

class StatusConta(enum.Enum):
    PENDENTE = "Pendente"
    PAGO = "Pago"
    VENCIDO = "Vencido"

class Conta(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "conta"

    # Chave primária
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    descricao = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
    data_vencimento = Column(DateTime, nullable=True)
    
    tipo = Column(SQLAlchemyEnum(TipoConta), nullable=False)
    status = Column(SQLAlchemyEnum(StatusConta), nullable=False, default=StatusConta.PENDENTE)

    # Exemplo de relacionamento (se uma conta estiver ligada a uma venda)
    venda_id = Column(UUID(as_uuid=True), ForeignKey("venda.id"), nullable=True)
    venda = relationship("Venda")

    def __repr__(self):
        return f"<Conta(id={self.id}, descricao='{self.descricao}', valor={self.valor})>"
