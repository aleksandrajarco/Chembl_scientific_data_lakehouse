from pathlib import Path


API_URL = "https://www.ebi.ac.uk/chembl/api/data/activity.json"

PAGE_SIZE = 5

OUTPUT_DIR = Path("data/raw")
STATE_FILE = Path("data/chembl_state.json")
SPARK_OUTPUT_DIR = Path.home() / "chembl_spark_output"