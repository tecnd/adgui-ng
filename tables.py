import dearpygui.dearpygui as dpg

ROWS = 10
COLS = 10

mouse_pos = (0,0)
mouse_clicked_pos = (0,0) # Global to keep track of initial mouse click

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
    Unselects all Selectables.
    '''
    for item in dpg.get_all_items():
        if dpg.get_item_type(item) == 'mvAppItemType::mvSelectable':
            dpg.set_value(item, False)

def get_mouse(sender, app_data):
    '''
    Mouse click handler. When mouse is clicked, triggers once. Stores mouse position in global
    variable and unselects all Selectables.

    Note: Does not work with left-mouse drag, since that disables hover.
    '''
    if app_data[0] == 1: # If right-mouse click
        global mouse_clicked_pos
        mouse_clicked_pos = dpg.get_item_user_data(app_data[1])
    # Clear selection on any mouse click
    clear_selection()

def update_mouse(sender, app_data):
    '''
    Mouse hover handler. Continuously triggers when mouse is hovering over a cell. Retrieves the
    cell coordinates from user_data and updates the global variable.
    '''
    global mouse_pos
    mouse_pos = dpg.get_item_user_data(app_data)
    # print(mouse_pos)

def select_cell(sender, app_data):
    '''
    Mouse drag handler. Continually triggers as long as mouse button is held. Creates rectangle
    between initial and current coordinates. Any Selectable whose coordinate is inside
    the rectangle is selected, otherwise not selected.
    '''
    global mouse_clicked_pos
    global mouse_pos
    # Create rectangle object
    drag_box = Rectangle(mouse_clicked_pos[0], mouse_pos[0], mouse_clicked_pos[1], mouse_pos[1])
    print(drag_box)
    items = dpg.get_all_items()
    for item in items:
        if dpg.get_item_type(item) == 'mvAppItemType::mvSelectable':
            if drag_box.contains(dpg.get_item_user_data(item)):
                dpg.set_value(item, True)
            else:
                dpg.set_value(item, False)

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
                   borders_outerV=True, policy=dpg.mvTable_SizingStretchProp):
        for i in range(COLS):
            dpg.add_table_column()
        for i in range(ROWS):
            with dpg.table_row():
                for j in range(COLS):
                    dpg.add_selectable(label=f"Cell", user_data=(i, j)) # Add cell coordinates to user_data of each cell
                    dpg.bind_item_handler_registry(dpg.last_item(), cell_handler)

# dpg.show_item_registry()

dpg.create_viewport(title='Drag demo')
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window(primary, True)
dpg.start_dearpygui()
dpg.destroy_context()