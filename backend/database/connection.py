"""
Conexão com o banco de dados PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging

from config import DATABASE_CONFIG

logger = logging.getLogger(__name__)

# Engine do banco de dados
engine = None

# Session factory
SessionLocal = None

# Base para os modelos
Base = declarative_base()


async def init_db():
    """Inicializa a conexão com o banco de dados"""
    global engine, SessionLocal
    
    try:
        # Cria o engine do banco
        engine = create_engine(
            DATABASE_CONFIG["url"],
            echo=DATABASE_CONFIG["echo"],
            poolclass=QueuePool,
            pool_size=DATABASE_CONFIG["pool_size"],
            max_overflow=DATABASE_CONFIG["max_overflow"],
            pool_pre_ping=DATABASE_CONFIG["pool_pre_ping"],
            pool_recycle=DATABASE_CONFIG["pool_recycle"]
        )
        
        # Cria a session factory
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        
        # Testa a conexão
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        logger.info("Conexão com o banco de dados estabelecida com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao conectar com o banco de dados: {str(e)}")
        raise


async def close_db():
    """Fecha a conexão com o banco de dados"""
    global engine
    
    if engine:
        engine.dispose()
        logger.info("Conexão com o banco de dados fechada!")


def get_db() -> Session:
    """Retorna uma sessão do banco de dados"""
    if not SessionLocal:
        raise RuntimeError("Banco de dados não inicializado. Chame init_db() primeiro.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_sync() -> Session:
    """Retorna uma sessão síncrona do banco de dados"""
    if not SessionLocal:
        raise RuntimeError("Banco de dados não inicializado. Chame init_db() primeiro.")
    
    return SessionLocal()


# Função para criar todas as tabelas
def create_tables():
    """Cria todas as tabelas do banco de dados"""
    try:
        # Importa todos os modelos para garantir que sejam registrados
        from models import Base
        
        # Cria as tabelas
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {str(e)}")
        raise


# Função para verificar se o banco está acessível
def check_db_connection() -> bool:
    """Verifica se o banco de dados está acessível"""
    try:
        if not engine:
            return False
        
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
        
    except Exception:
        return False


# Função para obter informações do banco
def get_db_info() -> dict:
    """Retorna informações sobre o banco de dados"""
    try:
        if not engine:
            return {"status": "não_inicializado"}
        
        with engine.connect() as conn:
            # Informações da conexão
            info = {
                "status": "conectado",
                "url": str(engine.url),
                "pool_size": engine.pool.size(),
                "pool_checked_in": engine.pool.checkedin(),
                "pool_checked_out": engine.pool.checkedout(),
                "pool_overflow": engine.pool.overflow()
            }
            
            # Testa uma query simples
            result = conn.execute("SELECT version()")
            version = result.fetchone()[0]
            info["postgres_version"] = version
            
            return info
            
    except Exception as e:
        return {
            "status": "erro",
            "error": str(e)
        } 