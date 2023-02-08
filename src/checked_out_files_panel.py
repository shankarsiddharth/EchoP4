import json

import dearpygui.dearpygui as dpg
import p4_tools_helper as p4th
from app_error import AppError


class CheckedOutFilesPanel:

    def __init__(self, parent=None, is_open=True):

        self.window_id = None
        self.uid_column = None
        self.name_column = None

        self.window_tag = "Checked Out Files"

    def init_ui(self, parent=None, is_open=True):
        if parent:
            self.window_id = parent
            # self.window_id = dpg.add_collapsing_header(label="Logger", tag="Logger", default_open=is_open, parent=parent)
        else:
            self.window_id = dpg.add_window(label=self.window_tag, tag=self.window_tag, no_title_bar=False, no_close=True)
            # self.window_id = dpg.add_collapsing_header(label="Logger", tag="Logger", default_open=is_open)

        # with dpg.add_collapsing_header(label="Logger", default_open=True, parent=self.window_id):
        with dpg.table(parent=self.window_id, header_row=True, policy=dpg.mvTable_SizingFixedFit,
                       borders_innerH=True, borders_outerH=True,
                       borders_innerV=True, borders_outerV=True,
                       row_background=True, sortable=True, resizable=True, reorderable=False, no_host_extendX=True,
                       # callback=lambda sender, app_data, user_data: self.sort_callback(sender, None)):
                       callback=self.sort_callback):

            self.uid_column = dpg.add_table_column(label="uID", default_sort=True, prefer_sort_ascending=True, width_fixed=True, no_clip=True)
            self.name_column = dpg.add_table_column(label="Name", default_sort=True, prefer_sort_ascending=True, no_clip=True)

            for i in range(25):
                with dpg.table_row():
                    dpg.add_input_int(label=" ", step=0, default_value=i)
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

            if sort_specs[0][0] == self.uid_column:
                first_cell = dpg.get_item_children(row, 1)[0]
            elif sort_specs[0][0] == self.name_column:
                first_cell = dpg.get_item_children(row, 1)[1]

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
