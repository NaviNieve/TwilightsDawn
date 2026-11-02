import tkinter as tk
import ctypes

class DarkModalPopup(tk.Toplevel):
    def __init__(self, parent, title, message, is_confirmation=False):
        super().__init__(parent, bg="#1e1e1e")
        self.result = False

        self.withdraw()
        self.wm_overrideredirect(True)

        outer_frame = tk.Frame(self, bg="#1e1e1e", highlightbackground="#00ffcc", highlightthickness=1)
        outer_frame.pack(fill=tk.BOTH, expand=True)

        title_lbl = tk.Label(outer_frame, text=f" 🛡️ {title.upper()}", font=("Segoe UI", 9, "bold"), bg="#252526", fg="#00ffcc", anchor="w", pady=4)
        title_lbl.pack(fill=tk.X)

        msg_lbl = tk.Label(outer_frame, text=message, font=("Segoe UI", 10), bg="#1e1e1e", fg="#ffffff",
                           wraplength=340, justify=tk.CENTER, pady=20)
        msg_lbl.pack(fill=tk.BOTH, expand=True, padx=20)

        btn_frame = tk.Frame(outer_frame, bg="#1e1e1e")
        btn_frame.pack(fill=tk.X, pady=(0, 15))

        if is_confirmation:
            yes_btn = tk.Button(btn_frame, text="Confirm", font=("Segoe UI", 9, "bold"), bg="#0a7b83", fg="#ffffff", activebackground="#0e9aa2", activeforeground="#ffffff", bd=0, padx=20, pady=6, cursor="hand2", command=self.action_confirm)
            yes_btn.pack(side=tk.LEFT, expand=True, padx=(30, 10))
            yes_btn.bind("<Enter>", lambda e: yes_btn.configure(bg="#0e9aa2"))
            yes_btn.bind("<Leave>", lambda e: yes_btn.configure(bg="#0a7b83"))

            no_btn = tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 9, "bold"), bg="#2d2d30", fg="#d4d4d4", activebackground="#3e3e42", activeforeground="#ffffff", bd=0, padx=20, pady=6, cursor="hand2", command=self.action_cancel)
            no_btn.pack(side=tk.RIGHT, expand=True, padx=(10, 30))
            no_btn.bind("<Enter>", lambda e: no_btn.configure(bg="#3e3e42", fg="#ffffff"))
            no_btn.bind("<Leave>", lambda e: no_btn.configure(bg="#2d2d30", fg="#d4d4d4"))
        else:
            ok_btn = tk.Button(btn_frame, text="Acknowledge", font=("Segoe UI", 9, "bold"), bg="#2d2d30", fg="#00ffcc", activebackground="#0a7b83", activeforeground="#ffffff", bd=0, padx=30, pady=6, cursor="hand2", command=self.action_confirm)
            ok_btn.pack(anchor=tk.CENTER)
            ok_btn.bind("<Enter>", lambda e: ok_btn.configure(bg="#3e3e42"))
            ok_btn.bind("<Leave>", lambda e: ok_btn.configure(bg="#2d2d30"))

        self.update_idletasks()

        req_width = self.winfo_reqwidth()
        req_height = self.winfo_reqheight()

        w = max(380, req_width)
        h = max(160, req_height)

        px = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
        py = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{px}+{py}")

        self.deiconify()
        self.grab_set()
        self.focus_set()
        parent.wait_window(self)

    def action_confirm(self):
        self.result = True
        self.destroy()

    def action_cancel(self):
        self.result = False
        self.destroy()


def show_dark_alert(parent, title, message):
    DarkModalPopup(parent, title, message, is_confirmation=False)


def ask_dark_confirmation(parent, title, message):
    popup = DarkModalPopup(parent, title, message, is_confirmation=True)
    return popup.result