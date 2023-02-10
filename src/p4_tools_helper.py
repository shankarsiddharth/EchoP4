import configparser
import os
import pathlib
import shutil

from cryptography.fernet import Fernet

import echo_p4_constants as ep4c

KEY_FOLDER_NAME = ".ep4dpg"
KEY_FILE_NAME = "ep4.key"

ASSETS_FOLDER_NAME = "assets"
FONTS_FOLDER_NAME = "fonts"
OPEN_SANS_FOLDER_NAME = "opensans"
DEFAULT_FONT_NAME = "OpenSans-Regular.ttf"
DEFAULT_FONT_SIZE = 18
DEFAULT_BOLD_FONT_NAME = "OpenSans-Bold.ttf"
DEFAULT_BOLD_FONT_SIZE = 16


def get_root_folder():
    bin_src_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder_path = os.path.dirname(bin_src_folder)
    return root_folder_path


def get_user_echo_p4_config_file_path():
    root_folder = get_root_folder()
    config_folder_path = os.path.join(root_folder, ep4c.CONFIG_FOLDER_NAME)
    echo_p4_ini_file_path = os.path.join(config_folder_path, ep4c.ECHO_P4_INI_FILE_NAME)
    return echo_p4_ini_file_path


def get_user_p4_config_file_path():
    root_folder = get_root_folder()
    config_folder_path = os.path.join(root_folder, ep4c.CONFIG_FOLDER_NAME)
    p4_ini_file_path = os.path.join(config_folder_path, ep4c.P4_INI_FILE_NAME)
    return p4_ini_file_path


def get_user_p4_group_config_file_path():
    root_folder = get_root_folder()
    config_folder_path = os.path.join(root_folder, ep4c.CONFIG_FOLDER_NAME)
    p4_group_ini_file_path = os.path.join(config_folder_path, ep4c.P4_GROUP_INI_FILE_NAME)
    return p4_group_ini_file_path


def get_group_info_file_path():
    root_folder = get_root_folder()
    data_folder_path = os.path.join(root_folder, ep4c.DATA_FOLDER_NAME)
    group_info_file_path = os.path.join(data_folder_path, ep4c.GROUP_INFO_JSON_FILE_NAME)
    return group_info_file_path


def get_group_members_info_file_path():
    root_folder = get_root_folder()
    data_folder_path = os.path.join(root_folder, ep4c.DATA_FOLDER_NAME)
    group_members_info_file_path = os.path.join(data_folder_path, ep4c.GROUP_MEMBERS_INFO_JSON_FILE_NAME)
    return group_members_info_file_path


def get_user_echo_p4_config_data():
    echo_p4_ini_file_path = get_user_echo_p4_config_file_path()
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


def get_user_p4_group_config_data():
    p4_group_ini_file_path = get_user_p4_group_config_file_path()
    p4_group_ini_file = pathlib.Path(p4_group_ini_file_path)
    if not p4_group_ini_file.exists():
        print("P4 Group file not found in the path: ", p4_group_ini_file_path)
        return None
    p4_group_config = configparser.ConfigParser()
    p4_group_config.read(p4_group_ini_file_path)
    return p4_group_config


def is_group_info_present():
    group_info_file_path = get_group_info_file_path()
    group_info_file = pathlib.Path(group_info_file_path)
    if not group_info_file.exists():
        return False
    return True


def is_group_members_info_present():
    group_members_info_file_path = get_group_members_info_file_path()
    group_members_info_file = pathlib.Path(group_members_info_file_path)
    if not group_members_info_file.exists():
        return False
    return True


def generate_key():
    key = Fernet.generate_key()
    home_folder = pathlib.Path.home()
    app_folder = os.path.join(home_folder, KEY_FOLDER_NAME)
    key_file_path = os.path.join(app_folder, KEY_FILE_NAME)
    pathlib.Path(app_folder).mkdir(parents=True, exist_ok=True)
    with open(key_file_path, 'wb') as key_file:
        key_file.write(key)
    return key


def get_key():
    home_folder = pathlib.Path.home()
    app_folder = os.path.join(home_folder, KEY_FOLDER_NAME)
    key_file_path = os.path.join(app_folder, KEY_FILE_NAME)
    key_file = pathlib.Path(key_file_path)
    if not key_file.exists():
        return None
    with open(key_file_path, 'rb') as key_file:
        key = key_file.read()
    return key


def delete_key():
    home_folder = pathlib.Path.home()
    app_folder = os.path.join(home_folder, KEY_FOLDER_NAME)
    key_file_path = os.path.join(app_folder, KEY_FILE_NAME)
    key_file = pathlib.Path(key_file_path)
    if not key_file.exists():
        return
    key_file.unlink()


def encrypt_password(plain_text_password):
    key = generate_key()
    fernet = Fernet(key)
    encrypted_password_bytes = fernet.encrypt(plain_text_password.encode())
    encrypted_password = encrypted_password_bytes.decode('utf-8')
    return encrypted_password


def decrypt_password(encrypted_password):
    decrypted_password = ''
    key = get_key()
    if key is None:
        return decrypted_password
    try:
        fernet = Fernet(key)
        decrypted_password = fernet.decrypt(encrypted_password.encode()).decode()
    except BaseException as e:
        delete_key()
        # print("Unexpected error:", e)
    return decrypted_password


def reset_user_data():
    # Delete the user echo p4 config file
    echo_p4_ini_file_path = get_user_echo_p4_config_file_path()
    echo_p4_ini_file = pathlib.Path(echo_p4_ini_file_path)
    if echo_p4_ini_file.exists():
        os.remove(echo_p4_ini_file_path)
    # Delete the user p4 config file
    p4_ini_file_path = get_user_p4_config_file_path()
    p4_ini_file = pathlib.Path(p4_ini_file_path)
    if p4_ini_file.exists():
        os.remove(p4_ini_file_path)
    # Delete the user p4 group config file
    p4_group_ini_file_path = get_user_p4_group_config_file_path()
    p4_group_ini_file = pathlib.Path(p4_group_ini_file_path)
    if p4_group_ini_file.exists():
        os.remove(p4_group_ini_file_path)
    # Delete the group info file
    group_info_file_path = get_group_info_file_path()
    group_info_file = pathlib.Path(group_info_file_path)
    if group_info_file.exists():
        os.remove(group_info_file_path)
    # Delete the group members info file
    group_members_info_file_path = get_group_members_info_file_path()
    group_members_info_file = pathlib.Path(group_members_info_file_path)
    if group_members_info_file.exists():
        os.remove(group_members_info_file_path)
    # Delete the key file
    delete_key()
    # Delete DPG ini file
    root_folder = get_root_folder()
    config_folder_path = os.path.join(root_folder, ep4c.CONFIG_FOLDER_NAME)
    dpg_ini_file_path = os.path.join(config_folder_path, ep4c.DPG_INI_FILE_NAME)
    if dpg_ini_file_path is not None and dpg_ini_file_path != '':
        dpg_ini_file = pathlib.Path(dpg_ini_file_path)
        if dpg_ini_file.exists():
            os.remove(dpg_ini_file_path)


def get_dpg_ini_file_path():
    user_echo_p4_config = get_user_echo_p4_config_data()
    if user_echo_p4_config is None:
        return ''
    dpg_ini_file_path = user_echo_p4_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_DPG_INI_FILE_PATH]
    return dpg_ini_file_path


def get_default_dpg_ini_file_path():
    user_echo_p4_config = get_user_echo_p4_config_data()
    if user_echo_p4_config is None:
        return ''
    default_dpg_ini_file_path = user_echo_p4_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_DEFAULT_DPG_INI_FILE_PATH]
    return default_dpg_ini_file_path


def reset_to_default_layout():
    dpg_ini_file_path = get_dpg_ini_file_path()
    default_dpg_ini_file_path = get_default_dpg_ini_file_path()
    dpg_ini_file = pathlib.Path(dpg_ini_file_path)
    if dpg_ini_file.exists():
        os.remove(dpg_ini_file_path)
    shutil.copy(default_dpg_ini_file_path, dpg_ini_file_path)


def get_default_font_file_path():
    root_folder = get_root_folder()
    asset_folder = os.path.join(root_folder, ASSETS_FOLDER_NAME)
    font_folder = os.path.join(asset_folder, FONTS_FOLDER_NAME)
    opensans_font_folder = os.path.join(font_folder, OPEN_SANS_FOLDER_NAME)
    default_font_file_path = os.path.join(opensans_font_folder, DEFAULT_FONT_NAME)
    return default_font_file_path


def get_default_font_size():
    return DEFAULT_FONT_SIZE


def get_default_bold_font_file_path():
    root_folder = get_root_folder()
    asset_folder = os.path.join(root_folder, ASSETS_FOLDER_NAME)
    font_folder = os.path.join(asset_folder, FONTS_FOLDER_NAME)
    opensans_font_folder = os.path.join(font_folder, OPEN_SANS_FOLDER_NAME)
    default_font_file_path = os.path.join(opensans_font_folder, DEFAULT_BOLD_FONT_NAME)
    return default_font_file_path


def get_bold_default_font_size():
    return DEFAULT_BOLD_FONT_SIZE

