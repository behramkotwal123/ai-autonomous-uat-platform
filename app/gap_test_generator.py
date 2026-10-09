import json

from openai import OpenAI

from app.document_retriever import retrieve_relevant_documentation


def generate_gap_tests(
    scenarios,
    coverage_analysis,
    max_tests=10
):
    """
    Generate additional UAT scenarios specifically for
    deterministic coverage gaps.

    AI may generate scenarios, but the existing deterministic
    validator remains the authority for scenario validity.
    """

    coverage = coverage_analysis.get(
        "coverage",
        {}
    )

    requirements = coverage.get(
        "requirements",
        []
    )

    gaps = [
        requirement
        for requirement in requirements
        if requirement.get("status") == "GAP"
    ]

    if not gaps:
        return {
            "generated_tests": [],
            "gap_count": 0,
            "message": "No coverage gaps identified."
        }

    documentation = retrieve_relevant_documentation(
        "API endpoints request fields validation rules "
        "successful responses error responses "
        "booking search baggage seat fares"
    )

    existing_scenarios = []

    for scenario in scenarios:
        existing_scenarios.append(
            {
                "id": scenario.get("id"),
                "category": scenario.get("category"),
                "priority": scenario.get("priority"),
                "description": scenario.get("description"),
                "scenario": scenario.get("scenario"),
                "method": scenario.get("method"),
                "endpoint": scenario.get("endpoint"),
                "request": scenario.get("request"),
                "expected": scenario.get("expected")
            }
        )

    prompt = f"""
You are an expert UAT test designer.

Generate additional UAT scenarios ONLY for the documented
coverage gaps.

IMPORTANT RULES:

1. Only generate tests for requirements explicitly marked GAP.
2. Do not generate tests for NOT_SPECIFIED requirements.
3. Do not duplicate existing scenarios.
4. Use only information supported by the API documentation.
5. Each test must be executable against the documented API.
6. Prefer concrete request values.
7. Include both positive and negative tests where appropriate.
8. Do not invent undocumented API behaviour.
9. The deterministic validator remains the final authority.
10. Generate no more than {max_tests} additional scenarios.
11. Use IDs beginning with AI-GAP-.
12. Use the exact scenario structure requested in the JSON schema.
13. For HTTP method, use the documented method such as GET or POST.
14. category should describe the functional area, for example Booking
    or Search.
15. priority should be one of Critical, High, Medium, or Low.
16. description should clearly describe the UAT test.
17. The scenario must explicitly target the identified coverage gap.

API DOCUMENTATION:

{documentation}

EXISTING SCENARIOS:

{json.dumps(existing_scenarios, indent=2)}

COVERAGE GAPS:

{json.dumps(gaps, indent=2)}

Return JSON only.
"""

    request_schema = {
        "type": "object",
        "properties": {
            "passenger_name": {
                "type": ["string", "null"]
            },
            "fare": {
                "type": ["string", "null"]
            },
            "baggage": {
                "type": ["string", "null"]
            },
            "seat": {
                "type": ["string", "null"]
            },
            "origin": {
                "type": ["string", "null"]
            },
            "destination": {
                "type": ["string", "null"]
            }
        },
        "required": [
            "passenger_name",
            "fare",
            "baggage",
            "seat",
            "origin",
            "destination"
        ],
        "additionalProperties": False
    }

    expected_schema = {
        "type": "object",
        "properties": {
            "success": {
                "type": ["boolean", "null"]
            },
            "booking_status": {
                "type": ["string", "null"]
            },
            "pnr": {
                "type": ["string", "null"]
            },
            "passenger_name": {
                "type": ["string", "null"]
            },
            "fare": {
                "type": ["string", "null"]
            },
            "baggage": {
                "type": ["string", "null"]
            },
            "seat": {
                "type": ["string", "null"]
            },
            "origin": {
                "type": ["string", "null"]
            },
            "destination": {
                "type": ["string", "null"]
            },
            "results": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False
                }
            },
            "error_code": {
                "type": ["string", "null"]
            },
            "message": {
                "type": ["string", "null"]
            }
        },
        "required": [
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
            "message"
        ],
        "additionalProperties": False
    }

    schema = {
        "type": "object",
        "properties": {
            "generated_tests": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string"
                        },
                        "category": {
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
                        "description": {
                            "type": "string"
                        },
                        "scenario": {
                            "type": "string"
                        },
                        "method": {
                            "type": "string",
                            "enum": [
                                "GET",
                                "POST",
                                "PUT",
                                "PATCH",
                                "DELETE"
                            ]
                        },
                        "endpoint": {
                            "type": "string"
                        },
                        "request": request_schema,
                        "expected": expected_schema,
                        "covers_requirement": {
                            "type": "string"
                        },
                        "reason": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "id",
                        "category",
                        "priority",
                        "description",
                        "scenario",
                        "method",
                        "endpoint",
                        "request",
                        "expected",
                        "covers_requirement",
                        "reason"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": [
            "generated_tests"
        ],
        "additionalProperties": False
    }

    client = OpenAI()
    response = client.responses.create(
        model="gpt-6-luna",
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "gap_test_generation",
                "strict": True,
                "schema": schema
            }
        }
    )

    result = json.loads(
        response.output_text
    )

    generated_tests = result.get(
        "generated_tests",
        []
    )

    # ---------------------------------------------------------
    # NORMALIZE GAP TEST IDS
    #
    # Ensure generated tests use AI-GAP IDs rather than
    # accidentally reusing IDs from the original scenarios.
    # ---------------------------------------------------------

    normalized_tests = []

    for index, test in enumerate(
        generated_tests[:max_tests],
        start=1
    ):

        test["id"] = f"AI-GAP-{index:03d}"

        normalized_tests.append(
            test
        )

    return {
        "generated_tests": normalized_tests,
        "gap_count": len(gaps)
    }


def print_gap_tests(result):
    """
    Print generated gap tests in a readable format.
    """

    tests = result.get(
        "generated_tests",
        []
    )

    print()
    print("=" * 60)
    print("           AI GAP TEST GENERATION")
    print("=" * 60)

    if not tests:

        print()
        print(
            "No additional tests generated."
        )

        return

    print()
    print(
        f"Additional tests generated : {len(tests)}"
    )

    print()
    print(
        "Generated Gap Tests"
    )
    print("-" * 60)

    for test in tests:

        print(
            f"{test.get('id')} | "
            f"{test.get('covers_requirement')}"
        )

        print(
            f"Category : {test.get('category')}"
        )

        print(
            f"Priority : {test.get('priority')}"
        )

        print(
            f"Description : "
            f"{test.get('description')}"
        )

        print(
            f"Scenario : "
            f"{test.get('scenario')}"
        )

        print(
            f"Reason   : "
            f"{test.get('reason')}"
        )

        print(
            f"Method   : "
            f"{test.get('method')}"
        )

        print(
            f"Endpoint : "
            f"{test.get('endpoint')}"
        )

        print(
            f"Request  : "
            f"{json.dumps(test.get('request'), ensure_ascii=False)}"
        )

        print(
            f"Expected : "
            f"{json.dumps(test.get('expected'), ensure_ascii=False)}"
        )

        print("-" * 60)