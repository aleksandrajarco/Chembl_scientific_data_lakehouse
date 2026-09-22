import json
from pathlib import Path

from config import API_URL, OUTPUT_DIR, PAGE_SIZE, STATE_FILE

import requests

def save_json(file_path :Path, data: dict) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def read_or_create_state(state_file: Path):
    if state_file.exists():
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        page = state["page"]
        offset = state["offset"]
        completed = state["completed"]
        if completed:
            print("pagination already completed")
            return None, None
        else:
            print("Resuming from page:", page)

    else:
        page = 1
        offset = 0

        print("Starting from the beginning")

    return page, offset

def open_page_file(file_path: Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def paginate_over_api(
        url: str,
        output_dir :Path,
        state_file: Path,
        page: int,
        limit: int,
        offset: int
    ) -> None:

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
                print(f"HTTP error:", {e})
                break

            except requests.exceptions.Timeout as e:
                print(f"Timeout error:{e}")
                break

            except requests.RequestException as e:
                print(f"Request error:{e}")
                break

            except ValueError as e:
                print(f"Invalid JSON response:{e}")
                break

            save_json(file_path, data)

            print("Saved:", file_path)

        records = data["activities"]

        print("Page:", page)
        print("Offset:", offset)
        print("Number of records:", len(records))

        if len(records) < limit:
            print("Last page reached.")
            state = {
                "page": page,
                "offset": offset,
                "completed": True}
            save_json(state_file, state)
            break

        offset += limit
        page += 1

        state = {
            "page": page,
            "offset": offset,
            "completed": False
        }

        save_json(state_file, state)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    page, offset = read_or_create_state(STATE_FILE)
    if page is not None:
        paginate_over_api(
            API_URL,
            OUTPUT_DIR,
            STATE_FILE,
            page,
            PAGE_SIZE,
            offset
        )


if __name__ == "__main__":
    main()
