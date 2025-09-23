# infrastructure/terraform/gcp_validatus.tf

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "validatus-prod"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

# Provider configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "cloudsql.googleapis.com",
    "storage.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudtasks.googleapis.com",
    "pubsub.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "secretmanager.googleapis.com"
  ])
  
  project = var.project_id
  service = each.value
  
  disable_dependent_services = true
}

# Storage buckets
resource "google_storage_bucket" "topic_storage" {
  name     = "${var.project_id}-validatus-topics"
  location = var.region
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "scraping_storage" {
  name     = "${var.project_id}-validatus-scraping"
  location = var.region
  
  uniform_bucket_level_access = true
}

# Cloud SQL instance
resource "google_sql_database_instance" "validatus_db" {
  name             = "validatus-db"
  database_version = "POSTGRES_15"
  region           = var.region
  
  settings {
    tier = "db-f1-micro"  # Adjust based on needs
    
    disk_autoresize       = true
    disk_autoresize_limit = 100
    disk_size             = 20
    disk_type             = "PD_SSD"
    
    backup_configuration {
      enabled    = true
      start_time = "03:00"
    }
    
    ip_configuration {
      ipv4_enabled = false
      require_ssl  = true
    }
  }
  
  deletion_protection = true
}

resource "google_sql_database" "validatus_main" {
  name     = "validatus"
  instance = google_sql_database_instance.validatus_db.name
}

# Cloud Tasks queue
resource "google_cloud_tasks_queue" "scraping_queue" {
  name     = "url-scraping-queue"
  location = var.region
  
  rate_limits {
    max_concurrent_dispatches = 100
    max_dispatches_per_second = 10
  }
  
  retry_config {
    max_attempts = 3
    max_retry_duration = "300s"
    min_backoff = "1s"
    max_backoff = "10s"
    max_doublings = 3
  }
}

# Pub/Sub topics
resource "google_pubsub_topic" "scraping_results" {
  name = "validatus-scraping-results"
}

resource "google_pubsub_topic" "analysis_events" {
  name = "validatus-analysis-events"
}

# Cloud Run services
resource "google_cloud_run_service" "topic_manager" {
  name     = "validatus-topic-manager"
  location = var.region
  
  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/validatus-topic-manager:latest"
        
        resources {
          limits = {
            cpu    = "2"
            memory = "4Gi"
          }
        }
        
        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }
        
        env {
          name  = "CLOUD_SQL_INSTANCE"
          value = google_sql_database_instance.validatus_db.connection_name
        }
      }
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "10"
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.validatus_db.connection_name
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
}

# IAM roles
resource "google_service_account" "validatus_service" {
  account_id   = "validatus-service"
  display_name = "Validatus Service Account"
}

resource "google_project_iam_member" "validatus_permissions" {
  for_each = toset([
    "roles/storage.admin",
    "roles/cloudsql.client",
    "roles/aiplatform.user",
    "roles/cloudtasks.enqueuer",
    "roles/pubsub.publisher",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.validatus_service.email}"
}

# Outputs
output "project_id" {
  value = var.project_id
}

output "topic_storage_bucket" {
  value = google_storage_bucket.topic_storage.name
}

output "cloud_sql_connection" {
  value = google_sql_database_instance.validatus_db.connection_name
}

output "service_account_email" {
  value = google_service_account.validatus_service.email
}
