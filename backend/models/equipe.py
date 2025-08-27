"""
Modelo de equipe do sistema
"""
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin


class Equipe(Base, TimestampMixin, SoftDeleteMixin):
    """Modelo de equipe para organização dos usuários"""
    
    __tablename__ = "equipe"
    
    # Campos básicos
    nome = Column(String(255), nullable=False, index=True)
    tipo = Column(String(50), nullable=False, index=True)
    
    # Relacionamentos
    vendedores = relationship("Vendedor", back_populates="equipe_vendas")
    assessores = relationship("Assessor", back_populates="equipe")
    
    def __repr__(self):
        return f"<Equipe(id={self.id}, nome='{self.nome}', tipo='{self.tipo}')>"
    
    @property
    def is_equipe_cs(self) -> bool:
        """Verifica se é equipe de Customer Success"""
        return self.tipo == "cs"
    
    @property
    def is_equipe_vendas(self) -> bool:
        """Verifica se é equipe de Vendas"""
        return self.tipo == "vendas"
    
    @property
    def is_equipe_financeiro(self) -> bool:
        """Verifica se é equipe Financeira"""
        return self.tipo == "financeiro"
    
    @property
    def is_equipe_dataops(self) -> bool:
        """Verifica se é equipe de DataOps"""
        return self.tipo == "dataops"
    
    @property
    def total_membros(self) -> int:
        """Retorna o total de membros ativos na equipe"""
        total = 0
        
        if self.is_equipe_vendas:
            total += len([v for v in self.vendedores if v.ativo])
        
        if self.is_equipe_cs:
            total += len([a for a in self.assessores if a.ativo])
        
        return total
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Converte a equipe para dicionário"""
        data = super().to_dict()
        
        # Adiciona propriedades calculadas
        data["is_equipe_cs"] = self.is_equipe_cs
        data["is_equipe_vendas"] = self.is_equipe_vendas
        data["is_equipe_financeiro"] = self.is_equipe_financeiro
        data["is_equipe_dataops"] = self.is_equipe_dataops
        data["total_membros"] = self.total_membros
        
        if include_relationships:
            data["vendedores"] = [v.to_dict() for v in self.vendedores]
            data["assessores"] = [a.to_dict() for a in self.assessores]
        
        return data 