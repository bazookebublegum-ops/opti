
import threading
import customtkinter as ctk
from ui.widgets import btn, section_title, label
import modules.registry_ops as ro
from pathlib import Path

class RegistryPage(ctk.CTkScrollableFrame):
    def __init__(self,parent,t,backup_dir:Path):
        super().__init__(parent,fg_color=t["bg"],scrollbar_button_color=t["border"])
        self._t=t; self._bdir=backup_dir; self._tweaks=[]
        self.grid_columnconfigure(0,weight=1); self._build()

    def _build(self):
        t=self._t
        section_title(self,t,"Registry Optimizer").grid(row=0,column=0,padx=20,pady=(20,2),sticky="w")
        label(self,t,"Safe reversible tweaks — every change is backed up automatically",color=t["fg2"]).grid(row=1,column=0,padx=20,pady=(0,12),sticky="w")
        top=ctk.CTkFrame(self,fg_color="transparent"); top.grid(row=2,column=0,padx=20,pady=4,sticky="ew")
        btn(top,t,"🔍  Scan",cmd=self._scan,variant="primary").pack(side="left")
        btn(top,t,"✅  Apply Selected",cmd=self._apply,variant="success").pack(side="left",padx=8)
        btn(top,t,"↩  Revert All",cmd=self._revert,variant="ghost").pack(side="left")
        self._status=label(top,t,"Click Scan to read current registry values",color=t["fg2"]); self._status.pack(side="left",padx=12)
        self._cf=ctk.CTkFrame(self,fg_color="transparent"); self._cf.grid(row=3,column=0,padx=20,pady=8,sticky="nsew"); self._cf.grid_columnconfigure(0,weight=1)

    def _scan(self):
        self._status.configure(text="Scanning…")
        def run():
            tweaks=ro.scan()
            self.after(0,lambda:self._fill(tweaks))
        threading.Thread(target=run,daemon=True).start()

    def _fill(self,tweaks):
        for w in self._cf.winfo_children(): w.destroy()
        self._tweaks=tweaks
        self._checks={}
        for i,tw in enumerate(tweaks):
            c=ctk.CTkFrame(self._cf,fg_color=self._t["card"],corner_radius=10)
            c.grid(row=i,column=0,padx=4,pady=4,sticky="ew"); c.grid_columnconfigure(1,weight=1)
            import tkinter as tk
            var=tk.BooleanVar(value=not tw.get("done",False))
            ctk.CTkCheckBox(c,variable=var,text="",fg_color=self._t["accent"],
                             border_color=self._t["border"],checkmark_color="#FFFFFF",width=24).grid(row=0,column=0,rowspan=2,padx=12,pady=8)
            self._checks[tw["id"]]=var
            ctk.CTkLabel(c,text=tw["label"],font=("Segoe UI",12,"bold"),text_color=self._t["fg"],fg_color="transparent",anchor="w").grid(row=0,column=1,padx=4,pady=(10,0),sticky="ew")
            ctk.CTkLabel(c,text=tw["desc"],font=("Segoe UI",10),text_color=self._t["fg2"],fg_color="transparent",anchor="w").grid(row=1,column=1,padx=4,pady=(0,10),sticky="ew")
            inf=ctk.CTkFrame(c,fg_color=self._t["bg2"],corner_radius=6)
            inf.grid(row=0,column=2,rowspan=2,padx=12,pady=8)
            cur=tw.get("current","?"); opt=tw["value"]
            ctk.CTkLabel(inf,text=f"Now: {cur}  →  {opt}",font=("Segoe UI",10),text_color=self._t["fg2"],fg_color="transparent").pack(padx=10,pady=6)
            done=tw.get("done",False)
            ctk.CTkLabel(c,text="✅ Done" if done else "⚡ Available",font=("Segoe UI",11,"bold"),
                         text_color=self._t["green"] if done else self._t["orange"],fg_color="transparent").grid(row=0,column=3,rowspan=2,padx=12)
        n=sum(1 for tw in tweaks if not tw.get("done"))
        self._status.configure(text=f"{n} tweaks available — {len(tweaks)} total")

    def _apply(self):
        sel=[tw for tw in self._tweaks if self._checks.get(tw["id"],type("X",(),{"get":lambda self:False})()).get()]
        if not sel: self._status.configure(text="Nothing selected"); return
        self._status.configure(text="Applying…")
        def run():
            ok=sum(ro.write_val(tw,tw["value"],self._bdir) for tw in sel)
            self.after(0,lambda:self._status.configure(text=f"✅ Applied {ok}/{len(sel)} tweaks"))
            self.after(600,self._scan)
        threading.Thread(target=run,daemon=True).start()

    def _revert(self):
        self._status.configure(text="Reverting…")
        def run():
            ok=sum(ro.revert_val(tw,self._bdir) for tw in self._tweaks)
            self.after(0,lambda:self._status.configure(text=f"↩ Reverted {ok} tweaks"))
            self.after(600,self._scan)
        threading.Thread(target=run,daemon=True).start()
