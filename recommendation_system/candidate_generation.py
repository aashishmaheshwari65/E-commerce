import numpy as np
import pandas as pd

def get_candidates(user_id, interactions_df, products_df, top_n=50):
    """
    Retrieve candidate products for a given user from their interaction history
    and product catalog.
    """
    u_str = str(user_id)
    if interactions_df.empty or products_df.empty:
        return []

    user_df = interactions_df[interactions_df["user_id"].astype(str) == u_str]
    user_interacted_pids = set(user_df["product_id"].astype(str).tolist())

    all_pids = products_df["product_id"].astype(str).tolist()
    candidates = [p for p in all_pids if p not in user_interacted_pids]
    return candidates[:top_n]
