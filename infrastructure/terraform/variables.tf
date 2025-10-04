# Project Configuration
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  # No default - must be explicitly set to prevent accidental production changes
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

# Database Configuration
variable "db_instance_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-custom-2-7680"
}

variable "db_disk_size" {
  description = "Database disk size in GB"
  type        = number
  default     = 100
  
  validation {
    condition     = var.db_disk_size >= 10
    error_message = "Database disk size must be at least 10 GB."
  }
}

variable "db_max_connections" {
  description = "Maximum database connections"
  type        = number
  default     = 100
  
  validation {
    condition     = var.db_max_connections > 0
    error_message = "Maximum database connections must be greater than 0."
  }
}

# Redis Configuration
variable "redis_memory_size" {
  description = "Redis memory size in GB"
  type        = number
  default     = 4
  
  validation {
    condition     = var.redis_memory_size >= 1
    error_message = "Redis memory size must be at least 1 GB."
  }
}

variable "redis_tier" {
  description = "Redis instance tier"
  type        = string
  default     = "STANDARD_HA"
  
  validation {
    condition     = contains(["BASIC", "STANDARD_HA"], var.redis_tier)
    error_message = "Redis tier must be BASIC or STANDARD_HA."
  }
}

# Spanner Configuration
variable "spanner_processing_units" {
  description = "Spanner processing units"
  type        = number
  default     = 100
  
  validation {
    condition     = var.spanner_processing_units >= 100 && var.spanner_processing_units % 100 == 0
    error_message = "Spanner processing units must be at least 100 and in multiples of 100."
  }
}

# Storage Configuration
variable "enable_bucket_versioning" {
  description = "Enable versioning for storage buckets"
  type        = bool
  default     = true
}

variable "bucket_lifecycle_enabled" {
  description = "Enable lifecycle management for buckets"
  type        = bool
  default     = true
}

# Security Configuration
variable "deletion_protection" {
  description = "Enable deletion protection for critical resources"
  type        = bool
  default     = true  # Safer default to prevent accidental deletion
}

variable "enable_backup" {
  description = "Enable backup for Cloud SQL"
  type        = bool
  default     = true
}

# Cost Optimization
variable "enable_cost_optimization" {
  description = "Enable cost optimization features"
  type        = bool
  default     = true
}

# Deployment Configuration
variable "deployment_target" {
  description = "Deployment target platform"
  type        = string
  default     = "cloud_run"
  
  validation {
    condition     = contains(["cloud_run", "gke", "compute_engine"], var.deployment_target)
    error_message = "Deployment target must be one of: cloud_run, gke, compute_engine."
  }
}

# Kubernetes Configuration (for GKE deployments)
variable "k8s_namespace" {
  description = "Kubernetes namespace for the application"
  type        = string
  default     = "default"
}

variable "k8s_service_account" {
  description = "Kubernetes service account name"
  type        = string
  default     = "validatus-backend"
}

# Tags
variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project   = "Validatus"
    ManagedBy = "terraform"
  }
  # Note: Environment tag should be added dynamically using merge(var.tags, { Environment = var.environment })
}
