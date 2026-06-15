"""
Monitoring page — pure CTkProgressBar bars, zero tk.Canvas, Python 3.14 safe.
"""
import threading, time
import customtkinter as ctk
from ui.widgets import section_title, label

class MonitoringPage(ctk.CTkFrame):
    def __init__(self,parent,t,metrics_fn,interval=2):
        super().__init__(parent,fg_color=t["bg"],corner_radius=0)
        self._t=t; self._mfn=metrics_fn; self._iv=interval; self._running=False
        self._vals={}; self._bars={}
        self.grid_columnconfigure((0,1),weight=1)
        self.grid_rowconfigure(2,weight=1); self.grid_rowconfigure(3,weight=1)
        self._build(); self.start()

    def _build(self):
        t=self._t
        section_title(self,t,"Real-Time Monitoring").grid(row=0,column=0,columnspan=2,padx=20,pady=(20,2),sticky="w")
        label(self,t,"Live metrics updated every 2 seconds",color=t["fg2"]).grid(row=1,column=0,columnspan=2,padx=20,pady=(0,12),sticky="w")
        specs=[
            ("CPU Usage",    "cpu",  t["accent"],  2,0),
            ("RAM Usage",    "ram",  t["accent2"],  2,1),
            ("Disk C: Used", "disk", t["orange"],   3,0),
            ("Network Recv", "net",  t["green"],    3,1),
        ]
        for lbl2,key,color,gr,gc in specs:
            card=ctk.CTkFrame(self,fg_color=t["card"],corner_radius=12)
            card.grid(row=gr,column=gc,padx=10,pady=8,sticky="nsew")
            card.grid_columnconfigure(0,weight=1)
            top=ctk.CTkFrame(card,fg_color="transparent"); top.grid(row=0,column=0,padx=14,pady=(14,6),sticky="ew"); top.grid_columnconfigure(1,weight=1)
            label(top,t,lbl2,size=12,color=t["fg2"]).grid(row=0,column=0,sticky="w")
            vl=label(top,t,"—",size=26,bold=True,color=color); vl.grid(row=0,column=1,sticky="e")
            self._vals[key]=vl
            # 30 vertical progress bars as chart
            cf=ctk.CTkFrame(card,fg_color=t["bg2"],corner_radius=6,height=72)
            cf.grid(row=1,column=0,padx=14,pady=(0,14),sticky="ew"); cf.grid_propagate(False)
            bars=[]
            for i in range(36):
                b=ctk.CTkProgressBar(cf,orientation="vertical",width=7,height=64,
                                      fg_color=t["prog_bg"],progress_color=color,corner_radius=2)
                b.place(x=4+i*9,y=4); b.set(0)
                bars.append(b)
            self._bars[key]=bars

    def _push(self,key,val,maxv=100):
        bars=self._bars[key]
        # shift left
        for i in range(len(bars)-1):
            try: bars[i].set(bars[i+1].get())
            except: pass
        try: bars[-1].set(min(1.0,float(val)/max(float(maxv),0.01)))
        except: pass

    def start(self):
        self._running=True
        threading.Thread(target=self._loop,daemon=True).start()

    def stop(self): self._running=False

    def _loop(self):
        while self._running:
            try:
                m=self._mfn()
                self.after(0,lambda mm=m:self._update(mm))
            except: pass
            time.sleep(self._iv)

    def _update(self,m):
        try:
            self._vals["cpu"].configure(text=f"{m['cpu']:.0f}%")
            self._vals["ram"].configure(text=f"{m['ram']:.0f}%")
            self._vals["disk"].configure(text=f"{m['disk']:.0f}%")
            self._vals["net"].configure(text=f"{m['net_recv']:.1f}MB")
            self._push("cpu",  m["cpu"])
            self._push("ram",  m["ram"])
            self._push("disk", m["disk"])
            self._push("net",  m["net_recv"], maxv=max(m["net_recv"],10))
        except: pass
