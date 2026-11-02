import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from modules.database import HERO_CLASSES, ITEM_DICTIONARY, HERO_ABILITY_IDS, ABILITY_DICTIONARY, ABILITY_MAX_LEVELS
from ui.dark_modal import show_dark_alert
from ui.searchable_combo import SearchableCombo

class ProfileEditorPanel(tk.Frame):
    def __init__(self, parent, manager, initial_data=None, on_close_callback=None):
        super().__init__(parent, bg="#1e1e1e")
        self.manager = manager
        self.on_close = on_close_callback
        self.data = initial_data if initial_data else {}
        self.pack(fill=tk.BOTH, expand=True)

        top_bar = tk.Frame(self, bg="#1e1e1e")
        top_bar.pack(fill=tk.X, pady=(5, 10))

        title_lbl = tk.Label(top_bar, text="🛠️ HERO CHARACTER PROFILE EDITOR",
                             font=("Segoe UI", 12, "bold"), bg="#1e1e1e", fg="#00ffcc")
        title_lbl.pack(side=tk.LEFT)

        close_btn = tk.Button(top_bar, text="❌ Close", font=("Segoe UI", 9, "bold"),
                              bg="#2d2d30", fg="#d4d4d4", activebackground="#cc3333", activeforeground="#ffffff",
                              bd=0, padx=12, pady=4, cursor="hand2", command=self.on_close)
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Enter>", lambda e: close_btn.configure(bg="#cc3333", fg="#ffffff"))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(bg="#2d2d30", fg="#d4d4d4"))

        canvas_container = tk.Frame(self, bg="#1e1e1e")
        canvas_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_container, bg="#1e1e1e", bd=0, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview,
                                  style="Dark.Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.scroll_content = tk.Frame(self.canvas, bg="#1e1e1e")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.scroll_content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width - 20))

        self.bind("<Enter>", lambda event: self.canvas.bind_all("<MouseWheel>", self.handle_mouse_wheel_scrolling))
        self.bind("<Leave>", lambda event: self.canvas.unbind_all("<MouseWheel>"))

        self.entries = {}
        self.ability_entries = []
        self.inventory_rows = []
        self.stash_containers = {f"stash_{i}": [] for i in range(1, 7)}
        self.add_buttons_map = {}
        self.has_validation_error = False

        self.build_primary_stats_grid_sections()
        self.build_abilities_panel_container()
        self.build_gear_and_stashes_panels_sections()
        self.build_minimized_progression_collapsible_box()
        self.build_footer_compilation_action_bar()

    def handle_mouse_wheel_scrolling(self, event):
        if self.winfo_exists() and self.winfo_viewable():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_stat_entry_field(self, parent, label_text, key_name, default_val="0", clamp_min=0, clamp_max=None, split_proportion=False):
        """
        Creates a crisp stat entry row. Supports standard fluid layouts or a strict
        balanced 50/50 proportional grid distribution wrapper for long metadata blocks.
        """
        frame = tk.Frame(parent, bg="#1e1e1e")
        frame.pack(fill=tk.X, pady=3)

        val = self.data.get(key_name, default_val)

        if split_proportion:
            frame.columnconfigure(0, weight=1, uniform="prog_row")
            frame.columnconfigure(1, weight=1, uniform="prog_row")

            lbl = tk.Label(frame, text=label_text, font=("Segoe UI", 9, "bold"), bg="#1e1e1e", fg="#ffffff", anchor="w")
            lbl.grid(row=0, column=0, sticky="ew", padx=(5, 5))

            entry = tk.Entry(frame, bg="#252526", fg="#ffffff", insertbackground="#00ffcc",
                             bd=1, relief=tk.SOLID, font=("Segoe UI", 10), justify=tk.CENTER,
                             highlightbackground="#2d2d30", highlightcolor="#00ffcc", highlightthickness=1)
            entry.insert(0, str(val))
            entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        else:
            lbl = tk.Label(frame, text=label_text, font=("Segoe UI", 9, "bold"), bg="#1e1e1e", fg="#ffffff", width=16, anchor="w")
            lbl.pack(side=tk.LEFT, padx=5)

            entry = tk.Entry(frame, bg="#252526", fg="#ffffff", insertbackground="#00ffcc",
                             bd=1, relief=tk.SOLID, font=("Segoe UI", 10), justify=tk.CENTER,
                             highlightbackground="#2d2d30", highlightcolor="#00ffcc", highlightthickness=1)
            entry.insert(0, str(val))
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        entry.bind("<FocusIn>", lambda e: entry.configure(highlightbackground="#00ffcc"))
        entry.bind("<FocusOut>", lambda e: entry.configure(highlightbackground="#2d2d30"))
        entry.bind("<Enter>", lambda e: entry.configure(highlightbackground="#00ffcc") if self.focus_get() != entry else None)
        entry.bind("<Leave>", lambda e: entry.configure(highlightbackground="#2d2d30") if self.focus_get() != entry else None)

        def enforce_numerical_bounds(event):
            try:
                num = int(entry.get())
                if clamp_min is not None and num < clamp_min: num = clamp_min
                if clamp_max is not None and num > clamp_max: num = clamp_max
                entry.delete(0, tk.END)
                entry.insert(0, str(num))
            except ValueError:
                entry.delete(0, tk.END)
                entry.insert(0, str(clamp_min))

        entry.bind("<FocusOut>", lambda event: (enforce_numerical_bounds(event), entry.configure(highlightbackground="#2d2d30")), add="+")
        self.entries[key_name] = entry

    def build_primary_stats_grid_sections(self):
        grid_frame = tk.Frame(self.scroll_content, bg="#1e1e1e")
        grid_frame.pack(fill=tk.X, pady=5)

        grid_frame.columnconfigure(0, weight=1, uniform="stat_cols")
        grid_frame.columnconfigure(1, weight=1, uniform="stat_cols")
        grid_frame.columnconfigure(2, weight=1, uniform="stat_cols")

        col1 = tk.LabelFrame(grid_frame, text=" 👤 CHARACTER", font=("Segoe UI", 9, "bold"),
                             bg="#1e1e1e", fg="#00ffcc", highlightbackground="#2d2d30", highlightthickness=1,
                             labelanchor="n")
        col1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        p_frame = tk.Frame(col1, bg="#1e1e1e")
        p_frame.pack(fill=tk.X, pady=4)
        tk.Label(p_frame, text="Player Name *", font=("Segoe UI", 9, "bold"), bg="#1e1e1e", fg="#ffffff", width=16,
                 anchor="w").pack(side=tk.LEFT, padx=5)

        p_entry = tk.Entry(p_frame, bg="#252526", fg="#ffffff", insertbackground="#00ffcc", bd=1, relief=tk.SOLID,
                           font=("Segoe UI", 10),
                           justify=tk.CENTER, highlightbackground="#2d2d30", highlightcolor="#00ffcc",
                           highlightthickness=1)
        p_entry.insert(0, self.data.get("player_name", ""))
        p_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entries["player_name"] = p_entry

        p_entry.bind("<FocusIn>", lambda e: p_entry.configure(
            highlightbackground="#00ffcc") if not self.has_validation_error else None)
        p_entry.bind("<FocusOut>", lambda e: p_entry.configure(
            highlightbackground="#2d2d30") if not self.has_validation_error else None)
        p_entry.bind("<Enter>", lambda e: p_entry.configure(highlightbackground="#00ffcc") if (
                    self.focus_get() != p_entry and not self.has_validation_error) else None)
        p_entry.bind("<Leave>", lambda e: p_entry.configure(highlightbackground="#2d2d30") if (
                    self.focus_get() != p_entry and not self.has_validation_error) else None)

        c_frame = tk.Frame(col1, bg="#1e1e1e")
        c_frame.pack(fill=tk.X, pady=4)
        tk.Label(c_frame, text="Hero Class *", font=("Segoe UI", 9, "bold"), bg="#1e1e1e", fg="#ffffff", width=16,
                 anchor="w").pack(side=tk.LEFT, padx=5)

        self.class_combo = SearchableCombo(c_frame, HERO_CLASSES.keys(),
                                           default_val=self.data.get("hero_class", "Novice (Male)"), width=20)
        self.class_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.class_combo.entry_var.trace_add("write", lambda *a: self.refresh_dynamic_abilities_grid())

        self.create_stat_entry_field(col1, "Hero Experience", "experience", default_val=0, clamp_min=0, clamp_max=4529550)

        z_frame = tk.Frame(col1, bg="#1e1e1e")
        z_frame.pack(fill=tk.X, pady=4)
        tk.Label(z_frame, text="Checkpoint Zone", font=("Segoe UI", 9, "bold"), bg="#1e1e1e", fg="#ffffff", width=16,
                 anchor="w").pack(side=tk.LEFT, padx=5)
        self.zone_combo = SearchableCombo(z_frame, ["1", "2", "3", "4", "5"],
                                          default_val=str(self.data.get("checkpoint_zone", 1)), width=20)
        self.zone_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        col2 = tk.LabelFrame(grid_frame, text=" 🛠️ PROFESSION ", font=("Segoe UI", 9, "bold"),
                             bg="#1e1e1e", fg="#00ffcc", highlightbackground="#2d2d30", highlightthickness=1,
                             labelanchor="n")
        col2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.create_stat_entry_field(col2, "Profession Level", "profession_level", default_val=0, clamp_min=0,
                                     clamp_max=250)
        self.create_stat_entry_field(col2, "Profession Quest", "profession_quest_complete", default_val=0, clamp_min=0,
                                     clamp_max=1)
        self.create_stat_entry_field(col2, "Profession Rank", "profession_rank", default_val=0, clamp_min=0,
                                     clamp_max=5)

        col3 = tk.LabelFrame(grid_frame, text=" 📊 ECONOMICS ", font=("Segoe UI", 9, "bold"),
                             bg="#1e1e1e", fg="#00ffcc", highlightbackground="#2d2d30", highlightthickness=1,
                             labelanchor="n")
        col3.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        self.create_stat_entry_field(col3, "Gold", "gold", default_val=1500, clamp_min=0, clamp_max=1000000)
        self.create_stat_entry_field(col3, "Power Shards", "power_shards", default_val=0, clamp_min=0, clamp_max=1000)
        self.create_stat_entry_field(col3, "Prestige", "prestige", default_val=0, clamp_min=0)
        self.create_stat_entry_field(col3, "Souls Collected", "souls", default_val=0, clamp_min=0, clamp_max=155)

    def build_abilities_panel_container(self):
        self.abilities_panel = tk.LabelFrame(self.scroll_content, text=" ✨ HERO SPELLS",
                                             font=("Segoe UI", 9, "bold"),
                                             bg="#1e1e1e", fg="#00ffcc", highlightbackground="#2d2d30",
                                             highlightthickness=1, labelanchor="n")
        self.abilities_panel.pack(fill=tk.X, padx=5, pady=10)

        self.inner_grid_area = tk.Frame(self.abilities_panel, bg="#1e1e1e")
        self.inner_grid_area.pack(fill=tk.X, padx=10, pady=10)
        self.refresh_dynamic_abilities_grid()

    def refresh_dynamic_abilities_grid(self):
        """Wipes out rows and populates inputs inside uniform columns matching level caps dynamically."""
        for widget in self.inner_grid_area.winfo_children(): widget.destroy()
        self.ability_entries.clear()

        active_class = self.class_combo.get()
        if active_class not in HERO_CLASSES:
            lbl = tk.Label(self.inner_grid_area, text="[⚠️ SYSTEM] Waiting for a verified Hero Class selection...",
                           font=("Segoe UI", 10, "italic"), bg="#1e1e1e", fg="#888888")
            lbl.pack(pady=15)
            return

        self.inner_grid_area.columnconfigure(0, weight=1, uniform="ab_cols")
        self.inner_grid_area.columnconfigure(1, weight=1, uniform="ab_cols")

        ability_indices = HERO_ABILITY_IDS.get(active_class, [])
        reverse_ability_names = {v: k for k, v in ABILITY_DICTIONARY.items()}
        saved_levels = self.data.get("ability_levels", [])

        running_slot_index = 0
        if active_class == "Annihilator":
            row_num = running_slot_index // 2
            col_num = running_slot_index % 2

            row_frame = tk.Frame(self.inner_grid_area, bg="#1e1e1e")
            row_frame.grid(row=row_num, column=col_num, sticky="ew", padx=15, pady=6)

            bounty_lbl = tk.Label(row_frame, text="⚔️ Annihilator Bounty Level", font=("Segoe UI", 10, "bold"),
                                  bg="#1e1e1e", fg="#d4d4d4", width=24, anchor="w")
            bounty_lbl.pack(side=tk.LEFT, padx=(5, 5))

            b_entry = tk.Entry(row_frame, bg="#252526", fg="#ffffff", insertbackground="#00ffcc",
                               bd=1, relief=tk.SOLID, font=("Segoe UI", 10), width=6, justify=tk.CENTER,
                               highlightbackground="#2d2d30", highlightcolor="#00ffcc", highlightthickness=1)
            b_entry.insert(0, str(self.data.get("annihilator_bounty_level", 0)))
            b_entry.pack(side=tk.RIGHT, padx=(0, 10))

            b_entry.bind("<FocusIn>", lambda e: b_entry.configure(highlightbackground="#00ffcc"))
            b_entry.bind("<FocusOut>", lambda e: b_entry.configure(highlightbackground="#2d2d30"))
            b_entry.bind("<Enter>", lambda e: b_entry.configure(highlightbackground="#00ffcc") if self.focus_get() != b_entry else None)
            b_entry.bind("<Leave>", lambda e: b_entry.configure(highlightbackground="#2d2d30") if self.focus_get() != b_entry else None)

            def clamp_bounty_range(event):
                try:
                    num = int(b_entry.get())
                    if num < 0: num = 0
                    if num > 17: num = 17
                    b_entry.delete(0, tk.END)
                    b_entry.insert(0, str(num))
                except ValueError:
                    b_entry.delete(0, tk.END)
                    b_entry.insert(0, "0")

            b_entry.bind("<FocusOut>", lambda event: (clamp_bounty_range(event), b_entry.configure(highlightbackground="#2d2d30")), add="+")
            self.entries["annihilator_bounty_level"] = b_entry
            running_slot_index += 1

        for ab_id in ability_indices:
            human_spell_name = reverse_ability_names.get(ab_id, f"Ability Slot Block (ID: {ab_id})")
            default_lvl = saved_levels[ability_indices.index(ab_id)] if ability_indices.index(ab_id) < len(saved_levels) else 0

            row_num = running_slot_index // 2
            col_num = running_slot_index % 2

            row_frame = tk.Frame(self.inner_grid_area, bg="#1e1e1e")
            row_frame.grid(row=row_num, column=col_num, sticky="ew", padx=15, pady=6)

            spell_lbl = tk.Label(row_frame, text=human_spell_name, font=("Segoe UI", 10, "bold"),
                                 bg="#1e1e1e", fg="#d4d4d4", width=24, anchor="w")
            spell_lbl.pack(side=tk.LEFT, padx=(5, 5))

            lvl_entry = tk.Entry(row_frame, bg="#252526", fg="#ffffff", insertbackground="#00ffcc",
                                 bd=1, relief=tk.SOLID, font=("Segoe UI", 10), width=6, justify=tk.CENTER,
                                 highlightbackground="#2d2d30", highlightcolor="#00ffcc", highlightthickness=1)
            lvl_entry.insert(0, str(default_lvl))
            lvl_entry.pack(side=tk.RIGHT, padx=(0, 10))

            lvl_entry.bind("<FocusIn>", lambda e, ent=lvl_entry: ent.configure(highlightbackground="#00ffcc"))
            lvl_entry.bind("<FocusOut>", lambda e, ent=lvl_entry: ent.configure(highlightbackground="#2d2d30"))
            lvl_entry.bind("<Enter>", lambda e, ent=lvl_entry: ent.configure(highlightbackground="#00ffcc") if self.focus_get() != ent else None)
            lvl_entry.bind("<Leave>", lambda e, ent=lvl_entry: ent.configure(highlightbackground="#2d2d30") if self.focus_get() != ent else None)

            current_max_clamp = ABILITY_MAX_LEVELS.get(ab_id, 30)

            def clamp_spell_range(event, ent=lvl_entry, max_limit=current_max_clamp):
                try:
                    num = int(ent.get())
                    if num < 0: num = 0
                    if num > max_limit: num = max_limit
                    ent.delete(0, tk.END)
                    ent.insert(0, str(num))
                except ValueError:
                    ent.delete(0, tk.END)
                    ent.insert(0, "0")

            lvl_entry.bind("<FocusOut>", lambda event, ent=lvl_entry, ml=current_max_clamp: (clamp_spell_range(event, ent, ml), ent.configure(highlightbackground="#2d2d30")), add="+")
            self.ability_entries.append((ab_id, lvl_entry))
            running_slot_index += 1

    def build_gear_and_stashes_panels_sections(self):
        """Builds parallel dynamic rows blocks for Main Inventory and Stashes 1-6 split exactly 50/50."""
        storage_frame = tk.Frame(self.scroll_content, bg="#1e1e1e")
        storage_frame.pack(fill=tk.X, pady=5)

        storage_frame.columnconfigure(0, weight=1, uniform="group1")
        storage_frame.columnconfigure(1, weight=1, uniform="group1")

        inv_box = tk.LabelFrame(storage_frame, text=" 🎒 INVENTORY ", font=("Segoe UI", 9, "bold"),
                                bg="#1e1e1e", fg="#00ffcc", highlightbackground="#2d2d30", highlightthickness=1,
                                labelanchor="n")
        inv_box.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        inv_box.grid_columnconfigure(0, weight=1)

        self.inv_rows_container = tk.Frame(inv_box, bg="#1e1e1e")
        self.inv_rows_container.pack(fill=tk.X, padx=10, pady=5)

        loaded_inv = [item for item in self.data.get("inventory", []) if item and item != "Empty"]
        for item in loaded_inv:
            self.add_item_row_slot(self.inv_rows_container, item, self.inventory_rows, "inventory")

        add_inv_btn = tk.Button(self.inv_rows_container, text="➕ Add Item Slot", font=("Segoe UI", 9, "bold"),
                                bg="#252526", fg="#00ffcc", activebackground="#0a7b83", activeforeground="#ffffff",
                                bd=0, pady=4, cursor="hand2",
                                command=lambda: self.add_item_row_slot(self.inv_rows_container, "Empty",
                                                                       self.inventory_rows, "inventory"))
        add_inv_btn.bind("<Enter>", lambda e: add_inv_btn.configure(bg="#2d2d30", fg="#ffffff"))
        add_inv_btn.bind("<Leave>", lambda e: add_inv_btn.configure(bg="#252526", fg="#00ffcc"))
        add_inv_btn.pack(fill=tk.X, padx=10, pady=(5, 10))
        self.add_buttons_map["inventory"] = add_inv_btn
        self.evaluate_button_limits_visibility(self.inventory_rows, "inventory")

        stashes_box = tk.LabelFrame(storage_frame, text=" 🗄️ STASHES ",
                                    font=("Segoe UI", 9, "bold"),
                                    bg="#1e1e1e", fg="#00ffcc", highlightbackground="#2d2d30", highlightthickness=1,
                                    labelanchor="n")
        stashes_box.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        notebook_style = ttk.Style()
        notebook_style.configure("CustomNotebook.TNotebook", background="#1e1e1e", borderwidth=0)
        notebook_style.configure("CustomNotebook.TNotebook.Tab", background="#2d2d30", foreground="#d4d4d4",
                                 font=("Segoe UI", 9), padding=5)
        notebook_style.map("CustomNotebook.TNotebook.Tab",
                           background=[("selected", "#0a7b83"), ("active", "#3e3e42")],
                           foreground=[("selected", "#ffffff"), ("active", "#ffffff")])

        tabs_control = ttk.Notebook(stashes_box, style="CustomNotebook.TNotebook")
        tabs_control.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        saved_stashes_dict = self.data.get("stashes", {})

        for i in range(1, 7):
            stash_key = f"stash_{i}"
            tab_frame = tk.Frame(tabs_control, bg="#1e1e1e")
            tabs_control.add(tab_frame, text=f"Stash {i}")

            rows_layout_area = tk.Frame(tab_frame, bg="#1e1e1e")
            rows_layout_area.pack(fill=tk.X, padx=5, pady=5)

            loaded_stash_items = [item for item in saved_stashes_dict.get(stash_key, []) if
                                  item and item != "Empty"]
            for item in loaded_stash_items:
                self.add_item_row_slot(rows_layout_area, item, self.stash_containers[stash_key], stash_key)

            add_stash_btn = tk.Button(rows_layout_area, text="➕ Add Stash Slot", font=("Segoe UI", 9, "bold"),
                                      bg="#252526", fg="#00ffcc", activebackground="#0a7b83",
                                      activeforeground="#ffffff", bd=0, pady=4, cursor="hand2")
            add_stash_btn.configure(
                command=lambda f=rows_layout_area, sk=stash_key: self.add_item_row_slot(f, "Empty",
                                                                                        self.stash_containers[sk],
                                                                                        sk))
            add_stash_btn.bind("<Enter>", lambda e, b=add_stash_btn: b.configure(bg="#2d2d30", fg="#ffffff"))
            add_stash_btn.bind("<Leave>", lambda e, b=add_stash_btn: b.configure(bg="#252526", fg="#00ffcc"))
            add_stash_btn.pack(fill=tk.X, pady=(5, 5))

            self.add_buttons_map[stash_key] = add_stash_btn
            self.evaluate_button_limits_visibility(self.stash_containers[stash_key], stash_key)

    def add_item_row_slot(self, parent_frame, item_name, tracking_list_target, storage_id_key):
        if len(tracking_list_target) >= 6: return

        row = tk.Frame(parent_frame, bg="#1e1e1e")
        row.pack(fill=tk.X, pady=3)

        combo = SearchableCombo(row, ITEM_DICTIONARY.keys(), default_val=item_name, width=28)
        combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 5))

        del_btn = tk.Button(row, text="✕", font=("Segoe UI", 8, "bold"),
                            bg="#1e1e1e", fg="#666666", activebackground="#1e1e1e", activeforeground="#cc3333",
                            bd=0, cursor="hand2", padx=4)
        del_btn.pack(side=tk.RIGHT)
        del_btn.bind("<Enter>", lambda e: del_btn.configure(fg="#cc3333"))
        del_btn.bind("<Leave>", lambda e: del_btn.configure(fg="#666666"))

        tracking_element_entry = {"frame": row, "combo": combo}
        tracking_list_target.append(tracking_element_entry)

        def trigger_row_destruction(ent=tracking_element_entry, lst=tracking_list_target, sk=storage_id_key):
            if ent in lst: lst.remove(ent)
            ent["frame"].destroy()

            for item_row in lst:
                item_row["frame"].pack_forget()

            for item_row in lst:
                item_row["frame"].pack(fill=tk.X, pady=3)

            self.evaluate_button_limits_visibility(lst, sk)

        del_btn.configure(command=trigger_row_destruction)
        self.evaluate_button_limits_visibility(tracking_list_target, storage_id_key)

    def evaluate_button_limits_visibility(self, active_list, storage_id_key):
        btn = self.add_buttons_map.get(storage_id_key)
        if btn and btn.winfo_exists():
            btn.pack_forget()
            if len(active_list) < 6:
                btn.pack(fill=tk.X, padx=10, pady=(5, 10) if storage_id_key == "inventory" else (5, 5))

    def build_minimized_progression_collapsible_box(self):
        """Maps out the definitive 12-variable progression matrix split across two clean layout panels."""
        self.collapsed_var = tk.BooleanVar(value=True)

        self.prog_box = tk.LabelFrame(self.scroll_content, text=" ⚙️ MAP PROGRESSION SETTINGS (MINIMIZED) ",
                                      font=("Segoe UI", 9, "bold"),
                                      bg="#1e1e1e", fg="#00ffcc", highlightbackground="#2d2d30", highlightthickness=1,
                                      labelanchor="n")
        self.prog_box.pack(fill=tk.X, padx=5, pady=10)

        self.toggle_btn = tk.Button(self.prog_box, text="▶ Expand Progression Settings",
                                    font=("Segoe UI", 9, "bold"),
                                    bg="#1e1e1e", fg="#00ffcc", bd=0, cursor="hand2", pady=4,
                                    command=self.toggle_progression_visibility)
        self.toggle_btn.pack(fill=tk.X, padx=10, pady=5)

        self.hidden_content_frame = tk.Frame(self.prog_box, bg="#1e1e1e")

        f_pane = tk.LabelFrame(self.hidden_content_frame, text=" Campaign Records & Milestones ",
                               font=("Segoe UI", 9, "bold"), bg="#1e1e1e", fg="#00ffcc")
        f_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.create_stat_entry_field(f_pane, "Ult-Gear Harbinger Count", "ultimate_gear_harbinger_count",
                                     default_val=0, clamp_min=0, split_proportion=True)
        self.create_stat_entry_field(f_pane, "Lucky Inspirit Flag", "lucky_inspirit_player", default_val=0,
                                     clamp_min=0, clamp_max=1, split_proportion=True)
        self.create_stat_entry_field(f_pane, "Lucky Triforce Flag", "lucky_triforce_player", default_val=0,
                                     clamp_min=0, clamp_max=1, split_proportion=True)
        self.create_stat_entry_field(f_pane, "Mysterious Sigils Collected", "mysterious_sigils_collected",
                                     default_val=0, clamp_min=0, split_proportion=True)
        self.create_stat_entry_field(f_pane, "Mysterious Notes Read", "mysterious_notes_read", default_val=0,
                                     clamp_min=0, split_proportion=True)
        self.create_stat_entry_field(f_pane, "Mysterious Orbs Collected", "mysterious_orbs_collected", default_val=0,
                                     clamp_min=0, split_proportion=True)

        b_pane = tk.LabelFrame(self.hidden_content_frame, text=" Dungeon Prestiges ",
                               font=("Segoe UI", 9, "bold"), bg="#1e1e1e", fg="#00ffcc")
        b_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.create_stat_entry_field(b_pane, "City of Illusions", "city_of_illusions_prestige", default_val=0,
                                     clamp_min=0, split_proportion=True)
        self.create_stat_entry_field(b_pane, "Dragon Fortress", "dragon_fortress_prestige", default_val=0,
                                     clamp_min=0, split_proportion=True)
        self.create_stat_entry_field(b_pane, "Punishment Chamber", "punishment_chamber_prestige",
                                     default_val=0, clamp_min=0, split_proportion=True)
        self.create_stat_entry_field(b_pane, "Cursed Heaven", "cursed_heaven_prestige", default_val=0,
                                     clamp_min=0, split_proportion=True)
        self.create_stat_entry_field(b_pane, "Chiral Valley", "chiral_valley_prestige", default_val=0,
                                     clamp_min=0, split_proportion=True)
        self.create_stat_entry_field(b_pane, "Tercessuinotlim", "tercessuinotlim_prestige", default_val=0,
                                     clamp_min=0, split_proportion=True)

    def toggle_progression_visibility(self):
        if self.collapsed_var.get():
            self.hidden_content_frame.pack(fill=tk.X, padx=15, pady=(5, 10))
            self.toggle_btn.configure(text="▼ Collapse Progression Settings")
            self.collapsed_var.set(False)
        else:
            self.hidden_content_frame.pack_forget()
            self.toggle_btn.configure(text="▶ Expand Progression Settings")
            self.collapsed_var.set(True)

    def build_footer_compilation_action_bar(self):
        footer = tk.Frame(self.scroll_content, bg="#1e1e1e")
        footer.pack(fill=tk.X, pady=(20, 15))
        center_frame = tk.Frame(footer, bg="#1e1e1e")
        center_frame.pack(anchor=tk.CENTER)

        save_btn = tk.Button(center_frame, text="💾 Encrypt & Save", font=("Segoe UI", 10, "bold"), bg="#0a7b83",
                             fg="#ffffff", activebackground="#0e9aa2", activeforeground="#ffffff", bd=0, padx=25,
                             pady=8, cursor="hand2", command=self.gather_and_validate_encryption_output)
        save_btn.pack(side=tk.LEFT, padx=15)
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg="#0e9aa2"))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg="#0a7b83"))

        copy_btn = tk.Button(center_frame, text="📋 Encrypt & Copy", font=("Segoe UI", 10, "bold"), bg="#2d2d30",
                             fg="#d4d4d4", activebackground="#3e3e42", activeforeground="#ffffff", bd=0, padx=25,
                             pady=8, cursor="hand2", command=self.gather_and_copy_code_clipboard)
        copy_btn.pack(side=tk.LEFT, padx=15)
        copy_btn.bind("<Enter>", lambda e: copy_btn.configure(bg="#3e3e42", fg="#ffffff"))
        copy_btn.bind("<Leave>", lambda e: copy_btn.configure(bg="#2d2d30", fg="#d4d4d4"))

    def collect_current_form_data(self):
        p_name = self.entries["player_name"].get().strip()
        if not p_name:
            self.has_validation_error = True
            self.entries["player_name"].configure(highlightbackground="#cc3333", highlightcolor="#cc3333",
                                                  highlightthickness=2)
            show_dark_alert(self.winfo_toplevel(), "Validation Failure",
                            "Player Name is a strict requirement parameter and cannot be left blank!")
            return None
        else:
            self.has_validation_error = False
            self.entries["player_name"].configure(highlightbackground="#2d2d30", highlightcolor="#00ffcc",
                                                  highlightthickness=1)

        hero_class_str = self.class_combo.get()
        compiled_inv = [row["combo"].get() if row["combo"].get() else "Empty" for row in self.inventory_rows]
        while len(compiled_inv) < 6: compiled_inv.append("Empty")

        compiled_stashes = {}
        for i in range(1, 7):
            sk = f"stash_{i}"
            compiled_stashes[sk] = [row["combo"].get() if row["combo"].get() else "Empty" for row in
                                    self.stash_containers[sk]]
            while len(compiled_stashes[sk]) < 6: compiled_stashes[sk].append("Empty")

        compiled_levels = [int(ent.get()) for ab_id, ent in self.ability_entries]

        saved_seed_i0111 = int(self.data.get("seed_i0111", 0))

        payload = {
            "player_name": p_name,
            "hero_class": hero_class_str,
            "experience": int(self.entries["experience"].get()),
            "checkpoint_zone": int(self.zone_combo.get()),

            "profession_level": int(self.entries["profession_level"].get()),
            "profession_quest_complete": int(self.entries["profession_quest_complete"].get()),
            "profession_rank": int(self.entries["profession_rank"].get()),

            "gold": int(self.entries["gold"].get()),
            "power_shards": int(self.entries["power_shards"].get()),
            "prestige": int(self.entries["prestige"].get()),
            "souls": int(self.entries["souls"].get()),
            "annihilator_bounty_level": int(
                self.entries["annihilator_bounty_level"].get()) if "annihilator_bounty_level" in self.entries else int(
                self.data.get("annihilator_bounty_level", 0)),
            "ability_levels": compiled_levels,
            "inventory": compiled_inv,
            "stashes": compiled_stashes,
            "ultimate_gear_harbinger_count": int(self.entries["ultimate_gear_harbinger_count"].get()),
            "lucky_inspirit_player": int(self.entries["lucky_inspirit_player"].get()),
            "lucky_triforce_player": int(self.entries["lucky_triforce_player"].get()),
            "mysterious_notes_read": int(self.entries["mysterious_notes_read"].get()),
            "mysterious_sigils_collected": int(self.entries["mysterious_sigils_collected"].get()),
            "mysterious_orbs_collected": int(self.entries["mysterious_orbs_collected"].get()),
            "city_of_illusions_prestige": int(self.entries["city_of_illusions_prestige"].get()),
            "dragon_fortress_prestige": int(self.entries["dragon_fortress_prestige"].get()),
            "punishment_chamber_prestige": int(self.entries["punishment_chamber_prestige"].get()),
            "cursed_heaven_prestige": int(self.entries["cursed_heaven_prestige"].get()),
            "chiral_valley_prestige": int(self.entries["chiral_valley_prestige"].get()),
            "tercessuinotlim_prestige": int(self.entries["tercessuinotlim_prestige"].get()),

            "seed_i0111": saved_seed_i0111,
            "pad_7400": 7400,
            "pad_7": 7,
            "pad_player": 0
        }
        return payload

    def gather_and_validate_encryption_output(self):
        data = self.collect_current_form_data()
        if not data: return
        import os, json, modules.encrypt_save as encrypt_save
        cfg_path = os.path.join("configs", "config.json") if os.path.exists("configs") else "config.json"
        with open(cfg_path, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)
        code = encrypt_save.run_encryption(config_path=cfg_path)
        data["generated_code"] = code
        saved_file_path = self.manager.write_save_file_to_disk(data)
        if saved_file_path:
            try:
                root_window = self.winfo_toplevel()
                root_window.sidebar.refresh_saved_directory()
            except Exception:
                pass
            show_dark_alert(self.winfo_toplevel(), "Success", f"Warcraft III Save Code compiled successfully:\n{os.path.basename(saved_file_path)}")

    def gather_and_copy_code_clipboard(self):
        data = self.collect_current_form_data()
        if not data: return
        import os, json, modules.encrypt_save as encrypt_save
        cfg_path = os.path.join("configs", "config.json") if os.path.exists("configs") else "config.json"
        with open(cfg_path, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)
        code = encrypt_save.run_encryption(config_path=cfg_path)
        self.clipboard_clear()
        self.clipboard_append(f"-l {code}")
        show_dark_alert(self.winfo_toplevel(), "Clipboard", "Warcraft III load string successfully copied to clipboard memory!")