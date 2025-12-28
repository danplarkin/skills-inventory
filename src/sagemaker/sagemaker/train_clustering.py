"""
SageMaker training script for skills clustering model.
Uses K-Means and DBSCAN for skill grouping.
"""

import pandas as pd
import numpy as np
import argparse
import os
import joblib
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score


def load_data(data_path):
    """Load skills data."""
    return pd.read_csv(data_path)


def create_skill_features(df):
    """Create features for clustering."""
    # Aggregate by skill
    skill_agg = df.groupby('skill').agg({
        'employee_id': 'count',
        'proficiency_score': 'mean',
        'years_experience': 'mean'
    }).reset_index()
    
    skill_agg.columns = ['skill', 'employee_count', 'avg_proficiency', 'avg_experience']
    
    # Create TF-IDF features from skill names
    tfidf = TfidfVectorizer(max_features=50)
    skill_text_features = tfidf.fit_transform(skill_agg['skill'])
    
    # Combine numeric and text features
    numeric_features = skill_agg[['employee_count', 'avg_proficiency', 'avg_experience']].values
    
    return skill_agg, numeric_features, skill_text_features, tfidf


def train_kmeans(features, n_clusters_range=range(3, 10)):
    """Train K-Means clustering model."""
    best_k = 5
    best_score = -1
    best_model = None
    
    for k in n_clusters_range:
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(features)
        
        if len(set(labels)) > 1:  # Need at least 2 clusters for silhouette
            score = silhouette_score(features, labels)
            print(f"K={k}, Silhouette Score: {score:.4f}")
            
            if score > best_score:
                best_score = score
                best_k = k
                best_model = model
    
    print(f"\nBest K: {best_k} with score: {best_score:.4f}")
    return best_model, best_k, best_score


def save_model(model, scaler, tfidf, output_path):
    """Save trained model and preprocessors."""
    os.makedirs(output_path, exist_ok=True)
    
    joblib.dump(model, os.path.join(output_path, 'clustering_model.pkl'))
    joblib.dump(scaler, os.path.join(output_path, 'scaler.pkl'))
    joblib.dump(tfidf, os.path.join(output_path, 'tfidf.pkl'))
    
    print(f"Model artifacts saved to {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-path', type=str, default='../data/skills_data.csv')
    parser.add_argument('--output-path', type=str, default='./model_artifacts')
    args = parser.parse_args()
    
    print("Loading data...")
    df = load_data(args.data_path)
    
    print("Creating features...")
    skill_data, numeric_features, text_features, tfidf = create_skill_features(df)
    
    print("Scaling features...")
    scaler = StandardScaler()
    numeric_scaled = scaler.fit_transform(numeric_features)
    
    # Combine features
    # For simplicity, using only numeric features
    # In production, you might want to combine with text features
    features = numeric_scaled
    
    print("Training clustering model...")
    model, best_k, score = train_kmeans(features)
    
    print("Saving model...")
    save_model(model, scaler, tfidf, args.output_path)
    
    print("Training complete!")
