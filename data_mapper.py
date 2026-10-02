import re


COLUMN_ALIASES = {
    "student_id": [
        "student id", "student_id", "roll no", "roll number",
        "rollno", "enrollment", "enrollment no", "registration no"
    ],

    "student_name": [
        "name", "student name", "student_name", "candidate name"
    ],

    "attendance": [
        "attendance", "attendance %", "attend %",
        "attendance percentage", "present %", "presence"
    ],

    "academic_performance": [
        "marks", "average marks", "avg marks", "total marks",
        "percentage", "percent", "score", "cgpa", "gpa",
        "grade", "academic performance"
    ],

    "backlogs": [
        "backlog", "backlogs", "arrears", "failures",
        "failed subjects", "supply"
    ]
}


def normalize_column_name(column):
    """Convert column name into a comparable format."""

    column = str(column).lower().strip()

    column = re.sub(r"[%()]", " ", column)
    column = re.sub(r"[_\-]+", " ", column)
    column = re.sub(r"\s+", " ", column)

    return column.strip()


def detect_column_type(column):

    normalized = normalize_column_name(column)

    for category, aliases in COLUMN_ALIASES.items():

        for alias in aliases:

            if normalized == alias:
                return category

    # Partial matching
    for category, aliases in COLUMN_ALIASES.items():

        for alias in aliases:

            if alias in normalized or normalized in alias:
                return category

    return "unknown"


def map_columns(df):

    mapping = {}

    for column in df.columns:

        category = detect_column_type(column)

        mapping[column] = category

    return mapping