output "bigquery_datasets" {
  value = [google_bigquery_dataset.raw.dataset_id, google_bigquery_dataset.marts.dataset_id]
}

output "raw_archive_bucket" {
  value = aws_s3_bucket.raw_archive.bucket
}

output "snowflake_database" {
  value = snowflake_database.fundlens.name
}
