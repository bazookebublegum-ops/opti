
import customtkinter as ctk, threading, time

class Splash(ctk.CTkToplevel):
    def __init__(self,parent,on_done):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost",True)
        self.configure(fg_color="#0D0F14")
        W,H=460,280
        sw,sh=self.winfo_screenwidth(),self.winfo_screenheight()
        self.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

        ctk.CTkLabel(self,text="⬡",font=("Segoe UI",56),text_color="#4F8EF7",fg_color="transparent").pack(pady=(30,0))
        ctk.CTkLabel(self,text="Windows Optimizer Pro",font=("Segoe UI",20,"bold"),text_color="#E8EAF6",fg_color="transparent").pack()
        ctk.CTkLabel(self,text="v2.0  Professional Edition",font=("Segoe UI",10),text_color="#8A92B2",fg_color="transparent").pack(pady=(2,16))
        self._s=ctk.CTkLabel(self,text="Starting…",font=("Segoe UI",11),text_color="#4F8EF7",fg_color="transparent"); self._s.pack()
        self._b=ctk.CTkProgressBar(self,width=320,height=5,progress_color="#4F8EF7",fg_color="#1A1E2E",corner_radius=3); self._b.pack(pady=10); self._b.set(0)
        ctk.CTkLabel(self,text="© 2025 WOP",font=("Segoe UI",8),text_color="#525A7A",fg_color="transparent").pack(pady=(4,0))
        self._done=on_done
        threading.Thread(target=self._run,daemon=True).start()

    def _run(self):
        for v,msg in [(0.2,"Checking system…"),(0.45,"Loading modules…"),(0.7,"Building interface…"),(1.0,"Ready!")]:
            time.sleep(0.35)
            try: self._b.set(v); self._s.configure(text=msg)
            except: break
        time.sleep(0.25)
        self.after(0,self._done)
