import pm_logic
from utils import validation
from utils import logging

class GuiLogicInterface:

    def __init__(self):
        self.cache = {}


    def add_to_cache(self, key, value):
        self.cache[key] = value

    def get_from_cache(self, key):
        return self.cache.get(key, None)
    
    def clear_cache(self):
        self.cache = {}

    def remove_from_cache(self, key):
        if key in self.cache:
            del self.cache[key]
    
    # User Authenication and Creation
    def login_user(self, username, password):
        logging.log_info("User clicked on login button")
        logging.log_info("Checking credentials.....")
        return pm_logic.check_credentials(username, password)

    def add_user(self, username, password, confirm_password, email):
        logging.log_info("User clicked on register button.")
        logging.log_info("Processing user inputs for valid registration....")
        return pm_logic.add_user(username, password, confirm_password, email)

    def send_reset_password_code(self, email):
        logging.log_info("User clicked on forgot password button.")
        logging.log_info("Processing email for validation....")
        return pm_logic.send_reset_password_email(email)
    
    
    def reset_password(self, password, confirm_password, email, code):
        logging.log_info("User clicked on 'Got Code' button.")
        logging.log_info("Process user inputs for validation....")
        return pm_logic.reset_password(password, confirm_password, email, code)
    
    # Main Application Logic
    def add_entry(self, user_id, website, username, password):
        logging.log_info("User clicked on 'Add Entry' button.")
        logging.log_info("Processing inputs to store to database.....")
        return pm_logic.add_entry(user_id, website, username, password)
    
    def edit_entry(self, user_id, website, username, password):
        logging.log_info("User clicked on 'Edit Entry' button.")
        logging.log_info("Process inputs to modify requested entry in database....")
        return pm_logic.modify_entry(user_id, website, username, password)

    def delete_entry(self, user_id, website, username):
        logging.log_info("User clicked on 'Delete Entry' button.")
        logging.log_info("Process inputs to delete requested entry from database....")
        return pm_logic.delete_entry(user_id, website, username)
    
    def list_entries(self, user_id):
        logging.log_info("User clicked on 'List Entries' button.")

        cached_result = self.get_from_cache(f"list_entries_{user_id}")
        if cached_result:
            return cached_result
        
        logging.log_info("Fetching user's entries from database....")
        result = pm_logic.list_entries(user_id)
        self.add_to_cache(f"list_entries_{user_id}", result)
        return result
    
    def get_password(self, user_id, website, username):
        cached_result = self.get_from_cache(f"get_password_{user_id}_{website}_{username}")
        if cached_result:
            return cached_result
        result = pm_logic.get_password(user_id, website, username)
        self.add_to_cache(f"get_password_{user_id}_{website}_{username}", result)
        return result
    

    def generate_password(self):
        logging.log_info("User clicked on 'generate password' button.")
        logging.log_info("Generating password for user.....")
        return pm_logic.generate_password()
    
    # Settings Logic
    def save_settings(self, user_id, settings):
        logging.log_warn("Applying changes to user's settings file.")
        logging.log_info("Saving changes....")
        pm_logic.update_user_settings(user_id, settings)

    def load_settings(self, user_id):
        logging.log_info("Loading user settings....")
        return pm_logic.initialize_user_settings(user_id)
        

    def load_settings_from_file(self, file_name):
        logging.log_info("Loading user settings from file....")
        return pm_logic.load_settings()
    
    def reset_defaults(self):
        logging.log_info("Reseting settings to default values....")
        return pm_logic.load_default_settings()

    def change_user_account_password(self, user_id, password, confirm_password):
        logging.log_info("Changing password.....")
        return pm_logic.change_user_account_password(user_id, password, confirm_password)

    def remove_account(self, user_id):
        logging.log_info("Removing user_account...")
        return pm_logic.remove_account(user_id)
    
    # Utility
    @staticmethod
    def validate_user_registration(username, password, email):
         """Validates user's registration"""
         logging.log_info("Checking user's input for validation.....")
         return validation.is_valid_input(username) and validation.is_valid_input(password) and validation.is_email_valid(email)
    
    @staticmethod
    def validate_user_login(username, password):
        """Validates user's login inputs"""
        logging.log_info("Checking user's input for validation.....")
        return validation.is_valid_input(username) and validation.is_valid_input(password)
    
    @staticmethod
    def validate_input(input):
        """Validates a single user's input"""
        logging.log_info("Checking user's input for validation.....")
        return validation.is_valid_input(input)
     
    @staticmethod
    def log_message(type:str, message:str):
        log_map = {
            'info': logging.log_info,
            'warn': logging.log_warn,
            'error': logging.log_error,
            'critical': logging.log_critical
        }
        log_func = log_map.get(type)

        if log_func:
            return log_func(message)
        else:
            logging.log_warn(f"Unknown log type: {type}")