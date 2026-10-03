# PySpark Distributed Data Processing

## Overview
This module (`spark_processing/`) provides a PySpark-based data processing pipeline for the E-Commerce platform. It complements the existing Pandas-based batch ETL by demonstrating how to handle larger volumes of data using distributed processing, allowing the platform to scale. PySpark is used here to enable distributed data transformations, aggregations, and quality checks.

## Installation

1. **Python Dependencies:** Ensure you have PySpark installed.
   ```powershell
   pip install pyspark pytest
   ```

2. **Java Requirement:** PySpark on Windows requires Java 8 or Java 11. 
   - Download and install Java (e.g., AdoptOpenJDK 11).
   - Set the `JAVA_HOME` environment variable to your Java installation path (e.g., `C:\Program Files\Java\jdk-11`).
   - Add `%JAVA_HOME%\bin` to your system `PATH`.
   - **Winutils (Optional for local testing but recommended):** PySpark on Windows might warn about missing `winutils.exe` or `HADOOP_HOME`. For local execution without HDFS, this warning can generally be ignored or resolved by downloading winutils for your Hadoop version and setting `HADOOP_HOME`.

## Module Structure

- `__init__.py`: Module initializer.
- `config.py`: Configuration for paths and Spark settings.
- `spark_session.py`: Creation and management of SparkSession.
- `reader.py`: Loads CSV/Parquet datasets.
- `transformations.py`: Spark DataFrame transformations (casting, normalization, derived columns).
- `aggregations.py`: Business aggregations (customer, product, sales analytics) and distributed joins.
- `writer.py`: Parquet output writer and Data Quality report generator.
- `main.py`: Main orchestrator script.
- `tests/`: Directory containing unit tests (`test_transformations.py`, `test_aggregations.py`).

## Paths

**Input:**
The reader primarily looks for datasets in `data_lake/silver/` (Parquet). If not found, it falls back to `data/processed/` (CSV).

**Output:**
- Processed Parquet Data: `data/spark/processed/`
- Analytics Parquet Data: `data/spark/analytics/`
- Data Quality Report: `data/spark/quality/data_quality_report.json`

## How to Run the Pipeline

Run the pipeline from the project root using:
```powershell
python -m spark_processing.main
```
You can also specify the log level:
```powershell
python -m spark_processing.main --log-level INFO
```

## How to Run Tests

Run tests using pytest from the project root:
```powershell
pytest spark_processing/tests/
```

## Transformations and Aggregations

**Transformations:** Data type casting, string normalization, parsing timestamps, and calculating derived columns (e.g., `discounted_price`, `calculated_line_total`). Invalid rows are flagged with an `is_valid` column rather than discarded immediately, allowing for quarantine or tracking.

**Aggregations:** Business metrics include Customer Analytics, Product Analytics, Monthly Sales, Category Performance, Payment Analytics, and Event Analytics. Aggregations use proper Spark distributed joins and groupings.

## PySpark vs Pandas ETL

The Pandas batch ETL is suitable for small-to-medium datasets processed in memory on a single machine. The PySpark pipeline is designed for horizontal scalability. It uses lazy evaluation, distributed DataFrames, and partition-aware processing, making it capable of handling large-scale datasets across a cluster.

## Limitations of Local Mode

In this current setup, Spark is running in `local[*]` mode (single machine, multiple threads). While it uses Spark's API, it is still constrained by the local machine's memory and CPU. 

## Extensibility

This module is designed to be easily extensible. 
- **Cluster Deployment:** To run on a real cluster (e.g., Databricks, EMR), you simply change the `MASTER_URL` and submit the job via `spark-submit`. 
- **Streaming:** The batch transformations can be adapted to Spark Structured Streaming (e.g., from Kafka) by changing `spark.read` to `spark.readStream`.
