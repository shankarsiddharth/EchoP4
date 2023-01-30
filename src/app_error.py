import sys

import dearpygui.dearpygui as dpg
from dearpygui_ext import themes

from app_globals import log


class AppErrorUI(object):
    __minimum_width__ = 700
    __minimum_height__ = 300

    def __init__(self, message=None, viewport_width=__minimum_width__, viewport_height=__minimum_height__):
        self.message = message
        # DearPyGUI's Viewport Constants
        if viewport_width is None or viewport_width <= self.__minimum_width__:
            viewport_width = self.__minimum_width__
        if viewport_height is None or viewport_height <= self.__minimum_height__:
            viewport_height = self.__minimum_height__
        self.VIEWPORT_WIDTH = viewport_width
        self.VIEWPORT_HEIGHT = viewport_height
        self.viewport_title = "Application Error"
        self.window_title = "Application Error Window"
        self.error_message_text_tag = "Error Message Text"
        self.close_button_tag = "Close Button"
        self.red_button_theme_tag = "Red Button Theme"
        self.auto_close_ui = False
        self.user_close_ui = False
        self.padding_value = 4
        self.x = viewport_width - 200
        self.y = viewport_height - 100
        self.__init_ui__()

    def close_ui(self):
        self.auto_close_ui = True

    def __exit_callback__(self):
        if not self.auto_close_ui:
            log.info("User Closed the Application Error UI.")
            self.user_close_ui = True

    def __close_button_clicked__(self, sender, data):
        self.close_ui()

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

        dpg.create_viewport(title=self.viewport_title, width=self.VIEWPORT_WIDTH, height=self.VIEWPORT_HEIGHT)

        dpg.set_exit_callback(callback=self.__exit_callback__)

        with dpg.theme(tag=self.red_button_theme_tag):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, self._hsv_to_rgb(0, 0.6, 0.6))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, self._hsv_to_rgb(0, 0.8, 0.8))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, self._hsv_to_rgb(0, 0.7, 0.7))
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, self.padding_value * 5)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, self.padding_value * 3, self.padding_value * 3)

        with dpg.window(label=self.window_title, tag=self.window_title, no_title_bar=False, no_close=True):
            dpg.add_text("Error Message")
            dpg.add_spacer(height=10)
            dpg.add_text(self.message, tag=self.error_message_text_tag)
            dpg.add_button(label="Close Application", tag=self.close_button_tag, callback=self.__close_button_clicked__, pos=[self.x, self.y])
            dpg.bind_item_theme(dpg.last_item(), self.red_button_theme_tag)

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


class AppError(object):

    def __init__(self, message=None):
        self.app_error_ui = AppErrorUI(message=message)


if __name__ == "__main__":
    app_error = AppError(message="This is an error message.")
