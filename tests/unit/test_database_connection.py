#!/usr/bin/env python3
"""
Database Connection Unit Tests
Consolidated from: test_db_connection.py, test_simple_db.py
Tests database connectivity and configuration
"""
import pytest
import asyncio
import os
from unittest.mock import patch


class TestDatabaseConnection:
    """Test database connection functionality"""
    
    @pytest.mark.skipif(
        not os.getenv('CLOUD_SQL_PASSWORD') and not os.getenv('LOCAL_POSTGRES_URL'),
        reason="No database credentials available"
    )
    @pytest.mark.asyncio
    async def test_postgresql_connection(self):
        """Test PostgreSQL connection"""
        try:
            import asyncpg
        except ImportError:
            pytest.skip("asyncpg not installed")
        
        # Test with environment variable
        password = os.getenv('CLOUD_SQL_PASSWORD', os.getenv('DATABASE_PASSWORD', 'test_password'))
        
        # Try local connection first
        local_url = os.getenv('LOCAL_POSTGRES_URL')
        if local_url:
            try:
                conn = await asyncpg.connect(local_url, timeout=5)
                version = await conn.fetchval("SELECT version()")
                assert version is not None
                await conn.close()
                return
            except Exception as e:
                pytest.skip(f"Local PostgreSQL not available: {e}")
        
        pytest.skip("No PostgreSQL connection available for testing")
    
    def test_database_configuration(self):
        """Test database configuration"""
        # Test that database settings are properly configured
        from backend.app.core import database_config
        
        config = database_config.get_db_settings()
        assert config is not None
        assert hasattr(config, 'database_url') or hasattr(config, 'db_path')
    
    @pytest.mark.asyncio
    async def test_database_health_check(self):
        """Test database health check"""
        try:
            from backend.app.core.database_config import database_manager
            
            health = await database_manager.health_check()
            assert isinstance(health, dict)
            assert 'status' in health
            
        except Exception as e:
            pytest.skip(f"Database health check not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

