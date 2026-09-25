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
        (
            2,
            "CHEMBL5",
            "CHEMBL6",
            "CHEMBL7",
            "IC50",
            None,
            "nM",
            None,
            "CHEMBL8",
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
    rows = result.collect()

    assert rows[0]["standard_value"] == 25.5
    assert rows[0]["pchembl_value"] == 7.2
    assert rows[1]["standard_value"] is None
    assert rows[1]["pchembl_value"] is None
