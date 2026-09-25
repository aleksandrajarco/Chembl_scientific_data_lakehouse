import pytest
from pyspark.sql import SparkSession

@pytest.fixture
def spark():
    spark = (SparkSession
    .builder
    .master("local[*]")
    .appName("unit_test")
    .getOrCreate()
    )
    yield spark
    spark.stop()