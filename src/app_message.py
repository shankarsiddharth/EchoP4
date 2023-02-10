import sys

import dearpygui.dearpygui as dpg
from dearpygui_ext import themes

import p4_tools_helper as p4th
from app_globals import log


class AppMessageUI(object):
    __minimum_width__ = 700
    __minimum_height__ = 300

    def __init__(self, message=None, should_reset_data=False, viewport_width=__minimum_width__, viewport_height=__minimum_height__):
        self.message = message
        self.should_reset_data = should_reset_data
        # DearPyGUI's Viewport Constants
        if viewport_width is None or viewport_width <= self.__minimum_width__:
            viewport_width = self.__minimum_width__
        if viewport_height is None or viewport_height <= self.__minimum_height__:
            viewport_height = self.__minimum_height__
        self.VIEWPORT_WIDTH = viewport_width
        self.VIEWPORT_HEIGHT = viewport_height
        self.viewport_title = "Application Message"
        self.window_title = "Application Message Window"
        self.message_title_text = "Message"
        self.user_message_text_tag = "Message Text"
        self.close_button_tag = "Close Button"
        self.close_button_text = "Close Application"
        self.reset_data_button_tag = "Reset Data Button"
        self.red_button_theme_tag = "Red Button Theme"
        self.green_button_theme_tag = "Green Button Theme"
        self.tooltip_theme_tag = "Tooltip Theme"
        self.reset_data_group_tag = "Reset Data Group"
        self.reset_data_button_tooltip_text_tag = "Reset Data Button Tooltip Text"
        self.reset_data_button_tooltip_text = "Some User Data Files have been corrupted. \n" \
                                              "Application cannot function without these data.\n" \
                                              "Click this button to reset the User Data Files.\n" \
                                              "You need to configure the application again by providing user details,\n when you reopen/restart the application."
        self.text_wrap_length = self.VIEWPORT_WIDTH - 30
        self.auto_close_ui = False
        self.user_close_ui = False
        self.padding_value = 4
        self.cx = viewport_width - 200  # X coordinate of the close button
        self.cy = viewport_height - 100  # Y coordinate of the close button
        self.rx = viewport_width - 200 - 200  # X coordinate of the reset data button
        self.ry = viewport_height - 100  # Y coordinate of the reset data button
        self.__init_ui__()

    def close_ui(self):
        self.auto_close_ui = True

    def __exit_callback__(self):
        dpg.configure_item(self.close_button_tag, show=False)
        dpg.configure_item(self.reset_data_button_tag, show=False)
        log.info("User requested to close the Message Window.")
        if not self.auto_close_ui:
            self.user_close_ui = True

    def __close_button_clicked__(self, sender, data):
        dpg.configure_item(self.close_button_tag, show=False)
        dpg.configure_item(self.reset_data_button_tag, show=False)
        log.info("User requested to close the application.")
        self.close_ui()

    def __reset_data_button_clicked__(self, sender, data):
        dpg.configure_item(self.close_button_tag, show=False)
        exception_message = ''
        dpg.configure_item(self.user_message_text_tag, default_value="Trying to reset user data...")
        dpg.configure_item(self.reset_data_button_tag, show=False)
        dpg.configure_item(self.reset_data_group_tag, show=False)
        try:
            p4th.reset_user_data()
            log.info("User data reset successfully.")
        except BaseException as e:
            log.exception(e)
            exception_message = f"An error occurred while trying to reset the user data. \n Error: {e}"
            dpg.configure_item(self.user_message_text_tag, default_value=exception_message)
            return
        finally:
            dpg.configure_item(self.close_button_tag, show=True)
        if exception_message == '':
            dpg.configure_item(self.user_message_text_tag, default_value="User data has been reset.\nPlease restart the application.")

    @staticmethod
    def _hsv_to_rgb(h, s, v):
        if s == 0.0:
            return v, v, v
        i = int(h * 6.)  # assume int() truncates!
        f = (h * 6.) - i
        p, q, t = v * (1. - s), v * (1. - s * f), v * (1. - s * (1. - f))
        i %= 6
        if i == 0:
            return 255 * v, 255 * t, 255 * p
        if i == 1:
            return 255 * q, 255 * v, 255 * p
        if i == 2:
            return 255 * p, 255 * v, 255 * t
        if i == 3:
            return 255 * p, 255 * q, 255 * v
        if i == 4:
            return 255 * t, 255 * p, 255 * v
        if i == 5:
            return 255 * v, 255 * p, 255 * q

    def __init_ui__(self):
        dpg.create_context()

        dark_theme_id = themes.create_theme_imgui_dark()
        dpg.bind_theme(dark_theme_id)

        dpg.configure_app(manual_callback_management=sys.flags.dev_mode)

        dpg.create_viewport(title=self.viewport_title, width=self.VIEWPORT_WIDTH, height=self.VIEWPORT_HEIGHT, resizable=False, always_on_top=True)

        dpg.set_exit_callback(callback=self.__exit_callback__)

        with dpg.theme(tag=self.red_button_theme_tag):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, self._hsv_to_rgb(4.0 / 7.0, 0.6, 0.6))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, self._hsv_to_rgb(4.0 / 7.0, 0.8, 0.8))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, self._hsv_to_rgb(4.0 / 7.0, 0.7, 0.7))
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, self.padding_value * 5)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, self.padding_value * 3, self.padding_value * 3)

        if self.should_reset_data:
            with dpg.theme(tag=self.green_button_theme_tag):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, self._hsv_to_rgb(0.5, 0.6, 0.6))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, self._hsv_to_rgb(0.5, 0.8, 0.8))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, self._hsv_to_rgb(0.5, 0.7, 0.7))
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, self.padding_value * 5)
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, self.padding_value * 3, self.padding_value * 3)

            with dpg.theme(tag=self.tooltip_theme_tag):
                with dpg.theme_component(dpg.mvText):
                    dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 255, 0])

        # with dpg.window(label=self.window_title, tag=self.window_title, no_title_bar=False, no_close=True, modal=True, no_resize=True):
        with dpg.window(label=self.window_title, tag=self.window_title, no_title_bar=False, no_close=True, modal=False, no_resize=True):
            dpg.add_text(self.message_title_text)
            dpg.add_spacer(height=10)
            dpg.add_text(self.message, tag=self.user_message_text_tag, wrap=self.text_wrap_length)
            dpg.add_button(label=self.close_button_text, tag=self.close_button_tag, callback=self.__close_button_clicked__, pos=[self.cx, self.cy])
            dpg.bind_item_theme(self.close_button_tag, self.red_button_theme_tag)
            if self.should_reset_data:
                with dpg.group(tag=self.reset_data_group_tag, horizontal=True, pos=[self.rx, self.ry]):
                    dpg.add_button(label="Reset User Data", tag=self.reset_data_button_tag, callback=self.__reset_data_button_clicked__, pos=[self.rx, self.ry])
                    dpg.bind_item_theme(self.reset_data_button_tag, self.green_button_theme_tag)
                    with dpg.tooltip(self.reset_data_button_tag):
                        dpg.add_text(default_value=self.reset_data_button_tooltip_text, tag=self.reset_data_button_tooltip_text_tag)
                        dpg.bind_item_theme(self.reset_data_button_tooltip_text_tag, self.tooltip_theme_tag)

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

        log.close_ui()
        dpg.destroy_context()


class AppMessage(Exception):

    def __init__(self, message=None, should_reset_data=False):
        self.message = message
        self.should_reset_data = should_reset_data
        self.app_message_ui = AppMessageUI(message=message, should_reset_data=should_reset_data)

    def __str__(self):
        if self.message is None:
            return "Application Message"
        else:
            return self.message
