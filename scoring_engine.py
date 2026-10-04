import pandas as pd
import numpy as np


# ============================================================
# CLEAN NUMERIC VALUES
# ============================================================

def clean_numeric(series):

    return pd.to_numeric(
        series.astype(str)
        .str.replace("%", "", regex=False)
        .str.strip(),
        errors="coerce"
    )


# ============================================================
# LOW VALUE = HIGHER RISK
# Example: Attendance, Marks, CGPA, Subject Marks
# ============================================================

def normalize_low_is_risk(series):

    values = clean_numeric(series)

    if values.notna().sum() <= 1:
        return pd.Series(
            0.0,
            index=series.index
        )

    min_val = values.min()
    max_val = values.max()

    if max_val == min_val:
        return pd.Series(
            0.0,
            index=series.index
        )

    return (
        (max_val - values)
        / (max_val - min_val)
    )


# ============================================================
# HIGH VALUE = HIGHER RISK
# Example: Backlogs
# ============================================================

def normalize_high_is_risk(series):

    values = clean_numeric(series)

    if values.notna().sum() <= 1:
        return pd.Series(
            0.0,
            index=series.index
        )

    min_val = values.min()
    max_val = values.max()

    if max_val == min_val:
        return pd.Series(
            0.0,
            index=series.index
        )

    return (
        (values - min_val)
        / (max_val - min_val)
    )


# ============================================================
# SUPPORT SCORE CALCULATION
# ============================================================

def calculate_support_score(
    df,
    column_mapping
):

    result = df.copy()

    risk_components = []

    reasons = [
        []
        for _ in range(len(df))
    ]


    # ========================================================
    # IDENTIFY COLUMNS
    # ========================================================

    attendance_columns = []

    academic_columns = []

    backlog_columns = []

    subject_columns = []

    institution_columns = []


    for column, category in column_mapping.items():

        if category == "attendance":

            attendance_columns.append(column)

        elif category == "academic_performance":

            academic_columns.append(column)

        elif category == "backlogs":

            backlog_columns.append(column)

        elif category == "subject":

            subject_columns.append(column)

        elif category == "institution_name":

            institution_columns.append(column)


    # ========================================================
    # ATTENDANCE
    # ========================================================

    for column in attendance_columns:

        risk = normalize_low_is_risk(
            result[column]
        )

        risk_components.append(
            (
                f"Attendance - {column}",
                risk
            )
        )

        for i, value in enumerate(risk):

            if value >= 0.60:

                reasons[i].append(
                    "Low attendance"
                )


    # ========================================================
    # ACADEMIC PERFORMANCE
    # ========================================================

    for column in academic_columns:

        risk = normalize_low_is_risk(
            result[column]
        )

        risk_components.append(
            (
                f"Academic - {column}",
                risk
            )
        )

        for i, value in enumerate(risk):

            if value >= 0.60:

                reasons[i].append(
                    f"Low {column}"
                )


    # ========================================================
    # SUBJECT PERFORMANCE
    # Physics / Chemistry / Maths / Biology etc.
    # ========================================================

    for column in subject_columns:

        risk = normalize_low_is_risk(
            result[column]
        )

        risk_components.append(
            (
                f"Subject - {column}",
                risk
            )
        )

        for i, value in enumerate(risk):

            if value >= 0.60:

                reasons[i].append(
                    f"Low {column}"
                )


    # ========================================================
    # BACKLOGS
    # ========================================================

    for column in backlog_columns:

        risk = normalize_high_is_risk(
            result[column]
        )

        risk_components.append(
            (
                f"Backlogs - {column}",
                risk
            )
        )

        for i, value in enumerate(risk):

            if value >= 0.50:

                reasons[i].append(
                    f"Backlogs in {column}"
                )


    # ========================================================
    # NO USABLE DATA
    # ========================================================

    if len(risk_components) == 0:

        result["support_score"] = 0.0

        result["support_reasons"] = (
            "No usable academic indicators detected."
        )

        return result


    # ========================================================
    # CREATE SCORE MATRIX
    # ========================================================

    score_matrix = pd.DataFrame(
        {
            name: values
            for name, values
            in risk_components
        },
        index=result.index
    )


    # ========================================================
    # FINAL SUPPORT SCORE
    # ========================================================

    result["support_score"] = (
        score_matrix.mean(axis=1)
    )


    # ========================================================
    # REASONS
    # ========================================================

    result["support_reasons"] = [

        ", ".join(reason)
        if reason
        else "No major risk indicator"

        for reason in reasons
    ]


    return result