import json
import utils.file_creator as file
import utils.logging as logging

CONFIG_DIR = 'config'
DB_DIR_NAME = 'data'
DB_NAME = 'users.db'

class Config:
    def __init__(self):
        self.settings_filename = file.create_file_path(CONFIG_DIR, f"pmapp_settings.json")
        self.db_setings_filename = file.create_file_path(DB_DIR_NAME, f"pmapp_db_settings.json")
        
        if not file.file_path_exists(self.settings_filename) and file.file_path_exists(self.db_setings_filename):
            self._create_new_user_configs()

    def _load_configurations(self, filename):
        with open(filename, 'r') as f:
            return json.load(f)
    
    def _save_configurations(self, data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f, filename)

    def get_setting(self, setting_key):
        settings = self._load_configurations(self.settings_filename)
        return settings.get(setting_key)
    
    def update_setting(self, setting_key, value):
        settings = self._load_configurations(self.settings_filename)
        settings[setting_key] = value
        self._save_configurations(settings, self.settings_filename)
    
    def update_settings(self, settings_dict):
        old_settings = self._load_configurations(self.settings_filename)
        for key, value in settings_dict.items():
            old_settings[key] = value
        
        self._save_configurations(old_settings, self.settings_filename)

    def get_db_config(self):
        return self._load_configurations(self.db_setings_filename)
    
    def update_db_config(self, db_config):
        self._save_configurations(db_config, self.db_setings_filename)
    
    def _create_new_user_configs(self):
        default_settings = {
            "font_type": "Arial",
            "encryption": "ON",

        }
        default_db_settings = {
            "db_type": "sqlite",
            "config": {
                "path": file.create_file_path(DB_DIR_NAME, DB_NAME)
            }
        }
        self._save_configurations(default_settings, self.settings_filename)
        self._save_configurations(default_db_settings, self.db_setings_filename)