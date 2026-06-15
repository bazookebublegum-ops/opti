import threading
import customtkinter as ctk
from ui.widgets import btn, section_title, label
import modules.gaming_ops as go

class GamingPage(ctk.CTkScrollableFrame):
    def __init__(self,parent,t):
        super().__init__(parent,fg_color=t["bg"],scrollbar_button_color=t["border"])
        self._t=t; self.grid_columnconfigure(0,weight=1); self._build()

    def _build(self):
        t=self._t
        section_title(self,t,"Gaming Optimizer").grid(row=0,column=0,padx=20,pady=(20,2),sticky="w")
        label(self,t,"Check and optimize Windows gaming performance settings",color=t["fg2"]).grid(row=1,column=0,padx=20,pady=(0,12),sticky="w")
        top=ctk.CTkFrame(self,fg_color="transparent"); top.grid(row=2,column=0,padx=20,pady=4,sticky="ew")
        btn(top,t,"Scan",cmd=self._scan,variant="primary").pack(side="left")
        btn(top,t,"Enable Game Mode",cmd=self._game_mode,variant="success").pack(side="left",padx=8)
        btn(top,t,"High Performance Power",cmd=self._power,variant="warning").pack(side="left")
        self._status=label(top,t,"",color=t["fg2"]); self._status.pack(side="left",padx=12)
        self._rf=ctk.CTkFrame(self,fg_color="transparent")
        self._rf.grid(row=3,column=0,padx=20,pady=8,sticky="nsew")
        self._rf.grid_columnconfigure((0,1),weight=1)

    def _scan(self):
        self._status.configure(text="Scanning...")
        for w in self._rf.winfo_children(): w.destroy()
        def run():
            s=go.get_status()
            self.after(0,lambda: self._fill(s))
        threading.Thread(target=run,daemon=True).start()

    def _fill(self,s):
        t=self._t
        checks=[
            ("Game Mode",   s["game_mode"].get("status","?"), 0,0),
            ("HAGS",        s["hags"].get("status","?"),       0,1),
            ("Power Plan",  s["power"].get("plan","?"),        1,0),
        ]
        for txt,val,r,c in checks:
            card=ctk.CTkFrame(self._rf,fg_color=t["card"],corner_radius=10)
            card.grid(row=r,column=c,padx=6,pady=6,sticky="ew")
            label(card,t,txt,size=11,color=t["fg2"]).pack(padx=14,pady=(12,0),anchor="w")
            col=t["green"] if "enabled" in val.lower() or "high" in val.lower() else t["orange"]
            label(card,t,val,size=16,bold=True,color=col).pack(padx=14,pady=(0,12),anchor="w")
        rc=ctk.CTkFrame(self._rf,fg_color=t["card"],corner_radius=10)
        rc.grid(row=2,column=0,columnspan=2,padx=6,pady=6,sticky="ew")
        label(rc,t,"Recommendations",size=13,bold=True).pack(padx=14,pady=(12,6),anchor="w")
        for rec in s["recommendations"]:
            label(rc,t,f"  - {rec}",size=11,color=t["fg2"]).pack(padx=14,pady=2,anchor="w")
        ctk.CTkFrame(rc,fg_color="transparent",height=8).pack()
        if s["processes"]:
            pc=ctk.CTkFrame(self._rf,fg_color=t["card"],corner_radius=10)
            pc.grid(row=3,column=0,columnspan=2,padx=6,pady=6,sticky="ew")
            label(pc,t,"Top CPU Processes",size=13,bold=True).pack(padx=14,pady=(12,6),anchor="w")
            for p in s["processes"][:8]:
                label(pc,t,f"  {p['name']:<32} CPU: {p['cpu']:.1f}%",size=10,color=t["fg2"]).pack(padx=14,pady=1,anchor="w")
            ctk.CTkFrame(pc,fg_color="transparent",height=8).pack()
        self._status.configure(text=f"Scan complete - {len(s['recommendations'])} recommendation(s)")

    def _game_mode(self):
        ok=go.enable_game_mode()
        self._status.configure(text="Game Mode enabled" if ok else "Failed (try as Admin)")

    def _power(self):
        ok=go.set_high_perf()
        self._status.configure(text="High Performance power plan set" if ok else "Failed")
