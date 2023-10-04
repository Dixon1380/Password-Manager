import logging 
import os

# Setting up a logger with the name 'PMApp_Logger'

logger = logging.getLogger('PMApp_logger')


if not logger.handlers:
    # Set the logging level
    logger.setLevel(logging.DEBUG)
    
    log_directory = 'logs' # specify your desired directory here

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    file_handler = logging.FileHandler(os.path.join(log_directory, 'PMApp.log'))

    # Create a formater
    formater = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formater)

    # Add the file handler to logger
    logger.addHandler(file_handler)

def log_error(message):
    logger.error(message)

def log_warn(message):
    logger.warning(message)

def log_info(message):
    logger.info(message)

def log_critical(message):
    logger.critical(message)