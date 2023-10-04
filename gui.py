import tkinter as tk
from tkinter import messagebox
from account import Account
import database_setup as dbs
import database_manager as dbm
from utils.validation import is_valid_input
import pm_logic

# Abstract application frame
class BaseFrame(tk.Frame):
    def __init__(self, master=None, frame_mappings=None):
        super().__init__(master)
        self.master = master
        self.frame_mappings = frame_mappings if frame_mappings else {}

    def switch_frame(self, frame_name):
        if frame_name in self.frame_mappings:
            self.destroy()
            self.frame_mappings[frame_name]()
        else:
            print(f"No frame mapping found for {frame_name}")

    def _create_widgets(self):
        pass

    def _create_label(self, text, row, col, padx=10, pady=10):
        label = tk.Label(self, text=text)
        label.grid(row=row, column=col, padx=padx, pady=pady)
        return label

    def _create_labeled_entry(self, label_text, row, col=1, entry_colspan=1, show_text=None):
        self._create_label(label_text, row, col-1)
        entry = tk.Entry(self, show=show_text)
        entry.grid(row=row, column=col, columnspan=entry_colspan, pady=10)
        return entry
    

    def _create_button(self, text, cmd, row, col, padx=10, pady=10):
        btn = tk.Button(self, text=text, command=cmd)
        btn.grid(row=row, column=col, padx=padx, pady=pady)
        return btn


# Login frame
class LoginFrame(BaseFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame_mappings = {
            "Register": self.master.show_register_frame,
            "ForgotPassword": self.master.show_forgotpassword_frame
        }
        self._create_widgets()


    def _create_widgets(self):
        self._create_label("Login", row=0, col=1)
        self.user_entry = self._create_labeled_entry('Username', row=1)
        self.password_entry = self._create_labeled_entry("Password", row=2, show_text="*")

        self._create_button("Login", cmd=self.on_login_button, row=3, col=1)
        self._create_button("Register", cmd=self.on_register_button, row=3, col=2)
        self._create_button("Forgot Password", cmd=self.on_forgotpassword_button, row=3, col=3)
    
    def on_login_button(self):
        username = self.user_entry.get()
        password = self.password_entry.get()
        
        if not is_valid_input(username) or not is_valid_input(password):
             messagebox.showerror("Error", "Invalid input")
        else:
            success, message = pm_logic.check_credentials(username, password)
            if success:
                messagebox.showerror("Error", message)
            else:
                if Account.verify(username, password):
                    messagebox.showinfo("Login Sucess", message)
                    # Transition to another window or do another action
                    self.destroy()
                else:
                    messagebox.showerror("Login Error", message)
                    # Show an error message to the user

    def on_forgotpassword_button(self):
       self.switch_frame("ForgotPassword")

    def on_register_button(self):
        self.switch_frame("Register")
    
# Registration frame 
class RegisterFrame(BaseFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame_mappings = {
            "Login": self.master.show_login_frame
        }
        self._create_widgets()

    def _create_widgets(self):
        self._create_label("Register", row=0, col=1)
        self.user_entry = self._create_labeled_entry("Username:", row=1)
        self.password_entry = self._create_labeled_entry("Password:", row=2, show_text="*")
        self.confirm_password_entry = self._create_labeled_entry("Confirm Password:", row=3, show_text="*")
        self.email_entry = self._create_labeled_entry("Email:", row=4)

        self._create_button("Register", cmd=self.on_register_button, row=5, col=0)
        self._create_button("Login", cmd=self.on_login_button, row=5, col=1)
        
    
    def on_login_button(self):
        self.switch_frame("Login")

    def on_register_button(self):
        username = self.user_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        email = self.email_entry.get()

        if not is_valid_input(password) or not is_valid_input(username):
            messagebox.showerror("Error", "Invalid input")
        else:
            success, message = pm_logic.add_user(username, password, confirm_password, email)
            if success:
                messagebox.showinfo("Registration Success", message)
                self.switch_frame("Login")
            else:
                messagebox.showerror("Registration Failed", message)

# Forgot password frame
class ForgotPasswordFrame(BaseFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame_mappings = {
            "Login": self.master.show_login_frame
        }
        self._create_widgets()

    def _create_widgets(self):
        self._create_label("Forgot password", row=0, col=1)
        self.email_entry = self._create_labeled_entry("Enter the email for the Account:", row=1)

        self._create_button("Submit", cmd=self.on_submit_button, row=2, col=0)
        self._create_button("Login", cmd=self.on_login_button, row=2, col=2)
        
    def on_submit_button(self):
        email = self.email_entry.get()
        result = pm_logic.reset_password(email)
        if result:
            self.resetpassword_window = tk.Toplevel(self)
            self.resetpassword_window.title("Reset Password")

            new_password_label = tk.Label(self.resetpassword_window, text="New Password:")
            new_password_label.grid(row=1, column=0, pady=10, padx=10)
            self.new_password_entry = tk.Entry(self.resetpassword_window, show="*")
            self.new_password_entry.grid(row=1, column=1, pady=10)

            confirm_password_label = tk.Label(self.resetpassword_window, text="Confirm password")
            confirm_password_label.grid(row=2, column=0, pady=10, padx=10)
            self.confirm_password_entry = tk.Entry(self.resetpassword_window, show="*")
            self.confirm_password_entry.grid(row=2, column=1, pady=10)

            submit_button = tk.Button(self.resetpassword_window, text="Update password", command=self.on_update_password_button)
            submit_button.grid(row=3, column=1, pady=10)

        else:
            messagebox.showinfo("Reset Password", "IF the account exists, you'll be able to reset your password.")

    def on_update_password_button(self):
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        email = self.email_entry.get()
        if not is_valid_input(new_password):
            messagebox.showerror("Error", "Invalid input. Please try again.")
        else:
            sucess, message = pm_logic.update_account(new_password, confirm_password, email)
            if sucess:
                messagebox.showinfo("Success!", message)
                self.switch_frame("Login")
            else:
                messagebox.showerror("Error!", message)

    def on_login_button(self):
        self.switch_frame("Login")

# Main application 
class PMApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Password Manager 1.0")
        self.geometry("600x400")

        if dbs.init_db():
             self.show_login_frame()

    def _create_label(self, text, row, col, padx=10, pady=10):
        label = tk.Label(self, text=text)
        label.grid(row=row, column=col, padx=padx, pady=pady)
        return label

    def _create_labeled_entry(self, label_text, row, col=1, entry_colspan=1, show_text=None):
        self._create_label(label_text, row, col-1)
        entry = tk.Entry(self, show=show_text)
        entry.grid(row=row, column=col, columnspan=entry_colspan, pady=10)
        return entry
    

    def _create_button(self, text, cmd, row, col, padx=10, pady=10):
        btn = tk.Button(self, text=text, command=cmd)
        btn.grid(row=row, column=col, padx=padx, pady=pady)
        return btn



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
        self.pm_window = tk.Toplevel(self)
        self.pm_window.title("Password Manager 1.0")
        self.website_entry = self._create_labeled_entry("Website:", row=1)
        self.username_entry = self._create_labeled_entry("Username:", row=2)
        self.password_entry = self._create_labeled_entry("Password:", row=3)

        self.add_button = self._create_button("Add")
        self.edit_button = self._create_button("Edit")
        self.delete_button = self._create_button("Delete")
        self.search_button = self._create_button("Search")
        self.list_button = self._create_button("List")
        self.settings_buttons = self._create_button("Settings")
        self.logout_button = self._create_button("Logout") 

        


if __name__ == "__main__":
    app = PMApp()
    app.mainloop()
