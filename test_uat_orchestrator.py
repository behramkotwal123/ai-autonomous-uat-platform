from app.uat_orchestrator import (
    build_execution_strategy,
    print_execution_strategy
)


def main():

    # ========================================================
    # SAMPLE PHASE 7A TEST PLAN
    # ========================================================

    test_plan = {

        "objective":
            "Execute selected UAT scenarios",

        "tests_selected":
            4,

        "coverage_percentage":
            90.91,

        "risk_level":
            "Medium",

        "tests": [

            {
                "execution_order": 1,
                "id": "AI-UAT-004",
                "scenario":
                    "Successful flight search",
                "category": "Search",
                "priority": "Medium",
                "method": "GET",
                "endpoint": "/search",
                "coverage_requirements": [
                    "SEARCH_SUCCESS"
                ],
                "expected_outcome":
                    "API should return a successful response."
            },

            {
                "execution_order": 2,
                "id": "AI-UAT-001",
                "scenario":
                    "Successful booking",
                "category": "Booking",
                "priority": "Critical",
                "method": "POST",
                "endpoint": "/booking",
                "coverage_requirements": [
                    "BOOKING_POSITIVE",
                    "HTTP_STATUS",
                    "RESPONSE_FIELDS",
                    "EXPECTED_VALUES"
                ],
                "expected_outcome":
                    "API should successfully complete the operation with status CONFIRMED."
            },

            {
                "execution_order": 3,
                "id": "AI-UAT-003",
                "scenario":
                    "Booking with invalid seat",
                "category": "Booking",
                "priority": "High",
                "method": "POST",
                "endpoint": "/booking",
                "coverage_requirements": [
                    "INVALID_SEAT"
                ],
                "expected_outcome":
                    "API should return error INVALID_SEAT."
            },

            {
                "execution_order": 4,
                "id": "AI-UAT-002",
                "scenario":
                    "Booking with baggage",
                "category": "Booking",
                "priority": "High",
                "method": "POST",
                "endpoint": "/booking",
                "coverage_requirements": [
                    "BOOKING_BAGGAGE"
                ],
                "expected_outcome":
                    "API should successfully complete the operation with status CONFIRMED."
            }
        ]
    }

    # ========================================================
    # BUILD STRATEGY
    # ========================================================

    result = build_execution_strategy(
        test_plan
    )

    strategy = result.get(
        "execution_strategy",
        {}
    )

    # ========================================================
    # ASSERTIONS
    # ========================================================

    assert strategy.get(
        "mode"
    ) == "SEQUENTIAL"

    print(
        "PASS | Sequential execution mode"
    )

    assert strategy.get(
        "total_tests"
    ) == 4

    print(
        "PASS | Correct test count"
    )

    assert strategy.get(
        "expected_executions"
    ) == 4

    print(
        "PASS | Expected execution count"
    )

    assert strategy.get(
        "risk_level"
    ) == "Medium"

    print(
        "PASS | Risk level preserved"
    )

    assert strategy.get(
        "failure_policy"
    ) == "CONTINUE"

    print(
        "PASS | Failure policy"
    )

    assert strategy.get(
        "stop_condition"
    ) == "DO_NOT_STOP_ON_SINGLE_TEST_FAILURE"

    print(
        "PASS | Stop condition"
    )

    assert strategy.get(
        "retry_policy"
    ) == (
        "USE_EXISTING_TEST_RUNNER_RETRY_POLICY"
    )

    print(
        "PASS | Existing retry policy preserved"
    )

    execution_order = strategy.get(
        "execution_order",
        []
    )

    assert len(
        execution_order
    ) == 4

    print(
        "PASS | Execution order generated"
    )

    ids = [
        test.get("id")
        for test in execution_order
    ]

    assert ids == [
        "AI-UAT-004",
        "AI-UAT-001",
        "AI-UAT-003",
        "AI-UAT-002"
    ]

    print(
        "PASS | Phase 7A execution order preserved"
    )

    # --------------------------------------------------------
    # Batch validation
    # --------------------------------------------------------

    batches = strategy.get(
        "batches",
        []
    )

    assert len(
        batches
    ) == 2

    print(
        "PASS | Endpoint batches generated"
    )

    assert len(
        batches[0].get(
            "tests",
            []
        )
    ) == 1

    print(
        "PASS | Search batch contains one test"
    )

    assert len(
        batches[1].get(
            "tests",
            []
        )
    ) == 3

    print(
        "PASS | Booking batch contains three tests"
    )

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    recommendation = strategy.get(
        "recommendation",
        ""
    )

    assert recommendation

    print(
        "PASS | Orchestration recommendation generated"
    )

    # ========================================================
    # PRINT
    # ========================================================

    print_execution_strategy(
        result
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print()
    print(
        "============================================================"
    )
    print(
        "             PHASE 7B TEST RESULT"
    )
    print(
        "============================================================"
    )

    print(
        "UAT Orchestrator : PASS"
    )

    print(
        f"Tests orchestrated : "
        f"{strategy.get('total_tests', 0)}"
    )

    print(
        f"Batches            : "
        f"{len(batches)}"
    )

    print(
        f"Mode               : "
        f"{strategy.get('mode', '')}"
    )

    print(
        f"Risk               : "
        f"{strategy.get('risk_level', '')}"
    )

    print(
        "STATUS             : PASS"
    )


if __name__ == "__main__":

    main()