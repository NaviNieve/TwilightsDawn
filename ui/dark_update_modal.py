import tkinter as tk
import webbrowser

class DarkUpdateModal(tk.Toplevel):
    def __init__(self, parent, latest_version, release_url):
        super().__init__(parent, bg="#1e1e1e")
        self.release_url = release_url

        self.withdraw()
        self.wm_overrideredirect(True)

        outer_frame = tk.Frame(self, bg="#1e1e1e", highlightbackground="#00ffcc", highlightthickness=1)
        outer_frame.pack(fill=tk.BOTH, expand=True)

        title_lbl = tk.Label(outer_frame, text=" 🚀 UPDATE DETECTED", font=("Segoe UI", 9, "bold"), bg="#252526",
                             fg="#00ffcc", anchor="w", pady=4)
        title_lbl.pack(fill=tk.X)

        msg = f"A new version ({latest_version}) of the Profile Suite is available!\n\nWould you like to open the GitHub releases page to download the latest executable installer?"
        msg_lbl = tk.Label(outer_frame, text=msg, font=("Segoe UI", 10), bg="#1e1e1e", fg="#ffffff", wraplength=340,
                           justify=tk.CENTER, pady=20)
        msg_lbl.pack(fill=tk.BOTH, expand=True, padx=20)

        btn_frame = tk.Frame(outer_frame, bg="#1e1e1e")
        btn_frame.pack(fill=tk.X, pady=(0, 15))

        yes_btn = tk.Button(btn_frame, text="Download Update", font=("Segoe UI", 9, "bold"), bg="#0a7b83", fg="#ffffff",
                            activebackground="#0e9aa2", activeforeground="#ffffff", bd=0, padx=15, pady=6,
                            cursor="hand2", command=self.open_url_and_close)
        yes_btn.pack(side=tk.LEFT, expand=True, padx=(30, 10))
        yes_btn.bind("<Enter>", lambda e: yes_btn.configure(bg="#0e9aa2"))
        yes_btn.bind("<Leave>", lambda e: yes_btn.configure(bg="#0a7b83"))

        no_btn = tk.Button(btn_frame, text="Remind Me Later", font=("Segoe UI", 9, "bold"), bg="#2d2d30", fg="#d4d4d4",
                           activebackground="#3e3e42", activeforeground="#ffffff", bd=0, padx=15, pady=6,
                           cursor="hand2", command=self.destroy)
        no_btn.pack(side=tk.RIGHT, expand=True, padx=(10, 30))
        no_btn.bind("<Enter>", lambda e: no_btn.configure(bg="#3e3e42", fg="#ffffff"))
        no_btn.bind("<Leave>", lambda e: no_btn.configure(bg="#2d2d30", fg="#d4d4d4"))

        self.update_idletasks()
        w, h = 380, 170
        px = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
        py = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{px}+{py}")

        self.deiconify()
        self.grab_set()
        self.focus_set()
        parent.wait_window(self)

    def open_url_and_close(self):
        try:
            webbrowser.open(self.release_url)
        except Exception:
            pass
        self.destroy()


def show_dark_update_popup(parent, latest_version, release_url):
    DarkUpdateModal(parent, latest_version, release_url)