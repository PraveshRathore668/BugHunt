import json

from minimizer import classify, minimize
from problems import PROBLEMS
from reports import build_report, report_to_json
from tester import run_differential, run_function


def _caller(func):
    return lambda a: run_function(func, a)


def test_minimizer_shrinks_skip_last_bug():
    p = PROBLEMS["max_element"]
    caller = _caller(p["candidates"]["bug: skips last element"])
    arr = [-7152, -6642, -5428, 7870, 9349]
    kind = classify(p["reference"], caller, arr)
    assert kind == "mismatch"
    r = minimize(p["reference"], caller, arr, kind)
    assert r["verified"]
    assert len(r["minimized"]) <= 2
    assert classify(p["reference"], caller, r["minimized"]) == "mismatch"


def test_minimizer_keeps_exception_kind():
    p = PROBLEMS["second_largest"]
    caller = _caller(p["candidates"]["bug: duplicates of max"])
    kind = classify(p["reference"], caller, [4])
    assert kind == "exception"
    r = minimize(p["reference"], caller, [4], kind)
    assert r["verified"] and r["kind"] == "exception"


def test_minimizer_respects_call_budget():
    p = PROBLEMS["max_subarray"]
    caller = _caller(p["candidates"]["bug: skips last element"])
    arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, -1, 50]
    kind = classify(p["reference"], caller, arr)
    r = minimize(p["reference"], caller, arr, kind, max_calls=3)
    assert r["calls_used"] <= 3
    assert classify(p["reference"], caller, r["minimized"]) == kind


def test_minimizer_does_not_reduce_passing_input():
    p = PROBLEMS["max_element"]
    caller = _caller(p["candidates"]["correct: built-in max"])
    assert classify(p["reference"], caller, [1, 2, 3]) is None


def test_report_is_valid_json_with_required_fields():
    p = PROBLEMS["max_element"]
    f = p["candidates"]["bug: zero init"]
    result = run_differential(p["reference"], f, 50, 7)
    result["per_test_timeout"] = 2.0
    rep = build_report("max_element", "bug: zero init", result, None, "t0")
    back = json.loads(report_to_json(rep))
    assert back["configuration"]["seed"] == 7
    assert back["summary"]["mismatches"] == result["mismatches"] > 0
    assert back["failures"][0]["expected"] is not None
    assert "does not prove correctness" in back["disclaimer"]
