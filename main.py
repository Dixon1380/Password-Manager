from passmanager import PasswordManager
import art
import os
from time import sleep
import datetime
import tkinter as tk


# Create a custom configuration here:

custom_config = {
    'app_file_path': os.path.join(os.getcwd(), 'Password Manager'),
    'master_key_filename': 'key.key',
    'master_key_dir': 'Keys',
    'master_key_filepath': os.path.join(os.getcwd(), 'Password Manager', 'Keys', 'key.key'),
    'save_password_dir': os.path.join(os.getcwd(), 'Password Manager', 'Database', 'json', 'Passwords'),
    'encryption': True,
    'file_extensions': ['.JSON', '.db'],
    'default_db_dir': os.path.join(os.getcwd(), 'Password Manager', 'Database', 'db', 'Passwords'),
    'default_db_name': 'passwords'.join(datetime.datetime.now().strftime('%Y_%m_%d')) + '.db',
    'default_db_path' : os.path.join(os.getcwd(), 'Password Manager', 'Database', 'db', 'Passwords', 'passwords'+ '_' + datetime.datetime.now().strftime('%Y_%m_%d') + '.db')
}



# Entry Point 
def main(isrunning=True):
    art.cls()
    print("Please wait while your app is initializing...")
    sleep(2)
    app = PasswordManager(custom_config)
    while isrunning:
        choice = ''
        print(art.main_screen)
        print("\t1) Add entry\n\t2) Delete entry\n\t3) Edit entry\n\t4) List Entries\n\t5) Get password\n\t6) Export to Database or File\n\t7) Load from Database or File\n")
        choice = input("Select an option or Press Q to quit: ")
        if choice == '1':
            art.cls()
            website = input("Enter the name of the website: ")
            username = input("What's the username?: ")
            passw = input("What's the password?: ")
            app.add_password(website, username, passw)
            print("Your entry has been added.")
            sleep(1)
        elif choice == '2':
            art.cls()
            website = input("Enter the name of the website:: ")
            username = input("What's the username?: ")
            password = input("What's the password?: ")
            app.delete_password(website, username, password)
            print("This entry has been sucessfully deleted.")
            sleep(1)
        elif choice == '3':
            art.cls()
            website = input("Enter the name of the website: ")
            username = input("What's the username?: ")
            new_password = input("Enter the new password: ")
            app.modify_password(website, username, password)
            print("This entry has been successfully modified.")
            sleep(1)
        elif choice == '4':
            art.cls()
            print("List of passwords entered:\n")
            app.list_passwords()
            sleep(1)
        elif choice == '5':
            website = input("Enter the name of the webiste: ")
            username = input("Enter the username: ")
            password = app.get_password(website, username)
            print(f'The password for that entry is {password}')
        elif choice == '6':
           art.cls()
           print("1) Save as JSON  2) Save to Database\n")
           option = input("Enter a option: ")
           if option == '1': # JSON Option
                print("Password you have entered:\n")
                app.list_passwords()
                choice = input("Do you want to commit to these changes(y/n)?: ")
                if choice.lower() == 'y':
                    filename = input("Enter a name for this save file: ")
                    filename = filename + '.json'
                    app.save_to_file(filename)
                    print("Your passwords were successfully saved to file.")
                    sleep(1)
                elif choice.lower() == 'n':
                    print("No changes were commited.")
           elif option == '2': # SQLITE Option
                app.list_passwords()
                choice = input("Do you want to commit to these changes(y/n)?: ")
                if choice.lower() == 'y':
                    print("1) Create New Database\n2) Use an existing database\n")
                    option = input("Enter an option: ")
                    if option == '1':
                        app.export_to_database()
                    elif option == '2':
                        file_name = input("Enter the db file you wish to use (without extension): ")
                        file_name = file_name + '.db'
                        file_path = os.path.join(os.getcwd(), 'Password Manager', 'Database', 'db', 'Passwords', file_name)
                        app.export_to_database(filepath=file_path)
                    print("Your passwords were successfully exported to database.")
                    sleep(1)
                elif choice.lower() == 'n':
                    print("No changes were made.")
                    sleep(1)
        elif choice == '7':
            print("1) Load JSON\n2) Load Database\n")
            option = input("Enter a option: ")
            if option == '1':
                art.cls()
                filename = input("Enter the name of the .JSON file you wish to load(without the extension): ")
                filename = filename + '.json'
                app.load_from_file(filename)
                sleep(1)    
            elif option == '2':
                art.cls()
                file_name = input("Enter the db file you wish to use (without extension): ")
                file_name = file_name + '.db'
                file_path = os.path.join(os.getcwd(), 'Password Manager', 'Database', 'db', 'Passwords', file_name)
                app.load_from_database(file_path)
                print("Database loaded successfully.")
                sleep(1)
        elif choice.lower() == 'q':
            art.cls()
            isrunning = False
            print("Exiting program")
            sleep(1)

        

if __name__ == '__main__':
    main()
 
 
    