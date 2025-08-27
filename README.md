# 🔮 HubControl - Sistema de Gestão Inteligente

Sistema completo de gestão de clientes, vendas e Customer Success com **Machine Learning** para previsão de churn.

## ✨ **Funcionalidades Principais**

### 🧠 **Machine Learning - Previsão de Churn**
- **Múltiplos algoritmos**: Random Forest, XGBoost, LightGBM, Neural Networks
- **Feature Engineering avançado**: 30+ features baseadas em dados do sistema
- **Previsões em tempo real**: API para análise individual e em lote
- **Insights automáticos**: Recomendações baseadas em risco
- **Dashboard interativo**: Visualizações e métricas de ML

### 📊 **Módulo Customer Success (CS)**
- **Health Score**: Avaliação de saúde do cliente (0-100)
- **CSAT**: Medição de satisfação e feedback qualitativo
- **Pipeline de Renovação**: Gestão de contratos e renovação
- **Alertas Inteligentes**: Notificações baseadas em ML
- **Métricas Avançadas**: LTV, churn, NRR, GRR

### 💰 **Módulo de Vendas**
- **Gestão de Vendas**: Registro e acompanhamento
- **Performance de Vendedores**: Métricas e bonificações
- **Dashboard de Vendas**: KPIs e análises
- **Relatórios**: Exportação e visualizações

## 🏗️ **Arquitetura**

```
HubControl/
├── 🐍 backend/                 # API FastAPI + ML
├── ⚛️  frontend/               # Interface React + Ant Design
├── 🗄️  database/               # Schema PostgreSQL + Migrações
├── 🤖 ml/                      # Sistema de Machine Learning
├── 📚 docs/                    # Documentação
├── 🐳 docker/                  # Configurações Docker
└── 📜 scripts/                 # Scripts de automação
```

## 🚀 **Tecnologias Utilizadas**

### **Backend & ML**
- **Python 3.11+** com FastAPI
- **Machine Learning**: Scikit-learn, XGBoost, LightGBM, TensorFlow
- **Banco de Dados**: PostgreSQL + SQLAlchemy
- **Cache**: Redis
- **Processamento**: Celery para tarefas assíncronas

### **Frontend**
- **React 18** com TypeScript
- **Ant Design**: Componentes profissionais
- **Ant Design Charts**: Gráficos interativos
- **Redux Toolkit**: Gerenciamento de estado
- **React Router**: Navegação SPA

### **Infraestrutura**
- **Docker & Docker Compose**
- **Nginx**: Proxy reverso e servidor web
- **Health Checks**: Monitoramento automático
- **Rate Limiting**: Proteção contra abuso

## 📦 **Instalação Rápida**

### **1. Pré-requisitos**
```bash
# Docker e Docker Compose instalados
docker --version
docker-compose --version
```

### **2. Clone e Execute**
```bash
git clone <repository-url>
cd HubControl

# Iniciar todos os serviços
./scripts/start.sh
```

### **3. Acesse o Sistema**
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **API Backend**: http://localhost:8000
- 📚 **Documentação**: http://localhost:8000/docs

## 🤖 **Sistema de Machine Learning**

### **Algoritmos Implementados**
- **Random Forest**: Para interpretabilidade e robustez
- **XGBoost**: Para performance e precisão
- **LightGBM**: Para velocidade e eficiência
- **Neural Networks**: Para padrões complexos
- **Ensemble**: Combinação inteligente dos modelos

### **Features de Engenharia**
- **Cliente**: LTV, tempo de relacionamento, status
- **Contratos**: Renovações, vencimento, valores
- **Health Score**: Componentes individuais e tendências
- **CSAT**: Satisfação, feedback, interações
- **Eventos**: Histórico de interações e ações

### **API de ML**
```bash
# Treinar modelos
POST /api/v1/ml/churn/train

# Prever churn individual
POST /api/v1/ml/churn/predict

# Insights gerais
GET /api/v1/ml/churn/insights

# Análise de risco em lote
GET /api/v1/ml/churn/clients/risk-analysis
```

## 📊 **Dashboards e Visualizações**

### **ML Dashboard**
- **Status dos Modelos**: Treinamento e performance
- **Previsões em Tempo Real**: Análise individual de clientes
- **Insights Automáticos**: Fatores de risco e recomendações
- **Métricas de Performance**: Acurácia, AUC, F1-Score

### **CS Dashboard**
- **Health Score**: Evolução e componentes
- **Pipeline de Renovação**: Status e próximos passos
- **Métricas de Churn**: Taxas e tendências
- **Alertas Inteligentes**: Baseados em ML

### **Vendas Dashboard**
- **Performance**: Vendedores e equipes
- **Métricas**: Valores, volumes, bonificações
- **Produtos**: Top sellers e análise de mix

## 🔐 **Segurança e Autenticação**

- **JWT**: Tokens seguros e renováveis
- **RBAC**: Controle de acesso baseado em perfis
- **Rate Limiting**: Proteção contra ataques
- **CORS**: Configuração segura para frontend
- **Audit Log**: Registro de todas as ações

## 📈 **Monitoramento e Observabilidade**

- **Health Checks**: Verificação automática de serviços
- **Logs Estruturados**: Formato JSON para análise
- **Métricas de Performance**: Tempo de resposta e throughput
- **Alertas**: Notificações para problemas críticos

## 🚀 **Deploy e Produção**

### **Ambiente de Desenvolvimento**
```bash
# Desenvolvimento local
./scripts/start.sh

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

### **Ambiente de Produção**
```bash
# Build de produção
docker-compose -f docker-compose.prod.yml up -d

# Variáveis de ambiente
cp backend/env.example backend/.env
# Editar .env com configurações de produção
```

## 📚 **Documentação Detalhada**

- **📖 [Implementação](docs/IMPLEMENTACAO.md)**: Arquitetura técnica completa
- **🔧 [API Reference](http://localhost:8000/docs)**: Documentação interativa da API
- **🤖 [ML Guide](docs/ML_GUIDE.md)**: Guia de Machine Learning
- **🎨 [Frontend Guide](docs/FRONTEND_GUIDE.md)**: Guia de desenvolvimento frontend

## 🤝 **Contribuição**

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🆘 **Suporte**

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/hubcontrol/issues)
- **Documentação**: [Wiki do Projeto](https://github.com/seu-usuario/hubcontrol/wiki)
- **Email**: suporte@hubcontrol.com

---

**🔮 HubControl** - Transformando dados em insights, insights em ações, e ações em resultados.

*Desenvolvido com ❤️ para otimizar a gestão de clientes e maximizar o valor do relacionamento.* 