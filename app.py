import json
from datetime import datetime, timezone
import pandas as pd
import streamlit as st
from audit_scope_data.analysis import profile_dataframe, group_outcome_analysis, build_markdown_report

st.set_page_config(page_title="AuditScopeData | Data Quality & Fairness Audit", page_icon="🔎", layout="wide")
st.title("🔎 AuditScopeData")
st.caption("Data quality and group outcome disparity — transparent first-pass audit")
st.warning("Prototype only. Metrics are descriptive screening signals, not proof of bias or legal compliance. Do not use as the sole basis for high-stakes decisions.")

uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded:
    try:
        df = pd.read_csv(uploaded)
    except Exception as exc:
        st.error(f"Could not read CSV: {exc}")
        st.stop()
else:
    st.info("Showing the bundled synthetic demo dataset. Upload a CSV to analyze your own data.")
    df = pd.read_csv("data/sample_applications.csv")

if df.empty:
    st.error("The dataset has no rows.")
    st.stop()

st.subheader("Dataset overview")
a, b, c, d = st.columns(4)
a.metric("Rows", f"{len(df):,}")
b.metric("Columns", f"{len(df.columns):,}")
c.metric("Duplicate rows", f"{int(df.duplicated().sum()):,}")
d.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")
with st.expander("Preview data", expanded=True):
    st.dataframe(df.head(100), use_container_width=True)

st.subheader("Data quality profile")
profile = profile_dataframe(df)
st.dataframe(pd.DataFrame(profile["columns"]), use_container_width=True, hide_index=True)
numeric_cols = df.select_dtypes(include="number").columns.tolist()
if numeric_cols:
    st.write("Numeric summary")
    st.dataframe(df[numeric_cols].describe().T, use_container_width=True)

st.subheader("Group outcome comparison")
st.write("Choose a group field and a binary outcome field. The positive value is treated as the favorable outcome for this descriptive comparison.")
left, middle, right = st.columns(3)
group_col = left.selectbox("Group column", options=list(df.columns), index=(list(df.columns).index("group") if "group" in df.columns else 0))
outcome_options = [c for c in df.columns if df[c].nunique(dropna=True) == 2]
if not outcome_options:
    st.info("No binary columns detected. Add/select a binary outcome column to calculate group rates.")
    outcome_col = None
else:
    default_outcome = outcome_options.index("approved") if "approved" in outcome_options else 0
    outcome_col = middle.selectbox("Binary outcome column", options=outcome_options, index=default_outcome)
    vals = list(pd.Series(df[outcome_col].dropna().unique()).sort_values(key=lambda s: s.astype(str)))
    positive = right.selectbox("Positive outcome value", options=vals, index=(vals.index(1) if 1 in vals else (vals.index("1") if "1" in vals else len(vals)-1)))
    if st.button("Run disparity analysis", type="primary"):
        result = group_outcome_analysis(df, group_col, outcome_col, positive)
        st.session_state["result"] = result
        st.session_state["analysis_meta"] = {"group_col": group_col, "outcome_col": outcome_col, "positive": str(positive)}

if "result" in st.session_state:
    result = st.session_state["result"]
    st.markdown("#### Group outcome rates")
    st.dataframe(pd.DataFrame(result["groups"]), use_container_width=True, hide_index=True)
    m1, m2, m3 = st.columns(3)
    spd = result["statistical_parity_difference"]
    di = result["disparate_impact_ratio"]
    m1.metric("Statistical parity difference", "N/A" if spd is None else f"{spd:.3f}")
    m2.metric("Disparate impact ratio", "N/A" if di is None else f"{di:.3f}")
    m3.metric("Groups analyzed", len(result["groups"]))
    st.caption("SPD = highest observed group rate minus lowest observed group rate with sign defined as max-rate group minus min-rate group here. Disparate impact = lowest nonzero-denominator group rate / highest group rate. These are descriptive, unadjusted comparisons.")
    report = {
        "tool": "AuditScopeData",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": {"rows": len(df), "columns": len(df.columns)},
        "quality_profile": profile,
        "analysis": result,
        "metadata": st.session_state.get("analysis_meta", {}),
        "limitations": [
            "Descriptive disparity is not proof of unfairness or causation.",
            "Small samples and missing data can make rates unstable.",
            "Group definitions and outcome semantics require domain review.",
            "This prototype is not legal advice or a compliance certification."
        ]
    }
    st.download_button("Download JSON report", json.dumps(report, indent=2, default=str), "audit_scope_data_report.json", "application/json")
    md = build_markdown_report(report)
    st.download_button("Download Markdown report", md, "audit_scope_data_report.md", "text/markdown")
