"""app.py - BugHunt Streamlit interface (Milestone 2.3: run tests + results)."""

import streamlit as st

from problems import PROBLEMS
from datetime import datetime, timezone

from minimizer import classify, minimize
from reports import build_report, report_to_json
from quality import find_duplicates, validate_problem
from sandbox import CandidateRunner
from tester import run_isolated

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
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    bar = st.progress(0.0, text="Running tests...")

    def on_progress(done, total):
        bar.progress(done / total, text=f"Running tests... {done}/{total}")

    result = run_isolated(
        key,
        cand_name,
        count,
        int(seed),
        progress=on_progress,
    )
    bar.empty()

    minimized = None
    if result["failures"] and result["failures"][0]["status"] != "reference_error":
        first = result["failures"][0]
        with st.spinner("Minimizing the failing input..."):
            with CandidateRunner(key, cand_name, result["per_test_timeout"]) as runner:
                minimized = minimize(problem["reference"], runner.call,
                                     first["input"], first["status"])
    st.session_state["minimized"] = minimized
    st.session_state["report"] = build_report(key, cand_name, result, minimized, started_at)
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
        label = {"exception": "Error", "timeout": "Timeout"}.get(f["status"], "Actual (candidate)")
        b.markdown(f'**{label}:** `{f["actual"]}`')
        st.markdown(f'**Seed:** `{f["seed"]}`')

        mz = st.session_state.get("minimized")
        st.subheader("Counterexample")
        o, r2 = st.columns(2)
        o.markdown(f'**Original** ({len(f["input"])} elements)')
        o.code(str(f["input"][:30]) + (" ..." if len(f["input"]) > 30 else ""))
        if mz and mz["verified"]:
            r2.markdown(f'**Reduced** ({len(mz["minimized"])} elements, re-verified)')
            r2.code(str(mz["minimized"]))
            st.caption(f'{mz["note"]}; {mz["calls_used"]} test calls used. '
                       "This is a reduced counterexample, not necessarily the smallest possible.")
        else:
            r2.markdown("**Reduced:** not available, showing the original.")

        total_fail = result["mismatches"] + result["exceptions"] + result["timeouts"]
        with st.expander(f"All recorded failures ({len(failures)} of {total_fail} shown)"):
            rows = []
            for x in failures:
                inp = x["input"] if len(x["input"]) <= 10 else x["input"][:10] + ["..."]
                rows.append({
                    "test": x["test_index"],
                    "type": x["category"],
                    "label": x["label"],
                    "input": str(inp),
                    "expected": str(x["expected"]),
                    "actual": str(x["actual"]),
                })
            st.table(rows)

    if st.session_state.get("report"):
        st.download_button(
            "Download JSON report",
            report_to_json(st.session_state["report"]),
            file_name="bughunt_report.json",
            mime="application/json",
        )
    if result["stopped_early"]:
        st.warning(f'Run ended early: {result["stopped_early"]}. '
                   f'Executed {result["executed"]} of {result["requested_tests"]} tests.')
    st.caption(f'Finished in {result["elapsed_seconds"]} s. '
               f'Each test is limited to {result["per_test_timeout"]} s.')


# ---------- question quality checks (deterministic, not AI) ----------
st.divider()
st.header("Question quality checks")
st.caption(
    "These checks come from fixed rules (missing fields, sample outputs checked "
    "against the reference, generated inputs checked against the constraints). "
    "They are deterministic and do not use AI."
)

issues = validate_problem(key, problem)
if issues:
    for i in issues:
        box = st.error if i["severity"] == "error" else st.warning
        box(f'[{i["check"]}] {i["message"]}')
else:
    st.success("No issues found by the deterministic checks for this problem.")

dups = find_duplicates(PROBLEMS)
if dups:
    for a, b, ratio in dups:
        st.warning(f"Possible duplicate questions: {a} and {b} (similarity {ratio}).")
else:
    st.caption(f"Duplicate check: no near-duplicate statements among {len(PROBLEMS)} problems.")
