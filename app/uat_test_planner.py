"""
Phase 7A - UAT Test Plan Builder

Builds a structured UAT execution plan from:
- validated scenarios
- deterministic coverage analysis
- autonomous test selection

The planner does NOT determine PASS/FAIL.
The deterministic test runner remains the authority for execution results.
"""

from typing import Any, Dict, List


# ---------------------------------------------------------
# PRIORITY ORDER
# ---------------------------------------------------------

PRIORITY_ORDER = {
    "Critical": 1,
    "High": 2,
    "Medium": 3,
    "Low": 4
}


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def get_scenario_id(scenario: Dict[str, Any]) -> str:
    return str(
        scenario.get("id", "")
    )


def get_scenario_name(scenario: Dict[str, Any]) -> str:
    return (
        scenario.get("scenario")
        or scenario.get("description")
        or scenario.get("id")
        or "Unnamed scenario"
    )


def get_priority(scenario: Dict[str, Any]) -> str:
    return (
        scenario.get("selection_priority")
        or scenario.get("priority")
        or "Medium"
    )


def get_endpoint(scenario: Dict[str, Any]) -> str:
    return str(
        scenario.get("endpoint", "")
    )


def get_method(scenario: Dict[str, Any]) -> str:
    return str(
        scenario.get("method", "")
    )


def get_selection_reason(scenario: Dict[str, Any]) -> str:
    return (
        scenario.get("selection_reason")
        or "Selected as part of the UAT test plan."
    )


def get_coverage_requirements(
    scenario: Dict[str, Any],
    coverage_analysis: Dict[str, Any]
) -> List[str]:
    """
    Determine which documented requirements are covered by a scenario.

    This is deterministic and based on the same requirement IDs used
    by the coverage analyzer.
    """

    requirements = (
        coverage_analysis
        .get("coverage", {})
        .get("requirements", [])
    )

    scenario_text = str(
        scenario
    ).upper()

    scenario_id = get_scenario_id(
        scenario
    ).upper()

    scenario_name = get_scenario_name(
        scenario
    ).upper()

    combined_text = (
        scenario_text
        + " "
        + scenario_id
        + " "
        + scenario_name
    )

    matched = []

    for requirement in requirements:

        requirement_id = requirement.get(
            "requirement_id",
            ""
        )

        if not requirement_id:
            continue

        if requirement_id.upper() in combined_text:

            matched.append(
                requirement_id
            )

    return matched


def get_expected_outcome(
    scenario: Dict[str, Any]
) -> str:
    """
    Produce a concise human-readable expected outcome.
    """

    expected = scenario.get(
        "expected",
        {}
    )

    if not isinstance(
        expected,
        dict
    ):
        return str(expected)

    if expected.get("error_code"):

        return (
            f"API should return error "
            f"{expected.get('error_code')}."
        )

    if expected.get("success") is True:

        if expected.get("booking_status"):

            return (
                "API should successfully complete "
                f"the operation with status "
                f"{expected.get('booking_status')}."
            )

        return (
            "API should return a successful response."
        )

    return (
        "API response should satisfy the "
        "expected response contract."
    )


# ---------------------------------------------------------
# EXECUTION ORDER
# ---------------------------------------------------------

def determine_execution_order(
    scenarios: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Determine a deterministic execution order.

    Ordering strategy:

    1. Core search / availability checks
    2. Critical tests
    3. High priority tests
    4. Medium priority tests
    5. Low priority tests

    Within the same priority, preserve the original
    scenario order.
    """

    indexed = []

    for index, scenario in enumerate(
        scenarios
    ):

        name = get_scenario_name(
            scenario
        ).lower()

        endpoint = get_endpoint(
            scenario
        ).lower()

        # Search is a useful prerequisite because it
        # establishes API availability and basic functionality.
        if (
            "/search" in endpoint
            or "search" in name
        ):
            category_order = 1
        else:
            category_order = 2

        priority = get_priority(
            scenario
        )

        priority_order = PRIORITY_ORDER.get(
            priority,
            PRIORITY_ORDER["Medium"]
        )

        indexed.append(
            (
                category_order,
                priority_order,
                index,
                scenario
            )
        )

    indexed.sort(
        key=lambda item: (
            item[0],
            item[1],
            item[2]
        )
    )

    return [
        item[3]
        for item in indexed
    ]


# ---------------------------------------------------------
# TEST PLAN BUILDER
# ---------------------------------------------------------

def build_test_plan(
    scenarios: List[Dict[str, Any]],
    coverage_analysis: Dict[str, Any],
    selected_tests: List[Dict[str, Any]],
    objective: str = (
        "Validate the documented API functionality, "
        "business rules, response contracts, and "
        "negative scenarios before UAT sign-off."
    )
) -> Dict[str, Any]:
    """
    Build a deterministic UAT test plan.

    Parameters
    ----------
    scenarios:
        Full set of validated scenarios.

    coverage_analysis:
        Output from app.coverage_analyzer.

    selected_tests:
        Output from autonomous_test_selector.select_tests().

    objective:
        Human-readable UAT objective.

    Returns
    -------
    dict
        Structured UAT test plan.
    """

    if not isinstance(
        scenarios,
        list
    ):
        scenarios = []

    if not isinstance(
        selected_tests,
        list
    ):
        selected_tests = []

    coverage = coverage_analysis.get(
        "coverage",
        {}
    )

    total_requirements = coverage.get(
        "total_requirements",
        0
    )

    covered_requirements = coverage.get(
        "covered",
        0
    )

    uncovered_requirements = coverage.get(
        "uncovered",
        0
    )

    not_specified = coverage.get(
        "not_specified",
        0
    )

    coverage_percentage = coverage.get(
        "coverage_percentage",
        0.0
    )

    ai_analysis = coverage_analysis.get(
        "ai_analysis",
        {}
    )

    risk_level = ai_analysis.get(
        "risk_level",
        "Low"
    )

    # -----------------------------------------------------
    # Match selected tests back to the actual scenarios.
    # -----------------------------------------------------

    scenario_by_id = {
        get_scenario_id(scenario): scenario
        for scenario in scenarios
        if get_scenario_id(scenario)
    }

    planned_scenarios = []

    for selection in selected_tests:

        if not isinstance(
            selection,
            dict
        ):
            continue

        scenario_id = (
            selection.get("id")
            or selection.get("scenario_id")
        )

        if not scenario_id:
            continue

        scenario = scenario_by_id.get(
            scenario_id
        )

        if scenario is None:
            continue

        planned_scenarios.append(
            {
                "scenario": scenario,
                "selection": selection
            }
        )

    # -----------------------------------------------------
    # If selection metadata isn't available, allow the
    # planner to work directly from the supplied scenarios.
    # -----------------------------------------------------

    if not planned_scenarios:

        for scenario in scenarios:

            planned_scenarios.append(
                {
                    "scenario": scenario,
                    "selection": {}
                }
            )

    ordered_pairs = determine_execution_order(
        [
            item["scenario"]
            for item in planned_scenarios
        ]
    )

    # Rebuild lookup after ordering.
    ordered_lookup = {
        get_scenario_id(scenario): scenario
        for scenario in ordered_pairs
    }

    tests = []

    for order, scenario in enumerate(
        ordered_pairs,
        start=1
    ):

        scenario_id = get_scenario_id(
            scenario
        )

        selection = {}

        for item in planned_scenarios:

            if (
                get_scenario_id(
                    item["scenario"]
                )
                == scenario_id
            ):
                selection = item["selection"]
                break

        priority = (
            selection.get("priority")
            or selection.get("selection_priority")
            or get_priority(scenario)
        )

        selection_reason = (
            selection.get("reason")
            or selection.get("selection_reason")
            or get_selection_reason(scenario)
        )

        coverage_requirements = (
            get_coverage_requirements(
                scenario,
                coverage_analysis
            )
        )

        # A gap-generated test can explicitly identify
        # the requirement it was created to address.
        explicit_requirement = scenario.get(
            "covers_requirement"
        )

        if (
            explicit_requirement
            and explicit_requirement
            not in coverage_requirements
        ):

            coverage_requirements.append(
                explicit_requirement
            )

        tests.append(
            {
                "execution_order": order,
                "id": scenario_id,
                "scenario": get_scenario_name(
                    scenario
                ),
                "category": scenario.get(
                    "category",
                    "General"
                ),
                "priority": priority,
                "method": get_method(
                    scenario
                ),
                "endpoint": get_endpoint(
                    scenario
                ),
                "selection_reason": selection_reason,
                "coverage_requirements": (
                    coverage_requirements
                ),
                "expected_outcome": (
                    get_expected_outcome(
                        scenario
                    )
                )
            }
        )

    # -----------------------------------------------------
    # Determine plan-level recommendation.
    # -----------------------------------------------------

    if uncovered_requirements > 0:

        recommendation = (
            "Coverage gaps remain. Complete gap analysis "
            "and generate or add appropriate tests before "
            "UAT sign-off."
        )

    elif risk_level == "High":

        recommendation = (
            "Coverage is complete, but the assessed risk "
            "is High. Review the identified risks before "
            "UAT sign-off."
        )

    elif risk_level == "Medium":

        recommendation = (
            "Coverage is complete. Review medium-risk "
            "observations before UAT sign-off."
        )

    else:

        recommendation = (
            "Documented coverage is complete and the "
            "planned tests are ready for execution."
        )

    # -----------------------------------------------------
    # Final test plan
    # -----------------------------------------------------

    return {
        "test_plan": {
            "objective": objective,
            "total_scenarios": len(scenarios),
            "tests_selected": len(tests),
            "coverage_percentage": coverage_percentage,
            "total_requirements": total_requirements,
            "covered_requirements": covered_requirements,
            "uncovered_requirements": uncovered_requirements,
            "not_specified_requirements": not_specified,
            "risk_level": risk_level,
            "execution_order": [
                test["id"]
                for test in tests
            ],
            "tests": tests,
            "recommendation": recommendation
        }
    }


# ---------------------------------------------------------
# PRINT TEST PLAN
# ---------------------------------------------------------

def print_test_plan(
    result: Dict[str, Any]
) -> None:
    """
    Print a readable UAT test plan.
    """

    plan = result.get(
        "test_plan",
        {}
    )

    print()
    print("=" * 60)
    print("              UAT TEST PLAN")
    print("=" * 60)

    print()
    print(
        f"Objective           : "
        f"{plan.get('objective', '')}"
    )

    print(
        f"Total scenarios     : "
        f"{plan.get('total_scenarios', 0)}"
    )

    print(
        f"Tests selected      : "
        f"{plan.get('tests_selected', 0)}"
    )

    print(
        f"Coverage            : "
        f"{plan.get('coverage_percentage', 0)}%"
    )

    print(
        f"Risk level          : "
        f"{plan.get('risk_level', 'Unknown')}"
    )

    print()
    print("EXECUTION ORDER")
    print("-" * 60)

    tests = plan.get(
        "tests",
        []
    )

    if not tests:

        print(
            "No tests available."
        )

    for test in tests:

        print(
            f"{test.get('execution_order')}. "
            f"{test.get('id')} | "
            f"{test.get('priority')} | "
            f"{test.get('scenario')}"
        )

        print(
            f"   {test.get('method')} "
            f"{test.get('endpoint')}"
        )

        requirements = test.get(
            "coverage_requirements",
            []
        )

        if requirements:

            print(
                f"   Coverage: "
                f"{', '.join(requirements)}"
            )

        print(
            f"   Expected: "
            f"{test.get('expected_outcome')}"
        )

    print()
    print(
        f"Recommendation: "
        f"{plan.get('recommendation', '')}"
    )