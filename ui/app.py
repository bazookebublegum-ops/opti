"""
ui/app.py - Main application window (Python 3.14 compatible)
"""
import threading, time, json
import customtkinter as ctk
from pathlib import Path
from ui.theme import DARK, LIGHT, NAV, PAGE_TITLES
from ui.splash import Splash
from ui.sidebar import Sidebar
from ui.topbar import Topbar
from core.system_info import get_metrics
from modules.backup_mgr import BackupManager
from modules.reports import Reporter

class Config:
    def __init__(self, base):
        self._f = base / "config.json"
        self._d = {"theme":"dark","backup_dir":str(base/"backups"),"auto_backup":True,
                   "auto_restore_point":True,"confirm_deletions":True}
        if self._f.exists():
            try: self._d.update(json.loads(self._f.read_text()))
            except: pass
    def get(self, k, default=None): return self._d.get(k, default)
    def set(self, k, v):
        self._d[k]=v
        try: self._f.write_text(json.dumps(self._d, indent=2))
        except: pass

class App:
    def __init__(self, base_dir: Path, is_admin: bool):
        self.base  = base_dir
        self.admin = is_admin
        self.cfg   = Config(base_dir)
        ctk.set_appearance_mode("dark" if self.cfg.get("theme")=="dark" else "light")
        ctk.set_default_color_theme("blue")
        self.bm  = BackupManager(Path(self.cfg.get("backup_dir", str(base_dir/"backups"))))
        self.rep = Reporter(base_dir/"reports")
        self._pages = {}

    def run(self):
        self._root = ctk.CTk()
        self._root.title("Windows Optimizer Pro v2.0")
        self._root.geometry("1280x800")
        self._root.minsize(960, 640)
        t = DARK if self.cfg.get("theme")=="dark" else LIGHT
        self._root.configure(fg_color=t["bg"])
        self._root.withdraw()
        self._splash = Splash(self._root, on_done=self._ready)
        self._root.mainloop()

    def _ready(self):
        try: self._splash.destroy()
        except: pass
        self._build()
        self._root.deiconify()

    def _build(self):
        self._t = DARK if self.cfg.get("theme")=="dark" else LIGHT
        t = self._t
        self._root.configure(fg_color=t["bg"])
        self._root.grid_columnconfigure(1, weight=1)
        self._root.grid_rowconfigure(1, weight=1)

        self._sidebar = Sidebar(self._root, t, NAV, self._nav, "2.0")
        self._sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")

        self._topbar = Topbar(self._root, t, "2.0", self.admin, self._toggle_theme)
        self._topbar.grid(row=0, column=1, sticky="ew")

        self._content = ctk.CTkFrame(self._root, fg_color=t["bg"], corner_radius=0)
        self._content.grid(row=1, column=1, sticky="nsew")
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

        self._build_pages()
        self._nav("dashboard")
        threading.Thread(target=self._ticker, daemon=True).start()

    def _build_pages(self):
        t = self._t; c = self._content
        bdir = Path(self.cfg.get("backup_dir", str(self.base/"backups")))

        from ui.pages.dashboard    import DashboardPage
        from ui.pages.cleanup_page import CleanupPage
        from ui.pages.disk_page    import DiskPage
        from ui.pages.startup_page import StartupPage
        from ui.pages.registry_page import RegistryPage
        from ui.pages.network_page  import NetworkPage
        from ui.pages.gaming_page   import GamingPage
        from ui.pages.monitoring_page import MonitoringPage
        from ui.pages.reports_page  import ReportsPage
        from ui.pages.restore_page  import RestorePage
        from ui.pages.settings_page import SettingsPage

        self._pages = {
            "dashboard":  DashboardPage(c, t, get_metrics, self._smart_optimize),
            "cleanup":    CleanupPage(c, t),
            "disk":       DiskPage(c, t),
            "startup":    StartupPage(c, t),
            "registry":   RegistryPage(c, t, bdir),
            "network":    NetworkPage(c, t),
            "gaming":     GamingPage(c, t),
            "monitoring": MonitoringPage(c, t, get_metrics, self.cfg.get("monitoring_interval", 2)),
            "reports":    ReportsPage(c, t, self.rep),
            "restore":    RestorePage(c, t, self.bm),
            "settings":   SettingsPage(c, t, self.cfg, self._apply_theme),
        }
        for pg in self._pages.values():
            pg.grid(row=0, column=0, sticky="nsew")
            pg.grid_remove()

    def _nav(self, page_id):
        for pid, pg in self._pages.items():
            pg.grid() if pid == page_id else pg.grid_remove()
        self._sidebar.activate(page_id)
        self._topbar.set_title(PAGE_TITLES.get(page_id, page_id.title()))
        if page_id == "dashboard":
            self._pages["dashboard"].refresh()

    def _smart_optimize(self, pbar, slbl):
        def run():
            steps = [(0.15,"Scanning temp files..."),(0.35,"Reading registry..."),
                     (0.55,"Checking startup..."),(0.75,"Analysing disk..."),
                     (0.90,"Building report..."),(1.0,"Done!")]
            for v,msg in steps:
                time.sleep(0.5)
                self._root.after(0, lambda v=v,m=msg: (pbar.set(v), slbl.configure(text=m)))
            m = get_metrics()
            self.rep.save("Smart Optimization Report", [{"heading":"System Status","items":[
                {"key":"Score","value":f"{m['score']}/100 ({m['label']})"},
                {"key":"CPU",  "value":f"{m['cpu']:.0f}%"},
                {"key":"RAM",  "value":f"{m['ram']:.0f}%"},
                {"key":"Disk", "value":f"{m['disk']:.0f}%"},
            ]}])
        threading.Thread(target=run, daemon=True).start()

    def _toggle_theme(self):
        self._apply_theme("light" if self.cfg.get("theme")=="dark" else "dark")

    def _apply_theme(self, name):
        self.cfg.set("theme", name)
        ctk.set_appearance_mode("dark" if name=="dark" else "light")

    def _ticker(self):
        while True:
            try:
                m = get_metrics()
                txt = f"CPU {m['cpu']:.0f}%  RAM {m['ram']:.0f}%  Disk {m['disk']:.0f}%"
                self._root.after(0, lambda t=txt: self._topbar.set_info(t))
            except: pass
            time.sleep(5)
