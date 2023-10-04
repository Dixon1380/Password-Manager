import sqlite3
import os
from config import directory, db_path

def create_directory(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def init_db():
    create_directory(directory)
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Creating the users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id  TEXT PRIMARY KEY,  # user_id set as the primary key
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE, # assuming each user's email is unique
                date_created DATE,
                is_lockout INTEGER
            );
            ''')
            
            # Indexing for users table
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON users(username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON users(email)')

            # Creating the passwords table
            cursor.execute('''
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
            ''')
            
            # General indexing for passwords table
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_website ON passwords(website)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_date_created ON passwords(date_created)')
            
            connection.commit()

        except sqlite3.Error as e:
            print("Database error:", e)  # or log it
            return (False, str(e))
        
    return {"status":True, "message": "Database initialized successfully"}
