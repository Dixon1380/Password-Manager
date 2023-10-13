from config import Config
import json 
import os
from utils import logging


class Settings:
    def __init__(self, user_id, base_dir="user_data"):
        self.user_dir = os.path.join(base_dir, user_id)
        self.config_path = os.path.join(self.user_dir, "settings.json")
        self.default_config_path = os.path.join(base_dir, "default_settings.json")
        self.options = {
            "font-type": "Arial",
            "encryption": True,
            "database" : "Sqlite3",
            "database_server": None,
            "database_username": None,
            "database_password": None,
            "database_port": None
        }
        
        #Ensure user directory exists
        if not os.path.exists(self.user_dir):
            os.makedirs(self.user_dir)
        
        if not os.path.exist(self.config_path):
            if not self.load_default_settings():
                self.create_default_settings()
        
    
    def create_default_settings(self):
        try:
            with open(self.default_config_path, 'w') as file:
                json.dump(self.options, file, indent=4)
                return True
        except Exception as e:
            logging.log_error(f"Error creating default settings file: {e}")
            return False
        
    def save_settings(self):
        """Saves the current settings to a file."""
        try:
            with open(self.config_path, 'w') as file:
                json.dump(self.options, file, indent=4)
            return True
        except Exception as e:
            logging.log_error(f"Error saving settings: {e}")
            return False
    
    def load_settings(self):
        """Loads settings from a file if it exists."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as file:
                    self.options.update(json.load(file))
                    return True
            except Exception as e:
                logging.log_error(f"Error loading settings: {e}")
                return False
            
    def load_default_settings(self):
        """Load default settings from file if it exists."""
        if os.path.exists(self.default_config_path):
            try:
                with open(self.default_config_path, 'r') as file:
                    self.options.update(json.load(file))
                    return True
            except Exception as e:
                logging.log_error(f"Error loading settings: {e}")
                return False
            
    def set_option(self, key, value):
        """Sets a specific setting."""
        if key in self.options:
            self.options[key] = value

    def get_option(self, key):
        """Returns the value of a specific setting, or Noneif not found."""
        return self.options.get(key)
    
    def __str__(self):
        return str(self.options)