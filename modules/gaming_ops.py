
import subprocess, logging
log=logging.getLogger(__name__)
try:
    import winreg; HAS=True
except ImportError: HAS=False

def check_game_mode()->Dict:
    if not HAS: return {"enabled":None,"status":"unknown"}
    try:
        k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\GameBar",0,winreg.KEY_READ)
        v,_=winreg.QueryValueEx(k,"AutoGameModeEnabled"); winreg.CloseKey(k)
        return {"enabled":bool(v),"status":"Enabled" if v else "Disabled"}
    except: return {"enabled":None,"status":"Unknown"}

def check_hags()->Dict:
    if not HAS: return {"enabled":None,"status":"unknown"}
    try:
        k=winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",0,winreg.KEY_READ)
        v,_=winreg.QueryValueEx(k,"HwSchMode"); winreg.CloseKey(k)
        return {"enabled":v==2,"status":"Enabled" if v==2 else "Disabled"}
    except: return {"enabled":None,"status":"Unknown"}

def check_power()->Dict:
    try:
        r=subprocess.run(["powercfg","/getactivescheme"],capture_output=True,text=True,timeout=10)
        out=r.stdout.lower()
        if "high performance" in out or "ultimate" in out: return {"plan":"High Performance","optimal":True}
        if "balanced" in out: return {"plan":"Balanced","optimal":False}
        return {"plan":"Power Saver","optimal":False}
    except: return {"plan":"Unknown","optimal":None}

def enable_game_mode()->bool:
    if not HAS: return False
    try:
        k=winreg.CreateKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\GameBar")
        winreg.SetValueEx(k,"AutoGameModeEnabled",0,winreg.REG_DWORD,1)
        winreg.CloseKey(k); log.info("Game mode enabled"); return True
    except Exception as e: log.error(f"game_mode: {e}"); return False

def set_high_perf()->bool:
    try:
        r=subprocess.run(["powercfg","/setactive","8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"],
                         capture_output=True,timeout=10)
        if r.returncode==0: log.info("High performance power plan set"); return True
        return False
    except Exception as e: log.error(f"power: {e}"); return False

def get_status()->dict:
    gm=check_game_mode(); hg=check_hags(); pw=check_power()
    recs=[]
    if not gm.get("enabled"):   recs.append("Enable Game Mode (Settings → Gaming → Game Mode)")
    if not hg.get("enabled"):   recs.append("Enable Hardware Accelerated GPU Scheduling")
    if not pw.get("optimal"):   recs.append("Switch to High Performance power plan")
    if not recs: recs=["Gaming settings look optimal!"]
    procs=[]
    try:
        import psutil
        procs=[{"name":p.info["name"],"cpu":p.info["cpu_percent"]}
               for p in psutil.process_iter(["name","cpu_percent"])
               if (p.info["cpu_percent"] or 0)>1]
        procs.sort(key=lambda x:x["cpu"],reverse=True)
        procs=procs[:10]
    except: pass
    return {"game_mode":gm,"hags":hg,"power":pw,"recommendations":recs,"processes":procs}

from typing import Dict  # fix forward ref
