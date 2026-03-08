import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- DATABASE ---------------- #

def create_tables():

    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS User_Login(
    USERNAME TEXT PRIMARY KEY,
    PASSWORD TEXT,
    ROLE TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Student_Details(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    STUDENT_NAME TEXT,
    GENDER TEXT,
    COURSE TEXT,
    SEMESTER INTEGER,
    AGE INTEGER,
    CONTACT_NUMBER TEXT,
    EMAIL_ID TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Marks(
    STUDENT_NAME TEXT,
    SUBJECT1 INTEGER,
    SUBJECT2 INTEGER,
    SUBJECT3 INTEGER,
    SUBJECT4 INTEGER,
    SUBJECT5 INTEGER,
    BACKLOGS INTEGER,
    ATTENDANCE REAL,
    CGPA REAL
    )
    """)

    conn.commit()
    conn.close()


create_tables()

# ---------------- SESSION ---------------- #

if "login_status" not in st.session_state:
    st.session_state.login_status = False


# ---------------- LOGIN FUNCTIONS ---------------- #

def login_user(username,password):

    conn=sqlite3.connect("student.db")
    cursor=conn.cursor()

    cursor.execute(
        "SELECT * FROM User_Login WHERE USERNAME=? AND PASSWORD=?",
        (username,password)
    )

    data=cursor.fetchone()

    conn.close()

    return data


def add_user(username,password):

    conn=sqlite3.connect("student.db")
    cursor=conn.cursor()

    cursor.execute(
        "SELECT * FROM User_Login WHERE USERNAME=?",
        (username,)
    )

    user=cursor.fetchone()

    if user:
        return False

    cursor.execute(
        "INSERT INTO User_Login VALUES (?,?,?)",
        (username,password,"student")
    )

    conn.commit()
    conn.close()

    return True


def reset_password(username,new_password):

    conn=sqlite3.connect("student.db")
    cursor=conn.cursor()

    cursor.execute(
        "SELECT * FROM User_Login WHERE USERNAME=?",
        (username,)
    )

    user=cursor.fetchone()

    if user:

        cursor.execute(
            "UPDATE User_Login SET PASSWORD=? WHERE USERNAME=?",
            (new_password,username)
        )

        conn.commit()
        conn.close()
        return True

    conn.close()
    return False


# ---------------- STUDENT DATA ---------------- #

def add_student(name,gender,course,semester,age,contact,email):

    conn=sqlite3.connect("student.db")
    cursor=conn.cursor()

    cursor.execute("""
    INSERT INTO Student_Details
    (STUDENT_NAME,GENDER,COURSE,SEMESTER,AGE,CONTACT_NUMBER,EMAIL_ID)
    VALUES (?,?,?,?,?,?,?)
    """,(name,gender,course,semester,age,contact,email))

    conn.commit()
    conn.close()


# ---------------- MARKS ---------------- #

def save_marks(name,m1,m2,m3,m4,m5,backlogs,attendance,cgpa):

    conn=sqlite3.connect("student.db")
    cursor=conn.cursor()

    cursor.execute("""
    INSERT INTO Marks
    (STUDENT_NAME,SUBJECT1,SUBJECT2,SUBJECT3,SUBJECT4,SUBJECT5,BACKLOGS,ATTENDANCE,CGPA)
    VALUES (?,?,?,?,?,?,?,?,?)
    """,(name,m1,m2,m3,m4,m5,backlogs,attendance,cgpa))

    conn.commit()
    conn.close()


# ---------------- CGPA CALCULATION ---------------- #

def calculate_cgpa(marks):

    grade_points=[]

    for m in marks:

        if m>=90: grade_points.append(10)
        elif m>=80: grade_points.append(9)
        elif m>=70: grade_points.append(8)
        elif m>=60: grade_points.append(7)
        elif m>=50: grade_points.append(6)
        elif m>=40: grade_points.append(5)
        else: grade_points.append(0)

    return round(sum(grade_points)/len(grade_points),2)


# ---------------- LOAD DATA ---------------- #

def load_students():

    conn=sqlite3.connect("student.db")
    df=pd.read_sql_query("SELECT * FROM Student_Details",conn)
    conn.close()

    return df


def load_marks():

    conn=sqlite3.connect("student.db")
    df=pd.read_sql_query("SELECT * FROM Marks",conn)
    conn.close()

    return df


# ---------------- STREAMLIT UI ---------------- #

st.title("🎓 Student CGPA Management System")

menu=["Login","Signup","Forgot Password"]

choice=st.sidebar.selectbox("Menu",menu)


# ---------------- LOGIN ---------------- #

if choice=="Login":

    if not st.session_state.login_status:

        st.subheader("Login")

        username=st.text_input("Username")
        password=st.text_input("Password",type="password")

        if st.button("Login"):

            result=login_user(username,password)

            if result:

                st.session_state.login_status=True
                st.success("Login Successful")
                st.rerun()

            else:

                st.error("Incorrect Username or Password")

    else:

        st.sidebar.success("Logged In")

        if st.sidebar.button("Logout"):
            st.session_state.login_status=False
            st.rerun()

        page=st.sidebar.selectbox(
            "Select Page",
            ["Student Details","Academic Details","Dashboard"]
        )


# ---------------- STUDENT DETAILS ---------------- #

        if page=="Student Details":

            st.subheader("Enter Student Details")

            name=st.text_input("Name")
            gender=st.selectbox("Gender",["Male","Female"])
            course=st.text_input("Course")
            semester=st.text_input("Semester")
            age=st.text_input("Age")
            contact=st.text_input("Contact")
            email=st.text_input("Email")

            if st.button("Save Student"):

                add_student(name,gender,course,semester,age,contact,email)

                st.success("Student Details Saved")


# ---------------- ACADEMIC DETAILS ---------------- #

        if page=="Academic Details":

            st.subheader("Enter Academic Details")

            name=st.text_input("Student Name")

            sub1=st.text_input("Subject 1 Marks")
            sub2=st.text_input("Subject 2 Marks")
            sub3=st.text_input("Subject 3 Marks")
            sub4=st.text_input("Subject 4 Marks")
            sub5=st.text_input("Subject 5 Marks")

            backlogs=st.text_input("Number of Backlogs")

            attendance=st.text_input("Attendance")

            if st.button("Calculate CGPA"):

                marks=[
                    int(sub1),
                    int(sub2),
                    int(sub3),
                    int(sub4),
                    int(sub5)
                ]

                cgpa=calculate_cgpa(marks)

                st.success(f"CGPA = {cgpa}")

                save_marks(name,*marks,int(backlogs),float(attendance),cgpa)

                if int(backlogs)>0:
                    st.warning(f"Backlogs : {backlogs}")

                if cgpa>=5 and int(backlogs)==0:
                    st.success("Status : PASS")
                else:
                    st.error("Status : FAIL")


# ---------------- DASHBOARD ---------------- #

        if page=="Dashboard":

            st.subheader("📊 Student Analytics Dashboard")

            df_students=load_students()
            df_marks=load_marks()

            st.dataframe(df_students)

            if not df_marks.empty:

                st.metric("Average CGPA",round(df_marks["CGPA"].mean(),2))

                st.metric("Total Students",len(df_students))

                fig,ax=plt.subplots()
                ax.hist(df_marks["CGPA"])
                st.pyplot(fig)

                fig2,ax2=plt.subplots()
                df_marks["BACKLOGS"].value_counts().plot(kind="bar",ax=ax2)
                st.pyplot(fig2)


# ---------------- SIGNUP ---------------- #

elif choice=="Signup":

    st.subheader("Create Account")

    new_user=st.text_input("Username")
    new_pass=st.text_input("Password",type="password")

    if st.button("Signup"):

        if add_user(new_user,new_pass):

            st.success("Account Created Successfully")

        else:

            st.warning("Username already exists")


# ---------------- FORGOT PASSWORD ---------------- #

elif choice=="Forgot Password":

    st.subheader("Reset Password")

    user=st.text_input("Enter Username")
    new_password=st.text_input("Enter New Password",type="password")

    if st.button("Reset"):

        if reset_password(user,new_password):

            st.success("Password Reset Successful")

        else:

            st.error("Username not found")