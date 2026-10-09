from app.uat_signoff_report import (
    build_signoff_report,
    print_signoff_report,
)


def run_test():
    release_readiness = {
        "status": "READY",
        "decision": "APPROVE",
        "risk_level": "LOW",
        "planned_tests": 5,
        "executed_tests": 5,
        "passed_tests": 5,
        "failed_tests": 0,
        "skipped_tests": 0,
        "pass_rate": 100.0,
        "coverage_percentage": 100.0,
        "coverage_gaps": 0,
        "critical_failures": [],
        "unresolved_failures": [],
        "recommendations": [
            "UAT execution and documented coverage satisfy "
            "the release readiness criteria."
        ],
    }

    test_plan = {
        "objective": (
            "Validate critical travel API booking and search "
            "functionality before release."
        )
    }

    coverage_analysis = {
        "coverage": {
            "coverage_percentage": 100.0,
            "uncovered": 0,
            "not_specified": 1,
        }
    }

    result = build_signoff_report(
        release_readiness=release_readiness,
        test_plan=test_plan,
        coverage_analysis=coverage_analysis,
    )

    report = result["uat_signoff_report"]

    assert (
        report["executive_summary"]["status"]
        == "READY"
    )

    print(
        "PASS | READY status preserved"
    )

    assert (
        report["executive_summary"]["decision"]
        == "APPROVE"
    )

    print(
        "PASS | APPROVE decision preserved"
    )

    assert (
        report["executive_summary"]["risk_level"]
        == "LOW"
    )

    print(
        "PASS | LOW risk preserved"
    )

    assert (
        report["executive_summary"]["planned_tests"]
        == 5
    )

    print(
        "PASS | Planned test count preserved"
    )

    assert (
        report["executive_summary"]["passed_tests"]
        == 5
    )

    print(
        "PASS | Passed test count preserved"
    )

    assert (
        report["executive_summary"]["coverage_percentage"]
        == 100.0
    )

    print(
        "PASS | Coverage preserved"
    )

    assert len(
        report["key_findings"]
    ) > 0

    print(
        "PASS | Key findings generated"
    )

    assert len(
        report["actions"]
    ) > 0

    print(
        "PASS | Sign-off actions generated"
    )

    assert (
        "READY for UAT sign-off"
        in report["signoff_statement"]["statement"]
    )

    print(
        "PASS | Executive sign-off statement generated"
    )

    print()
    print("=" * 60)
    print("          PHASE 8B — UAT SIGN-OFF TEST")
    print("=" * 60)

    print_signoff_report(result)

    print()
    print("=" * 60)
    print("          PHASE 8B TEST RESULT")
    print("=" * 60)

    print("UAT Sign-off Report : PASS")
    print("Test Cases          : 9")
    print("STATUS              : PASS")

    print("=" * 60)


if __name__ == "__main__":
    run_test()