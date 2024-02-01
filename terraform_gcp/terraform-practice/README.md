# Using Terraform to Create a GCP Bucket

This project demonstrates how to create a GCP bucket using Terraform. It includes creating a service account in GCP, setting up Terraform configurations, and executing the Terraform plan to create resources in GCP.

**Prerequities**
- A GCP account
- Terraform installed
- Homebrew installed (macOS users)

## Setup and Configuration

### Creating a Service Account
1. Navigate to IAM & Admin in the GCP Console and select Service Accounts.
2. Click Create Service Account and fill in the service account details.
3. Assign the following roles to the service account:
   - Storage Admin
   - Bigquery Admin
   - Compute Admin
4. Click Done to create the service account.
5. In the Service Accounts page, find your new service account and click the three dots (menu icon) and select Manage Keys.
6. Click Add Key, then Create New Key, and select JSON as the key type.
7. Save the JSON key file in a secure location on your machine.
- an easy way is to create a file in a directory, and use `nano` command to copy the key into the file

#
### Terraform Configuration Files
[main.tf](main.tf)

```python
# Terraform block specifies the required version and providers
terraform {
  required_providers {
    google = {
      source = "hashicorp/google" # Google Cloud provider source
      version = "5.13.0" # Specifying the provider version
    }
  }
}

# Provider block configures the specified provider, in this case, Google
provider "google" {
  credentials = file(var.credentials)  # Path to the JSON credentials file
  project = var.project # GCP project ID
  region = var.region # GCP region
}

# Resource block for creating a Google Cloud Storage bucket
resource "google_storage_bucket" "terraform-demo-bucket" {
  name = var.gcs_bucket_name # Name of the bucket
  location = var.location # Bucket location
  force_destroy = true # Allows bucket deletion with objects in it

  # Lifecycle rule to manage objects within the bucket
  lifecycle_rule {
    condition {
      age = 1 # Age in days to take action
    }
    action {
      type = "AbortIncompleteMultipartUpload" # Action type
    }
  }
}

# Resource block for creating a Google BigQuery dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.bq_dataset_name # Dataset ID
  location = var.location # Dataset location
}
```
This is the main Terraform configuration file. It defines the required providers and declares the resources to be created.

#
[variables.tf](variables.tf)

```python
variable "credentials" {
  description = "My credentials"
  default     = "data/keys/my-creds.json"
}

variable "project" {
  description = "Project"
  default     = "radiant-psyche-403018"
}

variable "region" {
  description = "Region"
  default     = "us-central1"
}

variable "location" {
  description = "Project Location"
  default     = "US"
}

variable "bq_dataset_name" {
  description = "Big Query Dataset"
  default     = "demo_dataset"
}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  default     = "radiant-psyche-403018-terrabucket"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}
```
This file defines variables used in `main.tf`.

### Usage
To use this Terraform configuration:

1. Navigate to the directory containing your Terraform files.
2. Initialize Terraform with `terraform init`.
3. Apply the Terraform plan with `terraform apply` or `terraform plan` to confirm before using applying.