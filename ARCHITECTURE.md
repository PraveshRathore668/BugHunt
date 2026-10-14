BugHunt architecture
            app.py  (Streamlit interface)
                         |
     +-------------+-----+--------+----------------+
     |             |              |                |
 problems.py   generators.py   tester.py        reports.py
 (statements,  (seeded edge    (compare ref     (JSON report)
  reference,    + random        vs candidate,
  buggy impls)  inputs)         count results)
                                  |
                      +-----------+-----------+
                      |                       |
                 sandbox.py              minimizer.py
                 (worker process,        (shrink failing
                  per-test timeout)       input, re-verify)
                      |
                 worker.py
                 (runs ONE built-in candidate)

 quality.py : deterministic problem-definition checks
File	Purpose
app.py	Streamlit interface
problems.py	Problem definitions, references, correct and buggy candidates
generators.py	Seeded input generation and validation
tester.py	Differential testing engine
sandbox.py, worker.py	Run a candidate in a separate process with a timeout
minimizer.py	Counterexample minimization
reports.py	JSON report
quality.py	Question quality checks and duplicate detection
tests/	pytest and Hypothesis tests