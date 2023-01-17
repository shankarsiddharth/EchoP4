import os
import configparser
import pathlib

from cryptography.fernet import Fernet

import echo_p4_constants as ep4c
from echo_p4_logger import EchoP4Logger


def get_root_folder():
    current_file_dir_path = os.path.dirname(os.path.realpath(__file__))
    if current_file_dir_path.endswith(ep4c.P4TOOLS_FOLDER_NAME):
        # print("root_folder: " + current_file_dir_path)
        pass
    else:
        current_file_dir_path = os.path.dirname(current_file_dir_path)
        if current_file_dir_path.endswith(ep4c.P4TOOLS_FOLDER_NAME):
            # print("root_folder: " + current_file_dir_path)
            pass
        else:
            print("Root folder not found")
            return None
    return current_file_dir_path


def get_echo_p4_config():
    root_folder = get_root_folder()
    config_folder_path = os.path.join(root_folder, ep4c.CONFIG_FOLDER_NAME)
    echo_p4_ini_file_path = os.path.join(config_folder_path, ep4c.ECHO_P4_INI_FILE_NAME)
    echo_p4_ini_file = pathlib.Path(echo_p4_ini_file_path)
    if not echo_p4_ini_file.exists():
        print("Echo P4 file not found in the path: ", echo_p4_ini_file_path)
        return None
    echo_p4_user_config = configparser.ConfigParser()
    echo_p4_user_config.read(echo_p4_ini_file_path)
    return echo_p4_user_config


def get_p4_config():
    root_folder = get_root_folder()
    config_folder_path = os.path.join(root_folder, ep4c.CONFIG_FOLDER_NAME)
    p4_ini_file_path = os.path.join(config_folder_path, ep4c.P4_INI_FILE_NAME)
    p4_ini_file = pathlib.Path(p4_ini_file_path)
    if not p4_ini_file.exists():
        print("P4 file not found in the path: ", p4_ini_file_path)
        return None
    p4_config = configparser.ConfigParser()
    p4_config.read(p4_ini_file_path)
    return p4_config


def get_logger(echo_p4_config):
    log_folder_path = echo_p4_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_LOG_FOLDER_PATH]
    log_file_path = echo_p4_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_LOG_FILE_PATH]
    backup_log_file_path = echo_p4_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_BACKUP_LOG_FILE_PATH]
    ep4l = EchoP4Logger(log_folder_path, log_file_path, backup_log_file_path)
    return ep4l


def encrypt_password(plain_text_password):
    key = 'mt1ae3whDt_f0VPNW1A2Tdg_UO7mZnqHwhFCFoQicGE='.encode('utf-8')
    # key = Fernet.generate_key()
    print("key: " + key.decode('utf-8'))
    fernet = Fernet(key)
    encrypted_password_bytes = fernet.encrypt(plain_text_password.encode())
    encrypted_password = encrypted_password_bytes.decode('utf-8')
    return encrypted_password


def decrypt_password(encrypted_password):
    key = 'mt1ae3whDt_f0VPNW1A2Tdg_UO7mZnqHwhFCFoQicGE='.encode('utf-8')
    # key = Fernet.generate_key()
    fernet = Fernet(key)
    decrypted_password = fernet.decrypt(encrypted_password).decode()
    return decrypted_password
