import json
from pathlib import Path
from typing import Any


def load_json(file_path: Path) -> list[dict[str, Any]]:
    with file_path.open(encoding="utf-8") as file:
        data: list[dict[str, Any]] = json.load(file)
    return data


def check_required_fields(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    required_fields = [
        "activity_id",
        "molecule_chembl_id",
        "target_chembl_id",
    ]
    problems = []
    for record in records:
        for field in required_fields:
            if record.get(field) is None:
                problems.append({
                    "activity_id": record.get("activity_id"),
                    "field": field,
                })
    return problems


def check_duplicate_activity_ids(
    records: list[dict[str, Any]],
) -> list[str | int]:
    activity_ids = [
        record.get("activity_id") for record in records
        if isinstance(record.get("activity_id"), (str, int))
    ]

    duplicates: list[str | int] = []
    seen = set()

    for activity_id in activity_ids:
        if activity_id in seen:
            duplicates.append(activity_id)
        else:
            seen.add(activity_id)
    return duplicates


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    file_path = project_root / "data" / "silver" / "combined.json"

    records = load_json(file_path)
    print(f"Total records: {len(records)}")
    missing_fields = check_required_fields(records)
    duplicate_ids = check_duplicate_activity_ids(records)

    print(f"Missing fields: {missing_fields}")
    print(f"Duplicate fields: {duplicate_ids}")

    if missing_fields:
        print(f"Example of missing fields: {missing_fields[:3]}")
    if duplicate_ids:
        print(f"Example of duplicate fields: {duplicate_ids[:3]}")


if __name__ == "__main__":
    main()
