# Built-in modules
import string
import random
import datetime
import json
import os
from cryptography.fernet import Fernet
import sqlite3


from config import Config

class PasswordManager:
    def __init__(self, config_file=None):
        self.passwords = []
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)
        self.config = Config(config_file=config_file)
        self.conn = None
        self.generate()
            
    def create_table(self):
        conn = self.conn
        if conn:
            try:
                c = conn.cursor()
                c.execute('''
                    CREATE TABLE IF NOT EXISTS passwords
                    (website TEXT, username TEXT, password TEXT, date_created DATE, date_modified DATE)
                    ''')
                conn.commit()
                print("Table created successfully")
            except Exception as e:
                print(e)
        else:
            print("Error! Cannot create the database connection.")

    def generate(self):
        # Creates directory for all of your saved password files.
        directories = [self.config.save_password_dir, self.config.default_db_dir, self.config.master_key_dir]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print("Password Directory was created: {}".format(directory))
        filepath = self.config.master_key_filepath
        if not os.path.exists(filepath):
            # Checks if master_key_file exists and if doesn't, create it and write the key to it.
            with open(filepath, 'wb') as f: 
                f.write(self.key)
            print("Master key was created: {}".format(self.config.master_key_filepath))
        else:
            # If it does exists, load open and read the key.
            with open(filepath, 'r') as f:
                self.key = f.read()
                self.fernet = Fernet(self.key)
       
    
    def generate_password(self, length=12):
        # Generate a random password of specified length
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for _ in range(length))
        return password
    
    def encrypt_password(self, password):
        # Encrypt a password using the Fernet encryption key
        if self.config.encryption == False:
            return password
        else:
            return self.fernet.encrypt(password.encode()).decode()
    

    def decrypt_password(self, encrypted_password):
        # Decrypt an encrypted password using the Fernet encryption key
        if self.config.encryption == False:
            return encrypted_password
        else:
            return self.fernet.decrypt(encrypted_password.encode()).decode()

    def add_password(self, website, username, password=None):
        # Add a password for a given website and username
        encrypted_password = None
        if not password:
            choice = input("You didn't specify a password. Do you want to generate one?(y/n)?: ")
            if choice.lower() == 'y':
                number = int(input("Enter password length (Default length: 12): "))
                if number == None or number > 20:
                    password = self.generate_password(length=number)
                    encrypted_password = self.encrypt_password(password)
                else:
                    password = self.generate_password(length=number)
                    encrypted_password = self.encrypt_password(password)
            elif choice.lower() == 'n':
                password = input("Enter a password: ")
                encrypted_password = self.encrypt_password(password)
        elif password:
            encrypted_password = self.encrypt_password(password)
        entry = {
            'website': website,
            'username': username,
            'password': encrypted_password,
            'date_created': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'date_modified': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        self.passwords.append(entry)

    def get_password(self, website, username):
        # Get the password for a given website and username
        for entry in self.passwords:
            if entry['website'] == website and entry['username'] == username:
                encrypted_password = entry['password']
                return self.decrypt_password(encrypted_password)
        return None

    def delete_password(self, website, username):
        # Delete the password for a given website and username
        for entry in self.passwords:
            if entry['website'] == website and entry['username'] == username:
                self.passwords.remove(entry)

    def list_passwords(self):
        # List all stored passwords
       for entry in self.passwords:
            encrypted_password = entry['password']
            # try:
            #     decrypted_password = self.decrypt_password(encrypted_password)
            # except Exception as e:
            #     print(f"Error: Could not decrypt password for {entry['website']} ({entry['username']}).")
            #     print(f"  Reason: {str(e)}")
            #     decrypted_password = None
            # if decrypted_password:
            #     print(f"Website: {entry['website']}\nUsername: {entry['username']}\nPassword: {decrypted_password}\nDate created: {entry['date_created']}\nDate modified: {entry['date_modified']}\n")
            # else:
            print(f"Website: {entry['website']}\nUsername: {entry['username']}\nPassword: {encrypted_password}\nDate created: {entry['date_created']}\nDate modified: {entry['date_modified']}\n")
    
    # def generate_and_add_password(self, website, username):
    #     # Generate a new password and add it for a website and username
    #     password = self.generate_password()
    #     self.add_password(website, username, password)

    def modify_password(self, website, username, new_password):
        # Modify the password for a given website and username
        for entry in self.passwords:
            if entry['website'] == website and entry['username'] == username:
                encrypted_password = self.encrypt_password(new_password)
                entry['password'] = encrypted_password
                entry['date_modified'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def save_to_file(self, filename):
        # Save passwords to a JSON file
        encrypted_passwords = []
        for entry in self.passwords:
            encrypted_entry = {
                'website': entry['website'],
                'username': entry['username'],
                'password': self.encrypt_password(entry['password']),
                'date_created': entry['date_created'],
                'date_modified': entry['date_modified']
            }
            encrypted_passwords.append(encrypted_entry)
        filepath = os.path.join(self.config.save_password_dir, filename)
        if os.path.exists(filepath):
            choice = input("This file already exists. Do you want to overwrite it (y/n)?: ")
            if choice.lower() == 'y':
                with open(filepath, 'w') as f:
                    json.dump(encrypted_passwords, f, indent=4)
            elif choice.lower() == 'n':
                print("If you want to save to a different file, try again with a different name.")
        else:
            with open(filepath, 'w') as f:
                json.dump(encrypted_passwords, f, indent=4)

    def load_from_file(self, filename):
        # Load passwords from a JSON file
        filepath = os.path.join(self.config.save_password_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                encrypted_passwords = json.load(f)
            self.passwords.clear()
            for entry in encrypted_passwords:
                decrypted_password = self.decrypt_password(entry['password'])
                password = {
                    'website': entry['website'],
                    'username': entry['username'],
                    'password': decrypted_password,
                    'date_created': entry['date_created'],
                    'date_modified': entry['date_modified']
                }
                self.passwords.append(password)
        else:
            print("Error: File not found.")
    def initialize_db(self):
         # Initializing Database
        self.create_table()
        print("New Database was initalized.")
        print("New Database created.")

    def export_to_database(self, filepath=None):
        # If the filepath is None, then we use the existing db. Else, we use connect to the filepath.
        if filepath is not None:
            if os.path.exists(filepath):
                self.conn = sqlite3.connect(filepath)
                
            else:
                print(f"Error: {filepath} does not exist")
                return
        else:
            self.conn = sqlite3.connect(self.config.default_db_path)
            self.initialize_db()
        for entry in self.passwords:
            query = "INSERT INTO passwords (website, username, password, date_created, date_modified) VALUES (?, ?, ?, ?, ?)"
            values = (entry['website'], entry['username'], self.encrypt_password(entry['password']), entry['date_created'], entry['date_modified'])
            try:
                c = self.conn.cursor()
                c.execute(query, values)
                self.conn.commit()
            except Exception as e:
                print(e)

    def load_from_database(self, file):
        if file:
            with sqlite3.connect(file) as self.conn:
                conn = self.conn
                query = "SELECT website, username, password, date_created, date_modified FROM passwords"
                try:
                    c = conn.cursor()
                    c.execute(query)
                    rows = c.fetchall()
                    if len(rows) > 0:
                        for row in rows:
                            password = {
                                'website': row[0],
                                'username': row[1],
                                'password': row[2],
                                'date_created': row[3],
                                'date_modified': row[4],
                            }
                            self.passwords.append(password)
                except Exception as e:
                    print(e)
        else:
            print(self.passwords)