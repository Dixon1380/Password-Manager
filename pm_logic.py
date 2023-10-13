from account import Account
from settings import Settings
import utils.validation as utils
import utils.hashing as hash
import database_manager as dbm
from email_handler import send_reset_email
import string
import random
from utils import logging

# User Auth and Creation Functions
def check_credentials(username, password):
        if not utils.is_valid_input(username) or not utils.is_valid_input(password):
            return False, "Invalid input! Please try again."
        else:
            if Account.verify(username, password):
                user_id = dbm.get_user_id_by_username(username)
                return True, user_id, username
            else:
               return False, "Incorrect login!", None, None
                

def add_user(username, password, confirm_password, email):
        if utils.is_password_match(password, confirm_password):
            success, message = utils.check_password_complexity(password)
            if success:
                if Account.create_user(username, password, email):   
                    logging.log_info(f"User {username} is registered successfully.")
                    return True, f"{username} has been successfully registered!"
                else:
                    logging.log_warning(f"Attempt to register already existing user: {username}. ")
                    return False, f"{username} is already in the database."
            else:
                 message = "Failed to create account. check logs for more details."
                 return False, message
        else:
            message = "Password do not match"
            return False,  message
    
def generate_unique_code():
    """Generates a unique six-digit code.

    Returns:
        str: The generated six-digit code.
    """
    return str(random.randint(100000,999999))

def get_user_details_by_email(email):
     """Retrieve username and user_id from database using email

        Returns:
            str: The username from database.
            str: The user_id from database.
     """
     username = dbm.get_username_by_email(email)
     user_id = dbm.get_user_id_by_username(username)
     return username, user_id

def send_reset_password_email(email):
    """Creates and sends email to user
    
    """
    code = generate_unique_code()
    if utils.is_email_valid(email):
        username, user_id = get_user_details_by_email(email)
        success = dbm.store_code(user_id, code)
        if success:
            if send_reset_email(email, username, code):
                return True
            else:
                return False
        else:
            return False
    else:
        return False



def reset_password(password, confirm_password, email, code):
        if password == confirm_password:
            hashed_password = Account.hash_password(password)
            username = dbm.get_username_by_email(email)
            if username:
                 user_id = dbm.get_user_id_by_username(username)
                 if user_id:
                    stored_code, code_timestamp = dbm.get_code_from_db(user_id)
                 if stored_code == code and not utils.is_expired(code_timestamp):
                    if dbm.update_password(hashed_password):
                        return True, "Password successfully updated!" 
                 else:
                    return False, "Unique code does not match"
            else:
                 return False, "Username does not exist."
        else:
            return False, "Password do not match!"

def remove_account(user_id):
     success = dbm.delete_account_from_db(user_id)
     if success:
          return True, "Account was removed successfully."
     else:
          return False, "Error removing account."
        
# Main Application Functions

def add_entry(user_id, website, username, password):
     hashed_password = hash.hash_password(password)
     success = dbm.store_password(user_id, website, username, hashed_password)
     if success:
          return True, "New Entry added."
     else:
          return False, "Failed to add entry!"

def modify_entry(user_id, website, username, new_password):
    """
    Modifies an exist entry in the database
    entry_id: The id of the entry 
    user_id: The id of the user
    """
    hashed_password = hash.hash_password(new_password)
    try:
        stored_entry = dbm.get_entry_by_user_id(user_id)

        if not stored_entry:
            raise ValueError("No entry found for given user_id.")
        if website != stored_entry[0] or username != stored_entry[1]:
            raise ValueError("Entry did not match any stored record.")
        if dbm.update_entry_by_user_id(user_id, website, username, hashed_password):
            return True, "Entry was successfully updated."
        else:
            raise ValueError("Error occurred when updating entry.")
    except ValueError as e:
        return False, str(e)
            
        
def list_entries(user_id):
    """
    Generates a list of password entries from user.

    Parameters:
    - user_id (str): The id of the user to query the database.

    Returns:
    - List: The list of entries associated with the user_id.
    """
    entries = dbm.get_entries_by_user_id(user_id)
    return entries

    

def get_password(user_id, website, username):
    """
    Gets the password based on website and username
    
    Parameters:
    - user_id: The id of the user to query the database.
    - website: The website the password is used on.
    - username: The username the password assigned to. 

    Returns:
    - String: The password of the associated entry.
    """
    success = dbm.check_entry_exists(user_id, website, username)
    if success:
         password = dbm.get_password_from_entry(user_id, website, username)
         return password
    else:
        return None
        

def generate_password(length=12, special_characters=True, digits=True):
    """
    Generates a password for user based
    - length: The length of the password to generate.
    - special_characters (bool): Option to add special characters in the password.
    - digits (bool): Option to add digits to the password.

    Returns:
    - string: Returns the password as a string.
    """
    chars = string.ascii_letters
    if digits:
        chars += string.digits
    if special_characters:
        chars += string.punctuation
    password = ''.join(random.choice(chars) for _ in range(length))
    return password


def delete_entry(user_id, website, username):
        """
        Deletes an entry in the password manager. 

        Parameters:
        - user_id: The id of the user in the database
        - website: The website that password is used on.
        - username: The username that the password is assigned to.


        Returns:
        - bool: True if deletion is successful, False otherwise.
        - string: Message based on bool (True or False)
        """
        if dbm.check_entry_exists(user_id, website, username):
            success = dbm.delete_entry_by_user_id(user_id, website, username)
            if success:
                return True, "Entry was successfully deleted."
            else:
                return False, "Error deleting entry."
            return True
        else:
             return False
    
          
# Main Application's Settings Functions

def initialize_user_settings(user_id):
    """Loads user_data for user"""
    user_settings = Settings(user_id)
    if not user_settings.load_settings():
         user_settings.load_default_settings()
    else:
         return user_settings
    
def update_user_settings(user_id, key, value):
     """
     Update a specific setting for a user.
     """
     user_settings = Settings(user_id)
     user_settings.set_option(key, value)
     user_settings.save_settings()

def get_user_settings(user_id, key):
    """
    Get a value of a specific setting for a user.
    """
    user_settings = Settings(user_id)
    return user_settings.get_option(key)

def load_default_settings(user_id):
     user_settings = Settings(user_id)
     user_settings.load_default_settings()
     
