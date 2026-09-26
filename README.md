# E-commerce Dataset Generator & Ingestion Pipeline

A reproducible, relationship-aware e-commerce dataset generator and ingestion pipeline using Python, Faker, Pandas, NumPy, and SQLAlchemy.

## Project Structure

```
E-Commerce/
│
├── data/
│   ├── raw/                      # Generated raw CSV datasets
│   └── ecommerce.db              # SQLite database (created on ingest)
│
├── dataset_generator/            # Synthetic data generation logic
│   ├── __init__.py
│   ├── config.py
│   ├── generator.py
│   └── main.py
│
├── ingestion/                    # Database models and ingestion pipeline
│   ├── __init__.py
│   ├── database.py
│   └── ingest.py
│
├── requirements.txt
└── README.md
```

## Setup & Prerequisites

```bash
pip install -r requirements.txt
```

## 1. Generate the Dataset

Run the generator to create synthetic datasets. The CSV files will be saved in `data/raw/`.

```bash
python -m dataset_generator.main
```

### Generated Files:
- `users.csv` — 100 users
- `products.csv` — 50 products
- `orders.csv` — 500 orders
- `order_items.csv` — 1,000+ order items
- `payments.csv` — 500 payments
- `reviews.csv` — 200 product reviews
- `user_events.csv` — 5,000 user events
- `data_dictionary.csv` — column definitions
- `dataset_statistics.json` — validation stats

The generator uses `RANDOM_SEED = 42`, so repeated runs produce the same deterministic dataset.

## 2. Ingest Data

Run the ingestion script to load the generated CSVs into a relational SQLite database (`data/ecommerce.db`). 
The script ensures referential integrity and maps the data to SQLAlchemy ORM models.

```bash
python -m ingestion.ingest
```
