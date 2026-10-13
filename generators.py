"""generators.py - seeded generation of valid test inputs.

Every input is a list of ints obeying the constraints in problems.py:
  1 <= len <= 1000, each value in [-10000, 10000].
The same seed always produces the same sequence of tests.
"""

import random

MIN_LEN, MAX_LEN = 1, 1000
MIN_VAL, MAX_VAL = -10000, 10000


def is_valid_input(arr):
    """True if arr obeys the documented constraints."""
    return (
        isinstance(arr, list)
        and MIN_LEN <= len(arr) <= MAX_LEN
        and all(
            isinstance(x, int) and not isinstance(x, bool)
            and MIN_VAL <= x <= MAX_VAL
            for x in arr
        )
    )


# ---------- small helpers ----------

def _size(rng, lo=2, hi=12):
    return rng.randint(lo, hi)


def _vals(rng, n, lo, hi):
    return [rng.randint(lo, hi) for _ in range(n)]


# ---------- deliberate edge-case builders ----------
# Each takes an rng and returns (label, list).

def _single_element(rng):
    return "single element", [rng.randint(MIN_VAL, MAX_VAL)]


def _all_negative(rng):
    return "all negative", _vals(rng, _size(rng), MIN_VAL, -1)


def _increasing(rng):
    n = _size(rng)
    arr = sorted(rng.sample(range(MIN_VAL, MAX_VAL + 1), n))
    return "strictly increasing", arr


def _duplicate_max(rng):
    m = rng.randint(MIN_VAL + 1, MAX_VAL)
    smaller = rng.randint(MIN_VAL, m - 1)
    arr = [m] * rng.randint(2, 4) + [smaller]
    arr += [rng.randint(MIN_VAL, m) for _ in range(rng.randint(0, 5))]
    rng.shuffle(arr)
    return "repeated maximum", arr


def _all_equal(rng):
    return "all equal", [rng.randint(MIN_VAL, MAX_VAL)] * _size(rng)


def _min_size_two(rng):
    return "two elements", _vals(rng, 2, MIN_VAL, MAX_VAL)


def _decreasing(rng):
    n = _size(rng)
    arr = sorted(rng.sample(range(MIN_VAL, MAX_VAL + 1), n), reverse=True)
    return "strictly decreasing", arr


def _all_positive(rng):
    return "all positive", _vals(rng, _size(rng), 1, MAX_VAL)


def _mixed(rng):
    return "mixed positive and negative", _vals(rng, _size(rng), -50, 50)


def _zeros(rng):
    return "all zeros", [0] * _size(rng)


def _repeated_min(rng):
    m = rng.randint(MIN_VAL, MAX_VAL - 1)
    arr = [m] * rng.randint(2, 4)
    arr += [rng.randint(m, MAX_VAL) for _ in range(rng.randint(1, 5))]
    rng.shuffle(arr)
    return "repeated minimum", arr


def _boundary_values(rng):
    pool = [MIN_VAL, MAX_VAL, 0, -1, 1]
    return "boundary values", [rng.choice(pool) for _ in range(_size(rng))]


def _all_min_boundary(rng):
    return "all at lower bound", [MIN_VAL] * _size(rng)


def _all_max_boundary(rng):
    return "all at upper bound", [MAX_VAL] * _size(rng)


def _negatives_then_big_end(rng):
    n = _size(rng)
    arr = _vals(rng, n - 1, MIN_VAL, -1) + [rng.randint(1, MAX_VAL)]
    return "negatives then big positive at end", arr


def _zeros_and_negatives(rng):
    return "zeros and negatives", _vals(rng, _size(rng), MIN_VAL, 0)


def _max_length_random(rng):
    return "maximum length (1000)", _vals(rng, MAX_LEN, MIN_VAL, MAX_VAL)


def _max_length_boundary(rng):
    pool = [MIN_VAL, MAX_VAL]
    return "maximum length, boundary values", [rng.choice(pool) for _ in range(MAX_LEN)]


# Order matters: the first few catch the most common bugs.
EDGE_BUILDERS = [
    _single_element,
    _all_negative,
    _increasing,
    _duplicate_max,
    _all_equal,
    _min_size_two,
    _decreasing,
    _all_positive,
    _mixed,
    _zeros,
    _repeated_min,
    _boundary_values,
    _all_min_boundary,
    _all_max_boundary,
    _negatives_then_big_end,
    _zeros_and_negatives,
    _max_length_random,
    _max_length_boundary,
]


def _random_input(rng):
    n = rng.randint(MIN_LEN, 50)
    lo = rng.choice([MIN_VAL, -100, -10])
    hi = rng.choice([MAX_VAL, 100, 10])
    return "uniform random", _vals(rng, n, lo, hi)


def generate_tests(count, seed):
    """Return `count` tests as dicts: index, category, label, input.

    category is "edge" (deliberate) or "random".
    The same (count, seed) always gives the same list.
    """
    if count < 1:
        raise ValueError("count must be at least 1")
    rng = random.Random(seed)
    tests = []
    for i in range(count):
        if i < len(EDGE_BUILDERS):
            label, arr = EDGE_BUILDERS[i](rng)
            category = "edge"
        elif rng.random() < 0.3:
            label, arr = rng.choice(EDGE_BUILDERS)(rng)
            category = "edge"
        else:
            label, arr = _random_input(rng)
            category = "random"
        tests.append({"index": i, "category": category, "label": label, "input": arr})
    return tests
