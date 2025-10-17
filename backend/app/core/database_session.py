# backend/app/core/database_session.py

"""
SQLAlchemy session configuration for ORM-based services
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os
import logging

logger = logging.getLogger(__name__)

class DatabaseSession:
    """SQLAlchemy session manager for Cloud SQL"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize SQLAlchemy engine"""
        try:
            # Get database configuration from environment
            if os.getenv("CLOUD_SQL_CONNECTION_NAME"):
                # Cloud Run deployment
                connection_name = os.getenv("CLOUD_SQL_CONNECTION_NAME")
                db_user = os.getenv("CLOUD_SQL_USER", "postgres")
                db_password = os.getenv("CLOUD_SQL_PASSWORD", "")
                db_name = os.getenv("CLOUD_SQL_DATABASE", "validatus_db")
                
                # Use Unix socket for Cloud SQL
                db_socket_dir = os.getenv("DB_SOCKET_DIR", "/cloudsql")
                unix_socket = f"{db_socket_dir}/{connection_name}"
                
                database_url = f"postgresql+psycopg2://{db_user}:{db_password}@/{db_name}?host={unix_socket}"
                
                logger.info(f"Initializing SQLAlchemy engine for Cloud SQL: {connection_name}")
                
            else:
                # Local development
                db_host = os.getenv("DB_HOST", "localhost")
                db_port = os.getenv("DB_PORT", "5432")
                db_user = os.getenv("DB_USER", "postgres")
                db_password = os.getenv("DB_PASSWORD", "")
                db_name = os.getenv("DB_NAME", "validatus_db")
                
                database_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
                
                logger.info(f"Initializing SQLAlchemy engine for local development: {db_host}:{db_port}")
            
            # Create engine with connection pooling
            self.engine = create_engine(
                database_url,
                poolclass=NullPool,  # Disable pooling for Cloud Run (short-lived connections)
                echo=False,  # Set to True for SQL query debugging
                pool_pre_ping=True,  # Enable connection health checks
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("✅ SQLAlchemy engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize SQLAlchemy engine: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a new database session"""
        if not self.SessionLocal:
            raise RuntimeError("Database session not initialized")
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            session = self.get_session()
            session.execute("SELECT 1")
            session.close()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

# Global session manager instance
db_session_manager = DatabaseSession()

def get_db():
    """Dependency for FastAPI endpoints to get database session"""
    db = db_session_manager.get_session()
    try:
        yield db
    finally:
        db.close()
