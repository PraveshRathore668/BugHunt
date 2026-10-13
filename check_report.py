import json
from reports import build_report, report_to_json
from tester import run_isolated

r = run_isolated("max_element", "bug: skips last element", 50, 42)
rep = build_report("max_element", "bug: skips last element", r, None, "now")
text = report_to_json(rep)
back = json.loads(text)
print("valid JSON:", isinstance(back, dict))
print("keys:", sorted(back))
print("mismatches in report:", back["summary"]["mismatches"])
