import re
import datetime
# Invaild Validation Handling

def is_valid_input(value):
    # Checks for allowed characters in the username and password
    if not re.match("^[a-zA-Z0-9_!@#S%^&*()]+$", value):
        return False
    # Checks for length constraints (between 3 and 50 characters)
    if not 3 <= len(value) <= 50:
        return False
    return True

def is_password_match(password, confirm_password):
    if not password or not confirm_password:
        return False
    else:
        return password == confirm_password

def is_email_valid(email):
    if not email:
        return False
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(email_regex, email))

def check_password_complexity(password):
    if not password:
        return False, "Password should not be empty"

    if len(password) < 8 or len(password) > 50:
        return False, "Password should be between 8 to 50 characters long"

    if not any(char.isdigit() for char in password):
        return False, "Password should have at least one numeral"

    if not any(char.isupper() for char in password):
        return False, "Password should have at least one uppercase letter"

    if not any(char.islower() for char in password):
        return False, "Password should have at least one lowercase letter"

    special_characters = "!@#$%^&*()-_+=<>?"
    if not any(char in special_characters for char in password):
        return False, "Password should have at least one of the special characters !@#$%^&*()-_+=<>?"

    # Add more rules here if needed

    return True, "Password is valid." 

def is_expired(code_timestamp):
    # Define how long the code is valid for (e.g., 24 hours)
    expiration_duration = datetime.timedelta(hours=24)
    
    # Convert the code_timestamp from string to datetime object
    # I'm assuming the timestamp is stored in the format 'YYYY-MM-DD HH:MM:SS'
    # Adjust the format if needed
    code_time = datetime.datetime.strptime(code_timestamp, '%Y-%m-%d %H:%M:%S')
    
    # Get current datetime
    current_time = datetime.datetime.now()
    
    # Calculate the expiration time for the code
    expiration_time = code_time + expiration_duration
    
    # If the current time is beyond the expiration time, then the code has expired
    return current_time > expiration_time

