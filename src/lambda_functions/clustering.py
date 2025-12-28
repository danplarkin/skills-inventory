"""
Lambda function for skills clustering using SageMaker.
Triggered after Glue ETL completes.
"""

import json
import boto3
import os
from datetime import datetime
import pandas as pd
from io import StringIO

# Initialize AWS clients
s3_client = boto3.client('s3')
athena_client = boto3.client('athena')
sagemaker_client = boto3.client('sagemaker')

# Environment variables
S3_BUCKET = os.environ['S3_BUCKET']
GLUE_DATABASE = os.environ['GLUE_DATABASE']
SAGEMAKER_ROLE = os.environ['SAGEMAKER_ROLE']


def lambda_handler(event, context):
    """
    Main Lambda handler for skills clustering.
    
    Args:
        event: Trigger event (can be S3 or scheduled)
        context: Lambda context
    
    Returns:
        dict: Response with clustering results
    """
    try:
        print("Starting skills clustering process...")
        
        # Query skills data from Athena
        skills_data = query_skills_from_athena()
        
        # Prepare data for clustering
        prepared_data = prepare_clustering_data(skills_data)
        
        # Run clustering analysis
        clusters = perform_clustering(prepared_data)
        
        # Store results back to S3
        store_clustering_results(clusters)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Clustering completed successfully',
                'num_clusters': len(set(clusters['cluster_labels'])),
                'num_skills': len(clusters['skills'])
            })
        }
        
    except Exception as e:
        print(f"Error in clustering: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def query_skills_from_athena():
    """Query processed skills data from Athena."""
    query = f"""
    SELECT 
        skill,
        COUNT(DISTINCT employee_id) as employee_count,
        AVG(proficiency_score) as avg_proficiency,
        AVG(years_experience) as avg_experience
    FROM skills_data
    GROUP BY skill
    """
    
    # Start query execution
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': GLUE_DATABASE},
        ResultConfiguration={
            'OutputLocation': f's3://{S3_BUCKET}/athena-results/'
        }
    )
    
    query_execution_id = response['QueryExecutionId']
    
    # Wait for query to complete
    while True:
        status = athena_client.get_query_execution(
            QueryExecutionId=query_execution_id
        )
        state = status['QueryExecution']['Status']['State']
        
        if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
    
    if state != 'SUCCEEDED':
        raise Exception(f"Athena query failed: {state}")
    
    # Get results
    results = athena_client.get_query_results(
        QueryExecutionId=query_execution_id
    )
    
    # Parse results into DataFrame
    data = []
    for row in results['ResultSet']['Rows'][1:]:  # Skip header
        data.append([col.get('VarCharValue', '') for col in row['Data']])
    
    df = pd.DataFrame(data, columns=['skill', 'employee_count', 'avg_proficiency', 'avg_experience'])
    
    # Convert to numeric
    df['employee_count'] = pd.to_numeric(df['employee_count'])
    df['avg_proficiency'] = pd.to_numeric(df['avg_proficiency'])
    df['avg_experience'] = pd.to_numeric(df['avg_experience'])
    
    return df


def prepare_clustering_data(df):
    """Prepare data for clustering."""
    from sklearn.preprocessing import StandardScaler
    
    # Select features for clustering
    features = ['employee_count', 'avg_proficiency', 'avg_experience']
    X = df[features].values
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return {
        'features': X_scaled,
        'skills': df['skill'].tolist(),
        'original_data': df
    }


def perform_clustering(data):
    """Perform K-Means clustering."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    
    X = data['features']
    
    # Determine optimal number of clusters using elbow method
    best_k = 5  # Default
    best_score = -1
    
    for k in range(3, 8):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        score = silhouette_score(X, labels)
        
        if score > best_score:
            best_score = score
            best_k = k
    
    # Final clustering with best K
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X)
    
    # Add cluster labels to data
    result_df = data['original_data'].copy()
    result_df['cluster_id'] = cluster_labels
    
    # Calculate cluster statistics
    cluster_stats = result_df.groupby('cluster_id').agg({
        'skill': 'count',
        'employee_count': 'sum',
        'avg_proficiency': 'mean',
        'avg_experience': 'mean'
    }).reset_index()
    
    cluster_stats.columns = ['cluster_id', 'num_skills', 'total_employees', 
                             'avg_cluster_proficiency', 'avg_cluster_experience']
    
    return {
        'skills': result_df,
        'cluster_stats': cluster_stats,
        'cluster_labels': cluster_labels,
        'silhouette_score': best_score
    }


def store_clustering_results(clusters):
    """Store clustering results to S3."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Store detailed results
    skills_csv = clusters['skills'].to_csv(index=False)
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=f'results/skill_clusters_{timestamp}.csv',
        Body=skills_csv
    )
    
    # Store cluster statistics
    stats_csv = clusters['cluster_stats'].to_csv(index=False)
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=f'results/cluster_stats_{timestamp}.csv',
        Body=stats_csv
    )
    
    # Store summary
    summary = {
        'timestamp': timestamp,
        'num_clusters': len(clusters['cluster_stats']),
        'num_skills': len(clusters['skills']),
        'silhouette_score': float(clusters['silhouette_score'])
    }
    
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=f'results/clustering_summary_{timestamp}.json',
        Body=json.dumps(summary, indent=2)
    )
    
    print(f"Clustering results stored with timestamp: {timestamp}")
