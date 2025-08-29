"""
Script para popular o banco com dados de exemplo baseados na planilha real
"""
import asyncio
from datetime import datetime, date
from database.connection import SessionLocal, engine
from models.base import Base
from models.cliente import Cliente
from models.vendedor import Vendedor
from models.venda import Venda

# Dados de exemplo baseados na planilha real
SAMPLE_DATA = [
    {
        "data": "2025-06-01",
        "loja": "BMP SHOP",
        "cliente_nome": "DENNIS",
        "telefone": "11 97366-9964",
        "produto": "ASSESSORIA MASTER",
        "valor_mensal": 2600.00,
        "percentual_variavel": None,
        "vendedor_nome": "Isaac",
        "contrato_meses": 12,
        "forma_pagamento": "BOLETO",
        "canal_venda": "Tráfego",
        "descricao": "Tráfego",
        "info_adicional": ""
    },
    {
        "data": "2025-06-01",
        "loja": "GKD FITNESS",
        "cliente_nome": "DANILLO",
        "telefone": "21 98560-2131",
        "produto": "ASSESSORIA MASTER",
        "valor_mensal": 3000.00,
        "percentual_variavel": None,
        "vendedor_nome": "Isaac",
        "contrato_meses": 12,
        "forma_pagamento": "BOLETO",
        "canal_venda": "Parceiro In",
        "descricao": "Indicação Clayton Friburgo",
        "info_adicional": ""
    },
    {
        "data": "2025-06-03",
        "loja": "SM ARTESANATOS",
        "cliente_nome": "ERIVELTON",
        "telefone": "35 99107-2468",
        "produto": "MENTORIA EDUCATIVA",
        "valor_mensal": 1750.00,
        "percentual_variavel": None,
        "vendedor_nome": "Isaac",
        "contrato_meses": 4,
        "forma_pagamento": "CRÉDITO RECORRENTE",
        "canal_venda": "OUTBOUND SALES",
        "descricao": "Publi 5.0",
        "info_adicional": ""
    },
    {
        "data": "2025-06-06",
        "loja": "KEPEL SUPRIMENTOS",
        "cliente_nome": "VINICIUS",
        "telefone": "11 97201-2639",
        "produto": "ASSESSORIA PERFORMANCE",
        "valor_mensal": 3000.00,
        "percentual_variavel": None,
        "vendedor_nome": "Keysi",
        "contrato_meses": 8,
        "forma_pagamento": "CRÉDITO RECORRENTE",
        "canal_venda": "Parceiro Out",
        "descricao": "Ecommerce Puro",
        "info_adicional": ""
    },
    {
        "data": "2025-06-09",
        "loja": "KIERY",
        "cliente_nome": "ERIK",
        "telefone": "31 7561-0245",
        "produto": "ASSESSORIA MASTER",
        "valor_mensal": 2600.00,
        "percentual_variavel": None,
        "vendedor_nome": "Isaac",
        "contrato_meses": 16,
        "forma_pagamento": "BOLETO",
        "canal_venda": "Parceiro Out",
        "descricao": "Igor de Savoia",
        "info_adicional": ""
    },
    {
        "data": "2025-06-09",
        "loja": "IMPERIAL LED",
        "cliente_nome": "RODRIGO",
        "telefone": "44 9135-1547",
        "produto": "ASSESSORIA MASTER",
        "valor_mensal": 2600.00,
        "percentual_variavel": None,
        "vendedor_nome": "Isaac",
        "contrato_meses": 12,
        "forma_pagamento": "BOLETO",
        "canal_venda": "Parceiro Out",
        "descricao": "Ecommerce Puro",
        "info_adicional": ""
    },
    {
        "data": "2025-06-17",
        "loja": "USEE BRASIL",
        "cliente_nome": "Gabriel Morais",
        "telefone": "16 99991-7946",
        "produto": "ASSESSORIA FULL FUNNEL",
        "valor_mensal": 5000.00,
        "percentual_variavel": None,
        "vendedor_nome": "Lucas",
        "contrato_meses": 12,
        "forma_pagamento": "BOLETO",
        "canal_venda": "Orgânico",
        "descricao": "Ecommerce Puro",
        "info_adicional": "Sem fidelidade"
    },
    {
        "data": "2025-06-20",
        "loja": "NDPNEUMATICA",
        "cliente_nome": "Felipe",
        "telefone": "19 99759-3332",
        "produto": "ASSESSORIA START",
        "valor_mensal": 3800.00,
        "percentual_variavel": None,
        "vendedor_nome": "Isaac",
        "contrato_meses": 4,
        "forma_pagamento": "PIX",
        "canal_venda": "Orgânico",
        "descricao": "Direto Wpp",
        "info_adicional": ""
    },
    {
        "data": "2025-06-26",
        "loja": "BLISS",
        "cliente_nome": "Matheus Ferreira",
        "telefone": "11 95118-0445",
        "produto": "ASSESSORIA MASTER + OTIMIZAÇÃO",
        "valor_mensal": 2400.00,
        "percentual_variavel": 2.0,
        "vendedor_nome": "Isaac",
        "contrato_meses": 12,
        "forma_pagamento": "BOLETO",
        "canal_venda": "Orgânico",
        "descricao": "Igor de Savoia",
        "info_adicional": ""
    },
    {
        "data": "2025-06-27",
        "loja": "RENAF CAR",
        "cliente_nome": "KARINA",
        "telefone": "11 98385-0085",
        "produto": "ASSESSORIA PERFORMANCE",
        "valor_mensal": 4800.00,
        "percentual_variavel": None,
        "vendedor_nome": "Isaac",
        "contrato_meses": 6,
        "forma_pagamento": "BOLETO",
        "canal_venda": "Parceiro Out",
        "descricao": "Ecommerce Puro",
        "info_adicional": ""
    },
    {
        "data": "2025-06-30",
        "loja": "RUBBER FIT",
        "cliente_nome": "GUSTAVO",
        "telefone": "11 99910-3405",
        "produto": "ASSESSORIA MASTER",
        "valor_mensal": 3200.00,
        "percentual_variavel": None,
        "vendedor_nome": "Isaac",
        "contrato_meses": 12,
        "forma_pagamento": "CRÉDITO RECORRENTE",
        "canal_venda": "Parceiro In",
        "descricao": "Indicação Caio FACT",
        "info_adicional": ""
    }
]

def create_tables():
    """Cria as tabelas no banco"""
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

def populate_database():
    """Popula o banco com dados de exemplo"""
    db = SessionLocal()
    
    try:
        # Limpa dados existentes
        db.query(Venda).delete()
        db.query(Cliente).delete()
        db.query(Vendedor).delete()
        
        # Cria vendedores únicos
        vendedores_nomes = set([item["vendedor_nome"] for item in SAMPLE_DATA])
        vendedores_map = {}
        
        for i, nome in enumerate(vendedores_nomes, 1):
            vendedor = Vendedor(
                id=i,
                nome=nome,
                email=f"{nome.lower().replace(' ', '.')}@hubcontrol.com"
            )
            db.add(vendedor)
            vendedores_map[nome] = i
        
        # Cria clientes únicos
        clientes_nomes = set([item["cliente_nome"] for item in SAMPLE_DATA])
        clientes_map = {}
        
        for i, nome in enumerate(clientes_nomes, 1):
            # Encontra telefone do cliente
            telefone = next((item["telefone"] for item in SAMPLE_DATA if item["cliente_nome"] == nome), None)
            
            cliente = Cliente(
                id=i,
                nome_principal=nome,
                telefone=telefone,
                status_cliente="ativo"
            )
            db.add(cliente)
            clientes_map[nome] = i
        
        # Commit vendedores e clientes primeiro
        db.commit()
        
        # Cria vendas
        for i, item in enumerate(SAMPLE_DATA, 1):
            venda = Venda(
                id=i,
                data=datetime.strptime(item["data"], "%Y-%m-%d").date(),
                loja=item["loja"],
                cliente_id=clientes_map[item["cliente_nome"]],
                vendedor_id=vendedores_map[item["vendedor_nome"]],
                produto=item["produto"],
                valor_mensal=item["valor_mensal"],
                contrato_meses=item["contrato_meses"],
                forma_pagamento=item["forma_pagamento"],
                canal_venda=item["canal_venda"],
                telefone_cliente=item["telefone"],
                percentual_variavel=item["percentual_variavel"],
                descricao=item["descricao"],
                info_adicional=item["info_adicional"]
            )
            db.add(venda)
        
        db.commit()
        print("Dados inseridos com sucesso!")
        print(f"   - {len(vendedores_nomes)} vendedores")
        print(f"   - {len(clientes_nomes)} clientes") 
        print(f"   - {len(SAMPLE_DATA)} vendas")
        
        # Mostra estatísticas
        total_vendas = db.query(Venda).count()
        valor_total = sum([float(venda.valor_mensal) for venda in db.query(Venda).all()])
        
        print(f"\nEstatisticas:")
        print(f"   - Total de vendas: {total_vendas}")
        print(f"   - Valor total: R$ {valor_total:,.2f}")
        print(f"   - Ticket medio: R$ {valor_total/total_vendas:,.2f}")
        
    except Exception as e:
        print(f"Erro ao popular banco: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando populacao do banco de dados...")
    create_tables()
    populate_database()
    print("Processo concluido!")