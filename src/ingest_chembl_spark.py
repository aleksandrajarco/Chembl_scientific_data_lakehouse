from pyspark.sql import SparkSession


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
    print("Number of rows: ", df.count())
    df.printSchema()
    df.show(5, truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()
