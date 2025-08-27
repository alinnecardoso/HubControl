"""
Modelo base para todos os modelos do sistema
"""
from datetime import datetime
from typing import Any, Dict
from sqlalchemy import Column, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr


class CustomBase:
    """Classe base personalizada para todos os modelos"""
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Gera automaticamente o nome da tabela baseado no nome da classe"""
        return cls.__name__.lower()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para dicionário"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat() if value else None
            else:
                result[column.name] = value
        return result
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Atualiza o modelo a partir de um dicionário"""
        for key, value in data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)


# Criar a base declarativa
Base = declarative_base(cls=CustomBase)


class TimestampMixin:
    """Mixin para adicionar campos de timestamp"""
    
    data_criacao = Column(DateTime, default=func.now(), nullable=False)
    data_ultima_atualizacao = Column(
        DateTime, 
        default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )


class SoftDeleteMixin:
    """Mixin para soft delete"""
    
    ativo = Column(Boolean, default=True, nullable=False)
    
    def soft_delete(self) -> None:
        """Marca o registro como inativo"""
        self.ativo = False
        self.data_ultima_atualizacao = datetime.utcnow()
    
    def restore(self) -> None:
        """Restaura o registro"""
        self.ativo = True
        self.data_ultima_atualizacao = datetime.utcnow() 