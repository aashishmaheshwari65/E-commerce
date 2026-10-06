from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys
import os

# Ensure the project root is in the Python path for Airflow workers/scheduler
sys.path.insert(0, os.getenv("AIRFLOW_HOME", "/opt/airflow"))

default_args = {
    'owner': 'ml_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=60),
}

with DAG(
    'automated_ml_pipeline',
    default_args=default_args,
    description='Automated ML Pipeline: Feature Engineering, Model Training, Evaluation, Selection, and Registry',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,
    tags=['ml_pipeline', 'ecommerce', 'machine_learning'],
) as dag:

    def task_feature_engineering(**kwargs):
        print("Starting Feature Engineering Task...")
        from ml_pipeline import feature_pipeline
        paths = feature_pipeline.save_features()
        print(f"Feature Engineering finished: {paths}")

    def task_validate_features(**kwargs):
        print("Starting Feature Validation Task...")
        import pandas as pd
        from ml_pipeline import config, feature_pipeline
        
        cust_df = pd.read_parquet(config.FEATURE_ROOT / "customer_features.parquet")
        churn_df = pd.read_parquet(config.FEATURE_ROOT / "churn_features.parquet")
        sales_df = pd.read_parquet(config.FEATURE_ROOT / "sales_features.parquet")
        rec_df = pd.read_parquet(config.FEATURE_ROOT / "recommendation_features.parquet")

        feature_pipeline.validate_features(cust_df, ["customer_id", "recency_days", "frequency", "monetary_value"])
        feature_pipeline.validate_features(churn_df, ["customer_id", "total_orders", "total_spend", "churn_label"])
        feature_pipeline.validate_features(sales_df, ["order_date", "total_revenue", "lag_1", "rolling_mean_7"])
        feature_pipeline.validate_features(rec_df, ["user_id", "product_id", "interaction_score"])
        print("Feature Validation PASSED.")

    def task_train_models(**kwargs):
        print("Starting Candidate Model Training Task...")
        from ml_pipeline import training_pipeline
        train_results = training_pipeline.train_all()
        # Save training output status to XCom or temporary state
        print("Model training completed for all domains.")

    def task_evaluate_models(**kwargs):
        print("Starting Model Evaluation Task...")
        from ml_pipeline import evaluation_pipeline
        eval_results = evaluation_pipeline.evaluate_all()
        print(f"Model evaluation completed: {eval_results.keys()}")

    def task_select_best_models(**kwargs):
        print("Selecting Best Candidate Models...")
        from ml_pipeline import config, pipeline_utils
        seg_m = pipeline_utils.load_json(config.METRIC_ROOT / "segmentation_metrics.json")
        churn_m = pipeline_utils.load_json(config.METRIC_ROOT / "churn_metrics.json")
        fore_m = pipeline_utils.load_json(config.METRIC_ROOT / "forecasting_metrics.json")
        rec_m = pipeline_utils.load_json(config.METRIC_ROOT / "recommendation_metrics.json")
        
        print("Selected Models Summary:")
        print(f"  - Segmentation : {seg_m.get('selected_model')}")
        print(f"  - Churn        : {churn_m.get('selected_model')}")
        print(f"  - Forecasting  : {fore_m.get('selected_model')}")
        print(f"  - Recommendation: {rec_m.get('selected_model')}")

    def task_save_models(**kwargs):
        print("Saving Selected Models to Model Registry...")
        from ml_pipeline import pipeline
        res = pipeline.run_pipeline(run_all=True)
        print(f"Model registry updated successfully. Version: {res.get('run_id')}")

    def task_generate_report(**kwargs):
        print("Generating Pipeline Reports...")
        from ml_pipeline import config, pipeline_utils
        runs = pipeline_utils.load_json(config.PIPELINE_ROOT / "pipeline_runs.json")
        if runs:
            print(f"Latest pipeline run status: {runs[0].get('status')}")

    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    t_feat_eng = PythonOperator(
        task_id='feature_engineering',
        python_callable=task_feature_engineering,
    )

    t_val_feat = PythonOperator(
        task_id='validate_features',
        python_callable=task_validate_features,
    )

    t_train = PythonOperator(
        task_id='train_models',
        python_callable=task_train_models,
    )

    t_eval = PythonOperator(
        task_id='evaluate_models',
        python_callable=task_evaluate_models,
    )

    t_select = PythonOperator(
        task_id='select_best_models',
        python_callable=task_select_best_models,
    )

    t_save = PythonOperator(
        task_id='save_models',
        python_callable=task_save_models,
    )

    t_report = PythonOperator(
        task_id='generate_report',
        python_callable=task_generate_report,
    )

    # Airflow task dependencies chain
    start >> t_feat_eng >> t_val_feat >> t_train >> t_eval >> t_select >> t_save >> t_report >> end
