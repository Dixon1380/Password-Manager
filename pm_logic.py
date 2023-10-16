from account import Account
from config import Config
import utils.validation as utils
import utils.hashing as hash
import utils.file_creator as file
import database_manager as dbm
from email_handler import send_reset_email
import string
import random
from utils import logging
from config import default_config


# User Auth and Creation Functions
def check_credentials(username, password):
        logging.log_warn("Attempt to check valid inputs from username and password....")
        if not utils.is_valid_input(username) or not utils.is_valid_input(password):
            logging.log_error("Invalid input in username or password fields....")
            return False, "Invalid input! Please try again."
        else:
            logging.log_warn("Attempt to verify user within our database.....")
            if Account.verify(username, password):
                logging.log_info("Success. Account does exists.")
                logging.log_info("Processing account for login.....")
                user_id = dbm.get_user_id_by_username(username)
                return True, user_id, username
            else:
               logging.log_info("Account does not exist. Either password or username is not spelled corrently.")
               return False, "Incorrect login!", None, None
                

def add_user(username, password, confirm_password, email):
        logging.log_warn("Attempting to register new user within our database.")
        logging.log_info("Verifying password match....")
        if utils.is_password_match(password, confirm_password):
            logging.log_info("Success. Password were matched.")
            logging.log_warn("Matching password with our security policy...")
            success, message = utils.check_password_complexity(password)
            if success:
                logging.log_info("Success. Password does meet complexity requirements.")
                logging.log_warn("Attempting to add user.....")
                if Account.create_user(username, password, email):
                    logging.log_info(f"Success. User {username} was successfully added to our database.")   
                    return True, f"{username} has been successfully registered!"
                else:
                    logging.log_warn(f"Attempt to register already existing user: {username}. ")
                    return False, f"{username} is already in the database."
            else:
                 logging.log_error()
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
                    if dbm.update_password(email, hashed_password):
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
        else:
             return False
    
          
# Main Application's Settings Functions

def initialize_user_settings(user_id):
    """Creates the user_settings file for user if not exists."""
    config = Config(user_id)
    user_settings_config = config._load_configurations(config.settings_filename)
    user_db_config = config._load_configurations(config.db_setings_filename)
    return user_settings_config, user_db_config
    
    
def update_user_settings(user_id, setting_dict):
    """
    Update a specific setting for a user.
    """
    config = Config(user_id)
    for key, value in setting_dict:
        config.update_setting()
    

def load_user_settings(user_id, file_path):
    if user_id not in file_path:
        raise ValueError("Can not user settings from another user.")
    config = Config(user_id)
    config.settings_filename = file_path
    user_settings = config._load_configurations(file_path)
    return user_settings

def load_user_db_settings(user_id, db_file_path):
    if user_id not in db_file_path:
        raise ValueError("Can not user db settings from another user.")
    config = Config(user_id)
    config.db_setings_filename = db_file_path
    db_config = config._load_configurations(db_file_path)
    return db_config

def load_default_settings():
    config = Config()
    user_settings = config._load_configurations(config.settings_filename)
    db_user_settings = config._load_configurations(config.db_setings_filename)
    return user_settings, db_user_settings

def change_user_account_password(user_id, password, confirm_password):
    if utils.is_password_match(password, confirm_password):
        hashed_password = Account.hash_password(password)
        email = dbm.get_email_by_user_id(user_id)
        success = dbm.update_password(email, hashed_password)
        if success:
            return True
        else:
            return False



