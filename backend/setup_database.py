"""
Script para configurar o banco de dados Supabase
Execute este script para criar as tabelas necessárias
"""
import os
from supabase import create_client, Client
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações do Supabase
SUPABASE_URL = "https://auhkbtxjoqvahiajopop.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1aGtidHhqb3F2YWhpYWpvcG9wIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNTA2ODI0MCwiZXhwIjoyMDUwNjQ0MjQwfQ.l8vgbAhQLHSKBcHOXFYVbkHqH1-Aa6HQ4YHKHlSFm0U"

def setup_database():
    """Configura o banco de dados criando as tabelas necessárias"""
    try:
        # Criar cliente Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Ler o arquivo SQL
        with open('database_schema.sql', 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        logger.info("Executando script de criação do banco de dados...")
        
        # Dividir em comandos individuais
        sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        for i, command in enumerate(sql_commands):
            if command.strip():
                try:
                    logger.info(f"Executando comando {i+1}/{len(sql_commands)}")
                    result = supabase.rpc('exec_sql', {'sql': command}).execute()
                    logger.info(f"Comando {i+1} executado com sucesso")
                except Exception as e:
                    logger.error(f"Erro no comando {i+1}: {e}")
                    # Continue com os próximos comandos mesmo se um falhar
                    continue
        
        logger.info("Setup do banco de dados concluído!")
        
        # Verificar se a tabela foi criada
        try:
            result = supabase.table('user_profiles').select('*').limit(1).execute()
            logger.info("Tabela user_profiles criada com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao verificar tabela: {e}")
            
    except Exception as e:
        logger.error(f"Erro geral no setup: {e}")

if __name__ == "__main__":
    setup_database()