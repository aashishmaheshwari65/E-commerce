import logging
from typing import Dict, Any, Set
from .config import EVENT_TYPES

logger = logging.getLogger(__name__)

class EventValidator:
    def __init__(self, valid_user_ids: Set[int], valid_product_ids: Set[int], max_cache_size: int = 100000):
        self.valid_user_ids = valid_user_ids
        self.valid_product_ids = valid_product_ids
        self.seen_event_ids: Set[str] = set()
        self.max_cache_size = max_cache_size
        self.events_processed = 0

    def is_valid(self, event: Dict[str, Any]) -> bool:
        required_keys = {"event_id", "user_id", "event_type", "event_timestamp"}
        
        if not required_keys.issubset(event.keys()):
            logger.debug(f"Rejected: Missing keys in {event}")
            return False

        event_id = event["event_id"]
        
        # Deduplication
        if event_id in self.seen_event_ids:
            logger.debug(f"Duplicate event skipped: {event_id}")
            return False
            
        if event["event_type"] not in EVENT_TYPES:
            logger.debug(f"Rejected: Invalid event type {event.get('event_type')}")
            return False

        if event["user_id"] not in self.valid_user_ids:
            logger.debug(f"Rejected: Unknown user_id {event.get('user_id')}")
            return False

        if event["event_type"] == "search":
            if not event.get("search_query"):
                return False
        else:
            if event.get("product_id") not in self.valid_product_ids:
                return False

        if not event.get("event_timestamp"):
            return False

        # Add to seen, managing memory
        self.seen_event_ids.add(event_id)
        self.events_processed += 1
        
        # Periodically clean up cache (naive approach for a rolling window)
        if len(self.seen_event_ids) > self.max_cache_size:
            # We can't pop from a set predictably, so we clear it and rely on file position
            # A more robust solution involves a queue or OrderedDict, but this is fine for now
            self.seen_event_ids.clear()
            self.seen_event_ids.add(event_id)

        return True
