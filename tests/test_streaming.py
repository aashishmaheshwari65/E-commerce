import unittest
import json
import tempfile
import os
import pandas as pd
import time
from pathlib import Path
import sys

# Add parent directory to path so streaming module is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streaming.processor import StreamProcessor
from streaming.validator import EventValidator
from streaming.reader import FileEventReader
from streaming.writer import MetricsWriter

class TestStreaming(unittest.TestCase):
    def setUp(self):
        # Mock products dataframe for revenue calculation
        self.mock_products = pd.DataFrame([
            {"product_id": 1, "price": 100.0, "discount_percent": 10.0}, # Actual = 90.0
            {"product_id": 2, "price": 50.0, "discount_percent": 0.0}    # Actual = 50.0
        ])
        
        self.valid_users = {101, 102}
        self.valid_products = {1, 2}
        
    def test_revenue_calculation_and_metrics(self):
        processor = StreamProcessor(self.mock_products)
        
        # Simulating events
        e1 = {"event_id": "1", "user_id": 101, "event_type": "product_view", "product_id": 1, "event_timestamp": "2026-10-01T00:00:00Z"}
        e2 = {"event_id": "2", "user_id": 101, "event_type": "purchase", "product_id": 1, "event_timestamp": "2026-10-01T00:01:00Z"}
        e3 = {"event_id": "3", "user_id": 102, "event_type": "purchase", "product_id": 2, "event_timestamp": "2026-10-01T00:02:00Z"}
        
        processor.process_event(e1)
        processor.process_event(e2)
        processor.process_event(e3)
        
        metrics = processor.get_live_metrics()["cumulative_metrics"]
        
        # Revenue should be 90 + 50 = 140
        self.assertAlmostEqual(metrics["revenue"], 140.0)
        self.assertEqual(metrics["total_events"], 3)
        self.assertEqual(metrics["purchases"], 2)
        
    def test_event_validator_duplicates(self):
        validator = EventValidator(self.valid_users, self.valid_products)
        
        valid_event = {"event_id": "1", "user_id": 101, "event_type": "product_view", "product_id": 1, "event_timestamp": "2026-10-01T00:00:00Z"}
        
        self.assertTrue(validator.is_valid(valid_event))
        self.assertFalse(validator.is_valid(valid_event)) # Duplicate should be rejected
        
    def test_file_reader_partial_lines(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(b'{"event_id": "1", "valid": true}\n')
            tmp.write(b'{"event_id": "2", ') # partial line (malformed JSON)
            
        with tempfile.NamedTemporaryFile(delete=False) as cp:
            cp_path = Path(cp.name)
            
        try:
            reader = FileEventReader(tmp_path, cp_path)
            events = list(reader.read_events())
            
            # Should only successfully read the first one, skipping the malformed one without crashing
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0][1]["event_id"], "1")
        finally:
            os.unlink(tmp_path)
            os.unlink(cp_path)
            
    def test_metrics_writer(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir)
            writer = MetricsWriter(dir_path)
            
            # Test writing JSON
            metrics = {"test": 123}
            writer.write_live_metrics(dir_path / "live.json", metrics)
            self.assertTrue((dir_path / "live.json").exists())
            
            # Test writing CSV trends
            trends = [{"timestamp_minute": "2026-10-01 00:00", "product_views": 1, "searches": 0, "add_to_carts": 0, "purchases": 0, "revenue": 0.0, "unique_active_users": 1}]
            writer.write_trends_csv(dir_path / "trends.csv", trends)
            self.assertTrue((dir_path / "trends.csv").exists())

if __name__ == "__main__":
    unittest.main()
