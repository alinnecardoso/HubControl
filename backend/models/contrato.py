"""
Modelo de contrato do sistema
"""
from datetime import date, datetime, timedelta
from sqlalchemy import Column, String, Date, Integer, Numeric, Boolean, ForeignKey, Computed
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Contrato(Base, TimestampMixin):
    """Modelo de contrato com gestão de ciclos e renovação"""
    
    __tablename__ = "contrato"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Campos de identificação
    cliente_id = Column(ForeignKey("cliente.id"), nullable=False, index=True)
    conta_id = Column(ForeignKey("conta.id"), nullable=True, index=True)
    
    # Campos de período
    data_inicio = Column(Date, nullable=False, index=True)
    data_fim = Column(Date, nullable=False, index=True)
    duracao_meses = Column(Integer, nullable=False)
    
    # Campos financeiros
    valor_mensal = Column(Numeric(15, 2), nullable=False)
    
    # Campos de status e ciclo
    status_contrato = Column(String(50), default="ativo", nullable=False, index=True)
    ciclo_atual = Column(Integer, default=1, nullable=False)
    auto_renovacao = Column(Boolean, default=False, nullable=False)
    
    # Campo calculado (removido computed column por incompatibilidade)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="contratos")
    conta = relationship("Conta", back_populates="contratos")
    status_historico = relationship("ContratoStatusHistorico", back_populates="contrato")
    historico_ciclos = relationship("HistoricoCicloContrato", back_populates="contrato")
    renovacoes = relationship("Renovacao", back_populates="contrato")
    eventos_cs = relationship("EventoCS", back_populates="contrato")
    churn_eventos = relationship("ChurnEvento", back_populates="contrato")
    
    def __repr__(self):
        return f"<Contrato(id={self.id}, cliente_id={self.cliente_id}, status='{self.status_contrato}', ciclo={self.ciclo_atual})>"
    
    @property
    def is_ativo(self) -> bool:
        """Verifica se o contrato está ativo"""
        return self.status_contrato == "ativo"
    
    @property
    def is_pausado(self) -> bool:
        """Verifica se o contrato está pausado"""
        return self.status_contrato == "pausado"
    
    @property
    def is_a_vencer(self) -> bool:
        """Verifica se o contrato está a vencer"""
        return self.status_contrato == "a_vencer"
    
    @property
    def is_vencido(self) -> bool:
        """Verifica se o contrato está vencido"""
        return self.status_contrato == "vencido"
    
    @property
    def is_encerrado(self) -> bool:
        """Verifica se o contrato está encerrado"""
        return self.status_contrato == "encerrado"
    
    @property
    def dias_restantes(self) -> int:
        """Retorna os dias restantes até o vencimento"""
        if self.data_fim:
            return (self.data_fim - date.today()).days
        return 0
    
    @property
    def valor_total_contrato(self) -> float:
        """Calcula o valor total do contrato (valor_mensal * duracao_meses * ciclo_atual)"""
        return float(self.valor_mensal * self.duracao_meses * self.ciclo_atual)
    
    @property
    def valor_restante(self) -> float:
        """Calcula o valor restante do contrato"""
        if self.is_encerrado:
            return 0
        
        # Calcula meses restantes
        if self.data_fim:
            meses_restantes = max(0, (self.data_fim - date.today()).days / 30)
            return float(self.valor_mensal * meses_restantes)
        
        return float(self.valor_mensal * self.duracao_meses)
    
    def atualizar_status_por_dias(self, dias_limite: int = 30) -> None:
        """Atualiza o status do contrato baseado nos dias para vencimento"""
        dias = self.dias_restantes
        
        if dias <= 0:
            if self.status_contrato != "vencido":
                self.mudar_status("vencido", "Contrato vencido automaticamente")
        elif dias <= dias_limite:
            if self.status_contrato not in ["a_vencer", "renegociar"]:
                self.mudar_status("a_vencer", f"Contrato a vencer em {dias} dias")
    
    def mudar_status(self, novo_status: str, motivo: str = None, usuario_id: str = None) -> None:
        """Muda o status do contrato e registra no histórico"""
        from .contrato_status_historico import ContratoStatusHistorico
        
        status_anterior = self.status_contrato
        self.status_contrato = novo_status
        
        # Registra no histórico
        historico = ContratoStatusHistorico(
            contrato_id=self.id,
            status_anterior=status_anterior,
            status_novo=novo_status,
            motivo_mudanca=motivo,
            usuario_id=usuario_id
        )
        
        # Adiciona ao relacionamento (será salvo quando o contrato for salvo)
        if not hasattr(self, 'status_historico'):
            self.status_historico = []
        self.status_historico.append(historico)
    
    def renovar_contrato(self, novo_ciclo: int, nova_data_fim: date, 
                         novo_valor_mensal: float = None, tipo: str = "manual",
                         observacoes: str = None, usuario_id: str = None) -> None:
        """Renova o contrato para um novo ciclo"""
        from .renovacao import Renovacao
        from .historico_ciclo_contrato import HistoricoCicloContrato
        
        # Registra o ciclo atual no histórico
        historico_ciclo = HistoricoCicloContrato(
            contrato_id=self.id,
            ciclo=self.ciclo_atual,
            data_inicio=self.data_inicio,
            data_fim=self.data_fim,
            duracao_meses=self.duracao_meses,
            valor_mensal=self.valor_mensal
        )
        
        # Adiciona ao relacionamento
        if not hasattr(self, 'historico_ciclos'):
            self.historico_ciclos = []
        self.historico_ciclos.append(historico_ciclo)
        
        # Registra a renovação
        renovacao = Renovacao(
            contrato_id=self.id,
            tipo=tipo,
            data_renovacao=date.today(),
            novo_ciclo=novo_ciclo,
            nova_data_fim=nova_data_fim,
            novo_valor_mensal=novo_valor_mensal or self.valor_mensal,
            observacoes=observacoes,
            usuario_id=usuario_id
        )
        
        # Adiciona ao relacionamento
        if not hasattr(self, 'renovacoes'):
            self.renovacoes = []
        self.renovacoes.append(renovacao)
        
        # Atualiza o contrato
        self.ciclo_atual = novo_ciclo
        self.data_inicio = self.data_fim
        self.data_fim = nova_data_fim
        if novo_valor_mensal:
            self.valor_mensal = novo_valor_mensal
        
        # Atualiza o status
        self.mudar_status("ativo", f"Contrato renovado para ciclo {novo_ciclo}")
    
    def auto_renovar(self) -> bool:
        """Executa a renovação automática se configurada"""
        if not self.auto_renovacao or self.is_vencido:
            return False
        
        # Calcula nova data de fim
        nova_data_fim = self.data_fim + timedelta(days=self.duracao_meses * 30)
        
        # Renova o contrato
        self.renovar_contrato(
            novo_ciclo=self.ciclo_atual + 1,
            nova_data_fim=nova_data_fim,
            tipo="auto_renovacao",
            observacoes="Renovação automática"
        )
        
        return True
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Converte o contrato para dicionário"""
        data = super().to_dict()
        
        if include_relationships:
            data["cliente"] = self.cliente.to_dict() if self.cliente else None
            data["conta"] = self.conta.to_dict() if self.conta else None
            data["status_historico"] = [h.to_dict() for h in self.status_historico]
            data["historico_ciclos"] = [h.to_dict() for h in self.historico_ciclos]
            data["renovacoes"] = [r.to_dict() for r in self.renovacoes]
        
        return data 