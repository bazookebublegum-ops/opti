import tkinter as tk
import customtkinter as ctk
from ui.widgets import btn, section_title, label

class SettingsPage(ctk.CTkScrollableFrame):
    def __init__(self, parent, t, config, on_theme):
        super().__init__(parent, fg_color=t["bg"], scrollbar_button_color=t["border"])
        self._t = t
        self._cfg = config
        self._on_theme = on_theme
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        t = self._t
        section_title(self, t, "Settings").grid(row=0, column=0, padx=20, pady=(20, 2), sticky="w")
        label(self, t, "Application preferences", color=t["fg2"]).grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")

        # Theme
        label(self, t, "Appearance", size=13, bold=True, color=t["fg2"]).grid(row=2, column=0, padx=20, pady=(8, 4), sticky="w")
        tc = ctk.CTkFrame(self, fg_color=t["card"], corner_radius=10)
        tc.grid(row=3, column=0, padx=20, pady=6, sticky="ew")
        label(tc, t, "Theme:", size=12, color=t["fg2"]).pack(side="left", padx=16, pady=14)
        self._tv = tk.StringVar(value=self._cfg.get("theme", "dark"))
        ctk.CTkRadioButton(tc, text="Dark",  variable=self._tv, value="dark",
                            fg_color=t["accent"], border_color=t["border"],
                            text_color=t["fg"], command=self._theme).pack(side="left", padx=12, pady=14)
        ctk.CTkRadioButton(tc, text="Light", variable=self._tv, value="light",
                            fg_color=t["accent"], border_color=t["border"],
                            text_color=t["fg"], command=self._theme).pack(side="left", padx=12, pady=14)

        # Safety
        label(self, t, "Safety", size=13, bold=True, color=t["fg2"]).grid(row=4, column=0, padx=20, pady=(16, 4), sticky="w")
        sf = ctk.CTkFrame(self, fg_color=t["card"], corner_radius=10)
        sf.grid(row=5, column=0, padx=20, pady=6, sticky="ew")
        sf.grid_columnconfigure(0, weight=1)
        self._svars = {}
        for i, (lbl2, key) in enumerate([
            ("Auto-backup before registry changes", "auto_backup"),
            ("Create restore point before changes", "auto_restore_point"),
            ("Confirm before deleting files",       "confirm_deletions"),
        ]):
            v = tk.BooleanVar(value=self._cfg.get(key, True))
            self._svars[key] = v
            ctk.CTkCheckBox(sf, text=lbl2, variable=v,
                             fg_color=t["accent"], border_color=t["border"],
                             checkmark_color="#FFFFFF", text_color=t["fg"],
                             command=lambda k=key, vv=v: self._cfg.set(k, vv.get())
                             ).grid(row=i, column=0, padx=16, pady=8, sticky="w")

        # Backup dir
        label(self, t, "Backup Directory", size=13, bold=True, color=t["fg2"]).grid(row=6, column=0, padx=20, pady=(16, 4), sticky="w")
        df = ctk.CTkFrame(self, fg_color=t["card"], corner_radius=10)
        df.grid(row=7, column=0, padx=20, pady=6, sticky="ew")
        df.grid_columnconfigure(1, weight=1)
        label(df, t, "Path:", size=11, color=t["fg2"]).grid(row=0, column=0, padx=14, pady=12)
        self._de = ctk.CTkEntry(df, fg_color=t["bg2"], text_color=t["fg"], border_color=t["border"])
        self._de.grid(row=0, column=1, padx=8, pady=12, sticky="ew")
        self._de.insert(0, self._cfg.get("backup_dir", ""))
        btn(df, t, "Save", cmd=self._save_dir, variant="primary", w=80, h=30).grid(row=0, column=2, padx=12, pady=12)

        self._status = label(self, t, "", color=t["green"])
        self._status.grid(row=8, column=0, padx=20, pady=8, sticky="w")

    def _theme(self):
        self._cfg.set("theme", self._tv.get())
        self._on_theme(self._tv.get())

    def _save_dir(self):
        self._cfg.set("backup_dir", self._de.get().strip())
        self._status.configure(text="Settings saved")
