"""minimizer.py - shrink a failing input to a smaller input that still fails.

The result is a REDUCED counterexample, not necessarily the globally smallest.
"""

import time

from generators import is_valid_input
from tester import outputs_match, run_function


def classify(reference, candidate_caller, arr):
    """Return the failure kind for arr: "mismatch", "exception", "timeout",
    or None if the candidate agrees with the reference."""
    ref_status, expected = run_function(reference, arr)
    if ref_status == "error":
        return None  # reference crashed: not a valid counterexample
    status, actual = candidate_caller(arr)
    if status == "timeout":
        return "timeout"
    if status == "error":
        return "exception"
    return None if outputs_match(expected, actual) else "mismatch"


def minimize(reference, candidate_caller, arr, kind, max_calls=300, max_seconds=10.0):
    """Reduce `arr` while it keeps failing with the same `kind`.

    Returns a dict: original, minimized, kind, verified, calls_used, note.
    Falls back to the original input if reduction or verification fails.
    """
    start = time.perf_counter()
    calls = 0

    def out_of_budget():
        return calls >= max_calls or time.perf_counter() - start > max_seconds

    def still_fails(candidate_input):
        nonlocal calls
        if out_of_budget() or not is_valid_input(candidate_input):
            return False
        calls += 1
        return classify(reference, candidate_caller, candidate_input) == kind

    current = list(arr)

    # Phase 1: remove chunks (halves, then smaller pieces, down to single elements).
    chunk = max(len(current) // 2, 1)
    while len(current) > 1:
        i, removed_any = 0, False
        while i < len(current):
            trial = current[:i] + current[i + chunk:]
            if trial and still_fails(trial):
                current, removed_any = trial, True   # keep it; retry same position
            else:
                i += chunk
        if chunk == 1 and not removed_any:
            break
        if out_of_budget():
            break
        chunk = max(chunk // 2, 1)

    # Phase 2: simplify values toward 0.
    for i in range(len(current)):
        for replacement in (0, current[i] // 2):
            if replacement != current[i]:
                trial = current[:i] + [replacement] + current[i + 1:]
                if still_fails(trial):
                    current = trial
                    break

    # Re-verify the final input against both implementations.
    if classify(reference, candidate_caller, current) != kind:
        return {"original": list(arr), "minimized": list(arr), "kind": kind,
                "verified": False, "calls_used": calls,
                "note": "minimization could not be verified; original kept"}

    note = "reduction stopped at budget limit" if out_of_budget() else "no further reduction found"
    return {"original": list(arr), "minimized": current, "kind": kind,
            "verified": True, "calls_used": calls, "note": note}
