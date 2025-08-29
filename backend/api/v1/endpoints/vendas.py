"""
Endpoint de vendas do sistema HubControl
"""
from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from database.connection import get_db
from models.venda import Venda
from models.vendedor import Vendedor
from models.cliente import Cliente
from schemas.venda import (
    VendaCreate,
    VendaUpdate,
    VendaResponse,
    VendaListResponse,
    VendaMetricsResponse,
    VendedorMetricsResponse
)

router = APIRouter()


@router.post("/", response_model=VendaResponse, summary="Criar nova venda")
async def criar_venda(
    venda: VendaCreate,
    db: Session = Depends(get_db)
):
    """
    Cria uma nova venda no sistema.
    
    - **data**: Data da venda
    - **loja**: Nome da loja
    - **cliente_id**: ID do cliente
    - **produto**: Nome do produto/serviço
    - **valor_mensal**: Valor mensal da venda
    - **vendedor_id**: ID do vendedor
    - **contrato_meses**: Duração do contrato em meses
    - **forma_pagamento**: Método de pagamento
    """
    try:
        # Verifica se o cliente existe
        cliente = db.query(Cliente).filter(Cliente.id == venda.cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        # Verifica se o vendedor existe
        vendedor = db.query(Vendedor).filter(Vendedor.id == venda.vendedor_id).first()
        if not vendedor:
            raise HTTPException(status_code=404, detail="Vendedor não encontrado")
        
        # Cria a venda
        db_venda = Venda(**venda.dict())
        db.add(db_venda)
        db.commit()
        db.refresh(db_venda)
        
        return VendaResponse.from_orm(db_venda)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar venda: {str(e)}")


@router.get("/", response_model=VendaListResponse, summary="Listar vendas")
async def listar_vendas(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    data_inicio: Optional[date] = Query(None, description="Data de início para filtro"),
    data_fim: Optional[date] = Query(None, description="Data de fim para filtro"),
    vendedor_id: Optional[int] = Query(None, description="ID do vendedor para filtro"),
    cliente_id: Optional[int] = Query(None, description="ID do cliente para filtro"),
    loja: Optional[str] = Query(None, description="Nome da loja para filtro"),
    produto: Optional[str] = Query(None, description="Nome do produto para filtro"),
    db: Session = Depends(get_db)
):
    """
    Lista as vendas com filtros opcionais.
    
    - **skip**: Número de registros para pular (paginação)
    - **limit**: Número máximo de registros retornados
    - **data_inicio**: Data de início para filtro
    - **data_fim**: Data de fim para filtro
    - **vendedor_id**: ID do vendedor para filtro
    - **cliente_id**: ID do cliente para filtro
    - **loja**: Nome da loja para filtro
    - **produto**: Nome do produto para filtro
    """
    try:
        # Query base
        query = db.query(Venda)
        
        # Aplica filtros
        if data_inicio:
            query = query.filter(Venda.data >= data_inicio)
        if data_fim:
            query = query.filter(Venda.data <= data_fim)
        if vendedor_id:
            query = query.filter(Venda.vendedor_id == vendedor_id)
        if cliente_id:
            query = query.filter(Venda.cliente_id == cliente_id)
        if loja:
            query = query.filter(Venda.loja.ilike(f"%{loja}%"))
        if produto:
            query = query.filter(Venda.produto.ilike(f"%{produto}%"))
        
        # Conta total de registros
        total = query.count()
        
        # Aplica paginação e ordenação
        vendas = query.order_by(Venda.data.desc()).offset(skip).limit(limit).all()
        
        return VendaListResponse(
            vendas=[VendaResponse.from_orm(v) for v in vendas],
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar vendas: {str(e)}")


@router.get("/metricas/gerais", response_model=VendaMetricsResponse, summary="Métricas gerais de vendas")
async def obter_metricas_gerais(
    data_inicio: Optional[date] = Query(None, description="Data de início para filtro"),
    data_fim: Optional[date] = Query(None, description="Data de fim para filtro"),
    db: Session = Depends(get_db)
):
    """
    Obtém métricas gerais de vendas.
    """
    try:
        # Query base
        query = db.query(Venda)
        
        # Aplica filtros de data se fornecidos
        if data_inicio:
            query = query.filter(Venda.data >= data_inicio)
        if data_fim:
            query = query.filter(Venda.data <= data_fim)
        
        vendas = query.all()
        
        # Calcula métricas
        total_vendas = len(vendas)
        valor_total = sum(float(v.valor_mensal) for v in vendas)
        media_valor = valor_total / total_vendas if total_vendas > 0 else 0
        
        # Top produtos
        produtos = {}
        for venda in vendas:
            if venda.produto not in produtos:
                produtos[venda.produto] = {"quantidade": 0, "valor_total": 0}
            produtos[venda.produto]["quantidade"] += 1
            produtos[venda.produto]["valor_total"] += float(venda.valor_mensal)
        
        top_produtos = sorted(
            produtos.items(), 
            key=lambda x: x[1]["valor_total"], 
            reverse=True
        )[:5]
        
        # Top vendedores
        vendedores = {}
        for venda in vendas:
            if venda.vendedor_id not in vendedores:
                vendedores[venda.vendedor_id] = {"quantidade": 0, "valor_total": 0}
            vendedores[venda.vendedor_id]["quantidade"] += 1
            vendedores[venda.vendedor_id]["valor_total"] += float(venda.valor_mensal)
        
        top_vendedores = sorted(
            vendedores.items(), 
            key=lambda x: x[1]["valor_total"], 
            reverse=True
        )[:5]
        
        return VendaMetricsResponse(
            periodo={
                "data_inicio": data_inicio.isoformat() if data_inicio else None,
                "data_fim": data_fim.isoformat() if data_fim else None
            },
            total_vendas=total_vendas,
            valor_total=round(valor_total, 2),
            media_valor=round(media_valor, 2),
            top_produtos=top_produtos,
            top_vendedores=top_vendedores
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter métricas: {str(e)}")


@router.get("/{venda_id}", response_model=VendaResponse, summary="Obter venda por ID")
async def obter_venda(
    venda_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtém uma venda específica por ID.
    """
    try:
        venda = db.query(Venda).filter(Venda.id == venda_id).first()
        if not venda:
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        return VendaResponse.from_orm(venda)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter venda: {str(e)}")


@router.put("/{venda_id}", response_model=VendaResponse, summary="Atualizar venda")
async def atualizar_venda(
    venda_id: int,
    venda_update: VendaUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza uma venda existente.
    """
    try:
        db_venda = db.query(Venda).filter(Venda.id == venda_id).first()
        if not db_venda:
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        # Atualiza apenas os campos fornecidos
        update_data = venda_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_venda, field, value)
        
        db.commit()
        db.refresh(db_venda)
        
        return VendaResponse.from_orm(db_venda)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar venda: {str(e)}")


@router.delete("/{venda_id}", summary="Excluir venda")
async def excluir_venda(
    venda_id: int,
    db: Session = Depends(get_db)
):
    """
    Exclui uma venda (hard delete).
    """
    try:
        db_venda = db.query(Venda).filter(Venda.id == venda_id).first()
        if not db_venda:
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        db.delete(db_venda)
        db.commit()
        
        return {"message": "Venda excluída com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao excluir venda: {str(e)}")


@router.get("/vendedor/{vendedor_id}/metricas", response_model=VendedorMetricsResponse, summary="Métricas do vendedor")
async def obter_metricas_vendedor(
    vendedor_id: int,
    data_inicio: Optional[date] = Query(None, description="Data de início para filtro"),
    data_fim: Optional[date] = Query(None, description="Data de fim para filtro"),
    db: Session = Depends(get_db)
):
    """
    Obtém métricas de vendas de um vendedor específico.
    """
    try:
        # Verifica se o vendedor existe
        vendedor = db.query(Vendedor).filter(Vendedor.id == vendedor_id).first()
        if not vendedor:
            raise HTTPException(status_code=404, detail="Vendedor não encontrado")
        
        # Query base para vendas do vendedor
        query = db.query(Venda).filter(Venda.vendedor_id == vendedor_id)
        
        # Aplica filtros de data se fornecidos
        if data_inicio:
            query = query.filter(Venda.data >= data_inicio)
        if data_fim:
            query = query.filter(Venda.data <= data_fim)
        
        vendas = query.all()
        
        # Calcula métricas
        total_vendas = len(vendas)
        valor_total = sum(float(v.valor_mensal) for v in vendas)
        valor_bonificacoes = sum(v.valor_bonificacao for v in vendas)
        media_valor = valor_total / total_vendas if total_vendas > 0 else 0
        
        # Produtos mais vendidos
        produtos = {}
        for venda in vendas:
            if venda.produto not in produtos:
                produtos[venda.produto] = 0
            produtos[venda.produto] += 1
        
        top_produtos = sorted(produtos.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return VendedorMetricsResponse(
            vendedor_id=vendedor_id,
            nome_vendedor=vendedor.nome,
            periodo={
                "data_inicio": data_inicio.isoformat() if data_inicio else None,
                "data_fim": data_fim.isoformat() if data_fim else None
            },
            total_vendas=total_vendas,
            valor_total=round(valor_total, 2),
            valor_bonificacoes=round(valor_bonificacoes, 2),
            media_valor=round(media_valor, 2),
            top_produtos=top_produtos
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter métricas: {str(e)}")