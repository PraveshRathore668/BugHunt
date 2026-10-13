# BugHunt

BugHunt finds bugs in programming solutions by comparing them against a trusted reference implementation (differential testing). It generates valid inputs, including deliberate edge cases, runs both implementations, and reports any input where they disagree. It then shrinks the failing input to a smaller one that still fails.

> Passing generated tests does **not** prove a solution is correct. BugHunt reports the failures it finds in a given run, nothing more.

**Live demo:** _(URL added after deployment)_

## The problem

An optimized solution can pass the sample cases and still fail on all-negative arrays, duplicate maximums, single-element inputs or boundary values. Finding the failing input by hand is slow. BugHunt automates that search and produces a small counterexample a reviewer can read at a glance.

## Features

- **Built-in problems:** Maximum Element, Second Largest Distinct Element, Maximum Subarray Sum. Each has a statement, constraints, samples, a reference solution, complexity notes and buggy variants.
- **Differential testing:** reference vs candidate on the same inputs, with mismatches, exceptions and timeouts counted separately.
- **Edge-case generation:** 18 deliberate edge-case builders (single element, all-equal, all-negative, duplicates of the maximum, boundary values, maximum length and more) plus random inputs, each labeled `edge` or `random`. Same seed, same tests.
- **Counterexample minimization:** removes chunks, simplifies values, runs within a call and time budget, re-verifies the result, and falls back to the original input.
- **Isolated execution:** candidates run in a separate worker process with a per-test timeout and run budgets.
- **JSON report:** configuration, seed, counts, failing inputs, expected and actual outputs, and the minimized counterexample.
- **Question quality checks:** deterministic checks for missing fields, wrong samples, invalid generated inputs and near-duplicate statements. These are rule-based, not AI.

## Architecture
cat >> README.md << 'EOF'

## Technology

Python, Streamlit, pytest, Hypothesis, Git and GitHub.

## Run locally

```bash
git clone <your-repo-url>
cd bughunt
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Run the tests

```bash
python3 -m pytest -q
```

At the last run, 69 tests passed (regression, engine, minimizer, report, timeout, quality and Hypothesis tests). Command-line demo: `python3 run_cli.py 100 42`.

## Example workflow

1. Choose **Maximum Element in an Array** and the candidate **bug: skips last element**.
2. Set 100 tests and seed 42, then click **Find Bugs**.
3. BugHunt reports 7 mismatches out of 100. The first failure is `[-7152, -6642, -5428, 7870, 9349]`: expected 9349, got 7870.
4. The minimizer reduces it to `[0, 3935]`, re-verified against both implementations.
5. Download the JSON report. Re-running with the same seed reproduces the same tests.

## Screenshots

_(Added after deployment.)_

## Security architecture

Running arbitrary code on a public server is dangerous, so **BugHunt does not execute code typed by visitors.** The public app runs only the built-in reference and candidate implementations, which are in this repository. Even so, candidates run in a separate worker process with a per-test timeout, CPU limit, run time budget and early stop after repeated timeouts, so a hang cannot freeze the app. The worker receives a minimal environment with no secrets.

This is process isolation, **not a full sandbox for untrusted code**. `sandbox.py` is the adapter where a properly isolated execution service could be plugged in later.

## Known limitations

- Passing tests do not prove correctness.
- A minimized input is a reduced counterexample, not necessarily the smallest possible.
- Only three array problems are supported, with candidates chosen from a built-in list.
- The memory limit in the worker applies on Linux only.
- Differential testing is only as good as the reference solution and the generators.

## Future improvements

- A secure, isolated execution service for user-submitted code.
- More problems, including SQL and string problems.
- Optional AI suggestions for problem quality, clearly separated from deterministic checks.
