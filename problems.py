"""problems.py - reference (trusted) and buggy implementations.

Shared semantics (statements, references and generators must all agree):
  - Input: a non-empty list of ints, 1 <= n <= 1000, each in [-10000, 10000].
  - second_largest_ref returns None if there are fewer than 2 distinct values.
  - max_subarray_ref considers NON-EMPTY subarrays only.
"""

# ====================================================================
# Problem 1: Maximum Element
# ====================================================================

def max_element_ref(arr):
    """Reference: scan once, keep the biggest. O(n) time, O(1) space."""
    best = arr[0]
    for x in arr[1:]:
        if x > best:
            best = x
    return best


def max_element_bug_zero_init(arr):
    """BUG: starts at 0, so all-negative arrays wrongly return 0."""
    best = 0
    for x in arr:
        if x > best:
            best = x
    return best


def max_element_bug_skip_last(arr):
    """BUG: never looks at the last element, so it fails whenever the
    maximum is the last item (e.g. [1, 2, 9])."""
    best = arr[0]
    for x in arr[1:-1]:
        if x > best:
            best = x
    return best


# ====================================================================
# Problem 2: Second Largest Distinct Element
# ====================================================================

def second_largest_ref(arr):
    """Reference: sort the distinct values, take the second from the end.
    Returns None if there are fewer than 2 distinct values.
    O(n log n) time, O(n) space."""
    distinct = sorted(set(arr))
    if len(distinct) < 2:
        return None
    return distinct[-2]


def second_largest_bug_duplicates(arr):
    """BUG: takes the second-last element of the sorted list, so
    duplicates of the maximum (e.g. [5, 5, 3]) give 5 instead of 3.
    Also crashes on a single-element array."""
    return sorted(arr)[-2]


def second_largest_bug_all_equal(arr):
    """BUG: when there is only one distinct value, returns that value
    instead of None (e.g. [7, 7] gives 7)."""
    distinct = sorted(set(arr))
    if len(distinct) < 2:
        return distinct[0]
    return distinct[-2]


# ====================================================================
# Problem 3: Maximum Subarray Sum
# ====================================================================

def max_subarray_ref(arr):
    """Reference: Kadane's algorithm. O(n) time, O(1) space."""
    best = current = arr[0]
    for x in arr[1:]:
        current = max(x, current + x)
        best = max(best, current)
    return best


def max_subarray_bug_zero_init(arr):
    """BUG: best starts at 0, so all-negative arrays wrongly return 0."""
    best = current = 0
    for x in arr:
        current = max(x, current + x)
        best = max(best, current)
    return best


def max_subarray_bug_skip_last(arr):
    """BUG: Kadane's loop skips the last element, so it fails whenever
    the best subarray ends at the last position (e.g. [-1, 5])."""
    best = current = arr[0]
    for x in arr[1:-1]:
        current = max(x, current + x)
        best = max(best, current)
    return best


# ====================================================================
# Extra CORRECT candidates (BugHunt must report zero failures on these)
# ====================================================================

def max_element_correct_builtin(arr):
    """Correct: uses Python's built-in max."""
    return max(arr)


def second_largest_correct_two_pass(arr):
    """Correct: O(n) without sorting. Find max, then max of values below it."""
    top = max(arr)
    below = [x for x in arr if x < top]
    return max(below) if below else None


def max_subarray_correct_bruteforce(arr):
    """Correct: tries every start/end. O(n^2), fine for n <= 1000."""
    best = arr[0]
    for i in range(len(arr)):
        total = 0
        for j in range(i, len(arr)):
            total += arr[j]
            if total > best:
                best = total
    return best


# ====================================================================
# Registry: what BugHunt can test. (Day 2 adds statements and metadata.)
# ====================================================================

PROBLEMS = {
    "max_element": {
        "title": "Maximum Element in an Array",
        "reference": max_element_ref,
        "candidates": {
            "correct: built-in max": max_element_correct_builtin,
            "bug: zero init": max_element_bug_zero_init,
            "bug: skips last element": max_element_bug_skip_last,
        },
    },
    "second_largest": {
        "title": "Second Largest Distinct Element",
        "reference": second_largest_ref,
        "candidates": {
            "correct: two-pass": second_largest_correct_two_pass,
            "bug: duplicates of max": second_largest_bug_duplicates,
            "bug: all-equal returns value": second_largest_bug_all_equal,
        },
    },
    "max_subarray": {
        "title": "Maximum Subarray Sum",
        "reference": max_subarray_ref,
        "candidates": {
            "correct: brute force": max_subarray_correct_bruteforce,
            "bug: zero init": max_subarray_bug_zero_init,
            "bug: skips last element": max_subarray_bug_skip_last,
        },
    },
}


# ====================================================================
# Metadata for the UI and quality checks (Day 2)
# ====================================================================

COMMON_CONSTRAINTS = [
    "1 <= n <= 1000, where n is the length of arr (empty arrays are NOT valid inputs)",
    "Every element is an integer in the range [-10000, 10000]",
    "Duplicates and negative values are allowed",
]

METADATA = {
    "max_element": {
        "statement": (
            "Given a non-empty list of integers, return the largest value in the list."
        ),
        "signature": "def solve(arr: list[int]) -> int",
        "input_spec": "arr: a list of n integers.",
        "output_spec": "A single integer: the maximum value in arr.",
        "constraints": COMMON_CONSTRAINTS,
        "samples": [
            {"input": [3, 1, 4, 1, 5], "output": 5,
             "explanation": "5 is the largest value."},
            {"input": [-7, -3, -9], "output": -3,
             "explanation": "With all-negative input, the maximum is the negative number closest to zero."},
        ],
        "algorithm": (
            "Start with the first element as the best so far. Scan the rest of the list "
            "once, replacing the best whenever a larger value appears."
        ),
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
    },
    "second_largest": {
        "statement": (
            "Given a non-empty list of integers, return the second largest DISTINCT value. "
            "Duplicates of the maximum do not count as the second largest. "
            "If the list has fewer than 2 distinct values, return None."
        ),
        "signature": "def solve(arr: list[int]) -> int | None",
        "input_spec": "arr: a list of n integers.",
        "output_spec": (
            "An integer (the second largest distinct value), or None if arr has "
            "fewer than 2 distinct values."
        ),
        "constraints": COMMON_CONSTRAINTS,
        "samples": [
            {"input": [5, 5, 3], "output": 3,
             "explanation": "The distinct values are 5 and 3, so the second largest is 3, not 5."},
            {"input": [7, 7], "output": None,
             "explanation": "Only one distinct value exists, so the answer is None."},
            {"input": [4, 9, 2, 9], "output": 4,
             "explanation": "The distinct values are 2, 4 and 9, so the second largest is 4."},
        ],
        "algorithm": (
            "Remove duplicates with a set, sort the distinct values, and return the "
            "second from the end. Return None if there are fewer than 2 distinct values."
        ),
        "time_complexity": "O(n log n)",
        "space_complexity": "O(n)",
    },
    "max_subarray": {
        "statement": (
            "Given a non-empty list of integers, return the largest possible sum of a "
            "NON-EMPTY contiguous subarray."
        ),
        "signature": "def solve(arr: list[int]) -> int",
        "input_spec": "arr: a list of n integers.",
        "output_spec": "A single integer: the maximum sum over all non-empty contiguous subarrays.",
        "constraints": COMMON_CONSTRAINTS,
        "samples": [
            {"input": [-2, 1, -3, 4, -1, 2, 1, -5, 4], "output": 6,
             "explanation": "The subarray [4, -1, 2, 1] has sum 6, the largest possible."},
            {"input": [-3, -1, -2], "output": -1,
             "explanation": "The subarray must be non-empty, so the best choice is [-1], not an empty sum of 0."},
        ],
        "algorithm": (
            "Kadane's algorithm: walk through the list keeping the best sum of a subarray "
            "ending at the current position (either extend the previous one or start fresh), "
            "and track the best value seen overall."
        ),
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
    },
}

for _key, _meta in METADATA.items():
    PROBLEMS[_key].update(_meta)


# ====================================================================
# Candidate that never finishes (tests timeout handling)
# ====================================================================

def max_element_bug_hang(arr):
    """BUG: infinite loop when there are 2+ elements and all are equal."""
    if len(arr) > 1 and len(set(arr)) == 1:
        while True:
            pass
    return max(arr)


PROBLEMS["max_element"]["candidates"]["bug: hangs on all-equal input"] = max_element_bug_hang
