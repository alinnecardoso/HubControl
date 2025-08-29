"""
Serviço de conexão com Supabase Database
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.sales_models import Base
import logging

logger = logging.getLogger(__name__)

# URL de conexão do Supabase (do ambiente ou padrão)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:himmelcorp123@db.auhkbtxjoqvahiajopop.supabase.co:5432/postgres"
)

class DatabaseService:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.connect()
    
    def connect(self):
        """Conectar ao banco de dados"""
        try:
            self.engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False  # Set to True for SQL debugging
            )
            
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Testar conexão
            with self.engine.connect() as conn:
                logger.info("✅ Conexão com Supabase estabelecida com sucesso!")
                
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com Supabase: {e}")
            raise e
    
    def create_tables(self):
        """Criar todas as tabelas no banco"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Tabelas criadas/atualizadas com sucesso!")
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
            raise e
    
    def get_db(self):
        """Obter sessão do banco de dados"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def test_connection(self):
        """Testar conexão com o banco"""
        try:
            from sqlalchemy import text
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test")).fetchone()
                return {"status": "success", "result": result[0]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Instância global do serviço
db_service = DatabaseService()