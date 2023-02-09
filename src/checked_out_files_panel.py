import json
import logging
import os
import re

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
        pass

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
            p4.run_login()

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
        except BaseException as e:
            log.exception(e)
        finally:
            if p4.connected():
                p4.disconnect()

        return self.checked_out_files


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
        self.checked_out_files_table_tag = None
        self._filter_text_tag = "Checked Out Filter Text Box"

        self.checked_out_files = dict()
        self.checked_out_files = self.controller.get_checked_out_files()

    def init_ui(self, parent=None, is_open=True):
        if parent:
            self.window_id = parent
        else:
            self.window_id = dpg.add_window(label=self.window_tag, tag=self.window_tag, no_title_bar=False, no_close=True)

        self.checked_out_files_table_tag = dpg.generate_uuid()
        self.filter_id = dpg.add_input_text(parent=self.window_id, label="Filter (inc, -exc)", user_data=self.checked_out_files_table_tag,
                                            callback=lambda s, a, u: dpg.set_value(u, dpg.get_value(s)))

        with dpg.group(horizontal=True, parent=self.window_id, before=self.filter_id):
            dpg.add_button(label="Refresh", callback=lambda: dpg.delete_item(self.table_id, children_only=True))

        with dpg.table(parent=self.window_id, tag=self.checked_out_files_table_tag,
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

    def __callback_on_filter_text_changed(self, sender):
        pass
