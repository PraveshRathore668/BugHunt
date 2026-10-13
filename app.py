"""app.py - BugHunt Streamlit interface (Milestone 2.2: problem description)."""

import streamlit as st

from problems import PROBLEMS

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
