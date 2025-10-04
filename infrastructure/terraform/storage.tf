# Cloud Storage Buckets
resource "google_storage_bucket" "validatus_content" {
  name                        = "${var.project_id}-validatus-content"
  location                   = var.region
  storage_class              = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy              = false  # Set to false in production

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

  # Versioning
  versioning {
    enabled = true
  }

  # CORS configuration
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
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

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age = 60
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

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age = 90
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
