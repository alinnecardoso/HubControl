"""
Modelo de churn evento para análise de perda de clientes
"""
from sqlalchemy import Column, String, Date, Numeric, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class ChurnEvento(Base, TimestampMixin):
    """Modelo de churn evento para análise de perda de clientes"""
    
    __tablename__ = "churn_evento"
    
    # Campos de identificação
    cliente_id = Column(ForeignKey("cliente.id"), nullable=False, index=True)
    contrato_id = Column(ForeignKey("contrato.id"), nullable=True, index=True)
    
    # Campos do churn
    data_churn = Column(Date, nullable=False, index=True)
    motivo = Column(String(100), nullable=False, index=True)
    descricao = Column(Text)
    valor_perdido = Column(Numeric(15, 2))
    
    # Campo de auditoria
    usuario_id = Column(ForeignKey("usuario.id"), nullable=True, index=True)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="churn_eventos")
    contrato = relationship("Contrato", back_populates="churn_eventos")
    usuario = relationship("Usuario", back_populates="churn_eventos")
    
    # Índices compostos
    __table_args__ = (
        Index('idx_churn_evento_cliente_data', 'cliente_id', 'data_churn'),
        Index('idx_churn_evento_motivo_data', 'motivo', 'data_churn'),
        Index('idx_churn_evento_valor_data', 'valor_perdido', 'data_churn'),
    )
    
    def __repr__(self):
        return f"<ChurnEvento(id={self.id}, cliente_id={self.cliente_id}, motivo='{self.motivo}', data_churn={self.data_churn})>"
    
    @property
    def is_churn_recente(self) -> bool:
        """Verifica se o churn é recente (últimos 30 dias)"""
        from datetime import date, timedelta
        return (date.today() - self.data_churn).days <= 30
    
    @property
    def is_churn_mes_atual(self) -> bool:
        """Verifica se o churn é do mês atual"""
        from datetime import date
        hoje = date.today()
        return self.data_churn.year == hoje.year and self.data_churn.month == hoje.month
    
    @property
    def is_churn_trimestre_atual(self) -> bool:
        """Verifica se o churn é do trimestre atual"""
        from datetime import date
        hoje = date.today()
        trimestre_atual = (hoje.month - 1) // 3 + 1
        trimestre_churn = (self.data_churn.month - 1) // 3 + 1
        return self.data_churn.year == hoje.year and trimestre_churn == trimestre_atual
    
    @property
    def dias_desde_churn(self) -> int:
        """Retorna os dias desde o churn"""
        from datetime import date
        return (date.today() - self.data_churn).days
    
    @property
    def valor_perdido_formatado(self) -> str:
        """Retorna o valor perdido formatado como moeda"""
        if not self.valor_perdido:
            return "R$ 0,00"
        
        valor = float(self.valor_perdido)
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Converte o churn evento para dicionário"""
        data = super().to_dict()
        
        # Adiciona propriedades calculadas
        data["is_churn_recente"] = self.is_churn_recente
        data["is_churn_mes_atual"] = self.is_churn_mes_atual
        data["is_churn_trimestre_atual"] = self.is_churn_trimestre_atual
        data["dias_desde_churn"] = self.dias_desde_churn
        data["valor_perdido_formatado"] = self.valor_perdido_formatado
        
        if include_relationships:
            data["cliente"] = self.cliente.to_dict() if self.cliente else None
            data["contrato"] = self.contrato.to_dict() if self.contrato else None
            data["usuario"] = self.usuario.to_dict() if self.usuario else None
        
        return data


class ChurnAnalytics:
    """Classe para análise agregada de churn"""
    
    @staticmethod
    def calcular_metricas_gerais(churn_eventos: list) -> dict:
        """Calcula métricas gerais de churn"""
        if not churn_eventos:
            return {
                "total_churns": 0,
                "valor_total_perdido": 0,
                "media_valor_perdido": 0,
                "churns_mes_atual": 0,
                "churns_trimestre_atual": 0
            }
        
        total_churns = len(churn_eventos)
        valor_total_perdido = sum(float(e.valor_perdido or 0) for e in churn_eventos)
        media_valor_perdido = valor_total_perdido / total_churns if total_churns > 0 else 0
        
        churns_mes_atual = sum(1 for e in churn_eventos if e.is_churn_mes_atual)
        churns_trimestre_atual = sum(1 for e in churn_eventos if e.is_churn_trimestre_atual)
        
        return {
            "total_churns": total_churns,
            "valor_total_perdido": round(valor_total_perdido, 2),
            "media_valor_perdido": round(media_valor_perdido, 2),
            "churns_mes_atual": churns_mes_atual,
            "churns_trimestre_atual": churns_trimestre_atual
        }
    
    @staticmethod
    def analisar_motivos_churn(churn_eventos: list) -> dict:
        """Analisa os motivos de churn"""
        motivos = {}
        
        for evento in churn_eventos:
            motivo = evento.motivo
            if motivo not in motivos:
                motivos[motivo] = {
                    "quantidade": 0,
                    "valor_total": 0,
                    "percentual": 0
                }
            
            motivos[motivo]["quantidade"] += 1
            motivos[motivo]["valor_total"] += float(evento.valor_perdido or 0)
        
        # Calcula percentuais
        total = len(churn_eventos)
        for motivo in motivos:
            motivos[motivo]["percentual"] = (motivos[motivo]["quantidade"] / total) * 100
            motivos[motivo]["valor_total"] = round(motivos[motivo]["valor_total"], 2)
            motivos[motivo]["percentual"] = round(motivos[motivo]["percentual"], 2)
        
        # Ordena por quantidade
        motivos_ordenados = dict(
            sorted(motivos.items(), key=lambda x: x[1]["quantidade"], reverse=True)
        )
        
        return motivos_ordenados
    
    @staticmethod
    def calcular_taxa_churn(clientes_ativos: int, churns_periodo: int) -> float:
        """Calcula a taxa de churn para um período"""
        if clientes_ativos == 0:
            return 0.0
        
        taxa = (churns_periodo / clientes_ativos) * 100
        return round(taxa, 2) 