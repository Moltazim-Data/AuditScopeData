from __future__ import annotations
import math
import pandas as pd

def profile_dataframe(df: pd.DataFrame) -> dict:
    rows = len(df)
    cols = []
    for name in df.columns:
        s = df[name]
        missing = int(s.isna().sum())
        cols.append({
            "column": str(name),
            "dtype": str(s.dtype),
            "missing_count": missing,
            "missing_pct": round((missing / rows * 100) if rows else 0.0, 2),
            "unique_non_null": int(s.nunique(dropna=True)),
            "sample_values": [str(x) for x in s.dropna().unique()[:5]],
        })
    return {
        "row_count": int(rows),
        "column_count": int(len(df.columns)),
        "duplicate_rows": int(df.duplicated().sum()),
        "columns": cols,
    }

def group_outcome_analysis(df: pd.DataFrame, group_col: str, outcome_col: str, positive_value) -> dict:
    if group_col not in df or outcome_col not in df:
        raise ValueError("Selected columns are not present in the dataset.")
    work = df[[group_col, outcome_col]].dropna().copy()
    if work.empty:
        raise ValueError("No complete rows remain for the selected columns.")
    values = set(work[outcome_col].unique())
    if len(values) != 2:
        raise ValueError("Outcome column must have exactly two non-null values.")
    if positive_value not in values and str(positive_value) not in {str(v) for v in values}:
        raise ValueError("Positive value is not present in the outcome column.")
    work["_positive"] = work[outcome_col].map(lambda x: int(str(x) == str(positive_value)))
    groups = []
    for group, part in work.groupby(group_col, dropna=False, sort=True):
        n = int(len(part))
        successes = int(part["_positive"].sum())
        rate = successes / n if n else None
        groups.append({"group": str(group), "sample_size": n, "positive_count": successes,
                       "positive_rate": round(rate, 6) if rate is not None else None})
    valid_rates = [x["positive_rate"] for x in groups if x["positive_rate"] is not None]
    max_rate = max(valid_rates) if valid_rates else None
    min_rate = min(valid_rates) if valid_rates else None
    spd = (max_rate - min_rate) if max_rate is not None else None
    di = (min_rate / max_rate) if max_rate is not None and max_rate > 0 else None
    return {
        "group_column": group_col,
        "outcome_column": outcome_col,
        "positive_value": str(positive_value),
        "rows_used": int(len(work)),
        "rows_excluded_missing": int(len(df) - len(work)),
        "groups": groups,
        "statistical_parity_difference": round(spd, 6) if spd is not None else None,
        "disparate_impact_ratio": round(di, 6) if di is not None else None,
        "interpretation": "Unadjusted descriptive comparison only; not causal evidence or a compliance conclusion."
    }

def build_markdown_report(report: dict) -> str:
    analysis = report.get("analysis", {})
    lines = [
        "# AuditScopeData audit report",
        "",
        f"- Generated (UTC): {report.get('generated_at_utc', 'unknown')}",
        f"- Dataset rows: {report.get('dataset', {}).get('rows', 'unknown')}",
        f"- Dataset columns: {report.get('dataset', {}).get('columns', 'unknown')}",
        "",
        "## Data quality",
        f"- Duplicate rows: {report.get('quality_profile', {}).get('duplicate_rows', 'unknown')}",
        "",
        "| Column | Type | Missing | Missing % | Unique |",
        "|---|---|---:|---:|---:|",
    ]
    for col in report.get("quality_profile", {}).get("columns", []):
        lines.append(f"| {col['column']} | {col['dtype']} | {col['missing_count']} | {col['missing_pct']}% | {col['unique_non_null']} |")
    if analysis:
        lines += [
            "", "## Group outcome comparison",
            f"- Group column: {analysis.get('group_column')}",
            f"- Outcome column: {analysis.get('outcome_column')}",
            f"- Positive outcome: {analysis.get('positive_value')}",
            f"- Statistical parity difference (max rate − min rate): {analysis.get('statistical_parity_difference')}",
            f"- Disparate impact ratio (min rate / max rate): {analysis.get('disparate_impact_ratio')}",
            "", "| Group | Sample size | Positive count | Positive rate |",
            "|---|---:|---:|---:|",
        ]
        for row in analysis.get("groups", []):
            lines.append(f"| {row['group']} | {row['sample_size']} | {row['positive_count']} | {row['positive_rate']} |")
    lines += ["", "## Limitations"]
    lines += [f"- {x}" for x in report.get("limitations", [
        "Descriptive disparities are not proof of unfairness or causation.",
        "Review sample sizes, data collection, and domain context before drawing conclusions."
    ])]
    return "\n".join(lines) + "\n"
