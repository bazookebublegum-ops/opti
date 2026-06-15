import os
import customtkinter as ctk
from ui.widgets import btn, section_title, label

class ReportsPage(ctk.CTkFrame):
    def __init__(self,parent,t,reporter):
        super().__init__(parent,fg_color=t["bg"],corner_radius=0)
        self._t=t; self._rep=reporter
        self.grid_columnconfigure(0,weight=1); self.grid_rowconfigure(2,weight=1)
        self._build(); self._refresh()

    def _build(self):
        t=self._t
        section_title(self,t,"Reports").grid(row=0,column=0,padx=20,pady=(20,2),sticky="w")
        label(self,t,"HTML and TXT reports generated after each operation",color=t["fg2"]).grid(row=1,column=0,padx=20,pady=(0,10),sticky="w")
        top=ctk.CTkFrame(self,fg_color="transparent"); top.grid(row=2,column=0,padx=20,pady=4,sticky="ew")
        btn(top,t,"Refresh",cmd=self._refresh,variant="ghost").pack(side="left")
        btn(top,t,"Open Folder",cmd=self._open_folder,variant="ghost").pack(side="left",padx=8)
        self._list=ctk.CTkScrollableFrame(self,fg_color=t["card"],scrollbar_button_color=t["border"])
        self._list.grid(row=3,column=0,padx=20,pady=(8,20),sticky="nsew")
        self.grid_rowconfigure(3,weight=1)

    def _refresh(self):
        for w in self._list.winfo_children(): w.destroy()
        reps=self._rep.list_reports()
        if not reps:
            label(self._list,self._t,"No reports yet. Run an optimization first.",color=self._t["fg2"]).pack(padx=20,pady=20)
            return
        for r in reps:
            row=ctk.CTkFrame(self._list,fg_color=self._t["bg2"],corner_radius=8)
            row.pack(fill="x",padx=8,pady=3); row.grid_columnconfigure(1,weight=1)
            ctk.CTkLabel(row,text=r["fmt"],font=("Segoe UI",10,"bold"),text_color=self._t["accent"],
                          fg_color=self._t["card"],corner_radius=4,width=44).grid(row=0,column=0,padx=8,pady=8)
            ctk.CTkLabel(row,text=r["name"],font=("Segoe UI",11),text_color=self._t["fg"],
                          fg_color="transparent",anchor="w").grid(row=0,column=1,sticky="w")
            ctk.CTkLabel(row,text=f"{r['modified']}  |  {r['size_kb']} KB",font=("Segoe UI",9),
                          text_color=self._t["fg3"],fg_color="transparent").grid(row=0,column=2,padx=8)
            btn(row,self._t,"Open",cmd=lambda p=r["path"]:self._open(p),variant="ghost",w=70,h=26).grid(row=0,column=3,padx=8,pady=6)

    def _open(self,path):
        try: os.startfile(path)
        except: pass

    def _open_folder(self):
        try: os.startfile(str(self._rep.dir))
        except: pass
