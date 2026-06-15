import tkinter as tk
import customtkinter as ctk
from typing import Dict, Callable, List

def btn(parent, t, text, cmd=None, variant="primary", w=140, h=36, **kw):
    kw.pop("height", None); kw.pop("width", None)
    colors = {
        "primary": t["accent"],  "success": t["green"],
        "danger":  t["red"],     "warning": t["orange"],
        "ghost":   t["card"],
    }
    fg = colors.get(variant, t["accent"])
    tc = "#FFFFFF" if variant != "ghost" else t["fg"]
    return ctk.CTkButton(
        parent, text=text, command=cmd,
        fg_color=fg, hover_color=t["hover"],
        text_color=tc, font=("Segoe UI", 13, "bold"),
        corner_radius=8, height=h, width=w, **kw
    )

def label(parent, t, text, size=12, bold=False, color=None, **kw):
    kw.pop("font", None)
    return ctk.CTkLabel(
        parent, text=text,
        font=("Segoe UI", size, "bold" if bold else "normal"),
        text_color=color or t["fg"], fg_color="transparent", **kw
    )

def section_title(parent, t, text):
    return ctk.CTkLabel(
        parent, text=text, font=("Segoe UI", 18, "bold"),
        text_color=t["fg"], fg_color="transparent"
    )

class StatCard(ctk.CTkFrame):
    def __init__(self, parent, t, lbl, val="--", icon="*", color=None):
        super().__init__(parent, fg_color=t["card"], corner_radius=12)
        self.grid_columnconfigure(0, weight=1)
        self._v = ctk.CTkLabel(
            self, text=val, font=("Segoe UI", 26, "bold"),
            text_color=color or t["accent"], fg_color="transparent"
        )
        ctk.CTkLabel(
            self, text=f"{icon}  {lbl}", font=("Segoe UI", 11),
            text_color=t["fg2"], fg_color="transparent"
        ).grid(row=0, column=0, padx=14, pady=(12, 0), sticky="w")
        self._v.grid(row=1, column=0, padx=14, pady=(0, 12), sticky="w")

    def set(self, v, color=None):
        self._v.configure(text=v)
        if color:
            self._v.configure(text_color=color)

class CheckRow(ctk.CTkFrame):
    def __init__(self, parent, t, lbl, desc="", size_text="--"):
        super().__init__(parent, fg_color=t["card"], corner_radius=8)
        self.grid_columnconfigure(1, weight=1)
        self._var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self, variable=self._var, text="",
            fg_color=t["accent"], border_color=t["border"],
            checkmark_color="#FFFFFF", width=24
        ).grid(row=0, column=0, rowspan=2, padx=12, pady=8)
        ctk.CTkLabel(
            self, text=lbl, font=("Segoe UI", 12, "bold"),
            text_color=t["fg"], fg_color="transparent", anchor="w"
        ).grid(row=0, column=1, sticky="ew", pady=(8, 0))
        ctk.CTkLabel(
            self, text=desc, font=("Segoe UI", 10),
            text_color=t["fg2"], fg_color="transparent", anchor="w"
        ).grid(row=1, column=1, sticky="ew", pady=(0, 8))
        self._sz = ctk.CTkLabel(
            self, text=size_text, font=("Segoe UI", 12, "bold"),
            text_color=t["accent"], fg_color="transparent", width=90, anchor="e"
        )
        self._sz.grid(row=0, column=2, rowspan=2, padx=12)

    def checked(self):
        return self._var.get()

    def set_size(self, text, color=None):
        self._sz.configure(text=text)
        if color:
            self._sz.configure(text_color=color)

class LogBox(ctk.CTkTextbox):
    def __init__(self, parent, t, **kw):
        kw.pop("fg_color", None)
        kw.pop("text_color", None)
        super().__init__(
            parent, fg_color=t["bg2"], text_color=t["fg"],
            font=("Consolas", 11), wrap="word", **kw
        )
        self.configure(state="disabled")

    def write(self, text):
        self.configure(state="normal")
        self.insert("end", text + "\n")
        self.see("end")
        self.configure(state="disabled")

    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")

def progress_bar(parent, t, **kw):
    kw.pop("progress_color", None)
    kw.pop("fg_color", None)
    return ctk.CTkProgressBar(
        parent, progress_color=t["accent"],
        fg_color=t["prog_bg"], height=6, corner_radius=3, **kw
    )
