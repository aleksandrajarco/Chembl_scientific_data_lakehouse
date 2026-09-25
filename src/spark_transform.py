from pathlib import Path
import logging
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col

from src.config import SPARK_OUTPUT_DIR
from src.quality.check_activity import (
    check_duplicate_activity_ids_df,
    check_required_fields_df,
    check_invalid_numerical_values
)

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

SELECTED_COLUMNS = (
    "activity_id",
    "molecule_chembl_id",
    "target_chembl_id",
    "assay_chembl_id",
    "standard_type",
    "standard_value",
    "standard_units",
    "pchembl_value",
    "document_chembl_id",
)


def get_input_files(input_dir: Path) -> list[Path]:
    """Find input JSON files."""
    input_files = sorted(input_dir.glob("page_*.json"))

    if not input_files:
        raise FileNotFoundError(
            f"No input files found in: {input_dir}"
        )

    logger.info("Input directory: %s", input_dir)
    logger.info("Files found: %s", len(input_files))
    return input_files

def create_spark_session() -> SparkSession:
    """Create and configure Spark session."""
    return (
        SparkSession.builder
        .appName("ChEMBLTransformation")
        .master("local[*]")
        .config("spark.hadoop.fs.permissions.umask-mode", "022")
        .config("spark.hadoop.fs.file.impl.disable.cache", "true")
        .getOrCreate()
    )


def read_json(
    spark: SparkSession,
    input_files: list[Path],
) -> DataFrame:
    """Read ChEMBL JSON files into a Spark DataFrame."""
    return (
        spark.read
        .option("multiLine", True)
        .json([str(file) for file in input_files])
    )


def transform_data(df: DataFrame) -> DataFrame:
    """Select columns required for the Silver dataset."""
    return (
        df.select(*SELECTED_COLUMNS)
        .withColumn("standard_value", col("standard_value").cast("double"))
        .withColumn("pchembl_value", col("pchembl_value").cast("double"))
    )


def write_parquet(
    df: DataFrame,
    output_path: Path,
) -> None:
    """Write DataFrame to Parquet."""
    (
        df.write
        .mode("overwrite")
        .parquet(str(output_path))
    )

    logger.info("Parquet data written to: %s", output_path)

def inspect_dataframe(df: DataFrame) -> None:
    """Display basic DataFrame information."""
    df.show(10, truncate=False)
    df.printSchema()

    logger.info("Rows: %s", df.count())
    logger.info("Columns: %s", df.columns)
    logger.info("Partitions: %s", df.rdd.getNumPartitions())


def explain_filter(
    df: DataFrame,
    value: str,
) -> None:
    """Show physical plan for a filtered DataFrame."""
    (
        df.filter(df.standard_type == value)
        .select("activity_id", "standard_value")
        .explain()
    )


def write_partitioned_parquet(
    df: DataFrame,
    output_path: Path,
) -> None:
    """Write DataFrame to partitioned Parquet."""

    (
        df.write
        .mode("overwrite")
        .partitionBy("standard_type")
        .parquet(str(output_path))
    )

    logger.info("Partitioned Parquet data written to: %s", output_path)

def main() -> None:
    project_root = Path(__file__).resolve().parents[1]

    input_dir = project_root / "data" / "silver"
    silver_path = SPARK_OUTPUT_DIR / "silver_parquet"
    partitioned_path = SPARK_OUTPUT_DIR / "silver_partitioned"

    input_files = get_input_files(input_dir)

    spark = create_spark_session()

    try:
        df = read_json(spark, input_files)
        invalid_standard_values = check_invalid_numerical_values(df, "standard_value")
        logger.info("Invalid standard values: %s", invalid_standard_values)

        if invalid_standard_values > 0:
            raise ValueError(
                f"Data quality check failed: "
                f"{invalid_standard_values} invalid standard values found"
            )
        invalid_pchembl_values = check_invalid_numerical_values(df, "pchembl_value")
        logger.info("Invalid pchembl values: %s", invalid_pchembl_values)

        if invalid_pchembl_values > 0:
            raise ValueError(
                f"Data quality check failed: "
                f"{invalid_pchembl_values} invalid pchembl values found"
            )

        transformed_df = transform_data(df)

        missing_required_fields = check_required_fields_df(
            transformed_df
        )

        logger.info("Missing required fields: %s", missing_required_fields)

        if missing_required_fields > 0:
            raise ValueError(
                f"Data quality check failed: "
                f"{missing_required_fields} rows have missing required fields"
            )

        duplicate_activity_ids = check_duplicate_activity_ids_df(
            transformed_df
        )
        if duplicate_activity_ids > 0:
            raise ValueError(
                f"Data quality check failed: "
                f"{duplicate_activity_ids} duplicate activity IDs found"
            )
        logger.info("Transformed DataFrame preview:\\n%s", transformed_df._show_string(n=10, truncate=False))

        write_parquet(
            transformed_df,
            silver_path,
        )

        silver_df = spark.read.parquet(
            str(silver_path)
        )

        inspect_dataframe(silver_df)

        explain_filter(
            silver_df,
            "KI",
        )

        write_partitioned_parquet(
            transformed_df,
            partitioned_path,
        )

        partitioned_df = spark.read.parquet(
            str(partitioned_path)
        )

        explain_filter(
            partitioned_df,
            "KI",
        )

        logger.info("Partitioned Spark partitions: %s", partitioned_df.rdd.getNumPartitions())

        logger.info("Silver Spark partitions: %s", silver_df.rdd.getNumPartitions())

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
