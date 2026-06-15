
import customtkinter as ctk
from typing import Callable, Dict, List

class Sidebar(ctk.CTkFrame):
    def __init__(self,parent,t,nav,on_nav:Callable,version:str):
        super().__init__(parent,fg_color=t["sidebar"],corner_radius=0,width=210)
        self.grid_propagate(False)
        self._t=t; self._btns={}
        # Logo
        top=ctk.CTkFrame(self,fg_color="transparent"); top.pack(fill="x",padx=14,pady=(18,4))
        ctk.CTkLabel(top,text="⬡",font=("Segoe UI",26),text_color=t["accent"],fg_color="transparent").pack(side="left")
        nf=ctk.CTkFrame(top,fg_color="transparent"); nf.pack(side="left",padx=8)
        ctk.CTkLabel(nf,text="Windows",font=("Segoe UI",12,"bold"),text_color=t["fg"],fg_color="transparent").pack(anchor="w")
        ctk.CTkLabel(nf,text="Optimizer Pro",font=("Segoe UI",10),text_color=t["accent"],fg_color="transparent").pack(anchor="w")
        ctk.CTkLabel(self,text=f"v{version}",font=("Segoe UI",9),text_color=t["fg3"],fg_color="transparent").pack(padx=14,anchor="w",pady=(0,8))
        ctk.CTkFrame(self,fg_color=t["border"],height=1).pack(fill="x",padx=14,pady=4)
        # Nav buttons
        for item in nav:
            b=ctk.CTkButton(self,text=f"  {item['icon']}  {item['label']}",anchor="w",
                             font=("Segoe UI",13),text_color=t["fg2"],fg_color="transparent",
                             hover_color=t["hover"],corner_radius=8,height=40,
                             command=lambda i=item["id"]:on_nav(i))
            b.pack(fill="x",padx=8,pady=2)
            self._btns[item["id"]]=b
        ctk.CTkFrame(self,fg_color=t["border"],height=1).pack(fill="x",padx=14,pady=4,side="bottom")
        ctk.CTkLabel(self,text="© 2025 WOP",font=("Segoe UI",8),text_color=t["fg3"],fg_color="transparent").pack(side="bottom",pady=4)

    def activate(self,page_id):
        for bid,b in self._btns.items():
            if bid==page_id:
                b.configure(fg_color=self._t["card"],text_color=self._t["accent"],font=("Segoe UI",13,"bold"))
            else:
                b.configure(fg_color="transparent",text_color=self._t["fg2"],font=("Segoe UI",13))
