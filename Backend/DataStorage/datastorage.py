import sqlite3
conn = sqlite3.connect('user_data.db')
c = conn.cursor()

def create_user_table():
    c.execute(   '''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT NOT NULL)''')
    conn.commit()

def create_doctor_table():
    c.execute(   '''CREATE TABLE IF NOT EXISTS doctors
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    password TEXT NOT NULL,
                    specialty TEXT NOT NULL,
                    email TEXT NOT NULL,
                    workplace TEXT NOT NULL,
                    degree TEXT NOT NULL)''')
    conn.commit()

def add_user(username, email):
    c.execute("INSERT INTO users (username, email) VALUES (?, ?)", (username, email))
    conn.commit()

def add_doctor(name, password, specialty, email, workplace, degree):
    c.execute("INSERT INTO doctors (name, password, specialty, email, workplace, degree) VALUES (?, ?, ?, ?, ?, ?)",
              (name, password, specialty, email, workplace, degree))
    conn.commit()


if __name__ == "__main__":
    create_user_table()
    create_doctor_table()