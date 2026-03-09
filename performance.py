import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from database import create_tables, execute_query
from utils import calculate_cgpa, predict_status

# ---------------- SETUP ---------------- #
create_tables()

if "login_status" not in st.session_state:
    st.session_state.login_status = False

if "cgpa_history" not in st.session_state:
    st.session_state.cgpa_history = []

# ---------------- LOGIN FUNCTIONS ---------------- #
def login_user(username, password):
    data = execute_query(
        "SELECT * FROM User_Login WHERE USERNAME=? AND PASSWORD=?",
        (username, password),
        fetch=True
    )
    return data[0] if data else None


def add_user(username, password):
    user = execute_query("SELECT * FROM User_Login WHERE USERNAME=?", (username,), fetch=True)

    if user:
        return False

    execute_query("INSERT INTO User_Login VALUES (?,?,?)", (username, password, "student"))
    return True


def reset_password(username, new_password):
    user = execute_query("SELECT * FROM User_Login WHERE USERNAME=?", (username,), fetch=True)

    if user:
        execute_query("UPDATE User_Login SET PASSWORD=? WHERE USERNAME=?", (new_password, username))
        return True

    return False


# ---------------- STUDENT DATA ---------------- #
def add_student(name, gender, course, semester, age, contact, email):

    execute_query("""
        INSERT INTO Student_Details
        (STUDENT_NAME,GENDER,COURSE,SEMESTER,AGE,CONTACT_NUMBER,EMAIL_ID)
        VALUES (?,?,?,?,?,?,?)
    """, (name, gender, course, semester, age, contact, email))


def save_marks(name, m1, m2, m3, m4, m5, backlogs, attendance, cgpa, predicted_status):

    execute_query("""
        INSERT INTO Marks
        (STUDENT_NAME,SUBJECT1,SUBJECT2,SUBJECT3,SUBJECT4,SUBJECT5,BACKLOGS,ATTENDANCE,CGPA,PREDICTED_STATUS)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (name, m1, m2, m3, m4, m5, backlogs, attendance, cgpa, predicted_status))


# ---------------- STREAMLIT UI ---------------- #
st.title("🎓 Student CGPA Management System")

menu = ["Login", "Signup", "Forgot Password"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- LOGIN ---------------- #
if choice == "Login":

    if not st.session_state.login_status:

        st.subheader("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            result = login_user(username, password)

            if result:
                st.session_state.login_status = True
                st.session_state.cgpa_history = []  # clear previous data

                st.success("Login Successful")
                st.rerun()

            else:
                st.error("Incorrect Username or Password")

    else:

        st.sidebar.success("Logged In")

        if st.sidebar.button("Logout"):

            st.session_state.login_status = False
            st.session_state.cgpa_history = []
            st.rerun()

        page = st.sidebar.selectbox(
            "Select Page",
            ["Student Details", "Academic Details", "Dashboard"]
        )

        # ---------------- STUDENT DETAILS ---------------- #
        if page == "Student Details":

            st.subheader("Enter Student Details")

            name = st.text_input("Name")
            gender = st.selectbox("Gender", ["Male", "Female"])
            course = st.text_input("Course")
            semester = st.text_input("Semester")
            age = st.text_input("Age")
            contact = st.text_input("Contact")
            email = st.text_input("Email")

            if st.button("Save Student"):

                if not all([name, gender, course, semester, age, contact, email]):
                    st.error("Please fill all student fields")

                else:
                    add_student(name, gender, course, semester, age, contact, email)
                    st.success("Student Details Saved")

        # ---------------- ACADEMIC DETAILS ---------------- #
        elif page == "Academic Details":

            st.subheader("Enter Academic Details")

            name = st.text_input("Student Name")

            sub1 = st.text_input("Subject 1 Marks")
            sub2 = st.text_input("Subject 2 Marks")
            sub3 = st.text_input("Subject 3 Marks")
            sub4 = st.text_input("Subject 4 Marks")
            sub5 = st.text_input("Subject 5 Marks")

            backlogs = st.text_input("Number of Backlogs")
            attendance = st.text_input("Attendance Percentage")

            if st.button("Calculate CGPA"):

                if not all([name, sub1, sub2, sub3, sub4, sub5, backlogs, attendance]):
                    st.error("Please fill all fields before calculating CGPA")

                else:

                    try:

                        marks = [int(sub1), int(sub2), int(sub3), int(sub4), int(sub5)]

                        backlogs_int = int(backlogs)
                        attendance_float = float(attendance)

                        cgpa = calculate_cgpa(marks)

                        predicted_status = predict_status(
                            cgpa,
                            backlogs_int,
                            attendance_float
                        )

                        save_marks(
                            name,
                            *marks,
                            backlogs_int,
                            attendance_float,
                            cgpa,
                            predicted_status
                        )

                        # Store for dashboard comparison
                        st.session_state.cgpa_history.append({
                            "Semester": len(st.session_state.cgpa_history) + 1,
                            "Name": name,
                            "CGPA": cgpa,
                            "Backlogs": backlogs_int,
                            "Predicted_Status": predicted_status
                        })

                        st.success(f"CGPA = {cgpa}")
                        st.info(f"Predicted Status = {predicted_status}")

                        if backlogs_int > 0:
                            st.warning(f"Backlogs: {backlogs_int}")

                        if cgpa >= 5 and backlogs_int == 0:
                            st.success("Status: PASS")
                        else:
                            st.error("Status: FAIL")

                    except ValueError:
                        st.error("Please enter valid numeric values")

        # ---------------- DASHBOARD ---------------- #
        elif page == "Dashboard":

            st.subheader("📊 Student CGPA Analytics Dashboard")

            if len(st.session_state.cgpa_history) == 0:

                st.info("No CGPA data yet. Please calculate CGPA first.")

            else:

                df = pd.DataFrame(st.session_state.cgpa_history)

                # ---------------- Predicted Status Table ---------------- #
                st.subheader("Predicted Academic Status")

                st.dataframe(df[[
                    "Semester",
                    "Name",
                    "CGPA",
                    "Backlogs",
                    "Predicted_Status"
                ]])

                # ---------------- Average CGPA ---------------- #
                st.metric("Average CGPA", round(df["CGPA"].mean(), 2))

                # ---------------- CGPA Line Chart ---------------- #
                st.subheader("CGPA Trend Across Semesters")

                fig1, ax1 = plt.subplots()

                ax1.plot(df["Semester"], df["CGPA"], marker="o")

                ax1.set_xlabel("Semester")
                ax1.set_ylabel("CGPA")
                ax1.set_title("CGPA Progress")

                st.pyplot(fig1)

                # ---------------- Backlogs Count Chart ---------------- #
                st.subheader("Backlogs Count")

                fig2, ax2 = plt.subplots()

                df["Backlogs"].value_counts().plot(kind="bar", ax=ax2)

                ax2.set_xlabel("BACKLOGS")
                ax2.set_ylabel("COUNT")
                ax2.set_title("Backlogs Count")

                st.pyplot(fig2)

# ---------------- SIGNUP ---------------- #
elif choice == "Signup":

    st.subheader("Create Account")

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Signup"):

        if add_user(new_user, new_pass):
            st.success("Account Created Successfully")

        else:
            st.warning("Username already exists")

# ---------------- FORGOT PASSWORD ---------------- #
elif choice == "Forgot Password":

    st.subheader("Reset Password")

    user = st.text_input("Enter Username")
    new_password = st.text_input("Enter New Password", type="password")

    if st.button("Reset"):

        if reset_password(user, new_password):
            st.success("Password Reset Successful")

        else:
            st.error("Username not found")
