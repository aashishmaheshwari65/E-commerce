# Apache Airflow Orchestration

This folder contains the Apache Airflow DAGs and configuration to orchestrate the E-Commerce Data Pipeline.

## Prerequisites
- Docker and Docker Compose installed.

## Installation and Setup
1. Ensure your `.env` file is present in the root directory (containing `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_KEY`).
2. The `docker-compose.yaml` handles everything from installing dependencies to running Airflow components.

## Docker Startup Instructions
To start Airflow locally, run the following from the root of the project:
```bash
docker-compose up -d
```
It may take a few minutes to initialize the metadata database and download dependencies for the first time.

## Accessing the Airflow UI
- Open your browser and navigate to: `http://localhost:8080`
- **Username:** `admin`
- **Password:** `admin`

## Triggering the DAG Manually
1. Navigate to `http://localhost:8080`.
2. Locate the `ecommerce_data_pipeline` DAG in the list.
3. Click the "Play" (▶) button on the right side of the DAG row.
4. Select "Trigger DAG" to run it manually.

## Inspecting Task Logs
1. Click on the `ecommerce_data_pipeline` DAG name.
2. Go to the "Grid" view and click on a specific task (e.g., `data_validation`, `batch_etl`).
3. In the panel that opens on the right, click on the **Logs** tab to view the detailed output of the task.

## Stopping Airflow
To stop the Airflow containers, run:
```bash
docker-compose down
```

## Troubleshooting
- **Missing Data or Directories:** Ensure that the local `./data` directories exist. The volumes are mounted into `/opt/airflow/`.
- **Dependency Issues:** Check `airflow-webserver` logs. The setup uses `_PIP_ADDITIONAL_REQUIREMENTS` to dynamically install `pandas`, `pyarrow`, and `supabase`. If installation fails, it will show up in the webserver or scheduler container logs.
- **DAG Import Errors:** Verify that the code inside `./validation`, `./etl`, and `./data_lake` contains no syntax errors. Look for import errors at the top of the Airflow UI.
