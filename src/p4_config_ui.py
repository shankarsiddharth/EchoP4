import configparser
import os
import pathlib
import sys
import shutil
import threading
import platform

from P4 import P4, P4Exception

import dearpygui.demo as demo
import dearpygui.dearpygui as dpg
from dearpygui_ext import themes

import echo_p4_constants as ep4c
from echo_p4_logger import EchoP4Logger
import p4_tools_helper as p4th

ep4l = EchoP4Logger()


def try_login(echo_p4_config, user, password, port, client):
    p4_tools_folder_path = echo_p4_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_P4TOOLS_FOLDER_PATH]
    project_folder_path = os.path.dirname(p4_tools_folder_path)
    workspace_root_folder_path = os.path.dirname(project_folder_path)

    result = dict()
    result['workspace_found'] = False
    result['message'] = 'Please check your credentials(user and password) and try again.'
    result['workspaces'] = list()
    result['current_workspace'] = ''

    try:
        p4 = P4()
        p4.user = user
        p4.password = password
        p4.port = port
        # p4.client = client
        p4.connect()
        p4.run_login()

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
        print(e)
    finally:
        if p4.connected():
            p4.disconnect()
        return result


def try_initializing_p4_config(echo_p4_config, user_data):
    result = dict()
    result['success'] = False
    result['message'] = 'Error occurred while initializing the p4 config file.'
    default_p4_config_file_path = echo_p4_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_DEFAULT_P4_INI_FILE_PATH]
    p4_config_file_path = echo_p4_config[ep4c.ECHO_P4_CONFIG_SECTION][ep4c.KEY_P4_INI_FILE_PATH]
    ep4l.info("Checking for p4 config file...")
    p4_config_file = pathlib.Path(p4_config_file_path)
    if p4_config_file.exists():
        ep4l.info('P4 config file already exists: ' + p4_config_file_path)
        ep4l.info('Removing the existing P4 config file: ' + p4_config_file_path)
        os.remove(p4_config_file_path)
    default_p4_config_file = pathlib.Path(default_p4_config_file_path)
    ep4l.info("Checking for default p4 config file...")
    if not default_p4_config_file.exists():
        ep4l.error('Default P4 config file does not exist: ' + default_p4_config_file_path)
        return result
    ep4l.info("Default p4 config file found.")
    ep4l.info("Reading default p4 config file...")
    user_p4_config = configparser.ConfigParser()
    user_p4_config.read(default_p4_config_file_path)
    p4ignore_file = user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4IGNORE]
    user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PORT] = user_data['server']
    user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4USER] = user_data['user']
    user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4CLIENT] = user_data['workspace']
    ep4l.info("Encrypting the password...")
    encrypted_password = p4th.encrypt_password(user_data['password'])
    user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PASSWD] = encrypted_password
    ep4l.info("Password encrypted.")
    ep4l.info("Writing user p4 config file...")
    with open(p4_config_file_path, 'w', encoding='UTF-8') as user_p4_config_file:
        user_p4_config.write(user_p4_config_file)
    ep4l.info("User's p4 config file written.")
    result['success'] = True
    result['message'] = 'User P4 config file initialized successfully.'
    return result


class P4ConfigUI:
    __minimum_height__ = 500
    __minimum_width__ = 700

    def __init__(self, echo_p4_config, viewport_width=700, viewport_height=500, is_debug=False):
        if echo_p4_config is None:
            return
        self.echo_p4_config = echo_p4_config
        global ep4l
        ep4l = p4th.get_logger(self.echo_p4_config)
        # DearPyGUI's Viewport Constants
        if viewport_width is None or viewport_width <= self.__minimum_width__:
            viewport_width = self.__minimum_width__
        if viewport_height is None or viewport_height <= self.__minimum_height__:
            viewport_height = self.__minimum_height__
        self.VIEWPORT_WIDTH = viewport_width
        self.VIEWPORT_HEIGHT = viewport_height
        self.is_debug = is_debug
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
        self.__init_ui__()
        pass

    def get_viewport_name(self):
        return self.viewport_title

    def get_window_name(self):
        return self.window_title

    def get_user_data(self):
        return self.user_data

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
        dpg.set_value(self.simple_log_tag, "Connecting to server with the data provided...")
        dpg.configure_item(self.login_tag, enabled=False, show=False)

        result = try_login(self.echo_p4_config, self.user_data['user'], self.user_data['password'], self.user_data['server'], workspace)

        if not result['workspace_found']:
            dpg.set_value(self.simple_log_tag, result['message'])
            dpg.configure_item(self.login_tag, enabled=True, show=True)
            return

        self.user_data['workspace'] = result['current_workspace']
        dpg.set_value(self.simple_log_tag, "Login successful.")

        result = try_initializing_p4_config(self.echo_p4_config, self.user_data)
        if not result['success']:
            dpg.set_value(self.simple_log_tag, result['message'])
            dpg.configure_item(self.login_tag, enabled=True, show=True)
            return

        self.auto_close_ui = True

    def __init_ui__(self):
        dpg.create_context()

        dark_theme_id = themes.create_theme_imgui_dark()
        dpg.bind_theme(dark_theme_id)

        # global is_debug
        dpg.configure_app(manual_callback_management=self.is_debug)

        dpg.create_viewport(title=self.viewport_title, width=self.VIEWPORT_WIDTH, height=self.VIEWPORT_HEIGHT)

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
            pass

        dpg.setup_dearpygui()
        dpg.show_viewport()

        dpg.set_primary_window(self.window_title, True)

        # below replaces, start_dearpygui()
        while dpg.is_dearpygui_running():

            if self.is_debug:
                jobs = dpg.get_callback_queue()  # retrieves and clears queue
                dpg.run_callbacks(jobs)

            dpg.render_dearpygui_frame()

            if self.auto_close_ui:
                break

        dpg.destroy_context()
