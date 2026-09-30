import time
import pandas as pd
from datetime import datetime
from collections import defaultdict
from typing import Dict, Any, List

class StreamProcessor:
    def __init__(self, products_df: pd.DataFrame, trend_window_minutes: int = 60):
        # Product catalog for revenue lookup
        self.product_prices = {}
        if not products_df.empty:
            # Calculate discounted price properly if applicable
            for _, row in products_df.iterrows():
                pid = row['product_id']
                price = row.get('price', 0.0)
                discount = row.get('discount_percent', 0.0)
                # Apply discount
                actual_price = price * (1 - (discount / 100.0))
                self.product_prices[pid] = actual_price

        self.trend_window_minutes = trend_window_minutes
        
        # Cumulative Metrics
        self.total_events = 0
        self.total_views = 0
        self.total_searches = 0
        self.total_carts = 0
        self.total_purchases = 0
        self.total_revenue = 0.0
        
        # Product rankings
        self.product_views = defaultdict(int)
        self.product_purchases = defaultdict(int)

        # Time-based tracking
        # Active users mapping: user_id -> latest_timestamp (Unix seconds)
        self.active_users: Dict[int, float] = {}
        
        # Trends: minute_string -> metrics_dict
        self.trends = defaultdict(lambda: {
            "product_view": 0,
            "search": 0,
            "add_to_cart": 0,
            "purchase": 0,
            "revenue": 0.0,
            "active_users": set()
        })
        
        self.start_time = time.time()

    def _parse_timestamp(self, iso_ts: str) -> float:
        try:
            return datetime.fromisoformat(iso_ts.replace('Z', '+00:00')).timestamp()
        except ValueError:
            return time.time()

    def process_event(self, event: Dict[str, Any]):
        self.total_events += 1
        
        evt_type = event["event_type"]
        user_id = event["user_id"]
        product_id = event.get("product_id")
        
        # Timestamp parsing
        ts = self._parse_timestamp(event["event_timestamp"])
        dt = datetime.fromtimestamp(ts)
        minute_key = dt.strftime("%Y-%m-%d %H:%M")
        
        # Track Active User
        self.active_users[user_id] = max(self.active_users.get(user_id, 0.0), ts)
        
        # Update trends
        trend_bucket = self.trends[minute_key]
        trend_bucket[evt_type] += 1
        trend_bucket["active_users"].add(user_id)
        
        if evt_type == "product_view":
            self.total_views += 1
            if product_id:
                self.product_views[product_id] += 1
        elif evt_type == "search":
            self.total_searches += 1
        elif evt_type == "add_to_cart":
            self.total_carts += 1
        elif evt_type == "purchase":
            self.total_purchases += 1
            if product_id:
                self.product_purchases[product_id] += 1
                # Calculate revenue safely
                revenue = self.product_prices.get(product_id, 0.0)
                self.total_revenue += revenue
                trend_bucket["revenue"] += revenue

    def get_active_users_5m(self) -> int:
        now = time.time()
        # Filter users active in the last 5 minutes (300 seconds)
        recent_users = [uid for uid, latest_ts in self.active_users.items() if (now - latest_ts) <= 300]
        return len(recent_users)

    def get_live_metrics(self) -> Dict[str, Any]:
        elapsed = time.time() - self.start_time
        events_per_sec = self.total_events / elapsed if elapsed > 0 else 0.0
        
        conversion_rate = (self.total_purchases / self.total_events * 100) if self.total_events > 0 else 0.0
        avg_purchase = (self.total_revenue / self.total_purchases) if self.total_purchases > 0 else 0.0
        
        return {
            "active_users_5m": self.get_active_users_5m(),
            "cumulative_metrics": {
                "total_events": self.total_events,
                "product_views": self.total_views,
                "searches": self.total_searches,
                "add_to_carts": self.total_carts,
                "purchases": self.total_purchases,
                "revenue": round(self.total_revenue, 2),
                "conversion_rate_pct": round(conversion_rate, 2),
                "avg_purchase_value": round(avg_purchase, 2)
            },
            "processing_stats": {
                "events_per_second": round(events_per_sec, 2),
                "uptime_seconds": round(elapsed, 2),
                "last_update": datetime.now().isoformat()
            }
        }

    def get_trends(self) -> List[Dict[str, Any]]:
        # Sort by minute
        sorted_minutes = sorted(self.trends.keys())
        # Filter to trend window (e.g., last 60 minutes)
        if len(sorted_minutes) > self.trend_window_minutes:
            sorted_minutes = sorted_minutes[-self.trend_window_minutes:]
            
        results = []
        for minute in sorted_minutes:
            bucket = self.trends[minute]
            results.append({
                "timestamp_minute": minute,
                "product_views": bucket["product_view"],
                "searches": bucket["search"],
                "add_to_carts": bucket["add_to_cart"],
                "purchases": bucket["purchase"],
                "revenue": round(bucket["revenue"], 2),
                "unique_active_users": len(bucket["active_users"])
            })
        return results

    def get_top_products(self, limit: int = 10) -> Dict[str, List[Dict]]:
        top_views = sorted(self.product_views.items(), key=lambda x: x[1], reverse=True)[:limit]
        top_purchases = sorted(self.product_purchases.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return {
            "top_by_views": [{"product_id": k, "views": v} for k, v in top_views],
            "top_by_purchases": [{"product_id": k, "purchases": v} for k, v in top_purchases]
        }
