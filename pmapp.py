import tkinter as tk
from gui import LoginFrame, RegisterFrame, ForgotPasswordFrame, PasswordManagerFrame
import database_manager as dbm
from utils import logging
import utils.file_creator as file
from config import Config


# Main application 
class PMApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.user_id = None
        self.username = None
        self.app_config = None
        self.settings = {}
        self.title("Password Manager 1.0")
        self.geometry("800x300")
        
        self.init_app()

    def init_db(self):
        app_config = Config()
        app_config._create_configs()
        return dbm.create_users_table() and dbm.create_passwords_table() and dbm.create_usercodes_table()
    
    def init_app(self):
        app_config = Config()
        if not file.file_path_exists(app_config.settings_filename):
            file.create_directory("config")
            file.create_file(app_config.settings_filename)
            self.settings = app_config._load_configurations()
        if self.init_db():
            logging.log_info("Database was successfully intialized.")
            self.show_login_frame()
        else:
            logging.log_error("Database failed to initalized....")

    def show_login_frame(self):
        frame = LoginFrame(self)
        frame.grid(sticky="nsew")  # This will make the frame expand to fill the App window.

        # Make sure that the frame expands with the window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def show_register_frame(self):
        frame = RegisterFrame(self)
        frame.grid(sticky="nsew")

        # Make sure that the frame expands with the window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def show_forgotpassword_frame(self):
        frame = ForgotPasswordFrame(self)
        frame.grid(sticky="nsew")

        # Make sure that the frame expands with the window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1) 

    def show_passmanager_application(self):
        frame = PasswordManagerFrame(self)
        frame.grid(sticky="nsew")

        # Make sure that the frame expands with the window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    

