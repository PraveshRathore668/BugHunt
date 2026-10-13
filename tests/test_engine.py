import pytest

from generators import generate_tests, is_valid_input
from problems import PROBLEMS
from tester import run_differential, run_function, outputs_match

# Deterministic inputs that MUST expose each known bug (no random luck).
KNOWN_BUG_INPUTS = {
    ("max_element", "bug: zero init"): [-5, -2, -9],
    ("max_element", "bug: skips last element"): [1, 2, 9],
    ("second_largest", "bug: duplicates of max"): [5, 5, 3],
    ("second_largest", "bug: all-equal returns value"): [7, 7],
    ("max_subarray", "bug: zero init"): [-3, -1, -2],
    ("max_subarray", "bug: skips last element"): [-1, 5],
}


def test_reference_known_values():
    p = PROBLEMS
    assert p["max_element"]["reference"]([-5, -2, -9]) == -2
    assert p["second_largest"]["reference"]([5, 5, 3]) == 3
    assert p["second_largest"]["reference"]([7, 7]) is None
    assert p["max_subarray"]["reference"]([-3, -1, -2]) == -1
    assert p["max_subarray"]["reference"]([-1, 5]) == 5


def test_generator_is_reproducible():
    assert generate_tests(200, 42) == generate_tests(200, 42)
    assert generate_tests(200, 42) != generate_tests(200, 43)


def test_generated_inputs_are_valid():
    for seed in range(20):
        for t in generate_tests(100, seed):
            assert is_valid_input(t["input"])


def test_generator_rejects_bad_count():
    with pytest.raises(ValueError):
        generate_tests(0, 1)


def test_outputs_match_checks_type():
    assert outputs_match(1, 1)
    assert not outputs_match(1, True)
    assert not outputs_match(None, 0)


def test_run_function_catches_exceptions():
    status, msg = run_function(lambda a: a[10], [1])
    assert status == "error" and "IndexError" in msg


@pytest.mark.parametrize("key", list(PROBLEMS))
def test_correct_candidates_have_no_failures(key):
    problem = PROBLEMS[key]
    for name, func in problem["candidates"].items():
        if name.startswith("correct"):
            r = run_differential(problem["reference"], func, 300, 42)
            assert r["mismatches"] == 0
            assert r["exceptions"] == 0
            assert r["reference_errors"] == 0
            assert r["matches"] == 300


@pytest.mark.parametrize("key,name", list(KNOWN_BUG_INPUTS))
def test_known_bug_is_exposed_by_fixed_input(key, name):
    problem = PROBLEMS[key]
    ref, cand = problem["reference"], problem["candidates"][name]
    arr = KNOWN_BUG_INPUTS[(key, name)]
    s1, expected = run_function(ref, arr)
    s2, actual = run_function(cand, arr)
    assert s1 == "ok"
    assert s2 == "error" or not outputs_match(expected, actual)


@pytest.mark.parametrize("key,name", list(KNOWN_BUG_INPUTS))
def test_known_bug_is_found_in_a_10_test_run(key, name):
    problem = PROBLEMS[key]
    r = run_differential(problem["reference"], problem["candidates"][name], 10, 1)
    assert r["mismatches"] + r["exceptions"] > 0


def test_same_seed_gives_same_result():
    p = PROBLEMS["max_subarray"]
    f = p["candidates"]["bug: skips last element"]
    a = run_differential(p["reference"], f, 100, 5)
    b = run_differential(p["reference"], f, 100, 5)
    a.pop("elapsed_seconds"); b.pop("elapsed_seconds")
    assert a == b
