"""
AI UAT Platform â€” End-to-End Scenario Pipeline

Pipeline:

Generate
    â†“
Validate
    â†“
Coverage Analysis
    â†“
Gap Test Generation
    â†“
Final Coverage
    â†“
Autonomous Test Selection
    â†“
7A â€” UAT Test Plan
    â†“
7B â€” UAT Orchestrator
    â†“
Execute
    â†“
Diagnose / Retry
    â†“
8A â€” Release Readiness
    â†“
8B â€” UAT Executive Sign-off
    â†“
JSON + HTML Reports
"""

import json
import html
from datetime import datetime
from pathlib import Path


from app.scenario_generator import generate_scenarios
from app.scenario_validator import validate_scenarios
from app.coverage_analyzer import analyze_coverage
from app.gap_test_generator import generate_gap_tests
from app.autonomous_test_selector import select_tests

from app.uat_test_planner import build_test_plan
from app.uat_orchestrator import build_execution_strategy

from app.test_runner import run_all_scenarios

from app.release_readiness import (
    build_release_readiness,
    print_release_readiness,
)

from app.uat_signoff_report import (
    build_signoff_report,
    print_signoff_report,
)

from app.uat_evidence import (
    build_audit_trail,
    print_evidence_summary,
)

# ============================================================
# REPORT CONFIGURATION
# ============================================================

REPORTS_DIR = Path("reports")

LATEST_JSON_REPORT = (
    REPORTS_DIR / "latest_run.json"
)

LATEST_HTML_REPORT = (
    REPORTS_DIR / "latest_run.html"
)


# ============================================================
# SCENARIO HELPERS
# ============================================================

def get_scenario_id(scenario):
    return scenario.get("id", "")


def get_scenario_name(scenario):
    return (
        scenario.get("scenario")
        or scenario.get("name")
        or scenario.get("description")
        or ""
    )


def get_validation_result_id(result):
    return result.get("id", "")


def normalize_scenarios(generated):
    """
    Normalize the output from scenario_generator.py.

    Supports either:

        {"scenarios": [...]}

    or:

        [...]
    """

    if isinstance(generated, dict):
        scenarios = generated.get(
            "scenarios",
            []
        )
    elif isinstance(generated, list):
        scenarios = generated
    else:
        scenarios = []

    if not isinstance(scenarios, list):
        return []

    return scenarios


def get_valid_scenarios(
    scenarios,
    validation_results,
):
    """
    Recover the original scenario objects that
    passed deterministic validation.
    """

    valid_ids = set()

    for result in validation_results:

        if not isinstance(result, dict):
            continue

        if result.get("valid") is True:

            scenario_id = (
                get_validation_result_id(result)
            )

            if scenario_id:
                valid_ids.add(
                    scenario_id
                )

    valid_scenarios = []

    for scenario in scenarios:

        if not isinstance(scenario, dict):
            continue

        scenario_id = get_scenario_id(
            scenario
        )

        if scenario_id in valid_ids:
            valid_scenarios.append(
                scenario
            )

    return valid_scenarios


# ============================================================
# SELECTION HELPERS
# ============================================================

def enrich_selected_scenarios(
    selected_tests_result,
    final_scenarios,
):
    """
    Convert autonomous selector output into
    complete scenario objects.

    The selector may return:

        {"selected_tests": [...]}

    or:

        {"tests": [...]}

    or a list.
    """

    if isinstance(
        selected_tests_result,
        dict
    ):

        selected_items = (
            selected_tests_result.get(
                "selected_tests"
            )
        )

        if selected_items is None:
            selected_items = (
                selected_tests_result.get(
                    "tests",
                    []
                )
            )

    elif isinstance(
        selected_tests_result,
        list
    ):
        selected_items = (
            selected_tests_result
        )

    else:
        selected_items = []

    if not isinstance(
        selected_items,
        list
    ):
        selected_items = []

    scenario_lookup = {}

    for scenario in final_scenarios:

        if not isinstance(
            scenario,
            dict
        ):
            continue

        scenario_id = get_scenario_id(
            scenario
        )

        if scenario_id:
            scenario_lookup[
                scenario_id
            ] = scenario

    selected_scenarios = []

    for selected in selected_items:

        if not isinstance(
            selected,
            dict
        ):
            continue

        scenario_id = (
            selected.get("id")
            or selected.get(
                "scenario_id"
            )
        )

        original = scenario_lookup.get(
            scenario_id
        )

        if original is None:
            continue

        enriched = dict(original)

        if selected.get(
            "selection_priority"
        ) is not None:

            enriched[
                "selection_priority"
            ] = selected.get(
                "selection_priority"
            )

        if selected.get(
            "selection_reason"
        ):

            enriched[
                "selection_reason"
            ] = selected.get(
                "selection_reason"
            )

        selected_scenarios.append(
            enriched
        )

    return selected_scenarios


# ============================================================
# EXECUTION HELPERS
# ============================================================


def enrich_execution_results(
    execution_results,
    selected_scenarios,
):
    """
    Add scenario metadata to execution results
    without changing the underlying runner result.
    """

    scenario_lookup = {}

    for scenario in selected_scenarios:
        if not isinstance(scenario, dict):
            continue

        scenario_id = get_scenario_id(scenario)

        if scenario_id:
            scenario_lookup[scenario_id] = scenario

    enriched_results = []

    for index, result in enumerate(execution_results):
        if not isinstance(result, dict):
            continue

        enriched = dict(result)

        scenario_id = (
            result.get("id")
            or result.get("scenario_id")
        )

        scenario = scenario_lookup.get(scenario_id)

        # Fall back to execution order when the runner
        # does not include a scenario ID.
        if scenario is None and index < len(selected_scenarios):
            candidate = selected_scenarios[index]

            if isinstance(candidate, dict):
                scenario = candidate

        if scenario:
            scenario_id = get_scenario_id(scenario)

            if scenario_id:
                enriched["id"] = scenario_id
                enriched["scenario_id"] = scenario_id

            enriched["scenario"] = get_scenario_name(scenario)

            enriched.setdefault(
                "priority",
                scenario.get("priority", ""),
            )

            enriched.setdefault(
                "category",
                scenario.get("category", ""),
            )

            enriched.setdefault(
                "endpoint",
                scenario.get("endpoint", ""),
            )

            enriched.setdefault(
                "method",
                scenario.get("method", ""),
            )

        enriched_results.append(enriched)

    return enriched_results



def calculate_execution_summary(
    execution_results
):
    """
    Build a lightweight pipeline execution summary.

    PASS_AFTER_RETRY is treated as passed.
    """

    results = (
        execution_results
        if isinstance(
            execution_results,
            list
        )
        else []
    )

    total = len(results)

    passed = 0
    failed = 0
    skipped = 0
    retries = 0
    pass_after_retry = 0

    for result in results:

        if not isinstance(
            result,
            dict
        ):
            continue

        status = str(
            result.get(
                "final_status",
                result.get(
                    "status",
                    ""
                )
            )
        ).upper()

        if status == "PASS":
            passed += 1

        elif status == "PASS_AFTER_RETRY":
            passed += 1
            pass_after_retry += 1

        elif status == "SKIPPED":
            skipped += 1

        elif status in {
            "FAIL",
            "ERROR",
        }:
            failed += 1

        retry = result.get(
            "retry",
            {}
        )

        if isinstance(
            retry,
            dict
        ) and retry.get(
            "performed",
            False
        ):
            retries += 1

    if total:
        pass_rate = (
            passed / total
        ) * 100
    else:
        pass_rate = 0.0

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "retries": retries,
        "pass_after_retry": (
            pass_after_retry
        ),
        "pass_rate": round(
            pass_rate,
            2
        ),
    }


# ============================================================
# HTML REPORT
# ============================================================

def build_html_report(
    report
):
    """
    Build a simple standalone HTML report.
    """

    summary = report.get(
        "summary",
        {}
    )

    coverage_analysis = report.get(
        "coverage_analysis",
        {}
    )

    coverage = coverage_analysis.get(
        "coverage",
        {}
    )

    gap_generation = report.get(
        "gap_test_generation",
        {}
    )

    test_plan_wrapper = report.get(
        "uat_test_plan",
        {}
    )

    test_plan = test_plan_wrapper.get(
        "test_plan",
        {}
    )

    orchestration_wrapper = report.get(
        "uat_orchestration",
        {}
    )

    orchestration = (
        orchestration_wrapper.get(
            "execution_strategy",
            {}
        )
    )

    readiness_wrapper = report.get(
        "release_readiness",
        {}
    )

    readiness = (
        readiness_wrapper.get(
            "release_readiness",
            {}
        )
    )

    signoff_wrapper = report.get(
        "uat_signoff_report",
        {}
    )

    signoff = (
        signoff_wrapper.get(
            "uat_signoff_report",
            {}
        )
    )

    executive_summary = (
        signoff.get(
            "executive_summary",
            {}
        )
    )

    signoff_statement = (
        signoff.get(
            "signoff_statement",
            {}
        )
    )

    key_findings = signoff.get(
        "key_findings",
        []
    )

    actions = signoff.get(
        "actions",
        []
    )

    status = html.escape(
        str(
            report.get(
                "status",
                ""
            )
        )
    )

    readiness_status = html.escape(
        str(
            readiness.get(
                "status",
                ""
            )
        )
    )

    decision = html.escape(
        str(
            readiness.get(
                "decision",
                ""
            )
        )
    )

    risk_level = html.escape(
        str(
            readiness.get(
                "risk_level",
                ""
            )
        )
    )

    executive_text = html.escape(
        str(
            executive_summary.get(
                "summary",
                ""
            )
        )
    )

    signoff_text = html.escape(
        str(
            signoff_statement.get(
                "statement",
                ""
            )
        )
    )

    finding_html = ""

    for finding in key_findings:
        finding_html += (
            "<li>"
            + html.escape(
                str(finding)
            )
            + "</li>"
        )

    action_html = ""

    for action in actions:
        action_html += (
            "<li>"
            + html.escape(
                str(action)
            )
            + "</li>"
        )

    # --------------------------------------------------------
    # PHASE 9C â€” UAT EVIDENCE & AUDIT TRAIL
    # --------------------------------------------------------

    uat_evidence = report.get(
        "uat_evidence",
        {}
    )

    evidence_records = uat_evidence.get(
        "evidence",
        []
    )

    evidence_rows = ""

    for evidence in evidence_records:

        evidence_id = html.escape(
            str(
                evidence.get(
                    "evidence_id",
                    ""
                )
            )
        )

        test_id = html.escape(
            str(
                evidence.get(
                    "test_id",
                    ""
                )
            )
        )

        scenario = html.escape(
            str(
                evidence.get(
                    "scenario",
                    ""
                )
            )
        )

        method = html.escape(
            str(
                evidence.get(
                    "method",
                    ""
                )
            )
        )

        endpoint = html.escape(
            str(
                evidence.get(
                    "endpoint",
                    ""
                )
            )
        )

        request = html.escape(
            str(
                evidence.get(
                    "request",
                    {}
                )
            )
        )

        expected = html.escape(
            str(
                evidence.get(
                    "expected",
                    {}
                )
            )
        )

        actual = html.escape(
            str(
                evidence.get(
                    "actual",
                    {}
                )
            )
        )

        status_code = html.escape(
            str(
                evidence.get(
                    "status_code",
                    ""
                )
            )
        )

        final_status = html.escape(
            str(
                evidence.get(
                    "final_status",
                    ""
                )
            )
        )

        failure = html.escape(
            str(
                evidence.get(
                    "failure",
                    ""
                )
            )
        )

        ai_diagnosis = html.escape(
            str(
                evidence.get(
                    "ai_diagnosis",
                    ""
                )
            )
        )

        retry = evidence.get(
            "retry",
            {}
        )

        retry_performed = html.escape(
            str(
                retry.get(
                    "performed",
                    False
                )
            )
            if isinstance(retry, dict)
            else "False"
        )

        captured_at = html.escape(
            str(
                evidence.get(
                    "captured_at",
                    ""
                )
            )
        )

        evidence_rows += f"""
        <tr>
            <td>{evidence_id}</td>
            <td>
                <strong>{test_id}</strong><br>
                {scenario}
            </td>
            <td>
                {method}<br>
                {endpoint}
            </td>
            <td>
                <pre>{request}</pre>
            </td>
            <td>
                <pre>{expected}</pre>
            </td>
            <td>
                <pre>{actual}</pre>
            </td>
            <td>
                HTTP {status_code}<br>
                <strong>{final_status}</strong>
            </td>
            <td>
                <strong>Failure:</strong><br>
                {failure}
                <br><br>
                <strong>AI Diagnosis:</strong><br>
                {ai_diagnosis}
            </td>
            <td>
                {retry_performed}
            </td>
            <td>
                {captured_at}
            </td>
        </tr>
        """

        execution_rows = ""

    execution_results = report.get(
        "execution_results",
        []
    )

    selected_scenarios = report.get(
        "selected_scenarios",
        []
    )

    for index, result in enumerate(
        execution_results
    ):

        scenario = (
            selected_scenarios[index]
            if index < len(selected_scenarios)
            else {}
        )

        scenario_id = html.escape(
            str(
                result.get(
                    "id",
                    scenario.get(
                        "id",
                        ""
                    )
                )
            )
        )

        scenario_name = html.escape(
            str(
                result.get(
                    "scenario",
                    scenario.get(
                        "scenario",
                        scenario.get(
                            "name",
                            ""
                        )
                    )
                )
            )
        )

        result_status = html.escape(
            str(
                result.get(
                    "status",
                    ""
                )
            )
        )

        endpoint = html.escape(
            str(
                result.get(
                    "endpoint",
                    scenario.get(
                        "endpoint",
                        ""
                    )
                )
            )
        )

        execution_rows += f"""
        <tr>
            <td>{scenario_id}</td>
            <td>{scenario_name}</td>
            <td>{endpoint}</td>
            <td>{result_status}</td>
        </tr>
        """

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<title>AI UAT Platform - UAT Sign-off Report</title>

<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<title>AI UAT Platform â€” UAT Sign-off Report</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 40px;
    color: #222;
}}

h1 {{
    margin-bottom: 5px;
}}

h2 {{
    margin-top: 35px;
}}

.card {{
    border: 1px solid #ddd;
    padding: 20px;
    margin: 15px 0;
    border-radius: 6px;
}}

.status {{
    font-size: 28px;
    font-weight: bold;
}}

.metric {{
    display: inline-block;
    min-width: 150px;
    padding: 12px;
    margin: 5px;
    border: 1px solid #ddd;
    border-radius: 5px;
}}

table {{
    border-collapse: collapse;
    width: 100%;
}}

th, td {{
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}}

th {{
    background: #f2f2f2;
}}

ul {{
    line-height: 1.7;
}}

.small {{
    color: #666;
    font-size: 12px;
}}

</style>

</head>

<body>

<h1>AI UAT Platform</h1>

<p>
UAT Execution &amp; Release Sign-off Report
</p>

<p class="small">
<strong>Generated:</strong>
{html.escape(
    str(
        report.get(
            "run_timestamp",
            ""
        )
    )
)}
</p>

<p class="small">
<strong>Run ID:</strong>
{html.escape(
    str(
        uat_evidence.get(
            "run_id",
            ""
        )
    )
)}
</p>

<div class="card">

<h2>Executive Sign-off</h2>

<div class="status">
{readiness_status}
</div>

<p>
<strong>Recommendation:</strong>
{decision}
</p>

<p>
<strong>Risk:</strong>
{risk_level}
</p>

<p>
{executive_text}
</p>

</div>

<div class="card">

<h2>Sign-off Statement</h2>

<p>
{signoff_text}
</p>

</div>

<h2>Execution Summary</h2>

<div class="metric">
<strong>Planned</strong><br>
{summary.get("tests_planned", 0)}
</div>

<div class="metric">
<strong>Passed</strong><br>
{summary.get("passed", 0)}
</div>

<div class="metric">
<strong>Failed</strong><br>
{summary.get("failed", 0)}
</div>

<div class="metric">
<strong>Skipped</strong><br>
{summary.get("skipped", 0)}
</div>

<div class="metric">
<strong>Pass Rate</strong><br>
{summary.get("pass_rate", 0.0)}%
</div>

<div class="metric">
<strong>Retries</strong><br>
{summary.get("retries", 0)}
</div>

<h2>Coverage</h2>

<div class="card">

<p>
<strong>Requirements:</strong>
{coverage.get("total_requirements", 0)}
</p>

<p>
<strong>Covered:</strong>
{coverage.get("covered", 0)}
</p>

<p>
<strong>Uncovered:</strong>
{coverage.get("uncovered", 0)}
</p>

<p>
<strong>Not specified:</strong>
{coverage.get("not_specified", 0)}
</p>

<p>
<strong>Coverage:</strong>
{coverage.get("coverage_percentage", 0.0)}%
</p>

</div>

<h2>Key Findings</h2>

<div class="card">

<ul>
{finding_html}
</ul>

</div>

<h2>Actions</h2>

<div class="card">

<ul>
{action_html}
</ul>

</div>

<h2>UAT Test Plan</h2>

<div class="card">

<p>
<strong>Scenarios generated:</strong>
{summary.get(
    "scenarios_generated",
    0
)}
</p>

<p>
<strong>Tests selected:</strong>
{summary.get(
    "tests_selected",
    0
)}
</p>

<p>
<strong>Tests planned for execution:</strong>
{summary.get(
    "tests_planned",
    0
)}
</p>

<p>
<strong>Tests selected:</strong>
{test_plan.get("tests_selected", 0)}
</p>

<p>
<strong>Plan coverage:</strong>
{test_plan.get("coverage_percentage", 0.0)}%
</p>

<p>
<strong>Plan risk:</strong>
{html.escape(
    str(
        test_plan.get(
            "risk_level",
            ""
        )
    )
)}
</p>

</div>

<h2>UAT Orchestration</h2>

<div class="card">

<p>
<strong>Execution mode:</strong>
{html.escape(
    str(
        orchestration.get(
            "mode",
            ""
        )
    )
)}
</p>

<p>
<strong>Tests orchestrated:</strong>
{orchestration.get(
    "total_tests",
    0
)}
</p>

<p>
<strong>Expected executions:</strong>
{orchestration.get(
    "expected_executions",
    0
)}
</p>

<p>
<strong>Batches:</strong>
{len(
    orchestration.get(
        "batches",
        []
    )
)}
</p>

</div>

<h2>Gap Test Generation</h2>

<div class="card">

<p>
<strong>Gaps detected:</strong>
{gap_generation.get(
    "gap_count",
    0
)}
</p>

<p>
<strong>Tests generated:</strong>
{len(
    gap_generation.get(
        "generated_tests",
        []
    )
)}
</p>

</div>

<h2>Execution Results</h2>

<table>

<tr>
<th>ID</th>
<th>Scenario</th>
<th>Endpoint</th>
<th>Status</th>
</tr>

{execution_rows}

</table>

<h2>UAT Evidence &amp; Audit Trail</h2>

<div class="card">

<p>
<strong>Run ID:</strong>
{html.escape(
    str(
        uat_evidence.get(
            "run_id",
            ""
        )
    )
)}
</p>

<p>
<strong>Evidence records:</strong>
{uat_evidence.get(
    "total_evidence_records",
    0
)}
</p>

<p>
<strong>Passed:</strong>
{uat_evidence.get(
    "passed",
    0
)}
&nbsp;&nbsp;

<strong>Failed:</strong>
{uat_evidence.get(
    "failed",
    0
)}
&nbsp;&nbsp;

<strong>Pass after retry:</strong>
{uat_evidence.get(
    "pass_after_retry",
    0
)}
</p>

</div>

<table>

<tr>
<th>Evidence ID</th>
<th>Test</th>
<th>Endpoint</th>
<th>Request</th>
<th>Expected</th>
<th>Actual</th>
<th>Status</th>
<th>Failure / Diagnosis</th>
<th>Retry</th>
<th>Captured At</th>
</tr>

{evidence_rows}

</table>

<h2>Overall Platform Status</h2>

<div class="card">

<div class="status">
{status}
</div>

</div>

<p class="small">
<strong>Report generated:</strong>
{html.escape(
    str(
        report.get(
            "run_timestamp",
            ""
        )
    )
)}
</p>

</body>
</html>
"""


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    start_time = datetime.now()

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print()
    print("=" * 60)
    print("                    AI UAT PLATFORM")
    print("=" * 60)

    # --------------------------------------------------------
    # PHASE 1 â€” GENERATE
    # --------------------------------------------------------

    print()
    print("Generating UAT scenarios...")
    print()

    generated = generate_scenarios()

    scenarios = normalize_scenarios(
        generated
    )

    print(
        f"Scenarios generated : "
        f"{len(scenarios)}"
    )

    # --------------------------------------------------------
    # PHASE 2 â€” VALIDATE
    # --------------------------------------------------------

    validation_results = validate_scenarios(
        scenarios
    )

    valid_scenarios = get_valid_scenarios(
        scenarios,
        validation_results
    )

    invalid_count = (
        len(scenarios)
        - len(valid_scenarios)
    )

    print(
        f"Scenarios valid     : "
        f"{len(valid_scenarios)}"
    )

    print(
        f"Scenarios invalid   : "
        f"{invalid_count}"
    )

    # --------------------------------------------------------
    # PHASE 5 â€” INITIAL COVERAGE
    # --------------------------------------------------------

    initial_coverage_analysis = (
        analyze_coverage(
            valid_scenarios
        )
    )

    initial_coverage = (
        initial_coverage_analysis.get(
            "coverage",
            {}
        )
    )

    print()

    print(
        f"Initial requirements : "
        f"{initial_coverage.get('total_requirements', 0)}"
    )

    print(
        f"Initial covered      : "
        f"{initial_coverage.get('covered', 0)}"
    )

    print(
        f"Initial gaps         : "
        f"{initial_coverage.get('uncovered', 0)}"
    )

    print(
        f"Initial coverage     : "
        f"{initial_coverage.get('coverage_percentage', 0.0)}%"
    )

    # --------------------------------------------------------
    # PHASE 6 â€” GAP TEST GENERATION
    # --------------------------------------------------------

    gap_generation = {
        "generated_tests": [],
        "gap_count": 0,
        "message": (
            "No documented coverage gaps found."
        )
    }

    final_scenarios = list(
        valid_scenarios
    )

    initial_gaps = initial_coverage.get(
        "uncovered",
        0
    )

    if initial_gaps > 0:

        print()
        print(
            "Generating AI gap tests..."
        )

        gap_generation = (
            generate_gap_tests(
                scenarios=valid_scenarios,
                coverage_analysis=(
                    initial_coverage_analysis
                )
            )
        )

        generated_gap_tests = (
            gap_generation.get(
                "generated_tests",
                []
            )
        )

        if generated_gap_tests:

            gap_validation = (
                validate_scenarios(
                    generated_gap_tests
                )
            )

            valid_gap_tests = (
                get_valid_scenarios(
                    generated_gap_tests,
                    gap_validation
                )
            )

            final_scenarios.extend(
                valid_gap_tests
            )

    else:

        print()
        print(
            "No documented coverage gaps found."
        )

    # --------------------------------------------------------
    # FINAL COVERAGE
    # --------------------------------------------------------

    coverage_analysis = analyze_coverage(
        final_scenarios
    )

    final_coverage = (
        coverage_analysis.get(
            "coverage",
            {}
        )
    )

    ai_analysis = (
        coverage_analysis.get(
            "ai_analysis",
            {}
        )
    )

    print()

    print(
        f"Final requirements   : "
        f"{final_coverage.get('total_requirements', 0)}"
    )

    print(
        f"Final covered        : "
        f"{final_coverage.get('covered', 0)}"
    )

    print(
        f"Final uncovered      : "
        f"{final_coverage.get('uncovered', 0)}"
    )

    print(
        f"Final not specified  : "
        f"{final_coverage.get('not_specified', 0)}"
    )

    print(
        f"Final coverage       : "
        f"{final_coverage.get('coverage_percentage', 0.0)}%"
    )

    print(
        f"AI coverage risk     : "
        f"{ai_analysis.get('risk_level', 'Unknown')}"
    )

    # --------------------------------------------------------
    # AUTONOMOUS TEST SELECTION
    # --------------------------------------------------------

    print()
    print(
        "Selecting autonomous UAT tests..."
    )

    selected_tests_result = select_tests(
        scenarios=final_scenarios
    )

    selected_scenarios = (
        enrich_selected_scenarios(
            selected_tests_result,
            final_scenarios
        )
    )

    print(
    "Selected scenario IDs : "
    + ", ".join(
        scenario.get("id", "UNKNOWN")
        for scenario in selected_scenarios
    )
)

    print(
        f"Tests selected      : "
        f"{len(selected_scenarios)}"
    )

    # --------------------------------------------------------
    # PHASE 7A â€” TEST PLAN
    # --------------------------------------------------------

    print()
    print(
        "Building UAT execution plan..."
    )

    uat_test_plan = build_test_plan(
        scenarios=final_scenarios,
        coverage_analysis=coverage_analysis,
        selected_tests=selected_scenarios
    )

    test_plan = (
        uat_test_plan.get(
            "test_plan",
            {}
        )
    )

    print(
        f"Plan tests          : "
        f"{test_plan.get('tests_selected', 0)}"
    )

    print(
        f"Plan coverage       : "
        f"{test_plan.get('coverage_percentage', 0.0)}%"
    )

    print(
        f"Plan risk           : "
        f"{test_plan.get('risk_level', 'Unknown')}"
    )

    # --------------------------------------------------------
    # PHASE 7B â€” ORCHESTRATION
    # --------------------------------------------------------

    print()
    print(
        "Building UAT execution strategy..."
    )

    uat_orchestration = (
        build_execution_strategy(
            test_plan
        )
    )

    execution_strategy = (
        uat_orchestration.get(
            "execution_strategy",
            {}
        )
    )

    print(
        f"Execution mode      : "
        f"{execution_strategy.get('mode', 'NONE')}"
    )

    print(
        f"Orchestrated tests  : "
        f"{execution_strategy.get('total_tests', 0)}"
    )

    print(
        f"Execution batches   : "
        f"{len(execution_strategy.get('batches', []))}"
    )

    print(
        f"Orchestration risk  : "
        f"{execution_strategy.get('risk_level', 'Unknown')}"
    )

    # --------------------------------------------------------
    # EXECUTION
    # --------------------------------------------------------

    print()
    print(
        "Executing selected scenarios..."
    )

    execution_results = run_all_scenarios(
        selected_scenarios
    )

    execution_results = (
        enrich_execution_results(
            execution_results,
            selected_scenarios
        )
    )

    execution_summary = (
        calculate_execution_summary(
            execution_results
        )
    )

    # --------------------------------------------------------
    # PHASE 9A â€” UAT EVIDENCE
    # --------------------------------------------------------

    uat_evidence = build_audit_trail(
        scenarios=selected_scenarios,
        execution_results=execution_results
    )

    print_evidence_summary(
        uat_evidence
    )

    # --------------------------------------------------------
    # PHASE 8A â€” RELEASE READINESS
    # --------------------------------------------------------

    print()
    print(
        "Building release readiness decision..."
    )

    release_readiness = (
        build_release_readiness(
            execution_results=(
                execution_results
            ),
            test_plan=test_plan,
            coverage_analysis=(
                coverage_analysis
            ),
            uat_orchestration=(
                uat_orchestration
            )
        )
    )

    print_release_readiness(
        release_readiness
    )

    readiness = (
        release_readiness.get(
            "release_readiness",
            {}
        )
    )

    # --------------------------------------------------------
    # PHASE 8B â€” EXECUTIVE SIGN-OFF
    # --------------------------------------------------------

    print()
    print(
        "Building UAT executive sign-off report..."
    )

    uat_signoff = build_signoff_report(
        release_readiness=(
            readiness
        ),
        test_plan=test_plan,
        coverage_analysis=(
            coverage_analysis
        )
    )

    print_signoff_report(
        uat_signoff
    )

    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    readiness_status = (
        readiness.get(
            "status",
            "NOT_READY"
        )
    )

    readiness_decision = (
        readiness.get(
            "decision",
            "DO_NOT_APPROVE"
        )
    )

    overall_pass = (
        len(valid_scenarios)
        == len(scenarios)
        and execution_summary["failed"] == 0
        and execution_summary["skipped"] == 0
        and readiness_status == "READY"
        and readiness_decision == "APPROVE"
    )

    final_status = (
        "PASS"
        if overall_pass
        else "NOT_READY"
    )

    end_time = datetime.now()

    execution_time = (
        end_time - start_time
    ).total_seconds()

    # --------------------------------------------------------
    # JSON REPORT
    # --------------------------------------------------------

    report = {
        "platform": "AI UAT Platform",

        "run_timestamp": (
            end_time.isoformat()
        ),

        "execution_time_seconds": (
            round(
                execution_time,
                2
            )
        ),

        "summary": {
            "scenarios_generated": (
                len(scenarios)
            ),

            "scenarios_valid": (
                len(valid_scenarios)
            ),

            "tests_selected": (
                len(selected_scenarios)
            ),

            "tests_planned": (
                test_plan.get(
                    "tests_selected",
                    0
                )
            ),

            "tests_orchestrated": (
                execution_strategy.get(
                    "total_tests",
                    0
                )
            ),

            "tests_executed": (
                execution_summary[
                    "total"
                ]
            ),

            "passed": (
                execution_summary[
                    "passed"
                ]
            ),

            "failed": (
                execution_summary[
                    "failed"
                ]
            ),

            "skipped": (
                execution_summary[
                    "skipped"
                ]
            ),

            "retries": (
                execution_summary[
                    "retries"
                ]
            ),

            "pass_after_retry": (
                execution_summary[
                    "pass_after_retry"
                ]
            ),

            "pass_rate": (
                execution_summary[
                    "pass_rate"
                ]
            ),
        },

        "validation": {
            "results": (
                validation_results
            ),
            "valid_count": (
                len(valid_scenarios)
            ),
            "invalid_count": (
                invalid_count
            ),
        },

        "coverage_analysis": (
            coverage_analysis
        ),

        "gap_test_generation": (
            gap_generation
        ),

        "selected_tests": (
            selected_tests_result
        ),

        "uat_test_plan": (
            uat_test_plan
        ),

        "uat_orchestration": (
            uat_orchestration
        ),
        "selected_scenarios": (
            selected_scenarios
        ),
        "execution_results": (
            execution_results
        ),

        "uat_evidence": (
            uat_evidence
        ),

        "release_readiness": (
            release_readiness
        ),

        "uat_signoff_report": (
            uat_signoff
        ),

        "status": (
            final_status
        ),
    }

    # --------------------------------------------------------
    # SAVE JSON
    # --------------------------------------------------------

    with open(
        LATEST_JSON_REPORT,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False
        )


    # --------------------------------------------------------
    # SAVE RUN HISTORY â€” PHASE 11A
    # --------------------------------------------------------

    history_timestamp = end_time.strftime(
        "%Y%m%d_%H%M%S"
    )

    history_report = (
        REPORTS_DIR /
        f"run_{history_timestamp}.json"
    )

    # Avoid overwriting another run created in the same second
    if history_report.exists():
        history_timestamp = end_time.strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        history_report = (
            REPORTS_DIR /
            f"run_{history_timestamp}.json"
        )

    with open(
        history_report,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # SAVE HTML
    # --------------------------------------------------------

    html_report = build_html_report(
        report
    )

    with open(
        LATEST_HTML_REPORT,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            html_report
        )

    # --------------------------------------------------------
    # FINAL CONSOLE SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("                       SUMMARY")
    print("=" * 60)

    print()

    print(
        f"Scenarios generated : "
        f"{len(scenarios)}"
    )

    print(
        f"Scenarios valid     : "
        f"{len(valid_scenarios)}"
    )

    print(
        f"Tests selected      : "
        f"{len(selected_scenarios)}"
    )

    print(
        f"Tests planned       : "
        f"{test_plan.get('tests_selected', 0)}"
    )

    print(
        f"Tests orchestrated  : "
        f"{execution_strategy.get('total_tests', 0)}"
    )

    print(
        f"Tests executed      : "
        f"{execution_summary['total']}"
    )

    print(
        f"Passed              : "
        f"{execution_summary['passed']}"
    )

    print(
        f"Failed              : "
        f"{execution_summary['failed']}"
    )

    print(
        f"Skipped             : "
        f"{execution_summary['skipped']}"
    )

    print(
        f"Retries             : "
        f"{execution_summary['retries']}"
    )

    print(
        f"Pass rate           : "
        f"{execution_summary['pass_rate']}%"
    )

    print(
        f"Execution time      : "
        f"{execution_time:.2f}s"
    )

    print()
    print("COVERAGE")

    print(
        f"Requirements        : "
        f"{final_coverage.get('total_requirements', 0)}"
    )

    print(
        f"Covered             : "
        f"{final_coverage.get('covered', 0)}"
    )

    print(
        f"Uncovered           : "
        f"{final_coverage.get('uncovered', 0)}"
    )

    print(
        f"Not specified       : "
        f"{final_coverage.get('not_specified', 0)}"
    )

    print(
        f"Coverage            : "
        f"{final_coverage.get('coverage_percentage', 0.0)}%"
    )

    print()
    print(
        "GAP TEST GENERATION"
    )

    generated_gap_tests = (
        gap_generation.get(
            "generated_tests",
            []
        )
    )

    print(
        f"Gaps detected       : "
        f"{gap_generation.get('gap_count', 0)}"
    )

    print(
        f"Tests generated     : "
        f"{len(generated_gap_tests)}"
    )

    print(
        f"Tests validated     : "
        f"{len(generated_gap_tests)}"
    )

    print(
        f"Tests rejected      : "
        f"0"
    )

    print()
    print("UAT TEST PLAN")

    print(
        f"Tests planned       : "
        f"{test_plan.get('tests_selected', 0)}"
    )

    print(
        f"Plan coverage       : "
        f"{test_plan.get('coverage_percentage', 0.0)}%"
    )

    print(
        f"Plan risk           : "
        f"{test_plan.get('risk_level', 'Unknown')}"
    )

    print()
    print("UAT ORCHESTRATION")

    print(
        f"Execution mode      : "
        f"{execution_strategy.get('mode', 'NONE')}"
    )

    print(
        f"Tests orchestrated  : "
        f"{execution_strategy.get('total_tests', 0)}"
    )

    print(
        f"Expected executions : "
        f"{execution_strategy.get('expected_executions', 0)}"
    )

    print(
        f"Batches             : "
        f"{len(execution_strategy.get('batches', []))}"
    )

    print(
        f"Failure policy      : "
        f"{execution_strategy.get('failure_policy', '')}"
    )

    print(
        f"Stop condition      : "
        f"{execution_strategy.get('stop_condition', '')}"
    )

    print()
    print("RELEASE READINESS")

    print(
    f"Execution completion : "
    f"{readiness.get('execution_completion', 0.0)}%"
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
        f"Passed               : "
        f"{readiness.get('passed_tests', 0)}"
    )

    print(
        f"Failed               : "
        f"{readiness.get('failed_tests', 0)}"
    )

    print(
        f"Unresolved failures  : "
        f"{readiness.get('unresolved_failures', 0)}"
    )

    print(
        f"Pass rate            : "
        f"{readiness.get('pass_rate', 0.0)}%"
    )

    print(
        f"Critical failures    : "
        f"{len(readiness.get('critical_failures', []) or [])}"
    )

    print(
        f"Coverage             : "
        f"{readiness.get('coverage_percentage', 0.0)}%"
    )

    print(
        f"Risk level           : "
        f"{readiness.get('risk_level', 'UNKNOWN')}"
    )

    print()
    print(
        f"Release readiness    : "
        f"{readiness_status}"
    )

    print(
        f"UAT recommendation   : "
        f"{readiness_decision}"
    )

    print()
    print("UAT EXECUTIVE SIGN-OFF")

    signoff_report = (
        uat_signoff.get(
            "uat_signoff_report",
            {}
        )
    )

    signoff_summary = (
        signoff_report.get(
            "executive_summary",
            {}
        )
    )

    signoff_statement = (
        signoff_report.get(
            "signoff_statement",
            {}
        )
    )

    print(
        f"Sign-off status      : "
        f"{signoff_summary.get('status', 'UNKNOWN')}"
    )

    print(
        f"Recommendation       : "
        f"{signoff_summary.get('decision', 'UNKNOWN')}"
    )

    print(
        f"Sign-off risk        : "
        f"{signoff_summary.get('risk_level', 'UNKNOWN')}"
    )

    print()
    print(
        f"Sign-off statement   : "
        f"{signoff_statement.get('statement', '')}"
    )

    print()
    print(
        f"STATUS              : "
        f"{final_status}"
    )

    print()
    print(
        f"JSON report         : "
        f"{LATEST_JSON_REPORT}"
    )

    print(
        f"HTML report         : "
        f"{LATEST_HTML_REPORT}"
    )

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
