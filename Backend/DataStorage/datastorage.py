import os
import sqlite3
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'user_data.db')

number_of_doctors=10
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
        
def create_document_table():
    with get_connection() as conn:
        create_string = '''CREATE TABLE IF NOT EXISTS documents
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        document_path TEXT NOT NULL,
                        summary TEXT NOT NULL,
                        user_id INTEGER NOT NULL,'''
        
        for i in range(number_of_doctors):
            create_string = create_string+f'matched_doctor_{i+1} TEXT NOT NULL DEFAULT \'\','
            create_string = create_string+f'similarity_score_{i+1} REAL NOT NULL DEFAULT 0,'

        create_string = create_string[:-1]+')'
        conn.execute(create_string)

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
#region loop through doctors

def get_num_doctors():
    with get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM doctors")
        return cursor.fetchone()[0]

def get_doctor_by_id(doctor_id):
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
        return cursor.fetchone()

#endregion
#region add documents

def add_document(document_path, summary, matched_doctors, user_id):
    with get_connection() as conn:
        columns = "document_path, summary, user_id"
        placeholders = "?, ?, ?"
        values = [document_path, summary, user_id]

        for i in range(number_of_doctors):
            columns += f", matched_doctor_{i+1}, similarity_score_{i+1}"
            placeholders += ", ?, ?"
            if i < len(matched_doctors):
                values.extend([matched_doctors[i][0], matched_doctors[i][1]])
            else:
                values.extend(['', 0])

        conn.execute(f"INSERT INTO documents ({columns}) VALUES ({placeholders})", values)
#endregion

create_user_table()
create_doctor_table()
create_document_table()
