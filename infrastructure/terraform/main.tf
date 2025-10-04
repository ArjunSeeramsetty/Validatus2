# Configure the Google Cloud Provider
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.84.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 4.84.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

# Configure the Google Cloud Provider
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Variables
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
  description = "Environment name"
  type        = string
  default     = "production"
}

# Data sources
data "google_project" "project" {
  project_id = var.project_id
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "compute.googleapis.com",
    "sqladmin.googleapis.com",
    "storage-api.googleapis.com",
    "firestore.googleapis.com",
    "redis.googleapis.com",
    "spanner.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudtasks.googleapis.com",
    "pubsub.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "servicenetworking.googleapis.com"
  ])

  project = var.project_id
  service = each.key

  disable_dependent_services = false
  disable_on_destroy         = false
}

# Create VPC Network
resource "google_compute_network" "validatus_vpc" {
  name                    = "validatus-vpc"
  auto_create_subnetworks = false
  project                 = var.project_id

  depends_on = [google_project_service.apis]
}

# Create subnet
resource "google_compute_subnetwork" "validatus_subnet" {
  name          = "validatus-subnet"
  network       = google_compute_network.validatus_vpc.name
  ip_cidr_range = "10.0.0.0/16"
  region        = var.region
  project       = var.project_id

  # Enable private Google access
  private_ip_google_access = true
}

# Create Cloud NAT for outbound internet access
resource "google_compute_router" "validatus_router" {
  name    = "validatus-router"
  region  = var.region
  network = google_compute_network.validatus_vpc.name
  project = var.project_id
}

resource "google_compute_router_nat" "validatus_nat" {
  name   = "validatus-nat"
  router = google_compute_router.validatus_router.name
  region = var.region

  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}
