import os
import sys
import configparser
import pathlib

from cryptography.fernet import Fernet

import echo_p4_constants as ep4c


def get_root_folder():
    bin_src_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder_path = os.path.dirname(bin_src_folder)
    return root_folder_path


def get_user_echo_p4_config_data():
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


def get_user_p4_config_data():
    p4_ini_file_path = get_user_p4_config_file_path()
    p4_ini_file = pathlib.Path(p4_ini_file_path)
    if not p4_ini_file.exists():
        print("P4 file not found in the path: ", p4_ini_file_path)
        return None
    p4_config = configparser.ConfigParser()
    p4_config.read(p4_ini_file_path)
    return p4_config


def get_user_p4_config_file_path():
    root_folder = get_root_folder()
    config_folder_path = os.path.join(root_folder, ep4c.CONFIG_FOLDER_NAME)
    p4_ini_file_path = os.path.join(config_folder_path, ep4c.P4_INI_FILE_NAME)
    return p4_ini_file_path


# TODO: Key should be stored in a secure location, not in the code
# Generate a key and store it in a file when the application login is successful which is not in the code
# Generated key should be unique for each user
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
    decrypted_password = ''
    try:
        decrypted_password = fernet.decrypt(encrypted_password.encode()).decode()
    except:
        e = sys.exc_info()[0]
        print("Unexpected error:", sys.exc_info()[0])
    return decrypted_password
