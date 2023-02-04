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

    def __init__(self, app_utility_controller=None, viewport_width=__minimum_width__, viewport_height=__minimum_height__):
        super().__init__()

        self.exception = None

        if app_utility_controller is None:
            self.app_utility_controller = None
            return

        self.app_utility_controller: AppUtilityController = app_utility_controller

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

        # ***** Command Window ***** #
        # Make Writable
        self.make_writable_tag = "Make Writable"
        # Clear Intermediate
        self.clear_intermediate_tag = "Clear Intermediate"
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

    def add_log(self):
        log.debug("Button Clicked")

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

        # add a font registry
        with dpg.font_registry():
            # first argument ids the path to the .ttf or .otf file
            default_font = dpg.add_font(p4th.get_default_font_file_path(), p4th.get_default_font_size())

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
            with dpg.collapsing_header(label=self.make_writable_tag, tag=self.make_writable_tag, default_open=True):
                dpg.add_text("Hello, world")
                dpg.add_button(label="Add Log", callback=self.add_log)
                dpg.add_input_text(label="string", default_value="Quick brown fox")
                dpg.add_slider_float(label="float", default_value=0.273, max_value=1)
                dpg.add_separator()

        dpg.show_font_manager()

        log.init_ui()

        dpg.setup_dearpygui()
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
            self.app_utility_ui = AppUtilityUI(self.app_utility_controller)
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

        self.init_and_render_ui()

        if self.app_utility_ui is not None:
            if self.app_utility_ui.user_close_ui:
                raise AppExit()
