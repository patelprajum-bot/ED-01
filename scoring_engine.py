import pandas as pd
import numpy as np


def clean_numeric(series):
    """
    Convert values like:
    85, '85%', '8.5' into numeric values.
    """
    return pd.to_numeric(
        series.astype(str)
        .str.replace("%", "", regex=False)
        .str.strip(),
        errors="coerce"
    )


def normalize_low_is_risk(series):
    """
    Low value = higher support need.

    Example:
    Low marks / low attendance / low CGPA
    """
    values = clean_numeric(series)

    if values.notna().sum() <= 1:
        return pd.Series(0.0, index=series.index)

    min_val = values.min()
    max_val = values.max()

    if max_val == min_val:
        return pd.Series(0.0, index=series.index)

    return (max_val - values) / (max_val - min_val)


def normalize_high_is_risk(series):
    """
    High value = higher support need.

    Example:
    Backlogs / failures
    """
    values = clean_numeric(series)

    if values.notna().sum() <= 1:
        return pd.Series(0.0, index=series.index)

    min_val = values.min()
    max_val = values.max()

    if max_val == min_val:
        return pd.Series(0.0, index=series.index)

    return (values - min_val) / (max_val - min_val)


def calculate_support_score(df, column_mapping):
    """
    Calculate a support-priority score using only
    indicators that are actually available in the PDF.
    """

    result = df.copy()

    risk_components = []
    reasons = [[] for _ in range(len(df))]

    # ---------------------------------
    # FIND AVAILABLE COLUMN TYPES
    # ---------------------------------

    attendance_columns = []
    academic_columns = []
    backlog_columns = []

    for column, category in column_mapping.items():

        if category == "attendance":
            attendance_columns.append(column)

        elif category == "academic_performance":
            academic_columns.append(column)

        elif category == "backlogs":
            backlog_columns.append(column)

    # ---------------------------------
    # ATTENDANCE RISK
    # ---------------------------------

    for column in attendance_columns:

        risk = normalize_low_is_risk(result[column])

        risk_components.append(("Attendance", risk))

        for i, value in enumerate(risk):
            if value >= 0.60:
                reasons[i].append("Low attendance")

    # ---------------------------------
    # ACADEMIC PERFORMANCE RISK
    # ---------------------------------

    for column in academic_columns:

        risk = normalize_low_is_risk(result[column])

        risk_components.append(("Academic Performance", risk))

        for i, value in enumerate(risk):
            if value >= 0.60:
                reasons[i].append(f"Low {column}")

    # ---------------------------------
    # BACKLOG RISK
    # ---------------------------------

    for column in backlog_columns:

        risk = normalize_high_is_risk(result[column])

        risk_components.append(("Backlogs", risk))

        for i, value in enumerate(risk):
            if value >= 0.50:
                reasons[i].append(f"Backlogs in {column}")

    # ---------------------------------
    # FINAL SCORE
    # ---------------------------------

    if len(risk_components) == 0:

        result["support_score"] = 0.0
        result["support_reasons"] = "No usable academic indicators detected."

        return result

    score_matrix = pd.DataFrame(
        {name: values for name, values in risk_components},
        index=result.index
    )

    result["support_score"] = score_matrix.mean(axis=1)

    result["support_reasons"] = [
        ", ".join(r) if r else "No major risk indicator"
        for r in reasons
    ]

    return result