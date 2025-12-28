# Terraform outputs

output "data_bucket_name" {
  description = "Name of the S3 bucket for skills data"
  value       = aws_s3_bucket.skills_data.id
}

output "website_bucket_name" {
  description = "Name of the S3 bucket for static website"
  value       = aws_s3_bucket.skills_website.id
}

output "website_url" {
  description = "URL of the static website"
  value       = aws_s3_bucket_website_configuration.skills_website.website_endpoint
}

output "glue_database_name" {
  description = "Name of the Glue database"
  value       = aws_glue_catalog_database.skills_db.name
}

output "athena_workgroup" {
  description = "Name of the Athena workgroup"
  value       = aws_athena_workgroup.skills_workgroup.name
}
