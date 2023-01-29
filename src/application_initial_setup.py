import sys

import p4_tools_helper as p4th
from app_globals import log
from echo_p4_config import EchoP4Config
from p4_config import P4Config
from p4_group_info_config import P4GroupInfoConfig


class ApplicationInitialSetup(object):

    def __init__(self):
        # Log the dev mode flag
        print("sys.flags.dev_mode : %s", sys.flags.dev_mode)

        self.user_echo_p4_config_data = p4th.get_user_echo_p4_config_data()
        self.user_p4_config_data = p4th.get_user_p4_config_data()
        self.user_p4_group_config_data = p4th.get_user_p4_group_config_data()
        self.check_user_echo_p4_config()
        self.check_user_p4_config()
        self.check_user_p4_group_config()

    def check_user_echo_p4_config(self):
        if self.user_echo_p4_config_data is None:
            log.info("No application config file found.")
            log.info("Trying to create a new config file for the current user...")
            user_echo_p4_config = EchoP4Config()
            self.user_echo_p4_config_data = p4th.get_user_echo_p4_config_data()
            log.info("New application config file created for the current user.")
        else:
            log.info("Application Config file found. Checking for P4 user config...")

    def check_user_p4_config(self):
        if self.user_p4_config_data is None:
            log.info("No P4 config file found.")
            log.info("Trying to create a new P4 config file for the current user...")
            user_p4_config = P4Config(user_echo_p4_config_data=self.user_echo_p4_config_data)
            self.user_p4_config_data = p4th.get_user_p4_config_data()
            log.info("New P4 config file created for the current user.")
        else:
            log.info("P4 Config file found.")
            user_p4_config = P4Config()
            is_login_success = user_p4_config.p4_login(user_p4_config_data=self.user_p4_config_data)
            while not is_login_success:
                log.info("P4 login failed with the saved data.")
                user_p4_config.delete_user_p4_config_file()
                log.info("Resetting the application config file...")
                user_echo_p4_config = EchoP4Config()
                self.user_echo_p4_config_data = p4th.get_user_echo_p4_config_data()
                log.info("Trying to create a new P4 config file for the current user...")
                user_p4_config = P4Config(user_echo_p4_config_data=self.user_echo_p4_config_data)
                self.user_p4_config_data = p4th.get_user_p4_config_data()
                is_login_success = user_p4_config.p4_login(user_p4_config_data=self.user_p4_config_data)

        log.info('User Login Successful.')

    def check_user_p4_group_config(self):
        if self.user_p4_group_config_data is None:
            log.info("No P4 Group Config file found.")
            log.info("Trying to create a new P4 Group config file for the current user...")
            self.check_user_p4_config()
            group_info_config = P4GroupInfoConfig(self.user_echo_p4_config_data, self.user_p4_config_data)
            if group_info_config.is_group_list_empty():
                log.error("No groups found in the P4 server.")
                log.error("Please create a group for the current user in the P4 server and then try again.")
                sys.exit(0)
            self.user_p4_group_config_data = p4th.get_user_p4_group_config_data()
            log.info("New P4 Group config file created for the current user.")
        else:
            log.info("P4 Group Config file found.")
