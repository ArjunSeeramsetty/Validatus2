<#
.SYNOPSIS
    Set up complete database infrastructure for Validatus
.DESCRIPTION
    This script creates all database resources and sets up the schema
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    
    [string]$Region = "us-central1",
    [string]$DatabaseInstanceName = "validatus-primary",
    [string]$DatabaseName = "validatus",
    [string]$DatabaseUser = "validatus_app",
    [switch]$SkipInfrastructure,
    [switch]$CreateMinimalSetup
)

Write-Host "🗄️ Setting up Validatus Database Infrastructure..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

$ErrorActionPreference = "Stop"

# Function to check if database instance exists
function Test-DatabaseInstance {
    param([string]$InstanceName)
    
    try {
        $instance = gcloud sql instances describe $InstanceName --project=$ProjectId 2>$null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

# Function to create minimal Cloud SQL instance
function New-MinimalCloudSQL {
    Write-Host "🔧 Creating minimal Cloud SQL instance..." -ForegroundColor Cyan
    
    # Generate separate secure passwords (no special characters for URL safety)
    $postgresPassword = -join ((1..20) | ForEach-Object { Get-Random -InputObject ([char[]]'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') })
    $appPassword = -join ((1..20) | ForEach-Object { Get-Random -InputObject ([char[]]'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') })
    
    Write-Host "Generated separate passwords for postgres and application user" -ForegroundColor Green
    
    # Create Cloud SQL instance
    $createArgs = @(
        "sql", "instances", "create", $DatabaseInstanceName,
        "--database-version=POSTGRES_15",
        "--tier=db-f1-micro",
        "--region=$Region",
        "--storage-type=SSD",
        "--storage-size=10GB",
        "--storage-auto-increase",
        "--backup-start-time=03:00",
        "--maintenance-release-channel=production",
        "--maintenance-window-day=SUN",
        "--maintenance-window-hour=4",
        "--project=$ProjectId"
    )
    
    Write-Host "Creating Cloud SQL instance (this may take 5-10 minutes)..." -ForegroundColor Yellow
    & gcloud @createArgs
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create Cloud SQL instance"
    }
    
    # Set postgres superuser password
    Write-Host "Setting postgres superuser password..." -ForegroundColor Cyan
    gcloud sql users set-password postgres --instance=$DatabaseInstanceName --password=$postgresPassword --project=$ProjectId
    
    # Create application user with separate password
    Write-Host "Creating application user with separate password..." -ForegroundColor Cyan
    gcloud sql users create $DatabaseUser --instance=$DatabaseInstanceName --password=$appPassword --project=$ProjectId
    
    # Create database
    Write-Host "Creating application database..." -ForegroundColor Cyan
    gcloud sql databases create $DatabaseName --instance=$DatabaseInstanceName --project=$ProjectId
    
    # Store passwords securely in Secret Manager
    Write-Host "Storing passwords in Secret Manager..." -ForegroundColor Cyan
    
    # Store postgres password
    try {
        $tempFile = [System.IO.Path]::GetTempFileName()
        $postgresPassword | Out-File -FilePath $tempFile -Encoding utf8 -NoNewline
        gcloud secrets create cloud-sql-postgres-password --data-file=$tempFile --project=$ProjectId 2>$null
        if ($LASTEXITCODE -ne 0) {
            # Secret might already exist, update it
            gcloud secrets versions add cloud-sql-postgres-password --data-file=$tempFile --project=$ProjectId
        }
        Remove-Item $tempFile -ErrorAction SilentlyContinue
        Write-Host "✅ Postgres password stored securely" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to store postgres password: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Store application password
    try {
        $tempFile = [System.IO.Path]::GetTempFileName()
        $appPassword | Out-File -FilePath $tempFile -Encoding utf8 -NoNewline
        gcloud secrets create cloud-sql-app-password --data-file=$tempFile --project=$ProjectId 2>$null
        if ($LASTEXITCODE -ne 0) {
            # Secret might already exist, update it
            gcloud secrets versions add cloud-sql-app-password --data-file=$tempFile --project=$ProjectId
        }
        Remove-Item $tempFile -ErrorAction SilentlyContinue
        Write-Host "✅ Application password stored securely" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to store application password: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host "✅ Cloud SQL instance created successfully with separate passwords" -ForegroundColor Green
    return @{
        PostgresPassword = $postgresPassword
        AppPassword = $appPassword
    }
}

# Function to setup database schema
function Initialize-DatabaseSchema {
    param([string]$Password)
    
    Write-Host "📝 Setting up database schema..." -ForegroundColor Cyan
    
    # Create schema SQL
    $schemaSQL = @'
-- Validatus Database Schema
-- Initial setup for minimal functionality

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Topics table (main entity)
CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL,
    topic VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'CREATED',
    analysis_type VARCHAR(50) NOT NULL DEFAULT 'comprehensive',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    search_queries TEXT[],
    initial_urls TEXT[],
    
    CONSTRAINT chk_topic_status CHECK (status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'ARCHIVED'))
);

-- URLs table for tracking URL collection and processing
CREATE TABLE IF NOT EXISTS topic_urls (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,
    source VARCHAR(100) NOT NULL DEFAULT 'unknown',
    status VARCHAR(50) DEFAULT 'pending',
    quality_score DECIMAL(3,2) CHECK (quality_score >= 0 AND quality_score <= 1),
    scraped_at TIMESTAMP WITH TIME ZONE,
    content_preview TEXT,
    title TEXT,
    word_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(session_id, url),
    CONSTRAINT chk_url_status CHECK (status IN ('pending', 'processing', 'scraped', 'failed', 'skipped')),
    FOREIGN KEY (session_id) REFERENCES topics(session_id) ON DELETE CASCADE
);

-- Simple analysis results table
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    analysis_id VARCHAR(50) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Core scoring results (normalized 0.0-1.0 with validation)
    overall_score DECIMAL(5,4) CHECK (overall_score >= 0 AND overall_score <= 1),
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- Detailed results as JSON
    results_data JSONB DEFAULT '{}'::jsonb,
    processing_metadata JSONB DEFAULT '{}'::jsonb,
    
    UNIQUE(session_id, analysis_id),
    FOREIGN KEY (session_id) REFERENCES topics(session_id) ON DELETE CASCADE
);

-- User activity tracking
CREATE TABLE IF NOT EXISTS user_activity (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    activity_data JSONB DEFAULT '{}'::jsonb,
    session_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_topics_user_id ON topics(user_id);
CREATE INDEX IF NOT EXISTS idx_topics_status ON topics(status);
CREATE INDEX IF NOT EXISTS idx_topics_created_at ON topics(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_topic_urls_session_id ON topic_urls(session_id);
CREATE INDEX IF NOT EXISTS idx_topic_urls_status ON topic_urls(status);
CREATE INDEX IF NOT EXISTS idx_analysis_results_session_id ON analysis_results(session_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity(user_id);

-- Create trigger for updating updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to topics table
DROP TRIGGER IF EXISTS update_topics_updated_at ON topics;
CREATE TRIGGER update_topics_updated_at BEFORE UPDATE ON topics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant minimal necessary permissions to application user
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO validatus_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO validatus_app;
GRANT USAGE ON SCHEMA public TO validatus_app;

-- Insert sample data for testing
INSERT INTO topics (session_id, topic, description, user_id, search_queries, initial_urls) VALUES 
('sample_topic_001', 'Sample Market Analysis', 'This is a sample topic for testing the database setup', 'setup_user', ARRAY['market analysis', 'business intelligence'], ARRAY['https://example.com/market-research'])
ON CONFLICT (session_id) DO NOTHING;

INSERT INTO topic_urls (session_id, url, source, status) VALUES 
('sample_topic_001', 'https://example.com/market-research', 'initial', 'pending'),
('sample_topic_001', 'https://example.com/industry-trends', 'search', 'pending')
ON CONFLICT (session_id, url) DO NOTHING;
'@
    
    # Save schema to temporary file
    $tempSchemaFile = [System.IO.Path]::GetTempFileName() + ".sql"
    $schemaSQL | Out-File -FilePath $tempSchemaFile -Encoding utf8
    
    try {
        # Execute schema using gcloud sql connect
        Write-Host "Executing schema creation..." -ForegroundColor Cyan
        
        # Use psql through gcloud sql connect
        $env:PGPASSWORD = $Password
        Get-Content $tempSchemaFile | gcloud sql connect $DatabaseInstanceName --user=$DatabaseUser --database=$DatabaseName --quiet
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Database schema created successfully" -ForegroundColor Green
        } else {
            throw "Failed to execute schema creation"
        }
    } finally {
        # Clean up temp file
        Remove-Item $tempSchemaFile -ErrorAction SilentlyContinue
        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    }
}

# Function to create Redis cache
function New-RedisCache {
    Write-Host "🔧 Setting up Redis cache..." -ForegroundColor Cyan
    
    # Check if Redis instance exists
    $redisExists = gcloud redis instances describe validatus-cache --region=$Region --project=$ProjectId 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Creating Redis instance..." -ForegroundColor Cyan
        
        gcloud redis instances create validatus-cache `
            --size=1 `
            --region=$Region `
            --redis-version=redis_7_0 `
            --project=$ProjectId
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Redis instance created successfully" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Failed to create Redis instance (optional component)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "✅ Redis instance already exists" -ForegroundColor Green
    }
}

# Function to update environment configuration
function Update-EnvironmentConfig {
    param([string]$Password)
    
    Write-Host "📝 Updating environment configuration..." -ForegroundColor Cyan
    
    # Get connection name
    $connectionName = gcloud sql instances describe $DatabaseInstanceName --format="value(connectionName)" --project=$ProjectId
    
    # Get Redis host if exists
    $redisHost = gcloud redis instances describe validatus-cache --region=$Region --format="value(host)" --project=$ProjectId 2>$null
    if ($LASTEXITCODE -ne 0) {
        $redisHost = "localhost"  # Fallback
    }
    
    # Create environment configuration
    $envContent = @"
# Validatus Production Environment Configuration
# Generated on: $(Get-Date)

# GCP Project Configuration
GCP_PROJECT_ID=$ProjectId
GCP_REGION=$Region
GCP_ZONE=${Region}-a
ENVIRONMENT=production

# Application URLs (update with your actual URLs)
FRONTEND_URL=https://validatus-frontend-ssivkqhvhq-uc.a.run.app
BACKEND_URL=https://validatus-backend-ssivkqhvhq-uc.a.run.app

# Database Configuration
DATABASE_URL=postgresql+asyncpg://${DatabaseUser}:${Password}@/${DatabaseName}?host=/cloudsql/${connectionName}
CLOUD_SQL_CONNECTION_NAME=$connectionName
CLOUD_SQL_DATABASE=$DatabaseName
CLOUD_SQL_USER=$DatabaseUser
CLOUD_SQL_PASSWORD_SECRET=cloud-sql-password

# Redis Configuration (if available)
REDIS_HOST=$redisHost
REDIS_PORT=6379

# Application Configuration
LOCAL_DEVELOPMENT_MODE=false
USE_IAM_AUTH=true
MAX_CONCURRENT_OPERATIONS=50
CONNECTION_POOL_SIZE=10
QUERY_TIMEOUT_SECONDS=30

# Storage Configuration (using default buckets for now)
CONTENT_STORAGE_BUCKET=${ProjectId}-content
EMBEDDINGS_STORAGE_BUCKET=${ProjectId}-embeddings
REPORTS_STORAGE_BUCKET=${ProjectId}-reports

# Feature Flags
ENABLE_CACHING=true
ENABLE_MONITORING=true
ENABLE_VECTOR_SEARCH=false
ENABLE_SPANNER_ANALYTICS=false

# CORS Configuration
ALLOWED_ORIGINS=https://validatus-frontend-ssivkqhvhq-uc.a.run.app,https://validatus-backend-ssivkqhvhq-uc.a.run.app

# Logging
LOG_LEVEL=INFO
"@

    $envPath = ".env.production"
    $envContent | Out-File -FilePath $envPath -Encoding utf8
    
    Write-Host "✅ Environment configuration saved to .env.production" -ForegroundColor Green
}

# Function to test database connection
function Test-DatabaseConnection {
    param([string]$Password)
    
    Write-Host "🧪 Testing database connection..." -ForegroundColor Cyan
    
    try {
        # Test connection and basic query
        $env:PGPASSWORD = $Password
        $result = gcloud sql connect $DatabaseInstanceName --user=$DatabaseUser --database=$DatabaseName --quiet --command="SELECT COUNT(*) FROM topics;"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Database connection test successful" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Database connection test failed" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Database connection test failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    } finally {
        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    }
}

# Main execution
try {
    Write-Host "Project ID: $ProjectId" -ForegroundColor White
    Write-Host "Region: $Region" -ForegroundColor White
    Write-Host "Database Instance: $DatabaseInstanceName" -ForegroundColor White
    Write-Host ""
    
    # Step 1: Enable required APIs
    Write-Host "📋 Step 1: Enabling required APIs..." -ForegroundColor Cyan
    $apis = @("sqladmin.googleapis.com", "redis.googleapis.com", "secretmanager.googleapis.com")
    foreach ($api in $apis) {
        Write-Host "Enabling $api..." -ForegroundColor Gray
        gcloud services enable $api --project=$ProjectId
    }
    Write-Host "✅ APIs enabled" -ForegroundColor Green
    Write-Host ""
    
    # Step 2: Create database infrastructure
    $password = $null
    if (-not $SkipInfrastructure) {
        Write-Host "📋 Step 2: Creating database infrastructure..." -ForegroundColor Cyan
        
        if (Test-DatabaseInstance $DatabaseInstanceName) {
            Write-Host "✅ Cloud SQL instance already exists" -ForegroundColor Green
            
            # Get existing password from Secret Manager
            try {
                $password = (gcloud secrets versions access latest --secret="cloud-sql-password" --project=$ProjectId).Trim()
                Write-Host "✅ Retrieved existing database password" -ForegroundColor Green
            } catch {
                Write-Host "❌ Failed to retrieve password from Secret Manager" -ForegroundColor Red
                throw "Please ensure the cloud-sql-password secret exists or recreate the database"
            }
        } else {
            $password = New-MinimalCloudSQL
        }
        
        Write-Host ""
    } else {
        # Retrieve password from Secret Manager when skipping infrastructure
        Write-Host "⚠️ Skipping infrastructure creation, retrieving existing password..." -ForegroundColor Yellow
        try {
            $password = (gcloud secrets versions access latest --secret="cloud-sql-password" --project=$ProjectId).Trim()
        } catch {
            throw "Cannot proceed without password. Ensure cloud-sql-password secret exists or remove -SkipInfrastructure flag."
        }
    }
    
    # Step 3: Setup database schema
    Write-Host "📋 Step 3: Setting up database schema..." -ForegroundColor Cyan
    Initialize-DatabaseSchema -Password $password
    Write-Host ""
    
    # Step 4: Setup Redis (optional)
    if ($CreateMinimalSetup) {
        Write-Host "📋 Step 4: Setting up Redis cache..." -ForegroundColor Cyan
        New-RedisCache
        Write-Host ""
    }
    
    # Step 5: Update environment configuration
    Write-Host "📋 Step 5: Updating environment configuration..." -ForegroundColor Cyan
    Update-EnvironmentConfig -Password $password
    Write-Host ""
    
    # Step 6: Test database connection
    Write-Host "📋 Step 6: Testing database connection..." -ForegroundColor Cyan
    $connectionSuccessful = Test-DatabaseConnection -Password $password
    Write-Host ""
    
    # Success summary
    Write-Host "🎉 Database setup completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Setup Summary:" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan
    Write-Host "✅ Cloud SQL instance: $DatabaseInstanceName" -ForegroundColor White
    Write-Host "✅ Database: $DatabaseName" -ForegroundColor White
    Write-Host "✅ User: $DatabaseUser" -ForegroundColor White
    Write-Host "✅ Schema: Created with sample data" -ForegroundColor White
    Write-Host "✅ Environment: .env.production updated" -ForegroundColor White
    
    if ($CreateMinimalSetup) {
        Write-Host "✅ Redis cache: Available" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Update your application configuration with .env.production" -ForegroundColor White
    Write-Host "2. Redeploy your backend with database connectivity" -ForegroundColor White
    Write-Host "3. Test the complete application workflow" -ForegroundColor White
    Write-Host ""
    
    if (-not $connectionSuccessful) {
        Write-Host "⚠️ Note: Database connection test failed. Please check the configuration." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Database setup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}
