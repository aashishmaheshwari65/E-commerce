import argparse
import time
import logging
import sys
import pandas as pd
from pathlib import Path

from .config import (
    DEFAULT_EVENTS_FILE, CHECKPOINT_FILE, LIVE_METRICS_FILE, 
    TRENDS_FILE, TOP_PRODUCTS_FILE, PRODUCTS_CSV, USERS_CSV, OUTPUT_DIR
)
from .reader import FileEventReader
from .validator import EventValidator
from .processor import StreamProcessor
from .writer import MetricsWriter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Near-Real-Time Stream Processor")
    parser.add_argument("--interval", type=float, default=2.0, help="Polling interval in seconds (default: 2.0)")
    parser.add_argument("--duration", type=int, default=0, help="Maximum running duration in seconds (0 for unlimited)")
    parser.add_argument("--max-events", type=int, default=0, help="Maximum events to process (0 for unlimited)")
    parser.add_argument("--trend-window", type=int, default=60, help="Trend window in minutes (default: 60)")
    parser.add_argument("--input", type=str, default=str(DEFAULT_EVENTS_FILE), help="Input events file")
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="Output directory for metrics")
    return parser.parse_args()

def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output_dir)
    checkpoint_file = output_path / "checkpoint.json"
    
    logger.info("Initializing Stream Processor...")
    
    try:
        users_df = pd.read_csv(USERS_CSV)
        valid_users = set(users_df['user_id'].tolist())
        products_df = pd.read_csv(PRODUCTS_CSV)
        valid_products = set(products_df['product_id'].tolist())
    except FileNotFoundError as e:
        logger.error(f"Missing essential raw datasets: {e}")
        sys.exit(1)
        
    reader = FileEventReader(input_path, checkpoint_file)
    validator = EventValidator(valid_user_ids=valid_users, valid_product_ids=valid_products)
    processor = StreamProcessor(products_df=products_df, trend_window_minutes=args.trend_window)
    writer = MetricsWriter(output_path)
    
    logger.info(f"Polling interval: {args.interval}s")
    logger.info(f"Input file: {input_path}")
    logger.info(f"Output directory: {output_path}")
    logger.info("Press Ctrl+C to stop.")
    
    start_time = time.time()
    events_processed = 0
    
    try:
        while True:
            # Check duration limits
            if args.duration > 0 and (time.time() - start_time) >= args.duration:
                logger.info(f"Reached max duration of {args.duration}s.")
                break
                
            if args.max_events > 0 and events_processed >= args.max_events:
                logger.info(f"Reached max events of {args.max_events}.")
                break
                
            new_events = 0
            rejected = 0
            last_checkpoint = None
            
            for marker, event in reader.read_events():
                if validator.is_valid(event):
                    processor.process_event(event)
                    new_events += 1
                    events_processed += 1
                else:
                    rejected += 1
                last_checkpoint = marker
                
                # Check max events inside loop as well
                if args.max_events > 0 and events_processed >= args.max_events:
                    break

            if new_events > 0 or rejected > 0:
                # Update metrics only if something changed
                metrics = processor.get_live_metrics()
                writer.write_live_metrics(output_path / "live_metrics.json", metrics)
                writer.write_trends_csv(output_path / "trends.csv", processor.get_trends())
                writer.write_top_products_csv(output_path / "top_products.csv", processor.get_top_products())
                
                # Commit checkpoint
                if last_checkpoint is not None:
                    reader.commit_checkpoint(last_checkpoint)
                
                logger.info(f"Batch processed: {new_events} valid, {rejected} rejected.")
                logger.info(f"Live Metrics: Active Users(5m): {metrics['active_users_5m']}, "
                            f"Revenue: ${metrics['cumulative_metrics']['revenue']}, "
                            f"Conversion: {metrics['cumulative_metrics']['conversion_rate_pct']}%")

            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        logger.info("\nReceived Ctrl+C. Shutting down gracefully...")
    finally:
        logger.info("Stream Processor stopped.")
        
if __name__ == "__main__":
    main()
