"""
Modelo de vendedor do sistema
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin


class Vendedor(Base, TimestampMixin, SoftDeleteMixin):
    """Modelo de vendedor para o módulo de vendas"""
    
    __tablename__ = "vendedor"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Campos de identificação
    usuario_id = Column(ForeignKey("usuario.id"), nullable=True, unique=True)
    nome = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    equipe_vendas_id = Column(ForeignKey("equipe.id"), nullable=True, index=True)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="vendedor")
    equipe_vendas = relationship("Equipe")
    vendas = relationship("Venda", back_populates="vendedor")
    
    # Índices compostos
    __table_args__ = (
        Index('idx_vendedor_equipe_ativo', 'equipe_vendas_id', 'ativo'),
    )
    
    def __repr__(self):
        return f"<Vendedor(id={self.id}, nome='{self.nome}', email='{self.email}')>"
    
    @property
    def total_vendas(self) -> int:
        """Retorna o total de vendas do vendedor"""
        return len(self.vendas)
    
    @property
    def total_vendas_mes_atual(self) -> int:
        """Retorna o total de vendas do mês atual"""
        return len([v for v in self.vendas if v.is_mes_atual])
    
    @property
    def total_vendas_trimestre_atual(self) -> int:
        """Retorna o total de vendas do trimestre atual"""
        return len([v for v in self.vendas if v.is_trimestre_atual])
    
    @property
    def valor_total_vendas(self) -> float:
        """Retorna o valor total das vendas"""
        return sum(v.valor_mensal for v in self.vendas)
    
    @property
    def valor_total_vendas_mes_atual(self) -> float:
        """Retorna o valor total das vendas do mês atual"""
        return sum(v.valor_mensal for v in self.vendas if v.is_mes_atual)
    
    @property
    def valor_total_vendas_trimestre_atual(self) -> float:
        """Retorna o valor total das vendas do trimestre atual"""
        return sum(v.valor_mensal for v in self.vendas if v.is_trimestre_atual)
    
    @property
    def valor_total_bonificacoes(self) -> float:
        """Retorna o valor total das bonificações"""
        return sum(v.valor_bonificacao for v in self.vendas)
    
    @property
    def valor_total_bonificacoes_mes_atual(self) -> float:
        """Retorna o valor total das bonificações do mês atual"""
        return sum(v.valor_bonificacao for v in self.vendas if v.is_mes_atual)
    
    @property
    def valor_total_bonificacoes_trimestre_atual(self) -> float:
        """Retorna o valor total das bonificações do trimestre atual"""
        return sum(v.valor_bonificacao for v in self.vendas if v.is_trimestre_atual)
    
    @property
    def media_valor_venda(self) -> float:
        """Retorna a média de valor por venda"""
        if not self.vendas:
            return 0.0
        return self.valor_total_vendas / len(self.vendas)
    
    @property
    def produtos_vendidos(self) -> list:
        """Retorna lista de produtos vendidos pelo vendedor"""
        produtos = {}
        for venda in self.vendas:
            if venda.produto not in produtos:
                produtos[venda.produto] = 0
            produtos[venda.produto] += 1
        
        # Retorna ordenado por quantidade
        return sorted(produtos.items(), key=lambda x: x[1], reverse=True)
    
    @property
    def top_produtos(self, limit: int = 5) -> list:
        """Retorna os top produtos vendidos"""
        return self.produtos_vendidos[:limit]
    
    def calcular_metricas_periodo(self, data_inicio: str, data_fim: str) -> dict:
        """Calcula métricas do vendedor para um período específico"""
        from datetime import datetime
        
        data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
        data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
        
        vendas_periodo = [
            v for v in self.vendas 
            if data_inicio <= v.data <= data_fim
        ]
        
        if not vendas_periodo:
            return {
                "total_vendas": 0,
                "valor_total": 0.0,
                "valor_bonificacoes": 0.0,
                "media_valor": 0.0,
                "produtos_vendidos": []
            }
        
        valor_total = sum(v.valor_mensal for v in vendas_periodo)
        valor_bonificacoes = sum(v.valor_bonificacao for v in vendas_periodo)
        media_valor = valor_total / len(vendas_periodo)
        
        # Produtos vendidos no período
        produtos = {}
        for venda in vendas_periodo:
            if venda.produto not in produtos:
                produtos[venda.produto] = 0
            produtos[venda.produto] += 1
        
        produtos_ordenados = sorted(produtos.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_vendas": len(vendas_periodo),
            "valor_total": round(valor_total, 2),
            "valor_bonificacoes": round(valor_bonificacoes, 2),
            "media_valor": round(media_valor, 2),
            "produtos_vendidos": produtos_ordenados
        }
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Converte o vendedor para dicionário"""
        data = super().to_dict()
        
        # Adiciona métricas calculadas
        data["total_vendas"] = self.total_vendas
        data["total_vendas_mes_atual"] = self.total_vendas_mes_atual
        data["total_vendas_trimestre_atual"] = self.total_vendas_trimestre_atual
        data["valor_total_vendas"] = round(self.valor_total_vendas, 2)
        data["valor_total_vendas_mes_atual"] = round(self.valor_total_vendas_mes_atual, 2)
        data["valor_total_vendas_trimestre_atual"] = round(self.valor_total_vendas_trimestre_atual, 2)
        data["valor_total_bonificacoes"] = round(self.valor_total_bonificacoes, 2)
        data["valor_total_bonificacoes_mes_atual"] = round(self.valor_total_bonificacoes_mes_atual, 2)
        data["valor_total_bonificacoes_trimestre_atual"] = round(self.valor_total_bonificacoes_trimestre_atual, 2)
        data["media_valor_venda"] = round(self.media_valor_venda, 2)
        data["produtos_vendidos"] = self.produtos_vendidos
        data["top_produtos"] = self.top_produtos
        
        if include_relationships:
            data["usuario"] = self.usuario.to_dict() if self.usuario else None
            data["equipe_vendas"] = self.equipe_vendas.to_dict() if self.equipe_vendas else None
            data["vendas"] = [v.to_dict() for v in self.vendas]
        
        return data 