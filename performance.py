# ============================================
# STREAMLIT STUDENT PREDICTION DASHBOARD
# With Registration + Login System
# ============================================

import streamlit as st
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import joblib

# Load Model
model = joblib.load("student_model.pkl")
le = pickle.load(open("label_encoder.pkl", "rb"))

st.set_page_config(page_title="Student Prediction System", layout="centered")

# -------------------------------
# Simple In-Memory User Database
# -------------------------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ================================
# SIDEBAR MENU
# ================================
menu = st.sidebar.selectbox("Menu", ["Register", "Login"])

# ================================
# REGISTER
# ================================
if menu == "Register":
    st.title("📝 Student Registration")

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Register"):
        if new_user in st.session_state.users:
            st.error("Username already exists!")
        else:
            st.session_state.users[new_user] = new_pass
            st.success("Registration Successful! Please Login.")

# ================================
# LOGIN
# ================================
elif menu == "Login":
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login Successful!")
        else:
            st.error("Invalid Username or Password")

# ================================
# AFTER LOGIN DASHBOARD
# ================================
if st.session_state.logged_in:

    st.title("🎓 AI-Based Student Academic Success & Dropout Prediction System")
    st.write(f"Welcome, {st.session_state.username}")

    st.markdown("---")

    # Academic Inputs
    st.header("📚 Academic Details")

    sem1_grade = st.number_input("Semester 1 Grade", 0.0, 20.0)
    sem1_approved = st.number_input("Semester 1 Approved Subjects", 0, 20)

    sem2_grade = st.number_input("Semester 2 Grade", 0.0, 20.0)
    sem2_approved = st.number_input("Semester 2 Approved Subjects", 0, 20)

    admission_grade = st.number_input("Admission Grade", 0.0, 20.0)

    # Financial Inputs
    st.header("💰 Financial Details")

    tuition = st.selectbox("Tuition Fees Up To Date?", [0,1])
    debtor = st.selectbox("Debtor?", [0,1])
    scholarship = st.selectbox("Scholarship Holder?", [0,1])

    # Demographics
    st.header("👤 Personal Details")

    age = st.number_input("Age at Enrollment", 17, 60)
    gender = st.selectbox("Gender (0=Female,1=Male)", [0,1])

    st.markdown("---")

    if st.button("🔮 Predict Outcome"):

        # CGPA Calculation
        if sem1_approved + sem2_approved == 0:
            cgpa = 0
        else:
            cgpa = (
                (sem1_grade * sem1_approved) +
                (sem2_grade * sem2_approved)
            ) / (sem1_approved + sem2_approved)

        st.subheader(f"🎯 Calculated CGPA: {round(cgpa,2)}")

        input_data = np.array([[ 
            admission_grade,
            sem1_approved,
            sem1_grade,
            sem2_approved,
            sem2_grade,
            tuition,
            debtor,
            scholarship,
            age,
            gender,
            cgpa
        ]])

        prediction = model.predict(input_data)
        probability = model.predict_proba(input_data)

        result = le.inverse_transform(prediction)

        st.success(f"📌 Prediction: {result[0]}")

        st.write("### 🔍 Prediction Probability")
        prob_df = pd.DataFrame(probability, columns=le.classes_)
        st.dataframe(prob_df)

        # Risk Level
        if result[0] == "Dropout":
            st.error("⚠ High Risk Student")
        elif result[0] == "Enrolled":
            st.warning("⚠ Moderate Risk")
        else:
            st.success("✅ Low Risk - Likely to Graduate")

        # Chart
        st.subheader("📊 Academic Performance Dashboard")

        labels = ["Semester 1", "Semester 2", "CGPA"]
        values = [sem1_grade, sem2_grade, cgpa]

        fig, ax = plt.subplots()
        ax.bar(labels, values)
        ax.set_ylim(0,20)
        st.pyplot(fig)

    # Logout Button
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.success("Logged Out Successfully")
