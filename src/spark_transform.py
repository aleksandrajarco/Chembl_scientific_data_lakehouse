from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col

from config import SPARK_OUTPUT_DIR
from quality.check_activity import (
    check_duplicate_activity_ids_df,
    check_required_fields_df,
    check_invalid_numerical_values
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

    print(f"Input directory: {input_dir}")
    print(f"Files found: {len(input_files)}")

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
        .withColumn("pchemb_value", col("pchembl_value").cast("double"))
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

    print(f"Parquet data written to: {output_path}")


def inspect_dataframe(df: DataFrame) -> None:
    """Display basic DataFrame information."""
    df.show(10, truncate=False)
    df.printSchema()

    print("Rows:", df.count())
    print("Columns:", df.columns)
    print("Partitions:", df.rdd.getNumPartitions())


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

    print(f"Partitioned Parquet data written to: {output_path}")


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
        print(f"Invalid standard values: {invalid_standard_values}")
        if invalid_standard_values > 0:
            raise ValueError(
                f"Data quality check failed: "
                f"{invalid_standard_values} invalid standard values found"
            )
        invalid_pchembl_values = check_invalid_numerical_values(df, "pchembl_value")
        print(
            f"Invalid pchembl values: "
            f"{invalid_pchembl_values}"
        )
        if invalid_pchembl_values > 0:
            raise ValueError(
                f"Data quality check failed: "
                f"{invalid_pchembl_values} invalid pchembl values found"
            )
        transformed_df = transform_data(df)

        missing_required_fields = check_required_fields_df(
            transformed_df
        )

        print(f"Missing required fields: {missing_required_fields}")

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
        transformed_df.show(10, truncate=False)

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

        print(
            "Partitioned Spark partitions:",
            partitioned_df.rdd.getNumPartitions(),
        )

        print(
            "Silver Spark partitions:",
            silver_df.rdd.getNumPartitions(),
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
