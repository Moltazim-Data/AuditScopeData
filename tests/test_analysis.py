import pandas as pd
from audit_scope_data.analysis import profile_dataframe, group_outcome_analysis

def test_profile_missing_and_duplicates():
    df = pd.DataFrame({"x": [1, 1, None], "g": ["A", "A", "B"]})
    result = profile_dataframe(df)
    assert result["row_count"] == 3
    assert result["duplicate_rows"] == 1
    x = next(c for c in result["columns"] if c["column"] == "x")
    assert x["missing_count"] == 1

def test_group_outcome_rates_and_metrics():
    df = pd.DataFrame({"group": ["A", "A", "B", "B"], "approved": [1, 1, 1, 0]})
    result = group_outcome_analysis(df, "group", "approved", 1)
    rates = {g["group"]: g["positive_rate"] for g in result["groups"]}
    assert rates == {"A": 1.0, "B": 0.5}
    assert result["statistical_parity_difference"] == 0.5
    assert result["disparate_impact_ratio"] == 0.5


def test_group_analysis_rejects_non_binary_outcome_column():
    df = pd.DataFrame({"group": ["A", "A", "B", "B"], "outcome": [0, 0, 0, 0]})
    try:
        group_outcome_analysis(df, "group", "outcome", 1)
    except ValueError as exc:
        assert "exactly two non-null values" in str(exc)
    else:
        raise AssertionError("Expected a single-valued outcome column to be rejected")


def test_group_analysis_excludes_rows_with_missing_selected_values():
    df = pd.DataFrame({"group": ["A", "A", "B"], "outcome": [1, None, 0]})
    result = group_outcome_analysis(df, "group", "outcome", 1)
    assert result["rows_used"] == 2
    assert result["rows_excluded_missing"] == 1
