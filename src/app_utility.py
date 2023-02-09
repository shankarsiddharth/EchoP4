import configparser
import os
import pathlib
import platform
import stat
import sys
import threading
import shutil

import dearpygui.dearpygui as dpg
from P4 import P4, P4Exception
from dearpygui_ext import themes

import echo_p4_constants as ep4c
import p4_tools_helper as p4th
from app_error import AppError
from app_exit import AppExit
from app_message import AppMessage
from app_globals import log
from checked_out_files_panel import CheckedOutFilesPanel
from group_members_panel import GroupMembersPanel


class AppUtilityController(object):

    def __init__(self):
        self.exception_message = ''
        self.result = dict()

        # Constants
        self.is_load_default_layout_clicked = False
        # is_menu_close_button_clicked = False
        self.is_window_close_button_clicked = False

        self.root_path = p4th.get_root_folder()
        self.project_path = os.path.dirname(self.root_path)

        self.project_binaries_path = os.path.join(self.project_path, ep4c.PROJECT_BINARIES_FOLDER_NAME)
        self.project_source_path = os.path.join(self.project_path, ep4c.PROJECT_SOURCE_FOLDER_NAME)
        self.project_config_path = os.path.join(self.project_path, ep4c.PROJECT_CONFIG_FOLDER_NAME)
        self.project_intermediate_path = os.path.join(self.project_path, ep4c.PROJECT_INTERMEDIATE_FOLDER_NAME)
        self.project_saved_path = os.path.join(self.project_path, ep4c.PROJECT_SAVED_FOLDER_NAME)
        self.project_plugins_path = os.path.join(self.project_path, ep4c.PROJECT_PLUGINS_FOLDER_NAME)
        self.project_plugins_list = self.get_subdirectories(self.project_plugins_path)
        if ep4c.DEVELOPER_PLUGINS_FOLDER_NAME in self.project_plugins_list:
            self.project_plugins_list.remove(ep4c.DEVELOPER_PLUGINS_FOLDER_NAME)
            self.developer_plugins_path = os.path.join(self.project_plugins_path, ep4c.DEVELOPER_PLUGINS_FOLDER_NAME)
            self.developer_plugins_list = self.get_subdirectories(self.developer_plugins_path)
        else:
            self.developer_plugins_path = None
            self.developer_plugins_list = list()

        self.project_plugins_binaries_path_list = list()
        self.project_plugins_source_path_list = list()
        self.project_plugins_config_path_list = list()
        self.project_plugins_intermediate_path_list = list()
        self.project_plugins_saved_path_list = list()

        for plugin_folder in self.project_plugins_list:
            plugin_path = os.path.join(self.project_plugins_path, plugin_folder)
            plugin_binaries_path = os.path.join(plugin_path, ep4c.PLUGIN_BINARIES_FOLDER_NAME)
            self.project_plugins_binaries_path_list.append(plugin_binaries_path)
            plugin_source_path = os.path.join(plugin_path, ep4c.PLUGIN_SOURCE_FOLDER_NAME)
            self.project_plugins_source_path_list.append(plugin_source_path)
            plugin_config_path = os.path.join(plugin_path, ep4c.PLUGIN_CONFIG_FOLDER_NAME)
            self.project_plugins_config_path_list.append(plugin_config_path)
            plugin_intermediate_path = os.path.join(plugin_path, ep4c.PLUGIN_INTERMEDIATE_FOLDER_NAME)
            self.project_plugins_intermediate_path_list.append(plugin_intermediate_path)
            plugin_saved_path = os.path.join(plugin_path, ep4c.PLUGIN_SAVED_FOLDER_NAME)
            self.project_plugins_saved_path_list.append(plugin_saved_path)

        # log.trace("Project Plugins Binaries Path List: " + str(self.project_plugins_binaries_path_list))
        # log.trace("Project Plugins Source Path List: " + str(self.project_plugins_source_path_list))
        # log.trace("Project Plugins Config Path List: " + str(self.project_plugins_config_path_list))
        # log.trace("Project Plugins Intermediate Path List: " + str(self.project_plugins_intermediate_path_list))
        # log.trace("Project Plugins Saved Path List: " + str(self.project_plugins_saved_path_list))

        self.developer_plugins_binaries_path_list = list()
        self.developer_plugins_source_path_list = list()
        self.developer_plugins_config_path_list = list()
        self.developer_plugins_intermediate_path_list = list()
        self.developer_plugins_saved_path_list = list()

        for developer_plugin in self.developer_plugins_list:
            developer_plugin_path = os.path.join(self.developer_plugins_path, developer_plugin)
            developer_plugin_binaries_path = os.path.join(developer_plugin_path, ep4c.PLUGIN_BINARIES_FOLDER_NAME)
            self.developer_plugins_binaries_path_list.append(developer_plugin_binaries_path)
            developer_plugin_source_path = os.path.join(developer_plugin_path, ep4c.PLUGIN_SOURCE_FOLDER_NAME)
            self.developer_plugins_source_path_list.append(developer_plugin_source_path)
            developer_plugin_config_path = os.path.join(developer_plugin_path, ep4c.PLUGIN_CONFIG_FOLDER_NAME)
            self.developer_plugins_config_path_list.append(developer_plugin_config_path)
            developer_plugin_intermediate_path = os.path.join(developer_plugin_path, ep4c.PLUGIN_INTERMEDIATE_FOLDER_NAME)
            self.developer_plugins_intermediate_path_list.append(developer_plugin_intermediate_path)
            developer_plugin_saved_path = os.path.join(developer_plugin_path, ep4c.PLUGIN_SAVED_FOLDER_NAME)
            self.developer_plugins_saved_path_list.append(developer_plugin_saved_path)

        # log.trace("Developer Plugins Binaries Path List: " + str(self.developer_plugins_binaries_path_list))
        # log.trace("Developer Plugins Source Path List: " + str(self.developer_plugins_source_path_list))
        # log.trace("Developer Plugins Config Path List: " + str(self.developer_plugins_config_path_list))
        # log.trace("Developer Plugins Intermediate Path List: " + str(self.developer_plugins_intermediate_path_list))
        # log.trace("Developer Plugins Saved Path List: " + str(self.developer_plugins_saved_path_list))

    @staticmethod
    def get_subdirectories(directory_path):
        return [name for name in os.listdir(directory_path)
                if os.path.isdir(os.path.join(directory_path, name))]

    @staticmethod
    def make_folder_writable(folder_path):
        for root, sub_dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                os.chmod(file_path, stat.S_IRWXU)
                log.trace("Made File Writable: " + file_path)

    def make_project_binaries_writable(self):
        project_binaries = pathlib.Path(self.project_binaries_path)
        if project_binaries.exists():
            self.make_folder_writable(self.project_binaries_path)
            log.success("Made Project Binaries Writable: " + self.project_binaries_path)
        else:
            log.warning("Project Binaries Folder Does Not Exist: " + self.project_binaries_path)

    def make_project_source_writable(self):
        project_source = pathlib.Path(self.project_source_path)
        if project_source.exists():
            self.make_folder_writable(self.project_source_path)
            log.success("Made Project Source Writable: " + self.project_source_path)
        else:
            log.warning("Project Source Folder Does Not Exist: " + self.project_source_path)

    def make_project_plugins_binaries_writable(self):
        for plugin_binaries_path in self.project_plugins_binaries_path_list:
            plugin_binaries = pathlib.Path(plugin_binaries_path)
            if plugin_binaries.exists():
                self.make_folder_writable(plugin_binaries_path)
                log.success("Made Project Plugin Binaries Writable: " + plugin_binaries_path)
            else:
                log.warning("Project Plugin Binaries Folder Does Not Exist: " + plugin_binaries_path)

    def make_project_plugins_source_writable(self):
        for plugin_source_path in self.project_plugins_source_path_list:
            plugin_source = pathlib.Path(plugin_source_path)
            if plugin_source.exists():
                self.make_folder_writable(plugin_source_path)
                log.success("Made Project Plugin Source Writable: " + plugin_source_path)
            else:
                log.warning("Project Plugin Source Folder Does Not Exist: " + plugin_source_path)

    def make_developer_plugins_binaries_writable(self):
        for plugin_binaries_path in self.developer_plugins_binaries_path_list:
            plugin_binaries = pathlib.Path(plugin_binaries_path)
            if plugin_binaries.exists():
                self.make_folder_writable(plugin_binaries_path)
                log.success("Made Developer Plugin Binaries Writable: " + plugin_binaries_path)
            else:
                log.warning("Developer Plugin Binaries Folder Does Not Exist: " + plugin_binaries_path)

    def make_developer_plugins_source_writable(self):
        for plugin_source_path in self.developer_plugins_source_path_list:
            plugin_source = pathlib.Path(plugin_source_path)
            if plugin_source.exists():
                self.make_folder_writable(plugin_source_path)
                log.success("Made Developer Plugin Source Writable: " + plugin_source_path)
            else:
                log.warning("Developer Plugin Source Folder Does Not Exist: " + plugin_source_path)

    def delete_project_binaries(self):
        project_binaries = pathlib.Path(self.project_binaries_path)
        if project_binaries.exists():
            shutil.rmtree(self.project_binaries_path)
            log.success("Deleted Project Binaries: " + self.project_binaries_path)
        else:
            log.warning("Project Binaries Folder Does Not Exist: " + self.project_binaries_path)

    def delete_project_intermediate(self):
        project_intermediate = pathlib.Path(self.project_intermediate_path)
        if project_intermediate.exists():
            shutil.rmtree(self.project_intermediate_path)
            log.success("Deleted Project Intermediate: " + self.project_intermediate_path)
        else:
            log.warning("Project Intermediate Folder Does Not Exist: " + self.project_intermediate_path)

    def delete_project_saved(self):
        project_saved = pathlib.Path(self.project_saved_path)
        if project_saved.exists():
            shutil.rmtree(self.project_saved_path)
            log.success("Deleted Project Saved: " + self.project_saved_path)
        else:
            log.warning("Project Saved Folder Does Not Exist: " + self.project_saved_path)

    def delete_plugin_binaries(self):
        for plugin_binaries_path in self.project_plugins_binaries_path_list:
            plugin_binaries = pathlib.Path(plugin_binaries_path)
            if plugin_binaries.exists():
                shutil.rmtree(plugin_binaries_path)
                log.success("Deleted Plugin Binaries: " + plugin_binaries_path)
            else:
                log.warning("Plugin Binaries Folder Does Not Exist: " + plugin_binaries_path)

    def delete_plugin_intermediate(self):
        for plugin_intermediate_path in self.project_plugins_intermediate_path_list:
            plugin_intermediate = pathlib.Path(plugin_intermediate_path)
            if plugin_intermediate.exists():
                shutil.rmtree(plugin_intermediate_path)
                log.success("Deleted Plugin Intermediate: " + plugin_intermediate_path)
            else:
                log.warning("Plugin Intermediate Folder Does Not Exist: " + plugin_intermediate_path)

    def delete_plugin_saved(self):
        for plugin_saved_path in self.project_plugins_saved_path_list:
            plugin_saved = pathlib.Path(plugin_saved_path)
            if plugin_saved.exists():
                shutil.rmtree(plugin_saved_path)
                log.success("Deleted Plugin Saved: " + plugin_saved_path)
            else:
                log.warning("Plugin Saved Folder Does Not Exist: " + plugin_saved_path)

    def delete_developer_plugin_binaries(self):
        for plugin_binaries_path in self.developer_plugins_binaries_path_list:
            plugin_binaries = pathlib.Path(plugin_binaries_path)
            if plugin_binaries.exists():
                shutil.rmtree(plugin_binaries_path)
                log.success("Deleted Developer Plugin Binaries: " + plugin_binaries_path)
            else:
                log.warning("Developer Plugin Binaries Folder Does Not Exist: " + plugin_binaries_path)

    def delete_developer_plugin_intermediate(self):
        for plugin_intermediate_path in self.developer_plugins_intermediate_path_list:
            plugin_intermediate = pathlib.Path(plugin_intermediate_path)
            if plugin_intermediate.exists():
                shutil.rmtree(plugin_intermediate_path)
                log.success("Deleted Developer Plugin Intermediate: " + plugin_intermediate_path)
            else:
                log.warning("Developer Plugin Intermediate Folder Does Not Exist: " + plugin_intermediate_path)

    def delete_developer_plugin_saved(self):
        for plugin_saved_path in self.developer_plugins_saved_path_list:
            plugin_saved = pathlib.Path(plugin_saved_path)
            if plugin_saved.exists():
                shutil.rmtree(plugin_saved_path)
                log.success("Deleted Developer Plugin Saved: " + plugin_saved_path)
            else:
                log.warning("Developer Plugin Saved Folder Does Not Exist: " + plugin_saved_path)


class AppUtilityUI(threading.Thread):
    __minimum_width__ = 1200
    __minimum_height__ = 900

    def __init__(self, app_utility_controller=None, group_members_panel=None, checked_out_files_panel=None,
                 viewport_width=__minimum_width__, viewport_height=__minimum_height__):
        super().__init__()

        self.exception = None

        if app_utility_controller is None:
            self.app_utility_controller = None
            return

        if group_members_panel is None:
            self.group_members_panel = None
            return

        if checked_out_files_panel is None:
            self.checked_out_files_panel = None
            return

        self.app_utility_controller: AppUtilityController = app_utility_controller
        self.group_members_panel: GroupMembersPanel = group_members_panel
        self.checked_out_files_panel: CheckedOutFilesPanel = checked_out_files_panel

        # DearPyGUI's Viewport Constants
        if viewport_width is None or viewport_width <= self.__minimum_width__:
            viewport_width = self.__minimum_width__
        if viewport_height is None or viewport_height <= self.__minimum_height__:
            viewport_height = self.__minimum_height__
        self.VIEWPORT_WIDTH = viewport_width
        self.VIEWPORT_HEIGHT = viewport_height
        self.viewport_title = "Echo P4 Tool"
        self.command_window_title = "Echo P4 Commands"
        self.user_close_ui = False
        self.reset_user_data = False
        self.exception_message = ''
        self.reset_user_data = False

        self.file_menu: str = "File"
        self.ui_menu: str = "UI"
        self.data_menu: str = "Data"
        self.save_current_layout_to_dpg_ini: str = "Save Current Layout"
        self.reset_to_default_layout_tag: str = "Reset to Default Layout"
        self.reset_user_data_tag: str = "Reset User Data"

        # Theme
        self.red_button_theme_tag = "Red Button Theme"
        self.red_collapsing_header_theme_tag = "Red Collapsing Header Theme"

        # ***** Command Window ***** #
        # Make Writable
        self.make_writable_tag = "Make Files Writable (Binaries & Source)"
        self.make_writable_project_binaries_tree_tag = "Project Binaries"
        self.make_writable_plugin_binaries_tree_tag = "Plugin Binaries"
        self.make_writable_project_source_tree_tag = "Project Source"
        self.make_writable_plugin_source_tree_tag = "Plugin Source"

        self.make_project_binaries_writable_tag = "Project Binaries (Make Files Writable)"
        self.make_plugin_binaries_writable_tag = "Plugin Binaries (Make Files Writable)"
        self.make_project_source_writable_tag = "Project Source (Make Files Writable)"
        self.make_plugin_source_writable_tag = "Plugin Source (Make Files Writable)"
        self.make_writable_help_message = "(Remove Read-Only Flag/Attribute)\n"

        # Clear Binaries
        self.clear_binaries_tag = "Clear Binaries"
        self.clear_project_binaries_tree_tag = "Project Binaries "  # Space at the end is intentional to avoid conflict with the "Project Binaries" tag
        self.clear_plugin_binaries_tree_tag = "Plugin Binaries "  # Space at the end is intentional to avoid conflict with the "Plugin Binaries" tag

        self.clear_project_binaries_tag = "Delete Project Binaries Folder"
        self.clear_plugin_binaries_tag = "Delete Plugin Binaries Folder"
        self.clear_binaries_help_message = "(Delete the Binaries Folder and Files)\n"

        # Clear Intermediate
        self.clear_intermediate_tag = "Clear Intermediate"
        self.clear_project_intermediate_tree_tag = "Project Intermediate"
        self.clear_plugin_intermediate_tree_tag = "Plugin Intermediate"

        self.clear_project_intermediate_tag = "Delete Project Intermediate Folder"
        self.clear_plugin_intermediate_tag = "Delete Plugin Intermediate Folder"
        self.clear_intermediate_help_message = "(Delete the Intermediate Folder and Files)\n"

        # Clear Saved
        self.clear_saved_tag = "Clear Saved"
        self.clear_project_saved_tree_tag = "Project Saved"
        self.clear_plugin_saved_tree_tag = "Plugin Saved"

        self.clear_project_saved_tag = "Delete Project Saved Folder"
        self.clear_plugin_saved_tag = "Delete Plugin Saved Folder"
        self.clear_saved_help_message = "(Delete the Saved Folder and Files)\n"
        # Checked Out Files
        self.checked_out_files_tag = "Checked Out Files"

        self.default_dpg_ini_file_path = p4th.get_default_dpg_ini_file_path()
        self.dpg_ini_file_path = p4th.get_dpg_ini_file_path()

    def run(self):
        try:
            if self.app_utility_controller is None:
                exception_message = "Invalid arguments passed to the AppUtilityUI constructor."
                raise AppError(exception_message)
            self.__init_ui__()
        except BaseException as e:
            self.exception = e

    def join(self, **kwargs):
        threading.Thread.join(self, **kwargs)
        # since join() returns in caller thread we re-raise the caught exception if any was caught
        if self.exception:
            raise self.exception

    def __exit_callback__(self):
        log.info("User clicked on the Close Window button.")
        self.app_utility_controller.is_window_close_button_clicked = True

    def load_default_layout(self):
        log.info("User clicked on the Load Default Layout button.")
        self.app_utility_controller.is_load_default_layout_clicked = True

    def reset_to_default_layout(self):
        self.exception_message = ''
        p4th.reset_to_default_layout()

    def reset_user_data_callback(self):
        log.info("User clicked on the Reset User Data button.")
        self.exception_message = 'Please, Confirm to reset user data.'
        self.app_utility_controller.is_window_close_button_clicked = True
        self.reset_user_data = True
        pass

    def _help(self, message):
        last_item = dpg.last_item()
        group = dpg.add_group(horizontal=True)
        dpg.move_item(last_item, parent=group)
        dpg.capture_next_item(lambda s: dpg.move_item(s, parent=group))
        t = dpg.add_text("(?)", color=[0, 255, 0])
        with dpg.tooltip(t):
            dpg.add_text(message)

    def __make_project_binaries_writable__(self, sender, data):
        log.info("User clicked on the Make Project Binaries Writable button.")
        dpg.configure_item(self.make_project_binaries_writable_tag, show=False)
        self.app_utility_controller.make_project_binaries_writable()
        dpg.configure_item(self.make_project_binaries_writable_tag, show=True)

    def __make_plugin_binaries_writable__(self, sender, data):
        log.info("User clicked on the Make Plugin Binaries Writable button.")
        dpg.configure_item(self.make_plugin_binaries_writable_tag, show=False)
        self.app_utility_controller.make_project_plugins_binaries_writable()
        self.app_utility_controller.make_developer_plugins_binaries_writable()
        dpg.configure_item(self.make_plugin_binaries_writable_tag, show=True)
        pass

    def __make_project_source_writable__(self, sender, data):
        log.info("User clicked on the Make Project Source Writable button.")
        dpg.configure_item(self.make_project_source_writable_tag, show=False)
        self.app_utility_controller.make_project_source_writable()
        dpg.configure_item(self.make_project_source_writable_tag, show=True)

    def __make_plugin_source_writable__(self, sender, data):
        log.info("User clicked on the Make Plugin Source Writable button.")
        dpg.configure_item(self.make_plugin_source_writable_tag, show=False)
        self.app_utility_controller.make_project_plugins_source_writable()
        self.app_utility_controller.make_developer_plugins_source_writable()
        dpg.configure_item(self.make_plugin_source_writable_tag, show=True)

    def __clear_project_binaries__(self, sender, data):
        log.info("User clicked on the Clear Project Binaries button.")
        dpg.configure_item(self.clear_project_binaries_tag, show=False)
        self.app_utility_controller.delete_project_binaries()
        dpg.configure_item(self.clear_project_binaries_tag, show=True)

    def __clear_plugin_binaries__(self, sender, data):
        log.info("User clicked on the Clear Plugin Binaries button.")
        dpg.configure_item(self.clear_plugin_binaries_tag, show=False)
        self.app_utility_controller.delete_plugin_binaries()
        self.app_utility_controller.delete_developer_plugin_binaries()
        dpg.configure_item(self.clear_plugin_binaries_tag, show=True)

    def __clear_project_intermediate__(self, sender, data):
        log.info("User clicked on the Clear Project Intermediate button.")
        dpg.configure_item(self.clear_project_intermediate_tag, show=False)
        self.app_utility_controller.delete_project_intermediate()
        dpg.configure_item(self.clear_project_intermediate_tag, show=True)

    def __clear_plugin_intermediate__(self, sender, data):
        log.info("User clicked on the Clear Plugin Intermediate button.")
        dpg.configure_item(self.clear_plugin_intermediate_tag, show=False)
        self.app_utility_controller.delete_plugin_intermediate()
        self.app_utility_controller.delete_developer_plugin_intermediate()
        dpg.configure_item(self.clear_plugin_intermediate_tag, show=True)

    def __clear_project_saved__(self, sender, data):
        log.info("User clicked on the Clear Project Saved button.")
        dpg.configure_item(self.clear_project_saved_tag, show=False)
        self.app_utility_controller.delete_project_saved()
        dpg.configure_item(self.clear_project_saved_tag, show=True)

    def __clear_plugin_saved__(self, sender, data):
        log.info("User clicked on the Clear Plugin Saved button.")
        dpg.configure_item(self.clear_plugin_saved_tag, show=False)
        self.app_utility_controller.delete_plugin_saved()
        self.app_utility_controller.delete_developer_plugin_saved()
        dpg.configure_item(self.clear_plugin_saved_tag, show=True)

    def __init_ui__(self):

        dpg.create_context()

        # demo.show_demo()

        light_theme_id = themes.create_theme_imgui_light()
        dark_theme_id = themes.create_theme_imgui_dark()
        dpg.bind_theme(dark_theme_id)

        dpg.configure_app(manual_callback_management=sys.flags.dev_mode, docking=True, docking_space=True, init_file="../config/" + ep4c.DPG_INI_FILE_NAME,
                          load_init_file=True, auto_device=True)

        dpg.create_viewport(title=self.viewport_title, width=self.VIEWPORT_WIDTH, height=self.VIEWPORT_HEIGHT)

        dpg.set_exit_callback(callback=self.__exit_callback__)

        # Add Theme
        with dpg.theme(tag=self.red_button_theme_tag):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (200, 0, 0, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (178, 34, 34, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (220, 20, 60, 255))

        with dpg.theme(tag=self.red_collapsing_header_theme_tag):
            with dpg.theme_component(dpg.mvCollapsingHeader):
                dpg.add_theme_color(dpg.mvThemeCol_Header, (200, 0, 0, 255))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (178, 34, 34, 255))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (220, 20, 60, 255))

        # add a font registry
        with dpg.font_registry():
            # first argument ids the path to the .ttf or .otf file
            default_font = dpg.add_font(p4th.get_default_font_file_path(), p4th.get_default_font_size())
            default_bold_font = dpg.add_font(p4th.get_default_bold_font_file_path(), p4th.get_default_font_size())

        dpg.bind_font(default_font)

        # Menu Bar
        with dpg.viewport_menu_bar():
            # File Menu
            # with dpg.menu(label=self.file_menu, tag=self.file_menu):
            #     dpg.add_menu_item(label=self.save_current_layout_to_dpg_ini, tag=self.save_current_layout_to_dpg_ini,
            #                       callback=lambda: dpg.save_init_file(self.dpg_ini_file_path))
            #     dpg.add_menu_item(label=self.reset_to_default_layout_tag, tag=self.reset_to_default_layout_tag, callback=self.load_default_layout)
            # UI Menu
            with dpg.menu(label=self.ui_menu, tag=self.ui_menu):
                dpg.add_menu_item(label=self.save_current_layout_to_dpg_ini, tag=self.save_current_layout_to_dpg_ini,
                                  callback=lambda: dpg.save_init_file(self.dpg_ini_file_path))
                dpg.add_menu_item(label=self.reset_to_default_layout_tag, tag=self.reset_to_default_layout_tag, callback=self.load_default_layout)
            # Data Menu
            with dpg.menu(label=self.data_menu, tag=self.data_menu):
                dpg.add_menu_item(label=self.reset_user_data_tag, tag=self.reset_user_data_tag, callback=self.reset_user_data_callback)

        # Command Window
        with dpg.window(label=self.command_window_title, tag=self.command_window_title, no_title_bar=False, no_close=True):
            # Make Files Writable
            with dpg.collapsing_header(label=self.make_writable_tag, tag=self.make_writable_tag, default_open=True):
                with dpg.tree_node(label=self.make_writable_project_binaries_tree_tag, tag=self.make_writable_project_binaries_tree_tag, default_open=True):
                    # dpg.add_text("Click the button to make all the files in the Project Binaries folder writable.")
                    dpg.add_button(label=self.make_project_binaries_writable_tag, tag=self.make_project_binaries_writable_tag, callback=self.__make_project_binaries_writable__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    self._help(self.make_writable_help_message)
                    dpg.add_separator()
                with dpg.tree_node(label=self.make_writable_plugin_binaries_tree_tag, tag=self.make_writable_plugin_binaries_tree_tag, default_open=True):
                    # dpg.add_text("Click the button to make all the files in the Plugin Binaries folder writable.")
                    dpg.add_button(label=self.make_plugin_binaries_writable_tag, tag=self.make_plugin_binaries_writable_tag, callback=self.__make_plugin_binaries_writable__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    self._help(self.make_writable_help_message)
                    dpg.add_separator()
                with dpg.tree_node(label=self.make_writable_project_source_tree_tag, tag=self.make_writable_project_source_tree_tag, default_open=True):
                    # dpg.add_text("Click the button to make all the files in the Project Source folder writable.")
                    dpg.add_button(label=self.make_project_source_writable_tag, tag=self.make_project_source_writable_tag, callback=self.__make_project_source_writable__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    self._help(self.make_writable_help_message)
                    dpg.add_separator()
                with dpg.tree_node(label=self.make_writable_plugin_source_tree_tag, tag=self.make_writable_plugin_source_tree_tag, default_open=True):
                    # dpg.add_text("Click the button to make all the files in the Plugin Source folder writable.")
                    dpg.add_button(label=self.make_plugin_source_writable_tag, tag=self.make_plugin_source_writable_tag, callback=self.__make_plugin_source_writable__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    self._help(self.make_writable_help_message)
                    dpg.add_separator()
            # Clear Binaries
            with dpg.collapsing_header(label=self.clear_binaries_tag, tag=self.clear_binaries_tag, default_open=False):
                dpg.bind_item_theme(dpg.last_item(), self.red_collapsing_header_theme_tag)
                with dpg.tree_node(label=self.clear_project_binaries_tree_tag, tag=self.clear_project_binaries_tree_tag, default_open=True):
                    # dpg.add_text("Click the button to delete Project Binaries folder.")
                    dpg.add_button(label=self.clear_project_binaries_tag, tag=self.clear_project_binaries_tag, callback=self.__clear_project_binaries__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    dpg.bind_item_theme(dpg.last_item(), self.red_button_theme_tag)
                    self._help(self.clear_binaries_help_message)
                    dpg.add_separator()
                with dpg.tree_node(label=self.clear_plugin_binaries_tree_tag, tag=self.clear_plugin_binaries_tree_tag, default_open=True):
                    # dpg.add_text("Click the button to delete Plugin Binaries folder.")
                    dpg.add_button(label=self.clear_plugin_binaries_tag, tag=self.clear_plugin_binaries_tag, callback=self.__clear_plugin_binaries__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    dpg.bind_item_theme(dpg.last_item(), self.red_button_theme_tag)
                    self._help(self.clear_binaries_help_message)
                    dpg.add_separator()
            # Clear Intermediate
            with dpg.collapsing_header(label=self.clear_intermediate_tag, tag=self.clear_intermediate_tag, default_open=False):
                dpg.bind_item_theme(dpg.last_item(), self.red_collapsing_header_theme_tag)
                with dpg.tree_node(label=self.clear_project_intermediate_tree_tag, tag=self.clear_project_intermediate_tree_tag, default_open=True):
                    # dpg.add_text("Click the button to delete Project Intermediate folder.")
                    dpg.add_button(label=self.clear_project_intermediate_tag, tag=self.clear_project_intermediate_tag, callback=self.__clear_project_intermediate__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    dpg.bind_item_theme(dpg.last_item(), self.red_button_theme_tag)
                    self._help(self.clear_intermediate_help_message)
                    dpg.add_separator()
                with dpg.tree_node(label=self.clear_plugin_intermediate_tree_tag, tag=self.clear_plugin_intermediate_tree_tag, default_open=True):
                    # dpg.add_text("Click the button to delete Plugin Intermediate folder.")
                    dpg.add_button(label=self.clear_plugin_intermediate_tag, tag=self.clear_plugin_intermediate_tag, callback=self.__clear_plugin_intermediate__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    dpg.bind_item_theme(dpg.last_item(), self.red_button_theme_tag)
                    self._help(self.clear_intermediate_help_message)
                    dpg.add_separator()
            # Clear Saved
            with dpg.collapsing_header(label=self.clear_saved_tag, tag=self.clear_saved_tag, default_open=False):
                dpg.bind_item_theme(dpg.last_item(), self.red_collapsing_header_theme_tag)
                with dpg.tree_node(label=self.clear_project_saved_tree_tag, tag=self.clear_project_saved_tree_tag, default_open=True):
                    # dpg.add_text("Click the button to delete Project Saved folder.")
                    dpg.add_button(label=self.clear_project_saved_tag, tag=self.clear_project_saved_tag, callback=self.__clear_project_saved__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    dpg.bind_item_theme(dpg.last_item(), self.red_button_theme_tag)
                    self._help(self.clear_saved_help_message)
                    dpg.add_separator()
                with dpg.tree_node(label=self.clear_plugin_saved_tree_tag, tag=self.clear_plugin_saved_tree_tag, default_open=True):
                    # dpg.add_text("Click the button to delete Plugin Saved folder.")
                    dpg.add_button(label=self.clear_plugin_saved_tag, tag=self.clear_plugin_saved_tag, callback=self.__clear_plugin_saved__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    dpg.bind_item_theme(dpg.last_item(), self.red_button_theme_tag)
                    self._help(self.clear_saved_help_message)
                    dpg.add_separator()

        # Log Panel
        log.init_ui()
        # Group Members Panel
        self.group_members_panel.init_ui()
        # Checked Out Files Panel
        self.checked_out_files_panel.init_ui()

        dpg.setup_dearpygui()
        dpg.maximize_viewport()
        dpg.show_viewport()

        # below replaces, start_dearpygui()
        while dpg.is_dearpygui_running():

            if sys.flags.dev_mode:
                jobs = dpg.get_callback_queue()  # retrieves and clears queue
                dpg.run_callbacks(jobs)

            # global is_load_default_layout_clicked
            if self.app_utility_controller.is_load_default_layout_clicked or self.app_utility_controller.is_window_close_button_clicked:
                dpg.stop_dearpygui()

            dpg.render_dearpygui_frame()

        log.close_ui()
        dpg.destroy_context()

        # global is_load_default_layout_clicked
        if self.app_utility_controller.is_load_default_layout_clicked:
            self.reset_to_default_layout()


class AppUtility(object):

    def init_and_render_ui(self):
        while not self.app_utility_controller.is_window_close_button_clicked:
            self.app_utility_ui = AppUtilityUI(self.app_utility_controller, self.group_members_panel, self.checked_out_files_panel)
            self.app_utility_ui.start()
            try:
                self.app_utility_ui.join()
                # Provide the option to reset the user data if there is an error.
                if self.app_utility_ui.reset_user_data:
                    # raise AppError(self.app_utility_ui.exception_message, True)
                    raise AppMessage(self.app_utility_ui.exception_message, True)
            except BaseException as e:
                raise e
            finally:
                if self.app_utility_controller.is_load_default_layout_clicked:
                    self.app_utility_controller.is_window_close_button_clicked = False
                    self.app_utility_controller.is_load_default_layout_clicked = False
                    continue

    def __init__(self):
        self.p4_ini_file = None
        self.p4_ini_file_path = None
        self.app_utility_controller = AppUtilityController()
        self.app_utility_ui = None

        self.group_members_panel = GroupMembersPanel()
        self.checked_out_files_panel = CheckedOutFilesPanel()

        self.init_and_render_ui()

        if self.app_utility_ui is not None:
            if self.app_utility_ui.user_close_ui:
                raise AppExit()
