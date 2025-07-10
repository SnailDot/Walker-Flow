import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import sys
import subprocess
import urllib.request
import webbrowser

sys.path.append(os.path.join(os.path.dirname(__file__), 'Backend', 'Tools'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'Backend', 'Tools', 'CourseInjector'))
from bin_to_img_enhanced import convert_bin_to_image, convert_image_to_bin

from main import PokeWalkerSlot, PokeWalkerItem, PokeWalkerCourse
from pokemonenums import RouteImage, Species, Move, Gender, Type, ITEMS

Version = "v1.0"

class WalkerFlowApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WalkerFlow")
        self.root.geometry("400x350")
        self.root.resizable(True, True)
        
        self.current_view = "main"
        self.selected_file_path = None
        
        self.route_data = {
            'pokemon_groups': {
                'A': [],
                'B': [],
                'C': []
            },
            'items': [],
            'route_info': {
                'image': RouteImage.FIELD,
                'watt_requirement': 0
            },
            'special_types': [Type.NORMAL, Type.NORMAL, Type.NORMAL]
        }
        
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        
        self.show_main_menu()
        
    def clear_frame(self):
        if hasattr(self, 'notebook'):
            self.notebook = None
        
        self.clear_string_vars()
        
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        self.main_frame.rowconfigure(2, weight=0)
        self.main_frame.columnconfigure(0, weight=1)
    
    def clear_string_vars(self):
        string_vars = [
            'pokemon_species_var', 'level_var', 'item_var', 'form_var', 'gender_var',
            'move1_var', 'move2_var', 'move3_var', 'move4_var', 'step_req_var', 'spawn_chance_var',
            'item_name_var', 'item_step_req_var', 'item_spawn_chance_var',
            'route_image_var', 'watt_requirement_var'
        ]
        
        for var_name in string_vars:
            if hasattr(self, var_name):
                var = getattr(self, var_name)
                if hasattr(var, 'set'):
                    var.set('')
                delattr(self, var_name)
    
    def show_main_menu(self):
        self.current_view = "main"
        self.clear_frame()
        
        title_label = ttk.Label(self.main_frame, text="WalkerFlow", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        subtitle_label = ttk.Label(self.main_frame, text="The Easiest Way To Handle Pokewalker Tasks", 
                                  font=("Arial", 10), foreground="gray")
        subtitle_label.grid(row=1, column=0, pady=(0, 20))
        
        convert_sprite_btn = ttk.Button(self.main_frame, text="Convert Sprite", 
                                       command=self.show_sprite_menu, width=30)
        convert_sprite_btn.grid(row=2, column=0, pady=5)
        
        action_replay_btn = ttk.Button(self.main_frame, text="Action Replay Codes", 
                                      command=self.show_action_replay_menu, width=30)
        action_replay_btn.grid(row=3, column=0, pady=5)
        
        help_btn = ttk.Button(self.main_frame, text="Help/Guide", 
                             command=self.open_help_guide, width=30)
        help_btn.grid(row=4, column=0, pady=5)
        
        info_btn = ttk.Button(self.main_frame, text="Check For Update", 
                             command=self.check_for_update, width=30)
        info_btn.grid(row=5, column=0, pady=5)
    
    def check_for_update(self):
        try:
            url = "https://raw.githubusercontent.com/SnailDot/Walker-Flow/main/UpdateCheck.txt"
            
            req = urllib.request.Request(url)
            req.add_header('Cache-Control', 'no-cache')
            req.add_header('Pragma', 'no-cache')
            
            with urllib.request.urlopen(req) as response:
                latest_version = response.read().decode('utf-8').strip()
            
            if latest_version != Version:
                self.show_update_available_dialog(latest_version)
            else:
                self.show_up_to_date_dialog()
                
        except Exception as e:
            messagebox.showerror("Update Check Failed", 
                               f"Unable to check for updates.\nError: {str(e)}")
    
    def show_update_available_dialog(self, latest_version):
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Available")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (dialog.winfo_screenheight() // 2) - (150 // 2)
        dialog.geometry(f"300x150+{x}+{y}")
        
        message_label = ttk.Label(dialog, 
                                 text=f"A new version is available!\n\nCurrent: {Version}\nLatest: {latest_version}",
                                 justify="center")
        message_label.pack(pady=20)
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        get_version_btn = ttk.Button(button_frame, text="Get New Version", 
                                   command=lambda: self.open_download_page(dialog))
        get_version_btn.pack(side="left", padx=5)
        
        close_btn = ttk.Button(button_frame, text="Close", 
                             command=dialog.destroy)
        close_btn.pack(side="left", padx=5)
    
    def show_up_to_date_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Up to Date")
        dialog.geometry("250x120")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250 // 2)
        y = (dialog.winfo_screenheight() // 2) - (120 // 2)
        dialog.geometry(f"250x120+{x}+{y}")
        
        message_label = ttk.Label(dialog, 
                                 text=f"You have the latest version!\n\nCurrent: {Version}",
                                 justify="center")
        message_label.pack(pady=20)
        
        close_btn = ttk.Button(dialog, text="Close", command=dialog.destroy)
        close_btn.pack(pady=10)
    
    def open_download_page(self, dialog):
        webbrowser.open("https://github.com/SnailDot/Walker-Flow")
        dialog.destroy()
    
    def open_help_guide(self):
        webbrowser.open("https://github.com/SnailDot/Walker-Flow/wiki")
    
    def show_sprite_menu(self):
        self.current_view = "sprite"
        self.clear_frame()
        
        back_btn = ttk.Button(self.main_frame, text="Back", 
                             command=self.show_main_menu, width=10)
        back_btn.grid(row=0, column=1, sticky="e", padx=(0, 10))
        
        title_label = ttk.Label(self.main_frame, text="Sprite Conversion", font=("Arial", 14, "bold"))
        title_label.grid(row=1, column=0, columnspan=2, pady=(20, 10))
        
        info_label = ttk.Label(self.main_frame, 
                              text="The Easiest Way To Handle Pokewalker Tasks", 
                              font=("Arial", 9), foreground="gray", justify="center")
        info_label.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        # Buttons
        convert_main_btn = ttk.Button(self.main_frame, text="Convert Main Sprite", 
                                     command=self.select_main_sprite_file, width=30)
        convert_main_btn.grid(row=3, column=0, columnspan=2, pady=5)
        
        convert_route_btn = ttk.Button(self.main_frame, text="Convert Route Sprite", 
                                     command=self.select_route_sprite_file, width=30)
        convert_route_btn.grid(row=4, column=0, columnspan=2, pady=5)
    
    def show_action_replay_menu(self):
        self.current_view = "action_replay"
        self.clear_frame()
        
        back_btn = ttk.Button(self.main_frame, text="Back", 
                             command=self.show_main_menu, width=10)
        back_btn.grid(row=0, column=1, sticky="e", padx=(0, 10))
        
        title_label = ttk.Label(self.main_frame, text="Action Replay Codes", font=("Arial", 14, "bold"))
        title_label.grid(row=1, column=0, columnspan=2, pady=(20, 10))
        
        info_label = ttk.Label(self.main_frame, 
                              text="Generate and manage Action Replay codes\nfor Pokéwalker functionality", 
                              font=("Arial", 9), foreground="gray", justify="center")
        info_label.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        custom_route_btn = ttk.Button(self.main_frame, text="Custom Route Code", 
                                     command=self.show_custom_route_warning, width=30)
        custom_route_btn.grid(row=3, column=0, columnspan=2, pady=5)
    
    def show_custom_route_warning(self):
        messagebox.showinfo("Custom Route Code", 
                           "Currently Walker Flow's custom route code system only works for USA Heart Gold copies. "
                           "Full support will be added once I get done figuring out the codes for each region and soul silver")
        
        self.show_custom_route_code()
    
    def show_custom_route_code(self):
        self.current_view = "custom_route_code"
        self.clear_frame()
        
        back_btn = ttk.Button(self.main_frame, text="Back", 
                             command=self.back_from_custom_route, width=10)
        back_btn.grid(row=0, column=1, sticky="e", padx=(0, 10))
        
        title_label = ttk.Label(self.main_frame, text="Custom Route Code", font=("Arial", 14, "bold"))
        title_label.grid(row=1, column=0, columnspan=2, pady=(20, 10))
        
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        
        self.create_route_pokemon_tab()
        self.create_route_items_tab()
        self.create_route_info_tab()
        self.create_route_groups_tab()
        self.create_export_route_tab()
    
    def create_route_pokemon_tab(self):
        """Create the Route Pokemon tab"""
        pokemon_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(pokemon_frame, text="Route Pokemon")
        
        # Configure grid weights
        pokemon_frame.columnconfigure(1, weight=1)
        
        # Pokemon Species (dropdown)
        ttk.Label(pokemon_frame, text="Pokemon Species:").grid(row=0, column=0, sticky="w", pady=2)
        self.pokemon_species_var = tk.StringVar(value="MEWTWO")
        # Create list of species names for dropdown
        species_names = [species.name for species in Species]
        pokemon_species_combo = ttk.Combobox(pokemon_frame, textvariable=self.pokemon_species_var,
                                            values=species_names, state="readonly", width=17)
        pokemon_species_combo.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Level
        ttk.Label(pokemon_frame, text="Level:").grid(row=1, column=0, sticky="w", pady=2)
        self.level_var = tk.StringVar(value="100")
        level_entry = ttk.Entry(pokemon_frame, textvariable=self.level_var, width=20)
        level_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Item
        ttk.Label(pokemon_frame, text="Item:").grid(row=2, column=0, sticky="w", pady=2)
        self.item_var = tk.StringVar(value="None")
        # ITEMS is already a list, no need to split
        item_combo = ttk.Combobox(pokemon_frame, textvariable=self.item_var,
                                 values=ITEMS, state="readonly", width=17)
        item_combo.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Form
        ttk.Label(pokemon_frame, text="Form:").grid(row=3, column=0, sticky="w", pady=2)
        self.form_var = tk.StringVar(value="0")
        form_entry = ttk.Entry(pokemon_frame, textvariable=self.form_var, width=20)
        form_entry.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Gender
        ttk.Label(pokemon_frame, text="Gender:").grid(row=4, column=0, sticky="w", pady=2)
        self.gender_var = tk.StringVar(value="MALE")
        gender_combo = ttk.Combobox(pokemon_frame, textvariable=self.gender_var, 
                                   values=["MALE", "FEMALE", "GENDERLESS"], state="readonly", width=17)
        gender_combo.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Move 1
        ttk.Label(pokemon_frame, text="Move 1:").grid(row=5, column=0, sticky="w", pady=2)
        self.move1_var = tk.StringVar(value="NONE")
        move1_combo = ttk.Combobox(pokemon_frame, textvariable=self.move1_var,
                                  values=[move.name for move in Move], state="readonly", width=17)
        move1_combo.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Move 2
        ttk.Label(pokemon_frame, text="Move 2:").grid(row=6, column=0, sticky="w", pady=2)
        self.move2_var = tk.StringVar(value="NONE")
        move2_combo = ttk.Combobox(pokemon_frame, textvariable=self.move2_var,
                                  values=[move.name for move in Move], state="readonly", width=17)
        move2_combo.grid(row=6, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Move 3
        ttk.Label(pokemon_frame, text="Move 3:").grid(row=7, column=0, sticky="w", pady=2)
        self.move3_var = tk.StringVar(value="NONE")
        move3_combo = ttk.Combobox(pokemon_frame, textvariable=self.move3_var,
                                  values=[move.name for move in Move], state="readonly", width=17)
        move3_combo.grid(row=7, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Move 4
        ttk.Label(pokemon_frame, text="Move 4:").grid(row=8, column=0, sticky="w", pady=2)
        self.move4_var = tk.StringVar(value="NONE")
        move4_combo = ttk.Combobox(pokemon_frame, textvariable=self.move4_var,
                                  values=[move.name for move in Move], state="readonly", width=17)
        move4_combo.grid(row=8, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Step Requirement
        ttk.Label(pokemon_frame, text="Step Requirement:").grid(row=9, column=0, sticky="w", pady=2)
        self.step_req_var = tk.StringVar()
        step_req_entry = ttk.Entry(pokemon_frame, textvariable=self.step_req_var, width=20)
        step_req_entry.grid(row=9, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Spawn Chance
        ttk.Label(pokemon_frame, text="Spawn Chance:").grid(row=10, column=0, sticky="w", pady=2)
        self.spawn_chance_var = tk.StringVar()
        spawn_chance_entry = ttk.Entry(pokemon_frame, textvariable=self.spawn_chance_var, width=20)
        spawn_chance_entry.grid(row=10, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Buttons frame
        buttons_frame = ttk.Frame(pokemon_frame)
        buttons_frame.grid(row=11, column=0, columnspan=2, pady=(20, 0))
        
        # Add to group buttons
        add_group_a_btn = ttk.Button(buttons_frame, text="Add to Group A", 
                                    command=self.add_to_group_a, width=15)
        add_group_a_btn.grid(row=0, column=0, padx=5)
        
        add_group_b_btn = ttk.Button(buttons_frame, text="Add to Group B", 
                                    command=self.add_to_group_b, width=15)
        add_group_b_btn.grid(row=0, column=1, padx=5)
        
        add_group_c_btn = ttk.Button(buttons_frame, text="Add to Group C", 
                                    command=self.add_to_group_c, width=15)
        add_group_c_btn.grid(row=0, column=2, padx=5)
    
    def create_route_items_tab(self):
        """Create the Route Items tab"""
        items_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(items_frame, text="Route Items")
        
        # Configure grid weights
        items_frame.columnconfigure(1, weight=1)
        
        # Item Name
        ttk.Label(items_frame, text="Item Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.item_name_var = tk.StringVar(value="None")
        # ITEMS is already a list, no need to split
        item_name_combo = ttk.Combobox(items_frame, textvariable=self.item_name_var,
                                      values=ITEMS, state="readonly", width=17)
        item_name_combo.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Step Requirements
        ttk.Label(items_frame, text="Step Requirements:").grid(row=1, column=0, sticky="w", pady=2)
        self.item_step_req_var = tk.StringVar(value="0")
        item_step_req_entry = ttk.Entry(items_frame, textvariable=self.item_step_req_var, width=20)
        item_step_req_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Spawn Chance
        ttk.Label(items_frame, text="Spawn Chance:").grid(row=2, column=0, sticky="w", pady=2)
        self.item_spawn_chance_var = tk.StringVar(value="10")
        item_spawn_chance_entry = ttk.Entry(items_frame, textvariable=self.item_spawn_chance_var, width=20)
        item_spawn_chance_entry.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Add Item button
        add_item_btn = ttk.Button(items_frame, text="Add Item to Route", 
                                 command=self.add_item_to_route, width=20)
        add_item_btn.grid(row=3, column=0, columnspan=2, pady=(20, 10))
        
        # Fill All Item Slots button
        fill_all_btn = ttk.Button(items_frame, text="Fill All Item Slots With This Item", 
                                 command=self.fill_all_item_slots, width=30)
        fill_all_btn.grid(row=4, column=0, columnspan=2, pady=(0, 0))
    
    def create_route_info_tab(self):
        """Create the Route Info tab"""
        info_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(info_frame, text="Route Info")
        
        # Configure grid weights
        info_frame.columnconfigure(1, weight=1)
        
        # Route Image
        ttk.Label(info_frame, text="Route Image:").grid(row=0, column=0, sticky="w", pady=2)
        self.route_image_var = tk.StringVar(value="FIELD")
        route_image_combo = ttk.Combobox(info_frame, textvariable=self.route_image_var,
                                        values=[image.name for image in RouteImage], 
                                        state="readonly", width=17)
        route_image_combo.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Watt Requirement
        ttk.Label(info_frame, text="Watt Requirement:").grid(row=1, column=0, sticky="w", pady=2)
        self.watt_requirement_var = tk.StringVar(value="0")
        watt_requirement_entry = ttk.Entry(info_frame, textvariable=self.watt_requirement_var, width=20)
        watt_requirement_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Update Route Info button
        update_info_btn = ttk.Button(info_frame, text="Update Route Info", 
                                   command=self.update_route_info, width=20)
        update_info_btn.grid(row=2, column=0, columnspan=2, pady=(20, 0))
    
    def create_route_groups_tab(self):
        """Create the Route Groups tab"""
        groups_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(groups_frame, text="Route Groups")
        
        # Configure grid weights for horizontal layout
        groups_frame.columnconfigure(0, weight=1)  # Group A
        groups_frame.columnconfigure(1, weight=1)  # Group B
        groups_frame.columnconfigure(2, weight=1)  # Group C
        groups_frame.columnconfigure(3, weight=1)  # Items
        groups_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(groups_frame, text="Current Route Groups", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 10))
        
        # Action buttons frame
        action_frame = ttk.Frame(groups_frame)
        action_frame.grid(row=1, column=0, columnspan=4, pady=(0, 10), sticky="ew")
        
        # Remove button
        self.remove_btn = ttk.Button(action_frame, text="Remove Selected", 
                                   command=self.remove_selected_item, width=15, state="disabled")
        self.remove_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh button
        refresh_btn = ttk.Button(action_frame, text="Refresh Display", 
                               command=self.refresh_groups_display, width=15)
        refresh_btn.pack(side=tk.LEFT)
        
        # Create panels for each group and items
        self.group_a_frame = ttk.LabelFrame(groups_frame, text="Group A", padding="5")
        self.group_a_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.group_b_frame = ttk.LabelFrame(groups_frame, text="Group B", padding="5")
        self.group_b_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.group_c_frame = ttk.LabelFrame(groups_frame, text="Group C", padding="5")
        self.group_c_frame.grid(row=2, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.items_frame = ttk.LabelFrame(groups_frame, text="Route Items", padding="5")
        self.items_frame.grid(row=2, column=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for each panel
        self.group_a_frame.columnconfigure(0, weight=1)
        self.group_b_frame.columnconfigure(0, weight=1)
        self.group_c_frame.columnconfigure(0, weight=1)
        self.items_frame.columnconfigure(0, weight=1)
        
        # Store selected item tracking
        self.selected_item = None
        self.selected_button = None
        
        # Initial display
        self.refresh_groups_display()
    
    def back_from_custom_route(self):
        """Go back from custom route screen and clear all route data"""
        # Reset route data to initial state
        self.route_data = {
            'pokemon_groups': {
                'A': [],
                'B': [],
                'C': []
            },
            'items': [],
            'route_info': {
                'image': RouteImage.FIELD,
                'watt_requirement': 0
            },
            'special_types': [Type.NORMAL, Type.NORMAL, Type.NORMAL]
        }
        
        # Go back to Action Replay menu
        self.show_action_replay_menu()
    
    def refresh_groups_display(self):
        """Refresh the groups display with panel-based interface"""
        # Clear existing content from all panels
        for widget in self.group_a_frame.winfo_children():
            widget.destroy()
        for widget in self.group_b_frame.winfo_children():
            widget.destroy()
        for widget in self.group_c_frame.winfo_children():
            widget.destroy()
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        
        # Reset selection
        self.selected_item = None
        self.selected_button = None
        self.remove_btn.config(state="disabled")
        
        # Display Pokemon Groups in their respective panels
        self.display_group_panel("A", self.group_a_frame)
        self.display_group_panel("B", self.group_b_frame)
        self.display_group_panel("C", self.group_c_frame)
        
        # Display Items in the items panel
        self.display_items_panel()
    
    def display_group_panel(self, group_name, frame):
        """Display a specific group in its panel"""
        pokemon_list = self.route_data['pokemon_groups'][group_name]
        row = 0
        
        # Group count label
        count_label = ttk.Label(frame, text=f"{len(pokemon_list)} Pokemon", 
                               font=("Arial", 9), foreground="gray")
        count_label.grid(row=row, column=0, sticky="w", pady=(0, 5))
        row += 1
        
        if pokemon_list:
            for i, pokemon in enumerate(pokemon_list):
                # Create button text
                button_text = f"{i+1}. {pokemon.species.name} (Lv.{pokemon.level}, {pokemon.gender.name})"
                
                # Create button
                pokemon_btn = tk.Button(frame, text=button_text, 
                                      anchor="w", relief="flat", bd=1,
                                      command=lambda p=pokemon, g=group_name, idx=i, btn=None: 
                                      self.select_item(("pokemon", g, idx), btn))
                
                # Store button reference for later highlighting
                pokemon_btn.configure(command=lambda p=pokemon, g=group_name, idx=i, btn=pokemon_btn: 
                                    self.select_item(("pokemon", g, idx), btn))
                
                pokemon_btn.grid(row=row, column=0, sticky="ew", pady=2)
                row += 1
                
                # Add details label
                details_text = f"   Item: {pokemon.item}, Form: {pokemon.form}"
                details_label = ttk.Label(frame, text=details_text, 
                                        font=("Arial", 7), foreground="gray")
                details_label.grid(row=row, column=0, sticky="w", padx=(10, 0), pady=(0, 1))
                row += 1
                
                moves_text = f"   Moves: {', '.join([move.name for move in pokemon.moves])}"
                moves_label = ttk.Label(frame, text=moves_text, 
                                      font=("Arial", 7), foreground="gray")
                moves_label.grid(row=row, column=0, sticky="w", padx=(10, 0), pady=(0, 1))
                row += 1
                
                stats_text = f"   Step Req: {pokemon.step_requirement}, Rarity: {pokemon.rarity_weight}"
                stats_label = ttk.Label(frame, text=stats_text, 
                                      font=("Arial", 7), foreground="gray")
                stats_label.grid(row=row, column=0, sticky="w", padx=(10, 0), pady=(0, 5))
                row += 1
        else:
            empty_label = ttk.Label(frame, text="(No Pokemon added)", 
                                  font=("Arial", 9), foreground="gray")
            empty_label.grid(row=row, column=0, sticky="w", pady=5)
    
    def display_items_panel(self):
        """Display items in the items panel"""
        items_list = self.route_data['items']
        row = 0
        
        # Items count label
        count_label = ttk.Label(self.items_frame, text=f"{len(items_list)} Items", 
                               font=("Arial", 9), foreground="gray")
        count_label.grid(row=row, column=0, sticky="w", pady=(0, 5))
        row += 1
        
        if items_list:
            for i, item in enumerate(items_list):
                # Create button text
                button_text = f"{i+1}. {item.item}"
                
                # Create button
                item_btn = tk.Button(self.items_frame, text=button_text, 
                                   anchor="w", relief="flat", bd=1,
                                   command=lambda it=item, idx=i, btn=None: 
                                   self.select_item(("item", idx), btn))
                
                # Store button reference for later highlighting
                item_btn.configure(command=lambda it=item, idx=i, btn=item_btn: 
                                 self.select_item(("item", idx), btn))
                
                item_btn.grid(row=row, column=0, sticky="ew", pady=2)
                row += 1
                
                # Add details label
                details_text = f"   Step Req: {item.step_requirement}, Rarity: {item.rarity_weight}"
                details_label = ttk.Label(self.items_frame, text=details_text, 
                                        font=("Arial", 7), foreground="gray")
                details_label.grid(row=row, column=0, sticky="w", padx=(10, 0), pady=(0, 5))
                row += 1
        else:
            empty_label = ttk.Label(self.items_frame, text="(No items added)", 
                                  font=("Arial", 9), foreground="gray")
            empty_label.grid(row=row, column=0, sticky="w", pady=5)
    
    def select_item(self, item_info, button):
        """Select an item and highlight its button"""
        # Unhighlight previously selected button
        if self.selected_button:
            self.selected_button.config(relief="flat", bg="SystemButtonFace")
        
        # Highlight new button
        if button:
            button.config(relief="sunken", bg="lightblue")
            self.selected_button = button
            self.selected_item = item_info
            self.remove_btn.config(state="normal")
        else:
            self.selected_button = None
            self.selected_item = None
            self.remove_btn.config(state="disabled")
    
    def remove_selected_item(self):
        """Remove the currently selected item"""
        if not self.selected_item:
            messagebox.showwarning("No Selection", "Please select an item to remove.")
            return
        
        item_type, *item_data = self.selected_item
        
        if item_type == "pokemon":
            group_name, pokemon_index = item_data
            removed_pokemon = self.route_data['pokemon_groups'][group_name].pop(pokemon_index)
            messagebox.showinfo("Pokemon Removed", 
                              f"Removed {removed_pokemon.species.name} from Group {group_name}")
        
        elif item_type == "item":
            item_index = item_data[0]
            removed_item = self.route_data['items'].pop(item_index)
            messagebox.showinfo("Item Removed", 
                              f"Removed {removed_item.item} from the route")
        
        # Refresh display
        self.refresh_groups_display()
    
    def create_export_route_tab(self):
        """Create the Export Route tab"""
        export_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(export_frame, text="Export Route")
        
        # Configure grid weights
        export_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(export_frame, text="Export Route Code", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Buttons
        generate_txt_btn = ttk.Button(export_frame, text="Generate Code As txt File", 
                                     command=self.generate_route_code_txt, width=30)
        generate_txt_btn.grid(row=1, column=0, pady=10)
        
        generate_here_btn = ttk.Button(export_frame, text="Generate Code Here", 
                                      command=self.generate_route_code_here, width=30)
        generate_here_btn.grid(row=2, column=0, pady=10)
        
        generate_clipboard_btn = ttk.Button(export_frame, text="Generate Code + Copy It", 
                                          command=self.generate_route_code_clipboard, width=30)
        generate_clipboard_btn.grid(row=3, column=0, pady=10)
        
        generate_usrcheat_btn = ttk.Button(export_frame, text="Generate Code As usrcheat.dat", 
                                          command=self.generate_route_code_usrcheat, width=30)
        generate_usrcheat_btn.grid(row=4, column=0, pady=10)
    
    def add_to_group_a(self):
        """Add Pokemon to Group A"""
        self.add_pokemon_to_group("A")
    
    def add_to_group_b(self):
        """Add Pokemon to Group B"""
        self.add_pokemon_to_group("B")
    
    def add_to_group_c(self):
        """Add Pokemon to Group C"""
        self.add_pokemon_to_group("C")
    
    def add_pokemon_to_group(self, group):
        """Add Pokemon to specified group"""
        try:
            # Check if group is already full (max 2 Pokemon per group)
            if len(self.route_data['pokemon_groups'][group]) >= 2:
                messagebox.showwarning("Group Full", 
                                     f"Group {group} already has the maximum of 2 Pokemon.\n"
                                     f"Please remove a Pokemon from Group {group} before adding another.")
                return
            
            # Get all the values from the input fields
            species_name = self.pokemon_species_var.get()
            level = int(self.level_var.get())
            item_name = self.item_var.get()
            form = int(self.form_var.get())
            gender_name = self.gender_var.get()
            move1_name = self.move1_var.get()
            move2_name = self.move2_var.get()
            move3_name = self.move3_var.get()
            move4_name = self.move4_var.get()
            step_requirement = int(self.step_req_var.get())
            rarity_weight = int(self.spawn_chance_var.get())
            
            # Convert string names to enum values
            species = Species[species_name]
            gender = Gender[gender_name]
            moves = [Move[move1_name], Move[move2_name], Move[move3_name], Move[move4_name]]
            
            # Create PokeWalkerSlot object
            pokemon_slot = PokeWalkerSlot(
                species=species,
                level=level,
                item=item_name,
                form=form,
                gender=gender,
                moves=moves,
                step_requirement=step_requirement,
                rarity_weight=rarity_weight
            )
            
            # Add to the appropriate group
            self.route_data['pokemon_groups'][group].append(pokemon_slot)
            
            # Show confirmation message
            messagebox.showinfo(f"Added to Group {group}", 
                              f"Pokemon added to Group {group}:\n" +
                              f"Species: {species_name}\n" +
                              f"Level: {level}\n" +
                              f"Gender: {gender_name}")
            
        except (ValueError, KeyError) as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    
    def add_item_to_route(self):
        """Add item to route"""
        try:
            # Check if route already has maximum items (max 10 items)
            if len(self.route_data['items']) >= 10:
                messagebox.showwarning("Route Full", 
                                     "Route already has the maximum of 10 items.\n"
                                     "Please remove an item from the route before adding another.")
                return
            
            # Get values from input fields
            item_name = self.item_name_var.get()
            step_requirement = int(self.item_step_req_var.get())
            rarity_weight = int(self.item_spawn_chance_var.get())
            
            # Create PokeWalkerItem object
            item = PokeWalkerItem(
                item=item_name,
                step_requirement=step_requirement,
                rarity_weight=rarity_weight
            )
            
            # Add to route data
            self.route_data['items'].append(item)
            
            # Show confirmation message
            messagebox.showinfo("Item Added", 
                              f"Item added to route:\n" +
                              f"Name: {item_name}\n" +
                              f"Step Requirement: {step_requirement}\n" +
                              f"Spawn Chance: {rarity_weight}")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    
    def fill_all_item_slots(self):
        """Fill all 10 item slots with the currently selected item"""
        try:
            # Get values from input fields
            item_name = self.item_name_var.get()
            step_requirement = int(self.item_step_req_var.get())
            rarity_weight = int(self.item_spawn_chance_var.get())
            
            # Create PokeWalkerItem object
            item = PokeWalkerItem(
                item=item_name,
                step_requirement=step_requirement,
                rarity_weight=rarity_weight
            )
            
            # Clear existing items and fill all 10 slots
            self.route_data['items'] = [item] * 10
            
            # Show confirmation message
            messagebox.showinfo("All Item Slots Filled", 
                              f"All 10 item slots have been filled with:\n" +
                              f"Name: {item_name}\n" +
                              f"Step Requirement: {step_requirement}\n" +
                              f"Spawn Chance: {rarity_weight}\n\n" +
                              f"Previous items have been overwritten.")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    
    def update_route_info(self):
        """Update route information"""
        try:
            # Get values from input fields
            route_image_name = self.route_image_var.get()
            watt_requirement = int(self.watt_requirement_var.get())
            
            # Convert string name to enum value
            route_image = RouteImage[route_image_name]
            
            # Update route data
            self.route_data['route_info']['image'] = route_image
            self.route_data['route_info']['watt_requirement'] = watt_requirement
            
            # Show confirmation message
            messagebox.showinfo("Route Info Updated", 
                              f"Route information updated:\n" +
                              f"Image: {route_image_name}\n" +
                              f"Watt Requirement: {watt_requirement}")
            
        except (ValueError, KeyError) as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    
    def generate_route_code_txt(self):
        """Generate route code and save as txt file"""
        try:
            # Validate route data
            if not self.validate_route_data():
                return
            
            # Create PokeWalkerCourse object
            course = self.create_course_object()
            
            # Generate AR code
            ar_code = course.to_ar_code()
            
            # Save to desktop
            desktop_path = self.get_desktop_path()
            filename = f"route_code_custom.txt"
            filepath = os.path.join(desktop_path, filename)
            
            with open(filepath, 'w') as f:
                f.write(ar_code)
            
            messagebox.showinfo("Success", f"Route code saved to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate route code: {str(e)}")
    
    def generate_route_code_here(self):
        """Generate route code and display here"""
        try:
            # Validate route data
            if not self.validate_route_data():
                return
            
            # Create PokeWalkerCourse object
            course = self.create_course_object()
            
            # Generate AR code
            ar_code = course.to_ar_code()
            
            # Create a new window to display the code
            code_window = tk.Toplevel(self.root)
            code_window.title("Generated Route Code")
            code_window.geometry("600x400")
            
            # Add text widget with scrollbar
            text_widget = tk.Text(code_window, wrap=tk.WORD, font=("Courier", 10))
            scrollbar = ttk.Scrollbar(code_window, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
            
            # Insert the code
            text_widget.insert(tk.END, ar_code)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate route code: {str(e)}")
    
    def generate_route_code_clipboard(self):
        """Generate route code and copy to clipboard"""
        try:
            # Validate route data
            if not self.validate_route_data():
                return
            
            # Create PokeWalkerCourse object
            course = self.create_course_object()
            
            # Generate AR code
            ar_code = course.to_ar_code()
            
            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(ar_code)
            
            messagebox.showinfo("Success", "Route code copied to clipboard!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate route code: {str(e)}")
    
    def generate_route_code_usrcheat(self):
        """Generate route code and save as usrcheat.dat file"""
        try:
            # Validate route data
            if not self.validate_route_data():
                return
            
            # Create PokeWalkerCourse object
            course = self.create_course_object()
            
            # Generate usrcheat.dat data
            usrcheat_data = course.to_usr_cheat_dat()
            
            # Save to desktop
            desktop_path = self.get_desktop_path()
            filename = "usrcheat.dat"
            filepath = os.path.join(desktop_path, filename)
            
            with open(filepath, 'wb') as f:
                f.write(usrcheat_data)
            
            messagebox.showinfo("Success", f"usrcheat.dat file saved to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate usrcheat.dat file: {str(e)}")
    
    def validate_route_data(self):
        """Validate that route data is complete"""
        # Check if all groups have exactly 2 Pokemon
        for group_name, pokemon_list in self.route_data['pokemon_groups'].items():
            if len(pokemon_list) != 2:
                messagebox.showerror("Validation Error", 
                                   f"Group {group_name} must have exactly 2 Pokemon. Current: {len(pokemon_list)}")
                return False
        
        # Check if we have exactly 10 items
        if len(self.route_data['items']) != 10:
            messagebox.showerror("Validation Error", 
                               f"Route must have exactly 10 items. Current: {len(self.route_data['items'])}")
            return False
        
        return True
    
    def create_course_object(self):
        """Create PokeWalkerCourse object from route data"""
        return PokeWalkerCourse(
            watt_requirement=self.route_data['route_info']['watt_requirement'],
            route_image=self.route_data['route_info']['image'],
            group_a=self.route_data['pokemon_groups']['A'],
            group_b=self.route_data['pokemon_groups']['B'],
            group_c=self.route_data['pokemon_groups']['C'],
            items=self.route_data['items'],
            special_types=self.route_data['special_types']
        )
    
    def select_main_sprite_file(self):
        """Open file dialog to select sprite file"""
        file_path = filedialog.askopenfilename(
            title="Select Sprite File",
            filetypes=[
                ("All supported files", "*.bin;*.png;*.jpg;*.jpeg"),
                ("Binary files", "*.bin"),
                ("Image files", "*.png;*.jpg;*.jpeg"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg;*.jpeg")
            ]
        )
        
        if file_path:
            self.handle_sprite_selection(file_path)
    
    def select_route_sprite_file(self):
        """Open file dialog to select route sprite file"""
        file_path = filedialog.askopenfilename(
            title="Select Route Sprite File",
            filetypes=[
                ("All supported files", "*.bin;*.png;*.jpg;*.jpeg"),
                ("Binary files", "*.bin"),
                ("Image files", "*.png;*.jpg;*.jpeg"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg;*.jpeg")
            ]
        )
        
        if file_path:
            self.handle_route_sprite_selection(file_path)
    
    def handle_sprite_selection(self, file_path):
        """Handle the selected sprite file"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension not in ['.bin', '.png', '.jpg', '.jpeg']:
            messagebox.showinfo("Invalid File", "Please select a .bin, .png, .jpg, or .jpeg file")
            return
        
        self.selected_file_path = file_path
        self.current_view = "sprite_result"
        self.clear_frame()
        
        # Back button (top right)
        back_btn = ttk.Button(self.main_frame, text="Back", 
                             command=self.show_sprite_menu, width=10)
        back_btn.grid(row=0, column=1, sticky="e", padx=(0, 10))
        
        if file_extension in ['.png', '.jpg', '.jpeg']:
            self.show_image_result(file_path)
        elif file_extension == '.bin':
            self.show_bin_result(file_path)
    
    def handle_route_sprite_selection(self, file_path):
        """Handle the selected route sprite file"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension not in ['.bin', '.png', '.jpg', '.jpeg']:
            messagebox.showinfo("Invalid File", "Please select a .bin, .png, .jpg, or .jpeg file")
            return
        
        self.selected_file_path = file_path
        self.current_view = "route_sprite_result"
        self.clear_frame()
        
        # Back button (top right)
        back_btn = ttk.Button(self.main_frame, text="Back", 
                             command=self.show_sprite_menu, width=10)
        back_btn.grid(row=0, column=1, sticky="e", padx=(0, 10))
        
        if file_extension in ['.png', '.jpg', '.jpeg']:
            self.show_route_image_result(file_path)
        elif file_extension == '.bin':
            self.show_route_bin_result(file_path)
    
    def show_image_result(self, file_path):
        """Show image file result"""
        # Convert button
        convert_btn = ttk.Button(self.main_frame, text="Convert To .Bin", 
                                command=self.convert_image_to_bin, width=30)
        convert_btn.grid(row=1, column=0, columnspan=2, pady=(20, 10))
        
        try:
            # Load and display image
            img = Image.open(file_path)
            
            # Resize if too large (max 200x200 for display)
            max_size = 200
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for Tkinter
            photo = ImageTk.PhotoImage(img)
            
            # Create image label
            img_label = ttk.Label(self.main_frame, image=photo)
            img_label.image = photo  # Keep a reference
            img_label.grid(row=2, column=0, columnspan=2, pady=10)
            
            # File info
            filename_label = ttk.Label(self.main_frame, text=f"Selected: {os.path.basename(file_path)}")
            filename_label.grid(row=3, column=0, columnspan=2, pady=5)
            
            size_label = ttk.Label(self.main_frame, text=f"Size: {img.width}x{img.height}")
            size_label.grid(row=4, column=0, columnspan=2, pady=5)
            
        except Exception as e:
            error_label = ttk.Label(self.main_frame, text=f"Error loading image: {e}")
            error_label.grid(row=2, column=0, columnspan=2, pady=10)
    
    def show_route_image_result(self, file_path):
        """Show route image file result"""
        # Convert button
        convert_btn = ttk.Button(self.main_frame, text="Convert To .Bin", 
                                command=self.convert_route_image_to_bin, width=30)
        convert_btn.grid(row=1, column=0, columnspan=2, pady=(20, 10))
        
        try:
            # Load and display image
            img = Image.open(file_path)
            
            # Resize if too large (max 200x200 for display)
            max_size = 200
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for Tkinter
            photo = ImageTk.PhotoImage(img)
            
            # Create image label
            img_label = ttk.Label(self.main_frame, image=photo)
            img_label.image = photo  # Keep a reference
            img_label.grid(row=2, column=0, columnspan=2, pady=10)
            
            # File info
            filename_label = ttk.Label(self.main_frame, text=f"Selected: {os.path.basename(file_path)}")
            filename_label.grid(row=3, column=0, columnspan=2, pady=5)
            
            size_label = ttk.Label(self.main_frame, text=f"Size: {img.width}x{img.height}")
            size_label.grid(row=4, column=0, columnspan=2, pady=5)
            
        except Exception as e:
            error_label = ttk.Label(self.main_frame, text=f"Error loading image: {e}")
            error_label.grid(row=2, column=0, columnspan=2, pady=10)
    
    def show_bin_result(self, file_path):
        """Show bin file result"""
        # Convert button
        convert_btn = ttk.Button(self.main_frame, text="Convert To Image", 
                                command=self.convert_bin_to_image, width=30)
        convert_btn.grid(row=1, column=0, columnspan=2, pady=(20, 20))
        
        # Message
        message_label = ttk.Label(self.main_frame, 
                                 text="You selected a .bin file, so nothing can be displayed until it has been converted",
                                 wraplength=350, justify="center")
        message_label.grid(row=2, column=0, columnspan=2, pady=10)
        
        # File info
        filename_label = ttk.Label(self.main_frame, text=f"Selected: {os.path.basename(file_path)}")
        filename_label.grid(row=3, column=0, columnspan=2, pady=5)
    
    def show_route_bin_result(self, file_path):
        """Show route bin file result"""
        # Convert button
        convert_btn = ttk.Button(self.main_frame, text="Convert To Image", 
                                command=self.convert_route_bin_to_image, width=30)
        convert_btn.grid(row=1, column=0, columnspan=2, pady=(20, 20))
        
        # Message
        message_label = ttk.Label(self.main_frame, 
                                 text="You selected a .bin file, so nothing can be displayed until it has been converted",
                                 wraplength=350, justify="center")
        message_label.grid(row=2, column=0, columnspan=2, pady=10)
        
        # File info
        filename_label = ttk.Label(self.main_frame, text=f"Selected: {os.path.basename(file_path)}")
        filename_label.grid(row=3, column=0, columnspan=2, pady=5)
    
    def convert_bin_to_image(self):
        """Convert the selected bin file to image and display it"""
        if not self.selected_file_path:
            messagebox.showerror("Error", "No file selected")
            return
        
        try:
            # Check for OneDrive desktop first, then fall back to default desktop
            desktop_path = self.get_desktop_path()
            output_filename = os.path.splitext(os.path.basename(self.selected_file_path))[0] + ".png"
            output_filepath = os.path.join(desktop_path, output_filename)
            
            # Convert the file
            final_img = convert_bin_to_image(self.selected_file_path, output_filepath)
            
            if final_img:
                # Update the display to show the converted image
                self.show_converted_image(final_img, output_filepath)
                messagebox.showinfo("Success", f"Image converted and saved to desktop as {output_filename}")
            else:
                messagebox.showerror("Error", "Failed to convert the binary file")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error converting file: {e}")
    
    def convert_route_bin_to_image(self):
        """Convert the selected route bin file to image using RouteImages.py"""
        if not self.selected_file_path:
            messagebox.showerror("Error", "No file selected")
            return
        
        try:
            # Get the path to RouteImages.py
            route_script_path = os.path.join(os.path.dirname(__file__), 'Backend', 'Tools', 'RouteImages.py')
            
            # Run RouteImages.py as a subprocess
            result = subprocess.run([sys.executable, route_script_path, self.selected_file_path], 
                                  capture_output=True, text=True, cwd=os.path.dirname(route_script_path))
            
            if result.returncode == 0:
                # Find the output file on desktop
                desktop_path = self.get_desktop_path()
                base_name = os.path.splitext(os.path.basename(self.selected_file_path))[0]
                output_filepath = os.path.join(desktop_path, f"{base_name}.png")
                
                if os.path.exists(output_filepath):
                    # Load and display the converted image
                    img = Image.open(output_filepath)
                    self.show_converted_image(img, output_filepath)
                    messagebox.showinfo("Success", f"Route image converted and saved to desktop as {os.path.basename(output_filepath)}")
                else:
                    messagebox.showerror("Error", "Conversion completed but output file not found")
            else:
                messagebox.showerror("Error", f"Failed to convert route binary file: {result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error converting route file: {e}")
    
    def get_desktop_path(self):
        """Get the correct desktop path, checking for OneDrive first"""
        # Check for OneDrive desktop
        onedrive_desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
        if os.path.exists(onedrive_desktop):
            return onedrive_desktop
        
        # Fall back to default desktop
        return os.path.join(os.path.expanduser("~"), "Desktop")
    
    def show_converted_image(self, img, output_filepath):
        """Show the converted image in the GUI"""
        # Clear the current display
        for widget in self.main_frame.winfo_children():
            if widget.grid_info()['row'] >= 2:  # Keep back button and convert button
                widget.destroy()
        
        try:
            # Resize if too large (max 200x200 for display)
            max_size = 200
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for Tkinter
            photo = ImageTk.PhotoImage(img)
            
            # Create image label
            img_label = ttk.Label(self.main_frame, image=photo)
            img_label.image = photo  # Keep a reference
            img_label.grid(row=2, column=0, columnspan=2, pady=10)
            
            # File info
            filename_label = ttk.Label(self.main_frame, text=f"Converted: {os.path.basename(output_filepath)}")
            filename_label.grid(row=3, column=0, columnspan=2, pady=5)
            
            size_label = ttk.Label(self.main_frame, text=f"Size: {img.width}x{img.height}")
            size_label.grid(row=4, column=0, columnspan=2, pady=5)
            
        except Exception as e:
            error_label = ttk.Label(self.main_frame, text=f"Error displaying converted image: {e}")
            error_label.grid(row=2, column=0, columnspan=2, pady=10)
    
    def convert_image_to_bin(self):
        """Convert the selected image file to binary and display it"""
        if not self.selected_file_path:
            messagebox.showerror("Error", "No file selected")
            return
        
        try:
            # Get desktop path (checking for OneDrive first)
            desktop_path = self.get_desktop_path()
            output_filename = os.path.splitext(os.path.basename(self.selected_file_path))[0] + ".bin"
            output_filepath = os.path.join(desktop_path, output_filename)
            
            # Convert the file
            binary_data = convert_image_to_bin(self.selected_file_path, output_filepath)
            
            if binary_data:
                messagebox.showinfo("Success", f"Image converted and saved to desktop as {output_filename}")
                
                # Update the display to show the conversion result
                self.show_bin_conversion_result(output_filepath)
            else:
                messagebox.showerror("Error", "Failed to convert the image file")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error converting file: {e}")
    
    def convert_route_image_to_bin(self):
        """Convert the selected route image file to binary using RouteImages.py"""
        if not self.selected_file_path:
            messagebox.showerror("Error", "No file selected")
            return
        
        try:
            # Get the path to RouteImages.py
            route_script_path = os.path.join(os.path.dirname(__file__), 'Backend', 'Tools', 'RouteImages.py')
            
            # Run RouteImages.py as a subprocess
            result = subprocess.run([sys.executable, route_script_path, self.selected_file_path], 
                                  capture_output=True, text=True, cwd=os.path.dirname(route_script_path))
            
            if result.returncode == 0:
                # Find the output file on desktop
                desktop_path = self.get_desktop_path()
                base_name = os.path.splitext(os.path.basename(self.selected_file_path))[0]
                output_filepath = os.path.join(desktop_path, f"{base_name}.bin")
                
                if os.path.exists(output_filepath):
                    messagebox.showinfo("Success", f"Route image converted and saved to desktop as {base_name}.bin")
                    
                    # Update the display to show the conversion result
                    self.show_route_bin_conversion_result(output_filepath)
                else:
                    messagebox.showerror("Error", "Conversion completed but output file not found")
            else:
                messagebox.showerror("Error", f"Failed to convert route image: {result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error converting route file: {e}")
    
    def show_bin_conversion_result(self, output_filepath):
        """Show the result of converting an image to binary"""
        # Clear the current display
        for widget in self.main_frame.winfo_children():
            if widget.grid_info()['row'] >= 2:  # Keep back button and convert button
                widget.destroy()
        
        # Show conversion result
        result_label = ttk.Label(self.main_frame, 
                                text="Image successfully converted to binary format!",
                                wraplength=350, justify="center")
        result_label.grid(row=2, column=0, columnspan=2, pady=10)
        
        # File info
        filename_label = ttk.Label(self.main_frame, text=f"Saved as: {os.path.basename(output_filepath)}")
        filename_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Size info
        file_size = os.path.getsize(output_filepath)
        size_label = ttk.Label(self.main_frame, text=f"File size: {file_size} bytes")
        size_label.grid(row=4, column=0, columnspan=2, pady=5)
    
    def show_route_bin_conversion_result(self, output_filepath):
        """Show the result of converting a route image to binary"""
        # Clear the current display
        for widget in self.main_frame.winfo_children():
            if widget.grid_info()['row'] >= 2:  # Keep back button and convert button
                widget.destroy()
        
        # Show conversion result
        result_label = ttk.Label(self.main_frame, 
                                text="Route image successfully converted to binary format!",
                                wraplength=350, justify="center")
        result_label.grid(row=2, column=0, columnspan=2, pady=10)
        
        # File info
        filename_label = ttk.Label(self.main_frame, text=f"Saved as: {os.path.basename(output_filepath)}")
        filename_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Size info
        file_size = os.path.getsize(output_filepath)
        size_label = ttk.Label(self.main_frame, text=f"File size: {file_size} bytes")
        size_label.grid(row=4, column=0, columnspan=2, pady=5)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = WalkerFlowApp()
    app.run() 