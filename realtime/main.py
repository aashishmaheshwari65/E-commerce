import argparse
import time
import logging
import sys
from collections import Counter
from pathlib import Path

from .config import OUTPUT_FILE, EVENT_TYPES
from .event_generator import EventGenerator
from .event_validator import EventValidator
from .event_writer import EventWriter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Real-Time E-Commerce Event Generator")
    parser.add_argument("--rate", type=float, default=5.0, help="Events per second (default: 5.0)")
    parser.add_argument("--max-events", type=int, default=0, help="Maximum number of events to generate (0 for unlimited)")
    parser.add_argument("--duration", type=int, default=0, help="Duration to run in seconds (0 for unlimited)")
    parser.add_argument("--output", type=str, default=str(OUTPUT_FILE), help="Output JSONL file path")
    return parser.parse_args()

def main():
    args = parse_args()
    
    logger.info("Initializing Real-Time Event Generator...")
    
    try:
        generator = EventGenerator()
    except Exception as e:
        logger.error(f"Failed to initialize generator: {e}")
        sys.exit(1)
        
    validator = EventValidator(
        valid_user_ids=set(generator.user_ids), 
        valid_product_ids=set(generator.product_ids)
    )
    
    writer = EventWriter(Path(args.output))
    
    events_generated = 0
    events_written = 0
    start_time = time.time()
    event_counts = Counter()
    
    sleep_time = 1.0 / args.rate if args.rate > 0 else 0
    
    logger.info(f"Target rate: {args.rate} events/sec")
    logger.info(f"Output file: {args.output}")
    logger.info("Press Ctrl+C to stop.")
    
    try:
        writer.open()
        
        while True:
            # Check duration
            if args.duration > 0 and (time.time() - start_time) >= args.duration:
                logger.info(f"Reached maximum duration of {args.duration}s.")
                break
                
            # Check max events
            if args.max_events > 0 and events_generated >= args.max_events:
                logger.info(f"Reached maximum event count of {args.max_events}.")
                break
                
            event = generator.generate_event()
            events_generated += 1
            
            if validator.validate(event):
                writer.write(event)
                events_written += 1
                event_counts[event["event_type"]] += 1
                
                # Log periodically or if rate is low
                if args.rate <= 5 or events_written % max(1, int(args.rate * 2)) == 0:
                    logger.info(f"Written {events_written} events... Last event: {event['event_type']} (ID: {event['event_id']})")
            
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        logger.info("\nReceived Ctrl+C. Shutting down gracefully...")
    finally:
        writer.close()
        
        elapsed = time.time() - start_time
        actual_rate = events_written / elapsed if elapsed > 0 else 0
        
        print("\n" + "="*40)
        print("EVENT GENERATION SUMMARY")
        print("="*40)
        print(f"Total time elapsed: {elapsed:.2f} seconds")
        print(f"Total events generated: {events_generated}")
        print(f"Total events written:   {events_written}")
        print(f"Actual write rate:      {actual_rate:.2f} events/sec")
        print("-" * 40)
        for evt_type in EVENT_TYPES:
            print(f"  - {evt_type}: {event_counts[evt_type]}")
        print("="*40)

if __name__ == "__main__":
    main()
