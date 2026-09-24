from pathlib import Path

from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import col, upper, broadcast
from config import SPARK_OUTPUT_DIR

def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    input_dir = project_root / "data" / "silver"
    input_files = sorted(input_dir.glob("page_*.json"))
    output_dir = SPARK_OUTPUT_DIR / "silver_parquet"
    if not input_files:
        raise FileNotFoundError(
            f"No input files found in: {input_dir}"
        )

    print(f"Input directory: {input_dir}")
    print(f"Files found: {len(input_files)}")

    #for file in input_files:
        #print(f"  - {file.name}")


    spark = (
        SparkSession.builder
        .appName("ChEMBLTransformation")
        .master("local[*]")
        .config("spark.hadoop.fs.permissions.umask-mode", "022")
        .config("spark.hadoop.fs.file.impl.disable.cache", "true")
        .getOrCreate()
    )

    try:
        df = (
            spark.read
            .option("multiLine", True)
            .json([str(file) for file in input_files])
        )

        rows = (
                [Row(key="common", value=i) for i in range(1000000)]
                + [Row(key="rare1", value=1)]
                + [Row(key="rare2", value=2)]
                + [Row(key="rare3", value=3)]
        )
        skewed_df = spark.createDataFrame(rows)

        lookup_rows =(
            [Row(key="common", description = "common key")]+
            [Row(key="rare1", description = "rare key")]+
            [Row(key="rare2", description = "rare key")]+
            [Row(key="rare3", description = "rare key")]
        )
        lookup_df = spark.createDataFrame(lookup_rows)
        joined_df = skewed_df.join(
            lookup_df,
            on="key",
            how="inner"
        )
        broadcast_joined_df = skewed_df.join(
            broadcast(lookup_df),
            on="key",
            how="inner"
        )

        print("Records:", skewed_df.count())

        skewed_df.groupBy("key").count().show()

        grouped_df = skewed_df.groupBy("key").count()
        grouped_df.show()

    finally:
        input("Press Enter to stop Spark...")
        spark.stop()

if __name__ == "__main__":
    main()
