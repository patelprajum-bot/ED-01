import numpy as np
import streamlit as st
import pandas as pd
import pdfplumber
import io

from data_mapper import map_columns
from scoring_engine import calculate_support_score


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ED-01 | Fair Student Support",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

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


# ============================================================
# HEADER
# ============================================================

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


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Admin Control Panel")

uploaded_file = st.sidebar.file_uploader(
    "📄 Upload Student PDF",
    type=["pdf"]
)


# ============================================================
# PDF TABLE EXTRACTION
# ============================================================

def extract_tables_from_pdf(pdf_file):

    tables = []

    pdf_bytes = pdf_file.getvalue()

    with pdfplumber.open(
        io.BytesIO(pdf_bytes)
    ) as pdf:

        for page_number, page in enumerate(
            pdf.pages,
            start=1
        ):

            extracted_tables = page.extract_tables()

            for table in extracted_tables:

                if table and len(table) > 1:

                    header = table[0]
                    data = table[1:]

                    df = pd.DataFrame(
                        data,
                        columns=header
                    )

                    # Remove empty rows
                    df = df.dropna(
                        how="all"
                    )

                    # Remove empty columns
                    df = df.dropna(
                        axis=1,
                        how="all"
                    )

                    if not df.empty:

                        tables.append({
                            "page": page_number,
                            "data": df
                        })

    return tables


# ============================================================
# MAIN APP
# ============================================================

if uploaded_file is None:

    st.markdown("""
    <div class="info-card">

    ### 📄 Upload Student Data

    Upload a student-performance PDF from:

    - 🏫 School
    - 🎓 College
    - 🏛️ University

    The system will extract student data from all pages
    and generate one combined priority-support list.

    </div>
    """, unsafe_allow_html=True)


else:

    st.success(
        "✅ PDF uploaded successfully!"
    )


    # ========================================================
    # FILE INFORMATION
    # ========================================================

    st.markdown(
        "### 📄 File Information"
    )

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


    # ========================================================
    # EXTRACT TABLES
    # ========================================================

    with st.spinner(
        "🔍 Extracting student data from all PDF pages..."
    ):

        tables = extract_tables_from_pdf(
            uploaded_file
        )


    # ========================================================
    # NO TABLE FOUND
    # ========================================================

    if len(tables) == 0:

        st.error(
            "❌ No table could be detected in this PDF."
        )

        st.info(
            "The PDF may be scanned/image-based. "
            "OCR support will be added later."
        )


    # ========================================================
    # TABLES FOUND
    # ========================================================

    else:

        st.success(
            f"✅ {len(tables)} table(s) detected across the PDF."
        )


        # ====================================================
        # COMBINE ALL TABLES FROM ALL PAGES
        # ====================================================

        all_dataframes = []

        for table_info in tables:

            page_df = table_info["data"].copy()

            # Remove empty rows
            page_df = page_df.dropna(
                how="all"
            )

            # Remove empty columns
            page_df = page_df.dropna(
                axis=1,
                how="all"
            )

            if not page_df.empty:

                all_dataframes.append(
                    page_df
                )


        # ====================================================
        # CHECK DATA
        # ====================================================

        if len(all_dataframes) == 0:

            st.error(
                "❌ No usable student data was found."
            )

        else:

            # =================================================
            # COMBINE ALL STUDENTS
            # =================================================

            combined_df = pd.concat(
                all_dataframes,
                ignore_index=True
            )


            # =================================================
            # REMOVE COMPLETELY EMPTY ROWS
            # =================================================

            combined_df = combined_df.dropna(
                how="all"
            ).reset_index(
                drop=True
            )


            # =================================================
            # TOTAL STUDENTS
            # =================================================

            total_students = len(
                combined_df
            )


            st.success(
                f"✅ {total_students} student records "
                "combined from all PDF pages."
            )


            # =================================================
            # AUTOMATIC COLUMN UNDERSTANDING
            # =================================================

            # st.markdown(
            #     "### 🧠 Automatic Column Understanding"
            # )

            column_mapping = map_columns(
                combined_df
            )


            # mapping_df = pd.DataFrame(
            #     column_mapping.items(),
            #     columns=[
            #         "Original Column",
            #         "Detected Meaning"
            #     ]
            # )


            # st.dataframe(
            #     mapping_df,
            #     use_container_width=True,
            #     hide_index=True
            # )


            # =================================================
            # SUPPORT SCORE
            # =================================================

            with st.spinner(
                "🧮 Calculating support scores for all students..."
            ):

                scored_df = calculate_support_score(
                    combined_df,
                    column_mapping
                )


            # =================================================
            # SUPPORT ALLOCATION
            # =================================================

            st.divider()

            st.markdown(
                "### 🎯 Support Allocation"
            )


            support_percentage = st.slider(
                "Select support capacity (%)",
                min_value=1,
                max_value=99,
                value=5,
                step=1,
                key="support_percentage"
            )


            st.info(
                f"Admin selected {support_percentage}% "
                "of all students for additional support."
            )


            # =================================================
            # NUMBER OF STUDENTS TO SELECT
            # =================================================

            students_to_select = max(
                1,
                int(
                    np.ceil(
                        total_students
                        * support_percentage
                        / 100
                    )
                )
            )


            # =================================================
            # PRIORITY RANKING
            # =================================================

            priority_df = scored_df.sort_values(
                by="support_score",
                ascending=False
            ).reset_index(
                drop=True
            )


            priority_df[
                "Priority Rank"
            ] = priority_df.index + 1


            # =================================================
            # SELECT TOP PRIORITY STUDENTS
            # =================================================

            selected_students = priority_df.head(
                students_to_select
            ).copy()


            # =================================================
            # FIND STUDENT ID
            # =================================================

            student_id_columns = [
                column
                for column, category
                in column_mapping.items()
                if category == "student_id"
            ]


            # =================================================
            # FIND STUDENT NAME
            # =================================================

            student_name_columns = [
                column
                for column, category
                in column_mapping.items()
                if category == "student_name"
            ]


            # =================================================
            # CREATE FINAL PRIORITY LIST
            # =================================================

            final_priority_list = pd.DataFrame()


            # -------------------------------------------------
            # SERIAL NUMBER
            # -------------------------------------------------

            final_priority_list[
                "Serial No."
            ] = range(
                1,
                len(selected_students) + 1
            )


            # -------------------------------------------------
            # ROLL NO / STUDENT ID
            # -------------------------------------------------

            if student_id_columns:

                student_id_column = (
                    student_id_columns[0]
                )

                final_priority_list[
                    "Roll No. / Student ID"
                ] = selected_students[
                    student_id_column
                ].values

            else:

                final_priority_list[
                    "Roll No. / Student ID"
                ] = [
                    "Not available"
                ] * len(
                    selected_students
                )


            # -------------------------------------------------
            # STUDENT NAME
            # -------------------------------------------------

            if student_name_columns:

                student_name_column = (
                    student_name_columns[0]
                )

                final_priority_list[
                    "Student Name"
                ] = selected_students[
                    student_name_column
                ].values

            else:

                final_priority_list[
                    "Student Name"
                ] = [
                    "Not available"
                ] * len(
                    selected_students
                )


            # -------------------------------------------------
            # SUPPORT SCORE
            # -------------------------------------------------

            final_priority_list[
                "Support Score"
            ] = selected_students[
                "support_score"
            ].values


            # -------------------------------------------------
            # PRIORITY RANK
            # -------------------------------------------------

            final_priority_list[
                "Priority Rank"
            ] = selected_students[
                "Priority Rank"
            ].values


            # -------------------------------------------------
            # REASON
            # -------------------------------------------------

            final_priority_list[
                "Reason"
            ] = selected_students[
                "support_reasons"
            ].values


            # =================================================
            # FINAL OUTPUT
            # =================================================

            st.divider()

            st.markdown(
                "### 🚨 Final Priority Support List"
            )


            st.write(
                f"Selected **{students_to_select} students** "
                f"from **{total_students} total students** "
                f"across all PDF pages."
            )


            st.dataframe(
                final_priority_list.style.format({
                    "Support Score": "{:.2f}"
                }),
                use_container_width=True,
                hide_index=True
            )


            # =================================================
            # HUMAN REVIEW NOTICE
            # =================================================

            st.warning(
                "⚠️ This priority list is a decision-support "
                "recommendation. Final student-support decisions "
                "should be reviewed by an authorized educator "
                "or administrator."
            )