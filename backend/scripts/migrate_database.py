#!/usr/bin/env python3
"""
Database Migration Script for Validatus Platform
Handles database schema migrations using Alembic
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from alembic.config import Config
from alembic import command
from app.core.gcp_persistence_config import get_gcp_persistence_settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_database_url():
    """Get database URL from environment or GCP settings."""
    # Try environment variable first
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        logger.info("Using DATABASE_URL from environment")
        return database_url
    
    # Fall back to GCP settings
    try:
        settings = get_gcp_persistence_settings()
        database_url = settings.get_cloud_sql_url()
        logger.info("Using DATABASE_URL from GCP settings")
        return database_url
    except Exception as e:
        logger.error(f"Failed to get database URL from GCP settings: {e}")
        raise


def run_migrations():
    """Run database migrations using Alembic."""
    try:
        # Get database URL
        database_url = get_database_url()
        
        # Set up Alembic configuration
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        logger.info("Starting database migration...")
        
        # Run the migration
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Database migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        raise


def create_migration(message: str):
    """Create a new migration file."""
    try:
        alembic_cfg = Config("alembic.ini")
        
        logger.info(f"Creating new migration: {message}")
        
        # Create the migration
        command.revision(alembic_cfg, message=message, autogenerate=True)
        
        logger.info("Migration file created successfully!")
        
    except Exception as e:
        logger.error(f"Failed to create migration: {e}")
        raise


def show_current_revision():
    """Show the current database revision."""
    try:
        alembic_cfg = Config("alembic.ini")
        
        # Get current revision
        command.current(alembic_cfg)
        
    except Exception as e:
        logger.error(f"Failed to get current revision: {e}")
        raise


def show_migration_history():
    """Show migration history."""
    try:
        alembic_cfg = Config("alembic.ini")
        
        # Show history
        command.history(alembic_cfg)
        
    except Exception as e:
        logger.error(f"Failed to show migration history: {e}")
        raise


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python migrate_database.py <command> [args...]")
        print("Commands:")
        print("  migrate              - Run all pending migrations")
        print("  create <message>     - Create a new migration")
        print("  current              - Show current revision")
        print("  history              - Show migration history")
        sys.exit(1)
    
    command_name = sys.argv[1]
    
    try:
        if command_name == "migrate":
            run_migrations()
        elif command_name == "create":
            if len(sys.argv) < 3:
                print("Usage: python migrate_database.py create <message>")
                sys.exit(1)
            message = sys.argv[2]
            create_migration(message)
        elif command_name == "current":
            show_current_revision()
        elif command_name == "history":
            show_migration_history()
        else:
            print(f"Unknown command: {command_name}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
