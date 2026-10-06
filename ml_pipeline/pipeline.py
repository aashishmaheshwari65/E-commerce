import os
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
from ml_pipeline import config
from ml_pipeline.pipeline_utils import get_logger, save_json, load_json
from ml_pipeline import feature_pipeline
from ml_pipeline import training_pipeline
from ml_pipeline import evaluation_pipeline
from ml_pipeline import model_registry

logger = get_logger("pipeline")

def record_pipeline_run(run_data):
    """Update pipeline execution history in data/ml_pipeline/pipeline_runs.json."""
    config.ensure_directories()
    runs_file = config.PIPELINE_ROOT / "pipeline_runs.json"
    history = load_json(runs_file, default=[])
    if not isinstance(history, list):
        history = []

    history.insert(0, run_data) # latest run first
    save_json(runs_file, history)
    return history

def generate_reports(run_data, eval_results):
    """Generate pipeline_report.json, pipeline_report.csv, and model_comparison.csv."""
    os.makedirs(config.REPORT_ROOT, exist_ok=True)

    # 1. Pipeline Report JSON
    save_json(config.REPORT_ROOT / "pipeline_report.json", run_data)

    # 2. Pipeline Summary CSV
    report_rows = []
    selected_models = run_data.get("selected_models", {})
    for domain, sel_name in selected_models.items():
        dom_eval = eval_results.get(domain, {})
        report_rows.append({
            "run_id": run_data["run_id"],
            "model_type": domain,
            "selected_model": sel_name,
            "primary_metric": dom_eval.get("primary_metric", "unknown"),
            "selected_score": dom_eval.get("selected_score", 0.0),
            "version": run_data.get("version", run_data["run_id"]),
            "status": run_data["status"],
            "timestamp": run_data["end_time"]
        })

    report_df = pd.DataFrame(report_rows)
    report_df.to_csv(config.REPORT_ROOT / "pipeline_report.csv", index=False)
    logger.info("Successfully generated pipeline reports.")

def run_pipeline(run_all=True, features_only=False, train_only=False, evaluate_only=False, target_model_type=None):
    """
    Execute end-to-end automated ML pipeline with status tracking, error handling, and model registry updates.
    """
    config.ensure_directories()
    run_id = config.generate_version()
    start_time = datetime.now().isoformat()
    start_ticks = time.time()

    run_meta = {
        "run_id": run_id,
        "version": run_id,
        "start_time": start_time,
        "status": "running",
        "feature_status": "pending",
        "training_status": "pending",
        "evaluation_status": "pending",
        "model_save_status": "pending",
        "selected_models": {},
        "errors": []
    }

    try:
        # Step 1: Feature Engineering
        logger.info("=== STEP 1: FEATURE ENGINEERING ===")
        feature_paths = feature_pipeline.save_features()
        run_meta["feature_status"] = "success"

        if features_only:
            run_meta["status"] = "success"
            run_meta["end_time"] = datetime.now().isoformat()
            record_pipeline_run(run_meta)
            logger.info("Features-only execution finished successfully.")
            return run_meta

        # Step 2: Model Training
        logger.info("=== STEP 2: MODEL TRAINING ===")
        if target_model_type:
            if target_model_type not in config.MODEL_TYPES:
                raise ValueError(f"Invalid model_type '{target_model_type}'. Choices: {config.MODEL_TYPES}")
            train_fn_map = {
                "segmentation": training_pipeline.train_customer_segmentation,
                "churn": training_pipeline.train_churn_models,
                "forecasting": training_pipeline.train_sales_forecasting,
                "recommendation": training_pipeline.train_recommendation_models
            }
            train_results = {target_model_type: train_fn_map[target_model_type]()}
        else:
            train_results = training_pipeline.train_all()

        run_meta["training_status"] = "success"

        if train_only:
            run_meta["status"] = "success"
            run_meta["end_time"] = datetime.now().isoformat()
            record_pipeline_run(run_meta)
            logger.info("Train-only execution finished successfully.")
            return run_meta

        # Step 3: Model Evaluation & Selection
        logger.info("=== STEP 3: MODEL EVALUATION & SELECTION ===")
        eval_results = {}
        if "segmentation" in train_results:
            eval_results["segmentation"] = evaluation_pipeline.evaluate_segmentation(train_results["segmentation"])
        if "churn" in train_results:
            eval_results["churn"] = evaluation_pipeline.evaluate_churn(train_results["churn"])
        if "forecasting" in train_results:
            eval_results["forecasting"] = evaluation_pipeline.evaluate_forecasting(train_results["forecasting"])
        if "recommendation" in train_results:
            eval_results["recommendation"] = evaluation_pipeline.evaluate_recommendation(train_results["recommendation"])

        run_meta["evaluation_status"] = "success"

        if evaluate_only:
            run_meta["status"] = "success"
            run_meta["end_time"] = datetime.now().isoformat()
            record_pipeline_run(run_meta)
            logger.info("Evaluate-only execution finished successfully.")
            return run_meta

        # Step 4: Model Registry & Save
        logger.info("=== STEP 4: MODEL REGISTRY & SAVE ===")
        selected_models_summary = {}

        for domain, domain_train in train_results.items():
            domain_eval = eval_results.get(domain, {})
            sel_model_name = domain_eval.get("selected_model")
            selected_models_summary[domain] = sel_model_name

            # Retrieve trained candidate model object
            trained_model_obj = domain_train["models"].get(sel_model_name)

            # Metadata formatting
            num_rows = len(domain_train.get("df", domain_train.get("X_train", domain_train.get("interactions_df", []))))
            feat_count = len(domain_train.get("feature_cols", []))

            metadata = {
                "model_type": domain,
                "model_name": sel_model_name,
                "version": run_id,
                "training_timestamp": start_time,
                "training_data_source": f"data/ml_pipeline/features/{domain}_features.parquet",
                "feature_count": feat_count,
                "training_rows": num_rows,
                "status": "selected"
            }

            model_registry.save_model(
                model_type=domain,
                model_obj=trained_model_obj,
                version=run_id,
                metadata=metadata,
                metrics=domain_eval
            )

        run_meta["selected_models"] = selected_models_summary
        run_meta["model_save_status"] = "success"
        run_meta["status"] = "success"
        run_meta["end_time"] = datetime.now().isoformat()
        run_meta["duration_seconds"] = round(time.time() - start_ticks, 2)

        # Step 5: Save Reports & Pipeline Run Entry
        generate_reports(run_meta, eval_results)
        record_pipeline_run(run_meta)

        logger.info(f"=== AUTOMATED ML PIPELINE EXECUTION PASSED (Run ID: {run_id}) ===")
        return run_meta

    except Exception as e:
        run_meta["status"] = "failed"
        run_meta["end_time"] = datetime.now().isoformat()
        run_meta["errors"].append(str(e))
        record_pipeline_run(run_meta)
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        raise e
