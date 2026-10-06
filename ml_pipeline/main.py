import argparse
import sys
from ml_pipeline import config
from ml_pipeline.pipeline import run_pipeline
from ml_pipeline.pipeline_utils import get_logger

logger = get_logger("main")

def main():
    parser = argparse.ArgumentParser(description="Automated ML Pipeline CLI")
    parser.add_argument("--run-all", action="store_true", default=False, help="Run end-to-end ML pipeline for all models")
    parser.add_argument("--features-only", action="store_true", default=False, help="Run feature engineering layer only")
    parser.add_argument("--train-only", action="store_true", default=False, help="Run feature engineering & model training only")
    parser.add_argument("--evaluate-only", action="store_true", default=False, help="Run model training & evaluation only")
    parser.add_argument("--model-type", type=str, default=None, choices=["churn", "segmentation", "forecasting", "recommendation"], help="Specific model type to target")
    parser.add_argument("--version", type=str, default=None, help="Model version identifier")

    args = parser.parse_args()

    # Default behavior if no flag passed: --run-all
    run_all_flag = args.run_all or not (args.features_only or args.train_only or args.evaluate_only)

    logger.info("Initializing Automated ML Pipeline Execution...")
    
    result = run_pipeline(
        run_all=run_all_flag,
        features_only=args.features_only,
        train_only=args.train_only,
        evaluate_only=args.evaluate_only,
        target_model_type=args.model_type
    )

    print("\n=====================================================")
    print("      AUTOMATED ML PIPELINE EXECUTION SUMMARY        ")
    print("=====================================================")
    print(f"Run ID             : {result.get('run_id')}")
    print(f"Status             : {result.get('status')}")
    print(f"Feature Status     : {result.get('feature_status')}")
    print(f"Training Status    : {result.get('training_status')}")
    print(f"Evaluation Status  : {result.get('evaluation_status')}")
    print(f"Model Save Status  : {result.get('model_save_status')}")
    print(f"Selected Models    : {result.get('selected_models')}")
    print("=====================================================\n")

if __name__ == "__main__":
    main()
