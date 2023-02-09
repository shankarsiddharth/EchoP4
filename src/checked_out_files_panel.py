import json

import dearpygui.dearpygui as dpg
import p4_tools_helper as p4th
from app_error import AppError


class CheckedOutFilesPanelController:

    def __init__(self):
        pass

    def get_checked_out_files(self):
        pass


class CheckedOutFilesPanel:
    def __init__(self, parent=None, is_open=True):

        self.controller: CheckedOutFilesPanelController = CheckedOutFilesPanelController()

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
        for i in range(10):
            self.checked_out_files[i] = i

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

            for i, j in self.checked_out_files.items():
                with dpg.table_row(filter_key=f"Cell {i}, 1"):
                    dpg.add_text(f"Cell {i}, 1")
                    dpg.add_text(f"Cell {i}, 1")
                    dpg.add_text(f"Cell {i}, 1")
                    dpg.add_text(f"Cell {i}, 1")
                    dpg.add_text(f"Cell {i}, 1")

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
