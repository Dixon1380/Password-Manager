import smtplib
from email.mime.text import MIMEText
import os
import json
from utils import logging


EMAIL_SETTINGS = {}

# Create your own email settings using JSON
json_file_path = os.path.join('data', 'email_settings.json')

def load_json_from_file(json_file):
    with open(json_file, 'r') as file:
        try:
            EMAIL_SETTINGS.update(json.load(file))
            return True
        except Exception as e:
            logging.log_error(f"Error importing email settings: {e}")
            return False




def send_reset_email(email, username, unique_code):
    # Email Structure
    if load_json_from_file(json_file_path):
        subject = "Password Reset Instructions for Password Manager"
        
        body = f"""
        
        Hello {username},

        You recently requested to reset your password for Password Manager. To complete this process, follow the steps below:

        
        1. Open Password Manager: Ensure you have the application running on your desktop.

        2. Navigate to the Login Screen: If you're already logged in, please log out to access the login screen.

        3. Navigate to Forgot Password
        
        4. Click on "Got Code" button

        5. Enter your new password

        6. Enter the Reset Code: In the password field, enter the following unique reset code:

        Unique Reset Code: {unique_code}

        Follow the Prompts: Upon clicking on "Got code", you'll be guided through the process to set a new password.

        Important:

        This reset code is valid for 24 hours. After this period, you'll need to request a new code if you still wish to reset your password.
        If you did not request this password reset, please ignore this email or contact our support team to ensure the security of your account.

        Thank you for using Password Manager!

        Warm regards,

        Password Manager
        """
        # Creating the email
        msg = MIMEText(body, 'plain')
        msg['From'] = EMAIL_SETTINGS['FROM_ADDRESS']
        msg['To'] = email
        msg['Subject'] = subject

        # Send the email
        try:
            with smtplib.SMTP(EMAIL_SETTINGS['SMTP_SERVER'], EMAIL_SETTINGS['SMTP_PORT']) as server:
                server.starttls() # Upgrade the connection to encrypted SSL/TLS
                server.login(EMAIL_SETTINGS['SMTP_USERNAME'], EMAIL_SETTINGS['SMTP_PASSWORD'])
                server.sendmail(EMAIL_SETTINGS['FROM_ADDRESS'], email, msg.as_string())
                logging.log_info("Email sent successfully!")
        except smtplib.SMTPAuthenticationError:
            logging.log_error("SMTP Authenication failed.")
            return False
        except smtplib.SMTPConnectError:
            logging.log_error("Could not establish a connection to the SMTP server.")
            return False
        return True
    else:
        return False

    