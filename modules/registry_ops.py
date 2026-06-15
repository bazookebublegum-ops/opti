
import subprocess, logging
from pathlib import Path
from typing import Dict, List, Optional
log = logging.getLogger(__name__)
try:
    import winreg; HAS=True
except ImportError: HAS=False

TWEAKS=[
    {"id":"menu_delay",   "label":"Menu Show Delay",          "desc":"0ms vs 400ms — faster menus",
     "hive":"HKCU","key":r"Control Panel\Desktop","name":"MenuShowDelay","default":"400","value":"0","type":"STR"},
    {"id":"hover",        "label":"Tooltip Hover Time",        "desc":"10ms vs 400ms",
     "hive":"HKCU","key":r"Control Panel\Mouse","name":"MouseHoverTime","default":"400","value":"10","type":"STR"},
    {"id":"win_anim",     "label":"Disable Window Animations", "desc":"Faster minimize/maximize",
     "hive":"HKCU","key":r"Control Panel\Desktop\WindowMetrics","name":"MinAnimate","default":"1","value":"0","type":"STR"},
    {"id":"taskbar_anim", "label":"Disable Taskbar Animations","desc":"Reduces UI CPU usage",
     "hive":"HKCU","key":r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
     "name":"TaskbarAnimations","default":"1","value":"0","type":"DWORD"},
    {"id":"hide_ext",     "label":"Show File Extensions",      "desc":"Improves security awareness",
     "hive":"HKCU","key":r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
     "name":"HideFileExt","default":"1","value":"0","type":"DWORD"},
    {"id":"hidden_files", "label":"Show Hidden Files",         "desc":"Better file visibility",
     "hive":"HKCU","key":r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
     "name":"Hidden","default":"2","value":"1","type":"DWORD"},
]

_H={}
def _init():
    if HAS:
        _H["HKCU"]=winreg.HKEY_CURRENT_USER
        _H["HKLM"]=winreg.HKEY_LOCAL_MACHINE
_init()

def read_val(t:Dict)->Optional[str]:
    if not HAS: return None
    try:
        k=winreg.OpenKey(_H[t["hive"]],t["key"],0,winreg.KEY_READ)
        v,_=winreg.QueryValueEx(k,t["name"]); winreg.CloseKey(k); return str(v)
    except FileNotFoundError: return t["default"]
    except Exception as e: log.debug(f"read {t['name']}: {e}"); return None

def write_val(t:Dict, val:str, bdir:Path)->bool:
    if not HAS: return False
    _backup(t,bdir)
    try:
        k=winreg.CreateKey(_H[t["hive"]],t["key"])
        rt=winreg.REG_DWORD if t["type"]=="DWORD" else winreg.REG_SZ
        v=int(val) if rt==winreg.REG_DWORD else val
        winreg.SetValueEx(k,t["name"],0,rt,v); winreg.CloseKey(k)
        log.info(f"Set {t['name']}={val}"); return True
    except Exception as e: log.error(f"write {t['name']}: {e}"); return False

def revert_val(t:Dict,bdir:Path)->bool: return write_val(t,t["default"],bdir)

def _backup(t,bdir:Path):
    try:
        bdir.mkdir(parents=True,exist_ok=True)
        subprocess.run(["reg","export",f"{t['hive']}\\{t['key']}",str(bdir/f"reg_{t['id']}.reg"),"/y"],
                       capture_output=True,timeout=10)
    except Exception as e: log.warning(f"backup: {e}")

def scan()->List[Dict]:
    res=[]
    for t in TWEAKS:
        d=dict(t); d["current"]=read_val(t); d["done"]=d["current"]==t["value"]
        res.append(d)
    return res
