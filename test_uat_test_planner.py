"""
Independent Phase 7A test.

Tests the UAT Test Plan Builder without modifying
or executing the production scenario pipeline.
"""

from app.uat_test_planner import (
    build_test_plan,
    print_test_plan
)


def main():

    print()
    print("=" * 60)
    print("        PHASE 7A - UAT TEST PLAN TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # Sample validated scenarios
    # ---------------------------------------------------------

    scenarios = [
        {
            "id": "AI-UAT-001",
            "category": "Booking",
            "priority": "Critical",
            "description": "Successful booking",
            "scenario": "Successful booking",
            "method": "POST",
            "endpoint": "/booking",
            "request": {
                "passenger_name": "Test Passenger",
                "fare": "ECONOMY",
                "baggage": None,
                "seat": None
            },
            "expected": {
                "success": True,
                "booking_status": "CONFIRMED",
                "error_code": None
            },
            "selection_priority": "Critical",
            "selection_reason": (
                "Core booking functionality is the primary "
                "business flow."
            )
        },
        {
            "id": "AI-UAT-002",
            "category": "Booking",
            "priority": "High",
            "description": "Booking with baggage",
            "scenario": "Booking with optional baggage",
            "method": "POST",
            "endpoint": "/booking",
            "request": {
                "passenger_name": "Test Passenger",
                "fare": "ECONOMY",
                "baggage": "20KG",
                "seat": None
            },
            "expected": {
                "success": True,
                "booking_status": "CONFIRMED",
                "error_code": None
            },
            "selection_priority": "High",
            "selection_reason": (
                "Validates optional baggage functionality."
            )
        },
        {
            "id": "AI-UAT-003",
            "category": "Booking",
            "priority": "High",
            "description": "Booking with invalid seat",
            "scenario": "Booking with unavailable seat",
            "method": "POST",
            "endpoint": "/booking",
            "request": {
                "passenger_name": "Test Passenger",
                "fare": "ECONOMY",
                "baggage": None,
                "seat": "INVALID"
            },
            "expected": {
                "success": False,
                "booking_status": None,
                "error_code": "INVALID_SEAT"
            },
            "selection_priority": "High",
            "selection_reason": (
                "Validates documented seat availability "
                "error handling."
            )
        },
        {
            "id": "AI-UAT-004",
            "category": "Search",
            "priority": "Medium",
            "description": "Successful flight search",
            "scenario": "Successful flight search",
            "method": "GET",
            "endpoint": "/search",
            "request": {
                "origin": "BOM",
                "destination": "DXB"
            },
            "expected": {
                "success": True,
                "error_code": None
            },
            "selection_priority": "Medium",
            "selection_reason": (
                "Validates core flight search functionality."
            )
        }
    ]

    # ---------------------------------------------------------
    # Deterministic coverage analysis
    # ---------------------------------------------------------

    coverage_analysis = {
        "coverage": {
            "total_requirements": 12,
            "covered": 10,
            "uncovered": 1,
            "not_specified": 1,
            "coverage_percentage": 90.91,
            "requirements": [
                {
                    "requirement_id": "BOOKING_POSITIVE",
                    "description": "Successful booking",
                    "status": "COVERED",
                    "covered": True
                },
                {
                    "requirement_id": "BOOKING_BAGGAGE",
                    "description": "Booking with optional baggage",
                    "status": "COVERED",
                    "covered": True
                },
                {
                    "requirement_id": "INVALID_SEAT",
                    "description": "Unavailable seat",
                    "status": "COVERED",
                    "covered": True
                },
                {
                    "requirement_id": "SEARCH_SUCCESS",
                    "description": "Successful flight search",
                    "status": "COVERED",
                    "covered": True
                },
                {
                    "requirement_id": "INVALID_PAX",
                    "description": "Invalid passenger",
                    "status": "GAP",
                    "covered": False
                },
                {
                    "requirement_id": "HTTP_STATUS",
                    "description": "HTTP status code validation",
                    "status": "NOT_SPECIFIED",
                    "covered": False
                }
            ]
        },
        "ai_analysis": {
            "overall_assessment": (
                "Most core functionality is covered."
            ),
            "risk_level": "Medium",
            "key_strengths": [
                "Core booking coverage",
                "Search coverage",
                "Negative seat validation"
            ],
            "coverage_gaps": [
                {
                    "requirement_id": "INVALID_PAX",
                    "risk": "Medium",
                    "reason": "Passenger validation is not covered.",
                    "recommended_test": (
                        "Submit a booking without passenger name."
                    )
                }
            ],
            "recommendations": [
                "Add invalid passenger coverage."
            ]
        }
    }

    # ---------------------------------------------------------
    # Autonomous selection output
    # ---------------------------------------------------------

    selected_tests = [
        {
            "id": "AI-UAT-001",
            "priority": "Critical",
            "reason": (
                "Core booking functionality should be "
                "executed first."
            )
        },
        {
            "id": "AI-UAT-002",
            "priority": "High",
            "reason": (
                "Validates optional baggage functionality."
            )
        },
        {
            "id": "AI-UAT-003",
            "priority": "High",
            "reason": (
                "Validates documented seat validation."
            )
        },
        {
            "id": "AI-UAT-004",
            "priority": "Medium",
            "reason": (
                "Validates successful flight search."
            )
        }
    ]

    # ---------------------------------------------------------
    # Build test plan
    # ---------------------------------------------------------

    print()
    print("BUILDING UAT TEST PLAN...")
    print()

    result = build_test_plan(
        scenarios=scenarios,
        coverage_analysis=coverage_analysis,
        selected_tests=selected_tests
    )

    print_test_plan(
        result
    )

    plan = result.get(
        "test_plan",
        {}
    )

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    print()
    print("VALIDATING TEST PLAN")
    print("--------------------")

    tests = plan.get(
        "tests",
        []
    )

    # Test 1
    assert (
        len(tests) == 4
    ), (
        "Expected 4 tests in the plan."
    )

    print(
        "PASS | Correct number of tests"
    )

    # Test 2
    execution_ids = [
        test.get("id")
        for test in tests
    ]

    assert (
        len(execution_ids) == len(
            set(execution_ids)
        )
    ), (
        "Duplicate test IDs detected."
    )

    print(
        "PASS | No duplicate test IDs"
    )

    # Test 3
    assert (
        tests[0]["id"]
        == "AI-UAT-004"
    ), (
        "Search test should be first "
        "because search is treated as the "
        "availability prerequisite."
    )

    print(
        "PASS | Search test ordered first"
    )

    # Test 4
    assert (
        tests[1]["id"]
        == "AI-UAT-001"
    ), (
        "Critical booking test should follow "
        "the search prerequisite."
    )

    print(
        "PASS | Critical booking ordered correctly"
    )

    # Test 5
    assert (
        tests[1]["priority"]
        == "Critical"
    )

    print(
        "PASS | Priority preserved"
    )

    # Test 6
    invalid_seat_test = next(
        (
            test
            for test in tests
            if test["id"] == "AI-UAT-003"
        ),
        None
    )

    assert (
        invalid_seat_test is not None
    ), (
        "INVALID_SEAT test missing."
    )

    assert (
        "INVALID_SEAT"
        in invalid_seat_test[
            "coverage_requirements"
        ]
    ), (
        "INVALID_SEAT coverage was not "
        "identified."
    )

    print(
        "PASS | Coverage requirement mapped"
    )

    # Test 7
    assert (
        plan["coverage_percentage"]
        == 90.91
    )

    print(
        "PASS | Coverage percentage preserved"
    )

    # Test 8
    assert (
        plan["risk_level"]
        == "Medium"
    )

    print(
        "PASS | Risk level preserved"
    )

    # Test 9
    assert (
        plan["uncovered_requirements"]
        == 1
    )

    print(
        "PASS | Coverage gap preserved"
    )

    # Test 10
    assert (
        "Coverage gaps remain"
        in plan["recommendation"]
    )

    print(
        "PASS | Gap recommendation generated"
    )

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("        PHASE 7A TEST RESULT")
    print("=" * 60)

    print(
        "Test Plan Builder : PASS"
    )

    print(
        f"Tests planned     : "
        f"{len(tests)}"
    )

    print(
        f"Coverage          : "
        f"{plan['coverage_percentage']}%"
    )

    print(
        f"Risk              : "
        f"{plan['risk_level']}"
    )

    print(
        "STATUS            : PASS"
    )

    print()
    print(
        "Phase 7A successfully built a "
        "deterministic UAT execution plan "
        "from validated scenarios, coverage "
        "analysis, and autonomous test selection."
    )


if __name__ == "__main__":
    main()