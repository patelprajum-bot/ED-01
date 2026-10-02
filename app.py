import numpy as np
import streamlit as st
import pandas as pd
import pdfplumber
import io
from data_mapper import map_columns
from scoring_engine import calculate_support_score


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="ED-01 | Fair Student Support",
    page_icon="🎓",
    layout="wide"
)

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>
.stApp {
    background-color: #0d1117;
    color: #c9d1d9;
}

[data-testid="stSidebar"] {
    background-color: #161b22;
}

h1, h2, h3 {
    color: #f0f6fc;
}

.info-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    "<h1 style='text-align:center;'>🎓 ED-01: Fair Student-Support Prioritization</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:#8b949e;'>"
    "Universal Student Support & Responsible AI System"
    "</p>",
    unsafe_allow_html=True
)

st.divider()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("⚙️ Admin Control Panel")

uploaded_file = st.sidebar.file_uploader(
    "📄 Upload Student PDF",
    type=["pdf"]
)

# -----------------------------
# PDF TABLE EXTRACTION
# -----------------------------
def extract_tables_from_pdf(pdf_file):

    tables = []

    pdf_bytes = pdf_file.getvalue()

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:

        for page_number, page in enumerate(pdf.pages, start=1):

            extracted_tables = page.extract_tables()

            for table in extracted_tables:

                if table and len(table) > 1:

                    header = table[0]

                    data = table[1:]

                    df = pd.DataFrame(
                        data,
                        columns=header
                    )

                    df = df.dropna(how="all")

                    tables.append({
                        "page": page_number,
                        "data": df
                    })

    return tables


# -----------------------------
# MAIN APP
# -----------------------------

if uploaded_file is None:

    st.markdown("""
    <div class="info-card">

    ### 📄 Upload Student Data

    Upload a student-performance PDF from:

    - 🏫 School
    - 🎓 College
    - 🏛️ University

    The system will extract the student table automatically.

    </div>
    """, unsafe_allow_html=True)

else:

    st.success("✅ PDF uploaded successfully!")

    st.markdown("### 📄 File Information")

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "File Name",
            uploaded_file.name
        )

    with c2:
        st.metric(
            "File Size",
            f"{uploaded_file.size / 1024:.1f} KB"
        )

    st.divider()

    # Extract tables
    with st.spinner("🔍 Extracting student data from PDF..."):

        tables = extract_tables_from_pdf(uploaded_file)

    # -----------------------------
    # RESULTS
    # -----------------------------

    if len(tables) == 0:

        st.error(
            "❌ No table could be detected in this PDF."
        )

        st.info(
            "The PDF may be scanned/image-based. "
            "OCR support will be added in the next stage."
        )

    else:

        st.success(
            f"✅ {len(tables)} table(s) detected!"
        )

        st.divider()

        st.markdown("### 📊 Detected Student Data")

        for i, table_info in enumerate(tables):

            st.markdown(
                f"#### Table {i + 1} — Page {table_info['page']}"
            )

            df = table_info["data"]

            st.dataframe(
                df,
                use_container_width=True
            )

            st.caption(
                f"{len(df)} students/rows detected"
            )


            # -----------------------------
# AUTOMATIC COLUMN UNDERSTANDING
# -----------------------------

            st.markdown("### 🧠 Automatic Column Understanding")

            column_mapping = map_columns(df)

            scored_df = calculate_support_score(
    df,
    column_mapping
)

            st.divider()

st.markdown("### 🎯 Support Allocation")

support_percentage = st.slider(
    "Select support capacity (%)",
    min_value=5,
    max_value=50,
    value=20,
    step=5
)

st.info(
    f"Admin selected {support_percentage}% of students for additional support."
)
mapping_df = pd.DataFrame(
              column_mapping.items(),
              columns=["Original Column", "Detected Meaning"]
)
st.dataframe(
              mapping_df,
              use_container_width=True
)

st.divider()
st.markdown('### Data Detection Status')



st.divider()

st.markdown("### 🎯 Support Allocation")

support_percentage = st.slider(
    "Select the percentage of students who can receive additional support",
    min_value=5,
    max_value=50,
    value=20,
    step=5
)

st.info(
    f"Admin has selected {support_percentage}% support capacity."
)
total_students = len(scored_df)

students_to_select = max(
    1,
    int(np.ceil(total_students * support_percentage / 100))
)

priority_df = scored_df.sort_values(
    by="support_score",
    ascending=False
).reset_index(drop=True)

priority_df["Priority Rank"] = priority_df.index + 1

selected_students = priority_df.head(
    students_to_select
)

st.markdown("### 🚨 Priority Support List")

st.write(
    f"Selected {students_to_select} students "
    f"from {total_students} total students "
    f"({support_percentage}%)."
)

display_columns = []

for column, category in column_mapping.items():
    if category in ["student_id", "student_name"]:
        display_columns.append(column)

display_columns += [
    "support_score",
    "Priority Rank",
    "support_reasons"
]

st.dataframe(
    selected_students[display_columns].style.format({
        "support_score": "{:.2f}"
    }),
    use_container_width=True
)

