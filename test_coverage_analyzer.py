from app.scenario_generator import generate_scenarios
from app.coverage_analyzer import (
    analyze_coverage,
    print_coverage_report
)


def main():

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
    print("Analyzing UAT coverage...")

    analysis = analyze_coverage(
        scenarios,
        use_ai=True
    )

    print_coverage_report(
        analysis
    )


if __name__ == "__main__":
    main()