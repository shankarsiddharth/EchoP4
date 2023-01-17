import os
import sys
import shutil
import configparser
import pathlib

import p4_tools_helper as p4th
import echo_p4_constants as ep4c
from echo_p4_logger import EchoP4Logger


ep4l = EchoP4Logger()


def initialize_logger(log_folder, log_file_path, backup_log_file_path):
    global ep4l
    ep4l = EchoP4Logger(log_folder, log_file_path, backup_log_file_path)


def main():

    p4tools_root_folder = p4th.get_root_folder()

    # Initialize the paths
    binary_folder_path = os.path.join(p4tools_root_folder, ep4c.BINARY_FOLDER_NAME)
    config_folder_path = os.path.join(p4tools_root_folder, ep4c.CONFIG_FOLDER_NAME)
    config_defaults_folder_path = os.path.join(config_folder_path, ep4c.CONFIG_DEFAULTS_FOLDER_NAME)
    data_folder_path = os.path.join(p4tools_root_folder, ep4c.DATA_FOLDER_NAME)
    data_defaults_folder_path = os.path.join(data_folder_path, ep4c.DATA_DEFAULTS_FOLDER_NAME)
    log_folder_path = os.path.join(p4tools_root_folder, ep4c.LOG_FOLDER_NAME)
    source_folder_path = os.path.join(p4tools_root_folder, ep4c.SOURCE_FOLDER_NAME)
    tools_folder_path = os.path.join(p4tools_root_folder, ep4c.TOOLS_FOLDER_NAME)
    tools_default_folder_path = os.path.join(tools_folder_path, ep4c.TOOLS_DEFAULTS_FOLDER_NAME)

    log_file_path = os.path.join(log_folder_path, ep4c.LOG_FILE_NAME)
    backup_log_file_path = os.path.join(log_folder_path, ep4c.BACKUP_LOG_FILE_NAME)

    default_dpg_ini_file_path = os.path.join(config_defaults_folder_path, ep4c.DEFAULT_DPG_INI_FILE_NAME)
    dpg_ini_file_path = os.path.join(config_folder_path, ep4c.DPG_INI_FILE_NAME)

    default_p4_ini_file_path = os.path.join(config_defaults_folder_path, ep4c.DEFAULT_P4_INI_FILE_NAME)
    p4_ini_file_path = os.path.join(config_folder_path, ep4c.P4_INI_FILE_NAME)

    team_members_json_file_path = os.path.join(data_folder_path, ep4c.TEAM_MEMBERS_JSON_FILE_NAME)

    default_p4_custom_tools_xml_file_path = os.path.join(tools_default_folder_path, ep4c.DEFAULT_P4_CUSTOM_TOOLS_XML_FILE_NAME)
    p4_custom_tools_xml_file_path = os.path.join(tools_folder_path, ep4c.P4_CUSTOM_TOOLS_XML_FILE_NAME)

    default_echo_p4_ini_file_path = os.path.join(config_defaults_folder_path, ep4c.DEFAULT_ECHO_P4_INI_FILE_NAME)
    echo_p4_ini_file_path = os.path.join(config_folder_path, ep4c.ECHO_P4_INI_FILE_NAME)

    # Initialize the logger
    log_folder = pathlib.Path(log_folder_path)
    if not log_folder.exists():
        # Folder does not exist, create it
        print("Log folder does not exist. Creating it.")
        print("Creating log folder: " + log_folder_path)
        try:
            os.makedirs(log_folder_path)
        except OSError:
            print("Creation of the log folder failed.")
            input("Press any key to exit...")
            sys.exit(1)
    print("Log folder exists.")
    print("Initializing logger...")
    initialize_logger(log_folder, log_file_path, backup_log_file_path)
    global ep4l
    ep4l.info("Logger Initialized.")

    # Check for the default echo p4 config files
    default_echo_p4_ini_file = pathlib.Path(default_echo_p4_ini_file_path)
    if not default_echo_p4_ini_file.exists():
        ep4l.error("Default echo p4 config file does not exist.")
        input("Press any key to exit...")
        sys.exit(1)

    # Check for the default p4 config files
    default_p4_ini_file = pathlib.Path(default_p4_ini_file_path)
    if not default_p4_ini_file.exists():
        ep4l.error("Default p4 config file does not exist.")
        input("Press any key to exit...")
        sys.exit(1)

    # Check for the default DearPyGUI config files
    default_dpg_ini_file = pathlib.Path(default_dpg_ini_file_path)
    if not default_dpg_ini_file.exists():
        ep4l.error("Default DearPyGUI config file does not exist.")
        input("Press any key to exit...")
        sys.exit(1)

    # Check for the Default P4 Custom Tool XML file
    default_p4_custom_tools_xml_file = pathlib.Path(default_p4_custom_tools_xml_file_path)
    if not default_p4_custom_tools_xml_file.exists():
        ep4l.error("Default P4 Custom Tools XML file does not exist.")
        input("Press any key to exit...")
        sys.exit(1)

    # Process Echo P4 config file
    ep4l.info("Reading default echo p4 config file...")
    echo_p4_user_config = configparser.ConfigParser()
    echo_p4_user_config.read(default_echo_p4_ini_file_path)

    ep4l.info("Populating values for key from default echo p4 config file...")
    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION] = {}
    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_P4TOOLS_FOLDER_PATH] = str(p4tools_root_folder)
    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_BINARY_FOLDER_PATH] = str(binary_folder_path)
    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_CONFIG_FOLDER_PATH] = str(config_folder_path)
    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_CONFIG_DEFAULTS_FOLDER_PATH] = str(config_defaults_folder_path)
    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_DATA_FOLDER_PATH] = str(data_folder_path)
    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_DATA_DEFAULTS_FOLDER_PATH] = str(data_defaults_folder_path)
    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_LOG_FOLDER_PATH] = str(log_folder_path)
    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_SOURCE_FOLDER_PATH] = str(source_folder_path)
    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_TOOLS_FOLDER_PATH] = str(tools_folder_path)
    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_TOOLS_DEFAULTS_FOLDER_PATH] = str(tools_default_folder_path)

    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_LOG_FILE_PATH] = str(log_file_path)
    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_BACKUP_LOG_FILE_PATH] = str(backup_log_file_path)

    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_DEFAULT_DPG_INI_FILE_PATH] = str(default_dpg_ini_file_path)
    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_DPG_INI_FILE_PATH] = str(dpg_ini_file_path)

    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_DEFAULT_P4_INI_FILE_PATH] = str(default_p4_ini_file_path)
    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_P4_INI_FILE_PATH] = str(p4_ini_file_path)

    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_TEAM_MEMBERS_JSON_FILE_PATH] = str(team_members_json_file_path)

    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_DEFAULT_P4_CUSTOM_TOOLS_XML_FILE_PATH] = str(default_p4_custom_tools_xml_file_path)
    echo_p4_user_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_P4_CUSTOM_TOOLS_XML_FILE_PATH] = str(p4_custom_tools_xml_file_path)
    ep4l.info("Values for keys assigned for the config file...")

    ep4l.info("Checking for echo p4 config file...")
    # Remove the echo p4 ini file if it exists
    echo_p4_ini_file = pathlib.Path(echo_p4_ini_file_path)
    if echo_p4_ini_file.exists():
        # file exists
        ep4l.info("echo p4 ini file exists. Removing it.")
        os.remove(echo_p4_ini_file_path)

    ep4l.info("Writing User's echo p4 config file...")
    with open(echo_p4_ini_file_path, 'w', encoding='UTF-8') as echo_p4_config_file:
        echo_p4_user_config.write(echo_p4_config_file)
    ep4l.info("User's echo p4 config file written.")

    # initialize_p4_config_file(default_p4_ini_file_path, p4_ini_file_path)

    ep4l.info("Checking for DearPyGUI ini config file...")
    # Remove the DearPyGUI ini config file if it exists
    dpg_ini_file = pathlib.Path(dpg_ini_file_path)
    if dpg_ini_file.exists():
        # file exists
        ep4l.info("DearPyGUI ini config file exists. Removing it.")
        os.remove(dpg_ini_file_path)
    ep4l.info("Writing DearPyGUI ini config file...")
    shutil.copyfile(default_dpg_ini_file_path, dpg_ini_file_path)
    ep4l.info("DearPyGUI ini config file written.")

    # Read the Default P4 Custom Tool XML file
    ep4l.info("Reading Default P4 Custom Tool XML file...")
    default_xml_file_lines = list()
    with open(default_p4_custom_tools_xml_file_path, 'r', encoding='UTF-8') as default_xml_file:
        default_xml_file_lines = default_xml_file.readlines()
    if len(default_xml_file_lines) == 0:
        ep4l.error("P4 Custom Tools XML file is empty.")
        input("Press any key to exit...")
        sys.exit(1)
    line_number = 0
    for line in default_xml_file_lines:
        if str(line.strip()).startswith("<InitDir>"):
            ep4l.info("Replacing Start Directory for the P4 Custom Tool in the XML file...")
            default_xml_file_lines[line_number] = "   <InitDir>" + str(p4tools_root_folder) + "</InitDir>\n"
            ep4l.info("Replaced the Start Directory for the P4 Custom Tool in the XML file.")
        line_number += 1
    ep4l.info("Writing User's P4 Custom Tool XML file...")
    with open(p4_custom_tools_xml_file_path, 'w', encoding='UTF-8') as xml_file:
        for line in default_xml_file_lines:
            xml_file.write(f"{line}")
    ep4l.info("User's P4 Custom Tool XML file written.")


if __name__ == "__main__":
    main()
    ep4l.info("Initial Setup Completed.")
    input("Press any key to exit...")
    sys.exit(0)
