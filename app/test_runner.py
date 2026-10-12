import json
import time
from datetime import datetime
from pathlib import Path

import httpx

from app.ai_diagnostic import diagnose_failure


API_BASE_URL = "http://127.0.0.1:8000"
REPORTS_PATH = Path("reports")


def execute_request(scenario):
    """
    Execute the HTTP request defined by a UAT scenario.

    TEMPORARY TEST:
    The configured scenario receives one simulated HTTP 503.
    The subsequent retry executes the real API request.
    """

    method = scenario.get(
        "method",
        "GET"
    ).upper()

    endpoint = scenario.get(
        "endpoint",
        ""
    )

    request_data = scenario.get(
        "request",
        {}
    )


  
    # ========================================================
    # REAL API REQUEST
    # ========================================================

    url = f"{API_BASE_URL}{endpoint}"

    start_time = time.perf_counter()

    try:

        with httpx.Client(
            timeout=10.0
        ) as client:

            if method == "GET":

                response = client.get(
                    url,
                    params=request_data
                )

            elif method == "POST":

                response = client.post(
                    url,
                    json=request_data
                )

            elif method == "PUT":

                response = client.put(
                    url,
                    json=request_data
                )

            elif method == "DELETE":

                response = client.delete(
                    url,
                    json=request_data
                )

            else:

                raise ValueError(
                    f"Unsupported HTTP method: {method}"
                )

        execution_time = round(
            time.perf_counter() - start_time,
            2
        )

        # ====================================================
        # PARSE RESPONSE
        # ====================================================

        try:

            response_data = response.json()

        except ValueError:

            response_data = {
                "raw_response": response.text
            }

        return {
            "status_code": response.status_code,

            "data": response_data,

            "execution_time_seconds": execution_time
        }

    except Exception as exc:

        execution_time = round(
            time.perf_counter() - start_time,
            2
        )

        return {
            "status_code": None,

            "data": {},

            "execution_time_seconds": execution_time,

            "error": str(exc),

            "error_type": type(exc).__name__
        }


# ============================================================
# EXPECTED FIELD VALIDATION
# ============================================================

def validate_expected_field(
    actual,
    field,
    expected_value
):
    """
    Validate one expected response field.

    Supports semantic expectations such as:

    - non-empty array
    - array
    - present
    """

    if field not in actual:
        return False

    actual_value = actual[field]

    # --------------------------------------------------------
    # NON-EMPTY ARRAY
    # --------------------------------------------------------

    if expected_value == "non-empty array":

        return (
            isinstance(
                actual_value,
                list
            )
            and len(actual_value) > 0
        )

    # --------------------------------------------------------
    # ARRAY
    # --------------------------------------------------------

    if expected_value == "array":

        return isinstance(
            actual_value,
            list
        )

    # --------------------------------------------------------
    # PRESENT
    # --------------------------------------------------------

    if expected_value == "present":

        return (
            actual_value is not None
            and actual_value != ""
        )

    # --------------------------------------------------------
    # EXACT VALUE
    # --------------------------------------------------------

    return actual_value == expected_value


# ============================================================
# SCENARIO VALIDATION
# ============================================================

def validate_scenario(
    scenario,
    response
):
    """
    Validate the actual API response against
    the deterministic scenario expectations.
    """

    expected = scenario.get(
        "expected",
        {}
    )

    status_code = response.get(
        "status_code"
    )

    actual = response.get(
        "data",
        {}
    )

    # --------------------------------------------------------
    # REQUEST / CONNECTION ERROR
    # --------------------------------------------------------

    if response.get("error"):

        return {
            "status": "FAIL",
            "failure": {
                "type": "REQUEST_ERROR",
                "error": response.get(
                    "error"
                ),
                "error_type": response.get(
                    "error_type"
                )
            }
        }

    # --------------------------------------------------------
    # HTTP STATUS CODE
    # --------------------------------------------------------

    expected_status_code = expected.get(
        "http_status",
        expected.get("status_code", 200)
    )

    if status_code != expected_status_code:

        return {
            "status": "FAIL",
            "failure": {
                "field": "status_code",
                "expected": expected_status_code,
                "actual": status_code
            }
        }

    # --------------------------------------------------------
    # RESPONSE FIELD VALIDATION
    # --------------------------------------------------------

    for field, expected_value in expected.items():

        if field in ("http_status", "status_code"):
            continue

        if not validate_expected_field(
            actual,
            field,
            expected_value
        ):

            return {
                "status": "FAIL",
                "failure": {
                    "field": field,
                    "expected": expected_value,
                    "actual": actual.get(
                        field
                    )
                }
            }

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    return {
        "status": "PASS"
    }


# ============================================================
# FAILURE CLASSIFICATION
# ============================================================

def classify_failure(result):
    """
    Classify a UAT failure into a high-level failure category
    and a more specific subtype.
    """

    if not result:

        return {
            "type": "UNKNOWN",
            "subtype": "UNKNOWN"
        }

    actual = result.get(
        "actual"
    ) or {}

    failure = result.get(
        "failure"
    ) or {}

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # HTTP status_code is stored directly in the result.
    # This allows 5xx responses to be correctly classified.
    # --------------------------------------------------------

    status_code = result.get(
        "status_code"
    )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if status_code is None:

        status_code = failure.get(
            "actual"
        )

    error_type = str(
        result.get(
            "error_type",
            ""
        )
    ).lower()

    failure_text = str(
        failure
    ).lower()

    # --------------------------------------------------------
    # TRANSIENT:
    # TIMEOUT / CONNECTION
    # --------------------------------------------------------

    if (
        "timeout" in error_type
        or "timeout" in failure_text
        or "connection" in error_type
        or "connection" in failure_text
    ):

        return {
            "type": "TRANSIENT",
            "subtype": "TIMEOUT_OR_CONNECTION"
        }

    # --------------------------------------------------------
    # TRANSIENT:
    # SERVER ERROR
    # --------------------------------------------------------

    if status_code in [
        500,
        502,
        503,
        504
    ]:

        return {
            "type": "TRANSIENT",
            "subtype": "SERVER_ERROR"
        }

    # --------------------------------------------------------
    # AUTHENTICATION / AUTHORIZATION
    # --------------------------------------------------------

    if status_code in [
        401,
        403
    ]:

        return {
            "type": "AUTHENTICATION",
            "subtype": "AUTHORIZATION_FAILURE"
        }

    # --------------------------------------------------------
    # CONTRACT FAILURE
    # --------------------------------------------------------

    contract_keywords = [
        "missing field",
        "missing required field",
        "schema",
        "type mismatch",
        "invalid type",
        "unexpected field",
        "response structure"
    ]

    if any(
        keyword in failure_text
        for keyword in contract_keywords
    ):

        return {
            "type": "CONTRACT",
            "subtype": "RESPONSE_CONTRACT"
        }

    # --------------------------------------------------------
    # EXPECTATION MISMATCH
    # --------------------------------------------------------

    if (
        failure.get("field")
        and "expected" in failure
        and "actual" in failure
    ):

        return {
            "type": "VALIDATION",
            "subtype": "EXPECTATION_MISMATCH"
        }

    # --------------------------------------------------------
    # FUNCTIONAL FAILURE
    # --------------------------------------------------------

    if (
        status_code == 200
        and failure
    ):

        return {
            "type": "FUNCTIONAL",
            "subtype": "BUSINESS_RULE_FAILURE"
        }

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    return {
        "type": "UNKNOWN",
        "subtype": "UNCLASSIFIED"
    }


# ============================================================
# RUN ONE SCENARIO
# ============================================================

def run_scenario(scenario):
    """
    Execute and deterministically validate one scenario.
    """

    response = execute_request(
        scenario
    )

    validation = validate_scenario(
        scenario,
        response
    )

    # --------------------------------------------------------
    # BASE RESULT
    # --------------------------------------------------------

    result = {
        "status": validation["status"],
        "attempt": 1,

        # IMPORTANT:
        # Store HTTP status code directly in the result.
        "status_code": response.get(
            "status_code"
        ),

        "endpoint": scenario.get(
            "endpoint"
        ),

        "method": scenario.get(
            "method"
        ),

        "request": scenario.get(
            "request",
            {}
        ),

        "expected": scenario.get(
            "expected",
            {}
        ),

        "actual": response.get(
            "data",
            {}
        ),

        "execution_time_seconds": response.get(
            "execution_time_seconds",
            0
        )
    }

    # --------------------------------------------------------
    # FAILURE PROCESSING
    # --------------------------------------------------------

    if validation["status"] == "FAIL":

        result["failure"] = validation.get(
            "failure"
        )

        if response.get(
            "error_type"
        ):

            result["error_type"] = response.get(
                "error_type"
            )

        # ----------------------------------------------------
        # AI DIAGNOSTIC INPUT
        # ----------------------------------------------------

        diagnosis_input = {
            "endpoint": scenario.get(
                "endpoint"
            ),

            "method": scenario.get(
                "method"
            ),

            "request": scenario.get(
                "request",
                {}
            ),

            "expected": scenario.get(
                "expected",
                {}
            ),

            "actual": response.get(
                "data",
                {}
            ),

            "failure": validation.get(
                "failure"
            )
        }

        # ----------------------------------------------------
        # AI DIAGNOSIS
        # ----------------------------------------------------

        try:

            result["ai_diagnosis"] = diagnose_failure(
                diagnosis_input
            )

        except Exception as exc:

            result["ai_diagnosis"] = {
                "root_cause": (
                    "AI diagnosis could not be completed."
                ),

                "impact": (
                    "The deterministic UAT failure "
                    "remains valid."
                ),

                "recommendation": (
                    "Investigate the deterministic "
                    "failure details."
                ),

                "confidence": "Low",

                "evidence": str(
                    exc
                )
            }

        # ----------------------------------------------------
        # FAILURE CLASSIFICATION
        # ----------------------------------------------------

        result["failure_classification"] = classify_failure(
            result
        )

    return result


# ============================================================
# RETEST SCENARIO
# ============================================================

def retest_scenario(scenario):
    """
    Execute the scenario again after an initial failure.
    """

    response = execute_request(
        scenario
    )

    validation = validate_scenario(
        scenario,
        response
    )

    result = {
        "status": validation["status"],

        "status_code": response.get(
            "status_code"
        ),

        "actual": response.get(
            "data",
            {}
        ),

        "execution_time_seconds": response.get(
            "execution_time_seconds",
            0
        )
    }

    # --------------------------------------------------------
    # RETEST FAILURE
    # --------------------------------------------------------

    if validation["status"] == "FAIL":

        result["failure"] = validation.get(
            "failure"
        )

        if response.get(
            "error_type"
        ):

            result["error_type"] = response.get(
                "error_type"
            )

    return result


# ============================================================
# BUILD FINAL RESULT
# ============================================================

def build_result(
    scenario,
    initial_result,
    retest_result
):
    """
    Combine the initial attempt and automatic retry
    into one final UAT result.
    """

    result = initial_result.copy()

    # --------------------------------------------------------
    # RETRY INFORMATION
    # --------------------------------------------------------

    result["retry"] = {
        "performed": True,

        "status": retest_result.get(
            "status"
        ),

        "status_code": retest_result.get(
            "status_code"
        ),

        "actual": retest_result.get(
            "actual"
        ),

        "failure": retest_result.get(
            "failure"
        ),

        "execution_time_seconds": retest_result.get(
            "execution_time_seconds",
            0
        )
    }

    # --------------------------------------------------------
    # RETRY PASSED
    # --------------------------------------------------------

    if initial_result["status"] == "FAIL":

        if retest_result["status"] == "PASS":

            result["retry_assessment"] = {
                "type": (
                    "Transient / Intermittent Failure"
                ),

                "confidence": "Medium",

                "description": (
                    "The scenario failed on the "
                    "initial attempt but passed "
                    "during automatic re-test."
                )
            }

            result["final_status"] = (
                "PASS_AFTER_RETRY"
            )

        # ----------------------------------------------------
        # RETRY ALSO FAILED
        # ----------------------------------------------------

        elif retest_result["status"] == "FAIL":

            result["retry_assessment"] = {
                "type": (
                    "Persistent Functional Failure"
                ),

                "confidence": "High",

                "description": (
                    "The scenario failed on both "
                    "the initial attempt and "
                    "automatic re-test."
                )
            }

            result["final_status"] = "FAIL"

        # ----------------------------------------------------
        # RETRY EXECUTION ERROR
        # ----------------------------------------------------

        else:

            result["retry_assessment"] = {
                "type": "Retry Execution Error",

                "confidence": "High",

                "description": (
                    "The initial scenario failed "
                    "and the automatic re-test "
                    "could not be completed "
                    "successfully."
                )
            }

            result["final_status"] = "ERROR"

    # --------------------------------------------------------
    # NO RETRY REQUIRED
    # --------------------------------------------------------

    else:

        result["retry"] = {
            "performed": False
        }

        result["final_status"] = (
            initial_result["status"]
        )

    return result


# ============================================================
# RUN ALL SCENARIOS
# ============================================================

def run_all_scenarios(scenarios):
    """
    Execute all scenarios.

    Failed scenarios are classified before deciding
    whether an automatic re-test is appropriate.
    """

    results = []

    for scenario in scenarios:

        initial_result = run_scenario(
            scenario
        )

        print(
            "DEBUG:",
            scenario.get("id"),
            "status=",
            initial_result.get("status"),
            "status_code=",
            initial_result.get("status_code"),
            "failure=",
            initial_result.get("failure"),
            "classification=",
            initial_result.get("failure_classification")
        )

        # ----------------------------------------------------
        # FAILED SCENARIO
        # ----------------------------------------------------

        if initial_result["status"] == "FAIL":

            classification = initial_result.get(
                "failure_classification",
                {}
            )

            failure_type = classification.get(
                "type",
                "UNKNOWN"
            )

            failure_subtype = classification.get(
                "subtype",
                "UNKNOWN"
            )

            # ------------------------------------------------
            # ONLY TRANSIENT FAILURES ARE RETRIED
            # ------------------------------------------------

            retry_allowed = (
                failure_type == "TRANSIENT"
            )

            if retry_allowed:

                retest_result = retest_scenario(
                    scenario
                )

                result = build_result(
                    scenario,
                    initial_result,
                    retest_result
                )

            # ------------------------------------------------
            # DETERMINISTIC FAILURE
            # ------------------------------------------------

            else:

                result = initial_result.copy()

                result["retry"] = {
                    "performed": False,

                    "reason": (
                        "Automatic retry not performed "
                        "because the failure was "
                        "classified as "
                        f"{failure_type}/"
                        f"{failure_subtype}."
                    )
                }

                result["retry_assessment"] = {
                    "type": (
                        "Deterministic Failure - "
                        "Retry Not Required"
                    ),

                    "confidence": "High",

                    "description": (
                        "The failure classification "
                        "indicates that repeating "
                        "the request is unlikely to "
                        "provide additional "
                        "diagnostic value."
                    )
                }

                result["final_status"] = "FAIL"

        # ----------------------------------------------------
        # SCENARIO PASSED ON FIRST ATTEMPT
        # ----------------------------------------------------

        else:

            result = initial_result

        results.append(
            result
        )

    return results


# ============================================================
# LEGACY REPORT FUNCTION
# ============================================================

def save_report(results):
    """
    Legacy JSON report function.

    The main pipeline currently owns the primary
    reporting process. This function is retained
    for compatibility.
    """

    REPORTS_PATH.mkdir(
        exist_ok=True
    )

    total = len(results)

    passed = sum(
        1
        for result in results
        if result["status"] == "PASS"
    )

    failed = sum(
        1
        for result in results
        if result["status"] == "FAIL"
    )

    success_rate = (
        round(
            (passed / total) * 100,
            2
        )
        if total
        else 0
    )

    report = {
        "run_timestamp": datetime.now().isoformat(),

        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": success_rate
        },

        "results": results
    }

    report_path = (
        REPORTS_PATH /
        "latest_test_report.json"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2
        )

    return report_path

