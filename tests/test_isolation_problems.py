import pytest

from generators import is_valid_input
from problems import PROBLEMS
from tester import run_isolated

REQUIRED = ["statement", "signature", "input_spec", "output_spec", "constraints",
            "samples", "algorithm", "time_complexity", "space_complexity", "reference"]


def test_isolated_matches_in_process_counts():
    r = run_isolated("max_element", "bug: zero init", 100, 42)
    assert (r["matches"], r["mismatches"]) == (82, 18)


def test_timeout_is_detected_and_run_stops_early():
    r = run_isolated("max_element", "bug: hangs on all-equal input",
                     100, 42, timeout=0.5, stop_after_timeouts=2)
    assert r["timeouts"] == 2
    assert r["stopped_early"]


def test_exceptions_counted_separately():
    r = run_isolated("second_largest", "bug: duplicates of max", 100, 42)
    assert r["exceptions"] > 0 and r["mismatches"] > 0


@pytest.mark.parametrize("key", list(PROBLEMS))
def test_problem_definition_is_complete(key):
    for field in REQUIRED:
        assert PROBLEMS[key].get(field), f"{key} missing {field}"


@pytest.mark.parametrize("key", list(PROBLEMS))
def test_samples_are_valid_and_match_reference(key):
    p = PROBLEMS[key]
    for s in p["samples"]:
        assert is_valid_input(s["input"])
        out = p["reference"](list(s["input"]))
        assert out == s["output"] and type(out) is type(s["output"])


def test_every_problem_has_a_buggy_candidate():
    for key, p in PROBLEMS.items():
        assert any(n.startswith("bug") for n in p["candidates"]), key
