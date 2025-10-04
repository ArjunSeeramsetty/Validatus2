# Service Account for Backend Application
resource "google_service_account" "validatus_backend" {
  account_id   = "validatus-backend"
  display_name = "Validatus Backend Service Account"
  description  = "Service account for Validatus backend application"
  project      = var.project_id

  depends_on = [google_project_service.apis]
}

# IAM roles for the service account
resource "google_project_iam_member" "validatus_backend_roles" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/storage.objectAdmin",
    "roles/redis.editor",
    "roles/spanner.databaseUser",
    "roles/aiplatform.user",
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/cloudtrace.agent"
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.validatus_backend.email}"
}

# Create service account key
resource "google_service_account_key" "validatus_backend_key" {
  service_account_id = google_service_account.validatus_backend.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

# Store service account key in Secret Manager
resource "google_secret_manager_secret" "service_account_key" {
  secret_id = "validatus-service-account-key"
  project   = var.project_id

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "service_account_key_version" {
  secret      = google_secret_manager_secret.service_account_key.id
  secret_data = base64decode(google_service_account_key.validatus_backend_key.private_key)
}
