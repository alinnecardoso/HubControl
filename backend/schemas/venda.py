"""
Schemas Pydantic para validação de dados de venda
"""
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class VendaBase(BaseModel):
    """Schema base para venda"""
    
    data: date = Field(..., description="Data da venda")
    loja: str = Field(..., min_length=1, max_length=255, description="Nome da loja")
    cliente_id: int = Field(..., description="ID do cliente")
    produto: str = Field(..., min_length=1, max_length=255, description="Nome do produto/serviço")
    valor_mensal: float = Field(..., gt=0, description="Valor mensal da venda")
    vendedor_id: int = Field(..., description="ID do vendedor")
    contrato_meses: int = Field(..., gt=0, le=120, description="Duração do contrato em meses")
    forma_pagamento: str = Field(..., min_length=1, max_length=100, description="Método de pagamento")
    
    # Campos opcionais
    telefone_cliente: Optional[str] = Field(None, max_length=20, description="Telefone do cliente")
    percentual_variavel: Optional[float] = Field(None, ge=0, le=100, description="Percentual variável para bonificação")
    canal_venda: Optional[str] = Field(None, max_length=100, description="Canal de venda")
    descricao: Optional[str] = Field(None, description="Descrição da venda")
    info_adicional: Optional[str] = Field(None, description="Informações adicionais")
    
    @validator('valor_mensal')
    def validar_valor_mensal(cls, v):
        """Valida o valor mensal"""
        if v <= 0:
            raise ValueError('O valor mensal deve ser maior que zero')
        return v
    
    @validator('contrato_meses')
    def validar_contrato_meses(cls, v):
        """Valida a duração do contrato"""
        if v <= 0:
            raise ValueError('A duração do contrato deve ser maior que zero')
        if v > 120:  # Máximo 10 anos
            raise ValueError('A duração do contrato não pode ser maior que 120 meses')
        return v


class VendaCreate(VendaBase):
    """Schema para criação de venda"""
    pass


class VendaUpdate(BaseModel):
    """Schema para atualização de venda"""
    
    data: Optional[date] = Field(None, description="Data da venda")
    loja: Optional[str] = Field(None, min_length=1, max_length=255, description="Nome da loja")
    cliente_id: Optional[int] = Field(None, description="ID do cliente")
    produto: Optional[str] = Field(None, min_length=1, max_length=255, description="Nome do produto/serviço")
    valor_mensal: Optional[float] = Field(None, gt=0, description="Valor mensal da venda")
    vendedor_id: Optional[int] = Field(None, description="ID do vendedor")
    contrato_meses: Optional[int] = Field(None, gt=0, le=120, description="Duração do contrato em meses")
    forma_pagamento: Optional[str] = Field(None, min_length=1, max_length=100, description="Método de pagamento")
    telefone_cliente: Optional[str] = Field(None, max_length=20, description="Telefone do cliente")
    percentual_variavel: Optional[float] = Field(None, ge=0, le=100, description="Percentual variável para bonificação")
    canal_venda: Optional[str] = Field(None, max_length=100, description="Canal de venda")
    descricao: Optional[str] = Field(None, description="Descrição da venda")
    info_adicional: Optional[str] = Field(None, description="Informações adicionais")


class VendaResponse(VendaBase):
    """Schema para resposta de venda"""
    
    id: int = Field(..., description="ID único da venda")
    data_criacao: date = Field(..., description="Data de criação")
    data_ultima_atualizacao: date = Field(..., description="Data da última atualização")
    
    # Campos calculados
    valor_total_contrato: float = Field(..., description="Valor total do contrato")
    valor_bonificacao: float = Field(..., description="Valor da bonificação")
    valor_total_com_bonificacao: float = Field(..., description="Valor total incluindo bonificação")
    is_recente: bool = Field(..., description="Indica se a venda é recente (últimos 30 dias)")
    is_mes_atual: bool = Field(..., description="Indica se a venda é do mês atual")
    is_trimestre_atual: bool = Field(..., description="Indica se a venda é do trimestre atual")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class VendaListResponse(BaseModel):
    """Schema para resposta de lista de vendas"""
    
    vendas: List[VendaResponse] = Field(..., description="Lista de vendas")
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Número de registros pulados")
    limit: int = Field(..., description="Limite de registros retornados")


class VendedorMetricsResponse(BaseModel):
    """Schema para métricas de vendedor"""
    
    vendedor_id: int = Field(..., description="ID do vendedor")
    nome_vendedor: str = Field(..., description="Nome do vendedor")
    periodo: dict = Field(..., description="Período das métricas")
    total_vendas: int = Field(..., description="Total de vendas")
    valor_total: float = Field(..., description="Valor total das vendas")
    valor_bonificacoes: float = Field(..., description="Valor total das bonificações")
    media_valor: float = Field(..., description="Média de valor por venda")
    top_produtos: List[tuple] = Field(..., description="Top produtos vendidos")


class VendaMetricsResponse(BaseModel):
    """Schema para métricas gerais de vendas"""
    
    periodo: dict = Field(..., description="Período das métricas")
    total_vendas: int = Field(..., description="Total de vendas")
    valor_total: float = Field(..., description="Valor total das vendas")
    media_valor: float = Field(..., description="Média de valor por venda")
    top_produtos: List[dict] = Field(..., description="Top produtos vendidos")
    top_vendedores: List[dict] = Field(..., description="Top vendedores")


class VendaFilter(BaseModel):
    """Schema para filtros de venda"""
    
    data_inicio: Optional[date] = Field(None, description="Data de início para filtro")
    data_fim: Optional[date] = Field(None, description="Data de fim para filtro")
    vendedor_id: Optional[int] = Field(None, description="ID do vendedor para filtro")
    cliente_id: Optional[int] = Field(None, description="ID do cliente para filtro")
    loja: Optional[str] = Field(None, description="Nome da loja para filtro")
    produto: Optional[str] = Field(None, description="Nome do produto para filtro")
    skip: int = Field(0, ge=0, description="Número de registros para pular")
    limit: int = Field(100, ge=1, le=1000, description="Número máximo de registros")
    
    @validator('data_fim')
    def validar_data_fim(cls, v, values):
        """Valida se a data de fim é posterior à data de início"""
        if v and 'data_inicio' in values and values['data_inicio']:
            if v < values['data_inicio']:
                raise ValueError('A data de fim deve ser posterior à data de início')
        return v 