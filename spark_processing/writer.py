import os
import json
from datetime import datetime
from . import config

def write_parquet(df, output_path, partition_by=None):
    """
    Writes a DataFrame to Parquet format safely.
    """
    writer = df.write.mode("overwrite")
    if partition_by:
        writer = writer.partitionBy(partition_by)
    writer.parquet(output_path)

def generate_quality_report(dataframes):
    """
    Generates a Spark data quality report.
    dataframes: dict of {name: df}
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "datasets": {}
    }
    
    for name, df in dataframes.items():
        total_records = df.count()
        
        # Count valid vs invalid if is_valid flag exists
        if "is_valid" in df.columns:
            valid_records = df.filter(df.is_valid == True).count()
            invalid_records = total_records - valid_records
        else:
            valid_records = total_records
            invalid_records = 0
            
        # Count duplicates (assuming first column is primary key)
        pk_col = df.columns[0]
        duplicate_records = total_records - df.select(pk_col).dropDuplicates().count()
        
        # Null counts for important columns
        null_counts = {}
        for col_name in df.columns[:5]: # Top 5 columns
            null_counts[col_name] = df.filter(df[col_name].isNull()).count()
            
        report["datasets"][name] = {
            "total_records": total_records,
            "valid_records": valid_records,
            "invalid_records": invalid_records,
            "duplicate_records": duplicate_records,
            "null_counts": null_counts
        }
        
    report_path = os.path.join(config.QUALITY_DIR, "data_quality_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)
        
    print(f"Data quality report written to {report_path}")
