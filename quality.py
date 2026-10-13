"""quality.py - deterministic quality checks for problem definitions.

Every issue here comes from fixed rules, not from AI. Each issue has
source="deterministic" so it can be told apart from any future AI suggestions.
"""

from difflib import SequenceMatcher

from generators import generate_tests, is_valid_input

REQUIRED_TEXT = {
    "statement": "problem statement",
    "input_spec": "input specification",
    "output_spec": "output specification",
    "constraints": "constraints",
    "algorithm": "algorithm explanation",
    "time_complexity": "time complexity",
    "space_complexity": "space complexity",
}


def _issue(key, check, message, severity="error"):
    return {"problem": key, "check": check, "severity": severity,
            "message": message, "source": "deterministic"}


def validate_problem(key, p, seeds=(1, 2, 3), tests_per_seed=100):
    """Return a list of issues for one problem definition (empty = no issues found)."""
    issues = []

    for field, label in REQUIRED_TEXT.items():
        value = p.get(field)
        if not value or (isinstance(value, str) and not value.strip()):
            issues.append(_issue(key, f"missing_{field}", f"Missing {label}."))

    reference = p.get("reference")
    if not callable(reference):
        issues.append(_issue(key, "missing_reference", "Missing reference implementation."))
        return issues

    samples = p.get("samples") or []
    if not samples:
        issues.append(_issue(key, "missing_samples", "No sample inputs and outputs."))
    for i, s in enumerate(samples, start=1):
        inp = s.get("input")
        if not is_valid_input(inp):
            issues.append(_issue(key, "invalid_sample_input",
                                 f"Sample {i} input violates the constraints."))
            continue
        try:
            actual = reference(list(inp))
        except Exception as exc:
            issues.append(_issue(key, "sample_reference_crash",
                                 f"Reference crashed on sample {i}: {type(exc).__name__}."))
            continue
        expected = s.get("output")
        if actual != expected or type(actual) is not type(expected):
            issues.append(_issue(
                key, "inconsistent_sample",
                f"Sample {i} says output {expected!r} but the reference returns {actual!r}."))

    bad_input = crash = False
    for seed in seeds:
        for t in generate_tests(tests_per_seed, seed):
            if not is_valid_input(t["input"]) and not bad_input:
                bad_input = True
                issues.append(_issue(key, "invalid_generated_input",
                                     f'Generator made an invalid input ({t["label"]}, seed {seed}).'))
            try:
                reference(list(t["input"]))
            except Exception as exc:
                if not crash:
                    crash = True
                    issues.append(_issue(
                        key, "reference_crash_on_generated_input",
                        f'Reference crashed on generated input ({t["label"]}): {type(exc).__name__}.'))

    names = list((p.get("candidates") or {}))
    if not any(n.startswith("correct") for n in names):
        issues.append(_issue(key, "no_correct_candidate",
                             "No correct candidate to check for false alarms.", "warning"))
    if not any(n.startswith("bug") for n in names):
        issues.append(_issue(key, "no_buggy_candidate",
                             "No buggy candidate to check that bugs are detected.", "warning"))
    return issues


def validate_all(problems, **kwargs):
    issues = []
    for key, p in problems.items():
        issues.extend(validate_problem(key, p, **kwargs))
    return issues


def _normalise(text):
    return " ".join(str(text).lower().split())


def find_duplicates(problems, threshold=0.85):
    """Return (key_a, key_b, similarity) for statements that look nearly identical."""
    keys = list(problems)
    found = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a = _normalise(problems[keys[i]].get("statement", ""))
            b = _normalise(problems[keys[j]].get("statement", ""))
            ratio = SequenceMatcher(None, a, b).ratio()
            if ratio >= threshold:
                found.append((keys[i], keys[j], round(ratio, 3)))
    return found
