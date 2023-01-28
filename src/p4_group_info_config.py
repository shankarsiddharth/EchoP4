import configparser
import os
import pathlib
import platform
import sys
import threading

import dearpygui.dearpygui as dpg
from P4 import P4, P4Exception
from dearpygui_ext import themes

import echo_p4_constants as ep4c
import p4_tools_helper as p4th
from echo_p4_logger import EchoP4Logger

log = EchoP4Logger()


class P4GroupInfoConfigController(object):

    @staticmethod
    def try_login(user, password, port, client=None):
        root_folder_path = p4th.get_root_folder()
        project_folder_path = os.path.dirname(root_folder_path)
        workspace_root_folder_path = os.path.dirname(project_folder_path)

        result = dict()
        result['workspace_found'] = False
        result['login_success'] = False
        result['message'] = 'Please check your credentials(user and password) and try again.'
        result['workspaces'] = list()
        result['current_workspace'] = ''

        p4 = P4()
        p4.user = user
        p4.password = password
        p4.port = port

        try:
            # p4.client = client
            p4.connect()
            p4.run_login()

            result['login_success'] = True

            workspaces = p4.run("workspaces", "-u", p4.user)  # Get the user's workspaces
            if len(workspaces) == 0:
                result['message'] = 'No workspace found for the user: ' + p4.user
            else:
                host_name = platform.node()
                for workspace in workspaces:
                    if host_name == workspace['Host']:
                        result['workspaces'].append(workspace)
                for workspace in result['workspaces']:
                    workspace_root = workspace['Root']
                    workspace_root_path = pathlib.Path(workspace_root)
                    if workspace_root_path.exists():
                        if str(workspace_root_folder_path) == str(workspace_root_path):
                            result['current_workspace'] = workspace['client']
                            result['workspace_found'] = True
                            break
                if not result['workspace_found']:
                    result['message'] = 'No valid workspace found for the user: ' + p4.user + ' in the current machine: ' + host_name
            p4.disconnect()
        except P4Exception as e:
            log.error(e)
        finally:
            if p4.connected():
                p4.disconnect()
            return result

    @staticmethod
    def try_initializing_p4_config(echo_p4_config, user_data):
        result = dict()
        result['success'] = False
        result['message'] = 'Error occurred while initializing the p4 config file.'
        default_p4_config_file_path = echo_p4_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_DEFAULT_P4_INI_FILE_PATH]
        p4_config_file_path = echo_p4_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_P4_INI_FILE_PATH]
        log.info("Checking for p4 config file...")
        p4_config_file = pathlib.Path(p4_config_file_path)
        if p4_config_file.exists():
            log.info('P4 config file already exists: ' + p4_config_file_path)
            log.info('Removing the existing P4 config file: ' + p4_config_file_path)
            os.remove(p4_config_file_path)
        default_p4_config_file = pathlib.Path(default_p4_config_file_path)
        log.info("Checking for default p4 config file...")
        if not default_p4_config_file.exists():
            log.error('Default P4 config file does not exist: ' + default_p4_config_file_path)
            return result
        log.info("Default p4 config file found.")
        log.info("Reading default p4 config file...")
        user_p4_config = configparser.ConfigParser()
        user_p4_config.read(default_p4_config_file_path)
        p4ignore_file = user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4IGNORE]
        user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PORT] = user_data['server']
        user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4USER] = user_data['user']
        user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4CLIENT] = user_data['workspace']
        log.info("Encrypting the password...")
        encrypted_password = p4th.encrypt_password(user_data['password'])
        user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PASSWD] = encrypted_password
        log.info("Password encrypted.")
        log.info("Writing user p4 config file... %s", p4_config_file_path)
        with open(p4_config_file_path, 'w', encoding='UTF-8') as user_p4_config_file:
            user_p4_config.write(user_p4_config_file)
        log.info("User's p4 config file written.")
        result['success'] = True
        result['message'] = 'User P4 config file initialized successfully.'
        return result

    def p4_login(self, user_p4_config_data):
        p4_port = user_p4_config_data[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PORT]
        p4_user = user_p4_config_data[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4USER]
        encrypted_p4_password = user_p4_config_data[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PASSWD]
        p4_password = p4th.decrypt_password(encrypted_p4_password)
        return self.try_login(p4_user, p4_password, p4_port)


class P4GroupInfoUI(object):
    __minimum_width__ = 700
    __minimum_height__ = 500

    def __init__(self, user_echo_p4_config_data=None, p4_config_controller=None, viewport_width=__minimum_width__, viewport_height=__minimum_height__):
        if p4_config_controller is None:
            log.error("Invalid arguments passed to the P4ConfigUI constructor.")
            sys.exit(1)
        self.user_echo_p4_config = user_echo_p4_config_data
        self.p4_config_controller: P4GroupInfoConfigController = p4_config_controller

        # DearPyGUI's Viewport Constants
        if viewport_width is None or viewport_width <= self.__minimum_width__:
            viewport_width = self.__minimum_width__
        if viewport_height is None or viewport_height <= self.__minimum_height__:
            viewport_height = self.__minimum_height__
        self.VIEWPORT_WIDTH = viewport_width
        self.VIEWPORT_HEIGHT = viewport_height
        self.viewport_title = "Echo P4 Config UI"
        self.window_title = "Echo P4 Config UI Window"
        self.server_tag = "Server"
        self.user_tag = "User"
        self.password_tag = "Password"
        self.workspace_tag = "Workspace"
        self.simple_log_tag = "Log"
        self.login_tag = "Login"
        self.log_width = viewport_width - 50
        self.log_height = viewport_height - 325
        self.user_data = dict()
        self.auto_close_ui = False
        self.user_close_ui = False
        self.__init_ui__()

    def get_viewport_name(self):
        return self.viewport_title

    def get_window_name(self):
        return self.window_title

    def get_user_data(self):
        return self.user_data

    def close_ui(self):
        self.auto_close_ui = True

    def __user_login_clicked__(self, sender, data):
        server = dpg.get_value(self.server_tag)
        user = dpg.get_value(self.user_tag)
        password = dpg.get_value(self.password_tag)
        workspace = dpg.get_value(self.workspace_tag)

        if server is None or server == "":
            dpg.set_value(self.simple_log_tag, "Server is required.")
            return
        if user is None or user == "":
            dpg.set_value(self.simple_log_tag, "User is required.")
            return
        if password is None or password == "":
            dpg.set_value(self.simple_log_tag, "Password is required.")
            return

        self.user_data = {"server": server.strip(), "user": user.strip(), "password": password, "workspace": ''}
        log_text = "Connecting to server with the data provided..."
        dpg.set_value(self.simple_log_tag, log_text)
        log.info(log_text)
        dpg.configure_item(self.login_tag, enabled=False, show=False)

        result = self.p4_config_controller.try_login(self.user_data['user'], self.user_data['password'], self.user_data['server'], workspace)

        if not result['workspace_found']:
            dpg.set_value(self.simple_log_tag, result['message'])
            log.error(result['message'])
            dpg.configure_item(self.login_tag, enabled=True, show=True)
            return

        self.user_data['workspace'] = result['current_workspace']
        log_text = "Login successful. Successfully connected to server with the data provided."
        dpg.set_value(self.simple_log_tag, log_text)
        log.info(log_text)

        result = self.p4_config_controller.try_initializing_p4_config(self.user_echo_p4_config, self.user_data)
        if not result['success']:
            dpg.set_value(self.simple_log_tag, result['message'])
            log.error(result['message'])
            dpg.configure_item(self.login_tag, enabled=True, show=True)
            return

        self.auto_close_ui = True

    def __exit_callback__(self):
        if not self.auto_close_ui:
            log.info("User Closed the P4ConfigUI.")
            self.user_close_ui = True

    def __init_ui__(self):
        dpg.create_context()

        dark_theme_id = themes.create_theme_imgui_dark()
        dpg.bind_theme(dark_theme_id)

        dpg.configure_app(manual_callback_management=sys.flags.dev_mode)

        dpg.create_viewport(title=self.viewport_title, width=self.VIEWPORT_WIDTH, height=self.VIEWPORT_HEIGHT)

        dpg.set_exit_callback(callback=self.__exit_callback__)

        with dpg.window(label=self.window_title, tag=self.window_title, no_title_bar=False, no_close=True):
            dpg.add_text("Server")
            dpg.add_input_text(tag=self.server_tag, default_value="ssl:halo.eng.utah.edu:1666", hint="server:port")
            dpg.add_text("User")
            dpg.add_input_text(tag=self.user_tag, default_value="")
            dpg.add_text("Password")
            dpg.add_input_text(tag=self.password_tag, default_value="", password=True)
            # dpg.add_text("Workspace")
            # dpg.add_input_text(tag=self.workspace_tag, default_value="")
            dpg.add_spacer(height=5)
            dpg.add_button(label="Login", tag=self.login_tag, callback=self.__user_login_clicked__)
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            dpg.add_text("Log")
            dpg.add_input_text(tag=self.simple_log_tag, password=False, multiline=True, width=self.log_width, height=self.log_height, readonly=True,
                               default_value="Enter the details and click Login to connect to the server.")

        dpg.setup_dearpygui()
        dpg.show_viewport()

        dpg.set_primary_window(self.window_title, True)

        # below replaces, start_dearpygui()
        while dpg.is_dearpygui_running():

            if sys.flags.dev_mode:
                jobs = dpg.get_callback_queue()  # retrieves and clears queue
                dpg.run_callbacks(jobs)

            dpg.render_dearpygui_frame()

            if self.auto_close_ui:
                break

        dpg.destroy_context()


class P4GroupInfoConfig(object):

    def init_and_render_ui(self, user_echo_p4_config_data):
        self.p4_config_ui = P4GroupInfoUI(user_echo_p4_config_data=user_echo_p4_config_data, p4_config_controller=self.p4_config_controller)

    def __init__(self, user_echo_p4_config_data=None):
        self.p4_ini_file = None
        self.p4_ini_file_path = None
        self.p4_config_controller = P4GroupInfoConfigController()
        if user_echo_p4_config_data is None:
            return
        self.p4_config_ui = None

        dpg_thread = threading.Thread(target=self.init_and_render_ui, args=[user_echo_p4_config_data])
        dpg_thread.start()
        dpg_thread.join()

        if self.p4_config_ui is not None:
            if self.p4_config_ui.user_close_ui:
                sys.exit(0)

    def get_user_data(self):
        return self.p4_config_ui.get_user_data()

    def p4_login(self, user_p4_config_data=None):
        if user_p4_config_data is None:
            return False
        result = self.p4_config_controller.p4_login(user_p4_config_data=user_p4_config_data)
        if not result['login_success']:
            log.error(result['message'])
            return False

        if not result['workspace_found']:
            log.error(result['message'])
            return False

        return True

    def delete_user_p4_config_file(self):
        self.p4_ini_file_path = p4th.get_user_p4_config_file_path()
        self.p4_ini_file = pathlib.Path(self.p4_ini_file_path)
        if not self.p4_ini_file.exists():
            return True

        try:
            log.info("Trying to delete the P4 Config file : " + self.p4_ini_file_path)
            os.remove(self.p4_ini_file_path)
            log.info("Successfully deleted the P4 Config file : " + self.p4_ini_file_path)
            return True
        except OSError as e:
            log.error("Error while deleting P4 Config file : ", e)
            sys.exit(0)

    def close_ui(self):
        if self.p4_config_ui is None:
            return
        self.p4_config_ui.close_ui()


if __name__ == "__main__":
    P4GroupInfoConfig()
