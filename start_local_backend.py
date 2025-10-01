#!/usr/bin/env python3
"""
Local Backend Startup Script for Validatus2
===========================================

This script starts the Validatus2 backend in local development mode
with optimized settings for testing the 5 core tasks.
"""

import os
import sys
import uvicorn
from pathlib import Path

def setup_local_environment():
    """Setup local development environment variables"""
    
    # Set local development mode
    os.environ["LOCAL_DEVELOPMENT_MODE"] = "true"
    os.environ["ENVIRONMENT"] = "development"
    
    # Set GCP project (required for structure, but not used in local mode)
    os.environ["GCP_PROJECT_ID"] = "validatus-local"
    os.environ["GCLOUD_PROJECT"] = "validatus-local"
    os.environ["GCP_REGION"] = "us-central1"
    
    # Disable GCP authentication for local development
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
    
    # CORS settings for local frontend
    os.environ["ALLOWED_ORIGINS"] = '["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000", "http://127.0.0.1:8000"]'
    
    # Local storage paths
    os.environ["LOCAL_DATA_PATH"] = "./local_data"
    os.environ["LOCAL_VECTOR_STORE_PATH"] = "./local_data/vector_stores"
    os.environ["LOCAL_SCRAPED_CONTENT_PATH"] = "./local_data/scraped_content"
    
    # Performance settings for local testing
    os.environ["MAX_CONCURRENT_REQUESTS"] = "10"
    os.environ["SCRAPING_DELAY"] = "0.2"
    os.environ["MIN_CONTENT_QUALITY"] = "0.3"
    
    # Suppress verbose logging for cleaner output
    os.environ["GRPC_ALTS_SKIP_HANDSHAKE"] = "true"
    os.environ["GRPC_VERBOSITY"] = "ERROR"
    
    # Disable warnings
    os.environ["PYTHONWARNINGS"] = "ignore"
    
    print("🔧 Local development environment configured")

def create_local_directories():
    """Create necessary local directories"""
    directories = [
        "./local_data",
        "./local_data/vector_stores",
        "./local_data/scraped_content",
        "./local_data/topics",
        "./local_data/sessions"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("📁 Local directories created")

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        sys.exit(1)

def main():
    """Main function to start the backend"""
    print("🚀 Starting Validatus2 Backend in Local Development Mode")
    print("=" * 60)
    
    # Setup environment
    setup_local_environment()
    create_local_directories()
    check_dependencies()
    
    # Change to backend directory if needed
    backend_dir = Path(__file__).parent / "backend"
    if backend_dir.exists():
        os.chdir(backend_dir)
        print(f"📂 Changed to backend directory: {backend_dir}")
    
    print("\n🌐 Server Configuration:")
    print("   Host: 0.0.0.0")
    print("   Port: 8000")
    print("   Mode: Development (with auto-reload)")
    print("   API Docs: http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/health")
    
    print("\n📋 Available Test Endpoints:")
    print("   • POST /api/v3/sequential-analysis/topics/{topic_id}/analysis/create")
    print("   • POST /api/v3/sequential-analysis/analysis/{session_id}/stage1/start")
    print("   • POST /api/v3/sequential-analysis/analysis/{session_id}/stage2/start")
    print("   • GET  /api/v3/pergola/market-intelligence")
    print("   • GET  /api/v3/pergola-intelligence/search")
    
    print("\n🧪 Test Scripts Available:")
    print("   • python test_pergola_workflow.py")
    print("   • python test_individual_tasks.py <task>")
    
    print("\n" + "=" * 60)
    print("🚀 Starting server...")
    print("=" * 60)
    
    try:
        # Start the server
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
