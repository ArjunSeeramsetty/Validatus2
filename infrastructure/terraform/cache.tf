# Memorystore Redis Instance
resource "google_redis_instance" "validatus_cache" {
  name           = "validatus-cache"
  memory_size_gb = 4
  region         = var.region
  
  # Use basic tier for development, standard for production
  tier = "STANDARD_HA"  # High availability
  
  # Network configuration
  authorized_network      = google_compute_network.validatus_vpc.id
  connect_mode           = "PRIVATE_SERVICE_ACCESS"
  
  # Redis configuration
  redis_version     = "REDIS_7_0"
  display_name      = "Validatus Cache"
  reserved_ip_range = "10.1.0.0/29"
  
  redis_configs = {
    maxmemory-policy = "allkeys-lru"
    notify-keyspace-events = "Ex"
  }

  # Maintenance policy
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 3
        minutes = 0
      }
    }
  }

  # Labels
  labels = {
    environment = var.environment
    service     = "validatus"
    component   = "cache"
  }

  depends_on = [google_project_service.apis]
}
