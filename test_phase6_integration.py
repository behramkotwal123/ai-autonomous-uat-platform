import json

from app.scenario_generator import generate_scenarios
from app.scenario_validator import validate_scenarios
from app.coverage_analyzer import analyze_coverage
from app.gap_test_generator import generate_gap_tests


def find_requirement(coverage_analysis, requirement_id):
    for requirement in coverage_analysis["coverage"]["requirements"]:
        if requirement["requirement_id"] == requirement_id:
            return requirement

    return None


def scenario_text(scenario):
    if isinstance(scenario, dict):
        return json.dumps(
            scenario,
            ensure_ascii=False
        ).upper()

    return str(scenario).upper()


def get_valid_scenarios(
    scenarios,
    validation_results
):
    """
    The validator returns:
        {
            "id": "...",
            "scenario": "...",
            "valid": True,
            "errors": []
        }

    The original scenario dictionary must therefore
    be recovered from the original scenario list using ID.
    """

    valid_ids = {
        result.get("id")
        for result in validation_results
        if result.get("valid") is True
    }

    return [
        scenario
        for scenario in scenarios
        if scenario.get("id") in valid_ids
    ]


def main():

    print()
    print("=" * 60)
    print("        PHASE 6 INTEGRATION TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Generate AI scenarios
    # ---------------------------------------------------------

    print()
    print("Generating AI scenarios...")

    generated = generate_scenarios()

    scenarios = generated.get(
        "scenarios",
        []
    )

    print(
        f"Scenarios generated : "
        f"{len(scenarios)}"
    )

    # ---------------------------------------------------------
    # 2. Validate generated scenarios
    # ---------------------------------------------------------

    validation_results = validate_scenarios(
        scenarios
    )

    valid_scenarios = get_valid_scenarios(
        scenarios,
        validation_results
    )

    print(
        f"Scenarios valid     : "
        f"{len(valid_scenarios)}"
    )

    print(
        f"Scenarios invalid   : "
        f"{len(scenarios) - len(valid_scenarios)}"
    )

    if not valid_scenarios:

        print()
        print(
            "ERROR: No valid scenarios available."
        )

        print("STATUS : FAIL")

        return

    # ---------------------------------------------------------
    # 3. Determine initial coverage
    # ---------------------------------------------------------

    print()
    print("ANALYZING GENERATED SCENARIO COVERAGE")
    print("--------------------------------------")

    initial_coverage = analyze_coverage(
        valid_scenarios,
        use_ai=False
    )

    initial = initial_coverage["coverage"]

    print(
        f"Requirements : "
        f"{initial['total_requirements']}"
    )

    print(
        f"Covered      : "
        f"{initial['covered']}"
    )

    print(
        f"Gaps         : "
        f"{initial['uncovered']}"
    )

    print(
        f"Not specified: "
        f"{initial['not_specified']}"
    )

    print(
        f"Coverage     : "
        f"{initial['coverage_percentage']}%"
    )

    invalid_seat_initial = find_requirement(
        initial_coverage,
        "INVALID_SEAT"
    )

    if invalid_seat_initial is None:

        print()
        print(
            "ERROR: INVALID_SEAT requirement "
            "does not exist in coverage analyzer."
        )

        print("STATUS : FAIL")

        return

    print()
    print(
        f"INVALID_SEAT status : "
        f"{invalid_seat_initial['status']}"
    )

    # ---------------------------------------------------------
    # 4. Create controlled INVALID_SEAT gap
    # ---------------------------------------------------------

    remaining_scenarios = list(
        valid_scenarios
    )

    removed_scenario = None

    if invalid_seat_initial["status"] == "COVERED":

        for scenario in valid_scenarios:

            if "INVALID_SEAT" in scenario_text(
                scenario
            ):

                removed_scenario = scenario

                break

        if removed_scenario is None:

            print()
            print(
                "ERROR: INVALID_SEAT is reported "
                "as COVERED, but no matching scenario "
                "was found."
            )

            print()
            print("Available scenarios:")

            for scenario in valid_scenarios:

                print(
                    f"  {scenario.get('id')} | "
                    f"{scenario.get('scenario', '')}"
                )

            print()
            print("STATUS : FAIL")

            return

        remaining_scenarios.remove(
            removed_scenario
        )

        print()
        print("CONTROLLED GAP CREATED")
        print("----------------------")

        print(
            f"Removed scenario : "
            f"{removed_scenario.get('id')}"
        )

        print(
            f"Scenario         : "
            f"{removed_scenario.get('scenario', '')}"
        )

    else:

        print()
        print(
            "INVALID_SEAT is already a natural "
            "coverage gap."
        )

        print(
            "No scenario needs to be removed."
        )

    # ---------------------------------------------------------
    # 5. Coverage BEFORE Phase 6
    # ---------------------------------------------------------

    print()
    print("COVERAGE BEFORE GAP TEST GENERATION")
    print("------------------------------------")

    coverage_before = analyze_coverage(
        remaining_scenarios,
        use_ai=False
    )

    before = coverage_before["coverage"]

    print(
        f"Requirements : "
        f"{before['total_requirements']}"
    )

    print(
        f"Covered      : "
        f"{before['covered']}"
    )

    print(
        f"Gaps         : "
        f"{before['uncovered']}"
    )

    print(
        f"Not specified: "
        f"{before['not_specified']}"
    )

    print(
        f"Coverage     : "
        f"{before['coverage_percentage']}%"
    )

    invalid_seat_before = find_requirement(
        coverage_before,
        "INVALID_SEAT"
    )

    if invalid_seat_before is None:

        print()
        print(
            "ERROR: INVALID_SEAT requirement "
            "not found."
        )

        print("STATUS : FAIL")

        return

    print()
    print(
        f"INVALID_SEAT status : "
        f"{invalid_seat_before['status']}"
    )

    # ---------------------------------------------------------
    # 6. Confirm gap
    # ---------------------------------------------------------

    if invalid_seat_before["status"] != "GAP":

        print()
        print(
            "ERROR: INVALID_SEAT did not become "
            "a GAP."
        )

        print(
            f"Expected : GAP"
        )

        print(
            f"Actual   : "
            f"{invalid_seat_before['status']}"
        )

        print()
        print("STATUS : FAIL")

        return

    print()
    print(
        "Confirmed: INVALID_SEAT is a "
        "deterministic coverage GAP."
    )

    # ---------------------------------------------------------
    # 7. AI Gap Test Generation
    # ---------------------------------------------------------

    print()
    print("AI GAP TEST GENERATION")
    print("----------------------")

    gap_generation = generate_gap_tests(
        remaining_scenarios,
        coverage_before,
        max_tests=10
    )

    gap_tests = gap_generation.get(
    "generated_tests",
    []
    )

    print(
        f"Additional tests generated : "
        f"{len(gap_tests)}"
    )

    if not gap_tests:

        print()
        print(
            "ERROR: AI did not generate "
            "a test for the detected gap."
        )

        print()
        print(
            f"Message: "
            f"{gap_generation.get('message', 'No message')}"
        )

        print()
        print("STATUS : FAIL")

        return

    for test in gap_tests:

        print()

        print(
            f"{test.get('id')} | "
            f"{test.get('covers_requirement')}"
        )

        print(
            f"Category    : "
            f"{test.get('category')}"
        )

        print(
            f"Priority    : "
            f"{test.get('priority')}"
        )

        print(
            f"Description : "
            f"{test.get('description')}"
        )

        print(
            f"Scenario    : "
            f"{test.get('scenario')}"
        )

        print(
            f"Method      : "
            f"{test.get('method')}"
        )

        print(
            f"Endpoint    : "
            f"{test.get('endpoint')}"
        )

    # ---------------------------------------------------------
    # 8. Deterministic validation of AI gap tests
    # ---------------------------------------------------------

    print()
    print("DETERMINISTIC VALIDATION")
    print("------------------------")

    gap_validation_results = validate_scenarios(
        gap_tests
    )

    validated_gap_tests = []

    for result in gap_validation_results:

        scenario_id = result.get(
            "id"
        )

        if result.get("valid") is True:

            # Match the validation result back to
            # the actual generated scenario dictionary.
            matching_test = next(
                (
                    test
                    for test in gap_tests
                    if test.get("id") == scenario_id
                ),
                None
            )

            if matching_test is not None:

                validated_gap_tests.append(
                    matching_test
                )

                print(
                    f"VALID   | "
                    f"{scenario_id}"
                )

        else:

            print(
                f"INVALID | "
                f"{scenario_id}"
            )

            for error in result.get(
                "errors",
                []
            ):

                print(
                    f"          {error}"
                )

    print()

    print(
        f"AI tests generated : "
        f"{len(gap_tests)}"
    )

    print(
        f"AI tests validated : "
        f"{len(validated_gap_tests)}"
    )

    print(
        f"AI tests rejected  : "
        f"{len(gap_tests) - len(validated_gap_tests)}"
    )

    if not validated_gap_tests:

        print()
        print(
            "ERROR: No AI-generated gap tests "
            "passed deterministic validation."
        )

        print()
        print("STATUS : FAIL")

        return

    # ---------------------------------------------------------
    # 9. Add ONLY validated tests
    # ---------------------------------------------------------

    print()
    print("ADDING VALIDATED GAP TESTS")
    print("--------------------------")

    final_scenarios = list(
        remaining_scenarios
    )

    existing_ids = {
        scenario.get("id")
        for scenario in final_scenarios
    }

    added_count = 0

    for scenario in validated_gap_tests:

        scenario_id = scenario.get(
            "id"
        )

        if scenario_id in existing_ids:

            print(
                f"SKIPPED | Duplicate ID | "
                f"{scenario_id}"
            )

            continue

        final_scenarios.append(
            scenario
        )

        existing_ids.add(
            scenario_id
        )

        added_count += 1

        print(
            f"ADDED   | "
            f"{scenario_id} | "
            f"{scenario.get('covers_requirement')}"
        )

    print()

    print(
        f"Gap tests added : "
        f"{added_count}"
    )

    # ---------------------------------------------------------
    # 10. Coverage AFTER Phase 6
    # ---------------------------------------------------------

    print()
    print("COVERAGE AFTER GAP TEST GENERATION")
    print("-----------------------------------")

    coverage_after = analyze_coverage(
        final_scenarios,
        use_ai=False
    )

    after = coverage_after["coverage"]

    print(
        f"Requirements : "
        f"{after['total_requirements']}"
    )

    print(
        f"Covered      : "
        f"{after['covered']}"
    )

    print(
        f"Gaps         : "
        f"{after['uncovered']}"
    )

    print(
        f"Not specified: "
        f"{after['not_specified']}"
    )

    print(
        f"Coverage     : "
        f"{after['coverage_percentage']}%"
    )

    invalid_seat_after = find_requirement(
        coverage_after,
        "INVALID_SEAT"
    )

    if invalid_seat_after is None:

        print()
        print(
            "ERROR: INVALID_SEAT requirement "
            "not found after generation."
        )

        print("STATUS : FAIL")

        return

    # ---------------------------------------------------------
    # 11. Verify gap closure
    # ---------------------------------------------------------

    print()
    print("GAP CLOSURE VERIFICATION")
    print("-------------------------")

    print(
        f"Coverage before : "
        f"{before['coverage_percentage']}%"
    )

    print(
        f"Coverage after  : "
        f"{after['coverage_percentage']}%"
    )

    print(
        f"Gaps before     : "
        f"{before['uncovered']}"
    )

    print(
        f"Gaps after      : "
        f"{after['uncovered']}"
    )

    print()

    print(
        f"INVALID_SEAT status : "
        f"{invalid_seat_after['status']}"
    )

    print(
        f"INVALID_SEAT covered: "
        f"{invalid_seat_after['covered']}"
    )

    # ---------------------------------------------------------
    # 12. Final assertions
    # ---------------------------------------------------------

    coverage_improved = (
        after["coverage_percentage"]
        > before["coverage_percentage"]
    )

    gap_closed = (
        invalid_seat_before["status"] == "GAP"
        and invalid_seat_after["status"] == "COVERED"
    )

    no_remaining_gaps = (
        after["uncovered"] == 0
    )

    tests_validated = (
        len(validated_gap_tests) > 0
    )

    overall_pass = (
        coverage_improved
        and gap_closed
        and no_remaining_gaps
        and tests_validated
    )

    # ---------------------------------------------------------
    # 13. Final result
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("        PHASE 6 INTEGRATION RESULT")
    print("=" * 60)

    print(
        f"AI tests generated       : "
        f"{len(gap_tests)}"
    )

    print(
        f"AI tests validated       : "
        f"{len(validated_gap_tests)}"
    )

    print(
        f"Coverage improved        : "
        f"{coverage_improved}"
    )

    print(
        f"INVALID_SEAT gap closed : "
        f"{gap_closed}"
    )

    print(
        f"Remaining gaps           : "
        f"{after['uncovered']}"
    )

    print(
        f"STATUS                   : "
        f"{'PASS' if overall_pass else 'FAIL'}"
    )

    print()

    if overall_pass:

        print(
            "Phase 6 integration successfully detected "
            "the coverage gap, generated an AI test, "
            "validated it deterministically, and "
            "closed the gap."
        )

    else:

        print(
            "Phase 6 integration did not satisfy "
            "all expected conditions."
        )


if __name__ == "__main__":
    main()