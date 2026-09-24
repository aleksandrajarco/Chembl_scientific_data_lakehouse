import json
from pathlib import Path
from typing import Any

FIELDS = (
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


def get_raw_files(input_dir: Path) -> list[Path]:
    return sorted(input_dir.glob("page_*.json"))


def load_json(file_path: Path) -> Any:
    with file_path.open(encoding="utf-8") as json_file:
        data: Any = json.load(json_file)
    return data


def extract_activities(data: dict[str, Any]) -> list[dict[str, Any]]:
    return data["activities"]


def transform_activities(
    activities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    transformed_activities: list[dict[str, Any]] = []
    for activity in activities:
        record: dict[str, Any] = {}
        for field in FIELDS:
            record[field] = activity.get(field)
        if record["standard_type"]:
            record["standard_type"] = record["standard_type"].upper()
        transformed_activities.append(record)
    return transformed_activities


def save_transformed(
    file_path: Path,
    data: list[dict[str, Any]],
) -> None:
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def main() -> None:
    input_dir = Path("data/raw")
    output_dir = Path("data/transformed")
    raw_files = get_raw_files(input_dir)
    print("Found", len(raw_files), "raw files")

    for input_file in raw_files:
        output_file = output_dir / input_file.name
        data = load_json(input_file)
        activities = extract_activities(data)
        transformed = transform_activities(activities)
        save_transformed(output_file, transformed)
        print("Transformed:", input_file, "-->", output_file)
        print("Records:", len(transformed))
    combined_file = output_dir / "combined.json"
    combined = combine_transformed_files(output_dir)
    save_transformed(combined_file, combined)
    print("Total records:", len(combined))
    print("Saved:", combined_file)


def combine_transformed_files(input_dir: Path) -> list[dict[str, Any]]:
    combined_files: list[dict[str, Any]] = []
    for file in sorted(input_dir.glob("page_*.json")):
        data = load_json(file)
        combined_files.extend(data)

    return combined_files


if __name__ == "__main__":
    main()
