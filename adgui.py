import dearpygui.dearpygui as dpg
# Constants
NUMBER_OF_PAGES = 13
NUM_ANALOG_CHANNELS = 40
NUM_DIGITAL_CHANNELS = 64
NUM_COLUMNS = 20
TABLE_POLICY_PROP = {
                    'header_row' : False,
                    'borders_innerH' : True,
                    'borders_outerH' : True,
                    'borders_innerV' : True,
                    'borders_outerV' : True,
                    'policy' : dpg.mvTable_SizingStretchProp
                    }
TABLE_POLICY_SAME = {
                    'header_row' : False,
                    'borders_innerH' : True,
                    'borders_outerH' : True,
                    'borders_innerV' : True,
                    'borders_outerV' : True,
                    'policy' : dpg.mvTable_SizingStretchSame
                    }

# Internal data stored as lists                    
layout = dict()
pages = [f'Page {i}' for i in range(NUMBER_OF_PAGES)]
units = ['Unit'] * NUM_ANALOG_CHANNELS
analog_channel_names = [('Name', i) for i in range(NUM_ANALOG_CHANNELS)]

def layout_windows():
    '''
    Moves the windows into default positions. Should be called after first full frame
    is rendered, as item dimensions may not be computed before rendering. For some
    reason the menu bar takes up the first frame, so technically should be called
    after the second frame.
    '''
    if 'page_selector_y' not in layout:
        layout['page_selector_y'] = dpg.get_item_height('menubar')
    if 'page_selector_width' not in layout:
        layout['page_selector_width'] = dpg.get_item_width('page_selector')
    if 'page_selector_height' not in layout:
        layout['page_selector_height'] = dpg.get_item_height('page_selector')
    dpg.configure_item('page_selector', pos=(0, layout['page_selector_y']),
        height=layout['page_selector_height'], width=layout['page_selector_width'], collapsed=False)
    if 'tables_y' not in layout:
        layout['tables_y'] = layout['page_selector_y'] + \
            layout['page_selector_height']
    if 'tables_width' not in layout:
        layout['tables_width'] = dpg.get_item_width('tables')
    if 'tables_height' not in layout:
        layout['tables_height'] = dpg.get_item_height('tables')
    dpg.configure_item('tables', pos=(0, layout['tables_y']),
        height=layout['tables_height'], width=layout['tables_width'], collapsed=False)


def rename_callback(selector, app_data, user_data):
    '''
    Callback for renaming units and pages. Parses object name and updates
    the internal lists accordingly.
    '''
    input, parent, popup = user_data
    # Update internal data arrays
    args = str(parent).split(';')
    if len(args) > 1:
        if args[0] == 'unit':
            units[int(args[1])] = str(dpg.get_value(input))
        elif args[0] == 'page':
            pages[int(args[1])] = str(dpg.get_value(input))
    dpg.configure_item(parent, label=dpg.get_value(input))
    dpg.configure_item(popup, show=False)

def configure_channel(selector, app_data, user_data):
    name, channel, new_name, new_channel, popup = user_data
    new_name = str(dpg.get_value(new_name))
    new_channel = int(dpg.get_value(new_channel))
    args = str(name).split(';')
    if len(args) > 1:
        if args[0] == 'analog_channel':
            analog_channel_names[int(args[1])] = (new_name, new_channel)
    dpg.configure_item(name, label=new_name)
    dpg.configure_item(channel, label=new_channel)
    dpg.configure_item(popup, show=False)

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=1080, height=2560)

with dpg.viewport_menu_bar(tag='menubar'):
    with dpg.menu(label='File'):
        dpg.add_selectable(label='Exit')
    with dpg.menu(label='View'):
        dpg.add_selectable(label='Reset view', callback=layout_windows)

with dpg.window(tag='page_selector', label='Page Selector', no_close=True, width=dpg.get_viewport_width()):
    with dpg.group(horizontal=True):
        with dpg.group():
            dpg.add_button(label='Run Cycle', callback=lambda: print(analog_channel_names))
            dpg.add_button(label='Stop')
            dpg.add_button(label='Scan')
            dpg.add_checkbox(label='Repeat')
        with dpg.group(horizontal=True):
            for i in range(NUMBER_OF_PAGES):
                dpg.add_checkbox(label=f'Page {i}')

with dpg.window(tag='tables', label='Tables', no_close=True, width=dpg.get_viewport_width()):
    with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchProp):
        dpg.add_table_column()
        dpg.add_table_column()
        dpg.add_table_column()
        with dpg.table_row():
            # Left bar, includes the channel names and numbers
            with dpg.group(width=150):
                dpg.add_spacer(height=57)
                dpg.add_text('Analog Channels | Line')
                with dpg.table(**TABLE_POLICY_PROP):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    for row in range(NUM_ANALOG_CHANNELS):
                        with dpg.table_row():
                            name = dpg.add_selectable(label='Name', tag=f'analog_channel;{row}', span_columns=True)
                            channel = dpg.add_selectable(label=f'{row + 1}')
                            with dpg.popup(name) as popup:
                                new_name = dpg.add_input_text(width=75, hint='Name')
                                new_channel = dpg.add_input_int(width=75, default_value=row+1, step=0, min_value=1, max_value=132, min_clamped=True, max_clamped=True)
                                dpg.add_button(label='Rename', user_data=(name, channel, new_name, new_channel, popup), callback=configure_channel)
                dpg.add_text('Digital Channels | Line')
                with dpg.table(**TABLE_POLICY_PROP):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    for row in range(NUM_DIGITAL_CHANNELS):
                        with dpg.table_row():
                            dpg.add_selectable(label='Name', span_columns=True)
                            dpg.add_selectable(label=f'{row + 1}')
            # Center bar, includes the main tables
            with dpg.tab_bar():
                for i in range(NUMBER_OF_PAGES):
                    with dpg.tab(label=f'Page {i}', tag=f'page;{i}') as tab:
                        with dpg.popup(tab) as popup:
                            dpg.add_input_text(width=75, hint=f'Page {i}')
                            dpg.add_button(label='Rename', user_data=(dpg.last_item(), tab, popup), callback=rename_callback)
                        with dpg.table(**TABLE_POLICY_SAME):
                            for col in range(NUM_COLUMNS):
                                dpg.add_table_column()
                            with dpg.table_row():
                                for col in range(NUM_COLUMNS):
                                    dpg.add_selectable(label="Label")
                            with dpg.table_row():
                                for col in range(NUM_COLUMNS):
                                    dpg.add_selectable(label="Time")
                        dpg.add_text('Analog Table')
                        with dpg.table(**TABLE_POLICY_SAME):
                            for col in range(NUM_COLUMNS):
                                dpg.add_table_column()
                            for row in range(NUM_ANALOG_CHANNELS):
                                with dpg.table_row():
                                    for col in range(NUM_COLUMNS):
                                        dpg.add_selectable(label="Cell")
                        dpg.add_text('Digital Table')
                        with dpg.table(**TABLE_POLICY_SAME):
                            for col in range(NUM_COLUMNS):
                                dpg.add_table_column()
                            for row in range(NUM_DIGITAL_CHANNELS):
                                with dpg.table_row():
                                    for col in range(NUM_COLUMNS):
                                        dpg.add_selectable(label="Cell")
            # Right bar, includes the analog units and scan values
            with dpg.group(width=100):
                dpg.add_spacer(height=57)
                dpg.add_text('Analog Units')
                with dpg.table(**TABLE_POLICY_PROP):
                    dpg.add_table_column()
                    for row in range(NUM_ANALOG_CHANNELS):
                        with dpg.table_row():
                            parent = dpg.add_selectable(label='Unit', tag=f'unit;{row}', callback=lambda s: dpg.set_value(s, False))
                            with dpg.popup(parent) as popup:
                                dpg.add_input_text(width=75, hint='Unit')
                                dpg.add_button(label='Rename', user_data=(dpg.last_item(), parent, popup), callback=rename_callback)
                dpg.add_text('Scan Values')
                with dpg.table(**TABLE_POLICY_PROP):
                    dpg.add_table_column()
                    for row in range(32):
                        with dpg.table_row():
                            dpg.add_selectable(label='Scan')

dpg.setup_dearpygui()
dpg.show_viewport()

menubar = True
first = True
while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()
    if menubar:
        menubar = False  # menubar takes up first frame of rendering
    elif first:
        layout_windows()  # window positions are not calculated until first full frame is rendered
        first = False
dpg.destroy_context()
