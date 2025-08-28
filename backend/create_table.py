"""
Script simples para criar a tabela user_profiles via API
"""
import requests
import json

# Configurações do Supabase
SUPABASE_URL = "https://auhkbtxjoqvahiajopop.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1aGtidHhqb3F2YWhpYWpvcG9wIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNTA2ODI0MCwiZXhwIjoyMDUwNjQ0MjQwfQ.l8vgbAhQLHSKBcHOXFYVbkHqH1-Aa6HQ4YHKHlSFm0U"

def create_table_direct():
    """Cria a tabela user_profiles diretamente via SQL"""
    
    # SQL para criar a tabela
    sql_command = """
    CREATE TABLE IF NOT EXISTS public.user_profiles (
        id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
        email VARCHAR(255) UNIQUE NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL DEFAULT 'cs_cx',
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
        PRIMARY KEY (id),
        CONSTRAINT valid_role CHECK (role IN ('admin', 'diretoria', 'cs_cx', 'financeiro', 'vendas', 'dataops'))
    );
    """
    
    headers = {
        'apikey': SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Tentar executar via RPC
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec"
    data = {
        'sql': sql_command
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("Tabela criada com sucesso!")
        else:
            print("Erro ao criar tabela")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")

def test_table_creation():
    """Testa se a tabela foi criada verificando sua existência"""
    headers = {
        'apikey': SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Tentar fazer um SELECT simples
    url = f"{SUPABASE_URL}/rest/v1/user_profiles"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Test Status Code: {response.status_code}")
        print(f"Test Response: {response.text}")
        
        if response.status_code == 200:
            print("Tabela user_profiles existe e está acessível!")
            return True
        else:
            print("Tabela ainda não existe ou não está acessível")
            return False
            
    except Exception as e:
        print(f"Erro no teste: {e}")
        return False

if __name__ == "__main__":
    print("Verificando se a tabela já existe...")
    if not test_table_creation():
        print("\nCriando tabela user_profiles...")
        create_table_direct()
        
        print("\nVerificando novamente...")
        test_table_creation()
    else:
        print("Tabela já existe!")