"""run_cli.py - command-line prototype: test every candidate of every problem."""

import sys

from problems import PROBLEMS
from tester import run_isolated

COUNT = int(sys.argv[1]) if len(sys.argv) > 1 else 100
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 42

print(f"Tests per candidate: {COUNT}   Seed: {SEED}\n")
header = f'{"candidate":<32}{"match":>7}{"mismatch":>10}{"exception":>11}{"timeout":>9}{"ref_err":>9}'

for key, problem in PROBLEMS.items():
    print(f'== {problem["title"]} ==')
    print(header)
    first_failures = []
    for name in problem["candidates"]:
        r = run_isolated(key, name, COUNT, SEED, timeout=0.5)
        print(f'{name:<32}{r["matches"]:>7}{r["mismatches"]:>10}'
              f'{r["exceptions"]:>11}{r["timeouts"]:>9}{r["reference_errors"]:>9}')
        if r["stopped_early"]:
            print(f'   ({name}: {r["stopped_early"]}, executed {r["executed"]})')
        if r["failures"]:
            f = r["failures"][0]
            shown = f["input"] if len(f["input"]) <= 6 else str(f["input"][:6])[:-1] + ", ...]"
            first_failures.append(
                f'   first failure of "{name}": test #{f["test_index"]} '
                f'[{f["label"]}] input={shown} expected={f["expected"]} actual={f["actual"]}'
            )
    for line in first_failures:
        print(line)
    print()
