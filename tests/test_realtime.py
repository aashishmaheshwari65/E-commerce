import unittest
import json
from pathlib import Path
import tempfile
import sys
import os

# Add parent directory to path so realtime module is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from realtime.event_validator import EventValidator
from realtime.event_writer import EventWriter

class TestRealtime(unittest.TestCase):
    def setUp(self):
        self.valid_users = {1, 2, 3}
        self.valid_products = {101, 102}
        self.validator = EventValidator(self.valid_users, self.valid_products)

    def test_valid_product_view(self):
        event = {
            "event_id": "123",
            "user_id": 1,
            "event_type": "product_view",
            "product_id": 101,
            "search_query": None,
            "event_timestamp": "2026-09-30T00:00:00Z"
        }
        self.assertTrue(self.validator.validate(event))

    def test_valid_search(self):
        event = {
            "event_id": "124",
            "user_id": 2,
            "event_type": "search",
            "product_id": None,
            "search_query": "laptop",
            "event_timestamp": "2026-09-30T00:00:00Z"
        }
        self.assertTrue(self.validator.validate(event))

    def test_invalid_event_type(self):
        event = {
            "event_id": "125",
            "user_id": 1,
            "event_type": "unknown",
            "product_id": 101,
            "search_query": None,
            "event_timestamp": "2026-09-30T00:00:00Z"
        }
        self.assertFalse(self.validator.validate(event))

    def test_duplicate_event_id(self):
        event = {
            "event_id": "126",
            "user_id": 1,
            "event_type": "product_view",
            "product_id": 101,
            "search_query": None,
            "event_timestamp": "2026-09-30T00:00:00Z"
        }
        self.assertTrue(self.validator.validate(event))
        self.assertFalse(self.validator.validate(event))

    def test_invalid_user(self):
        event = {
            "event_id": "127",
            "user_id": 999,
            "event_type": "product_view",
            "product_id": 101,
            "search_query": None,
            "event_timestamp": "2026-09-30T00:00:00Z"
        }
        self.assertFalse(self.validator.validate(event))

    def test_search_with_product_id_rejected(self):
        event = {
            "event_id": "128",
            "user_id": 1,
            "event_type": "search",
            "product_id": 101,
            "search_query": "laptop",
            "event_timestamp": "2026-09-30T00:00:00Z"
        }
        self.assertFalse(self.validator.validate(event))

    def test_event_writer(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            writer = EventWriter(tmp_path)
            event = {"event_id": "write_test", "user_id": 1}
            writer.write(event)
            writer.close()
            
            with open(tmp_path, "r") as f:
                lines = f.readlines()
                self.assertEqual(len(lines), 1)
                loaded_event = json.loads(lines[0])
                self.assertEqual(loaded_event["event_id"], "write_test")
        finally:
            os.unlink(tmp_path)

if __name__ == "__main__":
    unittest.main()
