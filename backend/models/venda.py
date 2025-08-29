"""
Modelo de venda do sistema
"""
from datetime import date
from sqlalchemy import Column, String, Date, Integer, Numeric, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Venda(Base, TimestampMixin):
    """Modelo de venda para o módulo de vendas"""
    
    __tablename__ = "venda"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Campos de identificação
    data = Column(Date, nullable=False, index=True)
    loja = Column(String(255), nullable=False, index=True)
    cliente_id = Column(ForeignKey("cliente.id"), nullable=False, index=True)
    vendedor_id = Column(ForeignKey("vendedor.id"), nullable=False, index=True)
    
    # Campos do produto/serviço
    produto = Column(String(255), nullable=False, index=True)
    valor_mensal = Column(Numeric(15, 2), nullable=False)
    contrato_meses = Column(Integer, nullable=False)
    
    # Campos de pagamento
    forma_pagamento = Column(String(100), nullable=False)
    canal_venda = Column(String(100), index=True)
    
    # Campos opcionais
    telefone_cliente = Column(String(20))
    percentual_variavel = Column(Numeric(5, 2))
    descricao = Column(Text)
    info_adicional = Column(Text)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="vendas")
    vendedor = relationship("Vendedor", back_populates="vendas")
    
    # Índices compostos
    __table_args__ = (
        Index('idx_venda_data_vendedor', 'data', 'vendedor_id'),
        Index('idx_venda_cliente_data', 'cliente_id', 'data'),
        Index('idx_venda_loja_data', 'loja', 'data'),
    )
    
    def __repr__(self):
        return f"<Venda(id={self.id}, data={self.data}, produto='{self.produto}', valor={self.valor_mensal})>"
    
    @property
    def valor_total_contrato(self) -> float:
        """Calcula o valor total do contrato"""
        return float(self.valor_mensal * self.contrato_meses)
    
    @property
    def valor_bonificacao(self) -> float:
        """Calcula o valor da bonificação se houver percentual variável"""
        if self.percentual_variavel:
            return float(self.valor_mensal * self.percentual_variavel / 100)
        return 0.0
    
    @property
    def valor_total_com_bonificacao(self) -> float:
        """Calcula o valor total incluindo bonificação"""
        return self.valor_total_contrato + self.valor_bonificacao
    
    @property
    def is_recente(self) -> bool:
        """Verifica se a venda é recente (últimos 30 dias)"""
        from datetime import timedelta
        return (date.today() - self.data).days <= 30
    
    @property
    def is_mes_atual(self) -> bool:
        """Verifica se a venda é do mês atual"""
        hoje = date.today()
        return self.data.year == hoje.year and self.data.month == hoje.month
    
    @property
    def is_trimestre_atual(self) -> bool:
        """Verifica se a venda é do trimestre atual"""
        hoje = date.today()
        trimestre_atual = (hoje.month - 1) // 3 + 1
        trimestre_venda = (self.data.month - 1) // 3 + 1
        return self.data.year == hoje.year and trimestre_venda == trimestre_atual
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Converte a venda para dicionário"""
        data = super().to_dict()
        
        # Adiciona campos calculados
        data["valor_total_contrato"] = self.valor_total_contrato
        data["valor_bonificacao"] = self.valor_bonificacao
        data["valor_total_com_bonificacao"] = self.valor_total_com_bonificacao
        data["is_recente"] = self.is_recente
        data["is_mes_atual"] = self.is_mes_atual
        data["is_trimestre_atual"] = self.is_trimestre_atual
        
        if include_relationships:
            data["cliente"] = self.cliente.to_dict() if self.cliente else None
            data["vendedor"] = self.vendedor.to_dict() if self.vendedor else None
        
        return data 