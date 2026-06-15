
import threading
import customtkinter as ctk
from ui.widgets import btn, section_title, label
import modules.startup_mgr as sm

class StartupPage(ctk.CTkFrame):
    def __init__(self,parent,t):
        super().__init__(parent,fg_color=t["bg"],corner_radius=0)
        self._t=t; self._entries=[]; self._wrows=[]
        self.grid_columnconfigure(0,weight=1); self.grid_rowconfigure(3,weight=1)
        self._build(); self._load()

    def _build(self):
        t=self._t
        section_title(self,t,"Startup Manager").grid(row=0,column=0,padx=20,pady=(20,2),sticky="w")
        label(self,t,"Manage programs that run at Windows startup",color=t["fg2"]).grid(row=1,column=0,padx=20,pady=(0,10),sticky="w")
        top=ctk.CTkFrame(self,fg_color="transparent"); top.grid(row=2,column=0,padx=20,pady=4,sticky="ew")
        btn(top,t,"🔄  Refresh",cmd=self._load,variant="primary").pack(side="left")
        self._status=label(top,t,"",color=t["fg2"]); self._status.pack(side="left",padx=12)
        # Header
        hdr=ctk.CTkFrame(self,fg_color=t["bg2"],corner_radius=0)
        hdr.grid(row=3,column=0,padx=20,pady=(6,0),sticky="ew")
        for txt,w in [("Name",200),("Source",90),("Path",360),("Status",80),("Action",100)]:
            ctk.CTkLabel(hdr,text=txt,font=("Segoe UI",10,"bold"),text_color=t["fg2"],fg_color="transparent",width=w,anchor="w").pack(side="left",padx=4,pady=5)
        self._list=ctk.CTkScrollableFrame(self,fg_color=t["card"],scrollbar_button_color=t["border"])
        self._list.grid(row=4,column=0,padx=20,pady=(0,20),sticky="nsew")
        self.grid_rowconfigure(4,weight=1)

    def _load(self):
        for w in self._wrows:
            for ww in w:
                try: ww.destroy()
                except: pass
        self._wrows.clear()
        self._status.configure(text="Scanning…")
        def run():
            entries=sm.get_entries()
            self.after(0,lambda:self._fill(entries))
        threading.Thread(target=run,daemon=True).start()

    def _fill(self,entries):
        self._entries=entries
        for i,e in enumerate(entries):
            bg=self._t["card"] if i%2==0 else self._t["bg2"]
            nc=self._t["orange"] if e.get("optional") else self._t["fg"]
            row=[]
            for txt,w,col in [(e["name"][:28],200,nc),(e["hive"],90,self._t["fg2"]),
                               (e["path"][:55],360,self._t["fg3"])]:
                lb=ctk.CTkLabel(self._list,text=txt,font=("Segoe UI",11),text_color=col,fg_color=bg,width=w,anchor="w")
                lb.grid(row=i,column=len(row),padx=2,pady=2,sticky="ew"); row.append(lb)
            sc=self._t["green"] if e.get("enabled") else self._t["fg3"]
            st_lb=ctk.CTkLabel(self._list,text="Enabled" if e.get("enabled") else "Disabled",
                                font=("Segoe UI",11),text_color=sc,fg_color=bg,width=80,anchor="w")
            st_lb.grid(row=i,column=3,padx=2,pady=2,sticky="ew"); row.append(st_lb)
            ab=btn(self._list,self._t,"Disable" if e.get("enabled") else "Enable",
                   cmd=lambda en=e,sl=st_lb:self._toggle(en,sl),
                   variant="warning" if e.get("enabled") else "success",w=88,h=26)
            ab.grid(row=i,column=4,padx=4,pady=2); row.append(ab)
            self._wrows.append(row)
        self._status.configure(text=f"{len(entries)} startup entries found")

    def _toggle(self,entry,st_lb):
        if entry.get("enabled"):
            ok=sm.disable(entry)
            if ok: entry["enabled"]=False; st_lb.configure(text="Disabled",text_color=self._t["fg3"])
        else:
            ok=sm.enable(entry)
            if ok: entry["enabled"]=True; st_lb.configure(text="Enabled",text_color=self._t["green"])
