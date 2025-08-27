"""
Modelo de Health Score Snapshot
"""
from sqlalchemy import Column, String, Integer, Numeric, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class HealthScoreSnapshot(Base, TimestampMixin):
    """Modelo de snapshot de Health Score dos clientes"""
    
    __tablename__ = "health_score_snapshot"
    
    # Campos de identificação
    id_cliente = Column(ForeignKey("cliente.id"), nullable=False, index=True)
    id_assessor = Column(ForeignKey("assessor.id"), nullable=False, index=True)
    data_avaliacao = Column(DateTime, nullable=False, index=True)
    
    # Componentes do Health Score (1-5)
    aprofundar_processos = Column(Integer, nullable=False)
    interesse_genuino = Column(Integer, nullable=False)
    comunicacao_ativa = Column(Integer, nullable=False)
    clareza_objetivos = Column(Integer, nullable=False)
    aceita_sugestoes = Column(Integer, nullable=False)
    condicoes_financeiras = Column(Integer, nullable=False)
    equipe_estrutura = Column(Integer, nullable=False)
    maturidade_processos = Column(Integer, nullable=False)
    delega_confianca = Column(Integer, nullable=False)
    relacionamento = Column(Integer, nullable=False)
    
    # Médias calculadas
    media_engaj_com = Column(Numeric(3, 2))
    media_direcao = Column(Numeric(3, 2))
    media_capacidade_recurso = Column(Numeric(3, 2))
    media_relacionamento = Column(Numeric(3, 2))
    media_geral = Column(Numeric(3, 2))
    
    # Score final e risco
    health_score_total = Column(Integer, nullable=False, index=True)
    nivel_risco = Column(String(50), nullable=False, index=True)
    observacoes = Column(Text)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="health_scores")
    assessor = relationship("Assessor", back_populates="health_scores")
    
    # Índices compostos
    __table_args__ = (
        Index('idx_health_score_cliente_data', 'id_cliente', 'data_avaliacao'),
        Index('idx_health_score_risco_data', 'nivel_risco', 'data_avaliacao'),
        Index('idx_health_score_assessor_data', 'id_assessor', 'data_avaliacao'),
    )
    
    def __repr__(self):
        return f"<HealthScoreSnapshot(id={self.id}, cliente_id={self.id_cliente}, score={self.health_score_total}, risco='{self.nivel_risco}')>"
    
    def calcular_medias(self) -> None:
        """Calcula todas as médias dos componentes"""
        # Média Engajamento e Comunicação
        self.media_engaj_com = (
            self.aprofundar_processos + 
            self.interesse_genuino + 
            self.comunicacao_ativa
        ) / 3
        
        # Média Direção
        self.media_direcao = (
            self.clareza_objetivos + 
            self.aceita_sugestoes
        ) / 2
        
        # Média Capacidade e Recursos
        self.media_capacidade_recurso = (
            self.condicoes_financeiras + 
            self.equipe_estrutura + 
            self.maturidade_processos
        ) / 3
        
        # Média Relacionamento
        self.media_relacionamento = (
            self.delega_confianca + 
            self.relacionamento
        ) / 2
        
        # Média Geral
        self.media_geral = (
            self.aprofundar_processos + 
            self.interesse_genuino + 
            self.comunicacao_ativa + 
            self.clareza_objetivos + 
            self.aceita_sugestoes + 
            self.condicoes_financeiras + 
            self.equipe_estrutura + 
            self.maturidade_processos + 
            self.delega_confianca + 
            self.relacionamento
        ) / 10
    
    def calcular_health_score_total(self) -> None:
        """Calcula o Health Score total (0-100)"""
        # Soma todos os componentes
        soma_componentes = (
            self.aprofundar_processos + 
            self.interesse_genuino + 
            self.comunicacao_ativa + 
            self.clareza_objetivos + 
            self.aceita_sugestoes + 
            self.condicoes_financeiras + 
            self.equipe_estrutura + 
            self.maturidade_processos + 
            self.delega_confianca + 
            self.relacionamento
        )
        
        # Converte para escala 0-100 (cada componente vale 10 pontos)
        self.health_score_total = soma_componentes * 2
    
    def determinar_nivel_risco(self) -> None:
        """Determina o nível de risco baseado no Health Score"""
        if self.health_score_total >= 80:
            self.nivel_risco = "baixo"
        elif self.health_score_total >= 60:
            self.nivel_risco = "medio"
        elif self.health_score_total >= 40:
            self.nivel_risco = "alto"
        else:
            self.nivel_risco = "critico"
    
    def calcular_todos_indicadores(self) -> None:
        """Calcula todos os indicadores do Health Score"""
        self.calcular_medias()
        self.calcular_health_score_total()
        self.determinar_nivel_risco()
    
    @property
    def is_risco_baixo(self) -> bool:
        """Verifica se o risco é baixo"""
        return self.nivel_risco == "baixo"
    
    @property
    def is_risco_medio(self) -> bool:
        """Verifica se o risco é médio"""
        return self.nivel_risco == "medio"
    
    @property
    def is_risco_alto(self) -> bool:
        """Verifica se o risco é alto"""
        return self.nivel_risco == "alto"
    
    @property
    def is_risco_critico(self) -> bool:
        """Verifica se o risco é crítico"""
        return self.nivel_risco == "critico"
    
    @property
    def componentes_baixos(self) -> list:
        """Retorna os componentes com pontuação baixa (1-2)"""
        componentes = {
            'aprofundar_processos': self.aprofundar_processos,
            'interesse_genuino': self.interesse_genuino,
            'comunicacao_ativa': self.comunicacao_ativa,
            'clareza_objetivos': self.clareza_objetivos,
            'aceita_sugestoes': self.aceita_sugestoes,
            'condicoes_financeiras': self.condicoes_financeiras,
            'equipe_estrutura': self.equipe_estrutura,
            'maturidade_processos': self.maturidade_processos,
            'delega_confianca': self.delega_confianca,
            'relacionamento': self.relacionamento
        }
        
        return [nome for nome, valor in componentes.items() if valor <= 2]
    
    @property
    def componentes_altos(self) -> list:
        """Retorna os componentes com pontuação alta (4-5)"""
        componentes = {
            'aprofundar_processos': self.aprofundar_processos,
            'interesse_genuino': self.interesse_genuino,
            'comunicacao_ativa': self.comunicacao_ativa,
            'clareza_objetivos': self.clareza_objetivos,
            'aceita_sugestoes': self.aceita_sugestoes,
            'condicoes_financeiras': self.condicoes_financeiras,
            'equipe_estrutura': self.equipe_estrutura,
            'maturidade_processos': self.maturidade_processos,
            'delega_confianca': self.delega_confianca,
            'relacionamento': self.relacionamento
        }
        
        return [nome for nome, valor in componentes.items() if valor >= 4]
    
    def get_tendencias(self, snapshots_anteriores: list) -> dict:
        """Analisa tendências comparando com snapshots anteriores"""
        if not snapshots_anteriores:
            return {"tendencia": "sem_dados", "melhorias": [], "pioras": []}
        
        # Ordena por data
        snapshots_ordenados = sorted(snapshots_anteriores, key=lambda x: x.data_avaliacao)
        snapshot_anterior = snapshots_ordenados[-1]
        
        # Compara componentes
        melhorias = []
        pioras = []
        
        componentes = [
            'aprofundar_processos', 'interesse_genuino', 'comunicacao_ativa',
            'clareza_objetivos', 'aceita_sugestoes', 'condicoes_financeiras',
            'equipe_estrutura', 'maturidade_processos', 'delega_confianca', 'relacionamento'
        ]
        
        for componente in componentes:
            valor_atual = getattr(self, componente)
            valor_anterior = getattr(snapshot_anterior, componente)
            
            if valor_atual > valor_anterior:
                melhorias.append(componente)
            elif valor_atual < valor_anterior:
                pioras.append(componente)
        
        # Determina tendência geral
        if self.health_score_total > snapshot_anterior.health_score_total:
            tendencia = "melhorando"
        elif self.health_score_total < snapshot_anterior.health_score_total:
            tendencia = "piorando"
        else:
            tendencia = "estavel"
        
        return {
            "tendencia": tendencia,
            "melhorias": melhorias,
            "pioras": pioras,
            "variacao_score": self.health_score_total - snapshot_anterior.health_score_total
        }
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Converte o Health Score para dicionário"""
        data = super().to_dict()
        
        # Adiciona propriedades calculadas
        data["is_risco_baixo"] = self.is_risco_baixo
        data["is_risco_medio"] = self.is_risco_medio
        data["is_risco_alto"] = self.is_risco_alto
        data["is_risco_critico"] = self.is_risco_critico
        data["componentes_baixos"] = self.componentes_baixos
        data["componentes_altos"] = self.componentes_altos
        
        if include_relationships:
            data["cliente"] = self.cliente.to_dict() if self.cliente else None
            data["assessor"] = self.assessor.to_dict() if self.assessor else None
        
        return data 