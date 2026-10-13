"""app.py - BugHunt Streamlit interface (Milestone 2.3: run tests + results)."""

import streamlit as st

from problems import PROBLEMS
from tester import run_differential

MAX_TESTS_LIMIT = 500

st.set_page_config(page_title="BugHunt", page_icon="🐞", layout="wide")

st.title("🐞 BugHunt")
st.caption(
    "Find bugs in programming solutions by comparing them against a trusted "
    "reference implementation (differential testing)."
)

st.info(
    "**Security note:** this app only runs the built-in reference and example "
    "candidate solutions. It never executes code typed by a visitor, because "
    "running arbitrary code on a public server is unsafe."
)

# ---------- problem selector ----------
keys = list(PROBLEMS)
key = st.selectbox(
    "Choose a problem",
    keys,
    format_func=lambda k: PROBLEMS[k]["title"],
)
problem = PROBLEMS[key]

# ---------- problem description ----------
st.header(problem["title"])
st.write(problem["statement"])

col1, col2 = st.columns(2)
with col1:
    st.subheader("Function signature")
    st.code(problem["signature"], language="python")
    st.subheader("Input")
    st.write(problem["input_spec"])
    st.subheader("Output")
    st.write(problem["output_spec"])
with col2:
    st.subheader("Constraints")
    for c in problem["constraints"]:
        st.markdown(f"- {c}")

st.subheader("Samples")
for i, s in enumerate(problem["samples"], start=1):
    with st.expander(f"Sample {i}: input = {s['input']}", expanded=(i == 1)):
        st.markdown(f"**Input:** `{s['input']}`")
        st.markdown(f"**Output:** `{s['output']}`")
        st.markdown(f"**Why:** {s['explanation']}")

with st.expander("Reference solution explanation"):
    st.write(problem["algorithm"])
    st.markdown(
        f"**Time complexity:** `{problem['time_complexity']}`  \n"
        f"**Space complexity:** `{problem['space_complexity']}`"
    )

# ---------- test configuration ----------
st.divider()
st.header("Find bugs")

c1, c2, c3 = st.columns(3)
with c1:
    cand_name = st.selectbox("Candidate solution (built-in)", list(problem["candidates"]))
with c2:
    count = st.select_slider("Number of tests", options=[10, 100, 500], value=100)
with c3:
    seed = st.number_input("Random seed", min_value=0, max_value=999_999, value=42, step=1)

st.caption("The same seed always produces the same tests, so results are reproducible.")

if st.button("Find Bugs", type="primary"):
    count = min(int(count), MAX_TESTS_LIMIT)
    bar = st.progress(0.0, text="Running tests...")

    def on_progress(done, total):
        bar.progress(done / total, text=f"Running tests... {done}/{total}")

    result = run_differential(
        problem["reference"],
        problem["candidates"][cand_name],
        count,
        int(seed),
        progress=on_progress,
    )
    bar.empty()
    st.session_state["result"] = result
    st.session_state["result_label"] = f'{problem["title"]} / {cand_name}'

# ---------- results ----------
result = st.session_state.get("result")
if result:
    st.subheader("Results")
    st.caption(f'Last run: {st.session_state["result_label"]}')

    m = st.columns(5)
    m[0].metric("Tests executed", result["executed"])
    m[1].metric("Matching outputs", result["matches"])
    m[2].metric("Output mismatches", result["mismatches"])
    m[3].metric("Exceptions", result["exceptions"])
    m[4].metric("Timeouts", result["timeouts"])

    if result["reference_errors"]:
        st.error(
            f'{result["reference_errors"]} test(s) crashed the REFERENCE solution. '
            "This means a problem with the test setup, not the candidate."
        )

    failures = result["failures"]
    if not failures and not result["reference_errors"]:
        st.success(
            "No failing test cases were found in this test run. "
            "This does not prove correctness."
        )
    elif failures:
        f = failures[0]
        st.error(f'Bug found. First failing test: #{f["test_index"]} ({f["category"]}: {f["label"]})')
        shown = f["input"] if len(f["input"]) <= 30 else f'{f["input"][:30]} ... ({len(f["input"])} elements)'
        st.markdown(f"**Failing input:** `{shown}`")
        a, b = st.columns(2)
        a.markdown(f'**Expected (reference):** `{f["expected"]}`')
        label = "Error" if f["status"] == "exception" else "Actual (candidate)"
        b.markdown(f'**{label}:** `{f["actual"]}`')
        st.markdown(f'**Seed:** `{f["seed"]}`')

        total_fail = result["mismatches"] + result["exceptions"]
        with st.expander(f"All recorded failures ({len(failures)} of {total_fail} shown)"):
            for x in failures:
                inp = x["input"] if len(x["input"]) <= 10 else f'{x["input"][:10]} ... ({len(x["input"])} elements)'
                st.markdown(
                    f'- #{x["test_index"]} [{x["category"]}: {x["label"]}] '
                    f'`{inp}` -> expected `{x["expected"]}`, got `{x["actual"]}`'
                )

    st.caption(f'Finished in {result["elapsed_seconds"]} s. Timeouts are always 0 until Day 3.')
