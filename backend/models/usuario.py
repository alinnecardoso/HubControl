"""
Modelo de usuário do sistema
"""
from sqlalchemy import Column, String, Boolean, DateTime, func, Integer
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin


class Usuario(Base, TimestampMixin, SoftDeleteMixin):
    """Modelo de usuário do sistema"""
    
    __tablename__ = "usuario"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Campos básicos
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(String(50), nullable=False, index=True)
    
    # Relacionamentos
    vendedor = relationship("Vendedor", back_populates="usuario", uselist=False)
    assessor = relationship("Assessor", back_populates="usuario", uselist=False)
    
    # Relacionamentos de auditoria
    contratos_status_historico = relationship("ContratoStatusHistorico", back_populates="usuario")
    renovacoes = relationship("Renovacao", back_populates="usuario")
    eventos_cs = relationship("EventoCS", back_populates="responsavel")
    churn_eventos = relationship("ChurnEvento", back_populates="usuario")
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, nome='{self.nome}', email='{self.email}', perfil='{self.perfil}')>"
    
    @property
    def is_admin(self) -> bool:
        """Verifica se o usuário é administrador"""
        return self.perfil == "admin"
    
    @property
    def is_cs(self) -> bool:
        """Verifica se o usuário é do Customer Success"""
        return self.perfil == "cs"
    
    @property
    def is_vendedor(self) -> bool:
        """Verifica se o usuário é vendedor"""
        return self.perfil == "vendedor"
    
    @property
    def is_gerente(self) -> bool:
        """Verifica se o usuário é gerente"""
        return self.perfil == "gerente"
    
    def can_access_module(self, module: str) -> bool:
        """Verifica se o usuário pode acessar um módulo específico"""
        if self.is_admin:
            return True
        
        module_permissions = {
            "cs": ["cs", "gerente"],
            "vendas": ["vendedor", "gerente"],
            "financeiro": ["gerente"],
            "dataops": ["gerente"]
        }
        
        return self.perfil in module_permissions.get(module, [])
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Converte o usuário para dicionário"""
        data = super().to_dict()
        if not include_sensitive:
            data.pop("senha_hash", None)
        return data 