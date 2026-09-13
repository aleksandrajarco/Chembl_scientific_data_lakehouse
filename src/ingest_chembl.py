import json
from pathlib import Path

import requests

url = "https://www.ebi.ac.uk/chembl/api/data/activity.json"

limit = 100
offset = 0
page = 1
output_dir = Path("data/raw")
output_dir.mkdir(parents=True, exist_ok=True)

while True:
    params = {
        "limit": limit,
        "offset": offset
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as e:
        print("HTTP error:", e)
        break
    except requests.exceptions.Timeout as e:
        print("Timeout error:", e)
        break
    except requests.RequestException as e:
        print("Request error:", e)
        break

    except ValueError as e:
        print("Value error:", e)
        break

    print("Page:", page)
    print("Offset:", offset)
    print("Number of records:", len(data["activities"]))
    print("Page metadata:", data["page_meta"])

    for activity in data["activities"]:
        print(activity["activity_id"])

    print("---")

    file_path = output_dir / f"page_{page}.json"
    if file_path.exists():
        print("file exists:", file_path)

    else:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    print("Saved:", file_path)
    print("---")

    if len(data["activities"]) < limit:
        break
    offset += limit
    page += 1

