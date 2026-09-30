import json
import csv
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MetricsWriter:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_live_metrics(self, file_path: Path, metrics: Dict[str, Any]):
        temp_file = file_path.with_suffix('.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2)
            temp_file.replace(file_path)
        except Exception as e:
            logger.error(f"Failed to write live metrics: {e}")

    def write_trends_csv(self, file_path: Path, trends: List[Dict[str, Any]]):
        if not trends:
            return
            
        temp_file = file_path.with_suffix('.tmp')
        try:
            keys = ["timestamp_minute", "product_views", "searches", "add_to_carts", "purchases", "revenue", "unique_active_users"]
            with open(temp_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(trends)
            temp_file.replace(file_path)
        except Exception as e:
            logger.error(f"Failed to write trends CSV: {e}")

    def write_top_products_csv(self, file_path: Path, top_products: Dict[str, List[Dict]]):
        temp_file = file_path.with_suffix('.tmp')
        try:
            with open(temp_file, 'w', newline='', encoding='utf-8') as f:
                # We'll just write them as two sections or merged. Let's merge them for simplicity.
                writer = csv.writer(f)
                writer.writerow(["Ranking", "Top by Views (Product ID)", "Views", "Top by Purchases (Product ID)", "Purchases"])
                
                views = top_products["top_by_views"]
                purchases = top_products["top_by_purchases"]
                max_len = max(len(views), len(purchases))
                
                for i in range(max_len):
                    v_id = views[i]["product_id"] if i < len(views) else ""
                    v_ct = views[i]["views"] if i < len(views) else ""
                    p_id = purchases[i]["product_id"] if i < len(purchases) else ""
                    p_ct = purchases[i]["purchases"] if i < len(purchases) else ""
                    
                    writer.writerow([i+1, v_id, v_ct, p_id, p_ct])
                    
            temp_file.replace(file_path)
        except Exception as e:
            logger.error(f"Failed to write top products CSV: {e}")
