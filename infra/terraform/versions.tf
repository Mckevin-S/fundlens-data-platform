terraform {
  required_version = ">= 1.8"
  required_providers {
    google    = { source = "hashicorp/google", version = "~> 6.10" }
    aws       = { source = "hashicorp/aws", version = "~> 5.75" }
    snowflake = { source = "Snowflake-Labs/snowflake", version = "~> 0.98" }
  }
  # État distant : décommenter et renseigner le bucket avant un usage partagé
  # backend "gcs" { bucket = "fundlens-tfstate" prefix = "infra" }
}

provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}

provider "aws" {
  region = var.aws_region
}

# Identifiants Snowflake fournis par les variables d'environnement SNOWFLAKE_* (jamais dans le code)
provider "snowflake" {}
