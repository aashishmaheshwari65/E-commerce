"""Event validation logic."""
from typing import Dict, Any, Set
import logging
from .config import EVENT_TYPES

logger = logging.getLogger(__name__)

class EventValidator:
    def __init__(self, valid_user_ids: Set[int], valid_product_ids: Set[int]):
        self.valid_user_ids = valid_user_ids
        self.valid_product_ids = valid_product_ids
        self.seen_event_ids: Set[str] = set()

    def validate(self, event: Dict[str, Any]) -> bool:
        """Validate an event against the schema and rules."""
        required_keys = {"event_id", "user_id", "event_type", "event_timestamp"}
        
        # Check required fields
        if not required_keys.issubset(event.keys()):
            logger.error(f"Missing required keys. Event: {event}")
            return False

        # Check unique event ID
        event_id = event["event_id"]
        if event_id in self.seen_event_ids:
            logger.error(f"Duplicate event_id found: {event_id}")
            return False
        self.seen_event_ids.add(event_id)

        # Check valid event type
        if event["event_type"] not in EVENT_TYPES:
            logger.error(f"Invalid event_type: {event['event_type']}")
            return False

        # Check user ID exists
        if event["user_id"] not in self.valid_user_ids:
            logger.error(f"Invalid user_id: {event['user_id']}")
            return False

        # Conditional checks based on event type
        if event["event_type"] == "search":
            if not event.get("search_query"):
                logger.error("Search event missing search_query")
                return False
            if pd := event.get("product_id"):
                logger.error(f"Search event should not have product_id: {pd}")
                return False
        else:
            if event.get("product_id") not in self.valid_product_ids:
                logger.error(f"Invalid product_id: {event.get('product_id')} for {event['event_type']}")
                return False
            if sq := event.get("search_query"):
                logger.error(f"Non-search event should not have search_query: {sq}")
                return False

        # Check timestamp exists (ISO 8601 validation could be more strict, assuming string presence)
        if not event["event_timestamp"]:
            logger.error("Missing event_timestamp")
            return False

        return True
