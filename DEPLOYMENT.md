# Deployment Guide - Skills Inventory & Gap Analysis Tool

Complete guide for running this ML clustering and ETL project locally and deploying to AWS.

---

## 📋 Prerequisites

### Required Tools
- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **AWS CLI** - [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **Terraform 1.0+** - [Download](https://www.terraform.io/downloads)
- **Git** - Already installed ✓
- **Modern Web Browser** - For viewing frontend dashboard

### AWS Account Setup
1. Create or use existing AWS account
2. Create IAM user with these permissions:
   - S3 (full)
   - Glue (full)
   - Lambda (full)
   - SageMaker (full)
   - Athena (full)
   - IAM (create roles)
   - CloudWatch Logs

3. Get Access Keys: IAM Console → Users → Security credentials → Create access key

---

## 🏠 Local Development

### 1. Setup Environment

**PowerShell (Windows):**
```powershell
# Navigate to project
cd C:\Users\danpl\projects\utilities\skills-inventory

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Bash (Linux/Mac):**
```bash
# Navigate to project
cd ~/projects/utilities/skills-inventory

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Run Tests Locally

**PowerShell (Windows):**
```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/unit/test_clustering.py -v
pytest tests/unit/test_etl_job.py -v

# View coverage report
start htmlcov/index.html
```

**Bash (Linux/Mac):**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/unit/test_clustering.py -v
pytest tests/unit/test_etl_job.py -v

# View coverage report (Linux)
xdg-open htmlcov/index.html
# Or on Mac
open htmlcov/index.html
```

### 3. Test Clustering Logic Locally

**PowerShell & Bash (same commands):**
```bash
# Test K-Means clustering with sample data
python -c "
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np

# Sample skills data
data = pd.DataFrame({
    'employee_id': ['emp_001', 'emp_002', 'emp_003', 'emp_004'],
    'python': [5, 2, 5, 1],
    'aws': [4, 1, 5, 2],
    'sql': [3, 4, 2, 5],
    'ml': [5, 1, 4, 1]
})

# Prepare features
features = data[['python', 'aws', 'sql', 'ml']]

# Perform clustering
kmeans = KMeans(n_clusters=2, random_state=42)
data['cluster'] = kmeans.fit_predict(features)

print('Clustering Results:')
print(data)
print('\nCluster Centers:')
print(kmeans.cluster_centers_)
"
```

### 4. Test Frontend Locally

**PowerShell (Windows):**
```powershell
# Start a simple local web server
cd frontend
python -m http.server 8000

# Open in browser
start http://localhost:8000

# Note: Will show "No data" until connected to AWS
```

**Bash (Linux/Mac):**
```bash
# Start a simple local web server
cd frontend
python -m http.server 8000

# Open in browser (Linux)
xdg-open http://localhost:8000
# Or on Mac
open http://localhost:8000

# Note: Will show "No data" until connected to AWS
```

### 5. Validate Data Format

**PowerShell & Bash (same commands):**
```bash
# Check sample data structure
python -c "
import csv

with open('data/skills_data.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    
print(f'Total records: {len(rows)}')
print(f'Columns: {list(rows[0].keys())}')
print(f'\nSample record:')
for key, value in rows[0].items():
    print(f'  {key}: {value}')
"
```

---

## ☁️ AWS Deployment

### Step 1: Configure AWS Credentials

**PowerShell & Bash (same commands):**
```bash
# Configure AWS CLI (one-time setup)
aws configure

# Enter when prompted:
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: us-east-1
# Default output format: json

# Verify configuration
aws sts get-caller-identity
```

### Step 2: Deploy Infrastructure with Terraform

**PowerShell & Bash (same commands):**
```bash
# Navigate to Terraform directory
cd infrastructure/terraform

# Initialize Terraform (first time only)
terraform init

# Preview changes
terraform plan

# Review the plan, then deploy
terraform apply

# Type 'yes' when prompted

# Save outputs (bucket names, website URL, etc.)
terraform output
```

**Resources Created:**
- S3 bucket for skills data and processed results
- S3 bucket for static website hosting
- AWS Glue ETL job and crawler
- Lambda function for clustering
- SageMaker training job and endpoint (optional)
- Athena database and tables
- IAM roles and policies
- CloudWatch log groups

### Step 3: Upload Skills Data

```powershell
# Get bucket name from Terraform output
$dataBucket = terraform output -raw skills_data_bucket

# Upload raw skills data
aws s3 cp ../../data/skills_data.csv s3://$dataBucket/raw/skills_data.csv

# Verify upload
aws s3 ls s3://$dataBucket/raw/
```

### Step 4: Run Glue ETL Job

```powershell
# Get Glue job name from Terraform
$gluejobName = terraform output -raw glue_job_name

# Start ETL job
aws glue start-job-run --job-name $glueJobName

# Get job run ID
$jobRunId = (aws glue get-job-runs --job-name $glueJobName --max-results 1 | ConvertFrom-Json).JobRuns[0].Id

# Monitor job status
aws glue get-job-run --job-name $glueJobName --run-id $jobRunId --query 'JobRun.JobRunState'

# View logs
Write-Host "Job running... Check CloudWatch Logs at /aws-glue/jobs/$glueJobName"
```

**What the ETL Job Does:**
1. Reads raw skills data from S3
2. Cleans and validates data
3. Transforms into analysis-ready format
4. Writes to processed/ folder in S3
5. Creates Glue Data Catalog tables

### Step 5: Run Crawler (Create Athena Tables)

**PowerShell (Windows):**
```powershell
# Get crawler name
$crawlerName = terraform output -raw glue_crawler_name

# Start crawler
aws glue start-crawler --name $crawlerName

# Wait for crawler to complete
do {
    Start-Sleep -Seconds 10
    $status = (aws glue get-crawler --name $crawlerName | ConvertFrom-Json).Crawler.State
    Write-Host "Crawler status: $status"
} while ($status -eq "RUNNING")

# Verify tables created
aws glue get-tables --database-name skills_inventory | ConvertFrom-Json | Select-Object -ExpandProperty TableList | Select-Object Name
```

**Bash (Linux/Mac):**
```bash
# Get crawler name
CRAWLER_NAME=$(terraform output -raw glue_crawler_name)

# Start crawler
aws glue start-crawler --name $CRAWLER_NAME

# Wait for crawler to complete
while true; do
    sleep 10
    STATUS=$(aws glue get-crawler --name $CRAWLER_NAME --query 'Crawler.State' --output text)
    echo "Crawler status: $STATUS"
    [[ "$STATUS" != "RUNNING" ]] && break
done

# Verify tables created
aws glue get-tables --database-name skills_inventory --query 'TableList[*].Name'
```

### Step 6: Train Clustering Model (Optional)

**PowerShell & Bash (same commands):**
```bash
# Train SageMaker K-Means model
cd ../../src/sagemaker/sagemaker
python train_clustering.py

# This will:
# 1. Load processed data from S3
# 2. Train K-Means clustering model
# 3. Save model to S3
# 4. Print cluster analysis
```

### Step 7: Deploy Frontend Dashboard

**PowerShell (Windows):**
```powershell
# Get website bucket name
$websiteBucket = terraform output -raw website_bucket

# Upload frontend files
cd ../../../frontend
aws s3 cp index.html s3://$websiteBucket/
aws s3 cp styles.css s3://$websiteBucket/
aws s3 cp app.js s3://$websiteBucket/

# Get website URL
cd ../infrastructure/terraform
$websiteUrl = terraform output -raw website_url

Write-Host "`nWebsite available at: $websiteUrl" -ForegroundColor Green

# Open in browser
start $websiteUrl
```

**Bash (Linux/Mac):**
```bash
# Get website bucket name
WEBSITE_BUCKET=$(terraform output -raw website_bucket)

# Upload frontend files
cd ../../../frontend
aws s3 cp index.html s3://$WEBSITE_BUCKET/
aws s3 cp styles.css s3://$WEBSITE_BUCKET/
aws s3 cp app.js s3://$WEBSITE_BUCKET/

# Get website URL
cd ../infrastructure/terraform
WEBSITE_URL=$(terraform output -raw website_url)

echo -e "\nWebsite available at: $WEBSITE_URL"

# Open in browser (Linux)
xdg-open $WEBSITE_URL
# Or on Mac
open $WEBSITE_URL
```

### Step 8: Test Clustering Lambda

```powershell
# Invoke clustering Lambda function
$functionName = terraform output -raw clustering_function_name

$payload = @{
    skill_categories = @("Python", "AWS", "SQL", "ML")
    threshold = 3
} | ConvertTo-Json

# Invoke function
aws lambda invoke `
    --function-name $functionName `
    --payload ($payload | Out-String) `
    response.json

# View results
Get-Content response.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

## 🧪 Testing in AWS

### Query Skills Data with Athena

```powershell
# Get Athena output bucket
$dataBucket = terraform output -raw skills_data_bucket

# Run Athena query
$queryString = "SELECT * FROM skills_inventory.employee_skills LIMIT 10"

$queryId = (aws athena start-query-execution `
    --query-string $queryString `
    --result-configuration "OutputLocation=s3://$dataBucket/athena-results/" `
    --query-execution-context "Database=skills_inventory" | ConvertFrom-Json).QueryExecutionId

# Wait for query to complete
Start-Sleep -Seconds 5

# Get results
aws athena get-query-results --query-execution-id $queryId
```

### Analyze Skills Gaps

```powershell
# Query to find skill gaps
$gapQuery = @"
SELECT 
    department,
    COUNT(DISTINCT employee_id) as employee_count,
    AVG(python_score) as avg_python,
    AVG(aws_score) as avg_aws,
    AVG(sql_score) as avg_sql
FROM skills_inventory.employee_skills
GROUP BY department
ORDER BY employee_count DESC
"@

$queryId = (aws athena start-query-execution `
    --query-string $gapQuery `
    --result-configuration "OutputLocation=s3://$dataBucket/athena-results/" `
    --query-execution-context "Database=skills_inventory" | ConvertFrom-Json).QueryExecutionId

Start-Sleep -Seconds 5
aws athena get-query-results --query-execution-id $queryId
```

### Test Frontend Visualization

```powershell
# Get website URL
$websiteUrl = terraform output -raw website_url

# Test with different parameters
start "$websiteUrl?department=Engineering"
start "$websiteUrl?skill=Python"

# Check browser console for any errors
Write-Host "Open browser DevTools (F12) to debug any issues"
```

---

## 📊 Monitoring & Troubleshooting

### Check Glue Job Status

```powershell
# List recent job runs
aws glue get-job-runs --job-name $glueJobName --max-results 5 | ConvertFrom-Json | Select-Object -ExpandProperty JobRuns | Select-Object Id, JobRunState, StartedOn, CompletedOn

# View job logs
aws logs tail /aws-glue/jobs/$glueJobName --follow --since 1h

# Check job metrics
aws glue get-job-run --job-name $glueJobName --run-id $jobRunId --query 'JobRun.{State:JobRunState,Duration:ExecutionTime,Error:ErrorMessage}'
```

### Monitor Lambda Function

```powershell
# View Lambda logs
aws logs tail /aws/lambda/$functionName --follow

# Check invocation metrics
aws cloudwatch get-metric-statistics `
    --namespace AWS/Lambda `
    --metric-name Invocations `
    --dimensions Name=FunctionName,Value=$functionName `
    --start-time (Get-Date).AddHours(-1) `
    --end-time (Get-Date) `
    --period 3600 `
    --statistics Sum
```

### Verify S3 Data

```powershell
# Check raw data
aws s3 ls s3://$dataBucket/raw/ --recursive

# Check processed data (after ETL)
aws s3 ls s3://$dataBucket/processed/ --recursive

# Check Athena query results
aws s3 ls s3://$dataBucket/athena-results/ --recursive

# Download sample processed file
aws s3 cp s3://$dataBucket/processed/part-00000.parquet ./sample.parquet
```

### Common Issues

**Issue: Glue job fails**
```powershell
# Check job logs for errors
aws logs tail /aws-glue/jobs/$glueJobName --filter-pattern "ERROR"

# Common fixes:
# 1. Verify CSV format matches expected schema
# 2. Check S3 bucket permissions
# 3. Increase Glue job timeout or DPU allocation
```

**Issue: Athena queries fail**
```powershell
# Verify crawler ran successfully
aws glue get-crawler --name $crawlerName --query 'Crawler.{State:State,LastCrawl:LastCrawl}'

# Manually run crawler
aws glue start-crawler --name $crawlerName

# Check table schema
aws glue get-table --database-name skills_inventory --name employee_skills
```

**Issue: Frontend shows no data**
```powershell
# 1. Check CORS configuration on S3 bucket
aws s3api get-bucket-cors --bucket $dataBucket

# 2. Verify Athena query results accessible
aws s3 ls s3://$dataBucket/athena-results/

# 3. Check browser console for errors
# Open DevTools (F12) and look for CORS or network errors
```

**Issue: Website not accessible**
```powershell
# Verify bucket website configuration
aws s3api get-bucket-website --bucket $websiteBucket

# Check bucket policy allows public read
aws s3api get-bucket-policy --bucket $websiteBucket

# Verify files uploaded
aws s3 ls s3://$websiteBucket/
```

---

## 📈 Advanced Queries

### Skills Gap Analysis

```sql
-- Find employees missing critical skills
SELECT 
    employee_id,
    department,
    CASE 
        WHEN python_score < 3 THEN 'Needs Python Training'
        WHEN aws_score < 3 THEN 'Needs AWS Training'
        WHEN sql_score < 3 THEN 'Needs SQL Training'
    END as recommendation
FROM skills_inventory.employee_skills
WHERE python_score < 3 OR aws_score < 3 OR sql_score < 3;
```

### Department Skills Heatmap

```sql
-- Average skills by department
SELECT 
    department,
    ROUND(AVG(python_score), 2) as python,
    ROUND(AVG(aws_score), 2) as aws,
    ROUND(AVG(sql_score), 2) as sql,
    ROUND(AVG(ml_score), 2) as ml,
    COUNT(*) as employees
FROM skills_inventory.employee_skills
GROUP BY department
ORDER BY employees DESC;
```

### Skill Clustering Analysis

```sql
-- Identify skill clusters
SELECT 
    cluster_id,
    COUNT(*) as employee_count,
    ROUND(AVG(python_score), 2) as avg_python,
    ROUND(AVG(aws_score), 2) as avg_aws,
    ROUND(AVG(sql_score), 2) as avg_sql
FROM skills_inventory.employee_skills
GROUP BY cluster_id
ORDER BY cluster_id;
```

---

## 💰 Cost Management

### Estimate Monthly Costs

**Typical Monthly Costs:**
- **S3 Storage** (<5GB): ~$0.12/month
- **Glue ETL** (1 job/day, 5 min each): ~$13/month
- **Lambda** (100 invocations/month): ~$0.02/month
- **Athena** (10GB scanned/month): ~$0.05/month
- **CloudWatch Logs**: ~$0.50/month
- **SageMaker Endpoint** (if deployed 24/7): ~$35/month

**Total: ~$14/month (without SageMaker endpoint)**
**Total with SageMaker: ~$49/month**

### Cost Optimization

**Option 1: Run Glue job on-demand only**
```powershell
# Remove schedule, run manually when needed
# Comment out schedule in infrastructure/terraform/main.tf
terraform apply
```

**Option 2: Use Athena only (skip SageMaker)**
```powershell
# Don't deploy SageMaker endpoint
# Use Athena for all analysis
# Saves ~$35/month
```

**Option 3: Use S3 Lifecycle policies**
```powershell
# Archive old data to Glacier
aws s3api put-bucket-lifecycle-configuration `
    --bucket $dataBucket `
    --lifecycle-configuration file://lifecycle-policy.json
```

---

## 🔄 Development Workflow

### Update Skills Data

```powershell
# 1. Add new data to CSV
# Edit data/skills_data.csv

# 2. Upload to S3
aws s3 cp data/skills_data.csv s3://$dataBucket/raw/skills_data_$(Get-Date -Format 'yyyyMMdd').csv

# 3. Run ETL job
aws glue start-job-run --job-name $glueJobName

# 4. Run crawler to update tables
aws glue start-crawler --name $crawlerName

# 5. Refresh frontend
start $websiteUrl
```

### Update Frontend

```powershell
# 1. Make changes to frontend files
# Edit frontend/app.js, styles.css, or index.html

# 2. Test locally
cd frontend
python -m http.server 8000
start http://localhost:8000

# 3. Deploy to S3
aws s3 sync . s3://$websiteBucket/ --exclude "*.md"

# 4. Clear browser cache and reload
start $websiteUrl
```

### Update ETL Job

```powershell
# 1. Edit ETL code
# Modify src/lambda_functions/etl_job.py

# 2. Test locally (mock PySpark context)
pytest tests/unit/test_etl_job.py

# 3. Deploy with Terraform
cd infrastructure/terraform
terraform apply -auto-approve

# 4. Test updated job
aws glue start-job-run --job-name $glueJobName
```

---

## 🗑️ Cleanup / Destroy Resources

### Delete S3 Data

```powershell
# Backup data first
$dataBucket = terraform output -raw skills_data_bucket
$websiteBucket = terraform output -raw website_bucket

aws s3 sync s3://$dataBucket ./backup/data/
aws s3 sync s3://$websiteBucket ./backup/website/

# Empty buckets
aws s3 rm s3://$dataBucket --recursive
aws s3 rm s3://$websiteBucket --recursive
```

### Destroy All Resources

```powershell
cd infrastructure/terraform

# Preview destruction
terraform plan -destroy

# Destroy everything
terraform destroy

# Type 'yes' when prompted
```

---

## 🚀 Quick Start Commands

**PowerShell (Windows):**
```powershell
# Complete local setup
cd C:\Users\danpl\projects\utilities\skills-inventory
pip install -r requirements.txt -r requirements-dev.txt
pytest

# Complete AWS deployment
aws configure
cd infrastructure/terraform
terraform init
terraform apply
$dataBucket = terraform output -raw skills_data_bucket
$websiteBucket = terraform output -raw website_bucket
$glueJobName = terraform output -raw glue_job_name
$crawlerName = terraform output -raw glue_crawler_name
aws s3 cp ../../data/skills_data.csv s3://$dataBucket/raw/skills_data.csv
aws glue start-job-run --job-name $glueJobName
Start-Sleep -Seconds 120
aws glue start-crawler --name $crawlerName
Start-Sleep -Seconds 60
cd ../../frontend
aws s3 sync . s3://$websiteBucket/ --exclude "*.md"
$websiteUrl = terraform output -raw website_url
start $websiteUrl
```

**Bash (Linux/Mac):**
```bash
# Complete local setup
cd ~/projects/utilities/skills-inventory
pip install -r requirements.txt -r requirements-dev.txt
pytest

# Complete AWS deployment
aws configure
cd infrastructure/terraform
terraform init
terraform apply
DATA_BUCKET=$(terraform output -raw skills_data_bucket)
WEBSITE_BUCKET=$(terraform output -raw website_bucket)
GLUE_JOB_NAME=$(terraform output -raw glue_job_name)
CRAWLER_NAME=$(terraform output -raw glue_crawler_name)
aws s3 cp ../../data/skills_data.csv s3://$DATA_BUCKET/raw/skills_data.csv
aws glue start-job-run --job-name $GLUE_JOB_NAME
sleep 120
aws glue start-crawler --name $CRAWLER_NAME
sleep 60
cd ../../frontend
aws s3 sync . s3://$WEBSITE_BUCKET/ --exclude "*.md"
cd ../infrastructure/terraform
WEBSITE_URL=$(terraform output -raw website_url)
# Linux
xdg-open $WEBSITE_URL
# Or Mac
open $WEBSITE_URL
```

---

## 📚 Additional Resources

- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/)
- [Amazon Athena Documentation](https://docs.aws.amazon.com/athena/)
- [D3.js Documentation](https://d3js.org/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Project README](README.md)

---

## 🆘 Getting Help

**Local Development**: Check [tests/unit/](tests/unit/) for test examples

**ETL Issues**: Review [src/lambda_functions/etl_job.py](src/lambda_functions/etl_job.py)

**Frontend Issues**: Check browser DevTools console, review [frontend/app.js](frontend/app.js)

**Infrastructure Issues**: Check [infrastructure/terraform/](infrastructure/terraform/) configs

**CI/CD Issues**: Check [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)
