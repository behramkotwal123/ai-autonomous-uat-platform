"""
Phase 8B â€” UAT Executive Sign-off Report

Converts the deterministic Phase 8A release-readiness result
into a concise business-facing UAT sign-off report.

This module does NOT change the readiness decision.

Phase 8A remains the authoritative source for:
    READY / NOT_READY
    APPROVE / DO_NOT_APPROVE
    Risk level
"""

from datetime import datetime

from app import release_readiness


def get_value(data, key, default=None):
    if not isinstance(data, dict):
        return default

    return data.get(key, default)


def build_executive_summary(
    release_readiness,
    test_plan,
    coverage_analysis,
):
    status = get_value(
        release_readiness,
        "status",
        "NOT_READY",
    )

    decision = get_value(
        release_readiness,
        "decision",
        "DO_NOT_APPROVE",
    )

    risk_level = get_value(
        release_readiness,
        "risk_level",
        "UNKNOWN",
    )

    planned_tests = get_value(
        release_readiness,
        "planned_tests",
        0,
    )

    executed_tests = get_value(
        release_readiness,
        "executed_tests",
        0,
    )

    passed_tests = get_value(
        release_readiness,
        "passed_tests",
        0,
    )

    failed_tests = get_value(
        release_readiness,
        "failed_tests",
        0,
    )

    skipped_tests = get_value(
        release_readiness,
        "skipped_tests",
        0,
    )

    pass_rate = get_value(
        release_readiness,
        "pass_rate",
        0.0,
    )

    coverage_percentage = get_value(
        release_readiness,
        "coverage_percentage",
        0.0,
    )

    coverage_gaps = get_value(
        release_readiness,
        "coverage_gaps",
        0,
    )

    
    critical_failures_value = get_value(
        release_readiness,
        "critical_failures",
        [],
    )

    if isinstance(critical_failures_value, int):
        critical_failures = critical_failures_value
    else:
        critical_failures = len(
            critical_failures_value or []
        )

    unresolved_failures_value = get_value(
        release_readiness,
        "unresolved_failures",
        [],
    )

    if isinstance(unresolved_failures_value, int):
        unresolved_failures = unresolved_failures_value
    else:
        unresolved_failures = len(
            unresolved_failures_value or []
        )

    if (
        status == "READY"
        and decision == "APPROVE"
    ):
        summary = (
            f"UAT execution completed successfully with "
            f"{passed_tests} of {planned_tests} planned tests "
            f"passed. Documented coverage is "
            f"{coverage_percentage:.1f}% with no unresolved "
            f"failures or critical issues. The UAT cycle "
            f"is ready for release sign-off."
        )
    else:
        summary = (
            f"The UAT cycle is not ready for release sign-off. "
            f"{passed_tests} of {planned_tests} planned tests "
            f"passed, with {failed_tests} failed and "
            f"{unresolved_failures} unresolved failures. "
            f"Documented coverage is "
            f"{coverage_percentage:.1f}%. Outstanding issues "
            f"must be addressed before approval."
        )

    return {
        "summary": summary,
        "status": status,
        "decision": decision,
        "risk_level": risk_level,
        "planned_tests": planned_tests,
        "executed_tests": executed_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "skipped_tests": skipped_tests,
        "pass_rate": pass_rate,
        "coverage_percentage": coverage_percentage,
        "coverage_gaps": coverage_gaps,
        "critical_failures": critical_failures,
        "unresolved_failures": unresolved_failures,
        "test_plan_objective": get_value(
            test_plan,
            "objective",
            "",
        ),
        "generated_at": datetime.now().isoformat(),
    }


def build_signoff_statement(executive_summary):
    status = executive_summary.get(
        "status",
        "NOT_READY",
    )

    decision = executive_summary.get(
        "decision",
        "DO_NOT_APPROVE",
    )

    risk_level = executive_summary.get(
        "risk_level",
        "UNKNOWN",
    )

    if (
        status == "READY"
        and decision == "APPROVE"
    ):
        statement = (
            "Based on the completed UAT execution, documented "
            "coverage, failure analysis and release-readiness "
            "assessment, the solution is READY for UAT sign-off "
            "and release approval."
        )
    else:
        statement = (
            "Based on the completed UAT assessment, the solution "
            "is NOT READY for UAT sign-off. Release approval "
            "should remain blocked until the identified "
            "outstanding issues are resolved."
        )

    return {
        "statement": statement,
        "status": status,
        "decision": decision,
        "risk_level": risk_level,
    }


def build_key_findings(
    release_readiness,
    coverage_analysis,
):
    findings = []

    planned = get_value(
        release_readiness,
        "planned_tests",
        0,
    )

    executed = get_value(
        release_readiness,
        "executed_tests",
        0,
    )

    passed = get_value(
        release_readiness,
        "passed_tests",
        0,
    )

    failed = get_value(
        release_readiness,
        "failed_tests",
        0,
    )

    skipped = get_value(
        release_readiness,
        "skipped_tests",
        0,
    )

    coverage = get_value(
        release_readiness,
        "coverage_percentage",
        0.0,
    )

    gaps = get_value(
        release_readiness,
        "coverage_gaps",
        0,
    )

    critical_value = get_value(
        release_readiness,
        "critical_failures",
        0,
    )

    critical = (
        len(critical_value)
        if isinstance(critical_value, (list, tuple, set))
        else int(critical_value or 0)
    )

    unresolved_value = get_value(
        release_readiness,
        "unresolved_failures",
        0,
    )

    unresolved = (
        len(unresolved_value)
        if isinstance(unresolved_value, (list, tuple, set))
        else int(unresolved_value or 0)
    )

    findings.append(
        f"{executed} of {planned} planned UAT tests were executed."
    )

    findings.append(
        f"{passed} tests passed and {failed} tests failed."
    )

    if skipped == 0:
        findings.append(
            "No UAT tests were skipped."
        )
    else:
        findings.append(
            f"{skipped} UAT test(s) were skipped."
        )

    findings.append(
        f"Documented requirement coverage is {coverage:.1f}%."
    )

    if gaps == 0:
        findings.append(
            "No documented coverage gaps remain."
        )
    else:
        findings.append(
            f"{gaps} documented coverage gap(s) remain."
        )

    if critical == 0:
        findings.append(
            "No critical failures were identified."
        )
    else:
        findings.append(
            f"{critical} critical failure(s) were identified."
        )

    if unresolved == 0:
        findings.append(
            "No unresolved execution failures remain."
        )
    else:
        findings.append(
            f"{unresolved} unresolved failure(s) remain."
        )

    return findings


def build_actions(release_readiness):
    recommendations = get_value(
        release_readiness,
        "recommendations",
        [],
    )

    if not recommendations:
        status = get_value(
            release_readiness,
            "status",
            "NOT_READY",
        )

        if status == "READY":
            return [
                "Proceed with UAT sign-off.",
                "Proceed with the release approval process.",
            ]

        return [
            "Resolve outstanding UAT issues.",
            "Re-run affected tests.",
            "Reassess release readiness before approval.",
        ]

    return list(recommendations)


def build_signoff_report(
    release_readiness,
    test_plan,
    coverage_analysis,
):
    executive_summary = build_executive_summary(
        release_readiness,
        test_plan,
        coverage_analysis,
    )

    signoff_statement = build_signoff_statement(
        executive_summary
    )

    key_findings = build_key_findings(
        release_readiness,
        coverage_analysis,
    )

    actions = build_actions(
        release_readiness
    )

    return {
        "uat_signoff_report": {
            "executive_summary": executive_summary,
            "signoff_statement": signoff_statement,
            "key_findings": key_findings,
            "actions": actions,
        }
    }


def print_signoff_report(result):
    report = result.get(
        "uat_signoff_report",
        {},
    )

    summary = report.get(
        "executive_summary",
        {},
    )

    statement = report.get(
        "signoff_statement",
        {},
    )

    findings = report.get(
        "key_findings",
        [],
    )

    actions = report.get(
        "actions",
        [],
    )

    print()
    print("=" * 60)
    print("             PHASE 8B â€” UAT SIGN-OFF")
    print("=" * 60)

    print()
    print("Executive Summary")
    print(
        f"  {summary.get('summary', '')}"
    )

    print()
    print("UAT Decision")
    print(
        f"  Status       : {statement.get('status', '')}"
    )
    print(
        f"  Recommendation: {statement.get('decision', '')}"
    )
    print(
        f"  Risk level   : {statement.get('risk_level', '')}"
    )

    print()
    print("Key Findings")

    for finding in findings:
        print(f"  - {finding}")

    print()
    print("Sign-off Statement")
    print(
        f"  {statement.get('statement', '')}"
    )

    print()
    print("Actions")

    for action in actions:
        print(f"  - {action}")

    print()
    print("=" * 60)
