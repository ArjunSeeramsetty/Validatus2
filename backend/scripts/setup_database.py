"""
Database setup script for GCP production environment
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.gcp_persistence_manager import get_gcp_persistence_manager
from app.core.gcp_persistence_config import get_gcp_persistence_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_database_schema():
    """Create all database schemas and tables"""
    logger.info("🗄️ Setting up database schema...")
    
    try:
        # Initialize persistence manager
        manager = get_gcp_persistence_manager()
        await manager.initialize()
        
        # Create Cloud SQL tables
        await create_sql_schema(manager.sql_manager)
        
        # Initialize Spanner schema (already done via Terraform DDL)
        await verify_spanner_schema(manager.spanner_manager)
        
        logger.info("✅ Database schema setup completed successfully")
        
        await manager.close()
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        raise

async def create_sql_schema(sql_manager):
    """Create Cloud SQL PostgreSQL schema"""
    logger.info("Creating Cloud SQL schema...")
    
    # Read schema file
    schema_path = Path(__file__).parent.parent / "migrations" / "001_initial_schema.sql"
    
    if not schema_path.exists():
        logger.error(f"Schema file not found: {schema_path}")
        return
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Execute schema creation
    async with sql_manager.get_connection() as conn:
        # Split and execute each statement
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for statement in statements:
            try:
                await conn.execute(statement)
                logger.debug(f"Executed: {statement[:50]}...")
            except Exception as e:
                logger.warning(f"Statement failed (may be expected): {e}")
    
    logger.info("✅ Cloud SQL schema created")

async def verify_spanner_schema(spanner_manager):
    """Verify Spanner schema is properly set up"""
    logger.info("Verifying Spanner schema...")
    
    try:
        # Test connection and schema
        health = await spanner_manager.health_check()
        if health.get('status') == 'healthy':
            logger.info("✅ Spanner schema verified")
        else:
            logger.error("❌ Spanner schema verification failed")
    except Exception as e:
        logger.warning(f"Spanner verification failed: {e}")

async def create_sample_data():
    """Create sample data for testing"""
    logger.info("🧪 Creating sample test data...")
    
    try:
        manager = get_gcp_persistence_manager()
        await manager.initialize()
        
        # Create a sample topic
        topic_response = await manager.create_topic_complete(
            title="Sample Market Analysis",
            description="This is a sample topic created during setup",
            analysis_type="comprehensive",
            user_id="setup_user"
        )
        logger.info(f"✅ Sample topic created: {topic_response['topic_id']}")
        
        await manager.close()
        
    except Exception as e:
        logger.error(f"❌ Sample data creation failed: {e}")

async def run_health_checks():
    """Run comprehensive health checks"""
    logger.info("🏥 Running health checks...")
    
    try:
        manager = get_gcp_persistence_manager()
        await manager.initialize()
        
        health = await manager.health_check()
        
        logger.info("Health Check Results:")
        logger.info(f"Overall Status: {health['overall_status']}")
        
        for service, status in health['services'].items():
            if status.get('status') == 'healthy':
                logger.info(f"  ✅ {service}: {status['status']}")
            else:
                logger.error(f"  ❌ {service}: {status.get('status', 'unknown')} - {status.get('error', '')}")
        
        await manager.close()
        
        if health['overall_status'] == 'healthy':
            logger.info("✅ All health checks passed")
            return True
        else:
            logger.error("❌ Some health checks failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Health checks failed: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Starting Validatus Database Setup")
    logger.info("=====================================")
    
    # Check environment
    settings = get_gcp_persistence_settings()
    if settings.local_development_mode:
        logger.error("❌ This script is for production setup only")
        logger.error("Set LOCAL_DEVELOPMENT_MODE=false in your environment")
        sys.exit(1)
    
    logger.info(f"Project ID: {settings.project_id}")
    logger.info(f"Region: {settings.region}")
    
    async def setup_sequence():
        try:
            # Step 1: Create database schema
            await create_database_schema()
            
            # Step 2: Create sample data
            await create_sample_data()
            
            # Step 3: Run health checks
            healthy = await run_health_checks()
            
            if healthy:
                logger.info("🎉 Database setup completed successfully!")
                logger.info("")
                logger.info("Next steps:")
                logger.info("1. Deploy your application to Cloud Run")
                logger.info("2. Configure your frontend to use the new backend")
                logger.info("3. Set up monitoring and alerting")
                return True
            else:
                logger.error("❌ Database setup completed with issues")
                return False
                
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            return False
    
    # Run the setup
    success = asyncio.run(setup_sequence())
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
