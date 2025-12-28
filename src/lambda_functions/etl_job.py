"""
AWS Glue ETL job for processing skills data.
Cleans and transforms raw skills data.
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, when, trim, upper, regexp_replace

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'S3_BUCKET'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read raw skills data from S3
input_path = f"s3://{args['S3_BUCKET']}/raw/skills_data.csv"
df = spark.read.option("header", "true").csv(input_path)

# Data cleaning
df_clean = df \
    .withColumn("skill", trim(upper(col("skill")))) \
    .withColumn("department", trim(col("department"))) \
    .withColumn("proficiency", trim(upper(col("proficiency")))) \
    .filter(col("skill").isNotNull()) \
    .filter(col("employee_id").isNotNull())

# Convert proficiency to numeric score
proficiency_mapping = {
    'BEGINNER': 1,
    'INTERMEDIATE': 2,
    'ADVANCED': 3,
    'EXPERT': 4
}

df_clean = df_clean.withColumn(
    "proficiency_score",
    when(col("proficiency") == "BEGINNER", 1)
    .when(col("proficiency") == "INTERMEDIATE", 2)
    .when(col("proficiency") == "ADVANCED", 3)
    .when(col("proficiency") == "EXPERT", 4)
    .otherwise(2)  # Default to intermediate
)

# Convert years_experience to integer
df_clean = df_clean.withColumn(
    "years_experience",
    col("years_experience").cast("integer")
)

# Remove duplicates
df_clean = df_clean.dropDuplicates(['employee_id', 'skill'])

# Write processed data back to S3
output_path = f"s3://{args['S3_BUCKET']}/processed/"
df_clean.write.mode("overwrite").parquet(output_path)

# Create Glue table
glueContext.write_dynamic_frame.from_options(
    frame=DynamicFrame.fromDF(df_clean, glueContext, "df_clean"),
    connection_type="s3",
    connection_options={"path": output_path},
    format="parquet",
    transformation_ctx="datasink"
)

print(f"ETL job completed. Processed {df_clean.count()} records.")
job.commit()
