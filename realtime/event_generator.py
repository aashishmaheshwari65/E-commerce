import uuid
import random
from datetime import datetime, timezone
import pandas as pd
from typing import Dict, Any

from .config import EVENT_TYPES, EVENT_WEIGHTS, MOCK_SEARCH_QUERIES, USERS_CSV, PRODUCTS_CSV

class EventGenerator:
    """Generates synthetic e-commerce events."""
    
    def __init__(self):
        self._load_data()

    def _load_data(self):
        """Load source users and products data for sampling."""
        try:
            users_df = pd.read_csv(USERS_CSV)
            self.user_ids = users_df['user_id'].tolist()
        except FileNotFoundError:
            raise FileNotFoundError(f"Missing {USERS_CSV}. Please generate datasets first.")

        try:
            products_df = pd.read_csv(PRODUCTS_CSV)
            self.product_ids = products_df['product_id'].tolist()
            # Also extract product names for more realistic search queries
            self.product_names = products_df['product_name'].tolist() if 'product_name' in products_df.columns else []
        except FileNotFoundError:
            raise FileNotFoundError(f"Missing {PRODUCTS_CSV}. Please generate datasets first.")

    def generate_event(self) -> Dict[str, Any]:
        """Generate a single random event."""
        event_type = random.choices(EVENT_TYPES, weights=EVENT_WEIGHTS)[0]
        user_id = random.choice(self.user_ids)
        
        event = {
            "event_id": str(uuid.uuid4()),
            "user_id": int(user_id),
            "event_type": event_type,
            "product_id": None,
            "search_query": None,
            "event_timestamp": datetime.now(timezone.utc).isoformat()
        }

        if event_type == "search":
            # 50% chance to search by a real product name vs mock query
            if self.product_names and random.random() > 0.5:
                event["search_query"] = random.choice(self.product_names)
            else:
                event["search_query"] = random.choice(MOCK_SEARCH_QUERIES)
        else:
            event["product_id"] = int(random.choice(self.product_ids))

        return event
