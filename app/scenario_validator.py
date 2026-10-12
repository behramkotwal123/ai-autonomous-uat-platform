import re

from app.document_retriever import load_document


ALLOWED_METHODS = {
    "GET",
    "POST",
    "PUT",
    "DELETE"
}


def contains_placeholder(value):

    if not isinstance(value, str):
        return False

    placeholder_patterns = [
        r"<[^>]+>",
        r"\bTBD\b",
        r"\bTODO\b",
        r"\bUNKNOWN\b"
    ]

    for pattern in placeholder_patterns:

        if re.search(
            pattern,
            value,
            re.IGNORECASE
        ):
            return True

    return False


def validate_values(value, path=""):

    errors = []

    if isinstance(value, dict):

        for key, item in value.items():

            current_path = (
                f"{path}.{key}"
                if path
                else key
            )

            errors.extend(
                validate_values(
                    item,
                    current_path
                )
            )

    elif isinstance(value, list):

        for index, item in enumerate(value):

            current_path = (
                f"{path}[{index}]"
            )

            errors.extend(
                validate_values(
                    item,
                    current_path
                )
            )

    elif isinstance(value, str):

        if contains_placeholder(value):

            errors.append(
                f"{path}: contains a placeholder value '{value}'"
            )

    return errors


def validate_semantic_rules(
    endpoint,
    request,
    expected
):

    errors = []

    # -----------------------------------------
    # SEARCH API
    # -----------------------------------------

    if endpoint == "/search":

        success = expected.get(
            "success"
        )

        # -------------------------------------
        # SUCCESSFUL SEARCH
        # -------------------------------------

        if success is True:

            # The scenario defines the business
            # expectation that a successful search
            # should occur.
            #
            # Actual flight results are dynamic
            # response data and will be validated
            # by the deterministic execution engine.

            if "origin" not in request:

                errors.append(
                    "Successful search request "
                    "must contain origin."
                )

            if "destination" not in request:

                errors.append(
                    "Successful search request "
                    "must contain destination."
                )

            # Expected origin must match
            # request origin when provided.

            if (
                "origin" in request
                and "origin" in expected
                and request["origin"]
                != expected["origin"]
            ):

                errors.append(
                    "Expected origin must match "
                    "the request origin."
                )

            # Expected destination must match
            # request destination when provided.

            if (
                "destination" in request
                and "destination" in expected
                and request["destination"]
                != expected["destination"]
            ):

                errors.append(
                    "Expected destination must "
                    "match the request destination."
                )

        # -------------------------------------
        # NO-FLIGHT SEARCH
        # -------------------------------------

        if success is False:

            if expected.get(
                "error_code"
            ) != "NO_FLIGHTS":

                errors.append(
                    "Failed search must use "
                    "error_code NO_FLIGHTS."
                )

            if request.get(
                "destination"
            ) != "XYZ":

                errors.append(
                    "The demo API's no-flight "
                    "scenario must use destination XYZ."
                )

    # -----------------------------------------
    # BOOKING API
    # -----------------------------------------

    if endpoint == "/booking":

        success = expected.get(
            "success"
        )

        # -------------------------------------
        # SUCCESSFUL BOOKING
        # -------------------------------------

        if success is True:

            if expected.get(
                "booking_status"
            ) != "CONFIRMED":

                errors.append(
                    "Successful booking must "
                    "have booking_status CONFIRMED."
                )

            if "passenger_name" not in request:

                errors.append(
                    "Successful booking request "
                    "must contain passenger_name."
                )

            if "fare" not in request:

                errors.append(
                    "Successful booking request "
                    "must contain fare."
                )

            # Expected passenger must match
            # request passenger.

            if (
                "passenger_name" in request
                and "passenger_name" in expected
                and request["passenger_name"]
                != expected["passenger_name"]
            ):

                errors.append(
                    "Expected passenger_name must "
                    "match the request."
                )

            # Expected fare must match request.

            if (
                "fare" in request
                and "fare" in expected
                and request["fare"]
                != expected["fare"]
            ):

                errors.append(
                    "Expected fare must match "
                    "the request."
                )

            # Optional fields must also match.

            for field in [
                "baggage",
                "seat"
            ]:

                if (
                    field in request
                    and field in expected
                    and request[field]
                    != expected[field]
                ):

                    errors.append(
                        f"Expected {field} must "
                        f"match the request."
                    )

        # -------------------------------------
        # BOOKING ERROR SCENARIOS
        # -------------------------------------

        if success is False:

            error_code = expected.get(
                "error_code"
            )

            if error_code == "INVALID_PAX":

                if request.get(
                    "passenger_name"
                ) not in [
                    None,
                    ""
                ]:

                    errors.append(
                        "INVALID_PAX must be "
                        "caused by a missing or "
                        "empty passenger_name."
                    )

            elif error_code == "INVALID_FARE":

                if request.get(
                    "fare"
                ) != "INVALID":

                    errors.append(
                        "INVALID_FARE must use "
                        "fare INVALID."
                    )

            elif error_code == "INVALID_BAGGAGE":

                if request.get(
                    "baggage"
                ) != "INVALID":

                    errors.append(
                        "INVALID_BAGGAGE must use "
                        "baggage INVALID."
                    )

            elif error_code == "INVALID_SEAT":

                if request.get(
                    "seat"
                ) != "INVALID":

                    errors.append(
                        "INVALID_SEAT must use "
                        "seat INVALID."
                    )

    return errors


def validate_scenario(scenario):

    errors = []

    documentation = load_document()

    endpoint = scenario.get(
        "endpoint",
        ""
    )

    method = scenario.get(
        "method",
        ""
    )

    request = scenario.get(
        "request",
        {}
    )

    expected = scenario.get(
        "expected",
        {}
    )

    # -----------------------------------------
    # REQUIRED STRUCTURE
    # -----------------------------------------

    required_fields = [
        "id",
        "scenario",
        "category",
        "priority",
        "description",
        "endpoint",
        "method",
        "request",
        "expected"
    ]

    for field in required_fields:

        if field not in scenario:

            errors.append(
                f"Missing required field: {field}"
            )

    # -----------------------------------------
    # HTTP METHOD
    # -----------------------------------------

    if method not in ALLOWED_METHODS:

        errors.append(
            f"Unsupported HTTP method: {method}"
        )

    # -----------------------------------------
    # DOCUMENTED ENDPOINT
    # -----------------------------------------

    
    documented_endpoint = endpoint.split("?", 1)[0]

    if documented_endpoint not in documentation:

        errors.append(
            f"Endpoint '{endpoint}' "
            f"is not documented"
        )


    # -----------------------------------------
    # REQUEST FIELDS
    # -----------------------------------------

    documented_request_fields = {
        "passenger_name",
        "fare",
        "baggage",
        "seat",
        "origin",
        "destination"
    }

    if isinstance(request, dict):

        for field in request:

            if field not in documented_request_fields:

                errors.append(
                    f"Request field '{field}' "
                    f"is not documented"
                )

    else:

        errors.append(
            "Request must be a JSON object"
        )

    # -----------------------------------------
    # EXPECTED FIELDS
    # -----------------------------------------

    documented_expected_fields = {
        "success",
        "booking_status",
        "pnr",
        "passenger_name",
        "fare",
        "baggage",
        "seat",
        "origin",
        "destination",
        "results",
        "error_code",
        "message",
        "http_status"
    }

    if isinstance(expected, dict):
        if "body" in expected:
            errors.append(
                "Expected response fields must be flat; "
                "do not wrap them inside 'body'"
            )

        for field in expected:

            if field not in documented_expected_fields:

                errors.append(
                    f"Expected field '{field}' "
                    f"is not documented"
                )

    else:

        errors.append(
            "Expected must be a JSON object"
        )

    # -----------------------------------------
    # PLACEHOLDER VALIDATION
    # -----------------------------------------

    errors.extend(
        validate_values(
            request,
            "request"
        )
    )

    errors.extend(
        validate_values(
            expected,
            "expected"
        )
    )

    # -----------------------------------------
    # HTTP STATUS
    # -----------------------------------------

    if "http_status" in expected:

        if expected["http_status"] != 200:

            errors.append(
                "Expected HTTP status must be 200 "
                "because the documentation does not "
                "specify another status."
            )

    # -----------------------------------------
    # SEMANTIC VALIDATION
    # -----------------------------------------

    errors.extend(
        validate_semantic_rules(
            endpoint,
            request,
            expected
        )
    )

    # -----------------------------------------
    # FINAL RESULT
    # -----------------------------------------

    if errors:

        return {
            "valid": False,
            "errors": errors
        }

    return {
        "valid": True,
        "errors": []
    }


def validate_scenarios(scenarios):

    results = []

    for scenario in scenarios:

        validation = validate_scenario(
            scenario
        )

        results.append(
            {
                "id": scenario.get(
                    "id",
                    "UNKNOWN"
                ),
                "scenario": scenario.get(
                    "scenario",
                    "UNKNOWN"
                ),
                "valid": validation["valid"],
                "errors": validation["errors"]
            }
        )

    return results