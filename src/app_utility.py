import configparser
import os
import pathlib
import platform
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

        pass

    def __make_plugin_binaries_writable__(self, sender, data):
        log.info("User clicked on the Make Plugin Binaries Writable button.")

        pass

    def __make_project_source_writable__(self, sender, data):
        log.info("User clicked on the Make Project Source Writable button.")

        pass

    def __make_plugin_source_writable__(self, sender, data):
        log.info("User clicked on the Make Plugin Source Writable button.")

        pass

    def __clear_project_intermediate__(self, sender, data):
        log.info("User clicked on the Clear Project Intermediate button.")

        pass

    def __clear_plugin_intermediate__(self, sender, data):
        log.info("User clicked on the Clear Plugin Intermediate button.")

        pass

    def __clear_project_saved__(self, sender, data):
        log.info("User clicked on the Clear Project Saved button.")

        pass

    def __clear_plugin_saved__(self, sender, data):
        log.info("User clicked on the Clear Plugin Saved button.")

        pass

    def __init_ui__(self):

        dpg.create_context()

        # demo.show_demo()

        light_theme_id = themes.create_theme_imgui_light()
        dark_theme_id = themes.create_theme_imgui_dark()
        dpg.bind_theme(dark_theme_id)

        dpg.configure_app(manual_callback_management=sys.flags.dev_mode, docking=True, docking_space=True, init_file="../config/" + ep4c.DPG_INI_FILE_NAME,
                          load_init_file=True)

        dpg.create_viewport(title=self.viewport_title, width=self.VIEWPORT_WIDTH, height=self.VIEWPORT_HEIGHT)

        dpg.set_exit_callback(callback=self.__exit_callback__)

        # Add Theme
        with dpg.theme(tag=self.red_button_theme_tag):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (200, 0, 0, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (178, 34, 34, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (220, 20, 60, 255))

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
                    dpg.add_text("Click the button to make all the files in the Project Binaries folder writable.")
                    dpg.add_button(label=self.make_project_binaries_writable_tag, tag=self.make_project_binaries_writable_tag, callback=self.__make_project_binaries_writable__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    self._help(self.make_writable_help_message)
                    dpg.add_separator()
                with dpg.tree_node(label=self.make_writable_plugin_binaries_tree_tag, tag=self.make_writable_plugin_binaries_tree_tag, default_open=True):
                    dpg.add_text("Click the button to make all the files in the Plugin Binaries folder writable.")
                    dpg.add_button(label=self.make_plugin_binaries_writable_tag, tag=self.make_plugin_binaries_writable_tag, callback=self.__make_plugin_binaries_writable__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    self._help(self.make_writable_help_message)
                    dpg.add_separator()
                with dpg.tree_node(label=self.make_writable_project_source_tree_tag, tag=self.make_writable_project_source_tree_tag, default_open=True):
                    dpg.add_text("Click the button to make all the files in the Project Source folder writable.")
                    dpg.add_button(label=self.make_project_source_writable_tag, tag=self.make_project_source_writable_tag, callback=self.__make_project_source_writable__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    self._help(self.make_writable_help_message)
                    dpg.add_separator()
                with dpg.tree_node(label=self.make_writable_plugin_source_tree_tag, tag=self.make_writable_plugin_source_tree_tag, default_open=True):
                    dpg.add_text("Click the button to make all the files in the Plugin Source folder writable.")
                    dpg.add_button(label=self.make_plugin_source_writable_tag, tag=self.make_plugin_source_writable_tag, callback=self.__make_plugin_source_writable__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    self._help(self.make_writable_help_message)
                    dpg.add_separator()
            # Clear Intermediate
            with dpg.collapsing_header(label=self.clear_intermediate_tag, tag=self.clear_intermediate_tag, default_open=True):
                with dpg.tree_node(label=self.clear_project_intermediate_tree_tag, tag=self.clear_project_intermediate_tree_tag, default_open=True):
                    dpg.add_text("Click the button to delete Project Intermediate folder.")
                    dpg.add_button(label=self.clear_project_intermediate_tag, tag=self.clear_project_intermediate_tag, callback=self.__clear_project_intermediate__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    dpg.bind_item_theme(dpg.last_item(), self.red_button_theme_tag)
                    self._help(self.clear_intermediate_help_message)
                    dpg.add_separator()
                with dpg.tree_node(label=self.clear_plugin_intermediate_tree_tag, tag=self.clear_plugin_intermediate_tree_tag, default_open=True):
                    dpg.add_text("Click the button to delete Plugin Intermediate folder.")
                    dpg.add_button(label=self.clear_plugin_intermediate_tag, tag=self.clear_plugin_intermediate_tag, callback=self.__clear_plugin_intermediate__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    dpg.bind_item_theme(dpg.last_item(), self.red_button_theme_tag)
                    self._help(self.clear_intermediate_help_message)
                    dpg.add_separator()
            # Clear Saved
            with dpg.collapsing_header(label=self.clear_saved_tag, tag=self.clear_saved_tag, default_open=True):
                with dpg.tree_node(label=self.clear_project_saved_tree_tag, tag=self.clear_project_saved_tree_tag, default_open=True):
                    dpg.add_text("Click the button to delete Project Saved folder.")
                    dpg.add_button(label=self.clear_project_saved_tag, tag=self.clear_project_saved_tag, callback=self.__clear_project_saved__)
                    dpg.bind_item_font(dpg.last_item(), default_bold_font)
                    dpg.bind_item_theme(dpg.last_item(), self.red_button_theme_tag)
                    self._help(self.clear_saved_help_message)
                    dpg.add_separator()
                with dpg.tree_node(label=self.clear_plugin_saved_tree_tag, tag=self.clear_plugin_saved_tree_tag, default_open=True):
                    dpg.add_text("Click the button to delete Plugin Saved folder.")
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
