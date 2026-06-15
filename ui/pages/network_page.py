import threading
import tkinter as tk
import customtkinter as ctk
from ui.widgets import btn, section_title, label, LogBox
import modules.network_ops as no

class NetworkPage(ctk.CTkScrollableFrame):
    def __init__(self, parent, t):
        super().__init__(parent, fg_color=t["bg"], scrollbar_button_color=t["border"])
        self._t = t
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        t = self._t
        section_title(self, t, "Network Tools").grid(row=0, column=0, padx=20, pady=(20, 2), sticky="w")
        label(self, t, "Flush DNS, reset Winsock, set DNS profiles, ping hosts", color=t["fg2"]).grid(
            row=1, column=0, padx=20, pady=(0, 14), sticky="w")

        # Quick op buttons
        opf = ctk.CTkFrame(self, fg_color=t["card"], corner_radius=10)
        opf.grid(row=2, column=0, padx=20, pady=6, sticky="ew")
        opf.grid_columnconfigure((0, 1, 2, 3), weight=1)
        ops = [
            ("Flush DNS",    no.flush_dns,    "primary"),
            ("Reset Winsock",no.reset_winsock,"warning"),
            ("Reset TCP/IP", no.reset_tcpip,  "warning"),
            ("Renew IP",     no.renew_ip,     "ghost"),
        ]
        for col, (lbl2, fn, var) in enumerate(ops):
            btn(opf, t, lbl2, cmd=lambda f=fn: self._run(f), variant=var, h=38).grid(
                row=0, column=col, padx=8, pady=10, sticky="ew")

        # Log output
        self._log = LogBox(self, t, height=130)
        self._log.grid(row=3, column=0, padx=20, pady=8, sticky="ew")

        # DNS Profiles
        df = ctk.CTkFrame(self, fg_color=t["card"], corner_radius=10)
        df.grid(row=4, column=0, padx=20, pady=8, sticky="ew")
        label(df, t, "DNS Profiles", size=13, bold=True).grid(
            row=0, column=0, columnspan=6, padx=16, pady=(12, 8), sticky="w")
        self._dns_v = tk.StringVar(value="Cloudflare")
        for col, name in enumerate(no.DNS):
            p, s = no.DNS[name]
            ctk.CTkRadioButton(
                df, text=f"{name}\n{p}", variable=self._dns_v, value=name,
                font=("Segoe UI", 10), text_color=t["fg"],
                fg_color=t["accent"], border_color=t["border"]
            ).grid(row=1, column=col, padx=16, pady=(0, 10), sticky="w")
        af = ctk.CTkFrame(df, fg_color="transparent")
        af.grid(row=2, column=0, columnspan=6, padx=14, pady=(0, 12), sticky="ew")
        label(af, t, "Adapter:", size=11, color=t["fg2"]).pack(side="left")
        self._adapt = ctk.CTkEntry(
            af, placeholder_text="e.g. Wi-Fi or Ethernet", width=200,
            fg_color=t["bg2"], text_color=t["fg"], border_color=t["border"])
        self._adapt.pack(side="left", padx=8)
        btn(af, t, "Apply DNS", cmd=self._set_dns, variant="primary", w=110, h=32).pack(side="left")

        # Ping test
        pf = ctk.CTkFrame(self, fg_color=t["card"], corner_radius=10)
        pf.grid(row=5, column=0, padx=20, pady=8, sticky="ew")
        label(pf, t, "Ping Test", size=13, bold=True).grid(
            row=0, column=0, columnspan=4, padx=16, pady=(12, 6), sticky="w")
        self._ping_e = ctk.CTkEntry(
            pf, placeholder_text="Host", width=200,
            fg_color=t["bg2"], text_color=t["fg"], border_color=t["border"])
        self._ping_e.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")
        self._ping_e.insert(0, "8.8.8.8")
        btn(pf, t, "Ping", cmd=self._ping, variant="primary", w=90, h=30).grid(
            row=1, column=1, padx=4, pady=(0, 12))
        self._ping_r = label(pf, t, "", color=t["fg2"])
        self._ping_r.grid(row=1, column=2, padx=16, pady=(0, 12), sticky="w")

        # Show adapters
        btn(self, t, "Show Network Adapters", cmd=self._show_adapters,
            variant="ghost", w=220, h=34).grid(row=6, column=0, padx=20, pady=6, sticky="w")

    def _run(self, fn):
        self._log.write(f"Running {fn.__name__}...")
        def run():
            r = fn()
            mark = "OK" if r["ok"] else "FAIL"
            out = r["out"] or r["err"]
            self.after(0, lambda: self._log.write(f"[{mark}] {r['label']}: {out[:120]}"))
        threading.Thread(target=run, daemon=True).start()

    def _set_dns(self):
        name = self._dns_v.get()
        p, s = no.DNS[name]
        adapter = self._adapt.get().strip()
        if not adapter:
            self._log.write("Enter adapter name first (e.g. Wi-Fi or Ethernet)")
            return
        self._log.write(f"Setting {name} DNS on {adapter}...")
        def run():
            r = no.set_dns(adapter, p, s)
            mark = "OK" if r["ok"] else "FAIL"
            self.after(0, lambda: self._log.write(f"[{mark}] {name} DNS ({p}, {s})"))
        threading.Thread(target=run, daemon=True).start()

    def _ping(self):
        host = self._ping_e.get().strip() or "8.8.8.8"
        self._ping_r.configure(text="Pinging...", text_color=self._t["fg2"])
        def run():
            r = no.ping(host)
            if r["ok"] and r["avg_ms"]:
                txt = f"OK  {host} -- avg {r['avg_ms']:.0f} ms"
                col = self._t["green"]
            else:
                txt = f"FAIL  {host} -- unreachable"
                col = self._t["red"]
            self.after(0, lambda: self._ping_r.configure(text=txt, text_color=col))
        threading.Thread(target=run, daemon=True).start()

    def _show_adapters(self):
        adapters = no.get_adapters()
        if not adapters:
            self._log.write("No adapters found (install psutil)")
            return
        self._log.write("-- Network Adapters --")
        for a in adapters:
            st = "UP" if a["up"] else "DOWN"
            self._log.write(f"  {a['name']:<24} {st}  IP: {a['ip'] or '--'}  {a['speed']} Mbps")
