from pyspark.sql import SparkSession
from src.quality.check_activity import check_invalid_numerical_values, check_required_fields_df, check_duplicate_activity_ids_df

def test_invalid_numerical_values(spark: SparkSession):
    test_data = [
        (1,"25.5"),
        (2, "not_a_number"),
        (3, "100"),
        (4, None)
    ]
    test_df = spark.createDataFrame(test_data, ["activity_id", "standard_value"])
    result  = check_invalid_numerical_values(test_df, "standard_value")
    assert result == 1

def test_check_required_fields(spark: SparkSession):
    test_data = [
    (1, 1, 1),
    (2, None, None),
    (3, 3, None)
    ]
    test_df = spark.createDataFrame(test_data, ["activity_id", "molecule_chembl_id", "target_chembl_id"])
    result = check_required_fields_df(test_df)
    assert result == 2

def test_check_duplicate_activity_ids(spark: SparkSession):
    test_data = [
        (1,),
        (1,),
        (2,),
        (3,),
        (3,),
        (4,)
    ]
    test_df = spark.createDataFrame(test_data, ["activity_id"])
    result = check_duplicate_activity_ids_df(test_df)
    assert result == 2