"""
Rotas de Vendas e Gestão de Clientes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import date, datetime, timedelta
import logging
import os
import tempfile
import json

# Importar dependências
from api.auth_routes import get_current_user
from services.database import db_service
from services.import_export_service import import_export_service
from models.sales_models import Cliente, Contrato, VendaMetrica, ImportLog, Vendedor, Venda

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sales", tags=["Sales"])

# Modelos Pydantic para requests/responses
class ClienteCreate(BaseModel):
    cust_id: Optional[str] = None
    nickname: str
    nome_principal: Optional[str] = None
    status: str
    tempo_ativo: Optional[int] = None
    data_inicio: Optional[date] = None
    jornada_iniciada: Optional[date] = None
    ltv_meses: Optional[int] = None
    ltv_valor: Optional[float] = None
    observacoes: Optional[str] = None

class ClienteResponse(BaseModel):
    id: int
    cust_id: Optional[str]
    nickname: str
    nome_principal: Optional[str]
    status: str
    tempo_ativo: Optional[int]
    data_inicio: Optional[date]
    jornada_iniciada: Optional[date]
    ltv_meses: Optional[int]
    ltv_valor: Optional[float]
    observacoes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MetricasVendas(BaseModel):
    total_clientes: int
    clientes_ativos: int
    clientes_novos_mes: int
    clientes_churn_mes: int
    receita_recorrente: float
    ltv_medio: float
    ticket_medio: float
    taxa_churn: float

class ImportResponse(BaseModel):
    success: bool
    total_rows: int
    success_rows: int
    error_rows: int
    errors: List[str]
    import_id: Optional[int]

# Modelos para Vendedor
class VendedorCreate(BaseModel):
    nome: str
    email: str
    equipe_vendas_id: Optional[int] = None

class VendedorResponse(BaseModel):
    id: int
    nome: str
    email: str
    equipe_vendas_id: Optional[int]
    ativo: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Modelos para Venda
class VendaCreate(BaseModel):
    data_venda: date
    loja: str
    cliente_id: int
    produto: str
    valor_mensal: float
    vendedor_id: int
    contrato_meses: int
    forma_pagamento: str
    canal_venda: Optional[str] = None
    telefone_cliente: Optional[str] = None
    percentual_variavel: Optional[float] = None
    descricao: Optional[str] = None
    info_adicional: Optional[str] = None

class VendaResponse(BaseModel):
    id: int
    data_venda: date
    loja: str
    cliente_id: int
    produto: str
    valor_mensal: float
    vendedor_id: int
    contrato_meses: int
    forma_pagamento: str
    canal_venda: Optional[str]
    telefone_cliente: Optional[str]
    percentual_variavel: Optional[float]
    descricao: Optional[str]
    info_adicional: Optional[str]
    valor_total_contrato: Optional[float]
    valor_bonificacao: Optional[float]
    valor_total_com_bonificacao: Optional[float]
    is_recente: bool
    is_mes_atual: bool
    is_trimestre_atual: bool
    created_at: datetime
    updated_at: datetime
    
    # Relacionamentos
    cliente: Optional[ClienteResponse] = None
    vendedor: Optional[VendedorResponse] = None
    
    class Config:
        from_attributes = True

# Modelo para métricas de vendas (dashboard)
class DashboardVendas(BaseModel):
    total_vendas: int
    valor_total: float
    media_valor: float
    top_produtos: List[Dict[str, Any]]
    top_vendedores: List[Dict[str, Any]]

# Modelo para bonificação por vendedor
class BonificacaoVendedor(BaseModel):
    vendedor_id: int
    vendedor_nome: str
    total_vendas: int
    valor_total_vendas: float
    valor_total_bonificacao: float
    periodo_inicio: date
    periodo_fim: date

# Dependência para obter sessão do banco
def get_db():
    return next(db_service.get_db())

# Rotas de vendedores
@router.get("/vendedores", response_model=List[VendedorResponse])
async def listar_vendedores(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Listar vendedores"""
    try:
        query = db.query(Vendedor)
        
        if ativo is not None:
            query = query.filter(Vendedor.ativo == ativo)
        
        vendedores = query.offset(skip).limit(limit).all()
        return vendedores
        
    except Exception as e:
        logger.error(f"Erro ao listar vendedores: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/vendedores/{vendedor_id}", response_model=VendedorResponse)
async def obter_vendedor(
    vendedor_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Obter vendedor por ID"""
    vendedor = db.query(Vendedor).filter(Vendedor.id == vendedor_id).first()
    
    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor não encontrado")
    
    return vendedor

@router.post("/vendedores", response_model=VendedorResponse)
async def criar_vendedor(
    vendedor_data: VendedorCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Criar novo vendedor"""
    try:
        # Verificar se email já existe
        existing = db.query(Vendedor).filter(Vendedor.email == vendedor_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Vendedor com este email já existe")
        
        vendedor = Vendedor(**vendedor_data.dict())
        db.add(vendedor)
        db.commit()
        db.refresh(vendedor)
        
        return vendedor
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar vendedor: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.put("/vendedores/{vendedor_id}", response_model=VendedorResponse)
async def atualizar_vendedor(
    vendedor_id: int,
    vendedor_data: VendedorCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Atualizar vendedor"""
    try:
        vendedor = db.query(Vendedor).filter(Vendedor.id == vendedor_id).first()
        
        if not vendedor:
            raise HTTPException(status_code=404, detail="Vendedor não encontrado")
        
        # Atualizar campos
        for field, value in vendedor_data.dict(exclude_unset=True).items():
            setattr(vendedor, field, value)
        
        vendedor.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(vendedor)
        
        return vendedor
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar vendedor: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete("/vendedores/{vendedor_id}")
async def desativar_vendedor(
    vendedor_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Desativar vendedor (soft delete)"""
    try:
        vendedor = db.query(Vendedor).filter(Vendedor.id == vendedor_id).first()
        
        if not vendedor:
            raise HTTPException(status_code=404, detail="Vendedor não encontrado")
        
        vendedor.ativo = False
        vendedor.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Vendedor desativado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao desativar vendedor: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Rotas de clientes
@router.get("/clientes", response_model=List[ClienteResponse])
async def listar_clientes(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Listar clientes com filtros"""
    try:
        query = db.query(Cliente)
        
        # Filtros
        if status:
            query = query.filter(Cliente.status == status)
        
        if search:
            search_filter = or_(
                Cliente.nickname.ilike(f"%{search}%"),
                Cliente.nome_principal.ilike(f"%{search}%"),
                Cliente.cust_id.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Paginação
        clientes = query.offset(skip).limit(limit).all()
        
        return clientes
        
    except Exception as e:
        logger.error(f"Erro ao listar clientes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/clientes/{cliente_id}", response_model=ClienteResponse)
async def obter_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Obter cliente por ID"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return cliente

@router.post("/clientes", response_model=ClienteResponse)
async def criar_cliente(
    cliente_data: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Criar novo cliente"""
    try:
        # Verificar se já existe
        if cliente_data.cust_id:
            existing = db.query(Cliente).filter(Cliente.cust_id == cliente_data.cust_id).first()
            if existing:
                raise HTTPException(status_code=400, detail="Cliente com este CustId já existe")
        
        cliente = Cliente(**cliente_data.dict())
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        
        return cliente
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar cliente: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.put("/clientes/{cliente_id}", response_model=ClienteResponse)
async def atualizar_cliente(
    cliente_id: int,
    cliente_data: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Atualizar cliente"""
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        # Atualizar campos
        for field, value in cliente_data.dict(exclude_unset=True).items():
            setattr(cliente, field, value)
        
        cliente.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(cliente)
        
        return cliente
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar cliente: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete("/clientes/{cliente_id}")
async def deletar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Deletar cliente"""
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        db.delete(cliente)
        db.commit()
        
        return {"message": "Cliente deletado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar cliente: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Rotas de vendas
@router.get("/vendas", response_model=List[VendaResponse])
async def listar_vendas(
    skip: int = 0,
    limit: int = 100,
    vendedor_id: Optional[int] = None,
    cliente_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    loja: Optional[str] = None,
    produto: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Listar vendas com filtros - RF002, RF003, RF004"""
    try:
        query = db.query(Venda).options(
            joinedload(Venda.cliente),
            joinedload(Venda.vendedor)
        )
        
        # Filtros conforme RF003 e RF004
        if vendedor_id:
            query = query.filter(Venda.vendedor_id == vendedor_id)
        
        if cliente_id:
            query = query.filter(Venda.cliente_id == cliente_id)
        
        if data_inicio:
            query = query.filter(Venda.data_venda >= data_inicio)
        
        if data_fim:
            query = query.filter(Venda.data_venda <= data_fim)
        
        if loja:
            query = query.filter(Venda.loja.ilike(f"%{loja}%"))
        
        if produto:
            query = query.filter(Venda.produto.ilike(f"%{produto}%"))
        
        # Controle de acesso: vendedores só veem suas vendas (RNF002)
        if current_user.get("role") == "vendas":
            # Assumindo que o vendedor está vinculado ao usuário logado
            query = query.filter(Venda.vendedor_id == current_user.get("vendedor_id"))
        
        # Ordenação por data (mais recente primeiro) - RF002
        vendas = query.order_by(Venda.data_venda.desc()).offset(skip).limit(limit).all()
        
        return vendas
        
    except Exception as e:
        logger.error(f"Erro ao listar vendas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/vendas/{venda_id}", response_model=VendaResponse)
async def obter_venda(
    venda_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Obter detalhes de uma venda - RF006"""
    venda = db.query(Venda).options(
        joinedload(Venda.cliente),
        joinedload(Venda.vendedor)
    ).filter(Venda.id == venda_id).first()
    
    if not venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    
    # Controle de acesso: vendedores só veem suas vendas
    if current_user.get("role") == "vendas" and venda.vendedor_id != current_user.get("vendedor_id"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return venda

@router.post("/vendas", response_model=VendaResponse)
async def criar_venda(
    venda_data: VendaCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Registrar nova venda - RF001"""
    try:
        # Calcular campos automáticos conforme RN001
        valor_total_contrato = venda_data.valor_mensal * venda_data.contrato_meses
        valor_bonificacao = 0
        
        if venda_data.percentual_variavel:
            valor_bonificacao = venda_data.valor_mensal * (venda_data.percentual_variavel / 100)
        
        valor_total_com_bonificacao = valor_total_contrato + valor_bonificacao
        
        # Determinar status para dashboard
        hoje = date.today()
        data_venda = venda_data.data_venda
        
        is_recente = (hoje - data_venda).days <= 30
        is_mes_atual = data_venda.month == hoje.month and data_venda.year == hoje.year
        
        # Trimestre atual
        trimestre_atual = (hoje.month - 1) // 3 + 1
        trimestre_venda = (data_venda.month - 1) // 3 + 1
        is_trimestre_atual = trimestre_venda == trimestre_atual and data_venda.year == hoje.year
        
        # Criar venda
        venda_dict = venda_data.dict()
        venda_dict.update({
            'valor_total_contrato': valor_total_contrato,
            'valor_bonificacao': valor_bonificacao,
            'valor_total_com_bonificacao': valor_total_com_bonificacao,
            'is_recente': is_recente,
            'is_mes_atual': is_mes_atual,
            'is_trimestre_atual': is_trimestre_atual
        })
        
        venda = Venda(**venda_dict)
        db.add(venda)
        db.commit()
        db.refresh(venda)
        
        # Carregar relacionamentos
        venda = db.query(Venda).options(
            joinedload(Venda.cliente),
            joinedload(Venda.vendedor)
        ).filter(Venda.id == venda.id).first()
        
        return venda
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar venda: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.put("/vendas/{venda_id}", response_model=VendaResponse)
async def atualizar_venda(
    venda_id: int,
    venda_data: VendaCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Atualizar venda"""
    try:
        venda = db.query(Venda).filter(Venda.id == venda_id).first()
        
        if not venda:
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        # Controle de acesso: vendedores só editam suas vendas
        if current_user.get("role") == "vendas" and venda.vendedor_id != current_user.get("vendedor_id"):
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Recalcular campos automáticos
        valor_total_contrato = venda_data.valor_mensal * venda_data.contrato_meses
        valor_bonificacao = 0
        
        if venda_data.percentual_variavel:
            valor_bonificacao = venda_data.valor_mensal * (venda_data.percentual_variavel / 100)
        
        valor_total_com_bonificacao = valor_total_contrato + valor_bonificacao
        
        # Atualizar campos
        for field, value in venda_data.dict(exclude_unset=True).items():
            setattr(venda, field, value)
        
        venda.valor_total_contrato = valor_total_contrato
        venda.valor_bonificacao = valor_bonificacao
        venda.valor_total_com_bonificacao = valor_total_com_bonificacao
        venda.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(venda)
        
        return venda
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar venda: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete("/vendas/{venda_id}")
async def deletar_venda(
    venda_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Deletar venda"""
    try:
        venda = db.query(Venda).filter(Venda.id == venda_id).first()
        
        if not venda:
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        # Controle de acesso
        if current_user.get("role") == "vendas" and venda.vendedor_id != current_user.get("vendedor_id"):
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        db.delete(venda)
        db.commit()
        
        return {"message": "Venda deletada com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar venda: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Rota para bonificação por vendedor - RF005
@router.get("/vendedores/{vendedor_id}/bonificacao", response_model=BonificacaoVendedor)
async def calcular_bonificacao_vendedor(
    vendedor_id: int,
    data_inicio: date,
    data_fim: date,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Calcular bonificação por vendedor em período específico - RF005"""
    try:
        # Verificar se vendedor existe
        vendedor = db.query(Vendedor).filter(Vendedor.id == vendedor_id).first()
        if not vendedor:
            raise HTTPException(status_code=404, detail="Vendedor não encontrado")
        
        # Buscar vendas do período
        vendas = db.query(Venda).filter(
            and_(
                Venda.vendedor_id == vendedor_id,
                Venda.data_venda >= data_inicio,
                Venda.data_venda <= data_fim
            )
        ).all()
        
        # Calcular totais
        total_vendas = len(vendas)
        valor_total_vendas = sum(venda.valor_mensal for venda in vendas)
        valor_total_bonificacao = sum(venda.valor_bonificacao or 0 for venda in vendas)
        
        return BonificacaoVendedor(
            vendedor_id=vendedor_id,
            vendedor_nome=vendedor.nome,
            total_vendas=total_vendas,
            valor_total_vendas=valor_total_vendas,
            valor_total_bonificacao=valor_total_bonificacao,
            periodo_inicio=data_inicio,
            periodo_fim=data_fim
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao calcular bonificação: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Dashboard de vendas - RF007, RF008
@router.get("/dashboard", response_model=DashboardVendas)
async def dashboard_vendas(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Dashboard de métricas de vendas - RF007, RF008"""
    try:
        # Filtro por mês/ano se especificado
        query = db.query(Venda)
        
        if mes and ano:
            query = query.filter(
                and_(
                    func.extract('month', Venda.data_venda) == mes,
                    func.extract('year', Venda.data_venda) == ano
                )
            )
        elif ano:
            query = query.filter(func.extract('year', Venda.data_venda) == ano)
        
        vendas = query.all()
        
        # Métricas básicas
        total_vendas = len(vendas)
        valor_total = sum(venda.valor_mensal for venda in vendas)
        media_valor = valor_total / total_vendas if total_vendas > 0 else 0
        
        # Top 5 produtos
        produtos_count = {}
        for venda in vendas:
            if venda.produto in produtos_count:
                produtos_count[venda.produto]['quantidade'] += 1
                produtos_count[venda.produto]['valor_total'] += venda.valor_mensal
            else:
                produtos_count[venda.produto] = {
                    'quantidade': 1,
                    'valor_total': venda.valor_mensal
                }
        
        top_produtos = sorted(
            [{'produto': k, **v} for k, v in produtos_count.items()],
            key=lambda x: x['valor_total'],
            reverse=True
        )[:5]
        
        # Top 5 vendedores
        vendedores_stats = {}
        for venda in vendas:
            if venda.vendedor_id in vendedores_stats:
                vendedores_stats[venda.vendedor_id]['quantidade'] += 1
                vendedores_stats[venda.vendedor_id]['valor_total'] += venda.valor_mensal
            else:
                vendedor = db.query(Vendedor).filter(Vendedor.id == venda.vendedor_id).first()
                vendedores_stats[venda.vendedor_id] = {
                    'nome': vendedor.nome if vendedor else 'Desconhecido',
                    'quantidade': 1,
                    'valor_total': venda.valor_mensal
                }
        
        top_vendedores = sorted(
            [{'vendedor_id': k, **v} for k, v in vendedores_stats.items()],
            key=lambda x: x['valor_total'],
            reverse=True
        )[:5]
        
        return DashboardVendas(
            total_vendas=total_vendas,
            valor_total=valor_total,
            media_valor=media_valor,
            top_produtos=top_produtos,
            top_vendedores=top_vendedores
        )
        
    except Exception as e:
        logger.error(f"Erro no dashboard: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Rotas de métricas
@router.get("/metricas", response_model=MetricasVendas)
async def obter_metricas(
    periodo: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Obter métricas de vendas"""
    try:
        if not periodo:
            periodo = date.today().replace(day=1)  # Primeiro dia do mês atual
        
        # Calcular métricas
        total_clientes = db.query(Cliente).count()
        
        clientes_ativos = db.query(Cliente).filter(
            Cliente.status.in_(['Ativo ML', 'Ativo'])
        ).count()
        
        # Clientes novos no mês
        primeiro_dia_mes = periodo
        ultimo_dia_mes = (primeiro_dia_mes.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        clientes_novos_mes = db.query(Cliente).filter(
            and_(
                Cliente.data_inicio >= primeiro_dia_mes,
                Cliente.data_inicio <= ultimo_dia_mes
            )
        ).count()
        
        # Clientes churn no mês
        clientes_churn_mes = db.query(Cliente).filter(
            and_(
                Cliente.status.in_(['Churn', 'Não é MAIS cliente']),
                Cliente.updated_at >= primeiro_dia_mes,
                Cliente.updated_at <= ultimo_dia_mes
            )
        ).count()
        
        # Receita recorrente (soma dos contratos ativos)
        receita_result = db.query(func.sum(Contrato.valor_mensal)).join(Cliente).filter(
            and_(
                Cliente.status.in_(['Ativo ML', 'Ativo']),
                Contrato.ativo == True
            )
        ).scalar()
        
        receita_recorrente = float(receita_result or 0)
        
        # LTV médio
        ltv_result = db.query(func.avg(Cliente.ltv_valor)).filter(
            Cliente.ltv_valor.isnot(None)
        ).scalar()
        
        ltv_medio = float(ltv_result or 0)
        
        # Ticket médio
        ticket_result = db.query(func.avg(Contrato.valor_mensal)).join(Cliente).filter(
            and_(
                Cliente.status.in_(['Ativo ML', 'Ativo']),
                Contrato.ativo == True
            )
        ).scalar()
        
        ticket_medio = float(ticket_result or 0)
        
        # Taxa de churn
        taxa_churn = (clientes_churn_mes / total_clientes * 100) if total_clientes > 0 else 0
        
        return MetricasVendas(
            total_clientes=total_clientes,
            clientes_ativos=clientes_ativos,
            clientes_novos_mes=clientes_novos_mes,
            clientes_churn_mes=clientes_churn_mes,
            receita_recorrente=receita_recorrente,
            ltv_medio=ltv_medio,
            ticket_medio=ticket_medio,
            taxa_churn=taxa_churn
        )
        
    except Exception as e:
        logger.error(f"Erro ao calcular métricas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Rotas de importação/exportação
@router.post("/import", response_model=ImportResponse)
async def importar_planilha(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Importar dados de planilha Excel/CSV"""
    try:
        # Validar tipo de arquivo
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="Formato de arquivo não suportado")
        
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Importar dados
            result = import_export_service.import_from_excel(
                temp_path, 
                db, 
                current_user["user_id"]
            )
            
            return ImportResponse(**result)
            
        finally:
            # Limpar arquivo temporário
            os.unlink(temp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na importação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na importação: {str(e)}")

@router.get("/export")
async def exportar_planilha(
    status: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_final: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Exportar dados para Excel"""
    try:
        filters = {}
        if status:
            filters['status'] = status
        if data_inicio:
            filters['data_inicio'] = data_inicio
        if data_final:
            filters['data_final'] = data_final
        
        # Gerar arquivo
        filepath = import_export_service.export_to_excel(db, filters)
        
        # Ler arquivo
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Limpar arquivo temporário
        os.unlink(filepath)
        
        # Retornar arquivo
        filename = os.path.basename(filepath)
        return Response(
            content=content,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Erro na exportação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na exportação: {str(e)}")

@router.get("/import-logs")
async def listar_logs_importacao(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Listar logs de importação"""
    try:
        logs = db.query(ImportLog).order_by(ImportLog.created_at.desc()).offset(skip).limit(limit).all()
        
        result = []
        for log in logs:
            result.append({
                "id": log.id,
                "filename": log.filename,
                "total_rows": log.total_rows,
                "success_rows": log.success_rows,
                "error_rows": log.error_rows,
                "status": log.status,
                "created_at": log.created_at,
                "errors": json.loads(log.errors_detail) if log.errors_detail else []
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao listar logs: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Rota de inicialização do banco
@router.post("/init-db")
async def inicializar_banco(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Inicializar tabelas do banco (apenas para admins)"""
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Apenas administradores podem inicializar o banco")
        
        db_service.create_tables()
        
        return {"message": "Banco de dados inicializado com sucesso!"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao inicializar banco: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao inicializar banco: {str(e)}")

@router.get("/test-db")
async def testar_conexao():
    """Testar conexão com banco"""
    result = db_service.test_connection()
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    return {"message": "Conexão com banco funcionando!", "result": result["result"]}