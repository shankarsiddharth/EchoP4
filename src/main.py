import shutil
import sys
import threading

import dearpygui.dearpygui as dpg
from dearpygui_ext import themes

import echo_p4_constants
from app_error import AppError
from app_exit import AppExit
from app_globals import log
from application_initial_setup import ApplicationInitialSetup

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

    try:
        ApplicationInitialSetup()
    except AppExit as e:
        log.info("Application Exited by User.")
        sys.exit(0)
    except AppError as e:
        log.error(str(e))
        sys.exit(0)
    except BaseException as e:
        log.error("Error occurred while initializing the application: " + str(e))
        sys.exit(0)

    log.info("Starting the application...")

    main()
