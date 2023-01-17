import dearpygui.dearpygui as dpg
import logging


class EchoP4UILogger:

    def __init__(self, parent, is_open=True):

        self.log_level = 0
        self._auto_scroll = True
        self._default_show_all_logs = False
        self._show_all_logs_tag = "UI Logger Show All Logs"
        self._filter_text_tag = "UI Logger Filter Text Box"
        self.filter_id = None
        if parent:
            self.window_id = parent
            # self.window_id = dpg.add_collapsing_header(label="Logger", tag="Logger", default_open=is_open, parent=parent)
        else:
            self.window_id = dpg.add_window(label="Echo P4 Logger", no_title_bar=False, no_close=True)
            # self.window_id = dpg.add_collapsing_header(label="Logger", tag="Logger", default_open=is_open)
        self.count = 0
        self.flush_count = 10000

        # with dpg.add_collapsing_header(label="Logger", default_open=True, parent=self.window_id):
        with dpg.group(horizontal=True, parent=self.window_id):
            dpg.add_checkbox(label="Auto-scroll", default_value=True, callback=lambda sender: self.auto_scroll(dpg.get_value(sender)))
            dpg.add_checkbox(tag=self._show_all_logs_tag, label="Show All Logs", default_value=self._default_show_all_logs, callback=self.__callback_show_all_logs)
            dpg.add_button(label="Clear", callback=lambda: dpg.delete_item(self.filter_id, children_only=True))

        dpg.add_input_text(tag=self._filter_text_tag, label="Filter", callback=self.__callback_on_filter_text_changed,
                           parent=self.window_id)
        self.child_id = dpg.add_child_window(parent=self.window_id, autosize_x=True, autosize_y=True)
        # self.child_id = dpg.add_child(parent=self.window_id, autosize_x=True, autosize_y=True)
        self.filter_id = dpg.add_filter_set(parent=self.child_id)

        with dpg.theme() as self.trace_theme:
            with dpg.theme_component(0):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))

        with dpg.theme() as self.debug_theme:
            with dpg.theme_component(0):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (64, 128, 255, 255))

        with dpg.theme() as self.info_theme:
            with dpg.theme_component(0):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 255, 0, 255))

        with dpg.theme() as self.warning_theme:
            with dpg.theme_component(0):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 0, 255))

        with dpg.theme() as self.error_theme:
            with dpg.theme_component(0):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0, 255))

        with dpg.theme() as self.critical_theme:
            with dpg.theme_component(0):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0, 255))

        self.__on_show_all_logs()

    def auto_scroll(self, value):
        self._auto_scroll = value

    def __callback_show_all_logs(self, sender):
        self.__on_show_all_logs()

    def __on_show_all_logs(self):
        show_all_logs = dpg.get_value(self._show_all_logs_tag)
        if show_all_logs:
            dpg.set_value(self.filter_id, '')
        else:
            dpg.set_value(self.filter_id, 'INFO, WARNING, ERROR, CRITICAL')

    def __callback_on_filter_text_changed(self, sender):
        filter_text = dpg.get_value(self._filter_text_tag)
        if str(filter_text) != '':
            dpg.configure_item(self._show_all_logs_tag, default_value=True)
            dpg.set_value(self.filter_id, filter_text)
        else:
            dpg.configure_item(self._show_all_logs_tag, default_value=False)
            self.__on_show_all_logs()

    def _log(self, message, level):

        if level < self.log_level:
            return

        self.count += 1

        if self.count > self.flush_count:
            self.clear_log()

        theme = self.info_theme

        if level == logging.NOTSET:
            message = "[TRACE]\t\t" + message
            theme = self.trace_theme
        elif level == logging.DEBUG:
            message = "[DEBUG]\t\t" + message
            theme = self.debug_theme
        elif level == logging.INFO:
            message = "[INFO]\t\t" + message
            theme = self.info_theme
        elif level == logging.WARNING:
            message = "[WARNING]\t\t" + message
            theme = self.warning_theme
        elif level == logging.ERROR:
            message = "[ERROR]\t\t" + message
            theme = self.error_theme
        elif level == logging.CRITICAL:
            message = "[CRITICAL]\t\t" + message
            theme = self.critical_theme

        new_log = dpg.add_text(message, parent=self.filter_id, filter_key=message)
        dpg.bind_item_theme(new_log, theme)
        if self._auto_scroll:
            scroll_max = dpg.get_y_scroll_max(self.child_id)
            dpg.set_y_scroll(self.child_id, -1.0)

    def trace(self, message):
        self._log(message, logging.NOTSET)

    def log_debug(self, message):
        self._log(message, logging.DEBUG)

    def log_info(self, message):
        self._log(message, logging.INFO)

    def log_warning(self, message):
        self._log(message, logging.WARNING)

    def log_error(self, message):
        self._log(message, logging.ERROR)

    def log_critical(self, message):
        self._log(message, logging.CRITICAL)

    def clear_log(self):
        dpg.delete_item(self.filter_id, children_only=True)
        self.count = 0
