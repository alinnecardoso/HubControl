#!/bin/bash

# HubControl - Script de Inicialização
# Este script configura e inicia o sistema HubControl com Supabase

set -e  # Para em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ⚠️  $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ❌ $1"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ℹ️  $1"
}

# Banner
echo -e "${BLUE}"
cat << "EOF"
 _    _       _     _       _____                      _ _ 
| |  | |     | |   | |     /  ___|                    | | |
| |  | |_ __ | |__ | |_   | |     _ __   ___  _ __   | | |
| |/\| | '_ \| '_ \| __|  | |    | '_ \ / _ \| '_ \  | | |
\  /\  / |_) | | | | |_   | |___| | | | (_) | | | | | | |
 \/  \/| .__/|_| |_|\__|  \____/|_| |_|\___/|_| |_| |_|
       | |                                                 
       |_|                                                 
EOF
echo -e "${NC}"

log "🚀 Iniciando HubControl com Supabase..."

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    error "Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se o Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Verificar se o Docker está rodando
if ! docker info &> /dev/null; then
    error "Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

log "✅ Docker e Docker Compose estão funcionando"

# Verificar portas disponíveis
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        error "Porta $port já está em uso. Por favor, libere a porta ou altere a configuração."
        exit 1
    fi
}

check_port 3000
check_port 8000
check_port 6379

log "✅ Portas disponíveis verificadas"

# Criar diretórios necessários
log "📁 Criando diretórios necessários..."
mkdir -p logs
mkdir -p uploads
mkdir -p models
mkdir -p backend/logs
mkdir -p backend/uploads
mkdir -p backend/models

# Criar arquivo .env se não existir
if [ ! -f "backend/.env" ]; then
    log "📝 Criando arquivo .env..."
    cp backend/env.example backend/.env
    
    # Atualizar configurações do Supabase
    sed -i 's|SUPABASE_URL=.*|SUPABASE_URL=https://auhkbtxjoqvahiajopop.supabase.co|g' backend/.env
    sed -i 's|SUPABASE_ANON_KEY=.*|SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1aGtidHhqb3F2YWhpYWpvcG9wIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYyNTk5NTYsImV4cCI6MjA3MTgzNTk1Nn0.TmzyeS7_NEiR3tQbFapsqGUi98Zb44YmuKFwlvCYX2I|g' backend/.env
    sed -i 's|DATABASE_URL=.*|DATABASE_URL=postgresql://postgres:himmelcorp@123@db.auhkbtxjoqvahiajopop.supabase.co:5432/postgres|g' backend/.env
    
    log "✅ Arquivo .env criado com configurações do Supabase"
else
    log "ℹ️  Arquivo .env já existe"
fi

# Parar containers existentes se houver
log "🛑 Parando containers existentes..."
docker-compose down --remove-orphans 2>/dev/null || true

# Limpar imagens antigas (opcional)
read -p "🧹 Deseja limpar imagens Docker antigas? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "🧹 Limpando imagens antigas..."
    docker system prune -f
fi

# Construir e iniciar serviços
log "🔨 Construindo e iniciando serviços..."
docker-compose up --build -d

# Aguardar serviços ficarem prontos
log "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Verificar saúde dos serviços
log "🏥 Verificando saúde dos serviços..."

# Verificar Redis
if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
    log "✅ Redis está funcionando"
else
    error "❌ Redis não está respondendo"
    exit 1
fi

# Verificar Backend
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    log "✅ Backend está funcionando"
else
    error "❌ Backend não está respondendo"
    exit 1
fi

# Verificar Frontend
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    log "✅ Frontend está funcionando"
else
    error "❌ Frontend não está respondendo"
    exit 1
fi

# Migrar schema para Supabase
log "🗄️  Migrando schema para Supabase..."
if [ -f "scripts/migrate_to_supabase.py" ]; then
    # Instalar dependências necessárias
    pip3 install psycopg2-binary >/dev/null 2>&1 || {
        warn "pip3 não disponível, tentando com pip..."
        pip install psycopg2-binary >/dev/null 2>&1 || {
            error "Não foi possível instalar psycopg2-binary. Execute manualmente: pip install psycopg2-binary"
        }
    }
    
    # Executar migração
    python3 scripts/migrate_to_supabase.py
    if [ $? -eq 0 ]; then
        log "✅ Schema migrado com sucesso para o Supabase"
    else
        warn "⚠️  Erro na migração do schema. Verifique os logs acima."
    fi
else
    warn "⚠️  Script de migração não encontrado"
fi

# Mostrar informações de acesso
echo
echo -e "${GREEN}🎉 HubControl iniciado com sucesso!${NC}"
echo
echo -e "${BLUE}📱 Acesse o sistema:${NC}"
echo -e "   Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "   Backend API: ${GREEN}http://localhost:8000${NC}"
echo -e "   Documentação API: ${GREEN}http://localhost:8000/docs${NC}"
echo
echo -e "${BLUE}🗄️  Banco de dados:${NC}"
echo -e "   Supabase: ${GREEN}https://auhkbtxjoqvahiajopop.supabase.co${NC}"
echo -e "   Status: ${GREEN}Conectado e funcionando${NC}"
echo
echo -e "${BLUE}🔧 Comandos úteis:${NC}"
echo -e "   Ver logs: ${YELLOW}docker-compose logs -f${NC}"
echo -e "   Parar: ${YELLOW}docker-compose down${NC}"
echo -e "   Reiniciar: ${YELLOW}docker-compose restart${NC}"
echo -e "   Status: ${YELLOW}docker-compose ps${NC}"
echo
echo -e "${BLUE}📊 Monitoramento:${NC}"
echo -e "   Redis: ${GREEN}http://localhost:6379${NC}"
echo -e "   Health Check: ${GREEN}http://localhost:8000/health${NC}"
echo

# Verificar se há atualizações disponíveis
log "🔍 Verificando atualizações..."
docker-compose pull --quiet

# Mostrar status final
log "📊 Status dos serviços:"
docker-compose ps

log "✨ Setup completo! O HubControl está rodando com Supabase!"
log "🌐 Acesse http://localhost:3000 para começar a usar o sistema" 