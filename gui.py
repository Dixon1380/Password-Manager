import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from gui_logic_handler import GuiLogicInterface


# Abstract application frame
class BaseFrame(tk.Frame):
    def __init__(self, master=None, frame_mappings=None):
        super().__init__(master)
        self.master = master
        self.frame_mappings = frame_mappings if frame_mappings else {}

    def switch_frame(self, frame_name):
        gui_api = GuiLogicInterface()
        if frame_name in self.frame_mappings:
            self.destroy()
            self.frame_mappings[frame_name]()
        else:
            gui_api.log_message("error", f"No frame mapping found for {frame_name}")

    def _create_widgets(self):
        pass

    def _create_label(self, text:str, row:int, col:int, padx=10, pady=10):
        label = tk.Label(self, text=text)
        label.grid(row=row, column=col, padx=padx, pady=pady)
        return label

    def _create_labeled_entry(self, label_text:str, l_row:int, l_col:int, e_row:int, e_col:int, entry_colspan=1, show_text=None):
        self._create_label(label_text, l_row, l_col)
        entry = tk.Entry(self, show=show_text)
        entry.grid(row=e_row, column=e_col, columnspan=entry_colspan, pady=10)
        return entry
    

    def _create_button(self, text:str, cmd, row:int, col:int, padx=10, pady=10):
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
        self.config(width=300, height=200)
        self._create_widgets()


    def _create_widgets(self):
        self._create_label("Login", row=0, col=3)
        self.user_entry = self._create_labeled_entry('Username', 1, 2, 1, 3)
        self.password_entry = self._create_labeled_entry("Password", 2, 2, 2, 3 ,show_text="*")

        self.hide_button = self._create_button("Show", cmd=self.on_toggle_password_button, row=2, col=4)

        self._create_button("Login", cmd=self.on_login_button, row=3, col=2)
        self._create_button("Register", cmd=self.on_register_button, row=3, col=3)
        self._create_button("Forgot Password", cmd=self.on_forgotpassword_button, row=3, col=4)
    


    def on_toggle_password_button(self):
        current_show_value = self.password_entry.cget("show")

        if current_show_value == "*":
            self.password_entry.config(show="")
            self.hide_button.config(text="Hide")
        else:
            self.password_entry.config(show="*")
            self.hide_button.config(text="Show")
            

    def on_login_button(self):
        username = self.user_entry.get()
        password = self.password_entry.get()
        gui_api = GuiLogicInterface()
        if not gui_api.validate_user_login(username, password):
             messagebox.showerror("Invalid input", "Your input was invalid. Please try again.")
        else:
            success, user_id, username = gui_api.login_user(username, password)
            if success:
                self.master.user_id = user_id
                self.master.username = username
                gui_api.init_settings
                self.master.app_settings, self.master.app_config = gui_api.load_settings()
                gui_api.log_message("info", f"{username} is now logged in.")
                messagebox.showinfo("Login Success", "You are now logged in.")
                if success:
                    gui_api.log_message("info", "User data has been loaded successfully.")
                else:
                    gui_api.log_message("warn", "No user data was found for this account. Configuring defaults for this account.")
                self.destroy()
                self.master.show_passmanager_application()
            else:
                gui_api.log_message("error", "Login was unsuccessful")
                messagebox.showerror("Login Error", "Username and Password are incorrect or Username does not exist.")
                

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
        self._create_label("Register", row=0, col=3)
        self.user_entry = self._create_labeled_entry("Username:", 1, 2, 1, 3)
        self.password_entry = self._create_labeled_entry("Password:", 2,2,2,3, show_text="*")
        self.confirm_password_entry = self._create_labeled_entry("Confirm Password:", 3,2,3,3, show_text="*")
        self.email_entry = self._create_labeled_entry("Email:", 4,2,4,3)

        self._create_button("Register", cmd=self.on_register_button, row=5, col=2)
        self._create_button("Login", cmd=self.on_login_button, row=5, col=3)
        
    
    def on_login_button(self):
        self.switch_frame("Login")

    def on_register_button(self):
        username = self.user_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        email = self.email_entry.get()
        gui_api = GuiLogicInterface()
        if not gui_api.validate_user_registration(username, password, email):
            messagebox.showerror("Invalid input!", "You entered invalid input. Please try again.")
        success, message = gui_api.add_user(username, password, confirm_password, email)
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
        self.email_entry = self._create_labeled_entry("Enter the email for the Account:", 1, 1, 1, 2)
        self._create_button("Submit", cmd=self.on_submit_button, row=2, col=0)
        self._create_button("Got Code", cmd=self.on_got_code_button, row=2, col=1)
        self._create_button("Login", cmd=self.on_login_button, row=2, col=2)
        
    def on_submit_button(self):
        email = self.email_entry.get()
        gui_api = GuiLogicInterface()
        gui_api.log_message('info', f"Sending email code to {email}")
        gui_api.send_reset_password_code(email)
        messagebox.showinfo("Reset Password", "IF the account exists, you'll be able to reset your password.")

    def on_got_code_button(self):
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
        
         email_label = tk.Label(self.resetpassword_window, text="Enter unique code email address: ")
         email_label.grid(row=3, column=0, pady=10, padx=10)
         self.email_entry = tk.Entry(self.resetpassword_window)
         self.email_entry.grid(row=3, column=1, pady=10, padx=10)

         unique_code_label = tk.Label(self.resetpassword_window, text="Enter unique code from email:")
         unique_code_label.grid(row=4, column=0, pady=10, padx=10)
         self.unique_code_entry = tk.Entry(self.resetpassword_window)
         self.unique_code_entry.grid(row=4, column=1, pady=10)

         submit_button = tk.Button(self.resetpassword_window, text="Update password", command=self.on_update_password_button)
         submit_button.grid(row=5, column=1, pady=10)

    def on_update_password_button(self):
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        email = self.email_entry.get()
        code = self.unique_code_entry.get()
        if not (new_password and confirm_password and email and code):
            messagebox.showerror("Error", "All fields are required. Please fill them out.")
        gui_api = GuiLogicInterface()
        
        if not gui_api.validate_input(new_password):
            messagebox.showerror("Error", "Invalid input. Please try again.")
        else:
            sucess, message = gui_api.reset_password(new_password, confirm_password, email, code)
            if sucess:
                messagebox.showinfo("Success!", message)
                gui_api.log_message('info', "Returning to login....")
                self.resetpassword_window.destroy()
                self.switch_frame("Login")
            else:
                messagebox.showerror("Error!", message)

    def on_login_button(self):
        self.switch_frame("Login")

class PasswordManagerFrame(BaseFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame_mappings = {
            "Logout": self.master.show_login_frame
        }
     
        self._create_widgets()

    def _create_widgets(self):
        self.website_entry = self._create_labeled_entry("Website:", 1, 1, 1, 2)
        self.username_entry = self._create_labeled_entry("Username:", 2, 1, 2, 2)
        self.password_entry = self._create_labeled_entry("Password:", 3, 1, 3, 2, show_text="")
        self.hide_entry = self._create_button("Hide", self.on_toggle_password_button, row=3, col=3)
        self.generate_password_button = self._create_button("Generate Password", self.on_generate_password_button, row=3, col=4)

        self.add_button = self._create_button("Add", self.on_add_button, row=4, col=1)
        self.edit_button = self._create_button("Edit", self.on_edit_button, row=4, col=2)
        self.delete_button = self._create_button("Delete", self.on_delete_button, row=4, col=3)
        self.search_button = self._create_button("Search", self.on_search_button, row=4, col=4)
        self.list_button = self._create_button("List", self.on_list_button, row=4, col=5)
        self.settings_buttons = self._create_button("Settings", self.on_settings_button, row=4, col=6)
        self.logout_button = self._create_button("Logout", self.on_logout_button, row=4, col=7) 
    

    def on_toggle_password_button(self):
        current_show_value = self.password_entry.cget("show")

        if current_show_value == "*":
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")


    def on_generate_password_button(self):
        gui_api = GuiLogicInterface()
        password = gui_api.generate_password()
        messagebox.showinfo("Password Generated", f"Your generated password is: {password}")
        if self.password_entry.get == "":
            self.password_entry.insert(tk.END, password)
        else:
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, password)

    def on_add_button(self):
        website = self.website_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        gui_api = GuiLogicInterface()
        success, message = gui_api.add_entry(self.master.user_id, website, username, password)
        if success:
            gui_api.log_message("info",message)
            messagebox.showinfo("New Entry", message)
        else:
            gui_api.log_message("error", message)
            messagebox.showerror("Entry Error", message)

    def on_edit_button(self):
        website = self.website_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        gui_api = GuiLogicInterface()
        if messagebox.askyesno("Modify Entry?", f"Do you want to edit this entry?\nWebsite: {website}\nUsername: {username}"):
            success, message = gui_api.edit_entry(self.master.user_id, website, username, password)
            if success:
                messagebox.showinfo("Modified Success!", message)
            else:
                messagebox.showerror("Modified Falied!", message)
        else:
            messagebox.showerror("Modify Entry?", "Entry does not exist.")

    def on_delete_button(self):
        website = self.website_entry.get()
        username = self.username_entry.get()
        gui_api = GuiLogicInterface()
        if messagebox.askyesno("Delete Entry?", f"Do you want to delete this entry?\nWebsite: {website}\nUsername:{username}"):
            success, message = gui_api.delete_entry(self.master.user_id, website, username)
            if success:
                gui_api.log_message("info",message)
                messagebox.showinfo("Deleted Entry!", message)
            else:
                gui_api.log_message("error", message)
                messagebox.showerror("Deleted Entry!", message)
        else:
            gui_api.log_message("error", message)
            messagebox.showerror("Delete Entry?", "Entry does not exist.")
        

    def on_search_button(self):
        website = self.website_entry.get()
        username = self.username_entry.get()

        gui_api = GuiLogicInterface()
        gui_api.log_message("info", "Entry was found!")
        password = gui_api.get_password(self.master.user_id, website, username)
        if password:
            messagebox.showinfo("Password for Entry", f"Your password is {password}")
        else:
            messagebox.showerror("Password for Entry", "Entry does not exist.")
    
    def on_list_button(self):
        gui_api = GuiLogicInterface()
        entries = gui_api.list_entries(self.master.user_id)
        
        self.list_window = tk.Toplevel(self)
        self.list_window.title("Entries List")

        self.list_window.grid_rowconfigure(0, weight=1)
        self.list_window.grid_columnconfigure(0, weight=1)

        scrollbar = tk.Scrollbar(self.list_window)
        scrollbar.grid(row=0, column=1, sticky="ns")

        listbox = tk.Listbox(self.list_window, yscrollcommand=scrollbar.set)
        gui_api.log_message("info", f"Retrieving list entries for current_user: {self.master.username}")
        for entry in entries:
            listbox.insert(tk.END, f"Entry {entry[0]} - Website: {entry[1]} Username:{entry[2]} Date Created:{entry[3]} Date Modified: {entry[4]}")
        listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=listbox.yview)

    def on_settings_button(self):
        self.settings_window = tk.Toplevel(self)
        self.settings_window.title("Settings")
        settings_label = tk.Label(self.settings_window, text="Settings")
        settings_label.grid(row=0, column=1)

        # Change Font 
        changefont_label = tk.Label(self.settings_window, text="Change Font:")
        changefont_label.grid(row=1, column=0, pady=10, padx=10)

        self.changefont_dropdownbox = ttk.Combobox(self.settings_window, values=("Times New Roman", "Arial", "Impact"))
        self.changefont_dropdownbox.grid(row=1, column=1)
       
        # Encryption settings checkboxes 
        encrypt_label = tk.Label(self.settings_window, text="Encrypt Data")
        encrypt_label.grid(row=2, column=0, pady=10, padx=10)
        self.encrypt_status = tk.StringVar()
        self.checkbox_True = ttk.Radiobutton(self.settings_window, value="ON", variable=self.encrypt_status, command=self.display_encrypt_status)
        self.checkbox_True.grid(row=2, column=1)
        self.checkbox_False = ttk.Radiobutton(self.settings_window, value="OFF", variable=self.encrypt_status, command=self.display_encrypt_status)
        self.checkbox_False.grid(row=2, column=2)

        # Database settings
        database_label = tk.Label(self.settings_window, text="Change Database:")
        database_label.grid(row=3, column=0, pady=10, padx=10)
        self.database_dropdownbox = ttk.Combobox(self.settings_window, values=("Sqlite3", "MySQL", "PostgresSQL"))
        self.database_dropdownbox.grid(row=3, column=1)

        # Buttons in settings window
        apply_button = tk.Button(self.settings_window, text="Apply", command=self.on_apply_button)
        apply_button.grid(row=4, column=1, pady=10)
        reset_default_button = tk.Button(self.settings_window, text="Reset Defaults", command=self.on_reset_defaults_button) 
        reset_default_button.grid(row=4, column=2, pady=10)

        # set default value for dropdownbox
        saved_font = self.master.app_settings['font_type']
        print(saved_font)

        if saved_font:
            self.changefont_dropdownbox.set(saved_font)
        else:
            self.changefont_dropdownbox.set("Select an option")
      
        self.changefont_dropdownbox.bind("<<ComboxSelected>>", self.on_settings_font_dropbox)


        encryption_status = str(self.master.app_settings['encryption'])
        if encryption_status is not None:
            self.encrypt_status.set(str(encryption_status))
        
        saved_db_option = self.master.app_settings['encryption']

        if saved_db_option:
            self.database_dropdownbox.set(saved_db_option)
        else:
            self.database_dropdownbox.set("Select an option")
      
        self.database_dropdownbox.bind("<<ComboxSelected>>", self.on_settings_db_dropbox)
        



    def on_settings_font_dropbox(self, event=None):
        self.master.app_settings['font-type'] = self.changefont_dropdownbox.get()

    def on_settings_db_dropbox(self, event=None):
        pass
    
    def display_encrypt_status(self):
        if self.encrypt_status.get() == "True":
            print(self.encrypt_status.get())
        else:
            print(self.encrypt_status.get())

    def on_apply_button(self):
        gui_api = GuiLogicInterface()
        if messagebox.askyesno("Apply changes?", "Do you want to apply changes to settings?"):
            gui_api.save_settings()
        

    def on_reset_defaults_button(self):
        gui_api = GuiLogicInterface()
        if messagebox.askyesno("Reset Default Settings?", "Do you want to reset to defaults?"):
            self.master.user_settings = gui_api.reset_defaults()


    def on_logout_button(self):
        gui_api = GuiLogicInterface()
        if messagebox.askyesno("Logout?", "Do you want to logout?"):
            self.master.user_id = None
            self.master.username = None
            self.master.user_settings.clear()
            gui_api.log_message('info', "Attempting to logout user....")
            gui_api.log_message('info', "Returning to login....")
            self.switch_frame("Logout")






