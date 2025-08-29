"""
Modelo de cliente central do sistema
"""
from sqlalchemy import Column, String, Date, Integer, Numeric, Text, Index
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Cliente(Base, TimestampMixin):
    """Modelo de cliente central para todos os módulos"""
    
    __tablename__ = "cliente"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Campos de identificação
    cust_id_externo = Column(String(100), unique=True, index=True)
    nome_principal = Column(String(255), nullable=False, index=True)
    nickname = Column(String(255), index=True)
    
    # Campos de contato
    telefone = Column(String(20), index=True)
    email = Column(String(255), index=True)
    
    # Campos de negócio
    loja_associada = Column(String(255), index=True)
    status_cliente = Column(String(50), default="ativo", nullable=False, index=True)
    jornada_iniciada_em = Column(Date, index=True)
    
    # Campos de LTV (Lifetime Value)
    ltv_meses = Column(Integer, default=0, nullable=False)
    ltv_valor = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Campos de informações adicionais
    info_adicional_vendas = Column(Text)
    info_adicional_cs = Column(Text)
    
    # Relacionamentos
    vendas = relationship("Venda", back_populates="cliente")
    contas = relationship("Conta", back_populates="cliente")
    contratos = relationship("Contrato", back_populates="cliente")
    eventos_cs = relationship("EventoCS", back_populates="cliente")
    churn_eventos = relationship("ChurnEvento", back_populates="cliente")
    health_scores = relationship("HealthScoreSnapshot", back_populates="cliente")
    csat_respostas = relationship("CSATResposta", back_populates="cliente")
    
    # Índices compostos
    __table_args__ = (
        Index('idx_cliente_status_ltv', 'status_cliente', 'ltv_valor'),
        Index('idx_cliente_jornada_status', 'jornada_iniciada_em', 'status_cliente'),
    )
    
    def __repr__(self):
        return f"<Cliente(id={self.id}, nome='{self.nome_principal}', status='{self.status_cliente}')>"
    
    @property
    def is_ativo(self) -> bool:
        """Verifica se o cliente está ativo"""
        return self.status_cliente == "ativo"
    
    @property
    def is_churn(self) -> bool:
        """Verifica se o cliente está em churn"""
        return self.status_cliente == "churn"
    
    @property
    def has_contratos_ativos(self) -> bool:
        """Verifica se o cliente tem contratos ativos"""
        return any(contrato.status_contrato == "ativo" for contrato in self.contratos)
    
    @property
    def contrato_principal(self):
        """Retorna o contrato principal do cliente (mais recente ou de maior valor)"""
        if not self.contratos:
            return None
        
        # Prioriza contratos ativos, depois por valor e data
        contratos_ativos = [c for c in self.contratos if c.status_contrato == "ativo"]
        if contratos_ativos:
            return max(contratos_ativos, key=lambda c: (c.valor_mensal, c.data_inicio))
        
        return max(self.contratos, key=lambda c: (c.valor_mensal, c.data_inicio))
    
    @property
    def dias_para_vencimento(self) -> int:
        """Retorna os dias para o próximo vencimento"""
        contrato = self.contrato_principal
        if not contrato:
            return None
        return contrato.dias_a_vencer
    
    @property
    def status_renovacao(self) -> str:
        """Retorna o status de renovação baseado no contrato principal"""
        contrato = self.contrato_principal
        if not contrato:
            return "sem_contrato"
        return contrato.status_contrato
    
    def calcular_ltv(self) -> tuple[int, float]:
        """Calcula o LTV em meses e valor baseado nos contratos"""
        total_meses = 0
        total_valor = 0
        
        for contrato in self.contratos:
            if contrato.status_contrato in ["ativo", "encerrado"]:
                # Calcula meses do contrato
                meses_contrato = contrato.duracao_meses * contrato.ciclo_atual
                total_meses += meses_contrato
                
                # Calcula valor total do contrato
                valor_total_contrato = contrato.valor_mensal * meses_contrato
                total_valor += valor_total_contrato
        
        return total_meses, float(total_valor)
    
    def atualizar_ltv(self) -> None:
        """Atualiza o LTV do cliente"""
        meses, valor = self.calcular_ltv()
        self.ltv_meses = meses
        self.ltv_valor = valor
    
    def marcar_churn(self, motivo: str, valor_perdido: float = None) -> None:
        """Marca o cliente como churn"""
        self.status_cliente = "churn"
        if valor_perdido:
            self.ltv_valor -= valor_perdido
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Converte o cliente para dicionário"""
        data = super().to_dict()
        
        if include_relationships:
            data["contratos"] = [c.to_dict() for c in self.contratos]
            data["vendas"] = [v.to_dict() for v in self.vendas]
            data["health_scores"] = [h.to_dict() for h in self.health_scores]
            data["csat_respostas"] = [c.to_dict() for c in self.csat_respostas]
        
        return data 