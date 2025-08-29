"""
Modelo de histórico de status de contrato
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class ContratoStatusHistorico(Base, TimestampMixin):
    """Modelo de histórico de status de contrato"""
    
    __tablename__ = "contrato_status_historico"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Campos de identificação
    contrato_id = Column(ForeignKey("contrato.id"), nullable=False, index=True)
    
    # Campos do histórico
    status_anterior = Column(String(50))
    status_novo = Column(String(50), nullable=False)
    motivo_mudanca = Column(Text)
    usuario_id = Column(ForeignKey("usuario.id"), nullable=True, index=True)
    
    # Relacionamentos
    contrato = relationship("Contrato", back_populates="status_historico")
    usuario = relationship("Usuario", back_populates="contratos_status_historico")
    
    def __repr__(self):
        return f"<ContratoStatusHistorico(id={self.id}, contrato_id={self.contrato_id}, status_anterior='{self.status_anterior}', status_novo='{self.status_novo}')>"
    
    @property
    def is_mudanca_importante(self) -> bool:
        """Verifica se a mudança de status é importante"""
        mudancas_importantes = [
            ("ativo", "pausado"),
            ("ativo", "a_vencer"),
            ("a_vencer", "renegociar"),
            ("a_vencer", "vencido"),
            ("vencido", "encerrado"),
            ("ativo", "encerrado")
        ]
        
        return (self.status_anterior, self.status_novo) in mudancas_importantes
    
    @property
    def is_melhoria_status(self) -> bool:
        """Verifica se a mudança representa uma melhoria no status"""
        melhorias = [
            ("pausado", "ativo"),
            ("a_vencer", "ativo"),
            ("renegociar", "ativo"),
            ("vencido", "ativo")
        ]
        
        return (self.status_anterior, self.status_novo) in melhorias
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Converte o histórico de status para dicionário"""
        data = super().to_dict()
        
        # Adiciona propriedades calculadas
        data["is_mudanca_importante"] = self.is_mudanca_importante
        data["is_melhoria_status"] = self.is_melhoria_status
        
        if include_relationships:
            data["contrato"] = self.contrato.to_dict() if self.contrato else None
            data["usuario"] = self.usuario.to_dict() if self.usuario else None
        
        return data 