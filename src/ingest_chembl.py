import json
from pathlib import Path

import requests

url = "https://www.ebi.ac.uk/chembl/api/data/activity.json"

limit = 100
offset = 0
page = 1
output_dir = Path("data/raw")
output_dir.mkdir(parents=True, exist_ok=True)

state_file = output_dir / "chembl_state.json"

if state_file.exists():
    with open(state_file, "r", encoding="utf-8") as f:
        state = json.load(f)
    page = state["page"]
    offset = state["offset"]
    print("Resuming from page: ", page)
else:
    page =1
    offset = 0
    print("Starting from the beginning")

while True:
    file_path = output_dir / f"page_{page}.json"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    else:
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

        print("---")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print("Saved:", file_path)
        print("---")

        if len(data["activities"]) < limit:
            break
    offset += limit
    page += 1
    state = {"page" : page, "offset" : offset}
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
