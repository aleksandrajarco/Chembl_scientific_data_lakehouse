from unittest.mock import patch, Mock, call
from src.ingest_chembl import fetch_page
import requests

MOCK_URL = "http://example.com"
MOCK_LIMIT = 2
MOCK_OFFSET = 0
MOCK_DATA = {
        "page_meta": {
            "limit": 2,
            "offset": 0,
            "next": None
        },
        "activities": [
            {
                "activity_id": 1,
                "standard_value": "50"
            },
            {
                "activity_id": 2,
                "standard_value": "100"
            }
        ]
    }


def make_response(data :dict =MOCK_DATA):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = data
    return mock_response


def test_fetch_page_returns_json_and_passes_request_parameters():
    response = make_response()

    with patch("src.ingest_chembl.requests.get") as mock_get:
        mock_get.return_value = response
        result = fetch_page(MOCK_URL, MOCK_LIMIT, MOCK_OFFSET)
        assert result == MOCK_DATA
        mock_get.assert_called_once_with(
            MOCK_URL,
            params={"limit": MOCK_LIMIT, "offset": MOCK_OFFSET},
            timeout=30,
        )

def test_fetch_page_retries_on_connection_error():
    response = make_response()
    with (
        patch("src.ingest_chembl.requests.get") as mock_get,
        patch("src.ingest_chembl.time.sleep") as mock_sleep,
    ):
        #mock_get.return_value = mock_response
        mock_get.side_effect = [
            requests.exceptions.ConnectionError(),
            requests.exceptions.ConnectionError(),
            response
        ]
        result = fetch_page(MOCK_URL, MOCK_LIMIT, MOCK_OFFSET)
        assert result == MOCK_DATA
        assert mock_get.call_args_list == [
            call(
                MOCK_URL,
                params={"limit": MOCK_LIMIT, "offset": MOCK_OFFSET},
                timeout=30,
            )
        ] * 3
        assert mock_sleep.call_count == 2

