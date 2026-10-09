"""
Execution specification validation for recommendation-generated UAT scenarios.

This validator determines whether a planned scenario contains
enough API execution information to be safely executed.

It does not execute the scenario.
"""


REQUIRED_EXECUTION_FIELDS = {
    "id",
    "scenario",
    "method",
    "endpoint",
    "request",
    "expected",
}


SUPPORTED_METHODS = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
}


def validate_execution_specification(scenario):
    """
    Validate whether a scenario contains a complete
    execution specification.
    """

    if not isinstance(scenario, dict):
        return {
            "executable": False,
            "status": "NOT_EXECUTABLE",
            "errors": [
                "Scenario must be a dictionary."
            ],
        }

    errors = []

    missing_fields = [
        field
        for field in REQUIRED_EXECUTION_FIELDS
        if field not in scenario
    ]

    if missing_fields:
        errors.append(
            "Missing execution fields: "
            + ", ".join(sorted(missing_fields))
        )

    method = str(
        scenario.get("method", "")
    ).strip().upper()

    if not method:
        errors.append(
            "HTTP method is required."
        )
    elif method not in SUPPORTED_METHODS:
        errors.append(
            f"Unsupported HTTP method: {method}"
        )

    if not str(
        scenario.get("endpoint", "")
    ).strip():
        errors.append(
            "API endpoint is required."
        )

    if not str(
        scenario.get("expected", "")
    ).strip():
        errors.append(
            "Expected result specification is required."
        )

    return {
        "executable": len(errors) == 0,
        "status": (
            "EXECUTABLE"
            if len(errors) == 0
            else "NOT_EXECUTABLE"
        ),
        "errors": errors,
    }