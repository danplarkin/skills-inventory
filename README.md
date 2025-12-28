# Skills Inventory & Gap Analysis Tool

An intelligent HR analytics platform that identifies skill clusters, gaps, and provides strategic insights using AWS Glue, SageMaker, and Athena.

## Architecture Diagram

```
Skills Data → S3 → AWS Glue → Lambda → SageMaker (Clustering) → Athena → S3 Static Site
```

## Tech Stack

- **AWS Services:** S3, Glue, Lambda, SageMaker, Athena
- **IaC:** Terraform or AWS CDK
- **Language:** Python for Lambda & ML
- **Frontend:** Static HTML/CSS/JS hosted on S3

## Project Overview

This project demonstrates expertise in:
- ETL pipeline design with AWS Glue
- ML clustering algorithms (K-Means, DBSCAN)
- Data lake architecture
- Static site hosting
- Skills gap analysis
- HR strategic planning

## Step-by-Step Implementation

1. **Deploy infrastructure** with Terraform/CDK (S3, Glue, Lambda, SageMaker, Athena via IaC)
2. **Glue ETL job** cleans HR skills dataset
3. **Lambda triggers** clustering job in SageMaker
4. **Store results** in S3 and query via Athena
5. **Build static site** hosted on S3 showing skill clusters and gaps
6. **Automate everything** with IaC

## Repository Structure

```
/skills-gap-analysis
├── terraform/       # IaC scripts
├── lambda/          # ETL + clustering code
├── sagemaker/       # ML scripts
├── frontend/        # Static site files
├── data/            # Sample skills data
└── README.md        # Setup guide
```

## Getting Started

### Prerequisites

- AWS Account with Glue and SageMaker permissions
- Terraform or AWS CDK installed
- Python 3.9+
- AWS CLI configured
- Basic understanding of clustering algorithms

### Installation

```bash
# Clone the repository
git clone https://github.com/danplarkin/skills-inventory.git
cd skills-inventory

# Deploy infrastructure
cd terraform
terraform init
terraform plan
terraform apply

# Upload sample skills data
aws s3 cp data/skills_data.csv s3://your-bucket-name/raw/

# Run Glue ETL job
aws glue start-job-run --job-name skills-etl-job

# Query results with Athena
aws athena start-query-execution \
  --query-string "SELECT * FROM skill_clusters LIMIT 10" \
  --result-configuration OutputLocation=s3://your-results-bucket/
```

## Features

- **Skill Clustering:** Automatically groups similar skills
- **Gap Analysis:** Identifies missing critical skills
- **Interactive Dashboard:** Visual representation of skills landscape
- **Athena Queries:** Ad-hoc analysis capabilities
- **Scalable ETL:** Handles large datasets efficiently
- **Static Site Hosting:** Fast, cost-effective frontend

## Analysis Capabilities

1. **Skill Distribution:** See which skills are most common
2. **Cluster Visualization:** Identify natural skill groupings
3. **Gap Identification:** Find underrepresented critical skills
4. **Team Composition:** Analyze skills by department/team
5. **Trend Analysis:** Track skill evolution over time

## Frontend Features

The static site provides:
- Interactive skill cluster visualization (D3.js)
- Gap analysis dashboard
- Department-level breakdowns
- Export capabilities (CSV, PDF)
- Search and filter functionality

## Data Schema

### Input Data (skills_data.csv)
```csv
employee_id,name,department,skill,proficiency,years_experience
emp_001,John Doe,Engineering,Python,Expert,5
emp_001,John Doe,Engineering,AWS,Intermediate,3
```

### Output Data (Athena Table)
```sql
skill_cluster_id, skill_name, cluster_label, employee_count, avg_proficiency
```

## ML Model Details

- **Algorithm:** K-Means Clustering
- **Features:** Skill embeddings using TF-IDF
- **Clusters:** Automatically determined using elbow method
- **Evaluation:** Silhouette score for cluster quality

## Future Enhancements

- Learning path recommendations
- Skill market demand integration
- Team formation suggestions
- Integration with learning management systems (LMS)
- Real-time skill tracking via API

## License

MIT

---

**Project Status:** In Development  
**Author:** Dan Larkin  
**Date:** December 2025
