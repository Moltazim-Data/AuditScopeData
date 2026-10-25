# AuditScopeData

**A lightweight data quality and group-outcome fairness auditing tool.**

AuditScopeData is an open-source MVP for exploring tabular data quality and descriptive differences in binary outcomes across groups. It combines a Streamlit dashboard, reusable Python analysis functions, and downloadable audit reports.

## Features

- Upload CSV files in a Streamlit dashboard
- Profile missing values, duplicate rows, column types, unique values, and numeric summaries
- Select a group column and a binary outcome column
- Compare positive outcome rates across groups
- Calculate statistical parity difference (maximum rate minus minimum rate) and disparate impact ratio (minimum rate divided by maximum rate)
- Export JSON and Markdown reports
- Explore an included synthetic sample dataset
- Run automated tests for profiling and disparity metrics

## Important limitations

AuditScopeData is a **screening and exploration tool**, not a legal compliance assessment or proof of discrimination. Group disparities can have many causes; metrics depend on how groups, outcomes, and eligible populations are defined. These are unadjusted descriptive comparisons and do not establish causation. Small samples and missing data can make rates unstable. Do not use this output alone to make high-stakes decisions. The included sample dataset is synthetic and demonstrates the workflow only.

## Quick start

Python 3.10+ is recommended. Run these commands from the repository root:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit. The app loads `data/sample_applications.csv` by default; you can also upload your own CSV.

## Demo walkthrough

1. Start the app using the command above.
2. Use the bundled sample dataset or upload a CSV.
3. Select `group` as the group column.
4. Select `approved` as the binary outcome column.
5. Set the positive outcome to `1`.
6. Run the comparison and review group sample sizes, outcome rates, and disparity metrics.
7. Download the JSON or Markdown report.

## Run tests

```bash
python -m pip install pytest
python -m pytest -q
```

## Project structure

```text
.
├── app.py
├── audit_scope_data/
│   ├── __init__.py
│   └── analysis.py
├── data/
│   └── sample_applications.csv
├── tests/
│   └── test_analysis.py
├── .gitignore
└── requirements.txt
```

## Metrics

- **Statistical parity difference (as implemented here):** highest observed group positive-outcome rate minus the lowest observed group rate. This is a non-negative range, not the signed unprivileged-minus-privileged definition sometimes used in fairness literature.
- **Disparate impact ratio (as implemented here):** lowest observed group positive-outcome rate divided by the highest. If the highest rate is zero, the ratio is reported as unavailable (`null` / `None`) because the division is undefined.

Both values are descriptive summaries. They do not adjust for confounders, uncertainty, sample composition, or domain-specific eligibility criteria.

## Validation and research roadmap

For a stronger evaluation, document a lawful real-world dataset, preregister the analysis question and metric, validate results against hand-calculated examples, report uncertainty intervals and sample sizes, and review interpretation with a domain expert. Evaluate usability and decision quality before claiming real-world impact.

## Repository description

> Lightweight Streamlit tool for auditing tabular data quality and exploring group-level outcome disparities with transparent metrics and downloadable reports.

This repository is a prototype and does not claim validated real-world impact or compliance certification.
