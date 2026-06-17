import os
import sqlite3
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'user_data.db')


def get_connection():
    return sqlite3.connect(DATABASE_PATH)

#region Create tables
def create_user_table():
    with get_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    location TEXT NOT NULL)''')

def create_doctor_table():
    with get_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS doctors
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    password TEXT NOT NULL,
                    specialty TEXT NOT NULL,
                    email TEXT NOT NULL,
                    workplace TEXT NOT NULL,
                    degree TEXT NOT NULL,
                    summary TEXT NOT NULL)''')

#endregion
#region Add users/doctors

def add_user(username, email, password, location):
    with get_connection() as conn:
        if conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone():
            return False 
        conn.execute("INSERT INTO users (username, email, password, location) VALUES (?, ?, ?, ?)", (username, email, password, location))
        return True

def add_doctor(name, password, specialty, email, workplace, degree, summary):
    with get_connection() as conn:
        if conn.execute("SELECT * FROM doctors WHERE name = ?", (name,)).fetchone():
            return False
        conn.execute("INSERT INTO doctors (name, password, specialty, email, workplace, degree, summary) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, password, specialty, email, workplace, degree, summary))
        return True

#endregion
#region Verify user/doctors

def verify_user(username, password):
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        return cursor.fetchone() is not None
    
def verify_doctor(name, password):
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM doctors WHERE name = ? AND password = ?", (name, password))
        return cursor.fetchone() is not None

#endregion

create_user_table()
create_doctor_table()
