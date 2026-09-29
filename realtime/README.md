# Real-Time Event Generator (Functionality 7)

This module simulates real-time e-commerce customer activity by generating events such as product views, searches, add-to-carts, and purchases based on existing users and products datasets.

## Architecture

* **`event_generator.py`**: Samples data from the raw CSVs (`users.csv`, `products.csv`) and creates simulated events.
* **`event_validator.py`**: Ensures all generated events conform to schema constraints (valid IDs, valid event types, correct schema).
* **`event_writer.py`**: Appends validated events in JSON Lines (`.jsonl`) format.
* **`main.py`**: The entrypoint that handles execution, CLI arguments, and graceful shutdown.

## Output Format

Events are written to `data/realtime/events.jsonl` by default. Each line is a single JSON object.

### Sample Event
```json
{
  "event_id": "a1b2c3d4-...",
  "user_id": 451,
  "event_type": "product_view",
  "product_id": 1023,
  "search_query": null,
  "event_timestamp": "2026-09-30T10:14:18.123456+00:00"
}
```

## Commands

Run the generator with default settings (5 events per second, infinite duration):
```bash
python -m realtime.main
```

### Options
- `--rate`: Events per second (default: `5.0`)
- `--max-events`: Stop after generating this many events (default: `0` / unlimited)
- `--duration`: Stop after this many seconds (default: `0` / unlimited)
- `--output`: Specify a custom output path (default: `data/realtime/events.jsonl`)

### Examples
Run for exactly 10 seconds at a high rate:
```bash
python -m realtime.main --rate 50 --duration 10
```

Generate exactly 1000 events:
```bash
python -m realtime.main --max-events 1000 --rate 10
```

## Stopping the Generator
Press `Ctrl+C` to gracefully shut down the generator. It will close the output file safely and print a summary of all events generated and written.
