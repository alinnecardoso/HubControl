"""
Conexão com o banco de dados PostgreSQL
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import logging

# Importação relativa para acessar o módulo de configuração a partir do diretório pai
from ..config import settings

logger = logging.getLogger(__name__)

# O SQLAlchemy Engine e a SessionLocal são inicializadas como None
# e configuradas pela função init_db no startup da aplicação.
engine = None
SessionLocal = None

# Base declarativa para os modelos do SQLAlchemy
Base = declarative_base()


def init_db():
    """Inicializa a conexão com o banco de dados e a session factory.""""""_summary_

    Raises:
        e: _description_
    """
    global engine, SessionLocal
    
    try:
        # Usa a DATABASE_URL do objeto de configurações
        engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,     # Loga as queries SQL se o modo DEBUG estiver ativo
            pool_pre_ping=True,      # Verifica a conexão antes de usar
            pool_recycle=3600        # Recicla conexões a cada hora
        )
        
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        
        # Testa a conexão para garantir que tudo está funcionando
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            
        logger.info("Conexão com o banco de dados estabelecida com sucesso.")

    except Exception as e:
        logger.error(f"Falha ao inicializar a conexão com o banco de dados: {e}")
        raise


def get_db():
    """
    Dependência do FastAPI para obter uma sessão do banco de dados.
    Garante que a sessão seja sempre fechada após o uso.
    """
    if not SessionLocal:
        raise RuntimeError("A conexão com o banco de dados não foi inicializada (SessionLocal é None). O evento de startup da aplicação foi executado? Ocorreu algum erro durante a inicialização? Verifique os logs.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para criar as tabelas
def create_tables():
    """Cria todas as tabelas no banco de dados que herdam de Base.""""""_summary_

    Raises:
        RuntimeError: _description_
    """
    if not engine:
        raise RuntimeError("O engine do banco de dados não foi inicializado.")
    
    # Para que o create_all funcione, todos os seus modelos do SQLAlchemy
    # que herdam de 'Base' precisam ser importados antes que esta função seja chamada.
    # Uma boa prática é importá-los no módulo onde 'Base' é usada (ex: models/__init__.py)
    # ou no ponto de entrada da sua aplicação.
    from ..models import cliente, venda, vendedor # Exemplo

    Base.metadata.create_all(bind=engine)
    logger.info("Tabelas verificadas/criadas com sucesso.")
