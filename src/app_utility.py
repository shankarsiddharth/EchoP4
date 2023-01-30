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
from app_error import AppError
from app_exit import AppExit
from app_globals import log


class AppUtilityController(object):

    def __init__(self):
        self.exception_message = ''
        self.result = dict()


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
        self.viewport_title = "Echo P4 Tool UI"
        self.window_title = "Echo P4 Tool UI Window"
        self.auto_close_ui = False
        self.user_close_ui = False
        self.reset_user_data = False
        self.exception_message = ''

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

    def close_ui(self):
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


class AppUtility(object):

    def init_and_render_ui(self):
        self.app_utility_ui = AppUtilityUI(self.app_utility_controller)
        self.app_utility_ui.start()
        try:
            self.app_utility_ui.join()
            # Provide the option to reset the user data if there is an error.
            if self.app_utility_ui.reset_user_data:
                raise AppError(self.app_utility_ui.exception_message, True)
        except Exception as e:
            raise e

    def __init__(self):
        self.p4_ini_file = None
        self.p4_ini_file_path = None
        self.app_utility_controller = AppUtilityController()
        self.app_utility_ui = None

        self.init_and_render_ui()

        if self.app_utility_ui is not None:
            if self.app_utility_ui.user_close_ui:
                raise AppExit()

    def close_ui(self):
        if self.app_utility_ui is None:
            return
        self.app_utility_ui.close_ui()
