
import threading, time
import customtkinter as ctk
from ui.widgets import StatCard, btn, section_title, progress_bar, label

class DashboardPage(ctk.CTkScrollableFrame):
    def __init__(self,parent,t,metrics_fn,smart_fn):
        super().__init__(parent,fg_color=t["bg"],scrollbar_button_color=t["border"])
        self._t=t; self._mfn=metrics_fn; self._sfn=smart_fn
        self.grid_columnconfigure((0,1,2,3),weight=1)
        self._build(); self.refresh()

    def _build(self):
        t=self._t
        section_title(self,t,"System Dashboard").grid(row=0,column=0,columnspan=4,padx=20,pady=(20,2),sticky="w")
        label(self,t,"Real-time performance overview",color=t["fg2"]).grid(row=1,column=0,columnspan=4,padx=20,pady=(0,14),sticky="w")
        self._c_cpu  =StatCard(self,t,"CPU Usage",  icon="🖥",color=t["accent"])
        self._c_ram  =StatCard(self,t,"RAM Usage",  icon="💾",color=t["accent2"])
        self._c_disk =StatCard(self,t,"Disk C:",    icon="💿",color=t["orange"])
        self._c_net  =StatCard(self,t,"Network ↓",  icon="🌐",color=t["green"])
        for col,c in enumerate([self._c_cpu,self._c_ram,self._c_disk,self._c_net]):
            c.grid(row=2,column=col,padx=8,pady=6,sticky="nsew")
        # Bars
        bf=ctk.CTkFrame(self,fg_color="transparent"); bf.grid(row=3,column=0,columnspan=3,padx=8,pady=6,sticky="nsew")
        bf.grid_columnconfigure(0,weight=1)
        self._bars={}
        for i,(lbl,key) in enumerate([("CPU %","cpu"),("RAM %","ram"),("Disk %","disk")]):
            row=ctk.CTkFrame(bf,fg_color=t["card"],corner_radius=8); row.grid(row=i,column=0,padx=4,pady=3,sticky="ew")
            row.grid_columnconfigure(1,weight=1)
            ctk.CTkLabel(row,text=lbl,font=("Segoe UI",11),text_color=t["fg2"],fg_color="transparent",width=60).grid(row=0,column=0,padx=10,pady=8)
            pb=ctk.CTkProgressBar(row,progress_color=t["accent"],fg_color=t["prog_bg"],height=8,corner_radius=4); pb.grid(row=0,column=1,padx=8,sticky="ew"); pb.set(0)
            vl=ctk.CTkLabel(row,text="0%",font=("Segoe UI",11,"bold"),text_color=t["fg"],fg_color="transparent",width=44); vl.grid(row=0,column=2,padx=8)
            self._bars[key]=(pb,vl)
        # Score card
        sc=ctk.CTkFrame(self,fg_color=t["card"],corner_radius=12); sc.grid(row=3,column=3,padx=8,pady=6,sticky="nsew"); sc.grid_columnconfigure(0,weight=1)
        label(sc,t,"System Health",size=11,color=t["fg2"]).grid(row=0,column=0,padx=14,pady=(14,0))
        self._score_val=ctk.CTkLabel(sc,text="—",font=("Segoe UI",44,"bold"),text_color=t["green"],fg_color="transparent"); self._score_val.grid(row=1,column=0)
        self._score_lbl=ctk.CTkLabel(sc,text="Calculating…",font=("Segoe UI",12),text_color=t["fg2"],fg_color="transparent"); self._score_lbl.grid(row=2,column=0,pady=(0,14))
        # Buttons
        ctk.CTkFrame(self,fg_color=t["border"],height=1).grid(row=4,column=0,columnspan=4,padx=20,pady=10,sticky="ew")
        bf2=ctk.CTkFrame(self,fg_color="transparent"); bf2.grid(row=5,column=0,columnspan=4,padx=20,sticky="ew")
        btn(bf2,t,"⚡  Start Smart Optimization",cmd=self._smart,variant="primary",w=260,h=44).pack(side="left")
        btn(bf2,t,"🔄  Refresh",cmd=self.refresh,variant="ghost",w=110,h=44).pack(side="left",padx=10)
        # Results
        self._res=ctk.CTkFrame(self,fg_color=t["card"],corner_radius=10); self._res.grid(row=6,column=0,columnspan=4,padx=20,pady=10,sticky="ew")
        self._res_lbl=ctk.CTkLabel(self._res,text="Press 'Start Smart Optimization' to analyze your system.",
                                    font=("Segoe UI",12),text_color=t["fg2"],fg_color="transparent",wraplength=700,justify="left")
        self._res_lbl.pack(padx=20,pady=14,anchor="w")
        self._res_bar=ctk.CTkProgressBar(self._res,progress_color=t["accent"],fg_color=t["prog_bg"],height=5)
        self._res_bar.pack(fill="x",padx=20,pady=(0,12)); self._res_bar.set(0)

    def refresh(self):
        threading.Thread(target=lambda:self.after(0,lambda m=self._mfn():self._apply(m)),daemon=True).start()

    def _apply(self,m):
        self._c_cpu.set(f"{m['cpu']:.0f}%", self._col(m["cpu"]))
        self._c_ram.set(f"{m['ram_used']} GB / {m['ram_total']} GB", self._col(m["ram"]))
        self._c_disk.set(f"{m['disk_used']} / {m['disk_total']} GB", self._col(m["disk"]))
        self._c_net.set(f"{m['net_recv']} MB")
        for key,(pb,vl) in self._bars.items():
            pct=m.get(key,0); pb.set(pct/100); vl.configure(text=f"{pct:.0f}%")
            pb.configure(progress_color=self._col(pct))
        sc=m["score"]
        self._score_val.configure(text=str(sc),text_color=self._col(100-sc))
        self._score_lbl.configure(text=m["label"])

    def _col(self,pct):
        t=self._t
        if pct<60: return t["green"]
        if pct<80: return t["orange"]
        return t["red"]

    def _smart(self):
        self._res_bar.set(0); self._res_lbl.configure(text="🔍 Analyzing system…")
        self._sfn(self._res_bar, self._res_lbl)
