import re


# ============================================================
# COLUMN ALIASES
# ============================================================

COLUMN_ALIASES = {

    "student_id": [
        "student id",
        "studentid",
        "student no",
        "student number",
        "roll no",
        "roll number",
        "rollno",
        "roll",
        "enrollment",
        "enrollment no",
        "enrollment number",
        "registration no",
        "registration number",
        "reg no",
        "admission no",
        "admission number"
    ],

    "student_name": [
        "name",
        "student name",
        "student_name",
        "candidate name",
        "full name",
        "student fullname",
        "student full name"
    ],

    "attendance": [
        "attendance",
        "attendance %",
        "attendance percentage",
        "attendance percent",
        "attend %",
        "attend percent",
        "attend percentage",
        "present %",
        "present percent",
        "present percentage",
        "presence",
        "class attendance",
        "overall attendance"
    ],

    "academic_performance": [
        "marks",
        "mark",
        "average marks",
        "avg marks",
        "average mark",
        "avg mark",
        "total marks",
        "total mark",
        "percentage",
        "percent",
        "percentage marks",
        "score",
        "academic score",
        "academic performance",
        "performance",
        "result",
        "cgpa",
        "gpa",
        "sgpa",
        "grade",
        "overall grade",
        "final score",
        "exam score",
        "exam marks",
        "semester marks",
        "semester score"
    ],

    "backlogs": [
        "backlog",
        "backlogs",
        "backlog count",
        "number of backlogs",
        "no of backlogs",
        "no. of backlogs",
        "arrears",
        "arrear",
        "failures",
        "failed subjects",
        "failed subject",
        "supply",
        "supplementary",
        "supplementary subjects"
    ],

    # ========================================================
    # SUBJECTS
    # ========================================================

    "subject": [
        "physics",
        "chemistry",
        "mathematics",
        "math",
        "maths",
        "biology",
        "english",
        "computer science",
        "history",
        "geography",
        "economics",
        "accountancy",
        "hindi",
        "commerce",
        "business studies",
        "political science",
        "psychology",
        "social science",
        "sanskrit",
        "physical education",
        "environment science",
        "environmental science",
        "evs",
        "civics"
    ],

    # ========================================================
    # INSTITUTION
    # ========================================================

    "institution_name": [
        "school name",
        "college name",
        "university name",
        "institution name"
    ]
}


# ============================================================
# NORMALIZE COLUMN NAME
# ============================================================

def normalize_column_name(column):

    column = str(column).lower().strip()

    column = re.sub(r"[%()]", " ", column)

    column = re.sub(r"[_\-]+", " ", column)

    column = re.sub(r"\s+", " ", column)

    return column.strip()


# ============================================================
# DETECT COLUMN TYPE
# ============================================================

def detect_column_type(column):

    normalized = normalize_column_name(column)

    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

    for category, aliases in COLUMN_ALIASES.items():

        for alias in aliases:

            alias = normalize_column_name(alias)

            if normalized == alias:
                return category


    # --------------------------------------------------------
    # Special categories that should be checked BEFORE
    # generic academic keywords
    # --------------------------------------------------------

    # Attendance
    if (
        "attendance" in normalized
        or "attend" in normalized
        or "presence" in normalized
    ):
        return "attendance"


    # Backlogs
    if (
        "backlog" in normalized
        or "arrear" in normalized
        or "failure" in normalized
        or "failed subject" in normalized
        or "supplementary" in normalized
        or "supply" in normalized
    ):
        return "backlogs"


    # Student ID
    if (
        ("student" in normalized and "id" in normalized)
        or "roll" in normalized
        or "enrollment" in normalized
        or "registration" in normalized
        or "admission no" in normalized
    ):
        return "student_id"


    # Student Name
    if (
        "student name" in normalized
        or "candidate name" in normalized
        or normalized == "name"
        or "full name" in normalized
    ):
        return "student_name"


    # Institution
    if (
        "school name" in normalized
        or "college name" in normalized
        or "university name" in normalized
        or "institution name" in normalized
    ):
        return "institution_name"


    # --------------------------------------------------------
    # SUBJECT DETECTION
    # --------------------------------------------------------

    for subject in COLUMN_ALIASES["subject"]:

        subject = normalize_column_name(subject)

        if normalized == subject:
            return "subject"

        if subject in normalized:
            return "subject"


    # --------------------------------------------------------
    # Academic Performance
    # --------------------------------------------------------

    if (
        "mark" in normalized
        or "score" in normalized
        or "percentage" in normalized
        or "percent" in normalized
        or "cgpa" in normalized
        or "gpa" in normalized
        or "sgpa" in normalized
        or "grade" in normalized
        or "performance" in normalized
    ):
        return "academic_performance"


    return "unknown"


# ============================================================
# MAP ALL COLUMNS
# ============================================================

def map_columns(df):

    mapping = {}

    for column in df.columns:

        mapping[column] = detect_column_type(column)

    return mapping