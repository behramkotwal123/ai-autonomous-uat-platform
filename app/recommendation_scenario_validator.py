"""
Validation for recommendation-generated UAT scenarios.

This validator checks that an accepted recommendation has
produced a structurally valid candidate scenario.

It does not execute the scenario and does not modify the
existing UAT execution pipeline.
"""


REQUIRED_FIELDS = {
    "id",
    "scenario",
    "category",
    "priority",
    "description",
    "recommendation_id",
    "recommendation_status",
    "coverage_dimension",
}


VALID_STATUSES = {
    "GENERATED",
    "VALIDATED",
}


def validate_recommendation_scenario(scenario):
    """
    Validate a recommendation-generated UAT scenario.

    Returns a deterministic validation result.
    """

    if not isinstance(scenario, dict):

        return {
            "valid": False,
            "errors": [
                "Scenario must be a dictionary."
            ],
        }

    errors = []

    missing_fields = [
        field
        for field in REQUIRED_FIELDS
        if field not in scenario
    ]

    if missing_fields:

        errors.append(
            "Missing required fields: "
            + ", ".join(sorted(missing_fields))
        )

    if not scenario.get("id"):

        errors.append(
            "Scenario ID is required."
        )

    if not scenario.get("scenario"):

        errors.append(
            "Scenario description is required."
        )

    if not scenario.get("category"):

        errors.append(
            "Scenario category is required."
        )

    if not scenario.get("priority"):

        errors.append(
            "Scenario priority is required."
        )

    if not scenario.get("recommendation_id"):

        errors.append(
            "Recommendation ID is required."
        )

    recommendation_status = scenario.get(
        "recommendation_status"
    )

    if recommendation_status not in VALID_STATUSES:

        errors.append(
            "Recommendation status must be "
            "GENERATED or VALIDATED."
        )

    if not scenario.get("coverage_dimension"):

        errors.append(
            "Coverage dimension is required."
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }