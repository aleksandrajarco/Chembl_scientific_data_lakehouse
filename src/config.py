from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

API_URL = "https://www.ebi.ac.uk/chembl/api/data/activity.json"

PAGE_SIZE = 5

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"
STATE_FILE = PROJECT_ROOT / "data" / "chembl_state.json"
SPARK_OUTPUT_DIR = Path.home() / "chembl_spark_output"
