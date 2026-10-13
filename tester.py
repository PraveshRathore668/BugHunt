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


def run_differential(reference, candidate, count, seed, max_recorded=20,
                     progress=None, candidate_caller=None,
                     max_seconds=None, stop_after_timeouts=None):
    """Compare a candidate against the reference on `count` seeded tests.

    candidate_caller: optional function arr -> (status, value) used instead of
        calling `candidate` directly (this is how isolated runs plug in).
        Status may be "ok", "error" or "timeout".
    max_seconds / stop_after_timeouts: budgets that end the run early.
    """
    if candidate_caller is None:
        def candidate_caller(arr):
            return run_function(candidate, arr)

    tests = generate_tests(count, seed)
    result = {
        "seed": seed,
        "requested_tests": count,
        "executed": 0,
        "matches": 0,
        "mismatches": 0,
        "exceptions": 0,
        "timeouts": 0,
        "reference_errors": 0,
        "failures": [],
        "failures_not_recorded": 0,
        "stopped_early": None,
        "elapsed_seconds": 0.0,
    }

    start = time.perf_counter()
    for test in tests:
        if stop_after_timeouts and result["timeouts"] >= stop_after_timeouts:
            result["stopped_early"] = f"stopped after {result['timeouts']} timeouts"
            break
        if max_seconds and time.perf_counter() - start > max_seconds:
            result["stopped_early"] = f"time budget of {max_seconds} s reached"
            break

        arr = test["input"]
        result["executed"] += 1
        if progress is not None:
            progress(result["executed"], count)

        ref_status, expected = run_function(reference, arr)
        if ref_status == "error":
            # Our trusted reference crashed: a bug in the test setup, not the candidate.
            result["reference_errors"] += 1
            status, actual = "reference_error", None
        else:
            cand_status, actual = candidate_caller(arr)
            if cand_status == "timeout":
                result["timeouts"] += 1
                status = "timeout"
            elif cand_status == "error":
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


def run_isolated(problem_key, candidate_name, count, seed, timeout=2.0,
                 max_seconds=30, stop_after_timeouts=5, **kwargs):
    """Like run_differential, but the candidate runs in a separate worker
    process with a per-test timeout."""
    from problems import PROBLEMS
    from sandbox import CandidateRunner

    reference = PROBLEMS[problem_key]["reference"]
    with CandidateRunner(problem_key, candidate_name, timeout) as runner:
        result = run_differential(
            reference, None, count, seed,
            candidate_caller=runner.call,
            max_seconds=max_seconds,
            stop_after_timeouts=stop_after_timeouts,
            **kwargs,
        )
    result["per_test_timeout"] = timeout
    return result
