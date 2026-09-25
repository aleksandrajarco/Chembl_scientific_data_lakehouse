from pyspark.sql import DataFrame
from pyspark.sql.functions import col

def check_required_fields_df(df: DataFrame) -> int:
    invalid = df.filter(
        df["activity_id"].isNull()
        | df["molecule_chembl_id"].isNull()
        | df["target_chembl_id"].isNull()
    )
    return invalid.count()

def check_duplicate_activity_ids_df(df: DataFrame) -> int:
    duplicates = df.groupBy("activity_id").count().filter("count >1")
    return duplicates.count()

def check_invalid_numerical_values(df: DataFrame, col_name : str) -> int:
    invalid = df.filter(
        col(col_name).isNotNull()
        & col(col_name).try_cast("double").isNull()
    )
    return invalid.count()
