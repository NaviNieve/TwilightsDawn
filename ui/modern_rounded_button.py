import sys
import argparse
import tkinter as tk
import ctypes

class ModernRoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, bg_color, fg_color, width=160, height=38, radius=8):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], bd=0, highlightthickness=0)
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.radius = radius
        self.width = width
        self.height = height
        self.text = text
        self.draw_button_state(self.bg_color)

        self.bind("<Enter>", lambda e: self.draw_button_state(self.adjust_color_brightness(self.bg_color, 20)))
        self.bind("<Leave>", lambda e: self.draw_button_state(self.bg_color))
        self.bind("<Button-1>", lambda e: self.command())
        self.configure(cursor="hand2")

    def draw_button_state(self, color):
        self.delete("all")
        r = self.radius
        w = self.width
        h = self.height
        self.create_arc(0, 0, r * 2, r * 2, start=90, extent=90, fill=color, outline=color)
        self.create_arc(w - r * 2, 0, w, r * 2, start=0, extent=90, fill=color, outline=color)
        self.create_arc(0, h - r * 2, r * 2, h, start=180, extent=90, fill=color, outline=color)
        self.create_arc(w - r * 2, h - r * 2, w, h, start=270, extent=90, fill=color, outline=color)
        self.create_rectangle(r, 0, w - r, h, fill=color, outline=color)
        self.create_rectangle(0, r, w, h - r, fill=color, outline=color)
        self.create_text(w // 2, h // 2, text=self.text, fill=self.fg_color, font=("Segoe UI", 10, "bold"))

    def adjust_color_brightness(self, hex_color, factor):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        new_rgb = tuple(max(0, min(255, c + factor)) for c in rgb)
        return f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"