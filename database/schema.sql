-- HubControl Database Schema
-- Módulos: Customer Success (CS) e Vendas

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================
-- TABELAS BASE
-- =====================================================

-- Tabela de usuários do sistema
CREATE TABLE usuario (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    perfil VARCHAR(50) NOT NULL CHECK (perfil IN ('admin', 'cs', 'vendedor', 'gerente')),
    ativo BOOLEAN DEFAULT true,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de equipes
CREATE TABLE equipe (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('cs', 'vendas', 'financeiro', 'dataops')),
    ativo BOOLEAN DEFAULT true,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- MÓDULO DE VENDAS
-- =====================================================

-- Tabela de vendedores
CREATE TABLE vendedor (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES usuario(id),
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    equipe_vendas_id UUID REFERENCES equipe(id),
    ativo BOOLEAN DEFAULT true,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de clientes (base para todos os módulos)
CREATE TABLE cliente (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cust_id_externo VARCHAR(100) UNIQUE,
    nome_principal VARCHAR(255) NOT NULL,
    nickname VARCHAR(255),
    telefone VARCHAR(20),
    email VARCHAR(255),
    loja_associada VARCHAR(255),
    status_cliente VARCHAR(50) DEFAULT 'ativo' CHECK (status_cliente IN ('ativo', 'inativo', 'potencial', 'churn')),
    jornada_iniciada_em DATE,
    ltv_meses INTEGER DEFAULT 0,
    ltv_valor NUMERIC(15,2) DEFAULT 0,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    info_adicional_vendas TEXT,
    info_adicional_cs TEXT
);

-- Tabela de vendas
CREATE TABLE venda (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data DATE NOT NULL,
    loja VARCHAR(255) NOT NULL,
    cliente_id UUID REFERENCES cliente(id),
    telefone_cliente VARCHAR(20),
    produto VARCHAR(255) NOT NULL,
    valor_mensal NUMERIC(15,2) NOT NULL,
    percentual_variavel NUMERIC(5,2),
    vendedor_id UUID REFERENCES vendedor(id),
    contrato_meses INTEGER NOT NULL,
    forma_pagamento VARCHAR(100) NOT NULL,
    canal_venda VARCHAR(100),
    descricao TEXT,
    info_adicional TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- MÓDULO DE CUSTOMER SUCCESS (CS)
-- =====================================================

-- Tabela de contas (para contas adicionais)
CREATE TABLE conta (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cliente_id UUID REFERENCES cliente(id),
    apelido VARCHAR(255),
    plataforma VARCHAR(100),
    status VARCHAR(50) DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo', 'suspenso')),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de contratos
CREATE TABLE contrato (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cliente_id UUID REFERENCES cliente(id),
    conta_id UUID REFERENCES conta(id),
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    duracao_meses INTEGER NOT NULL,
    valor_mensal NUMERIC(15,2) NOT NULL,
    status_contrato VARCHAR(50) DEFAULT 'ativo' CHECK (status_contrato IN ('ativo', 'pausado', 'a_vencer', 'renegociar', 'vencido', 'encerrado')),
    ciclo_atual INTEGER DEFAULT 1,
    auto_renovacao BOOLEAN DEFAULT false,
    dias_a_vencer INTEGER GENERATED ALWAYS AS (data_fim - CURRENT_DATE) STORED,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Histórico de status do contrato
CREATE TABLE contrato_status_historico (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contrato_id UUID REFERENCES contrato(id),
    status_anterior VARCHAR(50),
    status_novo VARCHAR(50),
    motivo_mudanca TEXT,
    usuario_id UUID REFERENCES usuario(id),
    data_mudanca TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Histórico de ciclos do contrato
CREATE TABLE historico_ciclo_contrato (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contrato_id UUID REFERENCES contrato(id),
    ciclo INTEGER NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    duracao_meses INTEGER NOT NULL,
    valor_mensal NUMERIC(15,2) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de renovações
CREATE TABLE renovacao (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contrato_id UUID REFERENCES contrato(id),
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('manual', 'auto_renovacao')),
    data_renovacao DATE NOT NULL,
    novo_ciclo INTEGER NOT NULL,
    nova_data_fim DATE NOT NULL,
    novo_valor_mensal NUMERIC(15,2),
    observacoes TEXT,
    usuario_id UUID REFERENCES usuario(id),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de eventos de CS
CREATE TABLE evento_cs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cliente_id UUID REFERENCES cliente(id),
    contrato_id UUID REFERENCES contrato(id),
    tipo VARCHAR(100) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,
    data_evento TIMESTAMP,
    proximos_passos TEXT,
    responsavel_id UUID REFERENCES usuario(id),
    status VARCHAR(50) DEFAULT 'agendado' CHECK (status IN ('agendado', 'realizado', 'cancelado', 'adiado')),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de eventos de churn
CREATE TABLE churn_evento (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cliente_id UUID REFERENCES cliente(id),
    contrato_id UUID REFERENCES contrato(id),
    data_churn DATE NOT NULL,
    motivo VARCHAR(100) NOT NULL,
    descricao TEXT,
    valor_perdido NUMERIC(15,2),
    usuario_id UUID REFERENCES usuario(id),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- HEALTH SCORE E CSAT
-- =====================================================

-- Tabela de assessores/consultores
CREATE TABLE assessor (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES usuario(id),
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    equipe_id UUID REFERENCES equipe(id),
    ativo BOOLEAN DEFAULT true,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de snapshots de Health Score
CREATE TABLE health_score_snapshot (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_cliente UUID REFERENCES cliente(id),
    id_assessor UUID REFERENCES assessor(id),
    data_avaliacao TIMESTAMP NOT NULL,
    
    -- Componentes do Health Score (1-5)
    aprofundar_processos INTEGER CHECK (aprofundar_processos >= 1 AND aprofundar_processos <= 5),
    interesse_genuino INTEGER CHECK (interesse_genuino >= 1 AND interesse_genuino <= 5),
    comunicacao_ativa INTEGER CHECK (comunicacao_ativa >= 1 AND comunicacao_ativa <= 5),
    clareza_objetivos INTEGER CHECK (clareza_objetivos >= 1 AND clareza_objetivos <= 5),
    aceita_sugestoes INTEGER CHECK (aceita_sugestoes >= 1 AND aceita_sugestoes <= 5),
    condicoes_financeiras INTEGER CHECK (condicoes_financeiras >= 1 AND condicoes_financeiras <= 5),
    equipe_estrutura INTEGER CHECK (equipe_estrutura >= 1 AND equipe_estrutura <= 5),
    maturidade_processos INTEGER CHECK (maturidade_processos >= 1 AND maturidade_processos <= 5),
    delega_confianca INTEGER CHECK (delega_confianca >= 1 AND delega_confianca <= 5),
    relacionamento INTEGER CHECK (relacionamento >= 1 AND relacionamento <= 5),
    
    -- Médias calculadas
    media_engaj_com NUMERIC(3,2),
    media_direcao NUMERIC(3,2),
    media_capacidade_recurso NUMERIC(3,2),
    media_relacionamento NUMERIC(3,2),
    media_geral NUMERIC(3,2),
    
    -- Score final e risco
    health_score_total INTEGER CHECK (health_score_total >= 0 AND health_score_total <= 100),
    nivel_risco VARCHAR(50) CHECK (nivel_risco IN ('baixo', 'medio', 'alto', 'critico')),
    observacoes TEXT,
    
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de respostas CSAT
CREATE TABLE csat_resposta (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_cliente UUID REFERENCES cliente(id),
    id_consultor UUID REFERENCES assessor(id),
    data_resposta TIMESTAMP NOT NULL,
    
    -- Avaliação da call (1-5)
    avaliacao_call INTEGER CHECK (avaliacao_call >= 1 AND avaliacao_call <= 5),
    
    -- Perguntas qualitativas
    temas_alinhados_objetivos BOOLEAN,
    o_que_falta TEXT,
    acoes_geram_resultados BOOLEAN,
    o_que_discutir_calls TEXT,
    comentarios_gerais TEXT,
    
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ÍNDICES PARA PERFORMANCE
-- =====================================================

-- Índices para vendas
CREATE INDEX idx_venda_data ON venda(data);
CREATE INDEX idx_venda_vendedor_id ON venda(vendedor_id);
CREATE INDEX idx_venda_cliente_id ON venda(cliente_id);

-- Índices para CS
CREATE INDEX idx_contrato_cliente_id ON contrato(cliente_id);
CREATE INDEX idx_contrato_status ON contrato(status_contrato);
CREATE INDEX idx_contrato_data_fim ON contrato(data_fim);
CREATE INDEX idx_contrato_dias_a_vencer ON contrato(dias_a_vencer);

CREATE INDEX idx_evento_cs_cliente_id ON evento_cs(cliente_id);
CREATE INDEX idx_evento_cs_data_evento ON evento_cs(data_evento);

CREATE INDEX idx_churn_evento_cliente_id ON churn_evento(cliente_id);
CREATE INDEX idx_churn_evento_data_churn ON churn_evento(data_churn);

-- Índices para Health Score e CSAT
CREATE INDEX idx_health_score_cliente_id ON health_score_snapshot(id_cliente);
CREATE INDEX idx_health_score_data_avaliacao ON health_score_snapshot(data_avaliacao);

CREATE INDEX idx_csat_cliente_id ON csat_resposta(id_cliente);
CREATE INDEX idx_csat_data_resposta ON csat_resposta(data_resposta);

-- =====================================================
-- FUNÇÕES E TRIGGERS
-- =====================================================

-- Função para atualizar data_ultima_atualizacao
CREATE OR REPLACE FUNCTION update_ultima_atualizacao()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_ultima_atualizacao = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para atualizar data_ultima_atualizacao
CREATE TRIGGER trigger_update_cliente
    BEFORE UPDATE ON cliente
    FOR EACH ROW
    EXECUTE FUNCTION update_ultima_atualizacao();

CREATE TRIGGER trigger_update_contrato
    BEFORE UPDATE ON contrato
    FOR EACH ROW
    EXECUTE FUNCTION update_ultima_atualizacao();

CREATE TRIGGER trigger_update_venda
    BEFORE UPDATE ON venda
    FOR EACH ROW
    EXECUTE FUNCTION update_ultima_atualizacao();

CREATE TRIGGER trigger_update_evento_cs
    BEFORE UPDATE ON evento_cs
    FOR EACH ROW
    EXECUTE FUNCTION update_ultima_atualizacao();

-- Função para calcular Health Score
CREATE OR REPLACE FUNCTION calcular_health_score(
    aprofundar_processos INTEGER,
    interesse_genuino INTEGER,
    comunicacao_ativa INTEGER,
    clareza_objetivos INTEGER,
    aceita_sugestoes INTEGER,
    condicoes_financeiras INTEGER,
    equipe_estrutura INTEGER,
    maturidade_processos INTEGER,
    delega_confianca INTEGER,
    relacionamento INTEGER
)
RETURNS INTEGER AS $$
DECLARE
    score INTEGER;
BEGIN
    -- Lógica de cálculo do Health Score (exemplo)
    score := (
        aprofundar_processos + interesse_genuino + comunicacao_ativa + 
        clareza_objetivos + aceita_sugestoes + condicoes_financeiras + 
        equipe_estrutura + maturidade_processos + delega_confianca + relacionamento
    ) * 2; -- Multiplica por 2 para escala 0-100
    
    RETURN score;
END;
$$ LANGUAGE plpgsql;

-- Função para determinar nível de risco
CREATE OR REPLACE FUNCTION determinar_nivel_risco(health_score INTEGER)
RETURNS VARCHAR(50) AS $$
BEGIN
    IF health_score >= 80 THEN
        RETURN 'baixo';
    ELSIF health_score >= 60 THEN
        RETURN 'medio';
    ELSIF health_score >= 40 THEN
        RETURN 'alto';
    ELSE
        RETURN 'critico';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- DADOS INICIAIS
-- =====================================================

-- Inserir usuário admin padrão
INSERT INTO usuario (nome, email, senha_hash, perfil) 
VALUES ('Administrador', 'admin@hubcontrol.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/vHhHhHh', 'admin');

-- Inserir equipes padrão
INSERT INTO equipe (nome, tipo) VALUES 
('Equipe CS', 'cs'),
('Equipe Vendas', 'vendas'),
('Equipe Financeiro', 'financeiro'),
('Equipe DataOps', 'dataops');

-- Comentários das tabelas
COMMENT ON TABLE cliente IS 'Tabela central de clientes para todos os módulos';
COMMENT ON TABLE venda IS 'Registro de vendas realizadas pelos vendedores';
COMMENT ON TABLE contrato IS 'Contratos dos clientes com gestão de ciclos e renovação';
COMMENT ON TABLE health_score_snapshot IS 'Snapshots de Health Score dos clientes';
COMMENT ON TABLE csat_resposta IS 'Respostas de satisfação dos clientes (CSAT)'; 