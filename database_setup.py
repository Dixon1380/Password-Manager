# import sqlite3
# from utils import logging
# from utils.file_creator import create_directory
# import database_manager as dbm
# from config import Config



# dbm.DatabaseFactory.create_connection()
# def init_db(db_config_path):
#     with sqlite3.connect(db_config_path) as connection:
#         cursor = connection.cursor()
#         try:
#             cursor.execute("PRAGMA foreign_keys = ON")
            
#             # Creating the users table
#             cursor.execute('''
#             CREATE TABLE IF NOT EXISTS users (
#                 user_id  TEXT PRIMARY KEY, 
#                 username TEXT NOT NULL UNIQUE,
#                 password TEXT NOT NULL,
#                 email TEXT NOT NULL UNIQUE, 
#                 date_created DATE,
#                 is_lockout INTEGER
#             );
#             ''')
            
#             # Indexing for users table
#             cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON users(username)')
#             cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON users(email)')

#             # Creating the passwords table
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS passwords(
#                     entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     user_id TEXT NOT NULL,
#                     website TEXT, 
#                     username TEXT, 
#                     password TEXT, 
#                     date_created DATE, 
#                     date_modified DATE,
#                     FOREIGN KEY (user_id) REFERENCES users(user_id)
#                 );
#             ''')
            
#             # General indexing for passwords table
#             cursor.execute('CREATE INDEX IF NOT EXISTS idx_website ON passwords(website)')
#             cursor.execute('CREATE INDEX IF NOT EXISTS idx_date_created ON passwords(date_created)')
            
#             # Creating the users code table
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS user_codes(
#                     code_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     user_id TEXT NOT NULL,
#                     unique_code VARCHAR(6),
#                     code_timestamp DATETIME,
#                     expired BOOLEAN DEFAULT FALSE,
#                     FOREIGN KEY (user_id) REFERENCES users(user_id)
#                 );
#             ''')
#             connection.commit()

#         except sqlite3.Error as e:
#             logging.log_error(f"Database error: {e}")  
#             return False
        
#     return True