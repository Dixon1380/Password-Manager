import os
from utils import logging


def create_file(file_name):
    if os.path.isfile(file_name) or os.path.exists(file_name):
        return True
    with open(file_name, 'w') as file:
        pass

def create_directory(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    logging.log_info(f"{dir_path} was created.")

def create_file_path(directory, file_name):
    return os.path.join(directory, file_name)

def file_path_exists(file_path):
    return os.path.exist(file_path)