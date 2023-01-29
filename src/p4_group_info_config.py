import configparser
import os
import pathlib
import platform
import sys
import threading
import json

import dearpygui.dearpygui as dpg
from P4 import P4, P4Exception
from dearpygui_ext import themes

import echo_p4_constants as ep4c
import p4_tools_helper as p4th
from echo_p4_logger import EchoP4Logger
from app_globals import log
from app_exception import AppException


class P4GroupInfoConfigController(object):

    @staticmethod
    def get_group_list(user, password, port):
        root_folder_path = p4th.get_root_folder()
        project_folder_path = os.path.dirname(root_folder_path)
        workspace_root_folder_path = os.path.dirname(project_folder_path)

        result = dict()
        result['login_success'] = False
        result['message'] = 'Please check your credentials(user and password) and try again.'
        result['groups_found'] = False
        result['groups'] = list()
        (result['groups']).append('None')

        p4 = P4()
        p4.user = user
        p4.password = password
        p4.port = port

        try:
            # p4.client = client
            p4.connect()
            p4.run_login()

            result['login_success'] = True

            user_groups = p4.run("groups", p4.user)  # Get the user's groups
            if len(user_groups) == 0:
                result['message'] = 'The user: ' + p4.user + ' is not a member of any group.'
            else:
                for user_group in user_groups:
                    (result['groups']).append(user_group['group'])
                result['groups_found'] = True
            p4.disconnect()
        except P4Exception as e:
            log.error(e)
        finally:
            if p4.connected():
                p4.disconnect()
            return result

    @staticmethod
    def generate_group_member_data(group_name, user, password, port):

        result = dict()
        result['login_success'] = False
        result['message'] = 'Please check your credentials(user and password) and try again.'
        result['group_data_generated'] = False

        root_folder_path = p4th.get_root_folder()
        data_folder_path = os.path.join(root_folder_path, ep4c.DATA_FOLDER_NAME)
        team_members_json_file_path = os.path.join(data_folder_path, ep4c.GROUP_MEMBERS_INFO_JSON_FILE_NAME)
        group_members_json_file_path = os.path.join(data_folder_path, ep4c.GROUP_INFO_JSON_FILE_NAME)

        data_folder = pathlib.Path(data_folder_path)
        if not data_folder.exists():
            # Folder does not exist, create it
            log.info("Data folder does not exist. Creating it.")
            log.info("Creating data folder: " + data_folder_path)
            try:
                os.makedirs(data_folder_path)
            except OSError:
                log.info("Creation of the data folder failed.")
                sys.exit(1)
        log.info("Data folder exists.")

        p4 = P4()
        p4.user = user
        p4.password = password
        p4.port = port

        try:
            # p4.client = client
            p4.connect()
            p4.run_login()

            result['login_success'] = True

            group_details = p4.run("group", "-o", group_name)
            if len(group_details) != 1:
                log_text = "Error: Group details not found for Group: %s" + group_name
                log.error(log_text)
                result['message'] = log_text
                raise AppException(log_text)

            log.info("Group details found for Group: %s", group_name)
            with open(group_members_json_file_path, 'w', encoding='UTF-8') as group_members_json:
                json.dump(group_details[0], group_members_json, indent=4)
            log.info("Group details saved to file: %s", group_members_json_file_path)
            group_users_list = group_details[0]['Users']

            team_members = dict()
            log.info("Getting user details for all group members/users.")
            for user in group_users_list:
                user_details = p4.run("user", "-o", user)
                if len(user_details) != 1:
                    log_text = "Error: User details not found for User: %s" + user
                    log.error(log_text)
                    result['message'] = log_text
                    raise AppException(log_text)
                team_members[user] = user_details[0]
            with open(team_members_json_file_path, 'w', encoding='UTF-8') as team_members_json:
                json.dump(team_members, team_members_json, indent=4)
            log.info("Team members details saved to file: %s", team_members_json_file_path)
            result['group_data_generated'] = True

            p4.disconnect()
        except P4Exception as e:
            log.error(e)
        except AppException as e:
            log.error(e)
        finally:
            if p4.connected():
                p4.disconnect()
            return result


class P4GroupInfoUI(object):
    __minimum_width__ = 700
    __minimum_height__ = 500

    def __init__(self, user_p4_config_data=None, p4_group_list=None, p4_group_config_controller=None, user=None, password=None, port=None, viewport_width=__minimum_width__,
                 viewport_height=__minimum_height__):
        if p4_group_config_controller is None or user_p4_config_data is None or p4_group_list is None or user is None or password is None or port is None:
            log.error("Invalid arguments passed to the GroupConfigUI constructor.")
            sys.exit(1)
        self.user_p4_config_data = user_p4_config_data
        self.p4_group_list = p4_group_list
        self.p4_group_config_controller: P4GroupInfoConfigController = p4_group_config_controller
        self.user = user
        self.password = password
        self.port = port

        self.user = self.user_p4_config_data[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4USER]

        if self.p4_group_list is None or len(self.p4_group_list) == 0:
            log.error("No groups found for the user: " + self.user)
            sys.exit(1)

        # Remove the Cohort-12 group from the list
        if "Cohort-12" in self.p4_group_list:
            self.p4_group_list.remove("Cohort-12")

        # DearPyGUI's Viewport Constants
        if viewport_width is None or viewport_width <= self.__minimum_width__:
            viewport_width = self.__minimum_width__
        if viewport_height is None or viewport_height <= self.__minimum_height__:
            viewport_height = self.__minimum_height__
        self.VIEWPORT_WIDTH = viewport_width
        self.VIEWPORT_HEIGHT = viewport_height
        self.viewport_title = "Group Config UI"
        self.window_title = "Group Config UI Window"
        self.group_list_tag = "Group/Project"
        self.simple_log_tag = "Log"
        self.select_group_button_tag = "Select Group/Project"
        self.log_width = viewport_width - 50
        self.log_height = viewport_height - 350
        self.auto_close_ui = False
        self.user_close_ui = False
        self.__init_ui__()

    def get_viewport_name(self):
        return self.viewport_title

    def get_window_name(self):
        return self.window_title

    def close_ui(self):
        self.auto_close_ui = True

    def __group_listbox_callback__(self, sender, data):
        selected_group = dpg.get_value(self.group_list_tag)
        if selected_group is None or selected_group == "" or selected_group == "None":
            dpg.set_value(self.simple_log_tag, "Please select a group.")
            dpg.configure_item(self.select_group_button_tag, enabled=False, show=False)
            return
        log_text = "\nSelected group: " + selected_group
        log_text += "\n\nPlease click on the 'Select Group/Project' button to proceed."
        dpg.set_value(self.simple_log_tag, log_text)
        dpg.configure_item(self.select_group_button_tag, enabled=True, show=True)
        pass

    def __select_group_project_clicked__(self, sender, data):
        selected_group = dpg.get_value(self.group_list_tag)

        log_text = "Fetching Group Members data from Perforce..."
        dpg.set_value(self.simple_log_tag, log_text)
        log.info(log_text)

        result = self.p4_group_config_controller.generate_group_member_data(selected_group, self.user, self.password, self.port)

        if not result['group_data_generated']:
            dpg.set_value(self.simple_log_tag, result['message'])
            log.error(result['message'])
            dpg.configure_item(self.select_group_button_tag, enabled=True, show=True)
            return

        self.auto_close_ui = True

    def __exit_callback__(self):
        if not self.auto_close_ui:
            log.info("User Closed the GroupConfigUI.")
            self.user_close_ui = True

    def __init_ui__(self):
        dpg.create_context()

        dark_theme_id = themes.create_theme_imgui_dark()
        dpg.bind_theme(dark_theme_id)

        dpg.configure_app(manual_callback_management=sys.flags.dev_mode)

        dpg.create_viewport(title=self.viewport_title, width=self.VIEWPORT_WIDTH, height=self.VIEWPORT_HEIGHT)

        dpg.set_exit_callback(callback=self.__exit_callback__)

        with dpg.window(label=self.window_title, tag=self.window_title, no_title_bar=False, no_close=True):
            dpg.add_spacer(height=25)
            dpg.add_text("Choose a Perforce group/project to configure:")
            dpg.add_listbox(items=self.p4_group_list, tag=self.group_list_tag, default_value=self.p4_group_list[0], width=500, num_items=5,
                            callback=self.__group_listbox_callback__)
            dpg.add_spacer(height=25)
            dpg.add_button(label="Select Group/Project", tag=self.select_group_button_tag, callback=self.__select_group_project_clicked__, show=False, enabled=False)
            dpg.add_spacer(height=50)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            dpg.add_text("Log")
            dpg.add_input_text(tag=self.simple_log_tag, password=False, multiline=True, width=self.log_width, height=self.log_height, readonly=True,
                               default_value="Select a Group/Project to Configure.")

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

    def init_and_render_ui(self, user_p4_config_data, p4_group_list):
        self.p4_group_config_ui = P4GroupInfoUI(user_p4_config_data=user_p4_config_data, p4_group_list=p4_group_list, p4_group_config_controller=self.p4_group_config_controller,
                                                user=self.user, password=self.password, port=self.port)
        pass

    def __init__(self, user_echo_p4_config_data=None, user_p4_config_data=None):
        self.user_echo_p4_config_data = user_echo_p4_config_data
        self.user_p4_config_data = user_p4_config_data
        self.p4_group_config_controller = P4GroupInfoConfigController()
        self.user = None
        self.password = None
        self.port = None
        self.workspace = None
        self.p4_group_list = self.get_group_list(self.user_p4_config_data)
        self.empty_group_list = False
        if len(self.p4_group_list) == 0:
            self.empty_group_list = True
            return
        self.p4_group_config_ui = None

        dpg_thread = threading.Thread(target=self.init_and_render_ui, args=[self.user_p4_config_data, self.p4_group_list])
        dpg_thread.start()
        dpg_thread.join()

        if self.p4_group_config_ui is not None:
            if self.p4_group_config_ui.user_close_ui:
                sys.exit(0)

    def is_group_list_empty(self):
        return self.empty_group_list

    def get_group_list(self, user_p4_config=None) -> list:
        if user_p4_config is None:
            return []

        self.user = user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4USER]
        self.port = user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PORT]
        encrypted_password = user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PASSWD]
        self.password = p4th.decrypt_password(encrypted_password)

        result = self.p4_group_config_controller.get_group_list(self.user, self.password, self.port)

        if not result['groups_found']:
            log.error(result['message'])
            return []

        log.info(result['groups'])
        return result['groups']

    def p4_login(self, user_p4_config_data=None):
        if user_p4_config_data is None:
            return False
        result = self.p4_group_config_controller.p4_login(user_p4_config_data=user_p4_config_data)
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
            log.error("Error while deleting P4 Config file : " + e)
            sys.exit(0)

    def close_ui(self):
        if self.p4_group_config_ui is None:
            return
        self.p4_group_config_ui.close_ui()
