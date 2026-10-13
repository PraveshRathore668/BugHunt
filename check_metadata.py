from generators import is_valid_input
from problems import PROBLEMS

required = ["statement", "signature", "input_spec", "output_spec", "constraints",
            "samples", "algorithm", "time_complexity", "space_complexity"]

ok = True
for key, p in PROBLEMS.items():
    missing = [f for f in required if not p.get(f)]
    print(f'{key}: missing fields = {missing or "none"}')
    ok &= not missing
    for s in p["samples"]:
        valid = is_valid_input(s["input"])
        actual = p["reference"](list(s["input"]))
        match = actual == s["output"] and type(actual) is type(s["output"])
        print(f'   sample {str(s["input"]):<42} valid={valid}  reference={actual}  expected={s["output"]}  match={match}')
        ok &= valid and match

print("\nALL METADATA CONSISTENT:", ok)
