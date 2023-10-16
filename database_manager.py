import sqlite3
import pymysql
import psycopg2
import uuid
from utils import logging
from config import Config


class BaseDatabase:
    def connect(self):
        raise NotImplementedError
    
    def execute(self, query, params=()):
        raise NotImplementedError
    
    def commit(self):
        raise NotImplementedError
    
    def __enter__(self):
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.connection.close()

    def safe_excute(self, cursor, query, params=()):
        try:
            cursor.execute(query, params)
        except Exception as e:
            logging.log_error(f"Error executing query: {e}")
            return None


class DatabaseFactory:

    @staticmethod
    def create_connection(user_id, db_type):
        config = Config(user_id)

        if db_type == "sqlite":
            db_path = config.get_db_setting( 'db_path')
            return SQLiteConnection(db_path)
            
        elif db_type == "mysql":
            db_host = config.get_db_setting('db_host')
            db_user = config.get_db_setting('db_user')
            db_password = config.get_db_setting( 'db_password')
            db_path = config.get_db_setting('db_path')
            return MySQLConnection(db_host, db_user, db_password, db_path)
            
        elif db_type == "postgres":
            db_name = config.get_db_setting(user_id, 'db_name')
            db_user = config.get_db_setting(user_id, 'db_user')
            return PostgreSQLConnection(db_name, db_user)
            
        else:
            raise ValueError(f"Unknown database type: {db_type}")

class SQLiteConnection(BaseDatabase):
    placeholder = "?"
    def __init__(self, path):
        self.path = path
        self.connection = None
    
    def connect(self):
        self.connection = sqlite3.connect(self.path)
        return self.connection
    
    def execute(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor
    
    def commit(self):
        self.connection.commit()

class MySQLConnection(BaseDatabase):
    def __init__(self, host, user, password, path):
        self.host = host
        self.user = user
        self.password = password
        self.path = path
        self.connection = None

    def connect(self):
        self.connection = pymysql.connect(host=self.host, 
                                          user=self.user, 
                                          password=self.password,
                                          database=self.path,
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)
        return self.connection
    
    def execute(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor
    
    def commit(self):
        self.connection.commit()


class PostgreSQLConnection(BaseDatabase):
    placeholder = "%s"
    def __init__(self, name, user):
        self.name = name
        self.user = user
        self.connection = None

    def connect(self):
        self.connection = psycopg2.connect(f"dbname={self.name} user={self.user}")
        return self.connection
    
    def execute(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor

    def commit(self):
        self.connection.commit()
        


# Account DB calls
def db_connection(func):
    def wrapper(*args, **kwargs):
        user_id = kwargs.get('user_id')
        if not user_id:
            raise ValueError("user_id is required")
        db_type = Config(user_id).get_db_config("db_type")
        with DatabaseFactory.create_connection(user_id, db_type) as connection:
            with connection.cursor() as cursor:
                result = func(cursor, *args, **kwargs)
            connection.commit()
        return result
    return wrapper

@db_connection
def check_account_exist(user_id, cursor, email):
    query = "SELECT COUNT(*) FROM users WHERE email=?"
    try:
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        return result[0] > 0
    except sqlite3.Error as e:
        logging.log_error(f"Error checking account existence by email: {e}")
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
        logging.log_error(f"Error retrieving username by email: {e}")
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
        logging.log_error(f"Error retrieving password by username: {e}")
        return None
    return result

@db_connection
def delete_account_from_db(cursor, user_id):
    query ='DELETE FROM users WHERE user_id=?'
    try:
        cursor.execute(query, (user_id,))
        return True
    except sqlite3.Error as e:
        logging.log_error(f"Error deleting account by using user_id: {e}")
        return False



@db_connection
def register_user(cursor, username, password, email):
    # Generate a unique user_id using uuid
    user_id = str(uuid.uuid4())
    query = 'INSERT INTO users (user_id, username, password, email, date_created, is_lockout) VALUES (?, ?, ?, ?, CURRENT_DATE, 0)'
    try:
        cursor.execute(query, (user_id, username, password, email,))
    except sqlite3.IntegrityError as e:
        logging.log_error(f"Integrity error when trying to insert data: {e}")
        if "unique" in str(e).lower():
            logging.log_error("Unique constraint violation: Attempted to insert duplicate value.")
            return False 
        return False
    except sqlite3.Error as e:
        logging.log_error(f"General SQLite error during data insertion: {e}")
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
        logging.log_error(f"Error retrieving user_id by username: {e}")
        return None

@db_connection
def store_code(cursor, user_id, code):
    query = """
    INSERT INTO user_codes(user_id, unique_code, code_timestamp, expired) 
    VALUES (?, ?, CURRENT_TIMESTAMP, ?)
    """
    try:
        cursor.execute(query, (user_id, code, 0))
    except sqlite3.IntegrityError as e:
        logging.log_error(f"Integrity error when trying to insert data: {e}")
        return False
    return True

@db_connection
def get_code_from_db(cursor, user_id):
    query = "SELECT unique_code, code_timestamp FROM user_codes WHERE user_id=?"
    try:
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            return result
    except sqlite3.Error as e:
        logging.log_error(f"Error retrieving unique_code and expired by using user_id: {e}")
        return None


# Main Application DB calls
@db_connection
def store_password(cursor, user_id, website, username, password):
    query = 'INSERT INTO passwords (user_id, website, username, password, date_created, date_modified) VALUES (?, ?, ?, ?, CURRENT_DATE, CURRENT_DATE)'
    try:
        cursor.execute(query, (user_id, website, username, password))
    except sqlite3.IntegrityError as e:
        logging.log_error(f"Integrity error when trying to insert data: {e}")
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
        logging.log_error(f"Error retrieving entry by user_id: {e}")
        return None
    
@db_connection
def update_entry_by_user_id(cursor, user_id, website, username, password):
    query = 'UPDATE passwords SET password=?, date_modified=CURRENT_DATE WHERE user_id=? AND website=? AND username=?'
    try:
        cursor.execute(query, (password, user_id, website, username))
        return cursor.rowcount > 0 
    except sqlite3.IntegrityError as e:
        logging.log_error(f"Integrity error when trying to insert data: {e}")
        return False

@db_connection
def get_entries_by_user_id(cursor, user_id):
    query = 'SELECT entry_id, website, username, date_created, date_modified FROM passwords WHERE user_id=?'
    try:
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        if results:
            return results if results else []
    except sqlite3.Error as e:
        logging.log_error(f"Error retrieving entries by using user_id: {e}")
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
        logging.log_error(f"Error retrieving password by using user_id, entry_website, and entry_username: {e}")
        return None

@db_connection
def delete_entry_by_user_id(cursor, user_id, website, username):
    query ="DELETE FROM passwords WHERE user_id=? AND website=? AND username=?"
    try:
        cursor.execute(query, (user_id, website, username))
        return cursor.rowcount > 0 
    except sqlite3.Error as e:
        logging.log_error(f"Error deleting password by using user_id, entry_website, and entry_username from database: {e}")
        return False

@db_connection
def check_entry_exists(cursor, user_id, website, username):
    query = "SELECT COUNT(*) FROM passwords WHERE user_id=? AND website=? AND username=?"
    try:
        cursor.execute(query, (user_id, website, username))
        result = cursor.fetchone()
        return result[0] > 0
    except sqlite3.Error as e:
        logging.log_error(f"Error retreiving entry using user_id, website and username: {e}")
        return False

@db_connection
def get_email_by_user_id(cursor, user_id):
    query = "SELECT email FROM users WHERE user_id=?"
    try:
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
    except sqlite3.Error as e:
        logging.log_error(f"Error retrieving email using user_id: {e}")
        return None