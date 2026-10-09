from app.scenario_generator import generate_scenarios
from app.autonomous_test_selector import (
    select_tests,
    print_selection
)


def main():

    print()
    print(
        "Generating scenarios..."
    )

    generated = generate_scenarios()

    scenarios = generated.get(
        "scenarios",
        []
    )

    print(
        f"Generated: {len(scenarios)}"
    )

    print()
    print(
        "Selecting autonomous UAT tests..."
    )

    selected = select_tests(
        scenarios,
        max_tests=5
    )

    print_selection(
        selected
    )


if __name__ == "__main__":
    main()