from app.scenario_generator import generate_scenarios
from app.scenario_validator import validate_scenarios
from app.coverage_analyzer import analyze_coverage
from app.gap_test_generator import (
    generate_gap_tests,
    print_gap_tests
)


def print_coverage_summary(
    title,
    coverage_analysis
):
    """
    Print a concise deterministic coverage summary.
    """

    coverage = coverage_analysis.get(
        "coverage",
        {}
    )

    requirements = coverage.get(
        "requirements",
        []
    )

    covered = coverage.get(
        "covered",
        0
    )

    uncovered = coverage.get(
        "uncovered",
        0
    )

    not_specified = coverage.get(
        "not_specified",
        0
    )

    coverage_percentage = coverage.get(
        "coverage_percentage",
        0
    )

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)

    print()
    print(
        f"Requirements : {len(requirements)}"
    )

    print(
        f"Covered      : {covered}"
    )

    print(
        f"Gaps         : {uncovered}"
    )

    print(
        f"Not specified: {not_specified}"
    )

    print(
        f"Coverage     : "
        f"{coverage_percentage:.1f}%"
    )

    print()

    for requirement in requirements:

        requirement_id = requirement.get(
            "requirement_id",
            ""
        )

        status = requirement.get(
            "status",
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


def find_invalid_seat_scenario(
    scenarios
):
    """
    Locate the scenario covering INVALID_SEAT.
    """

    for index, scenario in enumerate(
        scenarios
    ):

        request = scenario.get(
            "request",
            {}
        )

        expected = scenario.get(
            "expected",
            {}
        )

        scenario_text = str(
            scenario.get(
                "scenario",
                ""
            )
        ).upper()

        request_text = str(
            request
        ).upper()

        expected_text = str(
            expected
        ).upper()

        combined_text = (
            scenario_text
            + " "
            + request_text
            + " "
            + expected_text
        )

        if "INVALID_SEAT" in combined_text:

            return index

        if (
            "INVALID" in combined_text
            and "SEAT" in combined_text
        ):

            return index

    return None


def main():

    # =========================================================
    # STEP 1
    # GENERATE ORIGINAL SCENARIOS
    # =========================================================

    print()
    print("Generating scenarios...")

    generated = generate_scenarios()

    scenarios = generated.get(
        "scenarios",
        []
    )

    print(
        f"Generated: {len(scenarios)}"
    )

    print()
    print("Available scenarios:")
    print("-" * 60)

    for scenario in scenarios:

        print(
            f"{scenario.get('id')} | "
            f"{scenario.get('scenario')}"
        )

    # =========================================================
    # STEP 2
    # CREATE CONTROLLED GAP
    # =========================================================

    target_index = find_invalid_seat_scenario(
        scenarios
    )

    if target_index is None:

        print()
        print("=" * 60)
        print("       INVALID_SEAT SCENARIO NOT FOUND")
        print("=" * 60)

        print()
        print(
            "Cannot perform the controlled Phase 6 test."
        )

        return

    removed = scenarios.pop(
        target_index
    )

    print()
    print("=" * 60)
    print("          CONTROLLED GAP CREATED")
    print("=" * 60)

    print()
    print(
        f"Removed scenario : "
        f"{removed.get('id')}"
    )

    print(
        f"Scenario         : "
        f"{removed.get('scenario')}"
    )

    print()
    print(
        f"Scenarios available for coverage: "
        f"{len(scenarios)}"
    )

    # =========================================================
    # STEP 3
    # ANALYZE COVERAGE BEFORE GAP GENERATION
    # =========================================================

    print()
    print(
        "Analyzing coverage before gap generation..."
    )

    coverage_before = analyze_coverage(
        scenarios,
        use_ai=True
    )

    print_coverage_summary(
        "COVERAGE BEFORE GAP TEST GENERATION",
        coverage_before
    )

    coverage_before_data = coverage_before.get(
        "coverage",
        {}
    )

    before_percentage = coverage_before_data.get(
        "coverage_percentage",
        0
    )

    before_gaps = [
        requirement
        for requirement
        in coverage_before_data.get(
            "requirements",
            []
        )
        if requirement.get("status") == "GAP"
    ]

    # =========================================================
    # STEP 4
    # GENERATE TESTS FOR THE GAP
    # =========================================================

    print()
    print(
        "Generating tests for coverage gaps..."
    )

    gap_result = generate_gap_tests(
        scenarios,
        coverage_before,
        max_tests=10
    )

    print_gap_tests(
        gap_result
    )

    generated_gap_tests = gap_result.get(
        "generated_tests",
        []
    )

    if not generated_gap_tests:

        print()
        print("=" * 60)
        print("             PHASE 6C RESULT")
        print("=" * 60)

        print()
        print(
            "STATUS : FAIL"
        )

        print()
        print(
            "No gap tests were generated."
        )

        return

    # =========================================================
    # STEP 5
    # DETERMINISTIC VALIDATION
    # =========================================================

    print()
    print("=" * 60)
    print("       DETERMINISTIC VALIDATION")
    print("=" * 60)

    validation_result = validate_scenarios(
        generated_gap_tests
    )

    valid_tests = []
    invalid_count = 0

    for index, validation in enumerate(
        validation_result
    ):

        scenario_id = validation.get(
            "id",
            ""
        )

        valid = validation.get(
            "valid",
            False
        )

        errors = validation.get(
            "errors",
            []
        )

        if valid:

            print(
                f"VALID   | "
                f"{scenario_id}"
            )

            valid_tests.append(
                generated_gap_tests[index]
            )

        else:

            invalid_count += 1

            print(
                f"INVALID | "
                f"{scenario_id}"
            )

            for error in errors:

                print(
                    f"          Error: {error}"
                )

    print()
    print(
        f"Generated gap tests : "
        f"{len(generated_gap_tests)}"
    )

    print(
        f"Valid               : "
        f"{len(valid_tests)}"
    )

    print(
        f"Invalid             : "
        f"{invalid_count}"
    )

    # =========================================================
    # STEP 6
    # ADD ONLY VALIDATED TESTS
    # =========================================================

    if not valid_tests:

        print()
        print("=" * 60)
        print("             PHASE 6C RESULT")
        print("=" * 60)

        print()
        print(
            "STATUS : FAIL"
        )

        print()
        print(
            "No AI-generated tests passed deterministic validation."
        )

        return

    print()
    print(
        "Adding validated AI-generated tests "
        "to the scenario set..."
    )

    for test in valid_tests:

        scenarios.append(
            test
        )

        print(
            f"Added : "
            f"{test.get('id')}"
        )

    # =========================================================
    # STEP 7
    # RE-CALCULATE COVERAGE
    # =========================================================

    print()
    print(
        "Recalculating coverage..."
    )

    coverage_after = analyze_coverage(
        scenarios,
        use_ai=True
    )

    print_coverage_summary(
        "COVERAGE AFTER GAP TEST GENERATION",
        coverage_after
    )

    coverage_after_data = coverage_after.get(
        "coverage",
        {}
    )

    after_percentage = coverage_after_data.get(
        "coverage_percentage",
        0
    )

    after_gaps = [
        requirement
        for requirement
        in coverage_after_data.get(
            "requirements",
            []
        )
        if requirement.get("status") == "GAP"
    ]

    # =========================================================
    # STEP 8
    # VERIFY INVALID_SEAT GAP IS CLOSED
    # =========================================================

    invalid_seat_after = None

    for requirement in coverage_after_data.get(
        "requirements",
        []
    ):

        if requirement.get(
            "requirement_id"
        ) == "INVALID_SEAT":

            invalid_seat_after = requirement

            break

    print()
    print("=" * 60)
    print("          GAP CLOSURE VERIFICATION")
    print("=" * 60)

    print()

    print(
        f"Coverage before : "
        f"{before_percentage:.1f}%"
    )

    print(
        f"Coverage after  : "
        f"{after_percentage:.1f}%"
    )

    print(
        f"Gaps before     : "
        f"{len(before_gaps)}"
    )

    print(
        f"Gaps after      : "
        f"{len(after_gaps)}"
    )

    if invalid_seat_after:

        print()

        print(
            "INVALID_SEAT status after generation:"
        )

        print(
            f"Status          : "
            f"{invalid_seat_after.get('status')}"
        )

        print(
            f"Covered         : "
            f"{invalid_seat_after.get('covered')}"
        )

    # =========================================================
    # STEP 9
    # FINAL RESULT
    # =========================================================

    gap_closed = (
        invalid_seat_after is not None
        and invalid_seat_after.get(
            "status"
        ) == "COVERED"
        and invalid_seat_after.get(
            "covered"
        ) is True
    )

    coverage_improved = (
        after_percentage > before_percentage
    )

    no_remaining_gaps = (
        len(after_gaps) == 0
    )

    print()
    print("=" * 60)
    print("             PHASE 6C RESULT")
    print("=" * 60)

    print()

    print(
        f"AI tests generated       : "
        f"{len(generated_gap_tests)}"
    )

    print(
        f"AI tests validated       : "
        f"{len(valid_tests)}"
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
        f"{len(after_gaps)}"
    )

    if (
        len(valid_tests) > 0
        and invalid_count == 0
        and gap_closed
        and coverage_improved
    ):

        print()
        print(
            "STATUS                   : PASS"
        )

        print()
        print(
            "Phase 6 successfully detected the coverage gap, "
            "generated a test, validated it deterministically, "
            "and closed the gap."
        )

    else:

        print()
        print(
            "STATUS                   : REVIEW"
        )

        print()
        print(
            "The complete gap-closure flow did not "
            "produce the expected result." 
        )


if __name__ == "__main__":
    main()