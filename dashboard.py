import json
import os
import subprocess
import sys
from datetime import datetime

import streamlit as st
from app.recommendation_scenario_generator import (
    build_recommendation_scenario
)
from pathlib import Path

from app.recommendation_scenario_validator import (
    validate_recommendation_scenario
)

from app.recommendation_scenario_readiness import (
    assess_scenario_readiness
)

from app.recommendation_scenario_execution_validator import (
    validate_execution_specification
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Autonomous UAT Platform",
    page_icon=None,
    layout="wide"
)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("AI Autonomous UAT Platform")

st.caption(
    "Travel API testing, automated validation and AI-powered diagnostics"
)


# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------

REPORT_PATH = "reports/latest_run.json"

RECOMMENDATION_AUDIT_PATH = Path(
    "reports/recommendation_decision_audit.json"
)

RECOMMENDATION_SCENARIO_AUDIT_PATH = Path(
    "reports/recommendation_scenario_audit.json"
)

RECOMMENDATION_SCENARIO_EXECUTION_AUDIT_PATH = Path(
    "reports/recommendation_scenario_execution_audit.json"
)

RECOMMENDATION_SCENARIO_SELECTION_AUDIT_PATH = Path(
    "reports/recommendation_scenario_selection_audit.json"
)

RECOMMENDATION_SCENARIO_EXECUTION_SPECIFICATION_AUDIT_PATH = Path(
    "reports/recommendation_scenario_execution_specification_audit.json"
)

if "recommendation_scenario_states" not in st.session_state:

    persisted_scenario_states = {}

    if RECOMMENDATION_SCENARIO_AUDIT_PATH.exists():

        try:

            with open(
                RECOMMENDATION_SCENARIO_AUDIT_PATH,
                "r",
                encoding="utf-8"
            ) as scenario_audit_file:

                persisted_scenario_states = json.load(
                    scenario_audit_file
                )

        except (
            json.JSONDecodeError,
            OSError
        ):

            persisted_scenario_states = {}

    st.session_state.recommendation_scenario_states = (
        persisted_scenario_states
    )

if "recommendation_scenario_selections" not in st.session_state:

    persisted_scenario_selections = {}

    if RECOMMENDATION_SCENARIO_SELECTION_AUDIT_PATH.exists():

        try:

            with open(
                RECOMMENDATION_SCENARIO_SELECTION_AUDIT_PATH,
                "r",
                encoding="utf-8"
            ) as selection_audit_file:

                persisted_scenario_selections = json.load(
                    selection_audit_file
                )

        except (
            json.JSONDecodeError,
            OSError
        ):

            persisted_scenario_selections = {}

    st.session_state.recommendation_scenario_selections = (
        persisted_scenario_selections
    )

if "recommendation_scenario_execution_states" not in st.session_state:
    persisted_execution_states = {}

    if RECOMMENDATION_SCENARIO_EXECUTION_AUDIT_PATH.exists():
        try:
            with open(
                RECOMMENDATION_SCENARIO_EXECUTION_AUDIT_PATH,
                "r",
                encoding="utf-8"
            ) as execution_audit_file:
                persisted_execution_states = json.load(
                    execution_audit_file
                )
        except (json.JSONDecodeError, OSError):
            persisted_execution_states = {}

    st.session_state.recommendation_scenario_execution_states = (
        persisted_execution_states
    )


if "recommendation_scenario_execution_specifications" not in st.session_state:

    persisted_execution_specifications = {}

    if RECOMMENDATION_SCENARIO_EXECUTION_SPECIFICATION_AUDIT_PATH.exists():
        try:
            with open(
                RECOMMENDATION_SCENARIO_EXECUTION_SPECIFICATION_AUDIT_PATH,
                "r",
                encoding="utf-8"
            ) as specification_audit_file:
                persisted_execution_specifications = json.load(
                    specification_audit_file
                )
        except (json.JSONDecodeError, OSError):
            persisted_execution_specifications = {}

    st.session_state.recommendation_scenario_execution_specifications = (
        persisted_execution_specifications
    )

# --------------------------------------------------
# RUN UAT
# --------------------------------------------------

if st.button("Run UAT Suite"):

    with st.spinner(
        "Running autonomous UAT pipeline..."
    ):

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "app.scenario_pipeline"
            ],
            capture_output=True,
            text=True
        )

    if result.returncode == 0:

        st.success(
            "Autonomous UAT pipeline completed successfully."
        )

    else:

        st.error(
            "Autonomous UAT pipeline encountered an error."
        )

        if result.stdout:
            st.markdown("### Pipeline Output")
            st.code(result.stdout)

        if result.stderr:
            st.markdown("### Pipeline Error")
            st.code(result.stderr)

    st.rerun()


# --------------------------------------------------
# LOAD LATEST REPORT
# --------------------------------------------------

if not os.path.exists(REPORT_PATH):

    st.warning(
        "No UAT report found. Run the UAT suite first."
    )

    st.stop()


try:

    with open(
        REPORT_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        report = json.load(file)

except json.JSONDecodeError as error:

    st.error(
        "The latest UAT report could not be read because "
        "it contains invalid JSON."
    )

    st.code(str(error))

    st.stop()


# --------------------------------------------------
# NORMALIZED REPORT DATA
# --------------------------------------------------

summary = report.get(
    "summary",
    {}
)

execution_results = report.get(
    "execution_results",
    []
)

run_timestamp = report.get(
    "run_timestamp",
    ""
)

pipeline_execution_time = report.get(
    "execution_time_seconds",
    0
)

selected_scenarios = report.get(
    "selected_scenarios",
    []
)


# --------------------------------------------------
# UAT EVIDENCE
# --------------------------------------------------

uat_evidence = report.get(
    "uat_evidence",
    {}
)

evidence_records = uat_evidence.get(
    "evidence",
    []
)


# Create lookup by test ID.

evidence_by_test_id = {
    evidence.get("test_id"): evidence
    for evidence in evidence_records
    if evidence.get("test_id")
}


# --------------------------------------------------
# SUMMARY VALUES
# --------------------------------------------------

tests_generated = summary.get(
    "scenarios_generated",
    0
)

tests_valid = summary.get(
    "scenarios_valid",
    0
)

tests_selected = summary.get(
    "tests_selected",
    0
)

tests_planned = summary.get(
    "tests_planned",
    0
)

tests_orchestrated = summary.get(
    "tests_orchestrated",
    0
)

tests_executed = summary.get(
    "tests_executed",
    len(execution_results)
)

passed = summary.get(
    "passed",
    0
)

failed = summary.get(
    "failed",
    0
)

skipped = summary.get(
    "skipped",
    0
)

retries = summary.get(
    "retries",
    0
)

pass_after_retry = summary.get(
    "pass_after_retry",
    0
)

pass_rate = summary.get(
    "pass_rate",
    0
)


# --------------------------------------------------
# RELEASE READINESS
# --------------------------------------------------

release_readiness_wrapper = report.get(
    "release_readiness",
    {}
)

release_readiness = release_readiness_wrapper.get(
    "release_readiness",
    {}
)

release_status = release_readiness.get(
    "status",
    "UNKNOWN"
)

recommendation = release_readiness.get(
    "decision",
    "UNKNOWN"
)

risk_level = release_readiness.get(
    "risk_level",
    "UNKNOWN"
)


# --------------------------------------------------
# UAT SIGN-OFF
# --------------------------------------------------

uat_signoff_report = report.get(
    "uat_signoff_report"
)

signoff_status = "UNKNOWN"

if isinstance(
    uat_signoff_report,
    dict
):

    signoff_details = uat_signoff_report.get(
        "uat_signoff_report",
        uat_signoff_report
    )

    if isinstance(
        signoff_details,
        dict
    ):

        executive_summary = signoff_details.get(
            "executive_summary",
            {}
        )

        signoff_statement = signoff_details.get(
            "signoff_statement",
            {}
        )

        signoff_status = (
            executive_summary.get(
                "status"
            )
            or signoff_statement.get(
                "status"
            )
            or signoff_details.get(
                "status"
            )
            or "UNKNOWN"
        )


# --------------------------------------------------
# UAT SUMMARY
# --------------------------------------------------

st.markdown("## UAT Summary")

col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "Tests Executed",
        tests_executed
    )


with col2:

    st.metric(
        "Passed",
        passed
    )


with col3:

    st.metric(
        "Failed",
        failed
    )


with col4:

    st.metric(
        "Pass Rate",
        f"{pass_rate:.1f}%"
    )


with col5:

    st.metric(
        "Execution Time",
        f"{pipeline_execution_time:.2f}s"
    )


# --------------------------------------------------
# OVERALL STATUS
# --------------------------------------------------

if (
    failed == 0
    and tests_executed > 0
):

    st.success(
        "Overall UAT Status: ALL EXECUTED TESTS PASSED"
    )

elif failed > 0:

    st.error(
        "Overall UAT Status: FAILURES DETECTED"
    )

else:

    st.warning(
        "Overall UAT Status: NO EXECUTED TESTS"
    )


# --------------------------------------------------
# RELEASE STATUS
# --------------------------------------------------

st.markdown("## Release Status")

status_col1, status_col2, status_col3, status_col4 = (
    st.columns(4)
)


with status_col1:

    st.metric(
        "Release Readiness",
        release_status
    )


with status_col2:

    st.metric(
        "Recommendation",
        recommendation
    )


with status_col3:

    st.metric(
        "Risk",
        risk_level
    )


with status_col4:

    st.metric(
        "Sign-off",
        signoff_status
    )


# --------------------------------------------------
# UAT INTELLIGENCE
# --------------------------------------------------

st.markdown("## UAT Intelligence")

release_details = release_readiness

execution_completion = release_details.get(
    "execution_completion",
    0
)

coverage_percentage = release_details.get(
    "coverage_percentage",
    0
)

critical_failures = release_details.get(
    "critical_failures",
    0
)

unresolved_failures = release_details.get(
    "unresolved_failures",
    0
)

coverage_gaps = release_details.get(
    "coverage_gaps",
    0
)

not_specified_requirements = release_details.get(
    "not_specified_requirements",
    0
)


health_col1, health_col2, health_col3, health_col4, health_col5 = (
    st.columns(5)
)


with health_col1:

    st.metric(
        "Execution Completion",
        f"{execution_completion:.1f}%"
    )


with health_col2:

    st.metric(
        "Documented Coverage",
        f"{coverage_percentage:.1f}%"
    )


with health_col3:

    st.metric(
        "Critical Failures",
        critical_failures
    )


with health_col4:

    st.metric(
        "Unresolved Failures",
        unresolved_failures
    )


with health_col5:

    st.metric(
        "Coverage Gaps",
        coverage_gaps
    )


if (
    failed == 0
    and unresolved_failures == 0
    and critical_failures == 0
    and coverage_gaps == 0
):

    st.success(
        "UAT Health: HEALTHY"
    )

else:

    st.warning(
        "UAT Health: ATTENTION REQUIRED"
    )


if not_specified_requirements > 0:

    st.info(
        f"Info: {not_specified_requirements} requirement(s) are not explicitly specified in the documented coverage."
    )

# --------------------------------------------------
# PHASE 10B.4 - ACTIONABLE UAT INTELLIGENCE
# --------------------------------------------------

RECOMMENDATION_STATUSES = {
    "RECOMMENDED",
    "ACCEPTED",
    "REJECTED",
}

st.markdown("## Actionable UAT Intelligence")

# --------------------------------------------------
# RELEASE DECISION
# --------------------------------------------------

if (
    release_status == "READY"
    and recommendation == "APPROVE"
    and risk_level == "LOW"
    and failed == 0
    and critical_failures == 0
    and unresolved_failures == 0
    and coverage_gaps == 0
):
    decision = "APPROVE"
    decision_reason = (
        "All executed tests passed, documented coverage is complete, "
        "no critical or unresolved failures were detected, and no "
        "coverage gaps remain."
    )
else:
    if critical_failures > 0:
        decision = "BLOCK"
        decision_reason = (
            f"{critical_failures} critical failure(s) require resolution "
            "before release."
        )
    elif unresolved_failures > 0:
        decision = "HOLD"
        decision_reason = (
            f"{unresolved_failures} unresolved failure(s) require "
            "resolution before release."
        )
    elif coverage_gaps > 0:
        decision = "HOLD"
        decision_reason = (
            f"{coverage_gaps} coverage gap(s) require additional "
            "testing before release."
        )
    elif failed > 0:
        decision = "HOLD"
        decision_reason = (
            f"{failed} test failure(s) require investigation and "
            "validation before release."
        )
    else:
        decision = "HOLD"
        decision_reason = (
            "Release criteria are not fully satisfied."
        )

decision_col1, decision_col2 = st.columns(2)

with decision_col1:

    st.metric(
        "Release Decision",
        decision
    )

with decision_col2:

    st.metric(
        "Risk Level",
        risk_level
    )

st.write(
    f"**Decision Reason:** {decision_reason}"
)

# --------------------------------------------------
# ACTION REQUIRED
# --------------------------------------------------

if decision == "APPROVE":

    st.success(
        "Action Required: None. UAT criteria are satisfied for release."
    )

else:

    st.warning(
        "Action Required: Review and resolve the outstanding UAT issues "
        "before release."
    )

    if critical_failures > 0:

        st.write(
            f"- Resolve {critical_failures} critical failure(s)."
        )

    if unresolved_failures > 0:

        st.write(
            f"- Resolve {unresolved_failures} unresolved failure(s)."
        )

    if failed > 0:

        st.write(
            f"- Investigate {failed} failed test(s)."
        )

    if coverage_gaps > 0:

        st.write(
            f"- Address {coverage_gaps} coverage gap(s)."
        )

    if not_specified_requirements > 0:

        st.write(
            f"- Review {not_specified_requirements} requirement(s) "
            "that are not explicitly specified in the documented coverage."
        )

st.divider()

# --------------------------------------------------
# COVERAGE INTELLIGENCE
# --------------------------------------------------

st.markdown("### Coverage Intelligence")

coverage_col1, coverage_col2, coverage_col3 = st.columns(3)

with coverage_col1:

    st.metric(
        "Documented Coverage",
        f"{coverage_percentage:.1f}%"
    )

with coverage_col2:

    st.metric(
        "Coverage Gaps",
        coverage_gaps
    )

with coverage_col3:

    st.metric(
        "Unspecified Requirements",
        not_specified_requirements
    )

if coverage_gaps == 0:

    coverage_assessment = "COMPLETE"

    st.success(
        "Coverage Assessment: COMPLETE"
    )

else:

    coverage_assessment = "ATTENTION REQUIRED"

    st.warning(
        "Coverage Assessment: ATTENTION REQUIRED"
    )

if not_specified_requirements > 0:

    st.info(
        f"Observation: {not_specified_requirements} "
        "requirement(s) are not explicitly specified in the "
        "documented coverage."
    )

else:

    st.success(
        "All requirements are explicitly represented in the documented coverage."
    )

st.divider()

# --------------------------------------------------
# RECOMMENDED NEXT TESTS
# --------------------------------------------------

st.markdown("### Recommended Next Tests")

functional_area_data = {}

for scenario in selected_scenarios:

    category = scenario.get(
        "category",
        "Uncategorized"
    )

    if "Booking" in category:
        functional_area = "Booking"

    elif "Flight Search" in category:
        functional_area = "Flight Search"

    else:
        functional_area = category

    if functional_area not in functional_area_data:

        functional_area_data[functional_area] = {
            "total": 0,
            "positive": 0,
            "negative": 0
        }

    functional_area_data[functional_area]["total"] += 1

    if "Positive" in category:

        functional_area_data[functional_area]["positive"] += 1

    elif "Negative" in category:

        functional_area_data[functional_area]["negative"] += 1


# --------------------------------------------------
# COVERAGE DIMENSIONS
# --------------------------------------------------

coverage_dimensions = {}

for functional_area in functional_area_data:

    coverage_dimensions[functional_area] = {
        "positive": False,
        "negative": False,
        "no_result": False,
        "invalid_parameters": False,
        "passenger_cabin": False,
        "boundary_dates": False
    }

    for scenario in selected_scenarios:

        category = scenario.get(
            "category",
            ""
        )

        scenario_name = scenario.get(
            "scenario",
            ""
        ).lower()

        if "Booking" in category:

            scenario_area = "Booking"

        elif "Flight Search" in category:

            scenario_area = "Flight Search"

        else:

            scenario_area = category

        if scenario_area != functional_area:
            continue

        if "Positive" in category:

            coverage_dimensions[
                functional_area
            ]["positive"] = True

        if "Negative" in category:

            coverage_dimensions[
                functional_area
            ]["negative"] = True

        if (
            "no flights" in scenario_name
            or "no result" in scenario_name
            or "no-result" in scenario_name
            or "no results" in scenario_name
        ):

            coverage_dimensions[
                functional_area
            ]["no_result"] = True

        if (
            "invalid" in scenario_name
            or "missing" in scenario_name
            or "empty" in scenario_name
            or "incomplete" in scenario_name
        ):

            coverage_dimensions[
                functional_area
            ]["invalid_parameters"] = True

        if (
            "passenger" in scenario_name
            or "cabin" in scenario_name
        ):

            coverage_dimensions[
                functional_area
            ]["passenger_cabin"] = True

        if (
            "boundary" in scenario_name
            or "date" in scenario_name
        ):

            coverage_dimensions[
                functional_area
            ]["boundary_dates"] = True


# --------------------------------------------------
# BUILD RECOMMENDATIONS
# --------------------------------------------------

recommendations = []

for functional_area, details in functional_area_data.items():

    total = details["total"]
    positive = details["positive"]
    negative = details["negative"]

    dimensions = coverage_dimensions.get(
        functional_area,
        {}
    )

    missing_dimensions = []

    if functional_area == "Flight Search":

        if not dimensions.get("positive"):

            missing_dimensions.append(
                "positive search"
            )

        if not dimensions.get("negative"):

            missing_dimensions.append(
                "negative search"
            )

        if not dimensions.get("no_result"):

            missing_dimensions.append(
                "no-result search"
            )

        if not dimensions.get("invalid_parameters"):

            missing_dimensions.append(
                "invalid or incomplete parameters"
            )

        if not dimensions.get("passenger_cabin"):

            missing_dimensions.append(
                "passenger or cabin combinations"
            )

        if not dimensions.get("boundary_dates"):

            missing_dimensions.append(
                "boundary date conditions"
            )

    if total == 1:

        recommendations.append(
            {
                "priority": "HIGH",
                "area": functional_area,
                "reason": (
                    f"{functional_area} has only "
                    f"{total} documented scenario and "
                    "requires broader coverage."
                ),
                "missing_dimensions": missing_dimensions
            }
        )

    elif total == 2:

        recommendations.append(
            {
                "priority": "MEDIUM",
                "area": functional_area,
                "reason": (
                    f"{functional_area} has only "
                    f"{total} documented scenarios. "
                    "Additional boundary and error coverage "
                    "is recommended."
                ),
                "missing_dimensions": missing_dimensions
            }
        )

    elif positive == 0 or negative == 0:

        recommendations.append(
            {
                "priority": "MEDIUM",
                "area": functional_area,
                "reason": (
                    f"{functional_area} does not currently "
                    "contain both positive and negative "
                    "test coverage."
                ),
                "missing_dimensions": missing_dimensions
            }
        )


# --------------------------------------------------
# RECOMMENDATION SUMMARY
# --------------------------------------------------

high_priority_count = sum(
    1
    for recommendation in recommendations
    if recommendation["priority"] == "HIGH"
)

medium_priority_count = sum(
    1
    for recommendation in recommendations
    if recommendation["priority"] == "MEDIUM"
)

low_priority_count = sum(
    1
    for recommendation in recommendations
    if recommendation["priority"] == "LOW"
)

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:

    st.metric(
        "High Priority",
        high_priority_count
    )

with summary_col2:

    st.metric(
        "Medium Priority",
        medium_priority_count
    )

with summary_col3:

    st.metric(
        "Low Priority",
        low_priority_count
)


# --------------------------------------------------
# RECOMMENDATION STATE
# --------------------------------------------------

if "recommendation_actions" not in st.session_state:

    st.session_state.recommendation_actions = {}


# --------------------------------------------------
# LOAD PERSISTED DECISIONS
# --------------------------------------------------

if "recommendation_decisions" not in st.session_state:

    persisted_recommendation_decisions = {}

    if RECOMMENDATION_AUDIT_PATH.exists():

        try:

            with open(
                RECOMMENDATION_AUDIT_PATH,
                "r",
                encoding="utf-8"
            ) as audit_file:

                persisted_recommendation_decisions = (
                    json.load(audit_file)
                )

        except (
            json.JSONDecodeError,
            OSError
        ):

            persisted_recommendation_decisions = {}

    st.session_state.recommendation_decisions = (
        persisted_recommendation_decisions
    )


if "generated_recommendation_scenarios" not in st.session_state:

    st.session_state.generated_recommendation_scenarios = {}


# --------------------------------------------------
# SAVE RECOMMENDATION DECISIONS
# --------------------------------------------------

def save_recommendation_decisions():

    RECOMMENDATION_AUDIT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        RECOMMENDATION_AUDIT_PATH,
        "w",
        encoding="utf-8"
    ) as audit_file:

        json.dump(
            st.session_state.recommendation_decisions,
            audit_file,
            indent=2
        )

def save_recommendation_scenario_states():

    def save_recommendation_scenario_selections():

        RECOMMENDATION_SCENARIO_SELECTION_AUDIT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
    )

    with open(
        RECOMMENDATION_SCENARIO_SELECTION_AUDIT_PATH,
        "w",
        encoding="utf-8"
    ) as selection_audit_file:

        json.dump(
            st.session_state.recommendation_scenario_selections,
            selection_audit_file,
            indent=2
        )

    RECOMMENDATION_SCENARIO_AUDIT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        RECOMMENDATION_SCENARIO_AUDIT_PATH,
        "w",
        encoding="utf-8"
    ) as scenario_audit_file:

        json.dump(
            st.session_state.recommendation_scenario_states,
            scenario_audit_file,
            indent=2
        )

def save_recommendation_scenario_selections():
    RECOMMENDATION_SCENARIO_SELECTION_AUDIT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        RECOMMENDATION_SCENARIO_SELECTION_AUDIT_PATH,
        "w",
        encoding="utf-8"
    ) as selection_audit_file:
        json.dump(
            st.session_state.recommendation_scenario_selections,
            selection_audit_file,
            indent=2
        )

RECOMMENDATION_SCENARIO_PLANNING_AUDIT_PATH = Path(
    "reports/recommendation_scenario_planning_audit.json"
)

def save_recommendation_scenario_execution_states():
    RECOMMENDATION_SCENARIO_EXECUTION_AUDIT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        RECOMMENDATION_SCENARIO_EXECUTION_AUDIT_PATH,
        "w",
        encoding="utf-8"
    ) as execution_audit_file:
        json.dump(
            st.session_state.recommendation_scenario_execution_states,
            execution_audit_file,
            indent=2
        )

def save_recommendation_scenario_execution_specifications():

    RECOMMENDATION_SCENARIO_EXECUTION_SPECIFICATION_AUDIT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        RECOMMENDATION_SCENARIO_EXECUTION_SPECIFICATION_AUDIT_PATH,
        "w",
        encoding="utf-8"
    ) as specification_audit_file:

        json.dump(
            st.session_state.recommendation_scenario_execution_specifications,
            specification_audit_file,
            indent=2
        )
# --------------------------------------------------
# BUILD RECOMMENDATION PAYLOAD
# --------------------------------------------------

recommendation_payload = []

recommendation_counter = 1

for recommendation in recommendations:

    area = recommendation["area"]

    priority = recommendation["priority"]

    missing_dimensions = recommendation.get(
        "missing_dimensions",
        []
    )

    recommended_tests = []

    # --------------------------------------------------
    # FLIGHT SEARCH
    # --------------------------------------------------

    if area == "Flight Search":

        if "invalid or incomplete parameters" in missing_dimensions:

            recommended_tests.append(
                {
                    "test_type": "Invalid Parameters",
                    "scenario": (
                        "Search with invalid or incomplete "
                        "route parameters."
                    ),
                    "priority": priority,
                    "coverage_dimension": (
                        "invalid or incomplete parameters"
                    )
                }
            )

        if "passenger or cabin combinations" in missing_dimensions:

            recommended_tests.append(
                {
                    "test_type": "Passenger / Cabin",
                    "scenario": (
                        "Search with unsupported passenger "
                        "or cabin configuration."
                    ),
                    "priority": priority,
                    "coverage_dimension": (
                        "passenger or cabin combinations"
                    )
                }
            )

        if "boundary date conditions" in missing_dimensions:

            recommended_tests.append(
                {
                    "test_type": "Boundary Date",
                    "scenario": (
                        "Search using boundary date conditions."
                    ),
                    "priority": priority,
                    "coverage_dimension": (
                        "boundary date conditions"
                    )
                }
            )

    # --------------------------------------------------
    # BOOKING
    # --------------------------------------------------

    elif area == "Booking":

        recommended_tests = [
            {
                "test_type": "Boundary Values",
                "scenario": (
                    "Booking with boundary passenger "
                    "or itinerary values."
                ),
                "priority": priority,
                "coverage_dimension": "boundary values"
            },
            {
                "test_type": "Unsupported Parameters",
                "scenario": (
                    "Booking with unsupported optional parameters."
                ),
                "priority": priority,
                "coverage_dimension": "unsupported parameters"
            },
            {
                "test_type": "Recovery",
                "scenario": (
                    "Booking recovery after an API "
                    "validation failure."
                ),
                "priority": priority,
                "coverage_dimension": "recovery"
            },
            {
                "test_type": "Passenger / Itinerary",
                "scenario": (
                    "Booking with additional passenger "
                    "and itinerary combinations."
                ),
                "priority": priority,
                "coverage_dimension": (
                    "passenger and itinerary combinations"
                )
            }
        ]

    # --------------------------------------------------
    # OTHER AREAS
    # --------------------------------------------------

    else:

        recommended_tests = [
            {
                "test_type": "Positive",
                "scenario": (
                    "Add additional positive scenarios."
                ),
                "priority": priority,
                "coverage_dimension": (
                    "additional positive coverage"
                )
            },
            {
                "test_type": "Negative",
                "scenario": (
                    "Add additional negative scenarios."
                ),
                "priority": priority,
                "coverage_dimension": (
                    "additional negative coverage"
                )
            },
            {
                "test_type": "Boundary / Error",
                "scenario": (
                    "Add boundary and error-condition scenarios."
                ),
                "priority": priority,
                "coverage_dimension": (
                    "boundary and error conditions"
                )
            }
        ]

    # --------------------------------------------------
    # CREATE STABLE RECOMMENDATION RECORDS
    # --------------------------------------------------

    for test in recommended_tests:

        recommendation_id = (
            f"REC-{area.upper().replace(' ', '-')}-"
            f"{recommendation_counter:03d}"
        )

        recommendation_payload.append(
            {
                "recommendation_id": recommendation_id,
                "area": area,
                "priority": test["priority"],
                "test_type": test["test_type"],
                "scenario": test["scenario"],
                "coverage_dimension": test.get(
                    "coverage_dimension",
                    ""
                ),
                "status": "RECOMMENDED"
            }
        )

        recommendation_counter += 1


# --------------------------------------------------
# VALIDATE RECOMMENDATION STATUSES
# --------------------------------------------------

for recommendation in recommendation_payload:

    status = recommendation.get(
        "status",
        "RECOMMENDED"
    )

    if status not in RECOMMENDATION_STATUSES:

        recommendation["status"] = "RECOMMENDED"


# --------------------------------------------------
# DISPLAY RECOMMENDATIONS
# --------------------------------------------------

if recommendations:

    st.write(
        "**Areas Requiring Additional Coverage**"
    )

    st.warning(
        "Additional test coverage is recommended for the "
        "following functional areas."
    )

    for recommendation in recommendations:

        area = recommendation["area"]

        priority = recommendation["priority"]

        reason = recommendation["reason"]

        area_details = functional_area_data.get(
            area,
            {}
        )

        total = area_details.get(
            "total",
            0
        )

        positive = area_details.get(
            "positive",
            0
        )

        negative = area_details.get(
            "negative",
            0
        )

        st.write(
            f"**{priority} | {area}**"
        )

        st.write(
            f"**Coverage:** {total} scenario(s)"
        )

        st.write(
            f"**Positive:** {positive} | "
            f"**Negative:** {negative}"
        )

        st.write(
            f"**Reason:** {reason}"
        )

        missing_dimensions = recommendation.get(
            "missing_dimensions",
            []
        )

        if missing_dimensions:

            st.write(
                "**Missing Coverage Dimensions:**"
            )

            for dimension in missing_dimensions:

                st.write(
                    f"- {dimension}"
                )

        st.write(
            "**Recommended Tests:**"
        )

        area_recommendations = [
            item
            for item in recommendation_payload
            if item["area"] == area
        ]

        if area_recommendations:

            for test in area_recommendations:

                recommendation_id = test[
                    "recommendation_id"
                ]

                persisted_decision = (
                    st.session_state
                    .recommendation_decisions
                    .get(
                        recommendation_id,
                        {}
                    )
                )

                current_status = (
                    persisted_decision.get(
                        "decision"
                    )
                    or st.session_state
                    .recommendation_actions.get(
                        recommendation_id,
                        test["status"]
                    )
                )

                st.write(
                    f"- **{test['test_type']}:** "
                    f"{test['scenario']}"
                )

                st.caption(
                    f"Status: {current_status} | "
                    f"ID: {recommendation_id}"
                )

                # --------------------------------------------------
                # ACTION BUTTONS
                # --------------------------------------------------

                action_col1, action_col2 = st.columns(2)

                with action_col1:

                    if st.button(
                        "Accept",
                        key=(
                            f"accept_"
                            f"{recommendation_id}"
                        ),
                        disabled=(
                            current_status == "ACCEPTED"
                        )
                    ):

                        st.session_state.recommendation_actions[
                            recommendation_id
                        ] = "ACCEPTED"

                        st.session_state.recommendation_decisions[
                            recommendation_id
                        ] = {
                            "decision": "ACCEPTED",
                            "reason": (
                                "User accepted recommendation"
                            ),
                            "timestamp": (
                                datetime.now().isoformat(
                                    timespec="seconds"
                                )
                            )
                        }

                        save_recommendation_decisions()

                        st.rerun()

                with action_col2:

                    if st.button(
                        "Reject",
                        key=(
                            f"reject_"
                            f"{recommendation_id}"
                        ),
                        disabled=(
                            current_status == "REJECTED"
                        )
                    ):

                        st.session_state.recommendation_actions[
                            recommendation_id
                        ] = "REJECTED"

                        st.session_state.recommendation_decisions[
                            recommendation_id
                        ] = {
                            "decision": "REJECTED",
                            "reason": (
                                "User rejected recommendation"
                            ),
                            "timestamp": (
                                datetime.now().isoformat(
                                    timespec="seconds"
                                )
                            )
                        }

                        save_recommendation_decisions()

                        st.rerun()

        else:

            st.info(
                "No immediate additional test coverage "
                "is recommended based on the current "
                "scenario distribution."
            )


# --------------------------------------------------
# DECISION SUMMARY
# --------------------------------------------------

st.markdown("### Decision Summary")

accepted_count = sum(
    1
    for decision in (
        st.session_state
        .recommendation_decisions
        .values()
    )
    if decision.get("decision") == "ACCEPTED"
)

rejected_count = sum(
    1
    for decision in (
        st.session_state
        .recommendation_decisions
        .values()
    )
    if decision.get("decision") == "REJECTED"
)

total_recommendations = len(
    recommendation_payload
)

pending_count = max(
    total_recommendations
    - accepted_count
    - rejected_count,
    0
)

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:

    st.metric(
        "Accepted",
        accepted_count
    )

with summary_col2:

    st.metric(
        "Rejected",
        rejected_count
    )

with summary_col3:

    st.metric(
        "Pending",
        pending_count
)


# --------------------------------------------------
# DECISION AUDIT
# --------------------------------------------------

st.markdown("### Decision Audit")

decision_audit_records = []

for recommendation_id, decision_data in (
    st.session_state
    .recommendation_decisions
    .items()
):

    decision_audit_records.append(
        {
            "Recommendation ID": recommendation_id,
            "Decision": decision_data.get(
                "decision",
                "UNKNOWN"
            ),
            "Reason": decision_data.get(
                "reason",
                ""
            ),
            "Decision Time": decision_data.get(
                "timestamp",
                ""
            )
        }
    )


if decision_audit_records:

    for record in decision_audit_records:

        st.write(
            f"- **{record['Recommendation ID']}** | "
            f"**{record['Decision']}** | "
            f"{record['Reason']} | "
            f"{record['Decision Time']}"
        )

else:

    st.info(
        "No recommendation decisions have been recorded."
    )


# --------------------------------------------------
# GENERATED RECOMMENDATION SCENARIOS
# --------------------------------------------------

st.markdown("### Generated Recommendation Scenarios")

generated_scenarios = []

for recommendation_id, decision_data in (
    st.session_state
    .recommendation_decisions
    .items()
):

    if decision_data.get("decision") != "ACCEPTED":
        continue

    recommendation = next(
        (
            item
            for item in recommendation_payload
            if item["recommendation_id"] == recommendation_id
        ),
        None
    )

    if not recommendation:
        continue

    scenario_id = (
        f"AI-REC-{len(generated_scenarios) + 1:03d}"
    )

    generated_scenario = build_recommendation_scenario(
        recommendation,
        scenario_id
    )

    if not generated_scenario:
        continue

    # --------------------------------------------------
    # VALIDATE GENERATED SCENARIO
    # --------------------------------------------------

    validation_result = validate_recommendation_scenario(
        generated_scenario
    )
    scenario_timestamp = datetime.now().isoformat(
    timespec="seconds"
)

if validation_result["valid"]:

    generated_scenario[
        "recommendation_status"
    ] = "VALIDATED"

    generated_scenario[
        "validation_status"
    ] = "VALID"

    generated_scenario[
        "validation_errors"
    ] = []

    st.session_state.recommendation_scenario_states[
        scenario_id
    ] = {
        "recommendation_id": recommendation_id,
        "status": "VALIDATED",
        "validation_status": "VALID",
        "validation_errors": [],
        "timestamp": scenario_timestamp
    }

    save_recommendation_scenario_states()

else:

    generated_scenario[
        "recommendation_status"
    ] = "GENERATED"

    generated_scenario[
        "validation_status"
    ] = "INVALID"

    generated_scenario[
        "validation_errors"
    ] = validation_result["errors"]

    st.session_state.recommendation_scenario_states[
        scenario_id
    ] = {
        "recommendation_id": recommendation_id,
        "status": "GENERATED",
        "validation_status": "INVALID",
        "validation_errors": validation_result["errors"],
        "timestamp": scenario_timestamp
    }

    save_recommendation_scenario_states()

    # --------------------------------------------------
# ASSESS SCENARIO READINESS
# --------------------------------------------------

readiness_result = assess_scenario_readiness(
    generated_scenario
)

if readiness_result["ready"]:

    generated_scenario[
        "readiness_status"
    ] = "READY_FOR_SELECTION"

    generated_scenario[
        "readiness_reasons"
    ] = []

else:

    generated_scenario[
        "readiness_status"
    ] = "NOT_READY"

    generated_scenario[
        "readiness_reasons"
    ] = readiness_result["reasons"]


# --------------------------------------------------
# PERSIST SCENARIO READINESS
# --------------------------------------------------

st.session_state.recommendation_scenario_states[
    scenario_id
].update(
    {
        "readiness_status": generated_scenario[
            "readiness_status"
        ],
        "readiness_reasons": generated_scenario[
            "readiness_reasons"
        ],
    }
)

save_recommendation_scenario_states()


# --------------------------------------------------
# ADD GENERATED SCENARIO
# --------------------------------------------------

generated_scenarios.append(
    generated_scenario
)


if generated_scenarios:

    for scenario in generated_scenarios:

        st.write(
            f"- **{scenario['id']}** | "
            f"{scenario['scenario']}"
        )

        st.caption(
    f"Recommendation: "
    f"{scenario['recommendation_id']} | "
    f"Status: {scenario['recommendation_status']} | "
    f"Validation: {scenario['validation_status']} | "
    f"Readiness: {scenario['readiness_status']} | "
    f"Category: {scenario['category']} | "
    f"Coverage Dimension: "
    f"{scenario['coverage_dimension']}"
)

        if scenario["validation_status"] == "VALID":

            st.success(
                "Generated scenario validation: VALID"
            )

        else:

            st.error(
                "Generated scenario validation: INVALID"
            )

            for error in scenario[
                "validation_errors"
            ]:

                st.write(
                    f"- {error}"
                )

else:

    st.info(
        "No accepted recommendations have generated "
        "candidate scenarios."
    )

# --------------------------------------------------
# SCENARIO READINESS DISPLAY
# --------------------------------------------------

readiness_status = scenario.get(
    "readiness_status",
    "NOT_READY"
)

if readiness_status == "READY_FOR_SELECTION":

    st.success(
        "Scenario readiness: READY FOR SELECTION"
    )

    # --------------------------------------------------
    # CONTROLLED SCENARIO SELECTION
    # --------------------------------------------------

    scenario_selection = (
        st.session_state
        .recommendation_scenario_selections
        .get(
            scenario["id"],
            {}
        )
    )

    selection_status = scenario_selection.get(
        "status",
        "READY_FOR_SELECTION"
    )

    st.caption(
        f"Selection Status: {selection_status}"
    )

    if st.button(
        "Select for UAT",
        key=f"select_{scenario['id']}",
        disabled=(
            selection_status == "SELECTED"
        )
    ):
        st.session_state.recommendation_scenario_selections[
            scenario["id"]
        ] = {
            "recommendation_id": scenario[
                "recommendation_id"
            ],
            "status": "SELECTED",
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            )
        }

        save_recommendation_scenario_selections()

        st.rerun()

elif readiness_status == "NOT_READY":

    st.warning(
        "Scenario readiness: NOT READY"
    )

    for reason in scenario.get(
        "readiness_reasons",
        []
    ):

        st.write(
            f"- {reason}"
        )

if "recommendation_scenario_plans" not in st.session_state:
    persisted_scenario_plans = {}

    if RECOMMENDATION_SCENARIO_PLANNING_AUDIT_PATH.exists():
        try:
            with open(
                RECOMMENDATION_SCENARIO_PLANNING_AUDIT_PATH,
                "r",
                encoding="utf-8"
            ) as planning_audit_file:
                persisted_scenario_plans = json.load(
                    planning_audit_file
                )
        except (json.JSONDecodeError, OSError):
            persisted_scenario_plans = {}

    st.session_state.recommendation_scenario_plans = (
        persisted_scenario_plans
    )

# --------------------------------------------------
# CONTROLLED SCENARIO PLANNING
# --------------------------------------------------

scenario_plan = (
    st.session_state
    .recommendation_scenario_plans
    .get(
        scenario["id"],
        {}
    )
)

planning_status = scenario_plan.get(
    "status",
    "SELECTED"
)

st.caption(
    f"Planning Status: {planning_status}"
)

if selection_status == "SELECTED":

    if planning_status == "SELECTED":

        if st.button(
            "Plan for UAT",
            key=f"plan_{scenario['id']}"
        ):
            st.session_state.recommendation_scenario_plans[
                scenario["id"]
            ] = {
                "recommendation_id": scenario[
                    "recommendation_id"
                ],
                "scenario_id": scenario["id"],
                "status": "PLANNED",
                "timestamp": datetime.now().isoformat(
                    timespec="seconds"
                )
            }

            save_recommendation_scenario_plans()

            st.rerun()

def save_recommendation_scenario_plans():
    RECOMMENDATION_SCENARIO_PLANNING_AUDIT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        RECOMMENDATION_SCENARIO_PLANNING_AUDIT_PATH,
        "w",
        encoding="utf-8"
    ) as planning_audit_file:
        json.dump(
            st.session_state.recommendation_scenario_plans,
            planning_audit_file,
            indent=2
        )

# --------------------------------------------------
# CONTROLLED EXECUTION HANDOFF
# --------------------------------------------------

if planning_status == "PLANNED":

    execution_state = (
        st.session_state
        .recommendation_scenario_execution_states
        .get(
            scenario["id"],
            {}
        )
    )

    execution_status = execution_state.get(
        "status",
        "PLANNED"
    )

    if execution_status == "PLANNED":

        if st.button(
            "Prepare for Execution",
            key=f"prepare_execution_{scenario['id']}"
        ):
            st.session_state.recommendation_scenario_execution_states[
                scenario["id"]
            ] = {
                "recommendation_id": scenario[
                    "recommendation_id"
                ],
                "scenario_id": scenario["id"],
                "status": "READY_FOR_EXECUTION",
                "timestamp": datetime.now().isoformat(
                    timespec="seconds"
                )
            }

            save_recommendation_scenario_execution_states()

            st.rerun()

    elif execution_status == "READY_FOR_EXECUTION":

        execution_specification = (
            st.session_state
            .recommendation_scenario_execution_specifications
            .get(
                scenario["id"],
                {}
            )
        )

        st.markdown("#### Execution Specification")

        specification_method = st.selectbox(
            "HTTP Method",
            [
                "GET",
                "POST",
                "PUT",
                "PATCH",
                "DELETE"
            ],
            index=(
                [
                    "GET",
                    "POST",
                    "PUT",
                    "PATCH",
                    "DELETE"
                ].index(
                    execution_specification.get(
                        "method",
                        "GET"
                    )
                )
                if execution_specification.get(
                    "method",
                    "GET"
                ) in {
                    "GET",
                    "POST",
                    "PUT",
                    "PATCH",
                    "DELETE"
                }
                else 0
            ),
            key=f"execution_method_{scenario['id']}"
        )

        specification_endpoint = st.text_input(
            "API Endpoint",
            value=execution_specification.get(
                "endpoint",
                ""
            ),
            key=f"execution_endpoint_{scenario['id']}"
        )

        specification_request = st.text_area(
            "Request",
            value=execution_specification.get(
                "request",
                ""
            ),
            key=f"execution_request_{scenario['id']}"
        )

        specification_expected = st.text_area(
            "Expected Result",
            value=execution_specification.get(
                "expected",
                ""
            ),
            key=f"execution_expected_{scenario['id']}"
        )

        if st.button(
            "Save Execution Specification",
            key=f"save_execution_specification_{scenario['id']}"
        ):

            st.session_state.recommendation_scenario_execution_specifications[
                scenario["id"]
            ] = {
                "recommendation_id": scenario[
                    "recommendation_id"
                ],
                "scenario_id": scenario["id"],
                "method": specification_method,
                "endpoint": specification_endpoint.strip(),
                "request": specification_request.strip(),
                "expected": specification_expected.strip(),
                "status": "EXECUTION_SPECIFIED",
                "timestamp": datetime.now().isoformat(
                    timespec="seconds"
                )
            }

            save_recommendation_scenario_execution_specifications()

            st.rerun()

        execution_specification = (
            st.session_state
            .recommendation_scenario_execution_specifications
            .get(
                scenario["id"],
                {}
            )
        )

        execution_validation_input = {
            **scenario,
            "method": execution_specification.get(
                "method",
                ""
            ),
            "endpoint": execution_specification.get(
                "endpoint",
                ""
            ),
            "request": execution_specification.get(
                "request",
                ""
            ),
            "expected": execution_specification.get(
                "expected",
                ""
            ),
        }

        execution_validation = validate_execution_specification(
            execution_validation_input
        )

        if execution_validation["executable"]:

            st.session_state.recommendation_scenario_execution_states[
                scenario["id"]
            ] = {
                "recommendation_id": scenario[
                    "recommendation_id"
                ],
                "scenario_id": scenario["id"],
                "status": "EXECUTABLE",
                "validation_status": "VALID",
                "validation_errors": [],
                "timestamp": datetime.now().isoformat(
                    timespec="seconds"
                )
            }

            save_recommendation_scenario_execution_states()

            st.success(
                "Execution status: EXECUTABLE"
            )

        else:

            st.warning(
                "Execution validation: NOT EXECUTABLE"
            )

            for error in execution_validation["errors"]:

                st.write(
                    f"- {error}"
                )

    elif execution_status == "EXECUTION_VALIDATED":

        execution_specification = (
            st.session_state
            .recommendation_scenario_execution_specifications
            .get(
                scenario["id"],
                {}
            )
        )

        execution_validation_input = {
            **scenario,
            "method": execution_specification.get(
                "method",
                ""
            ),
            "endpoint": execution_specification.get(
                "endpoint",
                ""
            ),
            "request": execution_specification.get(
                "request",
                ""
            ),
            "expected": execution_specification.get(
                "expected",
                ""
            ),
        }

        execution_validation = validate_execution_specification(
            execution_validation_input
        )

        if execution_validation["executable"]:

            st.session_state.recommendation_scenario_execution_states[
                scenario["id"]
            ] = {
                "recommendation_id": scenario[
                    "recommendation_id"
                ],
                "scenario_id": scenario["id"],
                "status": "EXECUTABLE",
                "validation_status": "VALID",
                "validation_errors": [],
                "timestamp": datetime.now().isoformat(
                    timespec="seconds"
                )
            }

            save_recommendation_scenario_execution_states()

            st.success(
                "Execution status: EXECUTABLE"
            )

        else:

            st.warning(
                "Execution validation: NOT EXECUTABLE"
            )

            for error in execution_validation["errors"]:

                st.write(
                    f"- {error}"
                )

    elif execution_status == "EXECUTABLE":

        st.success(
            "Execution status: EXECUTABLE"
        )        

# --------------------------------------------------
# ASSESS SCENARIO READINESS
# --------------------------------------------------

readiness_result = assess_scenario_readiness(
    generated_scenario
)

if readiness_result["ready"]:

    generated_scenario[
        "readiness_status"
    ] = "READY_FOR_SELECTION"

    generated_scenario[
        "readiness_reasons"
    ] = []

else:

    generated_scenario[
        "readiness_status"
    ] = "NOT_READY"

    generated_scenario[
        "readiness_reasons"
    ] = readiness_result["reasons"]

    st.session_state.recommendation_scenario_states[
    scenario_id
].update(
    {
        "readiness_status": generated_scenario[
            "readiness_status"
        ],
        "readiness_reasons": generated_scenario[
            "readiness_reasons"
        ],
    }
)

save_recommendation_scenario_states()
        
# --------------------------------------------------
# SCENARIO HEALTH
# --------------------------------------------------

st.markdown("## Scenario Health")


scenario_results = {}

for index, execution in enumerate(execution_results):

    if index >= len(selected_scenarios):
        continue

    scenario_definition = selected_scenarios[index]

    scenario_id = scenario_definition.get(
        "id",
        f"TEST-{index + 1:03d}"
    )

    scenario_name = scenario_definition.get(
        "scenario",
        "Scenario not available"
    )

    category = scenario_definition.get(
        "category",
        "Uncategorized"
    )

    status = execution.get(
        "status",
        "UNKNOWN"
    )

    if category not in scenario_results:

        scenario_results[category] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }

    scenario_results[category]["total"] += 1

    if status in {
        "PASS",
        "PASS_AFTER_RETRY"
    }:

        scenario_results[category]["passed"] += 1

    elif status == "FAIL":

        scenario_results[category]["failed"] += 1

    scenario_results[category]["tests"].append(
        {
            "id": scenario_id,
            "scenario": scenario_name,
            "status": status
        }
    )


if not scenario_results:

    st.info(
        "No scenario health information is available."
    )

else:

    scenario_columns = st.columns(
        min(len(scenario_results), 4)
    )

    for index, (
        category,
        details
    ) in enumerate(
        scenario_results.items()
    ):

        column = scenario_columns[
            index % len(scenario_columns)
        ]

        with column:

            total = details["total"]
            category_passed = details["passed"]
            category_failed = details["failed"]

            if category_failed == 0:

                status_text = "PASS"

            else:

                status_text = "FAIL"

            st.metric(
                category,
                f"{category_passed}/{total} passed"
            )

            if status_text == "PASS":

                st.success(
                    "PASS"
                )

            else:

                st.error(
                    "FAIL"
                )

# --------------------------------------------------
# TEST HEALTH
# --------------------------------------------------

st.markdown("## Test Health")

test_health = {}

for execution in execution_results:

    endpoint = execution.get(
        "endpoint",
        ""
    )

    if "search" in endpoint.lower():

        functional_area = "Flight Search"

    else:

        functional_area = "Booking"

    if functional_area not in test_health:

        test_health[functional_area] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "retry": 0
        }

    test_health[functional_area]["total"] += 1

    status = execution.get(
        "status",
        ""
    ).upper()

    if status == "PASS":

        test_health[functional_area]["passed"] += 1

    elif status == "FAIL":

        test_health[functional_area]["failed"] += 1

    if execution.get(
        "attempt",
        1
    ) > 1:

        test_health[functional_area]["retry"] += 1


test_health_columns = st.columns(
    len(test_health)
)

for index, (
    functional_area,
    details
) in enumerate(
    test_health.items()
):

    total = details["total"]
    category_passed = details["passed"]
    category_failed = details["failed"]
    retries = details["retry"]

    pass_rate = (
        (category_passed / total) * 100
        if total > 0
        else 0
    )

    with test_health_columns[index]:

        st.metric(
            functional_area,
            f"{category_passed}/{total}"
        )

        st.write(
            f"**Failed:** {category_failed}"
        )

        st.write(
            f"**Retry:** {retries}"
        )

        st.write(
            f"**Pass Rate:** {pass_rate:.1f}%"
        )


# Overall Test Health

total_tests = len(execution_results)

total_passed = sum(
    1
    for execution in execution_results
    if execution.get(
        "status",
        ""
    ).upper() == "PASS"
)

total_failed = sum(
    1
    for execution in execution_results
    if execution.get(
        "status",
        ""
    ).upper() == "FAIL"
)

total_retries = sum(
    1
    for execution in execution_results
    if execution.get(
        "attempt",
        1
    ) > 1
)

overall_pass_rate = (
    (total_passed / total_tests) * 100
    if total_tests > 0
    else 0
)

st.divider()

health_col1, health_col2, health_col3, health_col4 = st.columns(4)

with health_col1:

    st.metric(
        "Overall Tests",
        total_tests
    )

with health_col2:

    st.metric(
        "Passed",
        total_passed
    )

with health_col3:

    st.metric(
        "Failed",
        total_failed
    )

with health_col4:

    st.metric(
        "Pass Rate",
        f"{overall_pass_rate:.1f}%"
    )


if total_failed == 0:

    st.success(
        "Test Health: HEALTHY"
    )

else:

    st.error(
        "Test Health: ATTENTION REQUIRED"
    )


# --------------------------------------------------
# EXECUTION PERFORMANCE
# --------------------------------------------------

st.markdown("## Phase 10A")

test_execution_times = []

for execution in execution_results:

    test_time = execution.get(
        "execution_time_seconds"
    )

    if isinstance(
        test_time,
        (int, float)
    ):

        test_execution_times.append(
            float(test_time)
        )


total_test_execution_time = sum(
    test_execution_times
)

average_test_execution_time = (
    total_test_execution_time
    / len(test_execution_times)
    if test_execution_times
    else 0
)

fastest_test_execution_time = (
    min(test_execution_times)
    if test_execution_times
    else 0
)

slowest_test_execution_time = (
    max(test_execution_times)
    if test_execution_times
    else 0
)

pass_after_retry = sum(
    1
    for execution in execution_results
    if execution.get(
        "attempt",
        1
    ) > 1
    and execution.get(
        "status",
        ""
    ).upper() == "PASS"
)

performance_col1, performance_col2, performance_col3 = (
    st.columns(3)
)

with performance_col1:

    st.metric(
        "Pipeline Execution Time",
        f"{pipeline_execution_time:.2f}s"
    )

    st.metric(
        "Total Test Execution Time",
        f"{total_test_execution_time:.2f}s"
    )

with performance_col2:

    st.metric(
        "Average Test Time",
        f"{average_test_execution_time:.2f}s"
    )

    st.metric(
        "Fastest Test",
        f"{fastest_test_execution_time:.2f}s"
    )

with performance_col3:

    st.metric(
        "Slowest Test",
        f"{slowest_test_execution_time:.2f}s"
    )

    st.metric(
        "Retries",
        total_retries
    )

st.write(
    f"**Pass After Retry:** {pass_after_retry}"
)

if total_failed == 0 and total_retries == 0:

    st.success(
        "Performance Health: HEALTHY"
    )

elif total_failed == 0:

    st.warning(
        "Performance Health: RETRIES DETECTED"
    )

else:

    st.error(
        "Performance Health: ATTENTION REQUIRED"
    )


# --------------------------------------------------
# FAILURE INTELLIGENCE
# --------------------------------------------------

st.markdown("## Failure Intelligence")

if total_failed == 0:

    st.success(
        "No failures detected in this UAT execution."
    )

else:

    failure_records = [
        execution
        for execution in execution_results
        if execution.get(
            "status",
            ""
        ).upper() == "FAIL"
    ]

    st.error(
        f"{len(failure_records)} failure(s) detected."
    )

    for failure in failure_records:

        st.write(
            f"**Endpoint:** {failure.get('endpoint', 'Not available')}"
        )

        st.write(
            f"**Method:** {failure.get('method', 'Not available')}"
        )

        st.write(
            f"**Status Code:** {failure.get('status_code', 'Not available')}"
        )

        st.write(
            f"**Error:** {failure.get('error', 'Not available')}"
        )

        st.divider()


# --------------------------------------------------
# TRACEABILITY
# --------------------------------------------------

st.markdown("## Test Traceability")

for index, scenario in enumerate(selected_scenarios):

    test_id = scenario.get(
        "id",
        f"TEST-{index + 1:03d}"
    )

    scenario_name = scenario.get(
        "scenario",
        "Scenario not available"
    )

    evidence = evidence_by_test_id.get(
        test_id,
        {}
    )

    if evidence:

        endpoint = evidence.get(
            "endpoint",
            "Not available"
        )

        method = evidence.get(
            "method",
            "Not available"
        )

        status_code = evidence.get(
            "status_code",
            "Not available"
        )

        execution_time = evidence.get(
            "execution_time_seconds"
        )

        request = evidence.get(
            "request",
            "Not available"
        )

        expected = evidence.get(
            "expected",
            "Not available"
        )

        actual = evidence.get(
            "actual",
            "Not available"
        )

        final_status = evidence.get(
            "final_status",
            "UNKNOWN"
        )

        evidence_id = evidence.get(
            "evidence_id",
            "Not available"
        )

        retry_data = evidence.get(
            "retry",
            {}
        )

        if isinstance(
            retry_data,
            dict
        ):
            retry = retry_data.get(
                "performed",
                False
            )
        else:
            retry = bool(retry_data)

        ai_diagnosis = evidence.get(
            "ai_diagnosis"
        )

        if not ai_diagnosis:
            ai_diagnosis = "Not required"

        if final_status.upper() == "PASS":
            release_impact = "No release impact"
        else:
            release_impact = "Requires release assessment"

    else:

        endpoint = "Not available"
        method = "Not available"
        status_code = "Not available"
        execution_time = None
        request = "Evidence not available"
        expected = "Evidence not available"
        actual = "Evidence not available"
        final_status = "UNKNOWN"
        evidence_id = "Not available"
        retry = False
        ai_diagnosis = "Not available"
        release_impact = "Traceability incomplete"

    with st.expander(
        f"{test_id} - {scenario_name}"
    ):

        st.write(
            f"**Scenario:** {scenario_name}"
        )

        st.write(
            f"**Endpoint:** {endpoint}"
        )

        st.write(
            f"**Method:** {method}"
        )

        st.write(
            f"**Status Code:** {status_code}"
        )

        if isinstance(
            execution_time,
            (int, float)
        ):

            st.write(
                f"**Execution Time:** "
                f"{pipeline_execution_time:.2f}s"
            )

        else:

            st.write(
                "**Execution Time:** Not available"
            )

        st.write(
            f"**Request:** {request}"
        )

        st.write(
            f"**Expected:** {expected}"
        )

        st.write(
            f"**Actual:** {actual}"
        )

        st.write(
            f"**Result:** {final_status}"
        )

        st.write(
            f"**Evidence ID:** {evidence_id}"
        )

        st.write(
            f"**Retry:** "
            f"{'Yes' if retry else 'No'}"
        )

        st.write(
            f"**AI Diagnosis:** {ai_diagnosis}"
        )

        st.write(
            f"**Release Impact:** {release_impact}"
        )

# --------------------------------------------------
# EVIDENCE INTELLIGENCE
# --------------------------------------------------

st.markdown("## Evidence & Audit")

total_evidence = len(
    evidence_records
)

complete_evidence = 0
missing_evidence = 0

for evidence in evidence_records:

    if (
        evidence.get("test_id")
        and evidence.get("final_status")
        and evidence.get("actual") is not None
        and evidence.get("expected") is not None
    ):

        complete_evidence += 1

    else:

        missing_evidence += 1


evidence_col1, evidence_col2, evidence_col3 = (
    st.columns(3)
)


with evidence_col1:

    st.metric(
        "Evidence Records",
        total_evidence
    )


with evidence_col2:

    st.metric(
        "Complete Evidence",
        complete_evidence
    )


with evidence_col3:

    st.metric(
        "Missing / Incomplete",
        missing_evidence
    )


if (
    total_evidence > 0
    and missing_evidence == 0
):

    st.success(
        "Evidence is complete for all executed tests."
    )

elif total_evidence == 0:

    st.warning(
        "No execution evidence is available."
    )

else:

    st.warning(
        f"{missing_evidence} evidence record(s) "
        "are incomplete."
    )

# --------------------------------------------------
# AI DIAGNOSTICS
# --------------------------------------------------

st.markdown("## AI Diagnostics")

diagnostic_records = []

for evidence in evidence_records:

    diagnosis = evidence.get(
        "ai_diagnosis"
    )

    if diagnosis:

        diagnostic_records.append(
            {
                "test_id": evidence.get(
                    "test_id",
                    "N/A"
                ),
                "scenario": evidence.get(
                    "scenario",
                    "N/A"
                ),
                "diagnosis": diagnosis
            }
        )


if not diagnostic_records:

    if failed == 0:

        st.info(
            "No AI diagnostics were required. "
            "All executed tests passed."
        )

    else:

        st.warning(
            "WARNING: Failures were detected but no AI "
            "diagnostic records are available."
        )

else:

    st.success(
        f"AI diagnostics available for "
        f"{len(diagnostic_records)} test(s)."
    )

    for diagnostic in diagnostic_records:

        with st.expander(
            f"{diagnostic['test_id']} - "
            f"{diagnostic['scenario']}"
        ):

            st.write(
                diagnostic["diagnosis"]
            )

# --------------------------------------------------
# EXECUTION PIPELINE
# --------------------------------------------------

st.markdown("## UAT Execution Pipeline")

pipeline_col1, pipeline_col2, pipeline_col3, pipeline_col4, pipeline_col5 = (
    st.columns(5)
)


with pipeline_col1:

    st.metric(
        "Generated",
        tests_generated
    )


with pipeline_col2:

    st.metric(
        "Valid",
        tests_valid
    )


with pipeline_col3:

    st.metric(
        "Selected",
        tests_selected
    )


with pipeline_col4:

    st.metric(
        "Planned",
        tests_planned
    )


with pipeline_col5:

    st.metric(
        "Orchestrated",
        tests_orchestrated
    )


# --------------------------------------------------
# EXECUTION DETAILS
# --------------------------------------------------

st.markdown("## Execution Details")

detail_col1, detail_col2, detail_col3 = st.columns(3)


with detail_col1:

    st.write(
        f"**Tests Executed:** {tests_executed}"
    )

    st.write(
        f"**Passed:** {passed}"
    )

    st.write(
        f"**Failed:** {failed}"
    )


with detail_col2:

    st.write(
        f"**Skipped:** {skipped}"
    )

    st.write(
        f"**Retries:** {retries}"
    )

    st.write(
        f"**Pass After Retry:** {pass_after_retry}"
    )


with detail_col3:

    st.write(
        f"**Pass Rate:** {pass_rate:.1f}%"
    )

    st.write(
    f"**Execution Time:** "
    f"{pipeline_execution_time:.2f} seconds"
    )


# --------------------------------------------------
# LAST EXECUTION
# --------------------------------------------------

st.markdown("## Last Execution")


if run_timestamp:

    try:

        timestamp = datetime.fromisoformat(
            run_timestamp
        )

        st.write(
            timestamp.strftime(
                "%d %b %Y, %H:%M:%S"
            )
        )

    except ValueError:

        st.write(
            run_timestamp
        )

else:

    st.write(
        "Timestamp not available"
    )


# --------------------------------------------------
# TEST RESULTS
# --------------------------------------------------

st.markdown("## Test Results")


if not execution_results:

    st.info(
        "No execution results are available."
    )

else:

    for index, result in enumerate(
        execution_results
    ):

        # --------------------------------------------------
        # MATCH EXECUTION RESULT TO EVIDENCE
        # --------------------------------------------------

        evidence = {}

        if index < len(evidence_records):

            evidence = evidence_records[index]

        else:

            evidence = evidence_by_test_id.get(
                result.get("id"),
                {}
            )

        test_id = evidence.get(
            "test_id",
            f"TEST-{index + 1:03d}"
        )

        scenario = evidence.get(
            "scenario",
            "Scenario not available"
        )

        category = evidence.get(
            "category",
            "N/A"
        )

        priority = evidence.get(
            "priority",
            "N/A"
        )

        method = result.get(
            "method",
            evidence.get(
                "method",
                "N/A"
            )
        )

        endpoint = result.get(
            "endpoint",
            evidence.get(
                "endpoint",
                "N/A"
            )
        )

        status = result.get(
            "status",
            evidence.get(
                "final_status",
                "UNKNOWN"
            )
        )

        duration = result.get(
            "execution_time_seconds",
            evidence.get(
                "execution_time_seconds",
                0
            )
        )

        # --------------------------------------------------
        # STATUS ICON
        # --------------------------------------------------

        if status in {
            "PASS",
            "PASS_AFTER_RETRY"
        }:

            status_icon = "PASS"

        elif status == "FAIL":

            status_icon = "FAIL"

        else:

            status_icon = "WARNING"

        # --------------------------------------------------
        # TEST EXPANDER
        # --------------------------------------------------

        with st.expander(
            f"{status_icon} "
            f"{test_id} - "
            f"{scenario}"
        ):

            result_col1, result_col2, result_col3, result_col4 = (
                st.columns(4)
            )

            with result_col1:

                st.write(
                    f"**Category:** {category}"
                )

            with result_col2:

                st.write(
                    f"**Priority:** {priority}"
                )

            with result_col3:

                st.write(
                    f"**Method:** {method}"
                )

            with result_col4:

                st.write(
                    f"**Endpoint:** {endpoint}"
                )

            st.write(
                f"**Status:** {status}"
            )

            st.write(
                f"**Duration:** "
                f"{duration:.2f} seconds"
            )


# --------------------------------------------------
# PHASE 10A STATUS
# --------------------------------------------------

st.markdown("## Phase 10A")

st.success(
    "Dashboard foundation successfully loaded the "
    "current Phase 9 report schema."
)


# --------------------------------------------------
# PLATFORM DEVELOPMENT ROADMAP
# --------------------------------------------------

st.markdown("---")
st.header("Platform Development Roadmap")

st.caption(
    "Development milestones are tracked separately from the "
    "runtime UAT execution pipeline. This roadmap is under "
    "reconciliation; statuses reflect currently available evidence."
)

roadmap = [
    {
        "phase": "Phase 1",
        "name": "Scenario Generation",
        "status": "Component identified"
    },
    {
        "phase": "Phase 2",
        "name": "Scenario Validation",
        "status": "Component identified"
    },
    {
        "phase": "Phase 3",
        "name": "Name to be verified",
        "status": "Needs verification"
    },
    {
        "phase": "Phase 4",
        "name": "Name to be verified",
        "status": "Needs verification"
    },
    {
        "phase": "Phase 5",
        "name": "Initial Coverage Analysis",
        "status": "Component identified"
    },
    {
        "phase": "Phase 6",
        "name": "Gap Test Generation",
        "status": "Component and tests identified"
    },
    {
        "phase": "Phase 7",
        "name": "Test Planning and Orchestration",
        "status": "Components and tests identified"
    },
    {
        "phase": "Phase 8",
        "name": "Release Readiness and Executive Sign-off",
        "status": "Components and tests identified"
    },
    {
        "phase": "Phase 9",
        "name": "UAT Evidence and Audit Trail",
        "status": "Evidence components identified"
    },
    {
        "phase": "Phase 10",
        "name": "Dashboard and UAT Intelligence",
        "status": "Dashboard components identified"
    },
    {
        "phase": "Phase 11",
        "name": "Run History and Run Comparison",
        "status": "Dashboard components identified"
    },
    {
        "phase": "Phase 12",
        "name": "Final Validation and Project Readiness",
        "status": "Reported complete; needs verification"
    }
]

with st.expander("View 12-phase development roadmap", expanded=True):

    st.warning(
        "This is a provisional roadmap. A component being present "
        "does not by itself prove that its development phase passed."
    )

    st.dataframe(
        roadmap,
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# REPORT INFORMATION
# --------------------------------------------------

run_id = report.get(
    "run_id"
)

if not run_id:
    run_id = uat_evidence.get(
        "run_id",
        "Not available"
    )

report_col1, report_col2 = st.columns(2)

with report_col1:

    st.write(
        "**Report:** reports/latest_run.json"
    )

with report_col2:

    st.write(
        f"**Run ID:** {run_id}"
    )


# --------------------------------------------------
# PHASE 11A — UAT RUN HISTORY
# --------------------------------------------------

st.markdown("---")
st.header("UAT Run History")

REPORTS_DIR = Path("reports")


def load_run_history():

    history = []

    if not REPORTS_DIR.exists():
        return history

    for history_file in REPORTS_DIR.glob("run_*.json"):

        try:

            with open(
                history_file,
                "r",
                encoding="utf-8"
            ) as file:

                historical_report = json.load(file)

            if not isinstance(historical_report, dict):
                continue

            summary_data = historical_report.get(
                "summary",
                {}
            )

            if not isinstance(summary_data, dict):
                summary_data = {}

            run_timestamp = historical_report.get(
                "run_timestamp"
            )

            # Older reports may not contain a timestamp.
            if not run_timestamp:

                timestamp_text = (
                    history_file.stem.removeprefix("run_")
                )

                try:

                    run_timestamp = datetime.strptime(
                        timestamp_text,
                        "%Y%m%d_%H%M%S"
                    ).isoformat()

                except ValueError:

                    run_timestamp = datetime.fromtimestamp(
                        history_file.stat().st_mtime
                    ).isoformat()

            history.append({
                "file": history_file.name,
                "path": history_file,
                "timestamp": run_timestamp,
                "executed": summary_data.get(
                    "tests_executed",
                    len(historical_report.get(
                        "execution_results",
                        []
                    ))
                ),
                "passed": summary_data.get("passed", 0),
                "failed": summary_data.get("failed", 0),
                "pass_rate": summary_data.get(
                    "pass_rate",
                    0
                ),
                "execution_time": historical_report.get(
                    "execution_time_seconds",
                    0
                ),
                "report": historical_report
            })

        except (
            json.JSONDecodeError,
            OSError,
            TypeError
        ):

            continue

    
    history.sort(
    key=lambda item: item["path"].stat().st_mtime,
    reverse=True
)

    return history


run_history = load_run_history()

if not run_history:

    st.info("No historical UAT runs were found.")

else:

    st.caption(
        f"{len(run_history)} historical run(s) available"
    )

    history_rows = []

    for item in run_history:

        history_rows.append({
            "Run": item["file"],
            "Timestamp": item["timestamp"],
            "Executed": item["executed"],
            "Passed": item["passed"],
            "Failed": item["failed"],
            "Pass Rate (%)": item["pass_rate"],
            "Duration (s)": item["execution_time"]
        })

    st.table(history_rows)

    selected_history_file = st.selectbox(
        "Inspect a historical run",
        options=[
            item["file"]
            for item in run_history
        ]
    )

    selected_run = next(
        item for item in run_history
        if item["file"] == selected_history_file
    )

    selected_report = selected_run["report"]
    selected_summary = selected_report.get(
        "summary",
        {}
    )

    st.subheader("Selected Run Details")

    detail_col1, detail_col2, detail_col3, detail_col4 = (
        st.columns(4)
    )

    detail_col1.metric(
        "Executed",
        selected_run["executed"]
    )

    detail_col2.metric(
        "Passed",
        selected_run["passed"]
    )

    detail_col3.metric(
        "Failed",
        selected_run["failed"]
    )

    detail_col4.metric(
        "Pass Rate",
        f'{selected_run["pass_rate"]}%'
    )

    with st.expander("View historical report data"):

        st.json(selected_report)

        
# --------------------------------------------------
# PHASE 11B - UAT RUN COMPARISON
# --------------------------------------------------

st.markdown("---")
st.header("UAT Run Comparison")

st.caption(
    "Compare two historical runs to identify changes in "
    "test outcomes, pass rate, and execution duration."
)

from datetime import datetime as comparison_datetime


def load_comparison_runs(reports_dir):
    runs = []

    for report_path in reports_dir.glob("run_*.json"):
        try:
            with report_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            summary_data = data.get("summary") or {}
            results = data.get("execution_results") or []

            # Prefer the report timestamp, then legacy summary timestamps.
            timestamp = (
                data.get("run_timestamp")
                or summary_data.get("completed_at")
                or summary_data.get("started_at")
            )

            if not timestamp:
                try:
                    timestamp = comparison_datetime.strptime(
                        report_path.stem.removeprefix("run_"),
                        "%Y%m%d_%H%M%S",
                    ).isoformat()
                except ValueError:
                    timestamp = datetime.fromtimestamp(
                        report_path.stat().st_mtime
                    ).isoformat()

            # Count final outcomes, including successful retries.
            passed = 0
            failed = 0
            skipped = 0

            for result in results:
                final_status = str(
                    result.get("final_status")
                    or result.get("status")
                    or ""
                ).upper()

                if final_status in {
                    "PASS",
                    "PASSED",
                    "PASS_AFTER_RETRY",
                    "PASS_AFTER_RETEST",
                }:
                    passed += 1
                elif final_status in {"SKIP", "SKIPPED"}:
                    skipped += 1
                elif final_status in {"FAIL", "FAILED"}:
                    failed += 1

            # Use summary counts if available; otherwise use result outcomes.
            summary_passed = summary_data.get("tests_passed")
            if summary_passed is None:
                summary_passed = summary_data.get("passed")

            summary_failed = summary_data.get("tests_failed")
            if summary_failed is None:
                summary_failed = summary_data.get("failed")

            if summary_passed is not None:
                passed = int(summary_passed)

            if summary_failed is not None:
                failed = int(summary_failed)

            executed = summary_data.get("tests_executed")
            if executed is None:
                executed = len(results)

            executed = int(executed or 0)

            pass_rate = summary_data.get("pass_rate")
            if pass_rate is None:
                pass_rate = (
                    round(passed / executed * 100, 1)
                    if executed > 0
                    else 0.0
                )

            duration = data.get("execution_time_seconds")
            if duration is None:
                duration = summary_data.get("execution_time_seconds")

            # Zero or missing duration in old reports is treated as unavailable.
            if duration is not None:
                duration = float(duration)
                if duration <= 0:
                    duration = None

            runs.append({
                "file": report_path.name,
                "path": report_path,
                "timestamp": str(timestamp),
                "executed": executed,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "pass_rate": float(pass_rate or 0),
                "duration": duration,
                "results": results,
                "report": data,
            })

        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            continue

    runs.sort(
        key=lambda run: run["path"].stat().st_mtime,
        reverse=True,
    )

    return runs


comparison_runs = load_comparison_runs(Path("reports"))

if len(comparison_runs) < 2:
    st.info("At least two readable historical reports are needed to compare runs.")
else:
    run_labels = {
        run["file"]: (
            f'{run["timestamp"]} | '
            f'{run["passed"]}/{run["executed"]} passed | '
            f'{run["file"]}'
        )
        for run in comparison_runs
    }

    comparison_files = [run["file"] for run in comparison_runs]

    baseline_col, comparison_col = st.columns(2)

    with baseline_col:
        baseline_file = st.selectbox(
            "Baseline run (older/reference)",
            options=comparison_files,
            index=min(1, len(comparison_files) - 1),
            format_func=lambda filename: run_labels[filename],
            key="phase11b_baseline",
        )

    with comparison_col:
        comparison_file = st.selectbox(
            "Comparison run",
            options=comparison_files,
            index=0,
            format_func=lambda filename: run_labels[filename],
            key="phase11b_comparison",
        )

    baseline = next(
        run for run in comparison_runs
        if run["file"] == baseline_file
    )

    current = next(
        run for run in comparison_runs
        if run["file"] == comparison_file
    )

    if baseline_file == comparison_file:
        st.warning("Select two different runs to compare.")
    else:
        st.subheader("Run Metrics")

        metric_cols = st.columns(4)

        metric_cols[0].metric(
            "Tests Executed",
            current["executed"],
            delta=current["executed"] - baseline["executed"],
        )

        metric_cols[1].metric(
            "Tests Passed",
            current["passed"],
            delta=current["passed"] - baseline["passed"],
        )

        metric_cols[2].metric(
            "Tests Failed",
            current["failed"],
            delta=current["failed"] - baseline["failed"],
            delta_color="inverse",
        )

        metric_cols[3].metric(
            "Pass Rate",
            f'{current["pass_rate"]:.1f}%',
            delta=f'{current["pass_rate"] - baseline["pass_rate"]:+.1f} percentage points',
            delta_color="normal",
        )

        duration_cols = st.columns(2)

        with duration_cols[0]:
            baseline_duration = (
                f'{baseline["duration"]:.2f} seconds'
                if baseline["duration"] is not None
                else "N/A"
            )
            st.metric("Baseline Duration", baseline_duration)

        with duration_cols[1]:
            current_duration = (
                f'{current["duration"]:.2f} seconds'
                if current["duration"] is not None
                else "N/A"
            )
            if (
                baseline["duration"] is not None
                and current["duration"] is not None
            ):
                duration_delta = (
                    current["duration"] - baseline["duration"]
                )
                st.metric(
                    "Comparison Duration",
                    current_duration,
                    delta=f"{duration_delta:+.2f} seconds",
                    delta_color="inverse",
                )
            else:
                st.metric("Comparison Duration", current_duration)

        st.subheader("Comparison Assessment")

        if current["failed"] > baseline["failed"]:
            st.error(
                f'Potential regression: failures increased from '
                f'{baseline["failed"]} to {current["failed"]}.'
            )
        elif current["failed"] < baseline["failed"]:
            st.success(
                f'Improvement: failures decreased from '
                f'{baseline["failed"]} to {current["failed"]}.'
            )
        else:
            st.info(
                f'Failure count unchanged at {current["failed"]}.'
            )

        if current["pass_rate"] < baseline["pass_rate"]:
            st.warning("The pass rate has decreased compared with the baseline.")
        elif current["pass_rate"] > baseline["pass_rate"]:
            st.success("The pass rate has improved compared with the baseline.")
        else:
            st.info("The pass rate is unchanged.")

        # Match scenarios by ID where available, with a request-based fallback.
        def scenario_key(result):
            request_data = result.get("request") or {}

            return (
                str(result.get("endpoint") or ""),
                str(result.get("method") or "").upper(),
                json.dumps(request_data, sort_keys=True, default=str),
            )

        def final_outcome(result):
            status = str(
                result.get("final_status")
                or result.get("status")
                or ""
            ).upper()

            if status in {
                "PASS",
                "PASSED",
                "PASS_AFTER_RETRY",
                "PASS_AFTER_RETEST",
            }:
                return "PASS"

            if status in {"FAIL", "FAILED"}:
                return "FAIL"

            if status in {"SKIP", "SKIPPED"}:
                return "SKIP"

            return "UNKNOWN"

        baseline_results = {
            scenario_key(result): result
            for result in baseline["results"]
        }

        current_results = {
            scenario_key(result): result
            for result in current["results"]
        }

        common_keys = (
            set(baseline_results.keys())
            & set(current_results.keys())
        )
                      
        
        comparison_rows = []

        for key in sorted(common_keys, key=str):
            old_result = baseline_results[key]
            new_result = current_results[key]

            old_status = final_outcome(old_result)
            new_status = final_outcome(new_result)

            scenario_id = (
                old_result.get("id")
                or new_result.get("id")
                or old_result.get("scenario_id")
                or new_result.get("scenario_id")
                or "Matched by request"
            )

            scenario_name = (
                new_result.get("scenario")
                or old_result.get("scenario")
                or str(scenario_id)
            )

            if old_status == "PASS" and new_status == "FAIL":
                change = "REGRESSION"
            elif old_status == "FAIL" and new_status == "PASS":
                change = "RECOVERED"
            elif old_status == new_status:
                change = "UNCHANGED"
            else:
                change = f"{old_status} → {new_status}"

            comparison_rows.append({
                "Scenario ID": scenario_id,
                "Scenario": scenario_name,
                "Baseline": old_status,
                "Comparison": new_status,
                "Baseline Retry": (
                    "Yes"
                    if str(
                        old_result.get("final_status") or ""
                    ).upper() in {
                        "PASS_AFTER_RETRY",
                        "PASS_AFTER_RETEST",
                    }
                    else "No"
                ),
                "Comparison Retry": (
                    "Yes"
                    if str(
                        new_result.get("final_status") or ""
                    ).upper() in {
                        "PASS_AFTER_RETRY",
                        "PASS_AFTER_RETEST",
                    }
                    else "No"
                ),
                "Change": change,
            })

        st.subheader("Scenario-Level Comparison")

        if comparison_rows:
            st.table(comparison_rows)

            regression_count = sum(
                row["Change"] == "REGRESSION"
                for row in comparison_rows
            )

            if regression_count:
                st.error(
                    f"{regression_count} matched scenario(s) changed "
                    "from PASS to FAIL."
                )
            else:
                st.caption(
                    "No matched scenario changed from PASS to FAIL."
                )
        else:
            st.info(
                "No scenarios could be matched between these reports. "
                "Aggregate metrics are still available."
            )

        with st.expander("View selected comparison report details"):
            st.write("**Baseline report**")
            st.json(baseline["report"])

            st.write("**Comparison report**")
            st.json(current["report"])