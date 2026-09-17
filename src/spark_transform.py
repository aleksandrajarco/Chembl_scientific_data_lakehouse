from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, upper


MIN_ACTIVITY_ID = 31865

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


def main() -> None:
    project_root = Path(__file__).resolve().parents[0]
    input_dir = project_root / "data" / "transformed"

    input_files = sorted(input_dir.glob("page_*.json"))

    if not input_files:
        raise FileNotFoundError(
            f"No input files found in: {input_dir}"
        )

    print(f"Input directory: {input_dir}")
    print(f"Files found: {len(input_files)}")

    for file in input_files:
        print(f"  - {file.name}")

    spark = (
        SparkSession.builder
        .appName("ChEMBLTransformation")
        .master("local[*]")
        .getOrCreate()
    )

    try:
        df = (
            spark.read
            .option("multiLine", True)
            .json([str(file) for file in input_files])
        )

        transformed_df = (
            df
            .select(*SELECTED_COLUMNS)
            .withColumn(
                "standard_type",
                upper(col("standard_type"))
            )
            .filter(
                col("activity_id") < MIN_ACTIVITY_ID
            )
            .withColumn(
                "pchembl_value_double",
                col("pchembl_value").cast("double")
            )
            .withColumn(
                "activity_id_string",
                col("activity_id").cast("string")
            )
        )

        transformed_df.show(10, truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()