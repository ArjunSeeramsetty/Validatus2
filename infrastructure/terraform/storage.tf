# Cloud Storage Buckets
resource "google_storage_bucket" "validatus_content" {
  name                        = "${var.project_id}-validatus-content"
  location                   = var.region
  storage_class              = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy              = false  # Set to false in production

  labels = {
    managed_by  = "terraform"
    environment = var.environment
    service     = "validatus"
    component   = "content_storage"
  }

  # Lifecycle management for cost optimization
  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age = 30
    }
  }

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
    condition {
      age = 90
    }
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 2555  # 7 years
    }
  }

  # Lifecycle rule for noncurrent versions
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      num_newer_versions = 5  # Keep only 5 most recent versions
      days_since_noncurrent_time = 30  # Delete versions older than 30 days
    }
  }

  # Versioning
  versioning {
    enabled = true
  }

  # CORS configuration - restricted for security
  cors {
    origin          = ["https://validatus.arjuncode.com", "https://app.validatus.arjuncode.com"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["Content-Type", "Content-Length", "ETag"]
    max_age_seconds = 3600
  }

  depends_on = [google_project_service.apis]
}

resource "google_storage_bucket" "validatus_embeddings" {
  name                        = "${var.project_id}-validatus-embeddings"
  location                   = var.region
  storage_class              = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy              = false

  labels = {
    managed_by  = "terraform"
    environment = var.environment
    service     = "validatus"
    component   = "embeddings_storage"
  }

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age = 60
    }
  }

  # Lifecycle rule for noncurrent versions
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      num_newer_versions = 3  # Keep only 3 most recent versions
      days_since_noncurrent_time = 30  # Delete versions older than 30 days
    }
  }

  versioning {
    enabled = true
  }

  depends_on = [google_project_service.apis]
}

resource "google_storage_bucket" "validatus_reports" {
  name                        = "${var.project_id}-validatus-reports"
  location                   = var.region
  storage_class              = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy              = false

  labels = {
    managed_by  = "terraform"
    environment = var.environment
    service     = "validatus"
    component   = "reports_storage"
  }

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age = 90
    }
  }

  # Lifecycle rule for noncurrent versions
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      num_newer_versions = 5  # Keep only 5 most recent versions
      days_since_noncurrent_time = 60  # Delete versions older than 60 days
    }
  }

  versioning {
    enabled = true
  }

  depends_on = [google_project_service.apis]
}

# Grant access to Cloud Run service
resource "google_storage_bucket_iam_member" "validatus_content_access" {
  bucket = google_storage_bucket.validatus_content.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.validatus_backend.email}"
}

resource "google_storage_bucket_iam_member" "validatus_embeddings_access" {
  bucket = google_storage_bucket.validatus_embeddings.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.validatus_backend.email}"
}

resource "google_storage_bucket_iam_member" "validatus_reports_access" {
  bucket = google_storage_bucket.validatus_reports.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.validatus_backend.email}"
}
