import configparser
import os
import pathlib
import platform
import sys
import threading
import re

import dearpygui.dearpygui as dpg
from P4 import P4, P4Exception
from dearpygui_ext import themes

import echo_p4_constants as ep4c
import p4_tools_helper as p4th
from app_error import AppError
from app_exit import AppExit
from app_globals import log


class P4ConfigController(object):

    def __init__(self):
        self.exception_message = ''
        self.result = dict()
        self.is_trusted_fingerprint = True
        self.fingerprint = ''

    def try_login(self, user, password, port, trust_fingerprint=False):
        regex = r"([0-9a-fA-F]{2}:){19}[0-9a-fA-F]{2}"

        root_folder_path = p4th.get_root_folder()
        project_folder_path = os.path.dirname(root_folder_path)
        workspace_root_folder_path = os.path.dirname(project_folder_path)

        self.result = dict()
        self.is_trusted_fingerprint = True
        self.result['workspace_found'] = False
        self.result['login_success'] = False
        self.result['message'] = 'Please check your credentials(user and password) and try again.'
        self.result['workspaces'] = list()
        self.result['current_workspace'] = ''

        p4 = P4()
        p4.user = user
        p4.password = password
        p4.port = port

        try:
            # p4.client = client
            p4.connect()
            if trust_fingerprint and self.fingerprint != '':
                p4.run("trust", "-i", self.fingerprint)
            p4.run_login()

            self.result['login_success'] = True

            workspaces = p4.run("workspaces", "-u", p4.user)  # Get the user's workspaces
            if len(workspaces) == 0:
                self.result['message'] = 'No workspace found for the user: ' + p4.user
            else:
                host_name = platform.node()
                for workspace in workspaces:
                    if host_name == workspace['Host']:
                        self.result['workspaces'].append(workspace)
                for workspace in self.result['workspaces']:
                    workspace_root = workspace['Root']
                    workspace_root_path = pathlib.Path(workspace_root)
                    if workspace_root_path.exists():
                        if str(workspace_root_folder_path) == str(workspace_root_path):
                            self.result['current_workspace'] = workspace['client']
                            self.result['workspace_found'] = True
                            break
                if not self.result['workspace_found']:
                    self.result['message'] = 'No valid workspace found for the user: ' + p4.user + ' in the current machine: ' + host_name
            p4.disconnect()
        except P4Exception as e:
            log.exception(e)
            exception_string = str(e)
            matches_list = list()
            matches = re.finditer(regex, exception_string, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                matches_list.append(match.group())
            if len(matches_list) == 1:
                self.fingerprint = matches_list[0]
                self.is_trusted_fingerprint = False
            if "ssl connect" in str(e).lower():
                self.result['message'] = 'Unable to connect to the server. \nPlease check the network/internet connection and the server port and try again.' + "\n\n" + str(e)
            elif "identification" in str(e).lower() or "authenticity" in str(e).lower():
                self.result['message'] = 'Unable to login to the server. \nPlease check the user credentials and try again.' + "\n\n" + str(e)
                self.result['message'] += "\n" + "If you are trying to connect to a server for the first time \n(or) \nif the server's certificate has changed recently, " \
                                                 "\nplease accept the fingerprint and try again."
            elif "connect" in str(e).lower():
                self.result['message'] = 'Unable to connect to the server. \nPlease check the network/internet connection.' \
                                         '\n Please, check the server and the port you are trying to connect to and try again.' + "\n\n" + str(e)
            elif "run" in str(e).lower():
                self.result['message'] = 'Unable to login to the server. \nPlease check the user credentials and try again.' + "\n\n" + str(e)
        except BaseException as e:
            log.exception(e)
            self.result['message'] = 'Exception occurred while trying to login to the server.'
            self.exception_message = "\n" + str(e)
        finally:
            if p4.connected():
                p4.disconnect()
            return self.result

    def try_initializing_p4_config(self, echo_p4_config, user_data):
        try:
            self.result = dict()
            self.result['success'] = False
            self.result['message'] = 'Error occurred while initializing the p4 config file.'
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
                return self.result
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
            self.result['success'] = True
            self.result['message'] = 'User P4 config file initialized successfully.'
        except BaseException as e:
            log.exception(e)
            self.result['message'] = 'Exception occurred while trying to login to the server.'
            self.exception_message = "\n" + str(e)
        finally:
            return self.result

    def p4_login(self, user_p4_config_data):
        try:
            p4_port = user_p4_config_data[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PORT]
            p4_user = user_p4_config_data[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4USER]
            encrypted_p4_password = user_p4_config_data[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PASSWD]
            p4_password = p4th.decrypt_password(encrypted_p4_password)
        except BaseException as e:
            log.exception(e)
            self.result['message'] = 'Exception occurred while trying to login to the server.'
            self.exception_message = "\n" + str(e)
            self.result = dict()
            self.result['login_success'] = False
            return self.result
        return self.try_login(p4_user, p4_password, p4_port)


class P4ConfigUI(threading.Thread):
    __minimum_width__ = 700
    __minimum_height__ = 500

    def __init__(self, user_echo_p4_config_data=None, p4_config_controller=None, viewport_width=__minimum_width__, viewport_height=__minimum_height__):
        super().__init__()

        self.exception = None

        if p4_config_controller is None:
            self.p4_config_controller = None
            return

        self.user_echo_p4_config_data = user_echo_p4_config_data
        self.p4_config_controller: P4ConfigController = p4_config_controller

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
        self.trust_fingerprint_tag = "Trust Fingerprint"
        self.log_width = viewport_width - 50
        self.log_height = viewport_height - 325
        self.user_data = dict()
        self.auto_close_ui = False
        self.user_close_ui = False
        self.reset_user_data = False
        self.exception_message = ''

    def run(self):
        try:
            if self.p4_config_controller is None:
                exception_message = "Invalid arguments passed to the P4ConfigUI constructor."
                raise AppError(exception_message)
            self.__init_ui__()
        except BaseException as e:
            self.exception = e

    def join(self, **kwargs):
        threading.Thread.join(self, **kwargs)
        # since join() returns in caller thread we re-raise the caught exception if any was caught
        if self.exception:
            raise self.exception

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

        if self.p4_config_controller.is_trusted_fingerprint:
            result = self.p4_config_controller.try_login(self.user_data['user'], self.user_data['password'], self.user_data['server'])
        else:
            result = self.p4_config_controller.try_login(self.user_data['user'], self.user_data['password'], self.user_data['server'], trust_fingerprint=True)

        if not self.p4_config_controller.is_trusted_fingerprint:
            fingerprint_string = self.p4_config_controller.fingerprint
            checkbox_label = "Trust fingerprint: " + fingerprint_string + " ?"
            login_label_text = "Trust fingerprint & Login"
            dpg.configure_item(self.trust_fingerprint_tag, enabled=True, show=True, label=checkbox_label)
            dpg.configure_item(self.login_tag, enabled=True, show=True, label=login_label_text)
            dpg.set_value(self.simple_log_tag, result['message'])
            return

        if not result['login_success']:
            dpg.configure_item(self.login_tag, enabled=True, show=True)
            dpg.set_value(self.simple_log_tag, result['message'])
            return

        if not result['workspace_found']:
            dpg.set_value(self.simple_log_tag, result['message'])
            dpg.configure_item(self.login_tag, enabled=True, show=True)
            self.reset_user_data = True
            self.exception_message = result['message']
            self.auto_close_ui = True
            return

        self.user_data['workspace'] = result['current_workspace']
        log_text = "Login successful. Successfully connected to server with the data provided."
        dpg.set_value(self.simple_log_tag, log_text)
        log.info(log_text)

        result = self.p4_config_controller.try_initializing_p4_config(self.user_echo_p4_config_data, self.user_data)

        if not result['success']:
            dpg.set_value(self.simple_log_tag, result['message'])
            dpg.configure_item(self.login_tag, enabled=True, show=True)
            self.reset_user_data = True
            self.exception_message = result['message'] + self.p4_config_controller.exception_message

        self.auto_close_ui = True

    def __exit_callback__(self):
        if not self.auto_close_ui:
            log.info("User Closed the P4ConfigUI.")
            self.user_close_ui = True

    def __enter_clicked__(self, sender, data):
        self.__user_login_clicked__(None, None)

    def __init_ui__(self):

        dpg.create_context()

        dark_theme_id = themes.create_theme_imgui_dark()
        dpg.bind_theme(dark_theme_id)

        dpg.configure_app(manual_callback_management=sys.flags.dev_mode)

        dpg.create_viewport(title=self.viewport_title, width=self.VIEWPORT_WIDTH, height=self.VIEWPORT_HEIGHT)

        dpg.set_exit_callback(callback=self.__exit_callback__)

        # add a font registry
        with dpg.font_registry():
            # first argument ids the path to the .ttf or .otf file
            default_font = dpg.add_font(p4th.get_default_font_file_path(), p4th.get_default_font_size())

        dpg.bind_font(default_font)

        with dpg.handler_registry():
            dpg.add_key_press_handler(key=dpg.mvKey_Return, callback=self.__enter_clicked__)

        with dpg.window(label=self.window_title, tag=self.window_title, no_title_bar=False, no_close=True):
            dpg.add_text("Server")
            dpg.add_input_text(tag=self.server_tag, default_value="", hint="server:port")
            dpg.add_text("User")
            dpg.add_input_text(tag=self.user_tag, default_value="")
            dpg.add_text("Password")
            dpg.add_input_text(tag=self.password_tag, default_value="", password=True)
            # dpg.add_text("Workspace")
            # dpg.add_input_text(tag=self.workspace_tag, default_value="")
            dpg.add_spacer(height=5)
            dpg.add_checkbox(tag=self.trust_fingerprint_tag, default_value=False, show=False)
            dpg.add_spacer(height=5)
            dpg.add_button(label="Login", tag=self.login_tag, callback=self.__user_login_clicked__)
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


class P4Config(object):

    def init_and_render_ui(self, user_echo_p4_config_data):
        self.p4_config_ui = P4ConfigUI(user_echo_p4_config_data=user_echo_p4_config_data, p4_config_controller=self.p4_config_controller)
        self.p4_config_ui.start()
        try:
            self.p4_config_ui.join()
            # Provide the option to reset the user data if there is an error.
            if self.p4_config_ui.reset_user_data:
                raise AppError(self.p4_config_ui.exception_message, True)
        except BaseException as e:
            raise e

    def __init__(self, user_echo_p4_config_data=None):
        self.p4_ini_file = None
        self.p4_ini_file_path = None
        self.p4_config_controller = P4ConfigController()
        if user_echo_p4_config_data is None:
            return
        self.p4_config_ui = None

        self.init_and_render_ui(user_echo_p4_config_data=user_echo_p4_config_data)

        if self.p4_config_ui is not None:
            if self.p4_config_ui.user_close_ui:
                raise AppExit()

    def get_user_data(self):
        return self.p4_config_ui.get_user_data()

    def p4_login(self, user_p4_config_data=None):
        if user_p4_config_data is None:
            return False
        result = self.p4_config_controller.p4_login(user_p4_config_data=user_p4_config_data)

        if self.p4_config_controller.exception_message != "":
            raise AppError(result['message'] + self.p4_config_controller.exception_message, True)

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
            log.exception(e)
            exception_message = "Error while deleting P4 Config file : " + str(e)
            raise AppError(exception_message)

    def close_ui(self):
        if self.p4_config_ui is None:
            return
        self.p4_config_ui.close_ui()
