
from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_search_rejects_unsupported_cabin():
    response = client.get(
        "/search",
        params={
            "origin": "DEL",
            "destination": "LHR",
            "cabin": "UNSUPPORTED",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "INVALID_CABIN"
    assert "ECONOMY, BUSINESS, or FIRST" in data["message"]


def test_search_accepts_supported_cabin():
    response = client.get(
        "/search",
        params={
            "origin": "DEL",
            "destination": "LHR",
            "cabin": "ECONOMY",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["cabin"] == "ECONOMY"


def test_search_no_flights():
    response = client.get(
        "/search",
        params={
            "origin": "DEL",
            "destination": "XYZ",
        },
    )

    assert response.status_code == 200
    assert response.json()["error_code"] == "NO_FLIGHTS"
