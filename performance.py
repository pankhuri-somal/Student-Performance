# =========================================================
# performance.py
# =========================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from database import create_tables, execute_query
from utils import calculate_cgpa, predict_status


# =========================================================
# DATABASE
# =========================================================

create_tables()


# =========================================================
# DEFAULT ADMIN
# =========================================================

admin = execute_query(
    "SELECT * FROM User_Login WHERE USERNAME=?",
    ("admin",),
    fetch=True
)

if not admin:

    execute_query(
        "INSERT INTO User_Login VALUES (?,?,?)",
        ("admin", "admin123", "admin")
    )


# =========================================================
# SESSION STATE
# =========================================================

if "login_status" not in st.session_state:
    st.session_state.login_status = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if "signup_success" not in st.session_state:
    st.session_state.signup_success = False


# =========================================================
# FUNCTIONS
# =========================================================

def login_user(username, password):

    data = execute_query(
        "SELECT * FROM User_Login WHERE USERNAME=? AND PASSWORD=?",
        (username, password),
        fetch=True
    )

    return data[0] if data else None


def add_user(username, password):

    user = execute_query(
        "SELECT * FROM User_Login WHERE USERNAME=?",
        (username,),
        fetch=True
    )

    if user:
        return False

    execute_query(
        "INSERT INTO User_Login VALUES (?,?,?)",
        (username, password, "student")
    )

    return True


def update_password(username, new_password):

    execute_query(
        "UPDATE User_Login SET PASSWORD=? WHERE USERNAME=?",
        (new_password, username)
    )


def get_student(username):

    data = execute_query(
        "SELECT * FROM Student_Details WHERE USERNAME=?",
        (username,),
        fetch=True
    )

    return data[0] if data else None


# =========================================================
# SAVE STUDENT DETAILS
# =========================================================

def save_student(
    username,
    name,
    gender,
    course,
    age,
    contact,
    email
):

    name = name.upper()
    gender = gender.upper()
    course = course.upper()
    email = email.lower()

    student = get_student(username)

    if student:

        execute_query("""
        UPDATE Student_Details
        SET
        STUDENT_NAME=?,
        GENDER=?,
        COURSE=?,
        AGE=?,
        CONTACT_NUMBER=?,
        EMAIL_ID=?
        WHERE USERNAME=?
        """,
        (
            name,
            gender,
            course,
            age,
            contact,
            email,
            username
        ))

    else:

        execute_query("""
        INSERT INTO Student_Details
        VALUES (?,?,?,?,?,?,?)
        """,
        (
            username,
            name,
            gender,
            course,
            age,
            contact,
            email
        ))


# =========================================================
# SAVE MARKS
# =========================================================

def save_marks(
    username,
    semester,
    m1,
    m2,
    m3,
    m4,
    m5,
    backlogs,
    attendance,
    cgpa,
    predicted_status
):

    execute_query("""
    INSERT INTO Marks
    VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """,
    (
        username,
        semester,
        m1,
        m2,
        m3,
        m4,
        m5,
        backlogs,
        attendance,
        cgpa,
        predicted_status
    ))


# =========================================================
# GET HISTORY
# =========================================================

def get_history(username):

    data = execute_query(
        "SELECT * FROM Marks WHERE USERNAME=? ORDER BY SEMESTER",
        (username,),
        fetch=True
    )

    return data


# =========================================================
# TITLE
# =========================================================

st.title("🎓 Machine Learning Based Academic Performance Analysis System")


menu = ["Login", "Signup", "Forgot Password"]


# =========================================================
# MENU
# =========================================================

if st.session_state.signup_success:

    choice = "Login"
    st.session_state.signup_success = False

else:

    choice = st.sidebar.selectbox("Menu", menu)


# =========================================================
# LOGIN
# =========================================================

if choice == "Login":

    if not st.session_state.login_status:

        st.subheader("Login")

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            result = login_user(
                username,
                password
            )

            if result:

                st.session_state.login_status = True
                st.session_state.username = result[0]
                st.session_state.role = result[2]

                st.success("Login Successful")

                st.rerun()

            else:

                st.error("Invalid Username or Password")

    else:

        st.sidebar.success(
            f"Logged in as {st.session_state.username}"
        )

        st.sidebar.write(
            f"Role : {st.session_state.role}"
        )

        if st.sidebar.button("Logout"):

            st.session_state.login_status = False
            st.session_state.username = ""
            st.session_state.role = ""

            st.rerun()


        # =====================================================
        # ADMIN MENU
        # =====================================================

        if st.session_state.role == "admin":

            page = st.sidebar.selectbox(
                "Select Page",
                ["Admin Dashboard"]
            )


        # =====================================================
        # STUDENT MENU
        # =====================================================

        else:

            page = st.sidebar.selectbox(
                "Select Page",
                [
                    "Student Details",
                    "Academic Details",
                    "Dashboard"
                ]
            )


        # =====================================================
        # STUDENT DETAILS
        # =====================================================

        if page == "Student Details":

            st.subheader("Student Details")

            student = get_student(
                st.session_state.username
            )

            if student:

                name_default = student[1]
                gender_default = student[2]
                course_default = student[3]
                age_default = student[4]
                contact_default = student[5]
                email_default = student[6]

            else:

                name_default = ""
                gender_default = "MALE"
                course_default = ""
                age_default = ""
                contact_default = ""
                email_default = ""

            name = st.text_input(
                "Student Name",
                value=name_default
            )

            gender = st.selectbox(
                "Gender",
                ["MALE", "FEMALE"],
                index=0 if gender_default == "MALE" else 1
            )

            course = st.text_input(
                "Course",
                value=course_default
            )

            age = st.text_input(
                "Age",
                value=age_default
            )

            contact = st.text_input(
                "Contact Number",
                value=contact_default
            )

            email = st.text_input(
                "Email ID",
                value=email_default
            )

            if st.button("Save Student Details"):

                save_student(
                    st.session_state.username,
                    name,
                    gender,
                    course,
                    age,
                    contact,
                    email
                )

                st.success(
                    "Student Details Saved Successfully"
                )


        # =====================================================
        # ACADEMIC DETAILS
        # =====================================================

        elif page == "Academic Details":

            st.subheader("Academic Details")

            semester = st.number_input(
                "Semester",
                min_value=1,
                max_value=8
            )

            sub1 = st.text_input("Subject 1 Marks")
            sub2 = st.text_input("Subject 2 Marks")
            sub3 = st.text_input("Subject 3 Marks")
            sub4 = st.text_input("Subject 4 Marks")
            sub5 = st.text_input("Subject 5 Marks")

            backlogs = st.text_input("Backlogs")

            attendance = st.text_input(
                "Attendance %"
            )

            if st.button("Calculate CGPA"):

                marks = [
                    int(sub1),
                    int(sub2),
                    int(sub3),
                    int(sub4),
                    int(sub5)
                ]

                cgpa = calculate_cgpa(marks)

                status = predict_status(
                    cgpa,
                    int(backlogs),
                    int(attendance)
                )

                save_marks(
                    st.session_state.username,
                    int(semester),
                    int(sub1),
                    int(sub2),
                    int(sub3),
                    int(sub4),
                    int(sub5),
                    int(backlogs),
                    int(attendance),
                    cgpa,
                    status
                )

                st.success(f"CGPA = {cgpa}")

                st.info(
                    f"Predicted Status = {status}"
                )


        # =====================================================
        # STUDENT DASHBOARD
        # =====================================================

        elif page == "Dashboard":

            st.subheader("🎓 Student Dashboard")

            history = get_history(
                st.session_state.username
            )

            if history:

                df = pd.DataFrame(history, columns=[
                    "Username",
                    "Semester",
                    "Sub1",
                    "Sub2",
                    "Sub3",
                    "Sub4",
                    "Sub5",
                    "Backlogs",
                    "Attendance",
                    "CGPA",
                    "Status"
                ])

                st.dataframe(df)

                latest_cgpa = df.iloc[-1]["CGPA"]

                total_backlogs = df["Backlogs"].sum()

                highest_cgpa = df["CGPA"].max()

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Latest CGPA", latest_cgpa)

                with col2:
                    st.metric("Highest CGPA", highest_cgpa)

                with col3:
                    st.metric("Total Backlogs", total_backlogs)

                if len(df) == 1:

                    st.subheader("📊 Subject Wise Marks")

                    subjects = [
                        "Sub1",
                        "Sub2",
                        "Sub3",
                        "Sub4",
                        "Sub5"
                    ]

                    marks = df.iloc[0][subjects]

                    fig, ax = plt.subplots()

                    ax.bar(subjects, marks)

                    ax.set_xlabel("Subjects")
                    ax.set_ylabel("Marks")
                    ax.set_title("Subject Wise Performance")

                    st.pyplot(fig)

                else:

                    st.subheader("📈 CGPA Trend")

                    fig, ax = plt.subplots()

                    ax.plot(
                        df["Semester"],
                        df["CGPA"],
                        marker="o"
                    )

                    ax.set_xticks(df["Semester"])

                    ax.set_xlabel("Semester")
                    ax.set_ylabel("CGPA")
                    ax.set_title("Semester Wise CGPA")

                    st.pyplot(fig)

                    st.subheader("📉 Backlog Analysis")

                    fig2, ax2 = plt.subplots()

                    ax2.bar(
                        df["Semester"],
                        df["Backlogs"]
                    )

                    ax2.set_xticks(df["Semester"])

                    ax2.set_xlabel("Semester")
                    ax2.set_ylabel("Backlogs")
                    ax2.set_title("Semester Wise Backlogs")

                    st.pyplot(fig2)

            else:

                st.info("No academic data found")


        # =====================================================
        # ADMIN DASHBOARD
        # =====================================================

        elif page == "Admin Dashboard":

            st.subheader("Admin Dashboard")

            students = execute_query("""

            SELECT DISTINCT

            Student_Details.USERNAME,
            STUDENT_NAME,
            COURSE,
            EMAIL_ID

            FROM Student_Details

            """, fetch=True)

            if students:

                student_df = pd.DataFrame(
                    students,
                    columns=[
                        "Username",
                        "Student Name",
                        "Course",
                        "Email"
                    ]
                )

                search = st.text_input(
                    "Search Student (Username / Name / Course)"
                )

                if search:

                    student_df = student_df[

                        student_df["Username"]
                        .str.contains(search, case=False)

                        |

                        student_df["Student Name"]
                        .str.contains(search, case=False)

                        |

                        student_df["Course"]
                        .str.contains(search, case=False)

                    ]

                st.subheader("All Students")

                st.dataframe(student_df)

                filtered_usernames = student_df[
                    "Username"
                ].tolist()

                if filtered_usernames:

                    placeholders = ",".join(
                        ["?"] * len(filtered_usernames)
                    )

                    query = f"""
                    SELECT * FROM Marks
                    WHERE USERNAME IN ({placeholders})
                    """

                    all_marks = execute_query(
                        query,
                        tuple(filtered_usernames),
                        fetch=True
                    )

                else:

                    all_marks = []

                if all_marks:

                    all_marks_df = pd.DataFrame(
                        all_marks,
                        columns=[
                            "Username",
                            "Semester",
                            "Sub1",
                            "Sub2",
                            "Sub3",
                            "Sub4",
                            "Sub5",
                            "Backlogs",
                            "Attendance",
                            "CGPA",
                            "Status"
                        ]
                    )

                    avg_cgpa = round(
                        all_marks_df["CGPA"].mean(),
                        2
                    )

                    max_cgpa = round(
                        all_marks_df["CGPA"].max(),
                        2
                    )

                    total_backlogs = (
                        all_marks_df["Backlogs"]
                        .sum()
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Total Students",
                            len(student_df)
                        )

                    with col2:
                        st.metric(
                            "Average CGPA",
                            avg_cgpa
                        )

                    with col3:
                        st.metric(
                            "Highest CGPA",
                            max_cgpa
                        )

                    st.metric(
                        "Total Backlogs",
                        total_backlogs
                    )

                    # TOPPER
                    st.subheader("🏆 Top Performers")

                    topper_df = all_marks_df.groupby(
                        "Username",
                        as_index=False
                    )["CGPA"].max()

                    topper_df = topper_df.sort_values(
                        by="CGPA",
                        ascending=False
                    ).head(5)

                    st.dataframe(topper_df)

                    # CGPA CHART
                    st.subheader(
                        "📈 Semester Wise Average CGPA"
                    )

                    cgpa_chart = all_marks_df.groupby(
                        "Semester",
                        as_index=False
                    )["CGPA"].mean()

                    fig_chart, ax_chart = plt.subplots()

                    ax_chart.plot(
                        cgpa_chart["Semester"],
                        cgpa_chart["CGPA"],
                        marker="o"
                    )

                    ax_chart.set_xticks(
                        cgpa_chart["Semester"]
                    )

                    ax_chart.set_xlabel("Semester")
                    ax_chart.set_ylabel("Average CGPA")
                    ax_chart.set_title(
                        "Semester Wise Average CGPA"
                    )

                    st.pyplot(fig_chart)

                    # BACKLOG BAR CHART
                    st.subheader(
                        "📊 Semester Wise Students With Backlogs"
                    )

                    backlog_students = all_marks_df[
                        all_marks_df["Backlogs"] > 0
                    ]

                    semester_backlogs = backlog_students.groupby(
                        "Semester"
                    )["Username"].nunique()

                    fig_backlog, ax_backlog = plt.subplots()

                    ax_backlog.bar(
                        semester_backlogs.index,
                        semester_backlogs.values
                    )

                    ax_backlog.set_xticks(
                        semester_backlogs.index
                    )

                    # SIMPLE Y AXIS GAP OF 1
                    max_value = int(
                        semester_backlogs.values.max()
                    )

                    ax_backlog.set_yticks(
                        range(0, max_value + 1, 1)
                    )

                    ax_backlog.set_xlabel(
                        "Semester"
                    )

                    ax_backlog.set_ylabel(
                        "No. of Students With Backlogs"
                    )

                    ax_backlog.set_title(
                        "Semester Wise Backlog Students"
                    )

                    st.pyplot(fig_backlog)

            else:

                st.info(
                    "No student data available"
                )


# =========================================================
# SIGNUP
# =========================================================

elif choice == "Signup":

    st.subheader("Create Account")

    new_user = st.text_input(
        "Create Username"
    )

    new_pass = st.text_input(
        "Create Password",
        type="password"
    )

    confirm_pass = st.text_input(
        "Confirm Password",
        type="password"
    )

    if st.button("Save Account"):

        if new_pass != confirm_pass:

            st.error(
                "Passwords do not match"
            )

        else:

            if add_user(
                new_user,
                new_pass
            ):

                st.success(
                    "Account Created Successfully"
                )

                st.session_state.signup_success = True

                st.rerun()

            else:

                st.error(
                    "Username already exists"
                )


# =========================================================
# FORGOT PASSWORD
# =========================================================

elif choice == "Forgot Password":

    st.subheader("Reset Password")

    username = st.text_input(
        "Enter Username"
    )

    new_password = st.text_input(
        "New Password",
        type="password"
    )

    if st.button("Reset Password"):

        update_password(
            username,
            new_password
        )

        st.success(
            "Password Updated Successfully"
        )
