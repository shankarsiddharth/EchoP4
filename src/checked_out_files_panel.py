import json
import logging
import os
import re
from datetime import datetime

import dearpygui.dearpygui as dpg
from P4 import P4, P4Exception

import p4_tools_helper as p4th
import echo_p4_constants as ep4c
from app_error import AppError
from app_globals import log


class CheckedOutFilesController:

    def __init__(self):
        self.regex_pattern = r"(//.+/...) (//.+/...)"  # e.g. //depot/... //client/...
        self.checked_out_files = dict()
        self.last_refresh_time_text = "Click Refresh to get the latest data"

        if not p4th.is_group_members_info_present():
            raise AppError("Group members info file not found", should_reset_data=True)

        group_members_info_file_path = p4th.get_group_members_info_file_path()
        with open(group_members_info_file_path, 'r', encoding='UTF-8') as group_members_info_file:
            self.group_members_info = json.load(group_members_info_file)

        self.group_members_info_dict = dict()
        for group_member_id, group_member_info in self.group_members_info.items():
            full_name = group_member_info["FullName"]
            full_name_split = full_name.split(" ")
            self.group_members_info_dict[group_member_id] = full_name_split[0]

    def get_checked_out_files(self):

        self.checked_out_files.clear()

        user_p4_config_data = p4th.get_user_p4_config_data()
        if user_p4_config_data is None:
            raise AppError("User p4 config data not found", should_reset_data=True)

        p4_port = user_p4_config_data[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PORT]
        p4_user = user_p4_config_data[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4USER]
        p4_client = user_p4_config_data[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4CLIENT]
        encrypted_password = user_p4_config_data[ep4c.P4_CONFIG_SECTION][ep4c.KEY_P4PASSWD]
        p4_password = p4th.decrypt_password(encrypted_password)

        p4 = P4()
        p4.port = p4_port
        p4.user = p4_user
        p4.client = p4_client
        p4.password = p4_password

        try:
            # p4.client = client
            p4.connect()
            # p4.run_login()

            p4_client_detail_list = p4.run("client", "-o")
            if len(p4_client_detail_list) == 0:
                raise AppError("Unable to get client details.")

            p4_client_detail = p4_client_detail_list[0]
            p4_client_view = p4_client_detail["View"]
            if len(p4_client_view) == 0:
                raise AppError("Unable to get client view details.")

            p4_current_client_view_string = p4_client_view[0].strip()
            matches = re.search(self.regex_pattern, p4_current_client_view_string)
            if matches is None or len(matches.groups()) != 2:
                raise AppError("Unable to get client view details.")

            p4_client_view_depot_path = matches.group(1)
            p4_client_view_client_path = matches.group(2)

            checked_out_files = p4.run("opened", "-a", p4_client_view_depot_path)
            if len(checked_out_files) == 0:
                logging.info("No files checked out.")
                return self.checked_out_files
            self.__update_last_refresh_time_text__()

            p4_client_view_depot_path_string = p4_client_view_depot_path.replace("...", "")
            checked_out_file_count = 0
            for checked_out_file_info in checked_out_files:
                checked_out_file_count += 1
                depot_file_path = checked_out_file_info["depotFile"]
                file_name_details = os.path.split(depot_file_path)
                file_name = file_name_details[1].strip()
                file_path = file_name_details[0].strip()
                project_file_path = file_path.replace(p4_client_view_depot_path_string, "")
                if file_name == "":
                    file_name = project_file_path
                    project_file_path = ""
                client_file_path = checked_out_file_info["clientFile"]
                client_name = checked_out_file_info["client"]
                user_id = checked_out_file_info["user"]
                user_name = self.group_members_info_dict[user_id]
                self.checked_out_files[checked_out_file_count] = {
                    "FileName": file_name,
                    "UserName": user_name,
                    "ClientName": client_name,
                    "UserId": user_id,
                    "ProjectFilePath": project_file_path,
                    "DepotFilePath": depot_file_path,
                    "ClientFilePath": client_file_path
                }

            p4.disconnect()
        except P4Exception as e:
            log.exception(e)
            raise AppError(e, should_reset_data=True)
        except BaseException as e:
            log.exception(e)
            raise AppError(e, should_reset_data=True)
        finally:
            if p4.connected():
                p4.disconnect()

        return self.checked_out_files

    def __update_last_refresh_time_text__(self):
        self.last_refresh_time_text = "Last Refresh: " + datetime.now().strftime("%d %B, %Y - %I:%M:%S %p")

    def get_last_refresh_time_text(self):
        return self.last_refresh_time_text


class CheckedOutFilesPanel:
    def __init__(self, parent=None, is_open=True):

        self.controller: CheckedOutFilesController = CheckedOutFilesController()

        self.window_id = None
        self.uid_column = None
        self.username_column = None
        self.file_name_column = None
        self.workspace_name_column = None
        self.path_column = None
        self.filter_id = None
        self.child_id = None

        self.window_tag = "Checked Out Files"
        self.refresh_button_tag = "Refresh"
        self.show_all_id = "Show All Files"
        self.hide_external_id = "Hide External Actors & Objects"
        self.hide_binaries_id = "Hide Binaries"
        self.hide_source_id = "Hide Source"
        self.hide_config_id = "Hide Config"
        self.hide_content_id = "Hide Content"
        self.hide_plugins_id = "Hide Plugins"
        self.checked_out_files_table_tag = None
        self._filter_text_tag = "Checked Out Filter Text Box"
        self.refresh_group_tag = "Refresh Group"
        self.filter_group_tag = "Filter Group"
        self.hide_filter_group_tag = "Hide Filter Group"
        self.last_refresh_time_text_tag = "Last Refresh Time Text"
        self.last_refresh_time_text = self.controller.get_last_refresh_time_text()

        self.filter_ui_text = ""
        self.filter_ui_text_previous = ""
        self.filter_text_current = ""
        self.filter_text_external_actors = "-__ExternalActors__,"
        self.filter_text_external_objects = "-__ExternalObjects__,"
        self.filter_text_binaries = "-Binaries,"
        self.filter_text_source = "-Source,"
        self.filter_text_config = "-Config,"
        self.filter_text_content = "-Content,"
        self.filter_text_plugins = "-Plugins,"

        self.filter_text_current = self.filter_text_external_actors + self.filter_text_external_objects + self.filter_text_binaries
        # self.filter_text_current += self.filter_text_source + self.filter_text_config + self.filter_text_plugins
        self.filter_text_current += self.filter_text_source + self.filter_text_config

        self.checked_out_files = dict()
        self.checked_out_files = self.controller.get_checked_out_files()

    def init_ui(self, parent=None, is_open=True):
        if parent:
            self.window_id = parent
        else:
            self.window_id = dpg.add_window(label=self.window_tag, tag=self.window_tag, no_title_bar=False, no_close=True)

        self.checked_out_files_table_tag = dpg.generate_uuid()
        self.filter_id = dpg.add_input_text(parent=self.window_id, label="Filter (inc, -exc)", user_data=self.checked_out_files_table_tag,
                                            default_value=self.filter_ui_text, show=False,
                                            # callback=lambda s, a, u: dpg.set_value(u, dpg.get_value(s)))
                                            callback=self.__callback_on_filter_text_changed__)

        with dpg.group(tag=self.filter_group_tag, horizontal=True, parent=self.window_id, before=self.filter_id, show=True):
            dpg.add_checkbox(tag=self.show_all_id, label=self.show_all_id, default_value=False, show=False, callback=self.__callback_show_all_files__)
            with dpg.group(tag=self.hide_filter_group_tag, horizontal=True, show=False):
                dpg.add_checkbox(tag=self.hide_binaries_id, label=self.hide_binaries_id, default_value=True, callback=self.__callback_hide_binaries__)
                dpg.add_checkbox(tag=self.hide_config_id, label=self.hide_config_id, default_value=True, callback=self.__callback_hide_config__)
                dpg.add_checkbox(tag=self.hide_content_id, label=self.hide_content_id, default_value=False, callback=self.__callback_hide_content__)
                dpg.add_checkbox(tag=self.hide_external_id, label=self.hide_external_id, default_value=True, callback=self.__callback_hide_external__)
                # dpg.add_checkbox(tag=self.hide_plugins_id, label=self.hide_plugins_id, default_value=True, callback=self.__callback_hide_plugins__)
                dpg.add_checkbox(tag=self.hide_source_id, label=self.hide_source_id, default_value=True, callback=self.__callback_hide_source__)

        with dpg.group(tag=self.refresh_group_tag, horizontal=True, parent=self.window_id, before=self.filter_group_tag):
            dpg.add_button(tag=self.refresh_button_tag, label=self.refresh_button_tag, callback=self.__callback_on_refresh__)
            dpg.add_text(tag=self.last_refresh_time_text_tag, default_value=self.last_refresh_time_text)

        self.__update_table__()

    def __update_table__(self):
        with dpg.table(parent=self.window_id, tag=self.checked_out_files_table_tag, show=False,
                       header_row=True, policy=dpg.mvTable_SizingFixedFit,
                       borders_innerH=True, borders_outerH=True,
                       borders_innerV=True, borders_outerV=True,
                       row_background=True, sortable=True, resizable=True, reorderable=False, no_host_extendX=True,
                       # callback=lambda sender, app_data, user_data: self.sort_callback(sender, None)):
                       callback=self.sort_callback) as self.table_id:
            self.file_name_column = dpg.add_table_column(label="Checked Out File", default_sort=True, prefer_sort_ascending=True, no_clip=True, width_fixed=False)
            self.username_column = dpg.add_table_column(label="User", default_sort=True, prefer_sort_ascending=True, no_clip=True, width_fixed=False)
            self.workspace_name_column = dpg.add_table_column(label="Workspace", default_sort=True, prefer_sort_ascending=True, no_clip=True, width_fixed=False)
            self.uid_column = dpg.add_table_column(label="uID", default_sort=True, prefer_sort_ascending=True, no_clip=True, width_fixed=False)
            self.path_column = dpg.add_table_column(label="Path", default_sort=True, prefer_sort_ascending=True, no_clip=True, width_stretch=False, init_width_or_weight=0.0)

            for file_count, file_details in self.checked_out_files.items():
                file_name = file_details["FileName"]
                user_name = file_details["UserName"]
                client_name = file_details["ClientName"]
                user_id = file_details["UserId"]
                project_file_path = file_details["ProjectFilePath"]
                filter_key_text = f"{file_name} {user_name} {client_name} {user_id} {project_file_path}"
                with dpg.table_row(filter_key=filter_key_text):
                    dpg.add_text(file_name)
                    dpg.add_text(user_name)
                    dpg.add_text(client_name)
                    dpg.add_text(str(user_id))
                    dpg.add_text(project_file_path)

    def sort_callback(self, sender, sort_specs):
        # sort_specs scenarios:
        #   1. no sorting -> sort_specs == None
        #   2. single sorting -> sort_specs == [[column_id, direction]]
        #   3. multi sorting -> sort_specs == [[column_id, direction], [column_id, direction], ...]
        #
        # notes:
        #   1. direction is ascending if == 1
        #   2. direction is ascending if == -1

        # no sorting case
        if sort_specs is None:
            return

        rows = dpg.get_item_children(sender, 1)

        # create a list that can be sorted based on first cell
        # value, keeping track of row and value used to sort
        sortable_list = []
        for row in rows:
            first_cell = None

            if sort_specs[0][0] == self.file_name_column:
                first_cell = dpg.get_item_children(row, 1)[0]
            elif sort_specs[0][0] == self.username_column:
                first_cell = dpg.get_item_children(row, 1)[1]
            elif sort_specs[0][0] == self.workspace_name_column:
                first_cell = dpg.get_item_children(row, 1)[2]
            elif sort_specs[0][0] == self.uid_column:
                first_cell = dpg.get_item_children(row, 1)[3]
            elif sort_specs[0][0] == self.path_column:
                first_cell = dpg.get_item_children(row, 1)[4]

            if first_cell is not None:
                sortable_list.append([row, dpg.get_value(first_cell)])

        def _sorter(e):
            return e[1]

        sortable_list.sort(key=_sorter, reverse=sort_specs[0][1] < 0)

        # create list of just sorted row ids
        new_order = []
        for pair in sortable_list:
            new_order.append(pair[0])

        dpg.reorder_items(sender, 1, new_order)

    def __process_filter_text__(self):
        self.filter_ui_text = self.filter_ui_text.removesuffix(self.filter_ui_text_previous)
        self.filter_text_current = self.filter_text_current.removesuffix(self.filter_ui_text_previous)
        self.filter_ui_text = dpg.get_value(self.filter_id)
        if self.filter_ui_text != "":
            self.filter_ui_text_previous = self.filter_ui_text + ","
            self.filter_text_current += self.filter_ui_text + ","
        elif self.filter_ui_text == "":
            self.filter_ui_text_previous = ""

    def __callback_on_filter_text_changed__(self, sender, app_data, user_data):
        self.__process_filter_text__()
        dpg.set_value(self.checked_out_files_table_tag, self.filter_text_current)
        log.trace(f"Filter: {self.filter_text_current}")

    def __callback_hide_external__(self, sender, app_data, user_data):
        is_checked = dpg.get_value(sender)
        is_content_hidden = dpg.get_value(self.hide_content_id)
        if not is_checked and is_content_hidden:
            dpg.set_value(self.hide_external_id, True)
            log.warning("Cannot show external actors & objects if content is hidden")
            return
        self.filter_text_current = self.filter_text_current.replace(self.filter_text_external_actors, "")
        self.filter_text_current = self.filter_text_current.replace(self.filter_text_external_objects, "")
        if is_checked:
            self.filter_text_current = self.filter_text_external_actors + self.filter_text_current
            self.filter_text_current = self.filter_text_external_objects + self.filter_text_current
        self.__process_filter_text__()
        log.trace(f"Filter: {self.filter_text_current}")
        dpg.set_value(self.checked_out_files_table_tag, self.filter_text_current)

    def __process_filter_folders__(self, sender, folder_text_to_filter):
        is_checked = dpg.get_value(sender)
        self.filter_text_current = self.filter_text_current.replace(folder_text_to_filter, "")
        if is_checked:
            self.filter_text_current = folder_text_to_filter + self.filter_text_current
        self.__process_filter_text__()
        log.trace(f"Filter: {self.filter_text_current}")
        dpg.set_value(self.checked_out_files_table_tag, self.filter_text_current)

    def __callback_hide_binaries__(self, sender, app_data, user_data):
        self.__process_filter_folders__(sender, self.filter_text_binaries)

    def __callback_hide_source__(self, sender, app_data, user_data):
        self.__process_filter_folders__(sender, self.filter_text_source)

    def __callback_hide_config__(self, sender, app_data, user_data):
        self.__process_filter_folders__(sender, self.filter_text_config)

    def __callback_hide_content__(self, sender, app_data, user_data):
        is_content_hidden = dpg.get_value(sender)
        dpg.configure_item(self.hide_external_id, show=not is_content_hidden)
        self.__process_filter_folders__(sender, self.filter_text_content)

    def __callback_hide_plugins__(self, sender, app_data, user_data):
        self.__process_filter_folders__(sender, self.filter_text_plugins)

    def __callback_show_all_files__(self, sender, app_data, user_data):
        dpg.configure_item(self.filter_group_tag, show=False)
        is_show_all_files_checked = dpg.get_value(sender)
        dpg.configure_item(self.hide_filter_group_tag, show=not is_show_all_files_checked)
        if is_show_all_files_checked:
            filter_ui_text = dpg.get_value(self.filter_id)
            if filter_ui_text != "":
                filter_ui_text = filter_ui_text + ","
            self.filter_text_current = self.filter_text_current.removesuffix(filter_ui_text)
            self.filter_text_cache = self.filter_text_current
            self.filter_text_current = ""
            dpg.set_value(self.filter_id, self.filter_text_current)
            log.trace(f"Filter: {self.filter_text_current}")
            dpg.set_value(self.checked_out_files_table_tag, self.filter_text_current)
        else:
            self.__process_filter_text__()
            dpg.set_value(self.filter_id, "")
            self.filter_text_current = self.filter_text_cache
            log.trace(f"Filter: {self.filter_text_current}")
            dpg.set_value(self.checked_out_files_table_tag, self.filter_text_current)
        dpg.configure_item(self.filter_group_tag, show=True)

    def __callback_on_refresh__(self):
        dpg.configure_item(self.refresh_button_tag, show=False)
        self.checked_out_files.clear()
        dpg.delete_item(self.table_id)
        self.checked_out_files = self.controller.get_checked_out_files()
        self.last_refresh_time_text = self.controller.get_last_refresh_time_text()
        dpg.configure_item(self.last_refresh_time_text_tag, default_value=self.last_refresh_time_text)
        self.__update_table__()
        self.__callback_hide_external__(self.hide_external_id, None, None)
        self.__callback_hide_binaries__(self.hide_binaries_id, None, None)
        self.__callback_hide_source__(self.hide_source_id, None, None)
        self.__callback_hide_config__(self.hide_config_id, None, None)
        self.__callback_hide_content__(self.hide_content_id, None, None)
        self.__callback_hide_plugins__(self.hide_plugins_id, None, None)
        dpg.configure_item(self.refresh_group_tag, show=True)
        dpg.configure_item(self.filter_group_tag, show=True)
        dpg.configure_item(self.show_all_id, show=True)
        dpg.configure_item(self.hide_filter_group_tag, show=True)
        dpg.configure_item(self.filter_id, show=True)
        dpg.configure_item(self.table_id, show=True)
        dpg.configure_item(self.refresh_button_tag, show=True)
