"""
tests/customer_segmentation/test_clustering.py

Tests KMeans clustering execution, random state reproducibility, and cluster profiling.
"""

import pytest
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


@pytest.mark.unit
@pytest.mark.ml
def test_kmeans_deterministic_clustering(sample_customer_features):
    features = sample_customer_features[["recency_days", "frequency", "monetary_value"]]
    scaled = StandardScaler().fit_transform(features)

    kmeans1 = KMeans(n_clusters=2, random_state=42, n_init=10)
    labels1 = kmeans1.fit_predict(scaled)

    kmeans2 = KMeans(n_clusters=2, random_state=42, n_init=10)
    labels2 = kmeans2.fit_predict(scaled)

    # Identical seed must produce identical cluster assignments
    assert np.array_equal(labels1, labels2)
    assert len(set(labels1)) == 2


@pytest.mark.unit
@pytest.mark.ml
def test_cluster_profiling(sample_customer_features):
    df = sample_customer_features.copy()
    features = df[["recency_days", "frequency", "monetary_value"]]
    scaled = StandardScaler().fit_transform(features)

    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    df["cluster_id"] = kmeans.fit_predict(scaled)

    profiles = df.groupby("cluster_id").agg({
        "recency_days": "mean",
        "frequency": "mean",
        "monetary_value": "mean",
        "customer_key": "count",
    }).rename(columns={"customer_key": "customer_count"})

    assert len(profiles) == 2
    assert profiles["customer_count"].sum() == len(sample_customer_features)
