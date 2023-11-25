import sqlite3
import psycopg2
from utils import logging
from config import Config



class BaseDatabase:
    def __init__(self):
        self.connection = None
        self.curr = None
        self.config = {}
        self.placeholder = '?'
        self.connect()

    def connect(self):
        raise NotImplementedError
    
    def execute(self, query, params=()):
        raise NotImplementedError
    
    def commit(self):
        if self.connection:
            self.connection.commit()
    
    def __enter__(self):
        return self.curr
    
    def __exit__(self, exc_type, exc_val, exc_tb):
       if self.curr:
           self.curr.close()
       self.commit()
       if self.connection:
           self.connection.close()

    def safe_excute(self, cursor, query, params=()):
        try:
            cursor.execute(query, params)
        except Exception as e:
            logging.log_error(f"Error executing query: {e}")
            return None


class DatabaseFactory:

    @staticmethod
    def create_connection(db_type):
        if db_type == "sqlite":
            return SQLiteConnection()
        elif db_type == "postgres":
            return PostgreSQLConnection()
        else:
            raise ValueError(f"Unknown database type: {db_type}")


class SQLiteConnection(BaseDatabase):
    def connect(self):
        self.path = self.config['db_path']
        self.connection = sqlite3.connect(self.path)
        self.curr = self.connection.cursor()

class PostgreSQLConnection(BaseDatabase):
    placeholder = "%s"
    
    def connect(self):
        self.config = Config()
        self.name = self.config.get_db_setting('db_name')
        self.user = self.config.get_db_setting('db_user')
        self.placeholder = PostgreSQLConnection.placeholder
        self.connection = psycopg2.connect(f"dbname={self.name} user={self.user}")
        self.curr = self.connection.cursor()
        
# Load config file
db_config = Config()

def db_connection(func):
    def wrapper(*args, **kwargs):
        db_settings = db_config._load_configurations()
        db_type = db_settings['db_settings']['db_type']
        db = DatabaseFactory.create_connection(db_type)
        with db as cursor:
            return func(cursor, *args, db=db, **kwargs)
    return wrapper


#Database Create
@db_connection
def create_users_table(cursor, db):
    create_users_table_query = '''
            CREATE TABLE IF NOT EXISTS users (
                user_id  TEXT PRIMARY KEY, 
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE, 
                date_created DATE,
                is_lockout INTEGER
            );
            '''
    create_user_index_query = 'CREATE INDEX IF NOT EXISTS idx_username ON users(username)'
    create_email_index_query = 'CREATE INDEX IF NOT EXISTS idx_email ON users(email)'

    try:
        # Creates user account table
        cursor.execute(create_users_table_query)
        # Create indexes for username and email
        cursor.execute(create_user_index_query)
        cursor.execute(create_email_index_query)
        return True
    except Exception as e:
            logging.log_error(f"Database error: {e}")  
            return False

@db_connection
def create_passwords_table(cursor, db):
    create_passwords_table_query = '''
                CREATE TABLE IF NOT EXISTS passwords(
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    website TEXT, 
                    username TEXT, 
                    password TEXT, 
                    date_created DATE, 
                    date_modified DATE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            '''
    create_website_index_query = 'CREATE INDEX IF NOT EXISTS idx_website ON passwords(website)'
    create_date_created_index_query = 'CREATE INDEX IF NOT EXISTS idx_date_created ON passwords(date_created)'
    try:
        # Create passwords table
        cursor.execute(create_passwords_table_query)
        # Create indexes for website and date created
        cursor.execute(create_website_index_query)
        cursor.execute(create_date_created_index_query)
        return True 
    except Exception as e:
            logging.log_error(f"Database error: {e}")  
            return False

@db_connection
def create_usercodes_table(cursor, db):
    create_usercodes_table_query = '''
                CREATE TABLE IF NOT EXISTS user_codes(
                    code_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    unique_code VARCHAR(6),
                    code_timestamp DATETIME,
                    expired BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            '''
    try:
        # Creates user_codes table
        cursor.execute(create_usercodes_table_query)
        return True
    except Exception as e:
            logging.log_error(f"Database error: {e}")  
            return False

@db_connection
def check_account_exist(cursor, db, email):
    query = f"SELECT COUNT(*) FROM users WHERE email={db.placeholder}"
    try:
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        return result[0] > 0
    except Exception as e:
        logging.log_error(f"Error checking account existence by email: {e}")
        return False

@db_connection
def get_username_by_email(cursor, db, email):
    query = f"SELECT username FROM users WHERE email={db.placeholder}"
    try:
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        if result:
            return result[0]
    except Exception as e:
        logging.log_error(f"Error retrieving username by email: {e}")
        return None

@db_connection
def update_password(cursor, db , email, password):
    query = f'UPDATE users SET password={db.placeholder} WHERE email={db.placeholder}'
    try:
        cursor.execute(query, (password, email))
    except Exception as e:
        return False
    return True

@db_connection
def get_password_by_username(cursor, db, username):
    query = f'SELECT password FROM users WHERE username={db.placeholder}'
    try:
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        if result:
            return result[0]
    except Exception as e:
        logging.log_error(f"Error retrieving password by username: {e}")
        return None 

@db_connection
def delete_account_from_db(user_id, cursor, db):
    query =f'DELETE FROM users WHERE user_id={db.placeholder}'
    try:
        cursor.execute(query, (user_id,))
        return True
    except Exception as e:
        logging.log_error(f"Error deleting account by using user_id: {e}")
        return False


@db_connection
def register_user(cursor, db, user_id, username, password, email):
    # Generate a unique user_id using uuid
    query = f'''INSERT INTO users (user_id, username, password, email, date_created, is_lockout) 
    VALUES (
        {db.placeholder}, 
        {db.placeholder}, 
        {db.placeholder}, 
        {db.placeholder}, 
        CURRENT_DATE, 
        0)'''
    try:
        cursor.execute(query, (user_id, username, password, email,))
    except Exception as e:
        logging.log_error(f"Integrity error when trying to insert data: {e}")
        if "unique" in str(e).lower():
            logging.log_error("Unique constraint violation: Attempted to insert duplicate value.")
            return False 
        return False
    except Exception as e:
        logging.log_error(f"General SQLite error during data insertion: {e}")
        return False
    return True

@db_connection
def get_user_id_from_db(cursor, db, username):
    query =f"SELECT user_id FROM users WHERE username={db.placeholder}"
    try:
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        if result:
            return result[0] 
    except Exception as e:
        logging.log_error(f"Error retrieving user_id by username: {e}")
        return None

@db_connection
def store_code(user_id, cursor, db, code):
    query = f"""
    INSERT INTO user_codes(user_id, unique_code, code_timestamp, expired) 
    VALUES ({db.placeholder}, {db.placeholder}, CURRENT_TIMESTAMP, {db.placeholder})
    """
    try:
        cursor.execute(query, (user_id, code, 0))
    except Exception as e:
        logging.log_error(f"Integrity error when trying to insert data: {e}")
        return False
    return True

@db_connection
def get_code_from_db(user_id, cursor, db):
    query = f"SELECT unique_code, code_timestamp FROM user_codes WHERE user_id={db.placeholder}"
    try:
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            return result
    except Exception as e:
        logging.log_error(f"Error retrieving unique_code and expired by using user_id: {e}")
        return None


# Main Application DB calls
@db_connection
def store_password(user_id, cursor, db, website, username, password):
    query = f'''INSERT INTO passwords (user_id, website, username, password, date_created, date_modified) VALUES (
        {db.placeholder}, 
        {db.placeholder}, 
        {db.placeholder}, 
        {db.placeholder}, 
        CURRENT_DATE, 
        CURRENT_DATE)'''
    try:
        cursor.execute(query, (user_id, website, username, password))
    except Exception as e:
        logging.log_error(f"Integrity error when trying to insert data: {e}")
        return False
    return True

@db_connection
def get_entry_from_db(user_id, cursor, db):
    query = f'SELECT website, username, password FROM passwords WHERE user_id={db.placeholder}'
    try:
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            return result
    except Exception as e: 
        logging.log_error(f"Error retrieving entry by user_id: {e}")
        return None
    
@db_connection
def update_entry(user_id, cursor, db, website, username, password):
    query = f'''UPDATE passwords SET password={db.placeholder}, date_modified=CURRENT_DATE WHERE 
    user_id={db.placeholder} AND website={db.placeholder} AND username={db.placeholder}'''
    try:
        cursor.execute(query, (password, user_id, website, username))
        return cursor.rowcount > 0 
    except Exception as e:
        logging.log_error(f"Integrity error when trying to insert data: {e}")
        return False

@db_connection
def get_entries(user_id, cursor, db):
    query = f'SELECT entry_id, website, username, date_created, date_modified FROM passwords WHERE user_id={db.placeholder}'
    try:
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        if results:
            return results if results else []
    except Exception as e:
        logging.log_error(f"Error retrieving entries by using user_id: {e}")
        return []

@db_connection
def get_password_from_entry(user_id, cursor, db, website, username):
    query =f'''SELECT password FROM passwords WHERE 
    user_id={db.placeholder} AND website={db.placeholder} AND username={db.placeholder}'''
    try:
        cursor.execute(query, (user_id, website, username))
        result = cursor.fetchone()
        if result:
            return result[0]
    except Exception as e:
        logging.log_error(f"Error retrieving password by using user_id, entry_website, and entry_username: {e}")
        return None

@db_connection
def delete_entry_from_db(user_id, cursor, db, website, username):
    query =f"DELETE FROM passwords WHERE user_id={db.placeholder} AND website={db.placeholder} AND username={db.placeholder}"
    try:
        cursor.execute(query, (user_id, website, username))
        return cursor.rowcount > 0 
    except Exception as e:
        logging.log_error(f"Error deleting password by using user_id, entry_website, and entry_username from database: {e}")
        return False

@db_connection
def check_entry_exists(user_id, cursor, db, website, username):
    query = f"SELECT COUNT(*) FROM passwords WHERE user_id={db.placeholder} AND website={db.placeholder} AND username={db.placeholder}"
    try:
        cursor.execute(query, (user_id, website, username))
        result = cursor.fetchone()
        return result[0] > 0
    except Exception as e:
        logging.log_error(f"Error retreiving entry using user_id, website and username: {e}")
        return False

@db_connection
def get_email_by_user_id(user_id, cursor, db):
    query = f"SELECT email FROM users WHERE user_id={db.placeholder}"
    try:
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
    except Exception as e:
        logging.log_error(f"Error retrieving email using user_id: {e}")
        return None