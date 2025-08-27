#!/bin/bash

# Script de configuração inicial do HubControl
echo "🚀 Configurando o HubControl..."

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale o Python 3.9+"
    exit 1
fi

# Verifica se o pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Por favor, instale o pip3"
    exit 1
fi

# Verifica se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker não encontrado. O projeto pode ser executado sem Docker, mas algumas funcionalidades podem não funcionar."
fi

# Verifica se o Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  Docker Compose não encontrado. O projeto pode ser executado sem Docker Compose."
fi

echo "✅ Dependências básicas verificadas"

# Cria diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p backend/logs
mkdir -p backend/uploads
mkdir -p frontend/build

# Configura o ambiente Python
echo "🐍 Configurando ambiente Python..."
cd backend

# Cria ambiente virtual
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativa o ambiente virtual
source venv/bin/activate

# Instala dependências
echo "📦 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend configurado"

# Volta para o diretório raiz
cd ..

# Configura o ambiente Node.js (se existir)
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    echo "📱 Configurando frontend..."
    cd frontend
    
    # Verifica se o Node.js está instalado
    if command -v node &> /dev/null; then
        echo "📦 Instalando dependências Node.js..."
        npm install
        echo "✅ Frontend configurado"
    else
        echo "⚠️  Node.js não encontrado. O frontend não será configurado."
    fi
    
    cd ..
fi

# Copia arquivo de ambiente
if [ ! -f "backend/.env" ]; then
    echo "🔧 Copiando arquivo de ambiente..."
    cp backend/env.example backend/.env
    echo "⚠️  Arquivo .env criado. Ajuste as configurações conforme necessário."
fi

# Inicia os serviços com Docker (se disponível)
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Iniciando serviços com Docker..."
    docker-compose up -d postgres redis
    
    echo "⏳ Aguardando serviços iniciarem..."
    sleep 10
    
    echo "✅ Serviços Docker iniciados"
    echo "📊 PostgreSQL: localhost:5432"
    echo "🔴 Redis: localhost:6379"
else
    echo "⚠️  Docker não disponível. Configure manualmente:"
    echo "   - PostgreSQL na porta 5432"
    echo "   - Redis na porta 6379"
fi

echo ""
echo "🎉 HubControl configurado com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Ajuste as configurações em backend/.env"
echo "2. Execute o banco de dados:"
echo "   - Com Docker: docker-compose up -d postgres"
echo "   - Manualmente: Configure PostgreSQL localmente"
echo "3. Execute o backend:"
echo "   cd backend && source venv/bin/activate && python main.py"
echo "4. Acesse a documentação: http://localhost:8000/docs"
echo ""
echo "🔗 Links úteis:"
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo "   - Health: http://localhost:8000/health" 