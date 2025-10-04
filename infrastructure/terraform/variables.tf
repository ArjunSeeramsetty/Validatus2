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
  default     = "production"
  
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
}

variable "db_max_connections" {
  description = "Maximum database connections"
  type        = number
  default     = 100
}

# Redis Configuration
variable "redis_memory_size" {
  description = "Redis memory size in GB"
  type        = number
  default     = 4
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
  default     = false
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

# Tags
variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "Validatus"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
