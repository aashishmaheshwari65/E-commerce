from pyspark.sql import SparkSession
import os
import sys
from . import config

def create_spark_session():
    # Check for Java
    if "JAVA_HOME" not in os.environ:
        print("ERROR: JAVA_HOME is not set. Java 8 or 11 is required for PySpark on Windows.")
        print("Please install Java, set JAVA_HOME, and add %JAVA_HOME%\\bin to PATH.")
        sys.exit(1)
        
    spark = SparkSession.builder \
        .appName(config.APP_NAME) \
        .master(config.MASTER_URL) \
        .config("spark.sql.shuffle.partitions", config.SHUFFLE_PARTITIONS) \
        .config("spark.sql.session.timeZone", "UTC") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel(config.LOG_LEVEL)
    return spark
