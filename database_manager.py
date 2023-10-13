import sqlite3
from config import db_path
import uuid
from utils import logging

# Account DB calls
def db_connection(func):
    def wrapper(*args, **kwargs):
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            result = func(cursor, *args, **kwargs)
            connection.commit()
        return result
    return wrapper

@db_connection
def check_account_exist(cursor, email):
    query = "SELECT COUNT(*) FROM users WHERE email=?"
    try:
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        return result[0] > 0
    except sqlite3.Error as e:
        logging.log_error(f"Error fetching entry: {e}")
        return False
    
    
@db_connection
def get_username_by_email(cursor, email):
    query = "SELECT username FROM users WHERE email=?"
    try:
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        if result:
            return result[0]
    except sqlite3.Error as e:
        logging.log_error(f"Error fetching user by email: {e}")
        return None

@db_connection
def update_password(cursor, email, password):
    query = 'UPDATE users SET password=? WHERE email=?'
    try:
        cursor.execute(query, (password, email))
    except sqlite3.Error as e:
        return False
    return True

@db_connection
def get_password_by_user(cursor, username):
    query = 'SELECT password FROM users WHERE username=?'
    try:
        cursor.execute(query, (username,))
        result = cursor.fetchone()
    except sqlite3.Error as e:
        logging.log_error(f"Error fetching password by user: {e}")
        return False
    return result

@db_connection
def delete_account_from_db(cursor, user_id):
    query ='DELETE FROM users WHERE user_id=?'
    try:
        cursor.execute(query, (user_id,))
        return True
    except sqlite3.Error as e:
        logging.log_error(f"Error deleting account by user_id: {e}")
        return False



@db_connection
def register_user(cursor, username, password, email):
    # Generate a unique user_id using uuid
    user_id = str(uuid.uuid4())
    query = 'INSERT INTO users (user_id, username, password, email, date_created, is_lockout) VALUES (?, ?, ?, ?, CURRENT_DATE, 0)'
    try:
        cursor.execute(query, (user_id, username, password, email,))
    except sqlite3.IntegrityError as e:
        logging.log_error(f"Integrity error: {e}")
        if "unique" in str(e).lower():
            logging.log_error("Username or email already exists.")
            return False 
        logging.log_error("Registration failed.")
        return False
    except sqlite3.Error as e:
        logging.log_error(f"Database error: {e}")
        return False
    return True

@db_connection
def get_user_id_by_username(cursor, username):
    query = "SELECT user_id FROM users WHERE username=?"
    try:
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        if result:
            return result[0] 
    except sqlite3.Error as e:
        logging.log_error(f"Error fetching user_id by username: {e}")
        return None

@db_connection
def store_code(cursor, user_id, code):
    query = """
    INSERT INTO users_codes(user_id, unique_code, code_timestamp, expired) 
    VALUES (?, ?, CURRENT_TIMESTAMP, ?)
    """
    try:
        cursor.execute(query, (user_id, code, 0))
    except sqlite3.IntegrityError:
        return False
    return True

@db_connection
def get_code_from_db(cursor, user_id):
    query = "SELECT unique_code AND code_timestamp FROM users_code WHERER user_id=?"
    try:
        cursor.execute(query, (user_id,))
    except sqlite3.Error as e:
        logging.log_error(f"Error fetching unique_code and expired by user_id: {e}")
        return False
    return True


# Main Application DB calls
@db_connection
def store_password(cursor, user_id, website, username, password):
    query = 'INSERT INTO passwords (user_id, website, username, password, date_created, date_modified) VALUES (?, ?, ?, ?, CURRENT_DATE, CURRENT_DATE)'
    try:
        cursor.execute(query, (user_id, website, username, password))
    except sqlite3.IntegrityError:
        return False
    return True

@db_connection
def get_entry_by_user_id(cursor, user_id):
    query = 'SELECT website, username, password FROM passwords WHERE user_id=?'
    try:
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            return result
    except sqlite3.Error as e: 
        logging.log_error(f"Error fetching entry by user_id: {e}")
        return None
    
@db_connection
def update_entry_by_user_id(cursor, user_id, website, username, password):
    query = 'UPDATE passwords SET password=? AND date_modified=CURRENT_DATE WHERE user_id=? AND website=? AND username=?'
    try:
        cursor.execute(query, (password, user_id, website, username))
        return cursor.rowcount > 0 #Return True if at least 1 row is updated.
    except sqlite3.Error:
        return False

@db_connection
def get_entries_by_user_id(cursor, user_id):
    query = 'SELECT website, username, password FROM passwords WHERE user_id=?'
    try:
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        if results:
            print(results)
            return results if results else []
    except sqlite3.Error as e:
        logging.log_error(f"Error fetching entries by user_id: {e}")
        return []

@db_connection
def get_password_from_entry(cursor, user_id, website, username):
    query ='SELECT password FROM passwords WHERE user_id=? AND website=? AND username=?'
    try:
        cursor.execute(query, (user_id, website, username))
        result = cursor.fetchone()
        if result:
            return result[0]
    except sqlite3.Error as e:
        logging.log_error(f"Error fetching password by user_id, entry_website, and entry_username: {e}")
        return None

@db_connection
def delete_entry_by_user_id(cursor, user_id, website, username):
    query ="DELETE FROM passwords WHERE user_id=? AND website=? AND username=?"
    try:
        cursor.execute(query, (user_id, website, username))
        return cursor.rowcount > 0 
    except sqlite3.Error as e:
        logging.log_error(f"Error deleteing password by user_id, entry_website, and entry_username from database: {e}")
        return False

@db_connection
def check_entry_exists(cursor, user_id, website, username):
    query = "SELECT COUNT(*) FROM passwords WHERE user_id=? AND website=? AND username=?"
    try:
        cursor.execute(query, (user_id, website, username))
        result = cursor.fetchone()
        return result[0] > 0
    except sqlite3.Error as e:
        logging.log_error(f"Error fetching entry: {e}")
        return False
