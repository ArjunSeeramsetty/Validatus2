# Terraform variables for Validatus GCP project
# This file contains the project-specific configuration

# GCP Project Configuration
project_id = "validatus-prod"
region     = "us-central1"
zone       = "us-central1-a"
environment = "prod"

# Project-specific naming
project_name = "Validatus"
project_description = "AI-powered strategic analysis platform"

# Resource naming conventions
resource_prefix = "validatus"
storage_bucket_prefix = "validatus"

# Database configuration
db_instance_name = "validatus-db"
db_name = "validatus"
db_user = "validatus_user"

# Networking
vpc_name = "validatus-vpc"
subnet_name = "validatus-subnet"

# Monitoring and logging
enable_monitoring = true
enable_logging = true
log_retention_days = 30

# Security
enable_vpc_native = true
enable_private_ip = true
enable_ssl = true
