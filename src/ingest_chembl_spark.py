import logging

from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("ChemblIngestion")
        .master("local[*]")
        .getOrCreate()
    )
    df = spark.read.option("multiLine", True).json(
        "data/transformed/page_1.json"
    )
    logger.info("Number of rows: %s", df.count())
    df.printSchema()
    df.show(5, truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()
