import shutil
import sys

import p4_tools_helper as p4th
from app_error import AppError
from app_globals import log
from echo_p4_config import EchoP4Config
from p4_config import P4Config
from p4_group_info_config import P4GroupInfoConfig


class ApplicationInitialSetup(object):

    def __init__(self):
        # Log the dev mode flag
        # print("sys.flags.dev_mode : %s", sys.flags.dev_mode)

        self.user_echo_p4_config: EchoP4Config = EchoP4Config()
        self.user_p4_config: P4Config = P4Config()
        self.user_p4_group_info_config: P4GroupInfoConfig = P4GroupInfoConfig()

        self.user_echo_p4_config_data = p4th.get_user_echo_p4_config_data()
        self.user_p4_config_data = p4th.get_user_p4_config_data()
        self.user_p4_group_config_data = p4th.get_user_p4_group_config_data()

        self.check_user_echo_p4_config()
        self.check_tools_xml_file()
        self.check_user_p4_config()
        self.check_user_p4_group_config()
        self.check_group_member_data()

    def check_user_echo_p4_config(self):
        if self.user_echo_p4_config_data is None:
            log.info("No application config file found.")
            log.info("Trying to create a new config file for the current user...")
            self.user_echo_p4_config.create_new_config_file()
            self.user_echo_p4_config_data = p4th.get_user_echo_p4_config_data()
            log.info("New application config file created for the current user.")
        else:
            log.info("Application Config file found. Checking for P4 user config...")

    def check_user_p4_config(self):
        if self.user_p4_config_data is None:
            log.info("No P4 config file found.")
            if p4th.get_key() is not None:
                log.info("Previous Key found. Clearing the previous key...")
                p4th.delete_key()
                log.info("Previous Key cleared.")
            log.info("Trying to create a new P4 config file for the current user...")
            self.user_p4_config = P4Config(user_echo_p4_config_data=self.user_echo_p4_config_data)
            self.user_p4_config_data = p4th.get_user_p4_config_data()
            log.info("New P4 config file created for the current user.")
        else:
            log.info("P4 Config file found.")
            user_p4_config = P4Config()
            is_login_success = user_p4_config.p4_login(user_p4_config_data=self.user_p4_config_data)
            if not is_login_success:
                user_message = "P4 login failed with the saved data.\nReset the User Data, re-open the application and try again."
                raise AppError(user_message, should_reset_data=True)
            # while not is_login_success:
            #     log.info("P4 login failed with the saved data.")
            #     user_p4_config.delete_user_p4_config_file()
            #     p4th.delete_key()
            #     log.info("Resetting the application config file...")
            #     self.user_echo_p4_config = EchoP4Config()
            #     self.user_echo_p4_config_data = p4th.get_user_echo_p4_config_data()
            #     log.info("Trying to create a new P4 config file for the current user...")
            #     user_p4_config = P4Config(user_echo_p4_config_data=self.user_echo_p4_config_data)
            #     self.user_p4_config_data = p4th.get_user_p4_config_data()
            #     is_login_success = user_p4_config.p4_login(user_p4_config_data=self.user_p4_config_data)

        log.info('User Login Successful.')

    def check_user_p4_group_config(self):
        if self.user_p4_group_config_data is None:
            log.info("No P4 Group Config file found.")
            log.info("Trying to create a new P4 Group config file for the current user...")
            # self.check_user_p4_config()
            self.user_p4_group_info_config = P4GroupInfoConfig(self.user_echo_p4_config_data, self.user_p4_config_data)
            if self.user_p4_group_info_config.is_login_success():
                if self.user_p4_group_info_config.is_group_list_empty():
                    exception_message = "No groups found in the P4 server."
                    exception_message += "\nPlease create a group for the current user in the P4 server and then try again."
                    raise AppError(exception_message)
            else:
                log.info("P4 login failed with the saved credentials.")
                log.info("Resetting the P4 Config file...")
                self.user_p4_config.delete_user_p4_config_file()
                p4th.delete_key()
                self.user_p4_config_data = p4th.get_user_p4_config_data()
                # self.check_user_p4_config()
            self.user_p4_group_config_data = p4th.get_user_p4_group_config_data()
            log.info("New P4 Group config file created for the current user.")
        else:
            log.info("P4 Group Config file found.")
            group_name = self.user_p4_group_info_config.get_group_name(self.user_p4_group_config_data)
            log.info("Group Name : %s", group_name)

    def check_group_member_data(self):
        if not (p4th.is_group_info_present() and p4th.is_group_members_info_present()):
            log.info("Group info or Group members info not found.")
            log.info("Removing the P4 Group Config file...")
            self.user_p4_group_info_config.delete_user_p4_group_config_file()
            self.user_p4_group_config_data = p4th.get_user_p4_group_config_data()
            log.info("Trying to create a new P4 Group config file for the current user...")
            self.check_user_p4_group_config()
        log.info("Group info and Group members info found.")
        pass

    def check_tools_xml_file(self):
        if not p4th.is_user_tools_xml_file_present():
            log.info("User Tools XML file not found.")
            log.info("Trying to create a new Tools XML file for the current user...")
            root_folder = p4th.get_root_folder()
            default_p4_custom_tools_xml_file_path = p4th.get_default_tools_xml_file_path()
            p4_custom_tools_xml_file_path = p4th.get_user_tools_xml_file_path()
            self.user_echo_p4_config.process_tools_xml_file(default_p4_custom_tools_xml_file_path, p4_custom_tools_xml_file_path, root_folder)
