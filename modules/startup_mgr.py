
import logging
log=logging.getLogger(__name__)
try:
    import winreg; HAS=True
except ImportError: HAS=False

OPT_NAMES={"adobe","discord","steam","teams","copilot","onedrive","spotify","slack","zoom","skype"}

def get_entries():
    from core.system_info import get_startup
    entries=get_startup()
    for e in entries:
        e["optional"]=any(o in e["name"].lower() for o in OPT_NAMES)
    return entries

def disable(entry)->bool:
    if not HAS or entry.get("hive")=="Folder": return False
    try:
        hmap={"HKCU":winreg.HKEY_CURRENT_USER,"HKLM":winreg.HKEY_LOCAL_MACHINE}
        hive=hmap.get(entry["hive"])
        if not hive: return False
        sk=entry["subkey"]
        k=winreg.OpenKey(hive,sk,0,winreg.KEY_ALL_ACCESS)
        val,vt=winreg.QueryValueEx(k,entry["name"])
        dk=winreg.CreateKey(hive,sk.replace("Run","Run_Disabled_WOP"))
        winreg.SetValueEx(dk,entry["name"],0,vt,val)
        winreg.DeleteValue(k,entry["name"])
        winreg.CloseKey(k); winreg.CloseKey(dk)
        log.info(f"Disabled: {entry['name']}"); return True
    except Exception as e: log.error(f"disable: {e}"); return False

def enable(entry)->bool:
    if not HAS: return False
    try:
        hmap={"HKCU":winreg.HKEY_CURRENT_USER,"HKLM":winreg.HKEY_LOCAL_MACHINE}
        hive=hmap.get(entry["hive"])
        sk=entry["subkey"]
        dk=winreg.OpenKey(hive,sk.replace("Run","Run_Disabled_WOP"),0,winreg.KEY_ALL_ACCESS)
        val,vt=winreg.QueryValueEx(dk,entry["name"])
        k=winreg.OpenKey(hive,sk,0,winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(k,entry["name"],0,vt,val)
        winreg.DeleteValue(dk,entry["name"])
        winreg.CloseKey(k); winreg.CloseKey(dk)
        log.info(f"Enabled: {entry['name']}"); return True
    except Exception as e: log.error(f"enable: {e}"); return False
