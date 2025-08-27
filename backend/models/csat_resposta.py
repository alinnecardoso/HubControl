"""
Modelo de CSAT (Customer Satisfaction) do sistema
"""
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class CSATResposta(Base, TimestampMixin):
    """Modelo de resposta CSAT dos clientes"""
    
    __tablename__ = "csat_resposta"
    
    # Campos de identificação
    id_cliente = Column(ForeignKey("cliente.id"), nullable=False, index=True)
    id_consultor = Column(ForeignKey("assessor.id"), nullable=False, index=True)
    data_resposta = Column(DateTime, nullable=False, index=True)
    
    # Avaliação da call (1-5)
    avaliacao_call = Column(Integer, nullable=False, index=True)
    
    # Perguntas qualitativas
    temas_alinhados_objetivos = Column(Boolean)
    acoes_geram_resultados = Column(Boolean)
    o_que_falta = Column(Text)
    o_que_discutir_calls = Column(Text)
    comentarios_gerais = Column(Text)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="csat_respostas")
    consultor = relationship("Assessor", back_populates="csat_respostas")
    
    # Índices compostos
    __table_args__ = (
        Index('idx_csat_cliente_data', 'id_cliente', 'data_resposta'),
        Index('idx_csat_consultor_data', 'id_consultor', 'data_resposta'),
        Index('idx_csat_avaliacao_data', 'avaliacao_call', 'data_resposta'),
    )
    
    def __repr__(self):
        return f"<CSATResposta(id={self.id}, cliente_id={self.id_cliente}, avaliacao={self.avaliacao_call})>"
    
    @property
    def is_avaliacao_positiva(self) -> bool:
        """Verifica se a avaliação é positiva (4-5 estrelas)"""
        return self.avaliacao_call >= 4
    
    @property
    def is_avaliacao_neutra(self) -> bool:
        """Verifica se a avaliação é neutra (3 estrelas)"""
        return self.avaliacao_call == 3
    
    @property
    def is_avaliacao_negativa(self) -> bool:
        """Verifica se a avaliação é negativa (1-2 estrelas)"""
        return self.avaliacao_call <= 2
    
    @property
    def nivel_satisfacao(self) -> str:
        """Retorna o nível de satisfação baseado na avaliação"""
        if self.avaliacao_call == 5:
            return "muito_satisfeito"
        elif self.avaliacao_call == 4:
            return "satisfeito"
        elif self.avaliacao_call == 3:
            return "neutro"
        elif self.avaliacao_call == 2:
            return "insatisfeito"
        else:
            return "muito_insatisfeito"
    
    @property
    def tem_feedback_negativo(self) -> bool:
        """Verifica se há feedback negativo"""
        return (
            self.is_avaliacao_negativa or
            self.o_que_falta or
            (self.comentarios_gerais and len(self.comentarios_gerais.strip()) > 0)
        )
    
    @property
    def tem_feedback_positivo(self) -> bool:
        """Verifica se há feedback positivo"""
        return (
            self.is_avaliacao_positiva or
            self.temas_alinhados_objetivos or
            self.acoes_geram_resultados or
            (self.comentarios_gerais and len(self.comentarios_gerais.strip()) > 0)
        )
    
    @property
    def score_numerico(self) -> float:
        """Retorna o score numérico para cálculos"""
        return float(self.avaliacao_call)
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Converte o CSAT para dicionário"""
        data = super().to_dict()
        
        # Adiciona propriedades calculadas
        data["is_avaliacao_positiva"] = self.is_avaliacao_positiva
        data["is_avaliacao_neutra"] = self.is_avaliacao_neutra
        data["is_avaliacao_negativa"] = self.is_avaliacao_negativa
        data["nivel_satisfacao"] = self.nivel_satisfacao
        data["tem_feedback_negativo"] = self.tem_feedback_negativo
        data["tem_feedback_positivo"] = self.tem_feedback_positivo
        data["score_numerico"] = self.score_numerico
        
        if include_relationships:
            data["cliente"] = self.cliente.to_dict() if self.cliente else None
            data["consultor"] = self.consultor.to_dict() if self.consultor else None
        
        return data


class CSATAnalytics:
    """Classe para análise agregada de CSAT"""
    
    @staticmethod
    def calcular_metricas_gerais(respostas: list) -> dict:
        """Calcula métricas gerais de CSAT"""
        if not respostas:
            return {
                "total_respostas": 0,
                "media_geral": 0,
                "percentual_positivo": 0,
                "percentual_neutro": 0,
                "percentual_negativo": 0,
                "nps_score": 0
            }
        
        total = len(respostas)
        positivas = sum(1 for r in respostas if r.is_avaliacao_positiva)
        neutras = sum(1 for r in respostas if r.is_avaliacao_neutra)
        negativas = sum(1 for r in respostas if r.is_avaliacao_negativa)
        
        media_geral = sum(r.score_numerico for r in respostas) / total
        percentual_positivo = (positivas / total) * 100
        percentual_neutro = (neutras / total) * 100
        percentual_negativo = (negativas / total) * 100
        
        # Calcula NPS (Net Promoter Score)
        promotores = sum(1 for r in respostas if r.avaliacao_call == 5)
        detratores = sum(1 for r in respostas if r.avaliacao_call <= 2)
        nps_score = ((promotores - detratores) / total) * 100
        
        return {
            "total_respostas": total,
            "media_geral": round(media_geral, 2),
            "percentual_positivo": round(percentual_positivo, 2),
            "percentual_neutro": round(percentual_neutro, 2),
            "percentual_negativo": round(percentual_negativo, 2),
            "nps_score": round(nps_score, 2)
        }
    
    @staticmethod
    def analisar_tendencias(respostas: list, periodo_dias: int = 30) -> dict:
        """Analisa tendências de CSAT ao longo do tempo"""
        from datetime import datetime, timedelta
        
        if not respostas:
            return {"tendencia": "sem_dados", "variacao": 0}
        
        # Filtra respostas do período
        data_limite = datetime.now() - timedelta(days=periodo_dias)
        respostas_recentes = [r for r in respostas if r.data_resposta >= data_limite]
        respostas_anteriores = [r for r in respostas if r.data_resposta < data_limite]
        
        if not respostas_recentes or not respostas_anteriores:
            return {"tendencia": "dados_insuficientes", "variacao": 0}
        
        # Calcula médias
        media_recente = sum(r.score_numerico for r in respostas_recentes) / len(respostas_recentes)
        media_anterior = sum(r.score_numerico for r in respostas_anteriores) / len(respostas_anteriores)
        
        variacao = media_recente - media_anterior
        
        if variacao > 0.5:
            tendencia = "melhorando"
        elif variacao < -0.5:
            tendencia = "piorando"
        else:
            tendencia = "estavel"
        
        return {
            "tendencia": tendencia,
            "variacao": round(variacao, 2),
            "media_recente": round(media_recente, 2),
            "media_anterior": round(media_anterior, 2)
        }
    
    @staticmethod
    def identificar_topicos_feedback(respostas: list) -> dict:
        """Identifica tópicos comuns no feedback"""
        topicos = {
            "positivos": [],
            "negativos": [],
            "sugestoes": []
        }
        
        for resposta in respostas:
            if resposta.comentarios_gerais:
                comentario = resposta.comentarios_gerais.lower()
                
                # Categoriza comentários
                if resposta.is_avaliacao_positiva:
                    topicos["positivos"].append(comentario)
                elif resposta.is_avaliacao_negativa:
                    topicos["negativos"].append(comentario)
                
                # Identifica sugestões
                if any(palavra in comentario for palavra in ["sugestão", "sugestao", "poderia", "gostaria"]):
                    topicos["sugestoes"].append(comentario)
        
        return topicos 