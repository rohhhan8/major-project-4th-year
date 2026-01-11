"""
train_model.py - Offline Model Trainer for Student Clustering

This script trains a K-Means clustering model to classify students into
"Learner Profiles" based on their quiz performance.

What this does:
1. Generates synthetic (fake) student data since we don't have real data yet
2. Trains a KMeans model to find 3 natural clusters
3. Saves the model so it can be used in production

Clusters represent:
- Cluster 0: "Struggling" - Low scores, taking long time
- Cluster 1: "High Achiever" - High scores, reasonable time  
- Cluster 2: "Rushed" - Quick answers, often lower accuracy

Author: ML Engineering Team
Run: python train_model.py
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

NUM_STUDENTS = 5000  # Number of synthetic records to generate (IEEE-scale validation)
NUM_CLUSTERS = 3    # Learner profile categories
MODEL_PATH = "./student_clustering_model.pkl"
RANDOM_SEED = 42    # For reproducibility

# ============================================================================
# STEP A: GENERATE SYNTHETIC DATA
# ============================================================================

def generate_synthetic_data(n_students: int = 500) -> pd.DataFrame:
    """
    Generate realistic fake student quiz data.
    
    We create 3 types of students to make the data somewhat realistic:
    
    1. Struggling Students (~40%):
       - Low scores (20-55)
       - Take longer time (60-120 seconds per question)
       - They're trying but finding it difficult
    
    2. High Achievers (~35%):
       - High scores (70-100)
       - Average time (30-70 seconds per question)
       - They understand the material well
    
    3. Rushed Students (~25%):
       - Variable scores (30-70) - often lower due to rushing
       - Very quick responses (10-35 seconds per question)
       - They're speeding through without careful thought
    
    Args:
        n_students: Number of fake student records to create
        
    Returns:
        DataFrame with columns: ['avg_score', 'avg_time_per_question']
    """
    
    np.random.seed(RANDOM_SEED)
    
    # Calculate how many of each type
    n_struggling = int(n_students * 0.40)   # 40% struggling
    n_achievers = int(n_students * 0.35)     # 35% high achievers
    n_rushed = n_students - n_struggling - n_achievers  # 25% rushed
    
    print(f"Generating {n_students} synthetic students...")
    print(f"  - Struggling: {n_struggling}")
    print(f"  - High Achievers: {n_achievers}")
    print(f"  - Rushed: {n_rushed}")
    
    # ----- Type 1: Struggling Students -----
    # Low scores, high time (they're trying but struggling)
    struggling_scores = np.random.uniform(20, 55, n_struggling)
    struggling_times = np.random.uniform(60, 120, n_struggling)
    
    # ----- Type 2: High Achievers -----
    # High scores, moderate time (efficient and accurate)
    achiever_scores = np.random.uniform(70, 100, n_achievers)
    achiever_times = np.random.uniform(30, 70, n_achievers)
    
    # ----- Type 3: Rushed Students -----
    # Variable scores, very low time (too fast, making mistakes)
    rushed_scores = np.random.uniform(30, 70, n_rushed)
    rushed_times = np.random.uniform(10, 35, n_rushed)
    
    # Combine all data
    all_scores = np.concatenate([struggling_scores, achiever_scores, rushed_scores])
    all_times = np.concatenate([struggling_times, achiever_times, rushed_times])
    
    # Create DataFrame
    df = pd.DataFrame({
        'avg_score': all_scores,
        'avg_time_per_question': all_times
    })
    
    # Shuffle the data (so clusters aren't in order)
    df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
    
    print(f"\nData Statistics:")
    print(df.describe())
    
    return df


# ============================================================================
# STEP B: TRAIN CLUSTERING MODEL
# ============================================================================

def train_clustering_model(df: pd.DataFrame, n_clusters: int = 3):
    """
    Train a KMeans clustering model on the student data.
    
    KMeans will automatically find 3 groups of similar students.
    We then look at the cluster centers to figure out what each cluster means.
    
    Args:
        df: DataFrame with student performance data
        n_clusters: Number of clusters (learner profiles)
        
    Returns:
        Tuple of (trained_model, scaler, cluster_labels_mapping)
    """
    
    print(f"\n{'='*60}")
    print("Training KMeans Clustering Model")
    print('='*60)
    
    # Get the features we want to cluster on
    X = df[['avg_score', 'avg_time_per_question']].values
    
    # ----- IMPORTANT: Scale the data -----
    # KMeans works better when features are on the same scale
    # Score is 0-100, Time is 10-120, so we need to normalize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    print("Data scaled using StandardScaler")
    
    # ----- Train KMeans -----
    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=RANDOM_SEED,
        n_init=10  # Run 10 times with different starting points
    )
    kmeans.fit(X_scaled)
    print(f"KMeans trained with {n_clusters} clusters")
    
    # ----- Analyze Cluster Centers -----
    # Transform centers back to original scale for interpretation
    centers_original = scaler.inverse_transform(kmeans.cluster_centers_)
    
    print("\nCluster Centers (original scale):")
    print("-" * 50)
    for i, center in enumerate(centers_original):
        avg_score, avg_time = center
        print(f"  Cluster {i}: Score={avg_score:.1f}, Time={avg_time:.1f}s")
    
    # ----- Assign Meaningful Labels -----
    # We'll map cluster numbers to labels based on their characteristics
    # Sort clusters by score to assign labels consistently
    cluster_info = []
    for i, center in enumerate(centers_original):
        cluster_info.append({
            'cluster_id': i,
            'avg_score': center[0],
            'avg_time': center[1]
        })
    
    # Create label mapping based on characteristics
    labels_mapping = {}
    for info in cluster_info:
        cid = info['cluster_id']
        score = info['avg_score']
        time = info['avg_time']
        
        if score >= 65:  # High score
            labels_mapping[cid] = "High Achiever"
        elif time <= 40:  # Low time (rushed)
            labels_mapping[cid] = "Rushed"
        else:  # Low score, high time
            labels_mapping[cid] = "Struggling"
    
    print("\nCluster Label Mapping:")
    for cid, label in labels_mapping.items():
        print(f"  Cluster {cid} -> '{label}'")
    
    return kmeans, scaler, labels_mapping


# ============================================================================
# STEP C: SAVE THE MODEL
# ============================================================================

def save_model(model, scaler, labels_mapping, filepath: str):
    """
    Save all components needed for prediction:
    - The trained KMeans model
    - The scaler (to transform new data the same way)
    - The cluster labels mapping
    
    We save everything as one dictionary in a .pkl file.
    
    Args:
        model: Trained KMeans model
        scaler: Fitted StandardScaler
        labels_mapping: Dictionary mapping cluster IDs to labels
        filepath: Where to save the file
    """
    
    model_package = {
        'model': model,
        'scaler': scaler,
        'labels_mapping': labels_mapping,
        'version': '1.0.0',
        'features': ['avg_score', 'avg_time_per_question']
    }
    
    joblib.dump(model_package, filepath)
    
    file_size = os.path.getsize(filepath) / 1024  # KB
    print(f"\nModel saved to: {filepath} ({file_size:.1f} KB)")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Student Clustering Model - Offline Training Pipeline")
    print("=" * 60)
    
    # Step A: Generate synthetic data
    student_data = generate_synthetic_data(NUM_STUDENTS)
    
    # Step B: Train the clustering model
    model, scaler, labels = train_clustering_model(student_data, NUM_CLUSTERS)
    
    # Step C: Save everything
    save_model(model, scaler, labels, MODEL_PATH)
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print(f"Next step: Use '{MODEL_PATH}' in quiz_engine.py for predictions")
