from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys
import os

# Ensure the project root is in the Python path
sys.path.insert(0, os.getenv("AIRFLOW_HOME", "/opt/airflow"))

from validation.main import main as run_validation
from etl.main import main as run_etl
from data_lake.main import main as run_data_lake

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=30),
}

with DAG(
    'ecommerce_data_pipeline',
    default_args=default_args,
    description='E-Commerce Data Pipeline: Validation, ETL, and Data Lake',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['ecommerce', 'pipeline'],
) as dag:

    def validation_task(**kwargs):
        print("Starting Data Validation...")
        # Since validation.main doesn't return or raise exception on failure by default,
        # we will use the validator directly to raise an exception if it fails.
        from validation.validate import DataValidator
        validator = DataValidator()
        report = validator.run()
        if report["status"] != "PASSED":
            raise Exception("Data Validation failed: " + str(report))
        print("Data Validation passed.")

    task_validation = PythonOperator(
        task_id='data_validation',
        python_callable=validation_task,
    )

    task_etl = PythonOperator(
        task_id='batch_etl',
        python_callable=run_etl,
    )

    task_data_lake = PythonOperator(
        task_id='data_lake',
        python_callable=run_data_lake,
    )

    # Set dependencies
    task_validation >> task_etl >> task_data_lake
