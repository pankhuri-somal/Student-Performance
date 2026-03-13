import sqlite3

DB_NAME = "student.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Login table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS User_Login(
        USERNAME TEXT PRIMARY KEY,
        PASSWORD TEXT,
        ROLE TEXT
    )
    """)

    # Student details
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Student_Details(
        USERNAME TEXT,
        STUDENT_NAME TEXT,
        GENDER TEXT,
        COURSE TEXT,
        AGE INTEGER,
        CONTACT_NUMBER TEXT,
        EMAIL_ID TEXT
    )
    """)

    # Marks table (semester wise)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Marks(
        USERNAME TEXT,
        SEMESTER INTEGER,
        SUBJECT1 INTEGER,
        SUBJECT2 INTEGER,
        SUBJECT3 INTEGER,
        SUBJECT4 INTEGER,
        SUBJECT5 INTEGER,
        BACKLOGS INTEGER,
        ATTENDANCE REAL,
        CGPA REAL,
        PREDICTED_STATUS TEXT
    )
    """)

    conn.commit()
    conn.close()


def execute_query(query, params=(), fetch=False):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)

    data = None
    if fetch:
        data = cursor.fetchall()

    conn.commit()
    conn.close()
    return data
