from fastapi import FastAPI


app = FastAPI(title="Demo Travel API")


@app.get("/")
def home():

    return {
        "message": "Demo Travel API is running"
    }


@app.post("/booking")
def create_booking(booking: dict):

    passenger_name = booking.get("passenger_name")
    fare = booking.get("fare")
    baggage = booking.get("baggage")
    seat = booking.get("seat")


    # ---------------------------------------------
    # Validate passenger
    # ---------------------------------------------

    if not passenger_name:

        return {
            "success": False,
            "error_code": "INVALID_PAX",
            "message": "Passenger name is required"
        }


    # ---------------------------------------------
    # Validate fare
    # ---------------------------------------------

    if fare == "INVALID":

        return {
            "success": False,
            "error_code": "INVALID_FARE",
            "message": "The selected fare is no longer available"
        }


    # ---------------------------------------------
    # Validate baggage
    # ---------------------------------------------

    if baggage == "INVALID":

        return {
            "success": False,
            "error_code": "INVALID_BAGGAGE",
            "message": "The selected baggage option is unavailable"
        }


    # ---------------------------------------------
    # Validate seat
    # ---------------------------------------------

    if seat == "INVALID":

        return {
            "success": False,
            "error_code": "INVALID_SEAT",
            "message": "The selected seat is unavailable"
        }


    # ---------------------------------------------
    # Successful booking
    # ---------------------------------------------

    return {
        "success": True,
        "booking_status": "CONFIRMED",
        "pnr": "DEMO123",
        "passenger_name": passenger_name,
        "fare": fare,
        "baggage": baggage,
        "seat": seat
    }
# --------------------------------------------------
# FLIGHT SEARCH
# --------------------------------------------------

@app.get("/search")
def search_flights(
    origin: str,
    destination: str
):

    # --------------------------------------------------
    # NO FLIGHTS AVAILABLE
    # --------------------------------------------------

    if destination == "XYZ":

        return {
            "success": False,
            "error_code": "NO_FLIGHTS",
            "message": "No flights available for this route"
        }

    # --------------------------------------------------
    # SUCCESSFUL SEARCH
    # --------------------------------------------------

    return {
        "success": True,
        "origin": origin,
        "destination": destination,
        "results": [
            {
                "flight_number": "AI101",
                "airline": "Air India",
                "departure": "08:00",
                "arrival": "10:30"
            },
            {
                "flight_number": "EK501",
                "airline": "Emirates",
                "departure": "10:15",
                "arrival": "12:45"
            }
        ]
    }