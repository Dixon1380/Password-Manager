import tkinter as tk
from gui import LoginFrame, RegisterFrame, ForgotPasswordFrame, PasswordManagerFrame, SettingsFrame
import database_setup as dbs
from utils import logging



# Main application 
class PMApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.user_id = None
        self.username = None
        self.user_data = None

        self.title("Password Manager 1.0")
        self.geometry("800x300")

        if dbs.init_db():
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

        

