import customtkinter as ctk
from ui.widgets import btn, section_title, label
from pathlib import Path

class RestorePage(ctk.CTkFrame):
    def __init__(self,parent,t,backup_mgr):
        super().__init__(parent,fg_color=t["bg"],corner_radius=0)
        self._t=t; self._bm=backup_mgr
        self.grid_columnconfigure(0,weight=1); self.grid_rowconfigure(2,weight=1)
        self._build(); self._refresh()

    def _build(self):
        t=self._t
        section_title(self,t,"Restore Center").grid(row=0,column=0,padx=20,pady=(20,2),sticky="w")
        label(self,t,"Restore registry keys from automatic backups",color=t["fg2"]).grid(row=1,column=0,padx=20,pady=(0,10),sticky="w")
        top=ctk.CTkFrame(self,fg_color="transparent"); top.grid(row=2,column=0,padx=20,pady=4,sticky="ew")
        btn(top,t,"Refresh",cmd=self._refresh,variant="ghost").pack(side="left")
        btn(top,t,"Create Restore Point",cmd=self._restore_pt,variant="primary").pack(side="left",padx=8)
        self._status=label(top,t,"",color=t["fg2"]); self._status.pack(side="left",padx=12)
        self._list=ctk.CTkScrollableFrame(self,fg_color=t["card"],scrollbar_button_color=t["border"])
        self._list.grid(row=3,column=0,padx=20,pady=(8,20),sticky="nsew")
        self.grid_rowconfigure(3,weight=1)

    def _refresh(self):
        for w in self._list.winfo_children(): w.destroy()
        backups=self._bm.list_backups()
        if not backups:
            label(self._list,self._t,"No backups yet.",color=self._t["fg2"]).pack(padx=20,pady=20)
            self._status.configure(text="No backups found")
            return
        for b in backups:
            row=ctk.CTkFrame(self._list,fg_color=self._t["bg2"],corner_radius=8)
            row.pack(fill="x",padx=8,pady=3); row.grid_columnconfigure(1,weight=1)
            ext=b["name"].split(".")[-1].upper()
            ctk.CTkLabel(row,text=ext,font=("Segoe UI",9,"bold"),text_color=self._t["accent"],
                          fg_color=self._t["card"],corner_radius=4,width=40).grid(row=0,column=0,padx=8,pady=8)
            ctk.CTkLabel(row,text=b["name"][:60],font=("Segoe UI",11),text_color=self._t["fg"],
                          fg_color="transparent",anchor="w").grid(row=0,column=1,sticky="w")
            ctk.CTkLabel(row,text=f"{b['modified']}  |  {b['size_kb']} KB",font=("Segoe UI",9),
                          text_color=self._t["fg3"],fg_color="transparent").grid(row=0,column=2,padx=8)
            if b["name"].endswith(".reg"):
                btn(row,self._t,"Restore",cmd=lambda p=b["path"]:self._restore_reg(p),
                    variant="warning",w=80,h=26).grid(row=0,column=3,padx=8,pady=6)
        self._status.configure(text=f"{len(backups)} backup(s) available")

    def _restore_reg(self,path):
        ok=self._bm.restore_reg(Path(path))
        self._status.configure(text="Restored successfully" if ok else "Restore failed")

    def _restore_pt(self):
        self._status.configure(text="Creating restore point...")
        import threading
        def run():
            ok=self._bm.create_restore_point()
            self.after(0,lambda: self._status.configure(text="Restore point created" if ok else "Failed (may need admin or System Protection enabled)"))
        threading.Thread(target=run,daemon=True).start()
