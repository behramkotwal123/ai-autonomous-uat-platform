"""
Phase 8A — UAT Release Readiness Analyzer

Determines whether a UAT cycle is ready for sign-off.

The readiness engine is deterministic.

AI must not override the readiness decision.

Inputs:
    execution_results
    test_plan
    coverage_analysis
    uat_orchestration

Outputs:
    {
        "release_readiness": {
            ...
        }
    }
"""


# ============================================================
# HELPERS
# ============================================================

def get_status(result):
    """
    Return the final execution status for a test result.

    If a retry occurred, final_status represents the
    authoritative outcome after retry.
    """

    return str(
        result.get(
            "final_status",
            result.get(
                "status",
                ""
            )
        )
    ).strip().upper()


def get_priority(result):
    """
    Return the test priority.
    """

    return str(
        result.get(
            "priority",
            ""
        )
    ).strip().lower()


def get_failure_type(result):
    """
    Return the failure type.
    """

    return str(
        result.get(
            "failure_type",
            ""
        )
    ).strip().upper()


def get_failure_category(result):
    """
    Return the failure category.
    """

    return str(
        result.get(
            "failure_category",
            ""
        )
    ).strip().upper()


def get_test_plan_tests(test_plan):
    """
    Safely return tests from the UAT test plan.
    """

    if not isinstance(
        test_plan,
        dict
    ):
        return []

    tests = test_plan.get(
        "tests",
        []
    )

    if not isinstance(
        tests,
        list
    ):
        return []

    return tests


def get_execution_results(
    execution_results
):
    """
    Safely return execution results.
    """

    if not isinstance(
        execution_results,
        list
    ):
        return []

    return execution_results


def get_coverage(
    coverage_analysis
):
    """
    Safely return coverage information.
    """

    if not isinstance(
        coverage_analysis,
        dict
    ):
        return {}

    coverage = coverage_analysis.get(
        "coverage",
        {}
    )

    if not isinstance(
        coverage,
        dict
    ):
        return {}

    return coverage


def get_orchestration(
    uat_orchestration
):
    """
    Safely return orchestration information.
    """

    if not isinstance(
        uat_orchestration,
        dict
    ):
        return {}

    strategy = (
        uat_orchestration.get(
            "execution_strategy",
            {}
        )
    )

    if not isinstance(
        strategy,
        dict
    ):
        return {}

    return strategy


# ============================================================
# TEST COUNTS
# ============================================================

def calculate_test_counts(
    execution_results
):
    """
    Calculate deterministic execution counts.

    PASS_AFTER_RETRY is treated as a successful final outcome.
    Retry activity is counted from the retry metadata.
    """

    results = get_execution_results(
        execution_results
    )

    passed = 0
    failed = 0
    skipped = 0
    errors = 0
    retries = 0
    pass_after_retry = 0

    for result in results:

        status = get_status(
            result
        )

        if status == "PASS":

            passed += 1

        elif status == "PASS_AFTER_RETRY":

            passed += 1
            pass_after_retry += 1

        elif status == "FAIL":

            failed += 1

        elif status == "SKIPPED":

            skipped += 1

        elif status == "ERROR":

            errors += 1

        
        retry = result.get(
            "retry",
            {}
        )

        retry_count = result.get(
            "retries",
            0
        )

        if isinstance(
            retry,
            dict
        ) and retry.get(
            "performed",
            False
        ):

            retries += 1

        elif isinstance(
            retry_count,
            int
        ) and retry_count > 0:

            retries += retry_count

        elif status == "PASS_AFTER_RETRY":

            retries += 1

    executed = len(
        results
    )

    if executed:

        pass_rate = round(
            (
                passed
                / executed
            )
            * 100,
            2
        )

    else:

        pass_rate = 0.0

    return {
        "executed": executed,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "errors": errors,
        "retries": retries,
        "pass_after_retry": pass_after_retry,
        "pass_rate": pass_rate
    }

# ============================================================
# EXECUTION COMPLETION
# ============================================================

def calculate_execution_completion(
    test_plan,
    execution_results
):
    """
    Determine whether all planned tests were executed.

    Execution completion is based on the number of tests
    planned by Phase 7A versus the number of execution
    results produced by the runner.
    """

    planned_tests = len(
        get_test_plan_tests(
            test_plan
        )
    )

    executed_tests = len(
        get_execution_results(
            execution_results
        )
    )

    if planned_tests == 0:

        return {
            "planned_tests": 0,
            "executed_tests": executed_tests,
            "execution_completion": 0.0,
            "complete": False
        }

    completion = round(
        (
            executed_tests
            / planned_tests
        )
        * 100,
        2
    )

    return {
        "planned_tests": planned_tests,
        "executed_tests": executed_tests,
        "execution_completion": completion,
        "complete": (
            executed_tests
            >= planned_tests
        )
    }


# ============================================================
# COVERAGE ASSESSMENT
# ============================================================

def assess_coverage(
    coverage_analysis
):
    """
    Determine whether documented coverage is complete.
    """

    coverage = get_coverage(
        coverage_analysis
    )

    coverage_percentage = float(
        coverage.get(
            "coverage_percentage",
            0.0
        ) or 0.0
    )

    uncovered = int(
        coverage.get(
            "uncovered",
            0
        ) or 0
    )

    not_specified = int(
        coverage.get(
            "not_specified",
            0
        ) or 0
    )

    return {
        "coverage_percentage":
            coverage_percentage,

        "uncovered":
            uncovered,

        "not_specified":
            not_specified,

        "complete":
            uncovered == 0
    }


# ============================================================
# CRITICAL FAILURE DETECTION
# ============================================================

def identify_critical_failures(
    execution_results
):
    """
    Identify failures that should be treated as critical.

    A failure is considered critical when:

    1. The scenario priority is Critical.
    2. The failure indicates an authentication /
       authorization problem.
    3. The failure indicates a server/system failure.
    4. The result is an ERROR rather than a normal test failure.
    """

    critical_failures = []

    results = get_execution_results(
        execution_results
    )

    for result in results:

        status = get_status(
            result
        )

        if status not in (
            "FAIL",
            "ERROR"
        ):

            continue

        priority = get_priority(
            result
        )

        failure_type = get_failure_type(
            result
        )

        failure_category = get_failure_category(
            result
        )

        is_critical = False

        if priority == "critical":

            is_critical = True

        if failure_type in (
            "AUTHENTICATION",
            "AUTHORIZATION"
        ):

            is_critical = True

        if failure_type == "TRANSIENT":

            if failure_category in (
                "SERVER_ERROR",
                "TIMEOUT_OR_CONNECTION"
            ):

                is_critical = True

        if failure_category in (
            "SERVER_ERROR",
            "AUTHENTICATION_FAILURE",
            "AUTHORIZATION_FAILURE"
        ):

            is_critical = True

        if status == "ERROR":

            is_critical = True

        if is_critical:

            critical_failures.append(
                {
                    "id":
                        result.get(
                            "id",
                            ""
                        ),

                    "scenario":
                        result.get(
                            "scenario",
                            ""
                        ),

                    "priority":
                        result.get(
                            "priority",
                            ""
                        ),

                    "status":
                        status,

                    "failure_type":
                        result.get(
                            "failure_type",
                            ""
                        ),

                    "failure_category":
                        result.get(
                            "failure_category",
                            ""
                        )
                }
            )

    return critical_failures


# ============================================================
# UNRESOLVED FAILURE DETECTION
# ============================================================

def identify_unresolved_failures(
    execution_results
):
    """
    Identify failures that remain unresolved after execution.

    PASS_AFTER_RETRY is considered resolved.

    PASS is considered resolved.

    FAIL, ERROR and SKIPPED are unresolved for sign-off.
    """

    unresolved = []

    results = get_execution_results(
        execution_results
    )

    for result in results:

        status = get_status(
            result
        )

        if status not in (
            "FAIL",
            "ERROR",
            "SKIPPED"
        ):

            continue

        unresolved.append(
            {
                "id":
                    result.get(
                        "id",
                        ""
                    ),

                "scenario":
                    result.get(
                        "scenario",
                        ""
                    ),

                "status":
                    status,

                "priority":
                    result.get(
                        "priority",
                        ""
                    ),

                "failure_type":
                    result.get(
                        "failure_type",
                        ""
                    ),

                "failure_category":
                    result.get(
                        "failure_category",
                        ""
                    )
            }
        )

    return unresolved


# ============================================================
# RETRY ASSESSMENT
# ============================================================

def assess_retries(
    execution_results
):
    """
    Assess retry activity.

    Retries do not automatically prevent sign-off.

    A test that finishes as PASS_AFTER_RETRY is considered
    successfully resolved.
    """

    counts = calculate_test_counts(
        execution_results
    )

    return {
        "retries": counts.get(
            "retries",
            0
        ),

        "pass_after_retry": counts.get(
            "pass_after_retry",
            0
        ),

        "retry_only_success": (
            counts.get(
                "pass_after_retry",
                0
            )
            > 0
        )
    }


# ============================================================
# RISK ASSESSMENT
# ============================================================

def determine_risk_level(
    execution_counts,
    coverage_assessment,
    critical_failures,
    unresolved_failures
):
    """
    Determine deterministic UAT risk.

    HIGH:
        Critical failures or unresolved system-level failures.

    MEDIUM:
        Unresolved non-critical failures, incomplete coverage,
        skipped tests or errors.

    LOW:
        All planned tests pass and coverage is complete.
    """

    if critical_failures:

        return "HIGH"

    if unresolved_failures:

        return "MEDIUM"

    if (
        coverage_assessment.get(
            "uncovered",
            0
        )
        > 0
    ):

        return "MEDIUM"

    if (
        execution_counts.get(
            "skipped",
            0
        )
        > 0
    ):

        return "MEDIUM"

    if (
        execution_counts.get(
            "errors",
            0
        )
        > 0
    ):

        return "MEDIUM"

    return "LOW"


# ============================================================
# READINESS DECISION
# ============================================================

def determine_readiness(
    execution_completion,
    execution_counts,
    coverage_assessment,
    critical_failures,
    unresolved_failures
):
    """
    Determine deterministic release readiness.

    READY requires:

    1. All planned tests executed.
    2. No failed tests.
    3. No unresolved failures.
    4. No skipped tests.
    5. No execution errors.
    6. No critical failures.
    7. No documented coverage gaps.
    """

    reasons = []

    recommendations = []

    # --------------------------------------------------------
    # Execution completion
    # --------------------------------------------------------

    if not execution_completion.get(
        "complete",
        False
    ):

        reasons.append(
            "Not all planned UAT tests were executed."
        )

        recommendations.append(
            "Complete execution of all planned UAT tests."
        )

    # --------------------------------------------------------
    # Failed tests
    # --------------------------------------------------------

    if (
        execution_counts.get(
            "failed",
            0
        )
        > 0
    ):

        reasons.append(
            "One or more UAT tests failed."
        )

        recommendations.append(
            "Resolve failed tests and rerun the affected scenarios."
        )

    # --------------------------------------------------------
    # Execution errors
    # --------------------------------------------------------

    if (
        execution_counts.get(
            "errors",
            0
        )
        > 0
    ):

        reasons.append(
            "One or more UAT executions ended in ERROR."
        )

        recommendations.append(
            "Investigate execution errors before UAT sign-off."
        )

    # --------------------------------------------------------
    # Skipped tests
    # --------------------------------------------------------

    if (
        execution_counts.get(
            "skipped",
            0
        )
        > 0
    ):

        reasons.append(
            "One or more planned UAT tests were skipped."
        )

        recommendations.append(
            "Execute skipped tests before UAT sign-off."
        )

    # --------------------------------------------------------
    # Critical failures
    # --------------------------------------------------------

    if critical_failures:

        reasons.append(
            "Critical UAT failures were detected."
        )

        recommendations.append(
            "Resolve all critical failures before release approval."
        )

    # --------------------------------------------------------
    # Unresolved failures
    # --------------------------------------------------------

    if unresolved_failures:

        reasons.append(
            "Unresolved UAT failures remain."
        )

        recommendations.append(
            "Resolve all outstanding failures before sign-off."
        )

    # --------------------------------------------------------
    # Coverage
    # --------------------------------------------------------

    if (
        coverage_assessment.get(
            "uncovered",
            0
        )
        > 0
    ):

        reasons.append(
            "Documented UAT coverage gaps remain."
        )

        recommendations.append(
            "Generate or add tests for uncovered requirements."
        )

    # --------------------------------------------------------
    # Final decision
    # --------------------------------------------------------

    if reasons:

        status = "NOT_READY"
        decision = "DO_NOT_APPROVE"

    else:

        status = "READY"
        decision = "APPROVE"

        recommendations.append(
            "UAT execution and documented coverage satisfy the release readiness criteria."
        )

    return {
        "status": status,
        "decision": decision,
        "reasons": reasons,
        "recommendations": recommendations
    }


# ============================================================
# BUILD RELEASE READINESS
# ============================================================

def build_release_readiness(
    execution_results,
    test_plan,
    coverage_analysis,
    uat_orchestration
):
    """
    Build the complete deterministic Phase 8A result.
    """

    execution_results = (
        get_execution_results(
            execution_results
        )
    )

    execution_counts = calculate_test_counts(
        execution_results
    )

    execution_completion = (
        calculate_execution_completion(
            test_plan,
            execution_results
        )
    )

    coverage_assessment = assess_coverage(
        coverage_analysis
    )

    critical_failures = (
        identify_critical_failures(
            execution_results
        )
    )

    unresolved_failures = (
        identify_unresolved_failures(
            execution_results
        )
    )

    retry_assessment = assess_retries(
        execution_results
    )

    risk_level = determine_risk_level(
        execution_counts=execution_counts,
        coverage_assessment=coverage_assessment,
        critical_failures=critical_failures,
        unresolved_failures=unresolved_failures
    )

    readiness = determine_readiness(
        execution_completion=execution_completion,
        execution_counts=execution_counts,
        coverage_assessment=coverage_assessment,
        critical_failures=critical_failures,
        unresolved_failures=unresolved_failures
    )

    orchestration = get_orchestration(
        uat_orchestration
    )

    strategy_expected_executions = int(
        orchestration.get(
            "expected_executions",
            0
        ) or 0
    )

    # --------------------------------------------------------
    # Cross-check planned execution count
    # --------------------------------------------------------

    orchestration_consistent = (
        strategy_expected_executions
        == execution_completion.get(
            "planned_tests",
            0
        )
    )

    if not orchestration_consistent:

        readiness["status"] = "NOT_READY"
        readiness["decision"] = "DO_NOT_APPROVE"

        if (
            "The orchestration plan and UAT test plan are inconsistent."
            not in readiness["reasons"]
        ):

            readiness["reasons"].append(
                "The orchestration plan and UAT test plan are inconsistent."
            )

        readiness["recommendations"].append(
            "Review the UAT test plan and orchestration strategy before sign-off."
        )

        risk_level = "MEDIUM"

    # --------------------------------------------------------
    # Build final result
    # --------------------------------------------------------

    result = {
        "release_readiness": {

            "status":
                readiness.get(
                    "status",
                    "NOT_READY"
                ),

            "decision":
                readiness.get(
                    "decision",
                    "DO_NOT_APPROVE"
                ),

            "risk_level":
                risk_level,

            "execution_completion":
                execution_completion.get(
                    "execution_completion",
                    0.0
                ),

            "planned_tests":
                execution_completion.get(
                    "planned_tests",
                    0
                ),

            "executed_tests":
                execution_completion.get(
                    "executed_tests",
                    0
                ),

            "passed_tests":
                execution_counts.get(
                    "passed",
                    0
                ),

            "failed_tests":
                execution_counts.get(
                    "failed",
                    0
                ),

            "skipped_tests":
                execution_counts.get(
                    "skipped",
                    0
                ),

            "error_tests":
                execution_counts.get(
                    "errors",
                    0
                ),

            "pass_rate":
                execution_counts.get(
                    "pass_rate",
                    0.0
                ),

            "critical_failures":
                len(
                    critical_failures
                ),

            "unresolved_failures":
                len(
                    unresolved_failures
                ),

            "coverage_percentage":
                coverage_assessment.get(
                    "coverage_percentage",
                    0.0
                ),

            "coverage_gaps":
                coverage_assessment.get(
                    "uncovered",
                    0
                ),

            "not_specified_requirements":
                coverage_assessment.get(
                    "not_specified",
                    0
                ),

            "retries":
                retry_assessment.get(
                    "retries",
                    0
                ),

            "pass_after_retry":
                retry_assessment.get(
                    "pass_after_retry",
                    0
                ),

            "orchestration_consistent":
                orchestration_consistent,

            "reasons":
                readiness.get(
                    "reasons",
                    []
                ),

            "recommendations":
                readiness.get(
                    "recommendations",
                    []
                ),

            "critical_failure_details":
                critical_failures,

            "unresolved_failure_details":
                unresolved_failures
        }
    }

    return result


# ============================================================
# PRINT RESULT
# ============================================================

def print_release_readiness(
    result
):
    """
    Print a concise Phase 8A readiness report.
    """

    readiness = result.get(
        "release_readiness",
        {}
    )

    print()

    print(
        "============================================================"
    )

    print(
        "             PHASE 8A — RELEASE READINESS"
    )

    print(
        "============================================================"
    )

    print()

    print(
        f"Execution completion : "
        f"{readiness.get('execution_completion', 0)}%"
    )

    print(
        f"Planned tests        : "
        f"{readiness.get('planned_tests', 0)}"
    )

    print(
        f"Executed tests       : "
        f"{readiness.get('executed_tests', 0)}"
    )

    print(
        f"Passed tests         : "
        f"{readiness.get('passed_tests', 0)}"
    )

    print(
        f"Failed tests         : "
        f"{readiness.get('failed_tests', 0)}"
    )

    print(
        f"Pass rate            : "
        f"{readiness.get('pass_rate', 0)}%"
    )

    print(
        f"Critical failures    : "
        f"{readiness.get('critical_failures', 0)}"
    )

    print(
        f"Unresolved failures  : "
        f"{readiness.get('unresolved_failures', 0)}"
    )

    print(
        f"Retries              : "
        f"{readiness.get('retries', 0)}"
    )

    print(
        f"Coverage             : "
        f"{readiness.get('coverage_percentage', 0)}%"
    )

    print(
        f"Coverage gaps        : "
        f"{readiness.get('coverage_gaps', 0)}"
    )

    print(
        f"Risk level           : "
        f"{readiness.get('risk_level', 'UNKNOWN')}"
    )

    print()

    print(
        f"Release readiness    : "
        f"{readiness.get('status', 'NOT_READY')}"
    )

    print(
        f"UAT recommendation   : "
        f"{readiness.get('decision', 'DO_NOT_APPROVE')}"
    )

    # --------------------------------------------------------
    # Reasons
    # --------------------------------------------------------

    reasons = readiness.get(
        "reasons",
        []
    )

    if reasons:

        print()

        print(
            "Reasons"
        )

        for reason in reasons:

            print(
                f"  - {reason}"
            )

    # --------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------

    recommendations = readiness.get(
        "recommendations",
        []
    )

    if recommendations:

        print()

        print(
            "Recommendations"
        )

        for recommendation in recommendations:

            print(
                f"  - {recommendation}"
            )

    print()

    print(
        "============================================================"
    )