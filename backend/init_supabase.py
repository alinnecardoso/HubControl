"""
Script para inicializar o Supabase e popular com dados de exemplo
"""
import asyncio
import sys
from datetime import datetime, date
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Adicionar o diretório atual ao path
sys.path.append('.')

from config import settings
from models.base import Base
from models.cliente import Cliente
from models.vendedor import Vendedor  
from models.venda import Venda

print("Conectando ao Supabase...")
print(f"URL: {settings.SUPABASE_URL}")
print(f"Database: {settings.DATABASE_URL}")

# Criar engine para Supabase
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_connection():
    """Testa a conexão com o Supabase"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"Conectado com sucesso! PostgreSQL Version: {version}")
            return True
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return False

def create_tables():
    """Cria as tabelas no Supabase"""
    try:
        print("Criando tabelas...")
        Base.metadata.create_all(bind=engine)
        print("Tabelas criadas com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        return False

def populate_sample_data():
    """Popula o banco com dados de exemplo baseados na planilha"""
    db = SessionLocal()
    
    try:
        print("Verificando dados existentes...")
        
        # Verifica se já existem dados
        existing_vendas = db.query(Venda).count()
        if existing_vendas > 0:
            print(f"Já existem {existing_vendas} vendas. Limpando dados antigos...")
            db.query(Venda).delete()
            db.query(Cliente).delete()
            db.query(Vendedor).delete()
            db.commit()
        
        print("Criando vendedores...")
        # Criar vendedores
        vendedores = [
            Vendedor(id=1, nome="Isaac", email="isaac@hubcontrol.com"),
            Vendedor(id=2, nome="Lucas", email="lucas@hubcontrol.com"),
            Vendedor(id=3, nome="Keysi", email="keysi@hubcontrol.com"),
            Vendedor(id=4, nome="Rogério", email="rogerio@hubcontrol.com")
        ]
        
        for vendedor in vendedores:
            db.add(vendedor)
        
        print("Criando clientes...")
        # Criar clientes
        clientes = [
            Cliente(id=1, nome_principal="DENNIS", telefone="11 97366-9964", status_cliente="ativo"),
            Cliente(id=2, nome_principal="DANILLO", telefone="21 98560-2131", status_cliente="ativo"),
            Cliente(id=3, nome_principal="Gabriel Morais", telefone="16 99991-7946", status_cliente="ativo"),
            Cliente(id=4, nome_principal="Matheus Ferreira", telefone="11 95118-0445", status_cliente="ativo"),
            Cliente(id=5, nome_principal="GUSTAVO", telefone="11 99910-3405", status_cliente="ativo"),
            Cliente(id=6, nome_principal="ERIVELTON", telefone="35 99107-2468", status_cliente="ativo"),
            Cliente(id=7, nome_principal="VINICIUS", telefone="11 97201-2639", status_cliente="ativo"),
            Cliente(id=8, nome_principal="ERIK", telefone="31 7561-0245", status_cliente="ativo"),
            Cliente(id=9, nome_principal="RODRIGO", telefone="44 9135-1547", status_cliente="ativo"),
            Cliente(id=10, nome_principal="Felipe", telefone="19 99759-3332", status_cliente="ativo")
        ]
        
        for cliente in clientes:
            db.add(cliente)
        
        print("Criando vendas...")
        # Criar vendas baseadas na planilha
        vendas = [
            Venda(
                id=1, data=date(2025, 6, 1), loja="BMP SHOP", cliente_id=1, vendedor_id=1,
                produto="ASSESSORIA MASTER", valor_mensal=2600.00, contrato_meses=12,
                forma_pagamento="BOLETO", canal_venda="Tráfego", telefone_cliente="11 97366-9964",
                descricao="Tráfego", info_adicional=""
            ),
            Venda(
                id=2, data=date(2025, 6, 1), loja="GKD FITNESS", cliente_id=2, vendedor_id=1,
                produto="ASSESSORIA MASTER", valor_mensal=3000.00, contrato_meses=12,
                forma_pagamento="BOLETO", canal_venda="Parceiro In", telefone_cliente="21 98560-2131",
                descricao="Indicação Clayton Friburgo", info_adicional=""
            ),
            Venda(
                id=3, data=date(2025, 6, 3), loja="SM ARTESANATOS", cliente_id=6, vendedor_id=1,
                produto="MENTORIA EDUCATIVA", valor_mensal=1750.00, contrato_meses=4,
                forma_pagamento="CRÉDITO RECORRENTE", canal_venda="OUTBOUND SALES", telefone_cliente="35 99107-2468",
                descricao="Publi 5.0", info_adicional=""
            ),
            Venda(
                id=4, data=date(2025, 6, 6), loja="KEPEL SUPRIMENTOS", cliente_id=7, vendedor_id=3,
                produto="ASSESSORIA PERFORMANCE", valor_mensal=3000.00, contrato_meses=8,
                forma_pagamento="CRÉDITO RECORRENTE", canal_venda="Parceiro Out", telefone_cliente="11 97201-2639",
                descricao="Ecommerce Puro", info_adicional=""
            ),
            Venda(
                id=5, data=date(2025, 6, 9), loja="KIERY", cliente_id=8, vendedor_id=1,
                produto="ASSESSORIA MASTER", valor_mensal=2600.00, contrato_meses=16,
                forma_pagamento="BOLETO", canal_venda="Parceiro Out", telefone_cliente="31 7561-0245",
                descricao="Igor de Savoia", info_adicional=""
            ),
            Venda(
                id=6, data=date(2025, 6, 9), loja="IMPERIAL LED", cliente_id=9, vendedor_id=1,
                produto="ASSESSORIA MASTER", valor_mensal=2600.00, contrato_meses=12,
                forma_pagamento="BOLETO", canal_venda="Parceiro Out", telefone_cliente="44 9135-1547",
                descricao="Ecommerce Puro", info_adicional=""
            ),
            Venda(
                id=7, data=date(2025, 6, 17), loja="USEE BRASIL", cliente_id=3, vendedor_id=2,
                produto="ASSESSORIA FULL FUNNEL", valor_mensal=5000.00, contrato_meses=12,
                forma_pagamento="BOLETO", canal_venda="Orgânico", telefone_cliente="16 99991-7946",
                descricao="Ecommerce Puro", info_adicional="Sem fidelidade"
            ),
            Venda(
                id=8, data=date(2025, 6, 20), loja="NDPNEUMATICA", cliente_id=10, vendedor_id=1,
                produto="ASSESSORIA START", valor_mensal=3800.00, contrato_meses=4,
                forma_pagamento="PIX", canal_venda="Orgânico", telefone_cliente="19 99759-3332",
                descricao="Direto Wpp", info_adicional=""
            ),
            Venda(
                id=9, data=date(2025, 6, 26), loja="BLISS", cliente_id=4, vendedor_id=1,
                produto="ASSESSORIA MASTER + OTIMIZAÇÃO", valor_mensal=2400.00, contrato_meses=12,
                forma_pagamento="BOLETO", canal_venda="Orgânico", telefone_cliente="11 95118-0445",
                percentual_variavel=2.0, descricao="Igor de Savoia", info_adicional=""
            ),
            Venda(
                id=10, data=date(2025, 6, 30), loja="RUBBER FIT", cliente_id=5, vendedor_id=1,
                produto="ASSESSORIA MASTER", valor_mensal=3200.00, contrato_meses=12,
                forma_pagamento="CRÉDITO RECORRENTE", canal_venda="Parceiro In", telefone_cliente="11 99910-3405",
                descricao="Indicação Caio FACT", info_adicional=""
            )
        ]
        
        for venda in vendas:
            db.add(venda)
        
        # Commit todas as mudanças
        db.commit()
        
        # Verificar dados inseridos
        total_vendedores = db.query(Vendedor).count()
        total_clientes = db.query(Cliente).count()
        total_vendas = db.query(Venda).count()
        from sqlalchemy import func
        valor_total = db.query(func.sum(Venda.valor_mensal)).scalar() or 0
        
        print(f"\nDados inseridos com sucesso!")
        print(f"- Vendedores: {total_vendedores}")
        print(f"- Clientes: {total_clientes}")
        print(f"- Vendas: {total_vendas}")
        print(f"- Valor total: R$ {valor_total:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"Erro ao popular dados: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Função principal"""
    print("Iniciando configuração do Supabase...")
    
    # Testa conexão
    if not test_connection():
        print("Falha na conexão com o Supabase!")
        return False
    
    # Cria tabelas
    if not create_tables():
        print("Falha ao criar tabelas!")
        return False
    
    # Popula dados
    if not populate_sample_data():
        print("Falha ao popular dados!")
        return False
    
    print("\nSupabase configurado com sucesso!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)