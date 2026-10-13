"""tester.py - differential testing engine.

Runs a trusted reference and a candidate on the same generated inputs
and records every disagreement. Passing tests never proves correctness.
"""

import copy
import time

from generators import generate_tests


def run_function(func, arr):
    """Run func on a COPY of arr (so it cannot change the original).

    Returns ("ok", value) or ("error", "ExceptionType: message").
    """
    try:
        return "ok", func(copy.deepcopy(arr))
    except Exception as exc:
        return "error", f"{type(exc).__name__}: {exc}"


def outputs_match(expected, actual):
    """Same output contract for every problem: equal value AND equal type."""
    return type(expected) is type(actual) and expected == actual


def run_differential(reference, candidate, count, seed, max_recorded=20):
    """Compare candidate against reference on `count` seeded tests.

    Returns a dict with exact counts plus up to `max_recorded` detailed
    failure records. Calling it again with the same arguments gives the
    same tests and the same results.
    """
    tests = generate_tests(count, seed)
    result = {
        "seed": seed,
        "requested_tests": count,
        "executed": 0,
        "matches": 0,
        "mismatches": 0,
        "exceptions": 0,
        "timeouts": 0,            # real timeout handling arrives on Day 3
        "reference_errors": 0,
        "failures": [],
        "failures_not_recorded": 0,
        "elapsed_seconds": 0.0,
    }

    start = time.perf_counter()
    for test in tests:
        arr = test["input"]
        result["executed"] += 1

        ref_status, expected = run_function(reference, arr)
        if ref_status == "error":
            # Our trusted reference crashed: a bug in the test setup, not the candidate.
            result["reference_errors"] += 1
            status, actual = "reference_error", None
        else:
            cand_status, actual = run_function(candidate, arr)
            if cand_status == "error":
                result["exceptions"] += 1
                status = "exception"
            elif outputs_match(expected, actual):
                result["matches"] += 1
                continue
            else:
                result["mismatches"] += 1
                status = "mismatch"

        if len(result["failures"]) < max_recorded:
            result["failures"].append({
                "status": status,
                "test_index": test["index"],
                "category": test["category"],
                "label": test["label"],
                "seed": seed,
                "input": arr,
                "expected": expected,
                "actual": actual,
            })
        else:
            result["failures_not_recorded"] += 1

    result["elapsed_seconds"] = round(time.perf_counter() - start, 4)
    return result
