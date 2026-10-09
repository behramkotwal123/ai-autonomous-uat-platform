"""
Phase 7B — UAT Orchestrator

Builds a deterministic execution strategy from the
Phase 7A UAT Test Plan.

The orchestrator does NOT execute tests.

Execution remains the responsibility of test_runner.py.
"""


# ============================================================
# HELPERS
# ============================================================

def get_test_id(test):
    return test.get(
        "id",
        ""
    )


def get_priority(test):
    return str(
        test.get(
            "priority",
            "Medium"
        )
    ).strip().lower()


def get_endpoint(test):
    return test.get(
        "endpoint",
        ""
    )


def get_method(test):
    return test.get(
        "method",
        ""
    )


# ============================================================
# PRIORITY RANKING
# ============================================================

def priority_rank(priority):

    ranking = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "low": 4
    }

    return ranking.get(
        str(priority).lower(),
        5
    )


# ============================================================
# EXECUTION MODE
# ============================================================

def determine_execution_mode(
    test_plan
):

    tests = test_plan.get(
        "tests",
        []
    )

    if not tests:

        return "NONE"

    return "SEQUENTIAL"


# ============================================================
# FAILURE POLICY
# ============================================================

def determine_failure_policy(
    test_plan
):

    risk_level = str(
        test_plan.get(
            "risk_level",
            "Low"
        )
    ).lower()

    if risk_level == "high":

        return "CONTINUE_WITH_FAILURE_ANALYSIS"

    return "CONTINUE"


# ============================================================
# STOP CONDITION
# ============================================================

def determine_stop_condition(
    test_plan
):

    risk_level = str(
        test_plan.get(
            "risk_level",
            "Low"
        )
    ).lower()

    if risk_level == "high":

        return (
            "STOP_ONLY_FOR_CRITICAL_SYSTEM_FAILURE"
        )

    return "DO_NOT_STOP_ON_SINGLE_TEST_FAILURE"


# ============================================================
# RETRY POLICY
# ============================================================

def determine_retry_policy():

    return (
        "USE_EXISTING_TEST_RUNNER_RETRY_POLICY"
    )


# ============================================================
# BUILD EXECUTION ORDER
# ============================================================

def build_execution_order(
    tests
):

    ordered_tests = []

    for index, test in enumerate(
        tests,
        start=1
    ):

        ordered_tests.append(
            {
                "execution_order": index,
                "id": get_test_id(test),
                "scenario": test.get(
                    "scenario",
                    ""
                ),
                "priority": test.get(
                    "priority",
                    ""
                ),
                "method": get_method(test),
                "endpoint": get_endpoint(test),
                "coverage_requirements":
                    test.get(
                        "coverage_requirements",
                        []
                    )
            }
        )

    return ordered_tests


# ============================================================
# BUILD BATCHES
# ============================================================

def build_batches(
    execution_order
):

    batches = []

    current_batch = []

    previous_endpoint = None

    for test in execution_order:

        endpoint = test.get(
            "endpoint",
            ""
        )

        if (
            current_batch
            and endpoint != previous_endpoint
        ):

            batches.append(
                {
                    "batch_id":
                        len(batches) + 1,
                    "tests":
                        current_batch
                }
            )

            current_batch = []

        current_batch.append(
            test
        )

        previous_endpoint = endpoint

    if current_batch:

        batches.append(
            {
                "batch_id":
                    len(batches) + 1,
                "tests":
                    current_batch
            }
        )

    return batches


# ============================================================
# BUILD ORCHESTRATION RECOMMENDATION
# ============================================================

def build_recommendation(
    test_plan,
    execution_order,
    batches
):

    risk_level = test_plan.get(
        "risk_level",
        "Low"
    )

    test_count = len(
        execution_order
    )

    batch_count = len(
        batches
    )

    if test_count == 0:

        return (
            "No tests are available for UAT execution."
        )

    if str(risk_level).lower() == "high":

        return (
            f"Execute {test_count} planned tests "
            f"in {batch_count} controlled batches. "
            "Continue execution unless a critical "
            "system-level failure occurs. "
            "Use the existing deterministic runner "
            "for execution, retries and PASS/FAIL "
            "determination."
        )

    return (
        f"Execute {test_count} planned tests "
        f"in {batch_count} controlled batches. "
        "Continue execution after individual test "
        "failures and rely on the existing runner "
        "for retries, diagnosis and deterministic "
        "PASS/FAIL determination."
    )


# ============================================================
# BUILD UAT EXECUTION STRATEGY
# ============================================================

def build_execution_strategy(
    test_plan
):

    if not isinstance(
        test_plan,
        dict
    ):

        return {
            "execution_strategy": {
                "mode": "NONE",
                "total_tests": 0,
                "expected_executions": 0,
                "batches": [],
                "execution_order": [],
                "failure_policy": (
                    "NO_EXECUTION"
                ),
                "stop_condition": (
                    "NO_EXECUTION"
                ),
                "retry_policy": (
                    "NO_EXECUTION"
                ),
                "recommendation": (
                    "No valid UAT test plan supplied."
                )
            }
        }

    tests = test_plan.get(
        "tests",
        []
    )

    if not isinstance(
        tests,
        list
    ):

        tests = []

    # --------------------------------------------------------
    # Preserve the deterministic order created by Phase 7A.
    # --------------------------------------------------------

    execution_order = build_execution_order(
        tests
    )

    batches = build_batches(
        execution_order
    )

    strategy = {

        "mode":
            determine_execution_mode(
                test_plan
            ),

        "total_tests":
            len(execution_order),

        "expected_executions":
            len(execution_order),

        "risk_level":
            test_plan.get(
                "risk_level",
                "Low"
            ),

        "failure_policy":
            determine_failure_policy(
                test_plan
            ),

        "stop_condition":
            determine_stop_condition(
                test_plan
            ),

        "retry_policy":
            determine_retry_policy(),

        "execution_order":
            execution_order,

        "batches":
            batches,

        "recommendation":
            build_recommendation(
                test_plan,
                execution_order,
                batches
            )
    }

    return {
        "execution_strategy":
            strategy
    }


# ============================================================
# PRINT EXECUTION STRATEGY
# ============================================================

def print_execution_strategy(
    result
):

    strategy = result.get(
        "execution_strategy",
        {}
    )

    print()
    print(
        "============================================================"
    )
    print(
        "              PHASE 7B — UAT ORCHESTRATOR"
    )
    print(
        "============================================================"
    )

    print()

    print(
        f"Mode                : "
        f"{strategy.get('mode', '')}"
    )

    print(
        f"Tests               : "
        f"{strategy.get('total_tests', 0)}"
    )

    print(
        f"Expected executions : "
        f"{strategy.get('expected_executions', 0)}"
    )

    print(
        f"Risk                : "
        f"{strategy.get('risk_level', '')}"
    )

    print(
        f"Failure policy      : "
        f"{strategy.get('failure_policy', '')}"
    )

    print(
        f"Stop condition      : "
        f"{strategy.get('stop_condition', '')}"
    )

    print(
        f"Retry policy        : "
        f"{strategy.get('retry_policy', '')}"
    )

    print()

    print(
        "Execution Order"
    )

    for test in strategy.get(
        "execution_order",
        []
    ):

        print(
            f"  {test.get('execution_order')}. "
            f"{test.get('id')} | "
            f"{test.get('method')} "
            f"{test.get('endpoint')} | "
            f"{test.get('priority')}"
        )

    print()

    print(
        "Batches"
    )

    for batch in strategy.get(
        "batches",
        []
    ):

        print(
            f"  Batch "
            f"{batch.get('batch_id')}: "
            f"{len(batch.get('tests', []))} test(s)"
        )

    print()

    print(
        "Recommendation"
    )

    print(
        strategy.get(
            "recommendation",
            ""
        )
    )

    print(
        "============================================================"
    )