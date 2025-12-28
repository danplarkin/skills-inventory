# Main Terraform configuration for Skills Inventory & Gap Analysis
# Provisions S3, Glue, Lambda, SageMaker, and Athena

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 bucket for skills data and results
resource "aws_s3_bucket" "skills_data" {
  bucket = "${var.project_name}-data-${var.environment}"
  
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# S3 bucket for static website
resource "aws_s3_bucket" "skills_website" {
  bucket = "${var.project_name}-website-${var.environment}"
  
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# Website configuration
resource "aws_s3_bucket_website_configuration" "skills_website" {
  bucket = aws_s3_bucket.skills_website.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
}

# Public read policy for website bucket
resource "aws_s3_bucket_policy" "website_policy" {
  bucket = aws_s3_bucket.skills_website.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.skills_website.arn}/*"
      }
    ]
  })
}

# Glue database
resource "aws_glue_catalog_database" "skills_db" {
  name = "${var.project_name}_database_${var.environment}"
}

# Glue crawler
resource "aws_glue_crawler" "skills_crawler" {
  database_name = aws_glue_catalog_database.skills_db.name
  name          = "${var.project_name}-crawler-${var.environment}"
  role          = aws_iam_role.glue_role.arn

  s3_target {
    path = "s3://${aws_s3_bucket.skills_data.bucket}/processed/"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# Glue ETL job
resource "aws_glue_job" "skills_etl" {
  name     = "${var.project_name}-etl-${var.environment}"
  role_arn = aws_iam_role.glue_role.arn

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.skills_data.bucket}/scripts/etl_job.py"
    python_version  = "3"
  }

  default_arguments = {
    "--TempDir"           = "s3://${aws_s3_bucket.skills_data.bucket}/temp/"
    "--job-language"      = "python"
    "--enable-spark-ui"   = "true"
    "--spark-event-logs-path" = "s3://${aws_s3_bucket.skills_data.bucket}/logs/"
  }

  max_retries       = 0
  timeout           = 60
  glue_version      = "4.0"
  number_of_workers = 2
  worker_type       = "G.1X"

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# Lambda function for clustering
resource "aws_lambda_function" "clustering" {
  filename         = "../lambda/clustering.zip"
  function_name    = "${var.project_name}-clustering-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "handler.lambda_handler"
  runtime         = "python3.11"
  timeout         = 900
  memory_size     = 1024

  environment {
    variables = {
      SAGEMAKER_ROLE   = aws_iam_role.sagemaker_role.arn
      S3_BUCKET        = aws_s3_bucket.skills_data.bucket
      GLUE_DATABASE    = aws_glue_catalog_database.skills_db.name
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# Athena workgroup
resource "aws_athena_workgroup" "skills_workgroup" {
  name = "${var.project_name}-workgroup-${var.environment}"

  configuration {
    result_configuration {
      output_location = "s3://${aws_s3_bucket.skills_data.bucket}/athena-results/"
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
