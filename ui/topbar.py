
import customtkinter as ctk
from typing import Callable

class Topbar(ctk.CTkFrame):
    def __init__(self,parent,t,version,is_admin,toggle_theme:Callable):
        super().__init__(parent,fg_color=t["topbar"],corner_radius=0,height=50)
        self.pack_propagate(False)
        self._t=t
        self._title=ctk.CTkLabel(self,text="Dashboard",font=("Segoe UI",15,"bold"),text_color=t["fg"],fg_color="transparent")
        self._title.pack(side="left",padx=20)
        right=ctk.CTkFrame(self,fg_color="transparent"); right.pack(side="right",padx=14)
        ctk.CTkButton(right,text="☀/🌙",width=54,height=26,fg_color=t["card"],
                      hover_color=t["hover"],text_color=t["fg"],font=("Segoe UI",11),
                      corner_radius=6,command=toggle_theme).pack(side="left",padx=4)
        ac=t["green"] if is_admin else t["orange"]
        at="🛡 Admin" if is_admin else "⚠ Limited"
        ctk.CTkLabel(right,text=at,font=("Segoe UI",11,"bold"),text_color=ac,fg_color="transparent").pack(side="left",padx=8)
        ctk.CTkLabel(right,text=f"v{version}",font=("Segoe UI",10),text_color=t["fg3"],fg_color="transparent").pack(side="left",padx=4)
        self._info=ctk.CTkLabel(right,text="",font=("Segoe UI",10),text_color=t["fg2"],fg_color="transparent")
        self._info.pack(side="left",padx=10)

    def set_title(self,text): self._title.configure(text=text)
    def set_info(self,text):  self._info.configure(text=text)
