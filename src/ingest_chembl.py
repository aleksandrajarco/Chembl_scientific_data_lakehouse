import json
import logging
from http import HTTPStatus
from idlelib.rpc import request_queue
from pathlib import Path
from typing import Any
import time
import requests

from config import (
    API_URL,
    MAX_RETRIES,
    OUTPUT_DIR,
    PAGE_SIZE,
    RETRY_DELAY,
    STATE_FILE,
)
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

def fetch_page(
    url: str,
    limit: int,
    offset: int
) -> dict:
    """Fetch one page from Chembl API. """
    params ={
        "limit": limit,
        "offset": offset
    }
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = request.get(url, params=params, timeout=30)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            if (isinstance(e, requests.exceptions.ConnectionError)
                or isinstance(e, requests.exceptions.Timeout)
                or (e.response is not None and 599 >= e.response.status_code >= 500)):
                    logger.warning("Request error (attempt %s/%s):%s", attempt, MAX_RETRIES, e)
                    if attempt == MAX_RETRIES:
                        raise
                    time.sleep(RETRY_DELAY * 2 ** (attempt - 1))

            else:
                logger.error("Request error: %s", e)

def save_json(file_path: Path, data: dict[str, Any]) -> None:
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def read_or_create_state(state_file: Path) -> tuple[int, int] | None:
    if state_file.exists():
        with state_file.open("r", encoding="utf-8") as file:
            state: dict[str, Any] = json.load(file)

        page = state["page"]
        offset = state["offset"]
        completed = state["completed"]
        if completed:
            logger.info("Pagination already completed")
            return None
        else:
            logger.info("Resuming from page: %s", page)

    else:
        page = 1
        offset = 0

        logger.info("Starting from the beginning")

    return page, offset


def open_page_file(file_path: Path) -> dict[str, Any]:
    with file_path.open("r", encoding="utf-8") as file:
        data: dict[str, Any] = json.load(file)
    return data


def paginate_over_api(
    url: str,
    output_dir: Path,
    state_file: Path,
    page: int,
    limit: int,
    offset: int,
) -> None:
    while True:
        file_path = output_dir / f"page_{page}.json"
        if file_path.exists():
            logger.info("File exists: %s", file_path)
            data = open_page_file(file_path)
        else:
            params = {
                "limit": limit,
                "offset": offset,
            }

            try:
                data =fetch_page(url, limit, params)

            except requests.exceptions.HTTPError as e:
                logger.exception("HTTP error while fetching page %s", page)
                break

            except requests.exceptions.Timeout as e:
                logger.exception("Timeout while fetching page %s", page)
                break

            except requests.RequestException as e:
                logger.exception("Request error while fetching page %s", page)
                break

            except ValueError as e:
                logger.exception("Invalid JSON response for page %s", page)
                break

            save_json(file_path, data)

            logger.info("Saved: %s", file_path)

        records = data["activities"]

        logger.info("Page: %s", page)
        logger.info("Offset: %s", offset)
        logger.info("Number of records: %s", len(records))

        if len(records) < limit:
            logger.info("Last page reached")
            state = {
                "page": page,
                "offset": offset,
                "completed": True,
            }
            save_json(state_file, state)
            break

        offset += limit
        page += 1

        state = {
            "page": page,
            "offset": offset,
            "completed": False,
        }

        save_json(state_file, state)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state = read_or_create_state(STATE_FILE)
    if state is not None:
        page, offset = state
        paginate_over_api(
            API_URL,
            OUTPUT_DIR,
            STATE_FILE,
            page,
            PAGE_SIZE,
            offset,
        )


if __name__ == "__main__":
    main()
