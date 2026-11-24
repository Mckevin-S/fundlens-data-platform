variable "gcp_project" {
  type        = string
  description = "Projet GCP hébergeant BigQuery et le bucket de transit"
}

variable "gcp_region" {
  type    = string
  default = "europe-west9"
}

variable "aws_region" {
  type    = string
  default = "eu-west-3"
}

variable "environment" {
  type    = string
  default = "dev"
  validation {
    condition     = contains(["dev", "recette", "prod"], var.environment)
    error_message = "environment doit valoir dev, recette ou prod."
  }
}
