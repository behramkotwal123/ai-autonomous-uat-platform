# Demo Travel API — Integration Documentation

## 1. Booking API

### Endpoint

`POST /booking`

### Purpose

Creates a travel booking for a passenger.

### Request Fields

| Field          | Required | Description                   |
| -------------- | -------- | ----------------------------- |
| passenger_name | Yes      | Passenger name                |
| fare           | Yes      | Fare selected for the booking |
| baggage        | No       | Optional baggage selection    |
| seat           | No       | Optional seat selection       |

### Successful Response

A successful booking returns:

* `success: true`
* `booking_status: CONFIRMED`
* `pnr`
* `passenger_name`
* `fare`
* `baggage`
* `seat`

### Validation Errors

#### INVALID_PAX

Returned when `passenger_name` is missing or empty.

#### INVALID_FARE

Returned when the selected fare is unavailable.

#### INVALID_BAGGAGE

Returned when the selected baggage option is unavailable.

#### INVALID_SEAT

Returned when the selected seat is unavailable.

---

# 2. Flight Search API

### Endpoint

`GET /search`

### Purpose

Searches for available flights between an origin and destination.

### Request Parameters

| Parameter   | Required | Description              |
| ----------- | -------- | ------------------------ |
| origin      | Yes      | Origin airport code      |
| destination | Yes      | Destination airport code |

### Successful Response

A successful search returns:

* `success: true`
* `origin`
* `destination`
* `results`

The `results` array contains available flights.

### No Flights

When no flights are available for the requested route, the API returns:

* `success: false`
* `error_code: NO_FLIGHTS`
* `message`

---

# 3. UAT Validation Rules

The UAT platform validates API responses against the expected response defined in each test scenario.

Validation includes:

1. HTTP status code
2. Response fields
3. Expected field values
4. API success status
5. Error codes for negative scenarios

A test passes only when the actual response satisfies all defined expectations.

The deterministic UAT engine is the source of truth for PASS/FAIL.

AI diagnosis must not override the deterministic test result.

---

# 4. AI Diagnostic Context

When a UAT test fails, the AI diagnostic engine may use:

* UAT request
* Expected response
* Actual response
* Failed field
* API endpoint
* Relevant API documentation

The AI should distinguish between:

* Confirmed facts
* Likely causes
* Possible causes

The AI must not invent information that is not supported by the available evidence or API documentation.
