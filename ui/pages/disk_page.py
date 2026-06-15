import threading
import customtkinter as ctk
from ui.widgets import btn, section_title, label
import modules.disk_analyzer as da

class DiskPage(ctk.CTkFrame):
    def __init__(self,parent,t):
        super().__init__(parent,fg_color=t["bg"],corner_radius=0)
        self._t=t
        self.grid_columnconfigure(0,weight=1); self.grid_rowconfigure(5,weight=1)
        self._build()

    def _build(self):
        t=self._t
        section_title(self,t,"Disk Analyzer").grid(row=0,column=0,padx=20,pady=(20,2),sticky="w")
        label(self,t,"Find large/old/junk/duplicate files — read-only, nothing deleted automatically",color=t["fg2"]).grid(row=1,column=0,padx=20,pady=(0,10),sticky="w")
        cf=ctk.CTkFrame(self,fg_color=t["card"],corner_radius=10)
        cf.grid(row=2,column=0,padx=20,pady=6,sticky="ew")
        cf.grid_columnconfigure(1,weight=1)
        label(cf,t,"Path:",size=11,color=t["fg2"]).grid(row=0,column=0,padx=12,pady=10)
        self._path=ctk.CTkEntry(cf,placeholder_text="C:\\Users",fg_color=t["bg2"],text_color=t["fg"],border_color=t["border"],width=260)
        self._path.grid(row=0,column=1,padx=6,pady=10,sticky="ew")
        self._path.insert(0,"C:\\Users")
        import tkinter as tk
        self._mode=tk.StringVar(value="large")
        for col,(lbl2,val) in enumerate([("Largest Files","large"),("Old (1yr+)","old"),("Junk Files","junk"),("Duplicates","dupes")]):
            ctk.CTkRadioButton(cf,text=lbl2,variable=self._mode,value=val,font=("Segoe UI",11),
                                text_color=t["fg"],fg_color=t["accent"],border_color=t["border"]).grid(row=0,column=2+col,padx=8)
        self._scan_btn=btn(cf,t,"Scan",cmd=self._scan,variant="primary",w=80,h=34)
        self._scan_btn.grid(row=0,column=6,padx=8,pady=10)
        self._stop_btn=btn(cf,t,"Stop",cmd=self._stop,variant="danger",w=70,h=34)
        self._stop_btn.grid(row=0,column=7,padx=4,pady=10)
        self._stop_btn.configure(state="disabled")
        self._bar=ctk.CTkProgressBar(self,progress_color=t["accent"],fg_color=t["prog_bg"],height=5)
        self._bar.grid(row=3,column=0,padx=20,pady=4,sticky="ew"); self._bar.set(0)
        self._status=label(self,t,"Select scan type and click Scan",color=t["fg2"])
        self._status.grid(row=4,column=0,padx=20,pady=(0,4),sticky="w")
        hdr=ctk.CTkFrame(self,fg_color=t["bg2"],corner_radius=0)
        hdr.grid(row=5,column=0,padx=20,pady=(4,0),sticky="ew")
        self._cols=[("Name",200),("Size",90),("Date",100),("Path",500)]
        for txt,w in self._cols:
            ctk.CTkLabel(hdr,text=txt,font=("Segoe UI",10,"bold"),text_color=t["fg2"],fg_color="transparent",width=w,anchor="w").pack(side="left",padx=4,pady=5)
        self._tbl=ctk.CTkScrollableFrame(self,fg_color=t["card"],scrollbar_button_color=t["border"])
        self._tbl.grid(row=6,column=0,padx=20,pady=(0,20),sticky="nsew")
        self.grid_rowconfigure(6,weight=1)

    def _scan(self):
        root=self._path.get().strip() or "C:\\Users"
        mode=self._mode.get()
        for w in self._tbl.winfo_children(): w.destroy()
        self._bar.set(0)
        self._scan_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")
        self._status.configure(text=f"Scanning {root}...")
        def prog(n,found):
            self.after(0,lambda: self._status.configure(text=f"Scanned {n:,} items, found {found:,}..."))
        def run():
            try:
                if   mode=="large": rows=[[r["name"],da.fmt(r["size"]),r["date"],r["path"]] for r in da.large_files(root,cb=prog)]
                elif mode=="old":   rows=[[r["name"],da.fmt(r["size"]),r["date"],r["path"]] for r in da.old_files(root,cb=prog)]
                elif mode=="junk":  rows=[[r["name"],da.fmt(r["size"]),r["ext"], r["path"]] for r in da.junk_files(root)]
                else:
                    rows=[]
                    for g in da.duplicates(root,cb=prog):
                        for f in g: rows.append([f["name"],da.fmt(f["size"]),f["hash"],f["path"]])
            except Exception as e:
                rows=[]
                self.after(0,lambda: self._status.configure(text=f"Error: {e}"))
            self.after(0,lambda: self._fill(rows))
        threading.Thread(target=run,daemon=True).start()

    def _stop(self):
        self._stop_btn.configure(state="disabled")
        self._status.configure(text="Stopped")
        self._scan_btn.configure(state="normal")

    def _fill(self,rows):
        for w in self._tbl.winfo_children(): w.destroy()
        widths=[w for _,w in self._cols]
        for i,row in enumerate(rows):
            bg=self._t["card"] if i%2==0 else self._t["bg2"]
            for j,(cell,w) in enumerate(zip(row,widths)):
                ctk.CTkLabel(self._tbl,text=str(cell)[:90],font=("Segoe UI",10),
                              text_color=self._t["fg"],fg_color=bg,width=w,anchor="w").grid(row=i,column=j,padx=2,pady=1,sticky="ew")
        self._bar.set(1)
        self._scan_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")
        self._status.configure(text=f"Found {len(rows)} items (nothing deleted automatically)")
