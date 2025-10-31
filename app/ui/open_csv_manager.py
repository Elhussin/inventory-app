

import ui.inventory_csv_manager 

def open_csv_manager(root, load_data_func, tree, search_term, stat_vars):
    """Opens the CSV Manager as a child window and reloads data upon closing/completion."""

    #    1. define the callback function
    def reload_main_data():
        load_data_func(tree, search_term, stat_vars)
        
    # 2. pass the parent window and callback function to the child window
    ui.inventory_csv_manager.open_csv_manager(
        parent=root, 
        reload_callback=reload_main_data 
    )
    

