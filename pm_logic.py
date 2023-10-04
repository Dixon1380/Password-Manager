import utils.validation as utils
from account import Account
import database_manager as dbm
import string
import random


def check_credentials(username, password):
        if not utils.is_valid_input(username) or not utils.is_valid_input(password):
            return False, "Invalid input! Please try again."
        else:
            if Account.verify(username, password):
                return True, "Access granted!"
                
            else:
               return False, "Incorrect login!"
                

def add_user(username, password, confirm_password, email):
        if utils.is_password_match(password, confirm_password):
            success, message = utils.check_password_complexity(password)
            if success:
                if Account.create_user(username, password, email):   
                    return True, f"{username} has been successfully registered!"
                else:
                    return False, f"{username} is already in the database."
            else:
                 return False, message
        else:
            return False,  "Passwords do not match!"
    
def reset_password(email):
    if utils.is_email_valid(email):
        result = dbm.get_user_by_email(email)
        if result:
            return True, email
        else:
            return False, "If the account exists, you'll be able to reset your password."


def update_account(password, confirm_password, email):
        if password == confirm_password:
            hashed_password = Account.hash_password(password)
            if dbm.update_password(email, hashed_password):
                return True, "Password successfully updated!"   
        else:
            return False, "Password do not match!"
        
# Main Application Functions

def add_entry(user_id, website, username, password):
     success = dbm.store_password(user_id, website, username, password)
     if success:
          return True, "New Entry added."
     else:
          return False, "Failed to add entry!"

def modify_entry(user_id, website, username, password):
    """
    Modifies an exist entry in the database
    entry_id: The id of the entry 
    user_id: The id of the user
    """
    pass

def list_passwords(user_id):
       """
       Generates a list of password entries from user.

       Parameters:
       - user_id (str): The id of the user to query the database.

       Returns:
       - List: The list of entries associated with the user_id.
       """
       pass
       

def get_password(website, username):
    """
    Gets the password based on website and username
    
    Parameters:
    - user_id: The id of the user to query the database.
    - website: The website the password is used on.
    - username: The username the password assigned to. 

    Returns:
    - String: The password of the associated entry.
    """
        


def generate_password(length=12, special_characters=True, digits=True):
    """
    Generates a password for user based
    - length: The length of the password to generate.
    - special_characters (bool): Option to add special characters in the password.
    - digits (bool): Option to add digits to the password.

    Returns:
    - string: Returns the password as a string.
    """
    # Generate a random password of specified length
    chars = string.ascii_letters + string.digits + string.punctuation
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
        pass
        

