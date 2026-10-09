import json

from openai import OpenAI

from app.document_retriever import (
    retrieve_relevant_documentation
)


# ============================================================
# COVERAGE REQUIREMENTS
# ============================================================

COVERAGE_REQUIREMENTS = [
    {
        "id": "BOOKING_POSITIVE",
        "description": "Successful booking",
    },
    {
        "id": "BOOKING_BAGGAGE",
        "description": "Booking with optional baggage",
    },
    {
        "id": "BOOKING_SEAT",
        "description": "Booking with optional seat",
    },
    {
        "id": "INVALID_PAX",
        "description": "Missing or empty passenger name",
    },
    {
        "id": "INVALID_FARE",
        "description": "Unavailable fare",
    },
    {
        "id": "INVALID_BAGGAGE",
        "description": "Unavailable baggage option",
    },
    {
        "id": "INVALID_SEAT",
        "description": "Unavailable seat",
    },
    {
        "id": "SEARCH_SUCCESS",
        "description": "Successful flight search",
    },
    {
        "id": "SEARCH_NO_FLIGHTS",
        "description": "Search with no available flights",
    },
    {
        "id": "HTTP_STATUS",
        "description": "HTTP status code validation",
    },
    {
        "id": "RESPONSE_FIELDS",
        "description": "Expected response field validation",
    },
    {
        "id": "EXPECTED_VALUES",
        "description": "Expected field value validation",
    },
]


# ============================================================
# HELPERS
# ============================================================

def get_scenario_name(scenario):
    """
    The scenario generator may use either:
    - scenario
    - name

    This helper supports both.
    """

    return (
        scenario.get("scenario")
        or scenario.get("name")
        or ""
    )


def get_endpoint(scenario):
    """
    Safely retrieve the endpoint from a scenario.
    """

    return (
        scenario.get("endpoint")
        or scenario.get("request", {}).get("endpoint")
        or ""
    )


def get_request(scenario):
    """
    Safely retrieve request data.
    """

    request = scenario.get("request", {})

    if isinstance(request, dict):
        return request

    return {}


def get_expected(scenario):
    """
    Safely retrieve expected response data.
    """

    expected = scenario.get("expected", {})

    if isinstance(expected, dict):
        return expected

    return {}


# ============================================================
# DETERMINISTIC REQUIREMENT MATCHING
# ============================================================

def requirement_is_covered(
    requirement,
    scenarios
):
    """
    Deterministically determine whether a requirement
    is represented adequately by the generated scenarios.

    AI is NOT used here.

    The deterministic coverage engine remains the
    source of truth.
    """

    requirement_id = requirement["id"]

    for scenario in scenarios:

        name = get_scenario_name(
            scenario
        ).lower()

        endpoint = get_endpoint(
            scenario
        ).lower()

        request = get_request(
            scenario
        )

        expected = get_expected(
            scenario
        )

        # ----------------------------------------------------
        # BOOKING POSITIVE
        # ----------------------------------------------------

        if requirement_id == "BOOKING_POSITIVE":

            if (
                "/booking" in endpoint
                and expected.get("success") is True
                and expected.get("booking_status") == "CONFIRMED"
            ):
                return True

            if (
                "successful booking" in name
                and "invalid" not in name
            ):
                return True

        # ----------------------------------------------------
        # BOOKING BAGGAGE
        # ----------------------------------------------------

        elif requirement_id == "BOOKING_BAGGAGE":

            if (
                "/booking" in endpoint
                and (
                    "baggage" in name
                    or "baggage" in request
                    or "baggage" in expected
                )
                and "invalid" not in name
            ):
                return True

        # ----------------------------------------------------
        # BOOKING SEAT
        # ----------------------------------------------------

        elif requirement_id == "BOOKING_SEAT":

            if (
                "/booking" in endpoint
                and (
                    "seat" in name
                    or "seat" in request
                    or "seat" in expected
                )
                and "invalid" not in name
            ):
                return True

        # ----------------------------------------------------
        # INVALID PAX
        # ----------------------------------------------------

        elif requirement_id == "INVALID_PAX":

            passenger_name = request.get(
                "passenger_name"
            )

            if (
                "/booking" in endpoint
                and (
                    "missing passenger" in name
                    or "empty passenger" in name
                    or "invalid pax" in name
                    or passenger_name in ("", None)
                )
            ):
                return True

            error_code = (
                expected.get("error_code")
                or expected.get("code")
            )

            if error_code == "INVALID_PAX":
                return True

        # ----------------------------------------------------
        # INVALID FARE
        # ----------------------------------------------------

        elif requirement_id == "INVALID_FARE":

            fare = request.get(
                "fare"
            )

            if (
                "/booking" in endpoint
                and (
                    "invalid fare" in name
                    or "unavailable fare" in name
                    or fare == "INVALID"
                )
            ):
                return True

            error_code = (
                expected.get("error_code")
                or expected.get("code")
            )

            if error_code == "INVALID_FARE":
                return True

        # ----------------------------------------------------
        # INVALID BAGGAGE
        # ----------------------------------------------------

        elif requirement_id == "INVALID_BAGGAGE":

            baggage = request.get(
                "baggage"
            )

            if (
                "/booking" in endpoint
                and (
                    "invalid baggage" in name
                    or "unavailable baggage" in name
                    or baggage == "INVALID"
                )
            ):
                return True

            error_code = (
                expected.get("error_code")
                or expected.get("code")
            )

            if error_code == "INVALID_BAGGAGE":
                return True

        # ----------------------------------------------------
        # INVALID SEAT
        # ----------------------------------------------------

        elif requirement_id == "INVALID_SEAT":

            seat = request.get(
                "seat"
            )

            if (
                "/booking" in endpoint
                and (
                    "invalid seat" in name
                    or "unavailable seat" in name
                    or seat == "INVALID"
                )
            ):
                return True

            error_code = (
                expected.get("error_code")
                or expected.get("code")
            )

            if error_code == "INVALID_SEAT":
                return True

        # ----------------------------------------------------
        # SEARCH SUCCESS
        # ----------------------------------------------------

        elif requirement_id == "SEARCH_SUCCESS":

            if (
                "/search" in endpoint
                and expected.get("success") is True
                and "no flight" not in name
                and "no result" not in name
            ):
                return True

            if (
                "successful flight search" in name
                or "successful search" in name
            ):
                return True

        # ----------------------------------------------------
        # SEARCH NO FLIGHTS
        # ----------------------------------------------------

        elif requirement_id == "SEARCH_NO_FLIGHTS":

            if (
                "/search" in endpoint
                and (
                    "no flights" in name
                    or "no results" in name
                    or "no available flights" in name
                    or expected.get("error_code") == "NO_FLIGHTS"
                )
            ):
                return True

        # ----------------------------------------------------
        # RESPONSE FIELDS
        # ----------------------------------------------------

        elif requirement_id == "RESPONSE_FIELDS":

            if (
                expected
                and isinstance(expected, dict)
                and len(expected.keys()) > 0
            ):
                return True

        # ----------------------------------------------------
        # EXPECTED VALUES
        # ----------------------------------------------------

        elif requirement_id == "EXPECTED_VALUES":

            if (
                expected
                and isinstance(expected, dict)
                and any(
                    value not in (None, "")
                    for value in expected.values()
                )
            ):
                return True

    return False


# ============================================================
# DETERMINISTIC COVERAGE CALCULATION
# ============================================================

def calculate_coverage(
    scenarios
):
    """
    Calculate deterministic UAT coverage.

    HTTP_STATUS is deliberately excluded from the
    executable coverage percentage because the current
    API documentation does not define expected HTTP
    status codes.
    """

    results = []

    for requirement in COVERAGE_REQUIREMENTS:

        requirement_id = requirement["id"]

        description = requirement.get(
            "description",
            requirement_id
        )

        # ----------------------------------------------------
        # HTTP STATUS
        # ----------------------------------------------------

        if requirement_id == "HTTP_STATUS":

            results.append({
                "requirement_id": requirement_id,
                "description": description,
                "status": "NOT_SPECIFIED",
                "covered": False,
                "reason": (
                    "API documentation does not define "
                    "expected HTTP status codes."
                ),
            })

            continue

        # ----------------------------------------------------
        # NORMAL REQUIREMENT
        # ----------------------------------------------------

        covered = requirement_is_covered(
            requirement,
            scenarios
        )

        results.append({
            "requirement_id": requirement_id,
            "description": description,
            "status": (
                "COVERED"
                if covered
                else "GAP"
            ),
            "covered": covered,
        })

    # --------------------------------------------------------
    # ONLY ASSESSABLE REQUIREMENTS COUNT TOWARD COVERAGE
    # --------------------------------------------------------

    assessable_requirements = [
        item
        for item in results
        if item["status"] != "NOT_SPECIFIED"
    ]

    covered_count = sum(
        1
        for item in assessable_requirements
        if item["covered"]
    )

    uncovered_count = (
        len(assessable_requirements)
        - covered_count
    )

    total_assessable = len(
        assessable_requirements
    )

    if total_assessable > 0:

        coverage_percentage = (
            covered_count
            / total_assessable
            * 100
        )

    else:

        coverage_percentage = 0

    return {
        "total_requirements": len(results),
        "assessable_requirements": total_assessable,
        "covered": covered_count,
        "uncovered": uncovered_count,
        "not_specified": (
            len(results)
            - total_assessable
        ),
        "coverage_percentage": round(
            coverage_percentage,
            2
        ),
        "requirements": results,
    }


# ============================================================
# AI COVERAGE ANALYSIS
# ============================================================

def analyze_coverage_with_ai(
    scenarios,
    coverage
):
    """
    Ask AI to interpret deterministic coverage results.

    AI does NOT calculate or override coverage.

    It only:
    - interprets risks
    - explains gaps
    - recommends additional tests
    """

    documentation = retrieve_relevant_documentation(
        "booking search validation errors baggage seats fares API requirements"
    )

    scenario_summary = []

    for scenario in scenarios:

        scenario_summary.append({
            "id": scenario.get("id"),
            "scenario": get_scenario_name(
                scenario
            ),
            "endpoint": get_endpoint(
                scenario
            ),
            "request": get_request(
                scenario
            ),
            "expected": get_expected(
                scenario
            ),
        })

    prompt = f"""
You are an expert UAT coverage analyst.

The deterministic UAT engine has already calculated
the coverage results.

You MUST NOT change, recalculate, or override the
deterministic coverage result.

Your job is to interpret the results and identify
important testing gaps.

API documentation:

{documentation}

Generated scenarios:

{json.dumps(
    scenario_summary,
    indent=2
)}

Deterministic coverage:

{json.dumps(
    coverage,
    indent=2
)}

Rules:

1. Use only the API documentation and scenario evidence.
2. Do not invent API behavior.
3. Do not invent undocumented requirements.
4. Do not change deterministic coverage numbers.
5. Treat NOT_SPECIFIED requirements differently from
   genuine coverage gaps.
6. Prioritize business-critical missing tests.
7. Explain why each gap matters.
8. Recommend a concrete additional UAT test.
9. Distinguish documented requirements from assumptions.
10. If HTTP status codes are not defined in the
    documentation, explicitly say they need to be
    defined before they can become an executable
    coverage requirement.
"""

    client = OpenAI()

    response = client.responses.create(
        model="gpt-6-luna",

        input=prompt,

        text={
            "format": {
                "type": "json_schema",
                "name": "coverage_analysis",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "overall_assessment": {
                            "type": "string"
                        },
                        "risk_level": {
                            "type": "string",
                            "enum": [
                                "Low",
                                "Medium",
                                "High"
                            ]
                        },
                        "key_strengths": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "coverage_gaps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "requirement_id": {
                                        "type": "string"
                                    },
                                    "risk": {
                                        "type": "string",
                                        "enum": [
                                            "Low",
                                            "Medium",
                                            "High"
                                        ]
                                    },
                                    "reason": {
                                        "type": "string"
                                    },
                                    "recommended_test": {
                                        "type": "string"
                                    }
                                },
                                "required": [
                                    "requirement_id",
                                    "risk",
                                    "reason",
                                    "recommended_test"
                                ],
                                "additionalProperties": False
                            }
                        },
                        "recommendations": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "required": [
                        "overall_assessment",
                        "risk_level",
                        "key_strengths",
                        "coverage_gaps",
                        "recommendations"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )

    try:
        return json.loads(
            response.output_text
        )

    except json.JSONDecodeError:

        return {
            "overall_assessment": (
                response.output_text
            ),
            "risk_level": "Medium",
            "key_strengths": [],
            "coverage_gaps": [],
            "recommendations": [],
        }


# ============================================================
# COMPLETE COVERAGE ANALYSIS
# ============================================================

def analyze_coverage(
    scenarios,
    use_ai=True
):
    """
    Perform complete coverage analysis.

    Step 1:
        Deterministic coverage calculation.

    Step 2:
        Optional AI interpretation.
    """

    coverage = calculate_coverage(
        scenarios
    )

    ai_analysis = {
        "overall_assessment": "",
        "risk_level": "Low",
        "key_strengths": [],
        "coverage_gaps": [],
        "recommendations": [],
    }

    if use_ai:

        ai_analysis = analyze_coverage_with_ai(
            scenarios,
            coverage
        )

    return {
        "coverage": coverage,
        "ai_analysis": ai_analysis,
    }


# ============================================================
# PRINT COVERAGE REPORT
# ============================================================

def print_coverage_report(
    analysis
):
    """
    Print a human-readable coverage report.
    """

    coverage = analysis.get(
        "coverage",
        {}
    )

    ai_analysis = analysis.get(
        "ai_analysis",
        {}
    )

    print()
    print("=" * 60)
    print("             UAT COVERAGE ANALYSIS")
    print("=" * 60)

    print(
        f"Total requirements  : "
        f"{coverage.get('total_requirements', 0)}"
    )

    print(
        f"Covered             : "
        f"{coverage.get('covered', 0)}"
    )

    print(
        f"Uncovered           : "
        f"{coverage.get('uncovered', 0)}"
    )

    print(
        f"Not specified       : "
        f"{coverage.get('not_specified', 0)}"
    )

    print(
        f"Coverage            : "
        f"{coverage.get('coverage_percentage', 0)}%"
    )

    print()
    print("Requirement Coverage")
    print("-" * 60)

    for requirement in coverage.get(
        "requirements",
        []
    ):

        status = requirement.get(
            "status",
            "UNKNOWN"
        )

        requirement_id = requirement.get(
            "requirement_id",
            ""
        )

        description = requirement.get(
            "description",
            ""
        )

        print(
            f"{status:<13} | "
            f"{requirement_id:<22} | "
            f"{description}"
        )

    print()
    print("AI Coverage Assessment")
    print("-" * 60)

    print(
        f"Risk level          : "
        f"{ai_analysis.get('risk_level', 'Unknown')}"
    )

    print(
        f"Assessment          : "
        f"{ai_analysis.get('overall_assessment', '')}"
    )

    strengths = ai_analysis.get(
        "key_strengths",
        []
    )

    if strengths:

        print()
        print("Key Strengths")

        for strength in strengths:

            print(
                f"   - {strength}"
            )

    gaps = ai_analysis.get(
        "coverage_gaps",
        []
    )

    if gaps:

        print()
        print("Coverage Gaps")

        for gap in gaps:

            print(
                f"   [{gap.get('risk', 'Unknown')}] "
                f"{gap.get('requirement_id', '')}"
            )

            print(
                f"      Reason : "
                f"{gap.get('reason', '')}"
            )

            print(
                f"      Test   : "
                f"{gap.get('recommended_test', '')}"
            )

    recommendations = ai_analysis.get(
        "recommendations",
        []
    )

    if recommendations:

        print()
        print("Recommendations")

        for recommendation in recommendations:

            print(
                f"   - {recommendation}"
            )

    print("=" * 60)