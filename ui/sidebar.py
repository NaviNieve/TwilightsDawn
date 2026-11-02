import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import re

from ui.dark_modal import show_dark_alert, ask_dark_confirmation


class SidebarFolderViewer(tk.Frame):
    def __init__(self, parent, manager, on_file_selected_callback):
        super().__init__(parent, bg="#1e1e1e", width=280)
        self.manager = manager
        self.on_file_selected = on_file_selected_callback

        self.pack_propagate(False)
        self.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))

        header = tk.Label(self, text="📁 PROFILE FILES SCANNER", font=("Segoe UI", 10, "bold"),
                          bg="#1e1e1e", fg="#00ffcc", anchor="w")
        header.pack(fill=tk.X, padx=15, pady=(15, 5))

        style = ttk.Style()
        if "clam" in style.theme_names(): style.theme_use("clam")

        style.configure("Treeview",
                        background="#1e1e1e", foreground="#d4d4d4", fieldbackground="#1e1e1e",
                        rowheight=26, font=("Segoe UI", 10), borderwidth=0, highlightthickness=0,
                        bordercolor="#1e1e1e", lightcolor="#1e1e1e", darkcolor="#1e1e1e", arrowcolor="#d4d4d4")
        style.map("Treeview", background=[("selected", "#0a7b83")], foreground=[("selected", "#ffffff")])

        style.configure("Dark.Vertical.TScrollbar",
                        background="#0a7b83", troughcolor="#1e1e1e", bordercolor="#1e1e1e",
                        lightcolor="#0a7b83", darkcolor="#0a7b83", gripcount=0, arrowcolor="#00ffcc",
                        arrowsize=11, thickness=12)
        style.map("Dark.Vertical.TScrollbar", background=[("active", "#0e9aa2"), ("pressed", "#0e9aa2")],
                  lightcolor=[("active", "#0e9aa2"), ("pressed", "#0e9aa2")],
                  darkcolor=[("active", "#0e9aa2"), ("pressed", "#0e9aa2")])

        tree_frame = tk.Frame(self, bg="#1e1e1e", highlightbackground="#00ffcc", highlightcolor="#00ffcc",
                              highlightthickness=1)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        self.tree = ttk.Treeview(tree_frame, show="tree", selectmode="browse", style="Treeview", padding=0)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview,
                                  style="Dark.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.saved_root = self.tree.insert("", "end", text="Saved", open=True)
        self.other_root = self.tree.insert("", "end", text="Other", open=True)

        self.tree.bind("<Double-1>", self.handle_double_click)
        self.tree.bind("<Return>", lambda event: self.handle_double_click(event))
        self.tree.bind("<Motion>", self.handle_row_hover_highlight)

        self.context_menu = tk.Menu(self, tearoff=0, bg="#252526", fg="#ffffff",
                                    activebackground="#0a7b83", activeforeground="#ffffff", bd=1, relief=tk.SOLID)
        self.context_menu.add_command(label="❌ Delete", command=self.execute_context_menu_deletion)

        self.tree.bind("<Button-3>", self.display_context_right_click_menu)

        self.tracked_paths = set()

        self.external_other_registry = []

        self.refresh_saved_directory()
        self.last_hovered_item = None

    def refresh_saved_directory(self):
        expanded_folders = set()

        def record_expanded_states(node_id):
            if self.tree.item(node_id, "open"):
                folder_text = self.tree.item(node_id, "text")
                expanded_folders.add(folder_text)

            for child in self.tree.get_children(node_id):
                record_expanded_states(child)

        record_expanded_states(self.saved_root)
        record_expanded_states(self.other_root)

        for child in self.tree.get_children(self.saved_root): self.tree.delete(child)
        for child in self.tree.get_children(self.other_root): self.tree.delete(child)
        self.tracked_paths.clear()

        disk_data = self.manager.scan_game_save_directory()
        for account_name, classes_dict in sorted(disk_data.items()):
            acc_node = self.tree.insert(self.saved_root, "end", text=account_name, open=False)

            if account_name in expanded_folders:
                self.tree.item(acc_node, open=True)

            for class_name, save_files in sorted(classes_dict.items()):
                class_node = self.tree.insert(acc_node, "end", text=class_name, open=False)

                if class_name in expanded_folders:
                    self.tree.item(class_node, open=True)

                def get_numerical_level_key(file_info):
                    match = re.search(r'\d+', file_info["display_name"])
                    return int(match.group()) if match else 0

                for file_info in sorted(save_files, key=get_numerical_level_key):
                    path_str = os.path.normpath(file_info["full_path"]).lower()
                    self.tracked_paths.add(path_str)
                    self.tree.insert(class_node, "end", text=file_info["display_name"],
                                     values=(file_info["full_path"], "saved"))

        temp_registry_backup = list(self.external_other_registry)
        self.external_other_registry.clear()

        for persistent_path in temp_registry_backup:
            self.add_external_file_to_other_view(persistent_path)

        for acc_node in self.tree.get_children(self.other_root):
            if self.tree.item(acc_node, "text") in expanded_folders:
                self.tree.item(acc_node, open=True)
            for class_node in self.tree.get_children(acc_node):
                if self.tree.item(class_node, "text") in expanded_folders:
                    self.tree.item(class_node, open=True)

    def add_external_file_to_other_view(self, absolute_file_path):
        path_str = os.path.normpath(absolute_file_path).lower()
        if path_str in self.tracked_paths: return

        self.tracked_paths.add(path_str)

        if absolute_file_path not in self.external_other_registry:
            self.external_other_registry.append(absolute_file_path)

        player_name, hero_class = self.manager.extract_metadata_from_external_file(absolute_file_path)
        file_title = os.path.splitext(os.path.basename(absolute_file_path))[0]

        target_acc_node = None
        for acc_node in self.tree.get_children(self.other_root):
            if self.tree.item(acc_node, "text") == player_name:
                target_acc_node = acc_node
                break
        if not target_acc_node: target_acc_node = self.tree.insert(self.other_root, "end", text=player_name, open=True)

        target_class_node = None
        for class_node in self.tree.get_children(target_acc_node):
            if self.tree.item(class_node, "text") == hero_class:
                target_class_node = class_node
                break
        if not target_class_node: target_class_node = self.tree.insert(target_acc_node, "end", text=hero_class,
                                                                       open=True)
        self.tree.insert(target_class_node, "end", text=file_title, values=(absolute_file_path, "other"))

    def handle_row_hover_highlight(self, event):
        item = self.tree.identify_row(event.y)
        if item != self.last_hovered_item:
            if self.last_hovered_item and self.tree.exists(self.last_hovered_item): self.tree.item(
                self.last_hovered_item, tags=())
            self.last_hovered_item = item
            if item:
                self.tree.item(item, tags=("hover",))
                self.tree.tag_configure("hover", background="#2a2a2b")

    def handle_double_click(self, event):
        """Routes selected sidebar nodes straight through the hardened validation gate."""
        selected_node = self.tree.selection()
        if not selected_node: return

        node_values = self.tree.item(selected_node[0], "values")
        if node_values and len(node_values) > 0:
            target_file_path = os.path.normpath(str(node_values[0]))

            if os.path.isfile(target_file_path):
                root = self.winfo_toplevel()
                root.process_incoming_file_ingestion(target_file_path)

    def process_drag_and_drop_file_ingestion(self, absolute_file_path):
        path_str = os.path.normpath(absolute_file_path)
        if not os.path.isfile(path_str):
            return False

        file_ext = os.path.splitext(path_str)[1].lower()
        if file_ext not in [".txt", ".json"]:
            messagebox.showerror("Ingestion Rejected",
                                 "Invalid File Type! The utility suite strictly processes authentic Warcraft III .txt logs or verified .json configurations.")
            return False

        try:
            if file_ext == ".txt":
                with open(path_str, "r", encoding="utf-8", errors="ignore") as f:
                    file_head = f.read(1500)

                if "function PreloadFiles" not in file_head and "call Preload" not in file_head:
                    messagebox.showerror("Ingestion Rejected",
                                         "Structural Validation Failed! This text file lacks the native Warcraft III Preload script headers.")
                    return False

            elif file_ext == ".json":
                import json
                with open(path_str, "r", encoding="utf-8") as f:
                    config_payload = json.load(f)

                required_keys = ["player_name", "hero_class", "inventory"]
                if not all(k in config_payload for k in required_keys):
                    messagebox.showerror("Ingestion Rejected",
                                         "Structural Validation Failed! The configuration JSON lacks critical character profile keys.")
                    return False

        except Exception as e:
            messagebox.showerror("Ingestion Error",
                                 f"An exception occurred while executing safety sieve verification rules: {e}")
            return False

        print(f"[DND INGESTION] Safety sieve passed perfectly for path: {path_str}")
        self.add_external_file_to_other_view(path_str)
        return True

    def display_context_right_click_menu(self, event):
        """Identifies the targeted node row beneath the mouse pointer and draws the pop-up panel."""
        targeted_node = self.tree.identify_row(event.y)
        if not targeted_node:
            return

        self.tree.selection_set(targeted_node)

        if targeted_node in [self.saved_root, self.other_root]:
            return

        self.context_menu.post(event.x_root, event.y_root)

    def execute_context_menu_deletion(self):
        selected_node = self.tree.selection()
        if not selected_node: return
        node_id = selected_node
        node_text = self.tree.item(node_id, "text")
        node_values = self.tree.item(node_id, "values")

        if node_values and len(node_values) > 0:
            target_path = os.path.normpath(str(node_values[0]))
            if os.path.isfile(target_path):
                if ask_dark_confirmation(self.winfo_toplevel(), "Confirm Deletion", f"Permanently delete profile file:\n'{node_text}'?"):
                    try:
                        os.remove(target_path)
                        if target_path in self.external_other_registry:
                            self.external_other_registry.remove(target_path)
                        self.refresh_saved_directory()
                    except Exception as e:
                        show_dark_alert(self.winfo_toplevel(), "Deletion Error", f"Failed to delete asset: {e}")
        else:
            discovered_file_paths = []
            def harvest_child_file_paths(parent_node):
                for child in self.tree.get_children(parent_node):
                    child_values = self.tree.item(child, "values")
                    if child_values and len(child_values) > 0:
                        discovered_file_paths.append(os.path.normpath(str(child_values[0])))
                    else:
                        harvest_child_file_paths(child)
            harvest_child_file_paths(node_id)

            if not discovered_file_paths:
                self.tree.delete(node_id)
                return

            if ask_dark_confirmation(self.winfo_toplevel(), "Confirm Group Deletion", f"Permanently delete folder '{node_text}' and all {len(discovered_file_paths)} files inside?"):
                try:
                    for target_file_path in discovered_file_paths:
                        if os.path.isfile(target_file_path):
                            os.remove(target_file_path)
                        if target_file_path in self.external_other_registry:
                            self.external_other_registry.remove(target_file_path)
                    self.refresh_saved_directory()
                except Exception as e:
                    show_dark_alert(self.winfo_toplevel(), "Deletion Error", f"Folder removal loop failed: {e}")