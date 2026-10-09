from app.release_readiness import (
    build_release_readiness,
    print_release_readiness
)


# ============================================================
# TEST DATA HELPERS
# ============================================================

def build_test_plan(
    test_count=5
):
    """
    Build a minimal Phase 7A-compatible test plan.
    """

    tests = []

    for index in range(
        1,
        test_count + 1
    ):

        tests.append(
            {
                "execution_order": index,
                "id": f"AI-UAT-{index:03d}",
                "scenario": (
                    f"Test scenario {index}"
                ),
                "category": "Booking",
                "priority": (
                    "Critical"
                    if index == 1
                    else "High"
                ),
                "method": "POST",
                "endpoint": "/booking",
                "selection_reason":
                    "Selected for UAT coverage.",
                "coverage_requirements": [
                    "BOOKING_POSITIVE"
                ],
                "expected_outcome":
                    "API should successfully complete the operation."
            }
        )

    return {
        "objective":
            "Validate core travel API functionality.",

        "total_scenarios":
            test_count,

        "tests_selected":
            test_count,

        "coverage_percentage":
            100.0,

        "total_requirements":
            12,

        "covered_requirements":
            11,

        "uncovered_requirements":
            0,

        "not_specified_requirements":
            1,

        "risk_level":
            "Low",

        "execution_order":
            tests,

        "tests":
            tests,

        "recommendation":
            "Tests are ready for UAT execution."
    }


def build_orchestration(
    test_count=5
):
    """
    Build a minimal Phase 7B-compatible
    orchestration strategy.
    """

    execution_order = []

    for index in range(
        1,
        test_count + 1
    ):

        execution_order.append(
            {
                "execution_order": index,
                "id": f"AI-UAT-{index:03d}",
                "scenario":
                    f"Test scenario {index}",
                "priority":
                    "Critical"
                    if index == 1
                    else "High",
                "method": "POST",
                "endpoint": "/booking",
                "coverage_requirements": [
                    "BOOKING_POSITIVE"
                ]
            }
        )

    return {
        "execution_strategy": {

            "mode":
                "SEQUENTIAL",

            "total_tests":
                test_count,

            "expected_executions":
                test_count,

            "risk_level":
                "Low",

            "failure_policy":
                "CONTINUE",

            "stop_condition":
                "DO_NOT_STOP_ON_SINGLE_TEST_FAILURE",

            "retry_policy":
                "USE_EXISTING_TEST_RUNNER_RETRY_POLICY",

            "execution_order":
                execution_order,

            "batches": [
                {
                    "batch_id": 1,
                    "tests": execution_order
                }
            ],

            "recommendation":
                "Execute planned UAT tests."
        }
    }


def build_coverage(
    uncovered=0,
    coverage_percentage=100.0
):
    """
    Build a minimal Phase 5-compatible coverage result.
    """

    return {
        "coverage": {

            "total_requirements":
                12,

            "assessable_requirements":
                11,

            "covered":
                11 - uncovered,

            "uncovered":
                uncovered,

            "not_specified":
                1,

            "coverage_percentage":
                coverage_percentage,

            "requirements": []
        },

        "ai_analysis": {

            "overall_assessment":
                "Coverage assessment.",

            "risk_level":
                "Low",

            "key_strengths": [],

            "coverage_gaps": [],

            "recommendations": []
        }
    }


def build_result(
    test_id,
    status="PASS",
    priority="High",
    retries=0,
    failure_type="",
    failure_category=""
):
    """
    Build a test_runner-compatible execution result.
    """

    return {

        "id":
            test_id,

        "scenario":
            f"Test scenario {test_id}",

        "status":
            status,

        "priority":
            priority,

        "method":
            "POST",

        "endpoint":
            "/booking",

        "retries":
            retries,

        "failure_type":
            failure_type,

        "failure_category":
            failure_category
    }


# ============================================================
# ASSERTION HELPER
# ============================================================

def check(
    condition,
    description
):
    """

    Print PASS/FAIL for a test condition.

    """

    if condition:

        print(
            f"PASS | {description}"
        )

    else:

        print(
            f"FAIL | {description}"
        )

        raise AssertionError(
            description
        )


# ============================================================
# TEST 1
# ALL TESTS PASS
# ============================================================

def test_all_tests_pass():

    test_plan = build_test_plan(
        5
    )

    coverage = build_coverage()

    orchestration = build_orchestration(
        5
    )

    execution_results = [

        build_result(
            "AI-UAT-001",
            "PASS",
            "Critical"
        ),

        build_result(
            "AI-UAT-002",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-003",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-004",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-005",
            "PASS",
            "High"
        )
    ]

    result = build_release_readiness(
        execution_results,
        test_plan,
        coverage,
        orchestration
    )

    readiness = result[
        "release_readiness"
    ]

    check(
        readiness["status"]
        == "READY",
        "All tests pass → READY"
    )

    check(
        readiness["decision"]
        == "APPROVE",
        "All tests pass → APPROVE"
    )

    check(
        readiness["risk_level"]
        == "LOW",
        "All tests pass → LOW risk"
    )

    check(
        readiness["execution_completion"]
        == 100.0,
        "Execution completion is 100%"
    )

    check(
        readiness["pass_rate"]
        == 100.0,
        "Pass rate is 100%"
    )

    check(
        readiness["coverage_percentage"]
        == 100.0,
        "Coverage is 100%"
    )


# ============================================================
# TEST 2
# ONE TEST FAILS
# ============================================================

def test_failed_test():

    test_plan = build_test_plan(
        5
    )

    coverage = build_coverage()

    orchestration = build_orchestration(
        5
    )

    execution_results = [

        build_result(
            "AI-UAT-001",
            "PASS",
            "Critical"
        ),

        build_result(
            "AI-UAT-002",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-003",
            "FAIL",
            "High",
            failure_type="VALIDATION",
            failure_category="EXPECTATION_MISMATCH"
        ),

        build_result(
            "AI-UAT-004",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-005",
            "PASS",
            "High"
        )
    ]

    result = build_release_readiness(
        execution_results,
        test_plan,
        coverage,
        orchestration
    )

    readiness = result[
        "release_readiness"
    ]

    check(
        readiness["status"]
        == "NOT_READY",
        "Failed test → NOT_READY"
    )

    check(
        readiness["decision"]
        == "DO_NOT_APPROVE",
        "Failed test → DO_NOT_APPROVE"
    )

    check(
        readiness["failed_tests"]
        == 1,
        "Failed test count detected"
    )

    check(
        readiness["unresolved_failures"]
        == 1,
        "Unresolved failure detected"
    )

    check(
        readiness["risk_level"]
        == "MEDIUM",
        "Non-critical failure → MEDIUM risk"
    )


# ============================================================
# TEST 3
# CRITICAL FAILURE
# ============================================================

def test_critical_failure():

    test_plan = build_test_plan(
        5
    )

    coverage = build_coverage()

    orchestration = build_orchestration(
        5
    )

    execution_results = [

        build_result(
            "AI-UAT-001",
            "FAIL",
            "Critical",
            failure_type="TRANSIENT",
            failure_category="SERVER_ERROR"
        ),

        build_result(
            "AI-UAT-002",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-003",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-004",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-005",
            "PASS",
            "High"
        )
    ]

    result = build_release_readiness(
        execution_results,
        test_plan,
        coverage,
        orchestration
    )

    readiness = result[
        "release_readiness"
    ]

    check(
        readiness["status"]
        == "NOT_READY",
        "Critical failure → NOT_READY"
    )

    check(
        readiness["risk_level"]
        == "HIGH",
        "Critical failure → HIGH risk"
    )

    check(
        readiness["critical_failures"]
        == 1,
        "Critical failure detected"
    )

    check(
        readiness["decision"]
        == "DO_NOT_APPROVE",
        "Critical failure → DO_NOT_APPROVE"
    )


# ============================================================
# TEST 4
# COVERAGE GAP
# ============================================================

def test_coverage_gap():

    test_plan = build_test_plan(
        5
    )

    coverage = build_coverage(
        uncovered=1,
        coverage_percentage=90.91
    )

    orchestration = build_orchestration(
        5
    )

    execution_results = [

        build_result(
            "AI-UAT-001",
            "PASS",
            "Critical"
        ),

        build_result(
            "AI-UAT-002",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-003",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-004",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-005",
            "PASS",
            "High"
        )
    ]

    result = build_release_readiness(
        execution_results,
        test_plan,
        coverage,
        orchestration
    )

    readiness = result[
        "release_readiness"
    ]

    check(
        readiness["status"]
        == "NOT_READY",
        "Coverage gap → NOT_READY"
    )

    check(
        readiness["decision"]
        == "DO_NOT_APPROVE",
        "Coverage gap → DO_NOT_APPROVE"
    )

    check(
        readiness["coverage_percentage"]
        == 90.91,
        "Coverage percentage preserved"
    )

    check(
        readiness["coverage_gaps"]
        == 1,
        "Coverage gap detected"
    )


# ============================================================
# TEST 5
# INCOMPLETE EXECUTION
# ============================================================

def test_incomplete_execution():

    test_plan = build_test_plan(
        5
    )

    coverage = build_coverage()

    orchestration = build_orchestration(
        5
    )

    execution_results = [

        build_result(
            "AI-UAT-001",
            "PASS",
            "Critical"
        ),

        build_result(
            "AI-UAT-002",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-003",
            "PASS",
            "High"
        )
    ]

    result = build_release_readiness(
        execution_results,
        test_plan,
        coverage,
        orchestration
    )

    readiness = result[
        "release_readiness"
    ]

    check(
        readiness["execution_completion"]
        == 60.0,
        "Incomplete execution detected"
    )

    check(
        readiness["status"]
        == "NOT_READY",
        "Incomplete execution → NOT_READY"
    )

    check(
        readiness["decision"]
        == "DO_NOT_APPROVE",
        "Incomplete execution → DO_NOT_APPROVE"
    )


# ============================================================
# TEST 6
# PASS AFTER RETRY
# ============================================================

def test_pass_after_retry():

    test_plan = build_test_plan(
        5
    )

    coverage = build_coverage()

    orchestration = build_orchestration(
        5
    )

    execution_results = [

        build_result(
            "AI-UAT-001",
            "PASS",
            "Critical"
        ),

        build_result(
            "AI-UAT-002",
            "PASS_AFTER_RETRY",
            "High",
            retries=1
        ),

        build_result(
            "AI-UAT-003",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-004",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-005",
            "PASS",
            "High"
        )
    ]

    result = build_release_readiness(
        execution_results,
        test_plan,
        coverage,
        orchestration
    )

    readiness = result[
        "release_readiness"
    ]

    check(
        readiness["status"]
        == "READY",
        "PASS_AFTER_RETRY → READY"
    )

    check(
        readiness["decision"]
        == "APPROVE",
        "PASS_AFTER_RETRY → APPROVE"
    )

    check(
        readiness["pass_rate"]
        == 100.0,
        "PASS_AFTER_RETRY counts as passed"
    )

    check(
        readiness["retries"]
        == 1,
        "Retry count preserved"
    )

    check(
        readiness["pass_after_retry"]
        == 1,
        "PASS_AFTER_RETRY count preserved"
    )


# ============================================================
# TEST 7
# ORCHESTRATION CONSISTENCY
# ============================================================

def test_orchestration_consistency():

    test_plan = build_test_plan(
        5
    )

    coverage = build_coverage()

    orchestration = build_orchestration(
        4
    )

    execution_results = [

        build_result(
            "AI-UAT-001",
            "PASS",
            "Critical"
        ),

        build_result(
            "AI-UAT-002",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-003",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-004",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-005",
            "PASS",
            "High"
        )
    ]

    result = build_release_readiness(
        execution_results,
        test_plan,
        coverage,
        orchestration
    )

    readiness = result[
        "release_readiness"
    ]

    check(
        readiness["orchestration_consistent"]
        is False,
        "Orchestration inconsistency detected"
    )

    check(
        readiness["status"]
        == "NOT_READY",
        "Orchestration inconsistency → NOT_READY"
    )

    check(
        readiness["decision"]
        == "DO_NOT_APPROVE",
        "Orchestration inconsistency → DO_NOT_APPROVE"
    )


# ============================================================
# RUN TESTS
# ============================================================

def main():

    print()

    print(
        "============================================================"
    )

    print(
        "          PHASE 8A — RELEASE READINESS TEST"
    )

    print(
        "============================================================"
    )

    print()

    test_all_tests_pass()

    test_failed_test()

    test_critical_failure()

    test_coverage_gap()

    test_incomplete_execution()

    test_pass_after_retry()

    test_orchestration_consistency()

    # --------------------------------------------------------
    # Demonstration
    # --------------------------------------------------------

    print()

    print(
        "============================================================"
    )

    print(
        "           PHASE 8A — SAMPLE READINESS"
    )

    print(
        "============================================================"
    )

    test_plan = build_test_plan(
        5
    )

    coverage = build_coverage()

    orchestration = build_orchestration(
        5
    )

    execution_results = [

        build_result(
            "AI-UAT-001",
            "PASS",
            "Critical"
        ),

        build_result(
            "AI-UAT-002",
            "PASS_AFTER_RETRY",
            "High",
            retries=1
        ),

        build_result(
            "AI-UAT-003",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-004",
            "PASS",
            "High"
        ),

        build_result(
            "AI-UAT-005",
            "PASS",
            "High"
        )
    ]

    result = build_release_readiness(
        execution_results,
        test_plan,
        coverage,
        orchestration
    )

    print_release_readiness(
        result
    )

    print()

    print(
        "============================================================"
    )

    print(
        "             PHASE 8A TEST RESULT"
    )

    print(
        "============================================================"
    )

    print(
        "Release Readiness : PASS"
    )

    print(
        "Test Cases        : 7"
    )

    print(
        "STATUS             : PASS"
    )

    print(
        "============================================================"
    )


if __name__ == "__main__":

    main()