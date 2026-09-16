import json
from pathlib import Path

def load_json(file_path):
    with open(file_path) as file:
        data = json.load(file)
    return data

def check_required_fields(records):
    required_fields = [
        "activity_id",
        "molecule_chembl_id",
        "target_chembl_id",
    ]
    problems =[]
    for record in records:
        for field in required_fields:
            if record.get(field) is None:
                problems.append({
                    "activity_id": record["activity_id"],
                    "field":field,
                })
    return problems

def check_duplicate_activity_ids(records):
    activity_ids =[
        record["activity_id"] for record in records
        if record["activity_id"] is not None
    ]

    duplicates =[]
    seen = set()

    for activity_id in activity_ids:
        if activity_id in seen:
            duplicates.append(activity_id)
        else:
            seen.add(activity_id)
    return duplicates

def main():
    file_path = Path("../data/transformed/combined.json")

    records = load_json(file_path)
    print("Total records: {}".format(len(records)))
    missing_fields = check_required_fields(records)
    duplicate_ids = check_duplicate_activity_ids(records)

    print("Missing fields: {}".format(missing_fields))
    print("Duplicate fields: {}".format(duplicate_ids))

    if missing_fields:
        print("Example of missing fields: {}".format(missing_fields[:3]))
    if duplicate_ids:
        print("Example of duplicate fields: {}".format(duplicate_ids[:3]))

if __name__ == "__main__":
    main()