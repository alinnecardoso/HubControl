"""
Modelo de evento CS para gestão de interações
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class EventoCS(Base, TimestampMixin):
    """Modelo de evento CS para gestão de interações"""
    
    __tablename__ = "evento_cs"
    
    # Campos de identificação
    cliente_id = Column(ForeignKey("cliente.id"), nullable=False, index=True)
    contrato_id = Column(ForeignKey("contrato.id"), nullable=True, index=True)
    
    # Campos do evento
    tipo = Column(String(100), nullable=False, index=True)
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text)
    data_evento = Column(DateTime, index=True)
    
    # Campos de acompanhamento
    proximos_passos = Column(Text)
    responsavel_id = Column(ForeignKey("usuario.id"), nullable=True, index=True)
    status = Column(String(50), default="agendado", nullable=False, index=True)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="eventos_cs")
    contrato = relationship("Contrato", back_populates="eventos_cs")
    responsavel = relationship("Usuario", back_populates="eventos_cs")
    
    # Índices compostos
    __table_args__ = (
        Index('idx_evento_cs_cliente_data', 'cliente_id', 'data_evento'),
        Index('idx_evento_cs_responsavel_status', 'responsavel_id', 'status'),
        Index('idx_evento_cs_tipo_status', 'tipo', 'status'),
    )
    
    def __repr__(self):
        return f"<EventoCS(id={self.id}, cliente_id={self.cliente_id}, tipo='{self.tipo}', titulo='{self.titulo}')>"
    
    @property
    def is_agendado(self) -> bool:
        """Verifica se o evento está agendado"""
        return self.status == "agendado"
    
    @property
    def is_realizado(self) -> bool:
        """Verifica se o evento foi realizado"""
        return self.status == "realizado"
    
    @property
    def is_cancelado(self) -> bool:
        """Verifica se o evento foi cancelado"""
        return self.status == "cancelado"
    
    @property
    def is_adiado(self) -> bool:
        """Verifica se o evento foi adiado"""
        return self.status == "adiado"
    
    @property
    def is_atrasado(self) -> bool:
        """Verifica se o evento está atrasado"""
        if not self.data_evento or self.is_realizado or self.is_cancelado:
            return False
        
        from datetime import datetime
        return datetime.now() > self.data_evento
    
    @property
    def dias_para_evento(self) -> int:
        """Retorna os dias para o evento"""
        if not self.data_evento:
            return None
        
        from datetime import datetime
        delta = self.data_evento - datetime.now()
        return delta.days
    
    @property
    def is_urgente(self) -> bool:
        """Verifica se o evento é urgente (menos de 3 dias)"""
        dias = self.dias_para_evento
        return dias is not None and dias <= 3 and dias >= 0
    
    @property
    def is_hoje(self) -> bool:
        """Verifica se o evento é hoje"""
        if not self.data_evento:
            return False
        
        from datetime import datetime, date
        hoje = date.today()
        data_evento = self.data_evento.date()
        return data_evento == hoje
    
    def marcar_realizado(self, observacoes: str = None) -> None:
        """Marca o evento como realizado"""
        self.status = "realizado"
        if observacoes:
            self.proximos_passos = observacoes
    
    def cancelar_evento(self, motivo: str = None) -> None:
        """Cancela o evento"""
        self.status = "cancelado"
        if motivo:
            self.descricao = f"Cancelado: {motivo}"
    
    def adiar_evento(self, nova_data: DateTime, motivo: str = None) -> None:
        """Adia o evento para uma nova data"""
        self.status = "adiado"
        self.data_evento = nova_data
        if motivo:
            self.descricao = f"Adiado: {motivo}"
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Converte o evento CS para dicionário"""
        data = super().to_dict()
        
        # Adiciona propriedades calculadas
        data["is_agendado"] = self.is_agendado
        data["is_realizado"] = self.is_realizado
        data["is_cancelado"] = self.is_cancelado
        data["is_adiado"] = self.is_adiado
        data["is_atrasado"] = self.is_atrasado
        data["is_urgente"] = self.is_urgente
        data["is_hoje"] = self.is_hoje
        data["dias_para_evento"] = self.dias_para_evento
        
        if include_relationships:
            data["cliente"] = self.cliente.to_dict() if self.cliente else None
            data["contrato"] = self.contrato.to_dict() if self.contrato else None
            data["responsavel"] = self.responsavel.to_dict() if self.responsavel else None
        
        return data 