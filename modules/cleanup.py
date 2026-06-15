
import os, subprocess, logging
from pathlib import Path
from typing import Callable, Dict, List, Optional
log = logging.getLogger(__name__)

CATS = [
    {"id":"temp",     "label":"User TEMP",             "env":"TEMP"},
    {"id":"win_temp", "label":"Windows Temp",           "path":r"C:\Windows\Temp"},
    {"id":"prefetch", "label":"Prefetch",               "path":r"C:\Windows\Prefetch"},
    {"id":"win_logs", "label":"Windows Logs",           "path":r"C:\Windows\Logs"},
    {"id":"update",   "label":"Windows Update Cache",   "path":r"C:\Windows\SoftwareDistribution\Download"},
    {"id":"recycle",  "label":"Recycle Bin",            "special":"recycle"},
    {"id":"chrome",   "label":"Chrome Cache",           "env_sub":("LOCALAPPDATA",r"Google\Chrome\User Data\Default\Cache")},
    {"id":"edge",     "label":"Edge Cache",             "env_sub":("LOCALAPPDATA",r"Microsoft\Edge\User Data\Default\Cache")},
]

def _path(cat):
    if "path"    in cat: return Path(cat["path"])
    if "env"     in cat: p=os.environ.get(cat["env"],""); return Path(p) if p else None
    if "env_sub" in cat:
        b=os.environ.get(cat["env_sub"][0],"")
        return Path(b)/cat["env_sub"][1] if b else None
    return None

def scan_cat(cat) -> Dict:
    r={"id":cat["id"],"label":cat["label"],"bytes":0,"files":0,"error":None}
    try:
        if cat.get("special")=="recycle":
            try:
                for f in Path("C:/$Recycle.Bin").rglob("*"):
                    if f.is_file():
                        try: r["bytes"]+=f.stat().st_size; r["files"]+=1
                        except: pass
            except: pass
            return r
        p=_path(cat)
        if not p or not p.exists(): return r
        for f in p.rglob("*"):
            if f.is_file():
                try: r["bytes"]+=f.stat().st_size; r["files"]+=1
                except: pass
    except Exception as e: r["error"]=str(e)
    return r

def scan_all(cb:Optional[Callable]=None) -> List[Dict]:
    res=[]
    for i,c in enumerate(CATS):
        res.append(scan_cat(c))
        if cb: cb(i+1,len(CATS),res[-1])
    return res

def clean_cat(cat, cb:Optional[Callable]=None) -> Dict:
    r={"id":cat["id"],"label":cat["label"],"deleted":0,"freed":0,"errors":[]}
    try:
        if cat.get("special")=="recycle":
            sz=0
            try:
                for f in Path("C:/$Recycle.Bin").rglob("*"):
                    if f.is_file():
                        try: sz+=f.stat().st_size
                        except: pass
            except: pass
            subprocess.run(["powershell","-NoProfile","-Command",
                "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
                capture_output=True,timeout=30)
            r["freed"]=sz; return r
        p=_path(cat)
        if not p or not p.exists(): return r
        files=[f for f in p.rglob("*") if f.is_file()]
        for i,f in enumerate(files):
            try:
                sz=f.stat().st_size; f.unlink(missing_ok=True)
                r["deleted"]+=1; r["freed"]+=sz
            except Exception as e: r["errors"].append(f"{f.name}: {e}")
            if cb: cb(i+1,len(files))
    except Exception as e: r["errors"].append(str(e))
    log.info(f"Clean {r['label']}: {r['deleted']} files, {r['freed']//1024}KB")
    return r

def fmt(b:int)->str:
    for u in ("B","KB","MB","GB"):
        if b<1024: return f"{b:.1f} {u}"
        b//=1024
    return f"{b:.1f} TB"
