import dearpygui.dearpygui as dpg

ROWS = 10
COLS = 10

mouse_pos = (0,0)
mouse_clicked_pos = (0,0)

dpg.create_context()

class Rectangle(object):
    '''
    Rectangle class. Automatically sorts corners in correct order and provides function
    to check if a point is inside the rectangle.
    '''
    def __init__(self, x0, x1, y0, y1):
        # Sort corners in increasing order
        if x0 < x1:
            self.x0 = x0
            self.x1 = x1
        else:
            self.x0 = x1
            self.x1 = x0
        if y0 < y1:
            self.y0 = y0
            self.y1 = y1
        else:
            self.y0 = y1
            self.y1 = y0
    
    def contains(self, pos:list) -> bool:
        '''
        Takes in a point and checks if it is in the rectangle.
        '''
        return self.x0 <= pos[0] <= self.x1 and self.y0 <= pos[1] <= self.y1

    def __str__(self) -> str:
        return str([self.x0, self.x1, self.y0, self.y1])

def clear_selection():
    '''
    Unhighlights all cells in tables.
    '''
    for item in dpg.get_all_items():
        if dpg.get_item_type(item) == 'mvAppItemType::mvTable':
            for row in range(ROWS):
                for col in range(COLS):
                    dpg.unhighlight_table_cell(item, row, col)

def get_mouse(sender, app_data):
    '''
    Mouse click handler. When mouse is clicked, triggers once. Sets the cell's table as the active table.
    Stores mouse position in global variable and unhighlights all cells in the active table.
    '''
    print(dpg.is_mouse_button_double_clicked(dpg.mvMouseButton_Left))
    # On click, set that table as active table
    global active_table
    active_table = dpg.get_item_user_data(app_data[1])[2]
    if app_data[0] == 1: # If right-mouse click
        global mouse_clicked_pos
        mouse_clicked_pos = dpg.get_item_user_data(app_data[1])
    elif app_data[0] == 0: # Clear selection on left-mouse click
        clear_selection()

def update_mouse(sender, app_data):
    '''
    Mouse hover handler. Continuously triggers when mouse is hovering over a cell. Retrieves the
    cell coordinates from user_data and updates the global variable if cell is in active table.
    '''
    # Check if cell belongs to active table
    if dpg.get_item_user_data(app_data)[2] == active_table:
        global mouse_pos
        mouse_pos = dpg.get_item_user_data(app_data)

def select_cell(sender, app_data):
    '''
    Mouse drag handler. Continually triggers as long as mouse button is held. Creates rectangle
    between initial and current coordinates. Any cell whose coordinate is inside the rectangle
    is highlighted, otherwise unhighlighted.

    Note: Does not work for left-mouse drag, since that disables hover.
    '''
    global mouse_clicked_pos
    global mouse_pos
    # Create rectangle object
    drag_box = Rectangle(mouse_clicked_pos[0], mouse_pos[0], mouse_clicked_pos[1], mouse_pos[1])
    for row in dpg.get_item_children(active_table, 1):
        for item in dpg.get_item_children(row, 1):
            if dpg.get_item_type(item) == 'mvAppItemType::mvSelectable':
                cell_pos = dpg.get_item_user_data(item)
                if drag_box.contains(cell_pos):
                    dpg.highlight_table_cell(active_table, cell_pos[0], cell_pos[1], dpg.mvThemeCol_ButtonHovered)
                else:
                    dpg.unhighlight_table_cell(active_table, cell_pos[0], cell_pos[1])

# Cell handler registry
with dpg.item_handler_registry() as cell_handler:
    dpg.add_item_hover_handler(callback=update_mouse)
    dpg.add_item_clicked_handler(callback=get_mouse)

# Global handler registry
with dpg.handler_registry():
    dpg.add_mouse_drag_handler(button=1, callback=select_cell) # Watch for right-mouse drag
    dpg.add_key_press_handler(key=dpg.mvKey_Escape, callback=clear_selection) # Also clear selection on ESC key

with dpg.window() as primary:
    # Create table
    with dpg.table(header_row=False, borders_innerH=True, borders_outerH=True, borders_innerV=True,
                   borders_outerV=True, policy=dpg.mvTable_SizingStretchProp) as table1:
        for i in range(COLS):
            dpg.add_table_column()
        for i in range(ROWS):
            with dpg.table_row():
                for j in range(COLS):
                    # Add cell coordinates and parent table to user_data of each cell
                    dpg.add_selectable(label="Cell", user_data=(i, j, table1),
                                       callback=lambda s: dpg.set_value(s, False))
                    dpg.bind_item_handler_registry(dpg.last_item(), cell_handler)
    # Create second table
    with dpg.table(header_row=False, borders_innerH=True, borders_outerH=True, borders_innerV=True,
                   borders_outerV=True, policy=dpg.mvTable_SizingStretchProp) as table2:
        for i in range(COLS):
            dpg.add_table_column()
        for i in range(ROWS):
            with dpg.table_row():
                for j in range(COLS):
                    dpg.add_selectable(label="Cell", user_data=(i, j, table2),
                                       callback=lambda s: dpg.set_value(s, False))
                    dpg.bind_item_handler_registry(dpg.last_item(), cell_handler)

active_table = table1 # Global to keep track of which table is active

dpg.show_item_registry()

dpg.create_viewport(title='Drag demo')
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window(primary, True)
dpg.start_dearpygui()
dpg.destroy_context()