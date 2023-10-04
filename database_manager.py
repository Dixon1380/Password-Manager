import sqlite3
from config import db_path
import uuid



def get_user_by_email(email):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        query = "SELECT username FROM users WHERE email=?"
        try:
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            if result:
                return result[0]
        except sqlite3.Error as e:
            print("Error fetching user by email:", e)
    return None


def update_password(email, password):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        query = 'UPDATE users SET password=? WHERE email=?'
        try:
            cursor.execute(query, (password, email))
            connection.commit()
        except sqlite3.Error as e:
            return False
    return True

def get_password_by_user(username):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        query = 'SELECT password FROM users WHERE username=?'
        try:
            cursor.execute(query, (username,))
            result = cursor.fetchone()
        except sqlite3.Error as e:
            return False, e
        
    return result
            
def register_user(username, password, email):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        # Generate a unique user_id using uuid
        user_id = str(uuid.uuid4())
        query = 'INSERT INTO users (user_id, username, password, email, date_created, is_lockout) VALUES (?, ?, ?, ?, CURRENT_DATE, 0)'
        try:
            cursor.execute(query, (user_id, username, password, email,))
            connection.commit()
        except sqlite3.IntegrityError as e:
            print("Integrity error:", e)
            if "unique" in str(e).lower():
                return False, "Username or email already exists."
            return False, "Registration failed."
        except sqlite3.Error as e:
            print("Database error:", e)
            return False, "Registration error."
    return True, "Registration success!"



def get_user_id_by_username(username):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        query = "SELECT user_id FROM users WHERE username=?"
        try:
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result:
                return result[0]
        except sqlite3.Error as e:
            return False, f"Error fetching user_id by username: {e}"


# Storing passwords to database

def store_password(user_id, website, username, password):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        query = 'INSERT INTO passwords (user_id, website, username, password, date_created, date_modified) VALUES (?, ?, ?, ?, CURRENT_DATE, CURRENT_DATE)'
        try:
            cursor.execute(query, (user_id, website, username, password))
            connection.commit()
        except sqlite3.IntegrityError:
            return False
    return True

