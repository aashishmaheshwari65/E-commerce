# SQL Analytics

This module (`sql_analytics/`) contains a comprehensive analytical layer built on top of the Parquet Data Warehouse (Star Schema). 

## SQL Engine
We use **DuckDB**, which acts as a lightweight, in-memory SQL engine capable of querying Parquet files directly. This eliminates the need for an active PostgreSQL/Supabase connection to perform fast local analytics.

## Folder Structure
- `config.py`: Directory paths configuration.
- `runner.py`: DuckDB session manager that maps `.parquet` dimension and fact tables to local SQL views.
- `main.py`: Command-line interface to execute the query groups and output results.
- `queries/`: SQL scripts covering distinct business domains (Revenue, Sales, Customers, etc.).
- `data/analytics/`: The destination folder where CSV results are dumped.

## How to Run

Run all queries:
```powershell
python -m sql_analytics.main
```

Run a specific analytics group (e.g., revenue):
```powershell
python -m sql_analytics.main --group revenue
```

Available groups: `revenue`, `sales`, `customers`, `products`, `retention`, `payments`, `kpis`, `advanced`.

*Note: DuckDB syntax is very similar to PostgreSQL. The queries are designed to be largely dialect-agnostic and should migrate easily if pushed to Supabase later.*
