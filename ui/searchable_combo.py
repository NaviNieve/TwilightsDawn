import tkinter as tk
from tkinter import ttk

_ACTIVE_TWILIGHT_COMBO_POPUP = None


class SearchableCombo(tk.Frame):
    def __init__(self, parent, values, default_val="", width=25):
        super().__init__(parent, bg="#1e1e1e")
        self.all_values = sorted(list(values))

        self.entry_var = tk.StringVar(value=default_val)

        self.drop_btn = tk.Button(self, text="▼", font=("Segoe UI", 7),
                                  bg="#2d2d30", fg="#d4d4d4", activebackground="#0a7b83",
                                  activeforeground="#ffffff", bd=0, cursor="hand2", width=2,
                                  command=self.toggle_dropdown_panel)
        self.drop_btn.pack(side=tk.RIGHT, fill=tk.Y)

        self.drop_btn.bind("<Enter>", lambda e: self.drop_btn.configure(bg="#3e3e42", fg="#00ffcc"))
        self.drop_btn.bind("<Leave>", lambda e: self.drop_btn.configure(bg="#2d2d30", fg="#d4d4d4"))

        self.entry = tk.Entry(self, textvariable=self.entry_var, width=width,
                              bg="#252526", fg="#ffffff", insertbackground="#00ffcc",
                              bd=1, relief=tk.SOLID, font=("Segoe UI", 10), justify=tk.CENTER,
                              highlightbackground="#2d2d30", highlightcolor="#00ffcc", highlightthickness=1)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.entry.bind("<FocusIn>", lambda e: self.entry.configure(highlightbackground="#00ffcc"))
        self.entry.bind("<FocusOut>", lambda e: self.entry.configure(highlightbackground="#2d2d30"))

        self.entry.bind("<Enter>", lambda e: self.entry.configure(
            highlightbackground="#00ffcc") if self.focus_get() != self.entry else None)
        self.entry.bind("<Leave>", lambda e: self.entry.configure(
            highlightbackground="#2d2d30") if self.focus_get() != self.entry else None)

        self.entry.bind("<KeyRelease>", self.on_key_release_handler)
        self.entry.bind("<KeyPress>", self.on_key_press_intercept)

        self.popup = None
        self.listbox = None
        self.choices = []

        self.winfo_toplevel().bind("<Button-1>", self.handle_global_click_dismiss, add="+")

    def toggle_dropdown_panel(self):
        self.entry.focus_set()
        if self.popup and self.popup.winfo_exists():
            self.close_dropdown_panel()
        else:
            self.display_dropdown_panel(self.all_values)

    def display_dropdown_panel(self, choices):
        global _ACTIVE_TWILIGHT_COMBO_POPUP
        if _ACTIVE_TWILIGHT_COMBO_POPUP and _ACTIVE_TWILIGHT_COMBO_POPUP != self:
            try:
                _ACTIVE_TWILIGHT_COMBO_POPUP.close_dropdown_panel()
            except Exception:
                pass

        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()

        if not choices: return
        self.choices = choices
        _ACTIVE_TWILIGHT_COMBO_POPUP = self

        self.popup = tk.Toplevel(self)
        self.popup.wm_overrideredirect(True)
        self.popup.configure(bg="#252526")

        visible_rows = min(8, len(choices))
        row_height = 20

        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        w = self.winfo_width()
        h = (visible_rows * row_height) + 4
        self.popup.wm_geometry(f"{w}x{h}+{x}+{y}")

        frame = tk.Frame(self.popup, bg="#252526", highlightbackground="#0a7b83", highlightthickness=1)
        frame.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(frame, bg="#252526", fg="#d4d4d4", selectbackground="#0a7b83",
                                  selectforeground="#ffffff", bd=0, highlightthickness=0,
                                  font=("Segoe UI", 9), activestyle="none", height=visible_rows)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(2, 0), pady=2)

        sb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.listbox.yview, style="Dark.Vertical.TScrollbar")
        self.listbox.configure(yscrollcommand=sb.set)
        if len(choices) > 8:
            sb.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 2), pady=2)

        for item in choices: self.listbox.insert(tk.END, item)
        self.listbox.bind("<ButtonRelease-1>",
                          lambda e: self.confirm_selection(self.listbox.get(self.listbox.nearest(e.y))))
        self.listbox.bind("<Motion>", self.handle_listbox_hover_tracking)

    def handle_listbox_hover_tracking(self, event):
        index = self.listbox.nearest(event.y)
        if index >= 0 and self.listbox:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)

    def handle_global_click_dismiss(self, event):
        """FIX 2: Closes the list view overlay instantly if clicking outside this component."""
        if not self.popup or not self.popup.winfo_exists():
            return

        click_widget = event.widget

        if click_widget == self.entry or click_widget == self.drop_btn:
            return

        if self.popup and (click_widget == self.listbox or click_widget.master == self.popup):
            return

        self.close_dropdown_panel()

    def on_key_press_intercept(self, event):
        if event.keysym in ["Up", "Down"]: return "break"

    def on_key_release_handler(self, event):
        if self.popup and self.popup.winfo_exists() and self.listbox:
            current_selection = self.listbox.curselection()
            current_index = current_selection[0] if current_selection else -1

            if event.keysym == "Down":
                next_index = min(len(self.choices) - 1, current_index + 1)
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(next_index)
                self.listbox.see(next_index)
                return
            elif event.keysym == "Up":
                next_index = max(0, current_index - 1) if current_index > 0 else 0
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(next_index)
                self.listbox.see(next_index)
                return
            elif event.keysym == "Return":
                if current_index >= 0: self.confirm_selection(self.listbox.get(current_index))
                return

        typed_text = self.entry_var.get().lower()
        if not typed_text:
            self.close_dropdown_panel()
            return
        filtered = [v for v in self.all_values if typed_text in v.lower()]
        if filtered:
            self.display_dropdown_panel(filtered)
        else:
            self.close_dropdown_panel()

    def confirm_selection(self, selected_text):
        self.entry_var.set(selected_text)
        self.close_dropdown_panel()

    def close_dropdown_panel(self):
        global _ACTIVE_TWILIGHT_COMBO_POPUP
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None
        if _ACTIVE_TWILIGHT_COMBO_POPUP == self: _ACTIVE_TWILIGHT_COMBO_POPUP = None

    def get(self):
        return self.entry_var.get()