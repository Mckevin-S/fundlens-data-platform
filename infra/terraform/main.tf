locals {
  prefix = "fundlens-${var.environment}"
  labels = { project = "fundlens", environment = var.environment }
}

# ---------- GCP : entrepôt BigQuery (cible principale) ----------
resource "google_bigquery_dataset" "raw" {
  dataset_id = "fundlens_raw_${var.environment}"
  location   = "EU"
  labels     = local.labels
}

resource "google_bigquery_dataset" "marts" {
  dataset_id = "fundlens_marts_${var.environment}"
  location   = "EU"
  labels     = local.labels
}

resource "google_storage_bucket" "landing" {
  name                        = "${local.prefix}-landing"
  location                    = "EU"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  labels                      = local.labels
  lifecycle_rule {
    condition { age = 30 }
    action { type = "Delete" }
  }
}

# ---------- AWS : archive des fichiers bruts ----------
resource "aws_s3_bucket" "raw_archive" {
  bucket = "${local.prefix}-raw-archive"
  tags   = local.labels
}

resource "aws_s3_bucket_public_access_block" "raw_archive" {
  bucket                  = aws_s3_bucket.raw_archive.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "raw_archive" {
  bucket = aws_s3_bucket.raw_archive.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

resource "aws_s3_bucket_versioning" "raw_archive" {
  bucket = aws_s3_bucket.raw_archive.id
  versioning_configuration { status = "Enabled" }
}

data "aws_iam_policy_document" "ingestion" {
  statement {
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.raw_archive.arn}/*"]
  }
}

resource "aws_iam_policy" "ingestion" {
  name   = "${local.prefix}-ingestion"
  policy = data.aws_iam_policy_document.ingestion.json
}

# ---------- Snowflake : seconde cible dbt ----------
resource "snowflake_database" "fundlens" {
  name = upper(replace(local.prefix, "-", "_"))
}

resource "snowflake_warehouse" "transform" {
  name           = "${upper(replace(local.prefix, "-", "_"))}_WH"
  warehouse_size = "XSMALL"
  auto_suspend   = 60
}

resource "snowflake_account_role" "transformer" {
  name = "${upper(replace(local.prefix, "-", "_"))}_TRANSFORMER"
}
