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

# Workload Identity Configuration (for GKE deployments)
# This allows Kubernetes service accounts to authenticate as GCP service accounts
# without requiring service account key files

# Enable Workload Identity on the service account
resource "google_service_account_iam_member" "workload_identity_user" {
  service_account_id = google_service_account.validatus_backend.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[${var.k8s_namespace}/${var.k8s_service_account}]"
  
  # Only create this binding if deploying to GKE
  count = var.deployment_target == "gke" ? 1 : 0
}

# Allow the service account to be used by Cloud Run (automatic)
# No additional configuration needed for Cloud Run deployments
