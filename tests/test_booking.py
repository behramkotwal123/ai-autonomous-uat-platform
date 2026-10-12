from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_successful_booking():

    request = {
        "passenger_name": "Behram",
        "fare": "ECONOMY"
    }

    response = client.post("/booking", json=request)

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["booking_status"] == "CONFIRMED"
    assert data["pnr"] is not None


def test_missing_passenger():

    request = {
        "passenger_name": "",
        "fare": "ECONOMY"
    }

    response = client.post("/booking", json=request)

    data = response.json()

    assert data["success"] is False
    assert data["error_code"] == "INVALID_PAX"


def test_invalid_fare():

    request = {
        "passenger_name": "Behram",
        "fare": "INVALID"
    }

    response = client.post("/booking", json=request)

    data = response.json()

    assert data["success"] is False
    assert data["error_code"] == "INVALID_FARE"

    
def test_missing_fare():
    request = {"passenger_name": "Behram"}
    response = client.post("/booking", json=request)
    data = response.json()

    assert response.status_code == 200
    assert data["success"] is False
    assert data["error_code"] == "INVALID_FARE"
