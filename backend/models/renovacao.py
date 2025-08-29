"""
Modelo de renovação para gestão de ciclos de contratos
"""
from sqlalchemy import Column, String, Date, Integer, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Renovacao(Base, TimestampMixin):
    """Modelo de renovação para gestão de ciclos de contratos"""
    
    __tablename__ = "renovacao"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Campos de identificação
    contrato_id = Column(ForeignKey("contrato.id"), nullable=False, index=True)
    tipo = Column(String(50), nullable=False, index=True)
    data_renovacao = Column(Date, nullable=False, index=True)
    
    # Campos do novo ciclo
    novo_ciclo = Column(Integer, nullable=False)
    nova_data_fim = Column(Date, nullable=False)
    novo_valor_mensal = Column(Numeric(15, 2))
    
    # Campos adicionais
    observacoes = Column(Text)
    usuario_id = Column(ForeignKey("usuario.id"), nullable=True, index=True)
    
    # Relacionamentos
    contrato = relationship("Contrato", back_populates="renovacoes")
    usuario = relationship("Usuario", back_populates="renovacoes")
    
    def __repr__(self):
        return f"<Renovacao(id={self.id}, contrato_id={self.contrato_id}, tipo='{self.tipo}', novo_ciclo={self.novo_ciclo})>"
    
    @property
    def is_renovacao_manual(self) -> bool:
        """Verifica se é renovação manual"""
        return self.tipo == "manual"
    
    @property
    def is_auto_renovacao(self) -> bool:
        """Verifica se é auto-renovação"""
        return self.tipo == "auto_renovacao"
    
    @property
    def variacao_valor(self) -> float:
        """Calcula a variação do valor mensal"""
        if not self.novo_valor_mensal or not self.contrato:
            return 0.0
        
        valor_anterior = float(self.contrato.valor_mensal)
        valor_novo = float(self.novo_valor_mensal)
        
        return valor_novo - valor_anterior
    
    @property
    def percentual_variacao_valor(self) -> float:
        """Calcula o percentual de variação do valor mensal"""
        if not self.novo_valor_mensal or not self.contrato:
            return 0.0
        
        valor_anterior = float(self.contrato.valor_mensal)
        if valor_anterior == 0:
            return 0.0
        
        variacao = self.variacao_valor
        return (variacao / valor_anterior) * 100
    
    @property
    def dias_entre_renovacoes(self) -> int:
        """Calcula os dias entre a renovação e o vencimento anterior"""
        if not self.contrato:
            return 0
        
        from datetime import date
        data_vencimento_anterior = self.contrato.data_fim
        return (self.data_renovacao - data_vencimento_anterior).days
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Converte a renovação para dicionário"""
        data = super().to_dict()
        
        # Adiciona propriedades calculadas
        data["is_renovacao_manual"] = self.is_renovacao_manual
        data["is_auto_renovacao"] = self.is_auto_renovacao
        data["variacao_valor"] = round(self.variacao_valor, 2)
        data["percentual_variacao_valor"] = round(self.percentual_variacao_valor, 2)
        data["dias_entre_renovacoes"] = self.dias_entre_renovacoes
        
        if include_relationships:
            data["contrato"] = self.contrato.to_dict() if self.contrato else None
            data["usuario"] = self.usuario.to_dict() if self.usuario else None
        
        return data 