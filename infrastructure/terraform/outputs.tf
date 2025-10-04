# Output values for use in application configuration
output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "vpc_network" {
  description = "VPC Network name"
  value       = google_compute_network.validatus_vpc.name
}

# Database outputs
output "cloud_sql_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.validatus_primary.connection_name
}

output "cloud_sql_private_ip" {
  description = "Cloud SQL private IP address"
  value       = google_sql_database_instance.validatus_primary.private_ip_address
}

output "database_name" {
  description = "Database name"
  value       = google_sql_database.validatus_db.name
}

output "database_user" {
  description = "Database user name"
  value       = google_sql_user.validatus_user.name
}

# Storage outputs
output "content_bucket_name" {
  description = "Content storage bucket name"
  value       = google_storage_bucket.validatus_content.name
}

output "embeddings_bucket_name" {
  description = "Embeddings storage bucket name"
  value       = google_storage_bucket.validatus_embeddings.name
}

output "reports_bucket_name" {
  description = "Reports storage bucket name"
  value       = google_storage_bucket.validatus_reports.name
}

# Redis outputs
output "redis_host" {
  description = "Redis instance host"
  value       = google_redis_instance.validatus_cache.host
}

output "redis_port" {
  description = "Redis instance port"
  value       = google_redis_instance.validatus_cache.port
}

# Spanner outputs
output "spanner_instance_id" {
  description = "Spanner instance ID"
  value       = google_spanner_instance.validatus_analytics.name
}

output "spanner_database_id" {
  description = "Spanner database ID"
  value       = google_spanner_database.validatus_analytics_db.name
}

# Service account outputs
output "service_account_email" {
  description = "Service account email"
  value       = google_service_account.validatus_backend.email
}

# Environment configuration template
output "env_template" {
  description = "Environment configuration template"
  value = {
    GCP_PROJECT_ID              = var.project_id
    GCP_REGION                  = var.region
    CLOUD_SQL_CONNECTION_NAME   = google_sql_database_instance.validatus_primary.connection_name
    CLOUD_SQL_DATABASE          = google_sql_database.validatus_db.name
    CLOUD_SQL_USER              = google_sql_user.validatus_user.name
    CONTENT_STORAGE_BUCKET      = google_storage_bucket.validatus_content.name
    EMBEDDINGS_STORAGE_BUCKET   = google_storage_bucket.validatus_embeddings.name
    REPORTS_STORAGE_BUCKET      = google_storage_bucket.validatus_reports.name
    REDIS_HOST                  = google_redis_instance.validatus_cache.host
    REDIS_PORT                  = google_redis_instance.validatus_cache.port
    SPANNER_INSTANCE_ID         = google_spanner_instance.validatus_analytics.name
    SPANNER_DATABASE_ID         = google_spanner_database.validatus_analytics_db.name
    SERVICE_ACCOUNT_EMAIL       = google_service_account.validatus_backend.email
  }
  sensitive = true
}
