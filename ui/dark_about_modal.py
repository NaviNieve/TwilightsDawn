import tkinter as tk
import ctypes
import webbrowser

class DarkAboutModal(tk.Toplevel):
    def __init__(self, parent, current_version):
        super().__init__(parent, bg="#1e1e1e")
        self.withdraw()
        self.wm_overrideredirect(True)

        outer_frame = tk.Frame(self, bg="#1e1e1e", highlightbackground="#00ffcc", highlightthickness=1)
        outer_frame.pack(fill=tk.BOTH, expand=True)

        title_lbl = tk.Label(outer_frame, text=" 📜 APPLICATION ATTRIBUTES", font=("Segoe UI", 9, "bold"),
                             bg="#252526", fg="#00ffcc", anchor="w", pady=4)
        title_lbl.pack(fill=tk.X)

        name_lbl = tk.Label(outer_frame, text="Twilights Dawn", font=("Segoe UI", 12, "bold"),
                            bg="#1e1e1e", fg="#00ffcc", pady=10)
        name_lbl.pack(fill=tk.X)

        version_lbl = tk.Label(outer_frame, text=f"Version: {current_version}", font=("Segoe UI", 10, "bold"),
                               bg="#1e1e1e", fg="#ffffff", justify=tk.CENTER)
        version_lbl.pack(fill=tk.X, pady=2)

        dev_lbl = tk.Label(outer_frame, text="Developer: Joshua Smith", font=("Segoe UI", 10, "bold"),
                           bg="#1e1e1e", fg="#ffffff", justify=tk.CENTER)
        dev_lbl.pack(fill=tk.X, pady=2)

        repo_btn = tk.Button(outer_frame, text="Github", font=("Segoe UI", 9, "bold"),
                                bg="#2d2d30", fg="#00ffcc", activebackground="#0a7b83", activeforeground="#ffffff",
                                bd=0, padx=15, pady=4, cursor="hand2",
                                command=lambda: webbrowser.open("https://github.com/NaviNieve/TwilightsDawn/"))
        repo_btn.pack(pady=(5, 10))
        repo_btn.bind("<Enter>", lambda e: repo_btn.configure(bg="#3e3e42"))
        repo_btn.bind("<Leave>", lambda e: repo_btn.configure(bg="#2d2d30"))

        licence_btn = tk.Button(outer_frame, text="Licence", font=("Segoe UI", 9, "bold"),
                               bg="#2d2d30", fg="#00ffcc", activebackground="#0a7b83", activeforeground="#ffffff",
                               bd=0, padx=15, pady=4, cursor="hand2",
                               command=lambda: webbrowser.open("https://github.com/NaviNieve/TwilightsDawn/LICENSE"))
        licence_btn.pack(pady=(5, 10))
        licence_btn.bind("<Enter>", lambda e: licence_btn.configure(bg="#3e3e42"))
        licence_btn.bind("<Leave>", lambda e: licence_btn.configure(bg="#2d2d30"))

        donate_btn = tk.Button(outer_frame, text="💝 Support Development (Donate)", font=("Segoe UI", 9, "bold"),
                               bg="#2d2d30", fg="#00ffcc", activebackground="#0a7b83", activeforeground="#ffffff",
                               bd=0, padx=15, pady=4, cursor="hand2",
                               command=lambda: webbrowser.open("https://ko-fi.com/navinieve"))
        donate_btn.pack(pady=(5, 10))
        donate_btn.bind("<Enter>", lambda e: donate_btn.configure(bg="#3e3e42"))
        donate_btn.bind("<Leave>", lambda e: donate_btn.configure(bg="#2d2d30"))

        close_btn = tk.Button(outer_frame, text="Close", font=("Segoe UI", 9, "bold"),
                              bg="#2d2d30", fg="#ffffff", activebackground="#cc3333", activeforeground="#ffffff",
                              bd=0, padx=25, pady=5, cursor="hand2", command=self.destroy)
        close_btn.pack(pady=(5, 15))
        close_btn.bind("<Enter>", lambda e: close_btn.configure(bg="#3e3e42", fg="#ff3333"))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(bg="#2d2d30", fg="#ffffff"))

        self.update_idletasks()
        w, h = 400, 300
        px = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
        py = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{px}+{py}")

        self.deiconify()
        self.grab_set()
        self.focus_set()
        parent.wait_window(self)


def show_dark_about_popup(parent, current_version):
    DarkAboutModal(parent, current_version)