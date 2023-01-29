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
from app_globals import log


class P4GroupInfoConfigController(object):

    @staticmethod
    def get_group_list(user, password, port, client=None):
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

    def p4_login(self, user_p4_config_data):
        p4_port = user_p4_config_data[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PORT]
        p4_user = user_p4_config_data[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4USER]
        encrypted_p4_password = user_p4_config_data[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PASSWD]
        p4_password = p4th.decrypt_password(encrypted_p4_password)
        return self.get_group_list(p4_user, p4_password, p4_port)


class P4GroupInfoUI(object):
    __minimum_width__ = 700
    __minimum_height__ = 500

    def __init__(self, user_p4_config=None, p4_group_list=None, p4_group_config_controller=None, viewport_width=__minimum_width__, viewport_height=__minimum_height__):
        if p4_group_config_controller is None or user_p4_config is None or p4_group_list is None:
            log.error("Invalid arguments passed to the GroupConfigUI constructor.")
            sys.exit(1)
        self.user_p4_config = user_p4_config
        self.p4_group_list = p4_group_list
        self.p4_group_config_controller: P4GroupInfoConfigController = p4_group_config_controller

        self.user = self.user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4USER]

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
        self.select_group_tag = "Select Group/Project"
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
            dpg.configure_item(self.select_group_tag, enabled=False, show=False)
            return
        log_text = "\nSelected group: " + selected_group
        log_text += "\n\nPlease click on the 'Select Group/Project' button to proceed."
        dpg.set_value(self.simple_log_tag, log_text)
        dpg.configure_item(self.select_group_tag, enabled=True, show=True)
        pass

    def __select_group_project_clicked__(self, sender, data):
        selected_group = dpg.get_value(self.group_list_tag)

        log_text = "Fetching Group Members data from Perforce..."
        dpg.set_value(self.simple_log_tag, log_text)
        log.info(log_text)
        return

        result = self.p4_group_config_controller.get_group_info(self.user_data['user'], self.user_data['password'], self.user_data['server'], selected_group)

        if not result['workspace_found']:
            dpg.set_value(self.simple_log_tag, result['message'])
            log.error(result['message'])
            dpg.configure_item(self.select_group_tag, enabled=True, show=True)
            return

        self.user_data['workspace'] = result['current_workspace']
        log_text = "Login successful. Successfully connected to server with the data provided."
        dpg.set_value(self.simple_log_tag, log_text)
        log.info(log_text)

        result = self.p4_group_config_controller.try_initializing_p4_config(self.user_echo_p4_config, self.user_data)
        if not result['success']:
            dpg.set_value(self.simple_log_tag, result['message'])
            log.error(result['message'])
            dpg.configure_item(self.select_group_tag, enabled=True, show=True)
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
            dpg.add_listbox(items=self.p4_group_list, tag=self.group_list_tag, default_value=self.p4_group_list[0], width=500, num_items=5, callback=self.__group_listbox_callback__)
            dpg.add_spacer(height=25)
            dpg.add_button(label="Select Group/Project", tag=self.select_group_tag, callback=self.__select_group_project_clicked__, show=False, enabled=False)
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

    def init_and_render_ui(self, user_p4_config, p4_group_list):
        self.p4_group_config_ui = P4GroupInfoUI(user_p4_config=user_p4_config, p4_group_list=p4_group_list, p4_group_config_controller=self.p4_group_config_controller)
        pass

    def __init__(self, user_echo_p4_config_data=None, user_p4_config_data=None):
        self.user_echo_p4_config = user_echo_p4_config_data
        self.user_p4_config = user_p4_config_data
        self.p4_group_config_controller = P4GroupInfoConfigController()
        self.p4_group_list = self.get_group_list(self.user_p4_config)
        if len(self.p4_group_list) == 0:
            return
        self.p4_group_config_ui = None

        dpg_thread = threading.Thread(target=self.init_and_render_ui, args=[self.user_p4_config, self.p4_group_list])
        dpg_thread.start()
        dpg_thread.join()

        if self.p4_group_config_ui is not None:
            if self.p4_group_config_ui.user_close_ui:
                sys.exit(0)

    def get_group_list(self, user_p4_config=None) -> list:
        # TODO: Replace with the p4 config data from the user
        if user_p4_config is None:
            return []

        user = user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4USER]
        port = user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PORT]
        encrypted_password = user_p4_config[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PASSWD]
        password = p4th.decrypt_password(encrypted_password)

        result = self.p4_group_config_controller.get_group_list(user, password, port, None)

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
            log.error("Error while deleting P4 Config file : ", e)
            sys.exit(0)

    def close_ui(self):
        if self.p4_group_config_ui is None:
            return
        self.p4_group_config_ui.close_ui()