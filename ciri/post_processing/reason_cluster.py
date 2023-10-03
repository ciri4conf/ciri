from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from collections import Counter
import random

def get_dominant_reason(reasons):
    # Calculate the TF-IDF scores
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(reasons)
    
    # Cluster the reasons using DBSCAN
    # These parameters can be tuned based on the nature of the data
    dbscan = DBSCAN(eps=0.3, min_samples=2, metric='cosine').fit(X)
    labels = dbscan.labels_
    # If all reasons are considered as noise by DBSCAN, just return a random reason
    if len(set(labels)) == 1 and -1 in labels:
        return random.choice(reasons)
    
    # Find the dominant cluster
    counter = Counter(labels)
    if -1 in counter:  # Removing the noise label
        del counter[-1]
    dominant_cluster_label = counter.most_common(1)[0][0]
    
    # Get a random reason from the dominant cluster
    dominant_cluster_reasons = [reason for idx, reason in enumerate(reasons) if labels[idx] == dominant_cluster_label]
    return random.choice(dominant_cluster_reasons)
