from pyspark.sql import SparkSession
from src.spark_transform import transform_data

def test_transform_data(spark :SparkSession):
    test_data = [
        (
            1,
            "CHEMBL1",
            "CHEMBL2",
            "CHEMBL3",
            "IC50",
            "25.5",
            "nM",
            "7.2",
            "CHEMBL4",
        ),
    ]

    test_df = spark.createDataFrame(
        test_data,
        [
            "activity_id",
            "molecule_chembl_id",
            "target_chembl_id",
            "assay_chembl_id",
            "standard_type",
            "standard_value",
            "standard_units",
            "pchembl_value",
            "document_chembl_id",
        ],
    )
    result = transform_data(test_df)

    assert result.schema["standard_value"].dataType.typeName() == "double"
    assert result.schema["pchembl_value"].dataType.typeName() == "double"
    row = result.first()

    assert row["standard_value"] == 25.5
    assert row["pchembl_value"] == 7.2