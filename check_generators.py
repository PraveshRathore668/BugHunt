from generators import generate_tests, is_valid_input, EDGE_BUILDERS

print("edge builders:", len(EDGE_BUILDERS))

a = generate_tests(200, seed=42)
b = generate_tests(200, seed=42)
c = generate_tests(200, seed=43)
print("same seed -> same tests:", a == b)
print("different seed -> different tests:", a != c)

all_valid = all(
    is_valid_input(t["input"])
    for seed in range(50)
    for t in generate_tests(300, seed)
)
print("all inputs valid (50 seeds x 300 tests):", all_valid)

print()
for t in generate_tests(20, seed=1):
    shown = t["input"] if len(t["input"]) <= 8 else str(t["input"][:8])[:-1] + ", ...]"
    print(f'{t["index"]:>2} [{t["category"]:<6}] {t["label"]:<38} {shown}')
