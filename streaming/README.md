# Streaming Analytics (Functionality 9)

This module implements a near-real-time processing engine that reads incoming e-commerce events and calculates live analytics metrics continuously. 

It is designed to be fully decoupled from the generation logic and operates entirely via file tailing (polling), enabling robust recovery and minimal memory footprints. It has been architected with an abstract interface (`EventReader`) so that a Kafka Consumer can be easily plugged in as a data source in future functionalities.

## Architecture

- **`config.py`**: Configuration properties and paths.
- **`reader.py`**: File-tailing system that reliably tracks the latest byte offset and saves it atomically to a checkpoint.
- **`validator.py`**: Performs schema checking, bounds checking, and exact deduplication using a rolling cache of `event_id`.
- **`processor.py`**: The aggregation engine. Computes total revenue by correlating the incoming `product_id` with existing `products.csv` prices (calculating correct discounted purchase value). Maintains a 5-minute sliding window for Active Users and groups trends by minute.
- **`writer.py`**: Uses atomic temporary file writes (`.tmp` -> replace) to ensure metric snapshots (`JSON` & `CSV`) are never corrupted even if read simultaneously by downstream dashboards.
- **`main.py`**: Entrypoint for controlling polling speed and limits.

## Metrics output

Outputs are stored continuously in `data/realtime/metrics/`:

- **`live_metrics.json`**: Cumulative counts (views, searches, purchases, revenue, conversion rate), active users (5m), and processing stats.
- **`trends.csv`**: Time-series grouping by minute tracking users and event types.
- **`top_products.csv`**: Separate rankings for highest viewed and highest purchased products.
- **`checkpoint.json`**: Preserves the exact file offset to guarantee zero data loss upon crash recovery.

## Setup and Execution

To run the streaming processor indefinitely (polls every 2.0s by default):
```bash
python -m streaming.main
```

### Options
- `--interval`: Polling interval in seconds (default: 2.0)
- `--max-events`: Stop after processing a set limit (default: 0 / unlimited)
- `--duration`: Stop after a set amount of seconds (default: 0 / unlimited)
- `--trend-window`: Rolling time-series window in minutes for `trends.csv` (default: 60)

Example (fast polling for 20 seconds):
```bash
python -m streaming.main --interval 0.5 --duration 20
```

## Kafka Integration
The code strictly isolates the I/O inside `reader.py`. To plug in Apache Kafka later, you only need to create a `KafkaEventReader(EventReader)` implementation that hooks into your topic. The validation and processing engine will seamlessly accept it!
