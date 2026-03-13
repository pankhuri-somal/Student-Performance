import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from database import create_tables, execute_query
from utils import calculate_cgpa, predict_status

create_tables()

# ---------------- SESSION STATE ---------------- #

if "login_status" not in st.session_state:
    st.session_state.login_status = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "signup_success" not in st.session_state:
    st.session_state.signup_success = False

# remember login
if "saved_username" not in st.session_state:
    st.session_state.saved_username = ""

if "saved_password" not in st.session_state:
    st.session_state.saved_password = ""


# ---------------- LOGIN FUNCTIONS ---------------- #

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


# ---------------- FORGOT PASSWORD ---------------- #

def update_password(username, new_password):

    execute_query(
        "UPDATE User_Login SET PASSWORD=? WHERE USERNAME=?",
        (new_password, username)
    )


# ---------------- GET STUDENT DETAILS ---------------- #

def get_student(username):

    data = execute_query(
        "SELECT * FROM Student_Details WHERE USERNAME=?",
        (username,),
        fetch=True
    )

    return data[0] if data else None


# ---------------- SAVE / UPDATE STUDENT DETAILS ---------------- #

def save_student(username, name, gender, course, age, contact, email):

    student = get_student(username)

    if student:
        execute_query("""
        UPDATE Student_Details
        SET STUDENT_NAME=?, GENDER=?, COURSE=?, AGE=?, CONTACT_NUMBER=?, EMAIL_ID=?
        WHERE USERNAME=?
        """,(name,gender,course,age,contact,email,username))
    else:
        execute_query("""
        INSERT INTO Student_Details
        (USERNAME,STUDENT_NAME,GENDER,COURSE,AGE,CONTACT_NUMBER,EMAIL_ID)
        VALUES (?,?,?,?,?,?,?)
        """,(username,name,gender,course,age,contact,email))


# ---------------- SAVE MARKS ---------------- #

def save_marks(username, semester, m1, m2, m3, m4, m5, backlogs, attendance, cgpa, predicted_status):

    execute_query("""
    INSERT INTO Marks
    VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """,(username,semester,m1,m2,m3,m4,m5,backlogs,attendance,cgpa,predicted_status))


# ---------------- GET HISTORY ---------------- #

def get_history(username):

    data = execute_query(
        "SELECT * FROM Marks WHERE USERNAME=? ORDER BY SEMESTER",
        (username,),
        fetch=True
    )

    return data


# ---------------- STREAMLIT UI ---------------- #

st.title("🎓 Student CGPA Management System")

menu = ["Login", "Signup", "Forgot Password"]

if st.session_state.signup_success:
    choice = "Login"
    st.session_state.signup_success = False
else:
    choice = st.sidebar.selectbox("Menu", menu)


# ---------------- LOGIN ---------------- #

if choice == "Login":

    if not st.session_state.login_status:

        st.subheader("Login")

        username = st.text_input("Username", value=st.session_state.saved_username)
        password = st.text_input("Password", type="password", value=st.session_state.saved_password)

        remember = st.checkbox("Remember Username & Password")

        if st.button("Login"):

            result = login_user(username, password)

            if result:

                st.session_state.login_status = True
                st.session_state.username = username

                # save credentials
                if remember:
                    st.session_state.saved_username = username
                    st.session_state.saved_password = password

                st.success("Login Successful")
                st.rerun()

            else:
                st.error("Invalid Login")

    else:

        st.sidebar.success("Logged in as " + st.session_state.username)

        if st.sidebar.button("Logout"):
            st.session_state.login_status = False
            st.rerun()

        page = st.sidebar.selectbox(
            "Select Page",
            ["Student Details", "Academic Details", "Dashboard"]
        )


        # ---------------- STUDENT DETAILS ---------------- #

        if page == "Student Details":

            st.subheader("Student Details")

            student = get_student(st.session_state.username)

            if student:
                name_default = student[1]
                gender_default = student[2]
                course_default = student[3]
                age_default = student[4]
                contact_default = student[5]
                email_default = student[6]
            else:
                name_default = ""
                gender_default = "Male"
                course_default = ""
                age_default = ""
                contact_default = ""
                email_default = ""

            name = st.text_input("Name", value=name_default)
            gender = st.selectbox(
                "Gender", ["Male","Female"],
                index=0 if gender_default=="Male" else 1
            )
            course = st.text_input("Course", value=course_default)
            age = st.text_input("Age", value=age_default)
            contact = st.text_input("Contact", value=contact_default)
            email = st.text_input("Email", value=email_default)

            if st.button("Save Student"):

                save_student(
                    st.session_state.username,
                    name,
                    gender,
                    course,
                    age,
                    contact,
                    email
                )

                st.success("Student Details Saved / Updated")


        # ---------------- ACADEMIC DETAILS ---------------- #

        elif page == "Academic Details":

            st.subheader("Enter Marks")

            semester = st.number_input("Semester",1,8)

            sub1 = st.text_input("Subject 1 Marks")
            sub2 = st.text_input("Subject 2 Marks")
            sub3 = st.text_input("Subject 3 Marks")
            sub4 = st.text_input("Subject 4 Marks")
            sub5 = st.text_input("Subject 5 Marks")

            backlogs = st.text_input("Backlogs")
            attendance = st.text_input("Attendance")

            if st.button("Calculate CGPA"):

                marks = [
                    int(sub1), int(sub2), int(sub3),
                    int(sub4), int(sub5)
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
                st.info(f"Predicted Status = {status}")


        # ---------------- DASHBOARD ---------------- #

        elif page == "Dashboard":

            st.subheader("Student Dashboard")

            history = get_history(st.session_state.username)

            if history:

                df = pd.DataFrame(history, columns=[
                    "Username","Semester",
                    "Sub1","Sub2","Sub3","Sub4","Sub5",
                    "Backlogs","Attendance","CGPA","Status"
                ])

                st.dataframe(df)

                if len(df) == 1:

                    st.subheader("Subject Wise Marks")

                    subjects = ["Sub1","Sub2","Sub3","Sub4","Sub5"]
                    marks = df.iloc[0][subjects]

                    fig, ax = plt.subplots()

                    ax.bar(subjects, marks)

                    ax.set_title("Subject Marks")
                    ax.set_ylabel("Marks")

                    st.pyplot(fig)

                else:

                    st.subheader("Semester CGPA Comparison")

                    fig, ax = plt.subplots()

                    ax.plot(df["Semester"], df["CGPA"], marker="o")

                    ax.set_xlabel("Semester")
                    ax.set_ylabel("CGPA")
                    ax.set_title("CGPA Trend")

                    ax.set_xticks(df["Semester"])

                    st.pyplot(fig)


                    st.subheader("Backlog Comparison")

                    fig2, ax2 = plt.subplots()

                    ax2.bar(df["Semester"], df["Backlogs"])

                    ax2.set_xlabel("Semester")
                    ax2.set_ylabel("Backlogs")
                    ax2.set_title("Backlogs per Semester")

                    ax2.set_xticks(df["Semester"])
                    ax2.set_yticks(range(0, int(df["Backlogs"].max()) + 1))

                    st.pyplot(fig2)

            else:
                st.info("No academic data yet")


# ---------------- SIGNUP ---------------- #

elif choice == "Signup":

    st.subheader("Create Account")

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")
    confirm_pass = st.text_input("Confirm Password", type="password")

    if st.button("Save Account"):

        if new_pass != confirm_pass:
            st.error("Passwords do not match")

        else:

            if add_user(new_user,new_pass):

                st.success("Account Created Successfully")
                st.session_state.signup_success = True
                st.rerun()

            else:
                st.error("Username already exists")


# ---------------- FORGOT PASSWORD ---------------- #

elif choice == "Forgot Password":

    st.subheader("Reset Password")

    username = st.text_input("Enter Username")
    new_password = st.text_input("New Password", type="password")

    if st.button("Reset Password"):

        update_password(username, new_password)

        st.success("Password Updated Successfully")
