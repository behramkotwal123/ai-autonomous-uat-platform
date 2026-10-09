import json

from openai import OpenAI

from app.document_retriever import retrieve_relevant_documentation


def select_tests(
    scenarios,
    max_tests=10
):
    """
    Use AI to select and prioritize the most
    valuable UAT scenarios.

    Deterministic validation and execution remain
    outside this module.
    """

    if not scenarios:
        return []

    documentation = retrieve_relevant_documentation(
        "API capabilities endpoints booking search "
        "validation errors baggage seats fares"
    )

    scenario_catalog = []

    for scenario in scenarios:

        scenario_catalog.append(
            {
                "id": scenario.get(
                    "id"
                ),
                "name": scenario.get(
                    "name",
                    scenario.get(
                        "scenario",
                        ""
                    )
                ),
                "description": scenario.get(
                    "description",
                    ""
                ),
                "endpoint": scenario.get(
                    "endpoint",
                    ""
                ),
                "method": scenario.get(
                    "method",
                    ""
                ),
                "request": scenario.get(
                    "request",
                    {}
                ),
                "expected": scenario.get(
                    "expected",
                    {}
                )
            }
        )

    prompt = f"""
You are an autonomous UAT test selection
engine for a travel technology API.

Your task is to select the most valuable
test scenarios from the supplied scenario
catalog.

Prioritize:

1. Core business functionality
2. Positive booking flows
3. Important validation rules
4. API contract coverage
5. Error handling
6. Search functionality
7. Boundary or negative scenarios
8. Scenarios that provide different
   coverage from other selected tests

Avoid selecting multiple scenarios that
test essentially the same behavior unless
they provide materially different coverage.

Do not invent scenarios.

Only select scenarios that exist in the
provided catalog.

Return at most {max_tests} scenarios.

For every selected scenario provide:

- id
- priority
- reason

Priority must be exactly one of:

Critical
High
Medium
Low

API DOCUMENTATION:

{documentation}

SCENARIO CATALOG:

{json.dumps(
    scenario_catalog,
    indent=2,
    ensure_ascii=False
)}
"""
    client = OpenAI()
    response = client.responses.create(
        model="gpt-6-luna",
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "uat_test_selection",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "selected_tests": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string"
                                    },
                                    "priority": {
                                        "type": "string",
                                        "enum": [
                                            "Critical",
                                            "High",
                                            "Medium",
                                            "Low"
                                        ]
                                    },
                                    "reason": {
                                        "type": "string"
                                    }
                                },
                                "required": [
                                    "id",
                                    "priority",
                                    "reason"
                                ],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": [
                        "selected_tests"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )

    result = json.loads(
        response.output_text
    )

    selected_tests = result.get(
        "selected_tests",
        []
    )

    scenario_map = {
        scenario.get("id"): scenario
        for scenario in scenarios
        if scenario.get("id")
    }

    selected_scenarios = []

    for selection in selected_tests:

        scenario_id = selection.get(
            "id"
        )

        scenario = scenario_map.get(
            scenario_id
        )

        if scenario is None:
            continue

        enriched_scenario = dict(
            scenario
        )

        enriched_scenario[
            "selection_priority"
        ] = selection.get(
            "priority"
        )

        enriched_scenario[
            "selection_reason"
        ] = selection.get(
            "reason"
        )

        selected_scenarios.append(
            enriched_scenario
        )

    return selected_scenarios


def print_selection(
    scenarios
):
    """
    Display the AI-selected scenarios
    in a readable format.
    """

    print()
    print("=" * 60)
    print(
        "          AUTONOMOUS UAT TEST SELECTION"
    )
    print("=" * 60)

    if not scenarios:

        print(
            "No scenarios selected."
        )

        return

    for index, scenario in enumerate(
        scenarios,
        start=1
    ):

        print()
        print(
            f"{index}. "
            f"{scenario.get('id', '')}"
        )

        print(
    f"   Scenario : "
    f"{scenario.get(
        'name',
        scenario.get(
            'scenario',
            ''
        )
    )}"
)

        print(
            f"   Priority : "
            f"{scenario.get(
                'selection_priority',
                ''
            )}"
        )

        print(
            f"   Reason   : "
            f"{scenario.get(
                'selection_reason',
                ''
            )}"
        )

    print()
    print("=" * 60)


if __name__ == "__main__":

    print(
        "Autonomous Test Selector"
    )

    print(
        "This module is designed to be "
        "called by the UAT pipeline."
    )