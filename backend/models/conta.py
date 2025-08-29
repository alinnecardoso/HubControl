"""
Modelo de conta para contas adicionais dos clientes
"""
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin


class Conta(Base, TimestampMixin, SoftDeleteMixin):
    """Modelo de conta para contas adicionais dos clientes"""
    
    __tablename__ = "conta"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Campos de identificação
    cliente_id = Column(ForeignKey("cliente.id"), nullable=False, index=True)
    apelido = Column(String(255), index=True)
    plataforma = Column(String(100), index=True)
    status = Column(String(50), default="ativo", nullable=False, index=True)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="contas")
    contratos = relationship("Contrato", back_populates="conta")
    
    def __repr__(self):
        return f"<Conta(id={self.id}, cliente_id={self.cliente_id}, apelido='{self.apelido}', plataforma='{self.plataforma}')>"
    
    @property
    def is_ativa(self) -> bool:
        """Verifica se a conta está ativa"""
        return self.status == "ativo"
    
    @property
    def is_suspensa(self) -> bool:
        """Verifica se a conta está suspensa"""
        return self.status == "suspenso"
    
    @property
    def is_inativa(self) -> bool:
        """Verifica se a conta está inativa"""
        return self.status == "inativo"
    
    @property
    def contratos_ativos(self) -> list:
        """Retorna os contratos ativos da conta"""
        return [c for c in self.contratos if c.is_ativo]
    
    @property
    def total_contratos(self) -> int:
        """Retorna o total de contratos da conta"""
        return len(self.contratos)
    
    @property
    def valor_mensal_total(self) -> float:
        """Retorna o valor mensal total dos contratos ativos"""
        return sum(c.valor_mensal for c in self.contratos_ativos)
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Converte a conta para dicionário"""
        data = super().to_dict()
        
        # Adiciona propriedades calculadas
        data["is_ativa"] = self.is_ativa
        data["is_suspensa"] = self.is_suspensa
        data["is_inativa"] = self.is_inativa
        data["contratos_ativos"] = len(self.contratos_ativos)
        data["total_contratos"] = self.total_contratos
        data["valor_mensal_total"] = round(self.valor_mensal_total, 2)
        
        if include_relationships:
            data["cliente"] = self.cliente.to_dict() if self.cliente else None
            data["contratos"] = [c.to_dict() for c in self.contratos]
        
        return data 