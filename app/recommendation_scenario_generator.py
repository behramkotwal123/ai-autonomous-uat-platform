"""
Recommendation-derived UAT scenario generation.

Converts an actionable UAT recommendation into a
standard executable UAT scenario structure.
"""


def build_recommendation_scenario(
    recommendation,
    scenario_id,
):
    """
    Build a standard UAT scenario from a recommendation.

    Recommendation metadata is preserved so the scenario
    can be traced back to its originating recommendation.
    """

    if not isinstance(recommendation, dict):
        return None

    recommendation_id = recommendation.get(
        "recommendation_id",
        "",
    )

    area = recommendation.get(
        "area",
        "",
    )

    priority = recommendation.get(
        "priority",
        "Medium",
    )

    test_type = recommendation.get(
        "test_type",
        "",
    )

    scenario_text = recommendation.get(
        "scenario",
        "",
    )

    coverage_dimension = recommendation.get(
        "coverage_dimension",
        "",
    )

    if not scenario_text:
        return None

    negative_test_types = {
        "negative",
        "invalid parameters",
        "unsupported parameters",
        "boundary / error",
        "recovery",
    }

    normalized_test_type = (
        str(test_type).strip().lower()
    )

    category = (
        f"{area} - Negative"
        if normalized_test_type in negative_test_types
        else f"{area} - Positive"
    )

    priority_map = {
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
    }

    normalized_priority = priority_map.get(
        str(priority).strip().lower(),
        "Medium",
    )

    return {
        "id": scenario_id,
        "scenario": scenario_text,
        "category": category,
        "priority": normalized_priority,
        "description": scenario_text,
        "endpoint": "",
        "method": "GET",
        "request": "",
        "expected": "",
        "recommendation_id": recommendation_id,
        "recommendation_status": "GENERATED",
        "coverage_dimension": coverage_dimension,
    }