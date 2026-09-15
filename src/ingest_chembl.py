import json
from pathlib import Path

import requests


url = "https://www.ebi.ac.uk/chembl/api/data/activity.json"


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def read_or_create_state(state_file):
    if state_file.exists():
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        page = state["page"]
        offset = state["offset"]

        print("Resuming from page:", page)

    else:
        page = 1
        offset = 0

        print("Starting from the beginning")

    return page, offset


def open_page_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def paginate_over_api(output_dir, state_file, page, limit, offset):

    while True:

        file_path = output_dir / f"page_{page}.json"

        if file_path.exists():

            print("File exists:", file_path)

            data = open_page_file(file_path)

        else:

            params = {
                "limit": limit,
                "offset": offset
            }

            try:
                response = requests.get(
                    url,
                    params=params,
                    timeout=30
                )

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

            save_json(file_path, data)

            print("Saved:", file_path)

        print("Page:", page)
        print("Offset:", offset)
        print("Number of records:", len(data["activities"]))

        if len(data["activities"]) < limit:
            print("Last page reached.")
            break

        offset += limit
        page += 1

        state = {
            "page": page,
            "offset": offset
        }

        save_json(state_file, state)


def main():

    limit = 100

    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    state_file = output_dir / "chembl_state.json"

    page, offset = read_or_create_state(state_file)

    paginate_over_api(
        output_dir,
        state_file,
        page,
        limit,
        offset
    )


if __name__ == "__main__":
    main()