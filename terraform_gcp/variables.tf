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