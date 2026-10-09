from app.uat_evidence import (
    build_evidence_record,
    build_evidence_records,
    build_audit_trail,
)


def test_uat_evidence():

    scenarios = [
        {
            "id": "AI-UAT-001",
            "category": "BOOKING",
            "priority": "Critical",
            "scenario": "Successful booking",
            "method": "POST",
            "endpoint": "/booking",
            "request": {
                "passenger_name": "John Doe",
                "fare": "ECONOMY"
            },
            "expected": {
                "success": True,
                "booking_status": "CONFIRMED"
            }
        },
        {
            "id": "AI-UAT-002",
            "category": "BOOKING",
            "priority": "High",
            "scenario": "Booking with baggage",
            "method": "POST",
            "endpoint": "/booking",
            "request": {
                "passenger_name": "Jane Doe",
                "fare": "ECONOMY",
                "baggage": "20KG"
            },
            "expected": {
                "success": True,
                "booking_status": "CONFIRMED"
            }
        },
        {
            "id": "AI-UAT-003",
            "category": "BOOKING",
            "priority": "High",
            "scenario": "Transient booking failure",
            "method": "POST",
            "endpoint": "/booking",
            "request": {
                "passenger_name": "Test User",
                "fare": "ECONOMY"
            },
            "expected": {
                "success": True,
                "booking_status": "CONFIRMED"
            }
        }
    ]

    execution_results = [
        {
            "status": "PASS",
            "attempt": 1,
            "status_code": 200,
            "endpoint": "/booking",
            "method": "POST",
            "request": {
                "passenger_name": "John Doe",
                "fare": "ECONOMY"
            },
            "expected": {
                "success": True,
                "booking_status": "CONFIRMED"
            },
            "actual": {
                "success": True,
                "booking_status": "CONFIRMED"
            },
            "execution_time_seconds": 0.25
        },
        {
            "status": "PASS",
            "attempt": 1,
            "status_code": 200,
            "endpoint": "/booking",
            "method": "POST",
            "request": {
                "passenger_name": "Jane Doe",
                "fare": "ECONOMY",
                "baggage": "20KG"
            },
            "expected": {
                "success": True,
                "booking_status": "CONFIRMED"
            },
            "actual": {
                "success": True,
                "booking_status": "CONFIRMED"
            },
            "execution_time_seconds": 0.31
        },
        {
            "status": "FAIL",
            "final_status": "PASS_AFTER_RETRY",
            "attempt": 2,
            "status_code": 200,
            "endpoint": "/booking",
            "method": "POST",
            "request": {
                "passenger_name": "Test User",
                "fare": "ECONOMY"
            },
            "expected": {
                "success": True,
                "booking_status": "CONFIRMED"
            },
            "actual": {
                "success": True,
                "booking_status": "CONFIRMED"
            },
            "execution_time_seconds": 0.42,
            "failure_classification": {
                "type": "TRANSIENT",
                "subtype": "SERVER_ERROR"
            },
            "retry": {
                "performed": True,
                "reason": "Transient failure automatically retried."
            },
            "retry_assessment": {
                "type": "Transient Failure",
                "confidence": "High"
            }
        }
    ]

    # --------------------------------------------------------
    # TEST 1 — SINGLE EVIDENCE RECORD
    # --------------------------------------------------------

    evidence = build_evidence_record(
        scenarios[0],
        execution_results[0],
        "EVID-0001"
    )

    assert evidence["evidence_id"] == "EVID-0001"
    assert evidence["test_id"] == "AI-UAT-001"
    assert evidence["scenario"] == "Successful booking"
    assert evidence["method"] == "POST"
    assert evidence["endpoint"] == "/booking"
    assert evidence["status_code"] == 200
    assert evidence["initial_status"] == "PASS"
    assert evidence["final_status"] == "PASS"

    print(
        "PASS | Single evidence record"
    )

    # --------------------------------------------------------
    # TEST 2 — MULTIPLE EVIDENCE RECORDS
    # --------------------------------------------------------

    records = build_evidence_records(
        scenarios,
        execution_results
    )

    assert len(records) == 3
    assert records[0]["evidence_id"] == "EVID-0001"
    assert records[1]["evidence_id"] == "EVID-0002"
    assert records[2]["evidence_id"] == "EVID-0003"

    print(
        "PASS | Multiple evidence records"
    )

    # --------------------------------------------------------
    # TEST 3 — RETRY EVIDENCE PRESERVED
    # --------------------------------------------------------

    retry_evidence = records[2]

    assert (
        retry_evidence["final_status"]
        == "PASS_AFTER_RETRY"
    )

    assert (
        retry_evidence["failure_classification"]["type"]
        == "TRANSIENT"
    )

    assert (
        retry_evidence["retry"]["performed"]
        is True
    )

    print(
        "PASS | Retry evidence preserved"
    )

    # --------------------------------------------------------
    # TEST 4 — AUDIT TRAIL
    # --------------------------------------------------------

    audit_trail = build_audit_trail(
        scenarios,
        execution_results,
        run_id="UAT-TEST-001"
    )

    assert (
        audit_trail["run_id"]
        == "UAT-TEST-001"
    )

    assert (
        audit_trail["total_evidence_records"]
        == 3
    )

    assert audit_trail["passed"] == 3
    assert audit_trail["failed"] == 0
    assert audit_trail["skipped"] == 0
    assert audit_trail["pass_after_retry"] == 1

    print(
        "PASS | Audit trail generated"
    )

    # --------------------------------------------------------
    # TEST 5 — EVIDENCE DOES NOT CHANGE OUTCOME
    # --------------------------------------------------------

    assert (
        execution_results[0]["status"]
        == "PASS"
    )

    assert (
        execution_results[2]["final_status"]
        == "PASS_AFTER_RETRY"
    )

    print(
        "PASS | Deterministic outcomes preserved"
    )

    print()
    print(
        "PHASE 9A — UAT EVIDENCE"
    )
    print(
        "Evidence records : "
        f"{audit_trail['total_evidence_records']}"
    )
    print(
        "Passed           : "
        f"{audit_trail['passed']}"
    )
    print(
        "Failed           : "
        f"{audit_trail['failed']}"
    )
    print(
        "Pass after retry : "
        f"{audit_trail['pass_after_retry']}"
    )
    print(
        "STATUS           : PASS"
    )


if __name__ == "__main__":
    test_uat_evidence()