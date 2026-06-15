
import threading
import customtkinter as ctk
from ui.widgets import CheckRow, btn, section_title, label
from modules.cleanup import CATS, scan_all, clean_cat, fmt

class CleanupPage(ctk.CTkScrollableFrame):
    def __init__(self,parent,t):
        super().__init__(parent,fg_color=t["bg"],scrollbar_button_color=t["border"])
        self._t=t; self._rows={}; self._scan=[]
        self.grid_columnconfigure(0,weight=1)
        self._build()

    def _build(self):
        t=self._t
        section_title(self,t,"System Cleanup").grid(row=0,column=0,padx=20,pady=(20,2),sticky="w")
        label(self,t,"Scan and safely remove temporary files, caches and junk",color=t["fg2"]).grid(row=1,column=0,padx=20,pady=(0,12),sticky="w")
        top=ctk.CTkFrame(self,fg_color="transparent"); top.grid(row=2,column=0,padx=20,pady=4,sticky="ew")
        self._scan_btn=btn(top,t,"🔍  Scan",cmd=self._do_scan,variant="primary")
        self._scan_btn.pack(side="left")
        self._clean_btn=btn(top,t,"🧹  Clean Selected",cmd=self._do_clean,variant="success")
        self._clean_btn.pack(side="left",padx=8); self._clean_btn.configure(state="disabled")
        self._total=ctk.CTkLabel(top,text="",font=("Segoe UI",12,"bold"),text_color=t["accent"],fg_color="transparent")
        self._total.pack(side="right")
        self._bar=ctk.CTkProgressBar(self,progress_color=t["accent"],fg_color=t["prog_bg"],height=5)
        self._bar.grid(row=3,column=0,padx=20,pady=4,sticky="ew"); self._bar.set(0)
        self._status=label(self,t,"Click Scan to analyse disk usage",color=t["fg2"])
        self._status.grid(row=4,column=0,padx=20,pady=(0,8),sticky="w")
        cf=ctk.CTkFrame(self,fg_color="transparent"); cf.grid(row=5,column=0,padx=20,pady=4,sticky="nsew")
        cf.grid_columnconfigure((0,1),weight=1)
        for i,cat in enumerate(CATS):
            row=CheckRow(cf,t,cat["label"],cat.get("desc",""))
            row.grid(row=i//2,column=i%2,padx=5,pady=4,sticky="ew")
            self._rows[cat["id"]]=row

    def _do_scan(self):
        self._scan_btn.configure(state="disabled",text="Scanning…")
        self._clean_btn.configure(state="disabled"); self._bar.set(0)
        def run():
            results=scan_all(cb=lambda d,total,r: self.after(0,lambda d=d,total=total,r=r: self._on_prog(d,total,r)))
            self.after(0,lambda:self._on_scan_done(results))
        threading.Thread(target=run,daemon=True).start()

    def _on_prog(self,done,total,r):
        self._bar.set(done/total)
        row=self._rows.get(r["id"])
        if row:
            col=self._t["orange"] if r["bytes"]>0 else self._t["fg3"]
            row.set_size(fmt(r["bytes"]),col)
        self._status.configure(text=f"Scanned: {r['label']} — {fmt(r['bytes'])}")

    def _on_scan_done(self,results):
        self._scan=results
        total=sum(r["bytes"] for r in results)
        self._total.configure(text=f"Total: {fmt(total)}")
        self._scan_btn.configure(state="normal",text="🔍  Scan")
        self._clean_btn.configure(state="normal")
        self._bar.set(1)
        self._status.configure(text=f"Scan complete — {fmt(total)} can be freed")

    def _do_clean(self):
        sel=[c for c in CATS if self._rows.get(c["id"],None) and self._rows[c["id"]].checked()]
        if not sel: self._status.configure(text="No categories selected"); return
        self._clean_btn.configure(state="disabled",text="Cleaning…")
        self._scan_btn.configure(state="disabled"); self._bar.set(0)
        def run():
            freed=0; deleted=0
            for i,cat in enumerate(sel):
                r=clean_cat(cat)
                freed+=r["freed"]; deleted+=r["deleted"]
                self.after(0,lambda i=i,cat=cat,r=r: (
                    self._bar.set((i+1)/len(sel)),
                    self._rows.get(cat["id"],type("X",(),{"set_size":lambda *a,**k:None})()).set_size(f"-{fmt(r['freed'])}",self._t["green"])
                ))
            self.after(0,lambda:self._on_clean_done(freed,deleted))
        threading.Thread(target=run,daemon=True).start()

    def _on_clean_done(self,freed,deleted):
        self._status.configure(text=f"✅  Deleted {deleted} files — freed {fmt(freed)}")
        self._clean_btn.configure(state="normal",text="🧹  Clean Selected")
        self._scan_btn.configure(state="normal"); self._bar.set(1)
        self._total.configure(text="")
        for row in self._rows.values(): row.set_size("—")
