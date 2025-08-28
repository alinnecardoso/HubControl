# 🚀 HubControl - Guia de Execução

## Pré-requisitos

### Sistemas Obrigatórios
- **Python 3.8+** - [Download aqui](https://www.python.org/downloads/)
- **Node.js 16+** - [Download aqui](https://nodejs.org/)
- **Git** - [Download aqui](https://git-scm.com/)

### Sistemas Opcionais (Recomendados)
- **Redis** - Para cache ML otimizado
- **PostgreSQL** - Para produção (SQLite funciona para desenvolvimento)

## 🔧 Instalação e Configuração

### 1. Setup Automático (Recomendado)
```bash
# Execute o script de configuração automática
setup_environment.bat
```

### 2. Setup Manual

#### Backend (Python/FastAPI)
```bash
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### Frontend (React/TypeScript)
```bash
cd frontend
npm install
```

### 3. Configuração de Ambiente
```bash
# Copie o arquivo de exemplo
copy .env.example .env

# Edite as variáveis conforme necessário
notepad .env
```

## 🏃‍♂️ Executando o Sistema

### Método 1: Scripts Automáticos (Recomendado)

#### Backend
```bash
# Inicia o servidor backend na porta 8000
start_backend.bat
```

#### Frontend
```bash
# Inicia o servidor frontend na porta 3000
start_frontend.bat
```

#### Testes ML
```bash
# Executa testes do sistema de Machine Learning
run_tests.bat
```

### Método 2: Comandos Manuais

#### Backend
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm start
```

## 🌐 Acessando o Sistema

### URLs Principais
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação API**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

### Funcionalidades ML Disponíveis
- **Análise de Churn**: Predição de risco de cancelamento
- **Dashboard Interativo**: Gráficos e métricas em tempo real
- **Cache Inteligente**: Sistema de cache Redis com fallback
- **Explicabilidade**: SHAP para interpretação de modelos
- **Validação Temporal**: Cross-validation específica para séries temporais

## 🧪 Testando o Sistema

### Testes Automatizados
```bash
# Executa todos os testes ML
run_tests.bat

# Ou manualmente
cd backend
python test_ml_system.py
```

### Testes Manuais
1. Acesse http://localhost:3000
2. Navegue para a aba "Análise de Churn"
3. Teste as funcionalidades de predição
4. Verifique os gráficos e métricas

## 🔍 Resolução de Problemas

### Problema: Python não encontrado
```bash
# Instale Python 3.8+ do site oficial
# Certifique-se de marcar "Add Python to PATH"
```

### Problema: Node.js não encontrado
```bash
# Instale Node.js 16+ do site oficial
# Reinicie o terminal após a instalação
```

### Problema: Erro de dependências Python
```bash
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --force-reinstall
```

### Problema: Erro de dependências Node.js
```bash
cd frontend
npm clean-install
# ou
rm -rf node_modules package-lock.json
npm install
```

### Problema: Redis não disponível
O sistema funciona sem Redis usando cache em memória. Para instalar Redis:
- **Windows**: Use WSL2 ou Docker
- **macOS**: `brew install redis`
- **Linux**: `sudo apt-get install redis-server`

## 📊 Monitoramento

### Logs do Sistema
- **Backend**: Console do terminal
- **Frontend**: Console do navegador
- **ML**: Logs detalhados no terminal backend

### Métricas ML
- Cache hit/miss rates
- Tempos de predição
- Acurácia dos modelos
- Estatísticas de uso

## 🔄 Desenvolvimento

### Estrutura do Projeto
```
HubControl/
├── backend/          # FastAPI + ML
├── frontend/         # React + TypeScript  
├── ml/              # Modelos de Machine Learning
├── *.bat            # Scripts de execução Windows
└── README_EXECUCAO.md # Este arquivo
```

### Comandos Úteis
```bash
# Reinstalar dependências
setup_environment.bat

# Executar apenas backend
start_backend.bat

# Executar apenas frontend  
start_frontend.bat

# Executar testes ML
run_tests.bat
```

## 🚨 Notas Importantes

1. **Primeira Execução**: Pode demorar devido ao download de dependências ML
2. **Cache ML**: Redis opcional, mas recomendado para performance
3. **Modelos**: Criados automaticamente na primeira predição
4. **Dados**: SQLite por padrão, configurável para PostgreSQL/MySQL
5. **CORS**: Configurado para desenvolvimento local

---

✨ **Sistema pronto para uso!** Execute `setup_environment.bat` e depois `start_backend.bat` + `start_frontend.bat`