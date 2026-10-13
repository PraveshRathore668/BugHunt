"""reports.py - build the downloadable JSON report. No secrets, no personal data."""

import json
from datetime import datetime, timezone

DISCLAIMER = ("Passing generated tests does not prove correctness. "
              "A minimized input is a reduced counterexample, not necessarily the smallest possible.")


def build_report(problem_key, candidate_name, result, minimized=None, started_at=None):
    """Return a JSON-serialisable dict describing one run."""
    return {
        "tool": "BugHunt",
        "problem": problem_key,
        "candidate": candidate_name,
        "configuration": {
            "requested_tests": result["requested_tests"],
            "seed": result["seed"],
            "per_test_timeout_seconds": result.get("per_test_timeout"),
        },
        "started_at_utc": started_at,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "summary": {
            "tests_executed": result["executed"],
            "matches": result["matches"],
            "mismatches": result["mismatches"],
            "exceptions": result["exceptions"],
            "timeouts": result["timeouts"],
            "reference_errors": result["reference_errors"],
            "stopped_early": result["stopped_early"],
            "elapsed_seconds": result["elapsed_seconds"],
        },
        "failures": result["failures"],
        "failures_not_recorded": result["failures_not_recorded"],
        "minimized_counterexample": minimized,
        "disclaimer": DISCLAIMER,
    }


def report_to_json(report):
    return json.dumps(report, indent=2, default=str)
