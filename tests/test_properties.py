from hypothesis import given, settings, strategies as st

from generators import generate_tests, is_valid_input
from minimizer import classify, minimize
from problems import PROBLEMS
from tester import run_differential, run_function

valid_arrays = st.lists(st.integers(-10000, 10000), min_size=1, max_size=60)


@given(valid_arrays)
def test_max_element_reference_matches_builtin(arr):
    assert PROBLEMS["max_element"]["reference"](arr) == max(arr)


@given(valid_arrays)
def test_max_subarray_reference_matches_bruteforce(arr):
    expected = max(sum(arr[i:j]) for i in range(len(arr)) for j in range(i + 1, len(arr) + 1))
    assert PROBLEMS["max_subarray"]["reference"](arr) == expected


@given(valid_arrays)
def test_second_largest_reference_matches_definition(arr):
    distinct = sorted(set(arr), reverse=True)
    expected = distinct[1] if len(distinct) > 1 else None
    assert PROBLEMS["second_largest"]["reference"](arr) == expected


@given(valid_arrays)
def test_correct_candidates_agree_with_references(arr):
    for p in PROBLEMS.values():
        ref = p["reference"]
        for name, f in p["candidates"].items():
            if name.startswith("correct"):
                assert f(list(arr)) == ref(list(arr))


@given(st.integers(1, 300), st.integers(0, 10**6))
@settings(deadline=None)
def test_generator_is_deterministic_and_valid(count, seed):
    a = generate_tests(count, seed)
    assert a == generate_tests(count, seed)
    assert len(a) == count
    assert all(is_valid_input(t["input"]) for t in a)


@given(valid_arrays)
@settings(deadline=None)
def test_minimized_input_is_valid_and_still_fails(arr):
    p = PROBLEMS["max_subarray"]
    caller = lambda a: run_function(p["candidates"]["bug: zero init"], a)
    kind = classify(p["reference"], caller, arr)
    if kind:
        r = minimize(p["reference"], caller, arr, kind)
        assert r["verified"]
        assert is_valid_input(r["minimized"])
        assert len(r["minimized"]) <= len(arr)
        assert classify(p["reference"], caller, r["minimized"]) == kind


@given(st.integers(0, 10**6))
@settings(deadline=None, max_examples=30)
def test_run_counts_add_up(seed):
    p = PROBLEMS["second_largest"]
    r = run_differential(p["reference"], p["candidates"]["bug: duplicates of max"], 50, seed)
    assert r["matches"] + r["mismatches"] + r["exceptions"] + r["timeouts"] + r["reference_errors"] == r["executed"]
