import database_manager as dbm
from utils.hashing import hash_password, check_password




class Account:

    @classmethod
    def hash_password(cls, password:str):
        """
        Hash password before storing to database.

        Parameters:
        - password (str): The user's password.

        Returns:
        - string: The hashed password will be return for storing in database.
        """
        hashed = hash_password(password)
        return hashed.decode('utf-8')


    @classmethod
    def verify(cls,username, password):
        """
        Verifies user in the database

        Parameters:
        - username (str): The desired username.
        - password (str): The user's password.

        Returns:
        - bool: True if verification is successful, False otherwise.
        """
        result = dbm.get_password_by_username(username)
        if result:
            stored_password = result[0]
            return check_password(password.encode('utf-8'), stored_password.encode('utf-8'))
        return True
        
      
    @classmethod
    def create_user(cls, user_id, username, password, email):
        """
        Registers a new user in the database 

        Parameters:
        - username (str): The desired username.
        - password (str): The user's password.
        - email (str): The user's email address.

        Returns:
        - bool: True if registration is successful, False otherwise.
        """
        hashed_password = cls.hash_password(password)
        success = dbm.register_user(user_id, username, hashed_password, email)
        if success:
            return True
        else:
            return False
    
  