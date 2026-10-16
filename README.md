# AI Autonomous UAT Platform

**Travel API testing, automated validation, execution evidence, and
release-readiness reporting.**

The AI Autonomous UAT Platform is a Python-based project for validating
travel API workflows through structured test scenarios, automated
execution, response checks, and auditable reports. It is being developed
with a focus on travel technology integrations and practical UAT
workflows.

## Project goals

-   Turn travel API requirements and scenarios into structured,
    repeatable tests.
-   Validate scenario definitions before execution.
-   Select and orchestrate relevant tests through the UAT pipeline.
-   Check API responses against expected behaviour and business rules.
-   Classify failures and retry eligible transient failures.
-   Produce run evidence, audit information, release-readiness results,
    and reports.
-   Provide a dashboard for reviewing UAT outcomes.
-   Build a persistent run history to support future comparisons and
    failure-trend analysis.

## Current capabilities

The project has implemented or exercised the following workflow
components:

-   Scenario validation and test selection.
-   UAT planning and orchestration.
-   API test execution and expectation checks.
-   Failure classification, with automatic retries for eligible
    transient failures.
-   Evidence and audit-trail generation.
-   Release-readiness assessment and UAT sign-off reporting.
-   JSON and HTML reports.
-   A dashboard foundation for viewing the latest run.
-   Basic test coverage for successful booking, missing passenger
    information, and invalid fare scenarios.

**Development status:** Phase 10B (transient-failure classification and
retry validation) is complete and frozen. Phase 11A, focused on UAT run
history, is in progress. Confirm the current local code and reports
before treating any planned history enhancements as implemented.

## Technology

-   Python
-   `pytest` for automated tests
-   JSON-based scenarios and reports
-   Streamlit for the dashboard
-   Travel API test endpoints in `app/api.py`
-   Windows PowerShell and a Python virtual environment for the current
    development setup

Check the project files for the exact dependency versions and
installation requirements.

## Project structure

The following are the key files and locations identified in the project:

``` text
ai-uat-platform/
├── app/
│   ├── api.py                  # Demo API endpoints used by tests
│   ├── scenario_pipeline.py    # Main UAT pipeline and report generation
│   ├── test_runner.py          # Test execution and response validation
│   └── uat_evidence.py         # UAT evidence and audit-trail functions
├── reports/
│   ├── latest_run.json         # Latest full pipeline report
│   ├── latest_run.html         # Latest HTML report
│   ├── latest_test_report.json # Test-runner report, if generated
│   └── run_*.json              # Timestamped reports from earlier runs
├── scenarios/
│   └── booking_tests.json      # Booking test scenarios
├── dashboard.py                # Streamlit dashboard entry point, if present
└── README.md
```

This is a guide to the main project files, not a complete inventory.
Your local folder may contain additional modules, tests, configuration
files, and reports.

## Setup on Windows

Open PowerShell and change to the project directory:

``` powershell
cd C:\Users\dilsh\ai-uat-platform
```

Activate the existing virtual environment:

``` powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation for the current terminal session, use:

``` powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

If you are setting up a fresh environment, create it with:

``` powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies using the repository's dependency file if one is
present:

``` powershell
pip install -r requirements.txt
```

If `requirements.txt` does not exist, inspect the project's
dependency/configuration files and install the listed packages rather
than guessing package versions.

## Running the UAT pipeline

From the project root, with the virtual environment active:

``` powershell
python -m app.scenario_pipeline
```

The pipeline is expected to run the configured scenario workflow and
write the latest report files under `reports/`.

### Run automated tests

``` powershell
python -m pytest -v
```

Use the test output as the source of truth for the current pass/fail
status. If tests call the local API, make sure the required API service
is running and reachable first.

### Launch the dashboard

If `dashboard.py` exists in the project root and is the current
Streamlit entry point:

``` powershell
streamlit run dashboard.py
```

Use the actual dashboard entry-point filename present in your local
project if it differs.

## API endpoints used in the demo

The project's demo API module has included these endpoints:

-   `POST /booking` --- returns a demo confirmed-booking response,
    including a PNR.
-   `GET /search` --- returns `NO_FLIGHTS` for the demo destination
    `XYZ`.

These are demonstration behaviours, not a production booking service.
Check `app/api.py` for the current request schema, response fields, and
server startup instructions.

## Reports and evidence

The pipeline's latest report files are:

-   `reports/latest_run.json` --- full structured report for the latest
    pipeline run.
-   `reports/latest_run.html` --- HTML representation of the latest
    report.

The separate test runner may also write:

-   `reports/latest_test_report.json` --- a simpler report containing
    test totals and individual results.

Timestamped `reports/run_*.json` files exist from earlier runs. Phase
11A is intended to make run history reliable and consistent for future
analysis. Verify that new runs are being archived by the current local
code before relying on the history as a complete record.

## Failure handling

The runner has been developed to distinguish transient failures (such as
server errors or connection/time-out problems) from contract,
validation, expectation, and business-rule failures. Automatic retries
are intended for eligible transient failures only; functional or
contract failures should not be treated as transient.

A local API connection error such as "connection refused" usually means
the API service is not running at the configured address or is not
reachable. Check the service and configured base URL before interpreting
that result as a defect in the test scenario.

## Development roadmap

The project roadmap is limited to 12 major phases. Current focus:

-   **Completed/frozen:** Phase 10B --- transient-failure classification
    and automatic retry validation.
-   **In progress:** Phase 11A --- UAT run history.
-   **Future direction:** use stored runs to compare results over time
    and support historical failure intelligence, trend analysis, and
    flaky-test identification.

Keep changes to frozen phases limited to verified defect fixes, and run
regression tests after modifications.

## Suggested demonstration flow

For an interview or technical walkthrough:

1.  Explain the travel API testing problem and the intended UAT
    workflow.
2.  Show the scenario definitions in `scenarios/booking_tests.json`.
3.  Run the pipeline with `python -m app.scenario_pipeline`.
4.  Walk through scenario selection, execution results, failure
    classification, and retry behaviour.
5.  Open `reports/latest_run.html` and inspect the corresponding JSON
    report.
6.  Explain how evidence and release-readiness outputs support an
    auditable UAT decision.
7.  Show the dashboard if it is available and explain the run-history
    work underway.

Use a clean, reproducible run and explain any demo-only API behaviour
clearly.

## Important notes

-   This is a development/demo project; do not connect it to production
    booking systems or real customer data without appropriate security,
    privacy, and operational controls.
-   Do not commit secrets, access tokens, credentials, or sensitive test
    data.
-   Treat report files as evidence of the specific run that generated
    them; do not assume older reports use the same schema as newer ones.
-   Update this README when the project structure, setup process,
    pipeline, or Phase 11A implementation changes.

## License

No license information has been specified here. Add a license section
once the project's intended distribution and licensing terms are
decided.
