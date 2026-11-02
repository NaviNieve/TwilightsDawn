import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import ctypes
import webbrowser

from tkinterdnd2 import TkinterDnD, DND_FILES
from modules.updater import check_for_updates_async
from ui.dark_about_modal import show_dark_about_popup

CURRENT_VERSION = "v1.0.1"

class TwilightDawnUI(TkinterDnD.Tk):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager

        self.title(f"Twilights Dawn - {CURRENT_VERSION}")
        self.geometry("1120x710")
        self.configure(bg="#1e1e1e")

        watermark_bar = tk.Frame(self, bg="#1e1e1e", height=26,
                                 highlightbackground="#2d2d30", highlightthickness=1)
        watermark_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)

        watermark_inner = tk.Frame(watermark_bar, bg="#1e1e1e", pady=3, padx=15)
        watermark_inner.pack(fill=tk.X)

        self.version_area_container = tk.Frame(watermark_inner, bg="#1e1e1e")
        self.version_area_container.pack(side=tk.LEFT)

        version_lbl = tk.Label(self.version_area_container, text=f"Application Build: {CURRENT_VERSION}",
                               font=("Segoe UI", 8, "bold"), bg="#1e1e1e", fg="#555555")
        version_lbl.pack(side=tk.LEFT)

        right_actions_frame = tk.Frame(watermark_inner, bg="#1e1e1e")
        right_actions_frame.pack(side=tk.RIGHT)

        about_link = tk.Label(right_actions_frame, text="About App",
                              font=("Segoe UI", 8, "bold", "underline"), bg="#1e1e1e", fg="#0a7b83", cursor="hand2")
        about_link.pack(side=tk.LEFT, padx=10)
        about_link.bind("<Enter>", lambda e: about_link.configure(fg="#00ffcc"))
        about_link.bind("<Leave>", lambda e: about_link.configure(fg="#0a7b83"))
        about_link.bind("<Button-1>", lambda e: show_dark_about_popup(self, CURRENT_VERSION))

        dot_lbl = tk.Label(right_actions_frame, text="•", font=("Segoe UI", 8), bg="#1e1e1e", fg="#333333")
        dot_lbl.pack(side=tk.LEFT)

        donate_link = tk.Label(right_actions_frame, text="Support Dev (Donate)",
                               font=("Segoe UI", 8, "bold", "underline"), bg="#1e1e1e", fg="#0a7b83", cursor="hand2")
        donate_link.pack(side=tk.LEFT, padx=10)
        donate_link.bind("<Enter>", lambda e: donate_link.configure(fg="#00ffcc"))
        donate_link.bind("<Leave>", lambda e: donate_link.configure(fg="#0a7b83"))
        donate_link.bind("<Button-1>", lambda e: webbrowser.open("https://ko-fi.com/navinieve"))

        check_for_updates_async(self, CURRENT_VERSION)

        def handle_secure_dropped_file_payload(event):
            """
                    Intercepts drag-and-drop strings dropped onto the user window,
                    cleans format encapsulation characters, and runs dark-themed alert checks.
                    """
            raw_dropped_data = event.data.strip()
            if not raw_dropped_data: return

            clean_path = raw_dropped_data
            if clean_path.startswith('{') and clean_path.endswith('}'):
                clean_path = clean_path[1:-1]

            clean_path = os.path.normpath(clean_path)

            success = self.process_incoming_file_ingestion(clean_path)

            if success:
                print(f"[DRAG-N-DROP] Successfully ingested save code file path resource: {clean_path}")

        try:
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", handle_secure_dropped_file_payload)
        except Exception as e:
            print(f"[-] DND initialization deferred or missing package binaries: {e}")

        try:
            self.update()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(1)),
                ctypes.sizeof(ctypes.c_int)
            )
        except Exception:
            pass

        from ui.sidebar import SidebarFolderViewer
        self.sidebar = SidebarFolderViewer(self, self.manager, self.load_profile_into_editor)

        self.main_container = tk.Frame(self, bg="#1e1e1e")
        self.main_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        def process_clipboard_file_paste(event):
            try:
                raw_clipboard_data = self.clipboard_get()
                if not raw_clipboard_data:
                    return

                clean_path = raw_clipboard_data.strip('{}临"\'\r\n\t ')
                if os.path.isfile(clean_path):
                    print(f"[CLIPBOARD INGESTION] Discovered file path target: {clean_path}")
                    if self.sidebar.process_drag_and_drop_file_ingestion(clean_path):
                        self.load_profile_into_editor(clean_path)
            except Exception:
                pass

        self.bind("<Control-v>", process_clipboard_file_paste)
        self.bind("<Control-V>", process_clipboard_file_paste)

        self.initialize_welcome_dashboard_screen()

    def initialize_welcome_dashboard_screen(self):
        for widget in self.main_container.winfo_children(): widget.destroy()
        welcome_frame = tk.Frame(self.main_container, bg="#1e1e1e")
        welcome_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        title_label = tk.Label(welcome_frame, text="TWILIGHT DAWN", font=("Segoe UI", 26, "bold"), bg="#1e1e1e",
                               fg="#00ffcc")
        title_label.pack(pady=(0, 15))

        subtitle = tk.Label(welcome_frame,
                            text="Select a character save file profile on the left side tree,\nor choose an initialization option below to begin editing.",
                            font=("Segoe UI", 10), bg="#1e1e1e", fg="#888888", justify=tk.CENTER)
        subtitle.pack(pady=(0, 35))

        from ui.modern_rounded_button import ModernRoundedButton
        btn_frame = tk.Frame(welcome_frame, bg="#1e1e1e")
        btn_frame.pack()

        ModernRoundedButton(btn_frame, text="📂 Open Save", command=lambda: self.trigger_file_browser_panel(),
                            bg_color="#0a7b83", fg_color="#ffffff").pack(side=tk.LEFT, padx=15)
        ModernRoundedButton(btn_frame, text="🛠️ Open Editor", command=lambda: self.launch_blank_editor_panel(),
                            bg_color="#2d2d30", fg_color="#d4d4d4").pack(side=tk.LEFT, padx=15)

    def trigger_file_browser_panel(self):
        """Launches a dark-mode aligned file explorer supporting both native save text and serialized JSON sheets."""
        from tkinter import filedialog

        target_path = filedialog.askopenfilename(
            parent=self.winfo_toplevel(),
            title="📂 SELECT WARCRAFT III SAVE PROFILE",
            filetypes=[
                ("Warcraft III Save Formats", "*.txt *.json"),
                ("Raw Text Logs (*.txt)", "*.txt"),
                ("Serialized Profile Sheets (*.json)", "*.json"),
                ("All Available Formats", "*.*")
            ]
        )
        if target_path:
            self.process_incoming_file_ingestion(target_path)

    def launch_blank_editor_panel(self):
        from ui.editor import ProfileEditorPanel
        for widget in self.main_container.winfo_children(): widget.destroy()
        self.editor = ProfileEditorPanel(self.main_container, self.manager, initial_data=None,
                                         on_close_callback=self.initialize_welcome_dashboard_screen)

    def load_profile_into_editor(self, absolute_file_path):
        """
        Dynamically routes file payloads based on extension profiles.
        Bypasses decryption for .json configs while processing .txt logs natively.
        """
        self.sidebar.add_external_file_to_other_view(absolute_file_path)
        import json

        if absolute_file_path.lower().endswith('.json'):
            print(f"[JSON LOADER] Reading pre-decrypted config matrix directly: {absolute_file_path}")
            with open(absolute_file_path, "r", encoding="utf-8") as f:
                decrypted_data = json.load(f)
        else:
            from modules.decrypt_save import SaveParserUtility
            decoder = SaveParserUtility()
            decoder.export_to_json(file_path=absolute_file_path)

            cfg_path = "configs/config.json" if os.path.exists("configs") else "config.json"
            with open(cfg_path, "r", encoding="utf-8") as f:
                decrypted_data = json.load(f)

        from ui.editor import ProfileEditorPanel
        for widget in self.main_container.winfo_children():
            widget.destroy()

        self.editor = ProfileEditorPanel(self.main_container, self.manager, initial_data=decrypted_data,
                                         on_close_callback=self.initialize_welcome_dashboard_screen)


    def inject_dynamic_update_alert_link(self, target_github_release_url):
        """
        Natively materializes an interactive 'Update now!' hyperlink text node
        directly next to the application version tag ONLY when an update is available.
        """
        gap_lbl = tk.Label(self.version_area_container, text="   ", font=("Segoe UI", 8), bg="#1e1e1e")
        gap_lbl.pack(side=tk.LEFT)

        update_alert_link = tk.Label(self.version_area_container, text="Update now!",
                                     font=("Segoe UI", 8, "bold", "underline"), bg="#1e1e1e", fg="#cc3333",
                                     cursor="hand2")
        update_alert_link.pack(side=tk.LEFT)

        update_alert_link.bind("<Enter>", lambda e: update_alert_link.configure(fg="#ff3333"))
        update_alert_link.bind("<Leave>", lambda e: update_alert_link.configure(fg="#cc3333"))

        update_alert_link.bind("<Button-1>", lambda e: webbrowser.open(target_github_release_url))

    def process_incoming_file_ingestion(self, file_path):
        """
        Natively inspects incoming files using a thread-safe validation sieve.
        Rejects malformed formats using dark-themed alerts before they hit your file tree or editor canvas.
        """
        import os, json
        from ui.dark_modal import show_dark_alert

        file_path = os.path.normpath(file_path)
        if not os.path.isfile(file_path):
            return False

        if file_path.lower().endswith('.json'):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    parsed_payload = json.load(f)

                required_keys = ["player_name", "hero_class", "experience", "checkpoint_zone"]
                if not all(key in parsed_payload for key in required_keys):
                    show_dark_alert(self.winfo_toplevel(), "Malformed Profile",
                                    "Validation Failure:\nThe selected JSON data file lacks the core parameter keys required by the editor.")
                    return False

            except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as err:
                show_dark_alert(self.winfo_toplevel(), "Parsing Crash",
                                f"JSON Decoding Mismatch:\nFile structure is invalid or corrupt.\n\nDetails: {err}")
                return False

        elif file_path.lower().endswith('.txt'):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                if "-l " not in content and not re.search(r'Preload\(\s*"[^"]*-', content):
                    show_dark_alert(self.winfo_toplevel(), "Invalid Format",
                                    "Validation Failure:\nThe text file contains no recognizable Warcraft III load strings or profile code blocks.")
                    return False
            except Exception as err:
                show_dark_alert(self.winfo_toplevel(), "Reading Error",
                                f"Failed to open targeted text asset log:\n{err}")
                return False

        else:
            show_dark_alert(self.winfo_toplevel(), "Extension Rejected",
                            "The tool profile suite restricts file intakes exclusively to .txt or .json variants.")
            return False

        try:
            if file_path not in self.sidebar.external_other_registry:
                is_native_save = "CustomGames" in file_path or "Twilight" in file_path
                if not is_native_save:
                    self.sidebar.external_other_registry.append(file_path)

            self.sidebar.refresh_saved_directory()

            self.load_profile_into_editor(file_path)
            return True
        except Exception as err:
            print(f"[-] Editor loading fail: {err}")
            return False