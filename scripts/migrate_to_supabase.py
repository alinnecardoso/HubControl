#!/usr/bin/env python3
"""
Script para migrar o schema do banco para o Supabase
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações do Supabase
SUPABASE_URL = "https://auhkbtxjoqvahiajopop.supabase.co"
DATABASE_URL = "postgresql://postgres:himmelcorp@123@db.auhkbtxjoqvahiajopop.supabase.co:5432/postgres"

def read_schema_file():
    """Lê o arquivo de schema SQL"""
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
    
    if not os.path.exists(schema_path):
        logger.error(f"Arquivo de schema não encontrado: {schema_path}")
        return None
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Erro ao ler arquivo de schema: {e}")
        return None

def execute_schema(connection, schema_sql):
    """Executa o schema SQL no banco"""
    try:
        cursor = connection.cursor()
        
        # Dividir o SQL em comandos individuais
        commands = schema_sql.split(';')
        
        for command in commands:
            command = command.strip()
            if command and not command.startswith('--'):
                try:
                    cursor.execute(command)
                    logger.info(f"Comando executado com sucesso: {command[:50]}...")
                except Exception as e:
                    logger.warning(f"Erro ao executar comando: {command[:50]}... - {e}")
                    # Continuar com outros comandos
        
        connection.commit()
        logger.info("Schema executado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao executar schema: {e}")
        connection.rollback()
        return False

def test_connection():
    """Testa a conexão com o Supabase"""
    try:
        connection = psycopg2.connect(DATABASE_URL)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        logger.info(f"Conexão bem-sucedida! PostgreSQL: {version[0]}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"Erro ao conectar com Supabase: {e}")
        return False

def create_database():
    """Cria o banco de dados se não existir"""
    try:
        # Conectar ao postgres padrão
        connection = psycopg2.connect(DATABASE_URL)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = connection.cursor()
        
        # Verificar se o banco existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'postgres'")
        exists = cursor.fetchone()
        
        if not exists:
            logger.info("Criando banco de dados 'postgres'...")
            cursor.execute("CREATE DATABASE postgres")
            logger.info("Banco de dados criado com sucesso!")
        else:
            logger.info("Banco de dados 'postgres' já existe")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"Erro ao criar banco de dados: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🚀 Iniciando migração para Supabase...")
    
    # Testar conexão
    if not test_connection():
        logger.error("❌ Falha na conexão com Supabase")
        sys.exit(1)
    
    # Ler schema
    schema_sql = read_schema_file()
    if not schema_sql:
        logger.error("❌ Falha ao ler arquivo de schema")
        sys.exit(1)
    
    # Executar schema
    try:
        connection = psycopg2.connect(DATABASE_URL)
        
        if execute_schema(connection, schema_sql):
            logger.info("✅ Migração concluída com sucesso!")
        else:
            logger.error("❌ Falha na migração")
            sys.exit(1)
            
        connection.close()
        
    except Exception as e:
        logger.error(f"❌ Erro durante migração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 