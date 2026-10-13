import pytest

from generators import is_valid_input
from problems import PROBLEMS
from quality import find_duplicates, validate_all, validate_problem
from tester import run_isolated


def test_builtin_problems_have_no_issues():
    assert validate_all(PROBLEMS) == []


@pytest.mark.parametrize("bad", [
    [], None, "abc", [10001], [-10001], [True], [1.5], [1, "2"], [0] * 1001,
])
def test_is_valid_input_rejects_invalid(bad):
    assert not is_valid_input(bad)


@pytest.mark.parametrize("good", [[0], [-10000, 10000], [5] * 1000])
def test_is_valid_input_accepts_valid(good):
    assert is_valid_input(good)


def test_correct_candidate_passes_isolated_path():
    r = run_isolated("max_element", "correct: built-in max", 100, 42)
    assert r["matches"] == 100
    assert r["mismatches"] == r["exceptions"] == r["timeouts"] == 0


@pytest.mark.parametrize("field", [
    "statement", "constraints", "input_spec", "output_spec", "algorithm",
])
def test_missing_field_is_reported(field):
    broken = dict(PROBLEMS["max_element"])
    broken[field] = ""
    checks = [i["check"] for i in validate_problem("max_element", broken)]
    assert f"missing_{field}" in checks


def test_missing_reference_is_reported():
    broken = dict(PROBLEMS["max_element"])
    broken["reference"] = None
    checks = [i["check"] for i in validate_problem("max_element", broken)]
    assert "missing_reference" in checks


def test_wrong_sample_output_is_reported():
    broken = dict(PROBLEMS["max_element"])
    broken["samples"] = [{"input": [1, 2, 3], "output": 99, "explanation": "wrong"}]
    checks = [i["check"] for i in validate_problem("max_element", broken)]
    assert "inconsistent_sample" in checks


def test_invalid_sample_input_is_reported():
    broken = dict(PROBLEMS["max_element"])
    broken["samples"] = [{"input": [], "output": 1, "explanation": "empty"}]
    checks = [i["check"] for i in validate_problem("max_element", broken)]
    assert "invalid_sample_input" in checks


def test_all_issues_are_marked_deterministic():
    broken = dict(PROBLEMS["max_element"])
    broken["statement"] = ""
    assert all(i["source"] == "deterministic"
               for i in validate_problem("max_element", broken))


def test_duplicate_questions_are_detected():
    copy_of = dict(PROBLEMS["max_element"])
    probs = {"a": PROBLEMS["max_element"], "b": copy_of}
    assert find_duplicates(probs)[0][:2] == ("a", "b")


def test_distinct_builtin_questions_are_not_duplicates():
    assert find_duplicates(PROBLEMS) == []
