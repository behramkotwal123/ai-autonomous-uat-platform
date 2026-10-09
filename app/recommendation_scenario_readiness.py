"""
Readiness assessment for recommendation-generated UAT scenarios.

Determines whether a validated recommendation-generated
scenario is eligible to enter the normal UAT selection
workflow.

This module does not select or execute scenarios.
"""


REQUIRED_FIELDS = {
    "id",
    "scenario",
    "category",
    "priority",
    "recommendation_id",
    "coverage_dimension",
}


def assess_scenario_readiness(scenario):
    """
    Determine whether a recommendation-generated scenario
    is ready for UAT selection.
    """

    if not isinstance(scenario, dict):

        return {
            "ready": False,
            "status": "NOT_READY",
            "reasons": [
                "Scenario must be a dictionary."
            ],
        }

    reasons = []

    missing_fields = [
        field
        for field in REQUIRED_FIELDS
        if not scenario.get(field)
    ]

    if missing_fields:

        reasons.append(
            "Missing required fields: "
            + ", ".join(sorted(missing_fields))
        )

    if scenario.get("validation_status") != "VALID":

        reasons.append(
            "Scenario validation must be VALID."
        )

    if scenario.get("recommendation_status") != "VALIDATED":

        reasons.append(
            "Scenario status must be VALIDATED."
        )

    if reasons:

        return {
            "ready": False,
            "status": "NOT_READY",
            "reasons": reasons,
        }

    return {
        "ready": True,
        "status": "READY_FOR_SELECTION",
        "reasons": [],
    }