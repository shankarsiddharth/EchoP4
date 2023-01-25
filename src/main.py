import os
import sys
import shutil
import threading

from P4 import P4, P4Exception

import dearpygui.demo as demo
import dearpygui.dearpygui as dpg
from dearpygui_ext import themes

import echo_p4_constants
import echo_p4_logger as ep4l
import p4_tools_helper as p4th
from p4_config import P4Config
from echo_p4_config import EchoP4Config

# Initialize the logger
log = ep4l.EchoP4Logger()
log.info("sys.flags.dev_mode : %s", sys.flags.dev_mode)

# sys.exit(0)

# TODO: Check if the file p4.ini exists in the config folder.
# If exists, then load the values from the file and start the tool UI
# If not, then show the config UI and then start the tool UI on success.

user_echo_p4_config_data = p4th.get_user_echo_p4_config_data()
user_p4_config_data = p4th.get_user_p4_config_data()

if user_echo_p4_config_data is None:
    log.info("No application config file found.")
    log.info("Trying to create a new config file for the current user...")
    user_echo_p4_config = EchoP4Config()
    log.info("New application config file created for the current user.")
else:
    log.info("Application Config file found. Checking for P4 user config...")
    if user_p4_config_data is None:
        log.info("No P4 config file found.")
        log.info("Trying to create a new P4 config file for the current user...")
        user_p4_config = P4Config(user_echo_p4_config_data=user_echo_p4_config_data)
        log.info("New P4 config file created for the current user.")
    else:
        log.info("P4 Config file found.")
        user_p4_config = P4Config()
        is_login_success = user_p4_config.p4_login(user_p4_config_data=user_p4_config_data)
        while not is_login_success:
            log.info("P4 login failed with the saved data.")
            user_p4_config.delete_user_p4_config_file()
            log.info("Trying to create a new P4 config file for the current user...")
            user_p4_config = P4Config(user_echo_p4_config_data=user_echo_p4_config_data)
            user_p4_config_data = p4th.get_user_p4_config_data()
            is_login_success = user_p4_config.p4_login(user_p4_config_data=user_p4_config_data)
        print(user_p4_config_data)

# sys.exit(0)

p4_config = p4th.get_user_p4_config_data()
encrypted_password = p4_config[echo_p4_constants.P4_CONFIG_SECTION][echo_p4_constants.KEY_P4PASSWD]
decrypted_password = p4th.decrypt_password(encrypted_password)
print("Decrypted password: " + decrypted_password)

# Constants
is_load_default_layout_clicked = False
# is_menu_close_button_clicked = False
is_window_close_button_clicked = False

# DearPyGUI's Viewport Constants
VIEWPORT_WIDTH = 1200
VIEWPORT_HEIGHT = 900  # 700


def save_current_layout_to_init():
    dpg.save_init_file("../config/" + echo_p4_constants.DPG_INI_FILE_NAME)


def load_default_layout():
    global is_load_default_layout_clicked
    is_load_default_layout_clicked = True


def reset_to_default_layout():
    shutil.copy("../config/defaults/" + echo_p4_constants.DEFAULT_DPG_INI_FILE_NAME, "../config/" + echo_p4_constants.DPG_INI_FILE_NAME)


# def close_app():
#     global is_menu_close_button_clicked
#     is_menu_close_button_clicked = True


def exit_callback():
    global is_window_close_button_clicked
    is_window_close_button_clicked = True


def add_log():
    log.debug("Button Clicked")


def init_and_render_ui():
    global is_load_default_layout_clicked

    dpg.create_context()

    # demo.show_demo()

    light_theme_id = themes.create_theme_imgui_light()
    dark_theme_id = themes.create_theme_imgui_dark()
    dpg.bind_theme(dark_theme_id)

    dpg.configure_app(manual_callback_management=sys.flags.dev_mode, docking=True, docking_space=True, init_file="../config/" + echo_p4_constants.DPG_INI_FILE_NAME,
                      load_init_file=True)

    dpg.create_viewport(title=echo_p4_constants.ECHO_P4_TOOL_WINDOW_TITLE, width=VIEWPORT_WIDTH, height=VIEWPORT_HEIGHT)

    dpg.set_exit_callback(callback=exit_callback)

    with dpg.viewport_menu_bar():
        with dpg.menu(label=echo_p4_constants.FILE_MENU, tag=echo_p4_constants.FILE_MENU):
            dpg.add_menu_item(label=echo_p4_constants.SAVE_CURRENT_LAYOUT_TO_DPG_INI, tag=echo_p4_constants.SAVE_CURRENT_LAYOUT_TO_DPG_INI,
                              callback=save_current_layout_to_init)
            dpg.add_menu_item(label=echo_p4_constants.RESET_TO_DEFAULT_LAYOUT, tag=echo_p4_constants.RESET_TO_DEFAULT_LAYOUT, callback=load_default_layout)
            # dpg.add_menu_item(label="Close", tag="Close", callback=close_app)

    with dpg.window(label=echo_p4_constants.ECHO_P4_COMMAND_WINDOW, tag=echo_p4_constants.ECHO_P4_COMMAND_WINDOW, no_title_bar=False, no_close=True):
        dpg.add_text("Hello, world")
        dpg.add_button(label="Add Log", callback=add_log)
        dpg.add_input_text(label="string", default_value="Quick brown fox")
        dpg.add_slider_float(label="float", default_value=0.273, max_value=1)

    log.init_ui()

    dpg.setup_dearpygui()
    dpg.show_viewport()

    # dpg.set_primary_window(echo_p4_constants.ECHO_P4_COMMAND_WINDOW, True)

    # below replaces, start_dearpygui()
    while dpg.is_dearpygui_running():

        if sys.flags.dev_mode:
            jobs = dpg.get_callback_queue()  # retrieves and clears queue
            dpg.run_callbacks(jobs)

        # global is_load_default_layout_clicked
        if is_load_default_layout_clicked:
            dpg.stop_dearpygui()
            # dpg.destroy_context()
            # break

        # global is_load_default_layout_clicked
        # if is_load_default_layout_clicked:
        #     reset_to_default_layout()
        #     is_load_default_layout_clicked = False

        dpg.render_dearpygui_frame()
    # dpg.delete_item(item=echo_p4_constants.ECHO_P4_TOOL_WINDOW_TITLE, children_only=False)
    # dpg.configure_viewport(item=echo_p4_constants.ECHO_P4_TOOL_WINDOW_TITLE, show=False)
    dpg.destroy_context()

    # global is_load_default_layout_clicked
    if is_load_default_layout_clicked:
        reset_to_default_layout()


def main() -> None:
    global is_window_close_button_clicked
    while not is_window_close_button_clicked:
        dpg_thread = threading.Thread(target=init_and_render_ui)
        dpg_thread.start()
        dpg_thread.join()

        global is_load_default_layout_clicked
        if is_load_default_layout_clicked:
            is_window_close_button_clicked = False
            is_load_default_layout_clicked = False
            continue


if __name__ == "__main__":
    main()
