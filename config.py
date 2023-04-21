import os
import configparser
import datetime


time_stamp = datetime.datetime.now()
time_stamp = time_stamp.strftime('%Y_%m_%d')

class Config:
    def __init__(self, options=None, config_file='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_file)
        self.app_file_path = config.get('DEFAULT', 'app_file_path', fallback=os.path.join(os.getcwd(), 'Password Manager'))
        self.master_key_filename = config.get('DEFAULT', 'master_key_filename', fallback='key.key')
        self.master_key_dir = config.get('DEFAULT', 'master_key_dir', fallback=os.path.join(self.app_file_path, 'Keys'))
        self.master_key_filepath = config.get('DEFAULT', 'master_key_filepath', fallback=os.path.join(self.app_file_path, self.master_key_dir, self.master_key_filename))
        self.save_password_dir = config.get('DEFAULT', 'save_password_dir', fallback=os.path.join(self.app_file_path,'Database', 'json', 'Passwords'))
        self.encryption = config.getboolean('DEFAULT', 'encryption', fallback=True)
        self.file_extensions = config.get('DEFAULT', 'file_extensions', fallback='.JSON, .db, .txt').split(', ')
        self.default_db_dir = config.get('DEFAULT', 'default_db_dir', fallback=os.path.join(self.app_file_path,'Database', 'db', 'Passwords'))
        self.default_db_name = config.get('DEFAULT', 'default_db_name', fallback='passwords'+ '_' + datetime.datetime.now().strftime('%Y_%m_%d') + '.db')
        self.default_db_path = config.get('DEFAULT', 'default_db_path', fallback=os.path.join(self.app_file_path, self.default_db_dir, self.default_db_name))
        if options:
            self.__dict__.update(options)