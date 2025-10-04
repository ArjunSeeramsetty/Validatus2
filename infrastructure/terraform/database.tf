# Cloud SQL PostgreSQL Instance
resource "google_sql_database_instance" "validatus_primary" {
  name                = "validatus-primary"
  database_version    = "POSTGRES_15"
  region             = var.region
  deletion_protection = false  # Set to true in production

  settings {
    tier                  = "db-custom-2-7680"  # 2 vCPU, 7.5GB RAM
    availability_type     = "REGIONAL"          # High availability
    disk_type            = "PD_SSD"
    disk_size            = 100
    disk_autoresize      = true
    disk_autoresize_limit = 500

    # Backup configuration
    backup_configuration {
      enabled                        = true
      start_time                    = "03:00"
      location                      = var.region
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 30
      }
    }

    # IP configuration for private networking
    ip_configuration {
      ipv4_enabled                                  = false
      private_network                              = google_compute_network.validatus_vpc.id
      enable_private_path_for_google_cloud_services = true
    }

    # Database flags for optimization
    database_flags {
      name  = "max_connections"
      value = "100"
    }
    
    database_flags {
      name  = "shared_preload_libraries"
      value = "pg_stat_statements"
    }

    # Maintenance window
    maintenance_window {
      day          = 7  # Sunday
      hour         = 3  # 3 AM
      update_track = "stable"
    }
  }

  depends_on = [
    google_project_service.apis,
    google_service_networking_connection.private_vpc_connection
  ]
}

# Create the main database
resource "google_sql_database" "validatus_db" {
  name     = "validatus"
  instance = google_sql_database_instance.validatus_primary.name
  project  = var.project_id
}

# Create database user
resource "google_sql_user" "validatus_user" {
  name     = "validatus_app"
  instance = google_sql_database_instance.validatus_primary.name
  password = random_password.db_password.result
  project  = var.project_id
}

# Generate random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store database password in Secret Manager
resource "google_secret_manager_secret" "db_password" {
  secret_id = "cloud-sql-password"
  project   = var.project_id

  replication {
    automatic = true
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "db_password_version" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

# Private service connection for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "private-ip-address"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.validatus_vpc.id
  project       = var.project_id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.validatus_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]

  depends_on = [google_project_service.apis]
}
