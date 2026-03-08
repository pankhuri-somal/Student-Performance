import sqlite3


# ---------- Create Connection ----------
def create_connection():
    conn = sqlite3.connect("student.db", check_same_thread=False)
    return conn


# ---------- Create Tables ----------
def create_tables():

    conn = create_connection()
    cursor = conn.cursor()

    # User login table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS User_Login(
    USERNAME TEXT PRIMARY KEY,
    PASSWORD TEXT,
    ROLE TEXT
    )
    """)

    # Student details table
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

    # Drop old Marks table if schema changed
    cursor.execute("DROP TABLE IF EXISTS Marks")

    # Create Marks table
    cursor.execute("""
    CREATE TABLE Marks(
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


# ---------- Run Automatically ----------
create_tables()