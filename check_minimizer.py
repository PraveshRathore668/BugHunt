from generators import generate_tests
from minimizer import classify, minimize
from problems import PROBLEMS
from sandbox import CandidateRunner
from tester import run_function

for key, p in PROBLEMS.items():
    for name, func in p["candidates"].items():
        if name.startswith("correct") or "hangs" in name:
            continue
        caller = lambda a, f=func: run_function(f, a)
        for t in generate_tests(100, 42):
            kind = classify(p["reference"], caller, t["input"])
            if kind:
                r = minimize(p["reference"], caller, t["input"], kind)
                print(f'{key:<15}{name:<32}{kind:<10}{len(r["original"]):>4} -> '
                      f'{r["minimized"]}  verified={r["verified"]}  calls={r["calls_used"]}')
                break

print("\nTimeout case (isolated worker):")
p = PROBLEMS["max_element"]
name = "bug: hangs on all-equal input"
with CandidateRunner("max_element", name, timeout=0.5) as runner:
    for t in generate_tests(100, 42):
        kind = classify(p["reference"], runner.call, t["input"])
        if kind:
            r = minimize(p["reference"], runner.call, t["input"], kind, max_calls=60)
            print(f'{kind}: {len(r["original"])} -> {r["minimized"]}  '
                  f'verified={r["verified"]}  calls={r["calls_used"]}')
            break
