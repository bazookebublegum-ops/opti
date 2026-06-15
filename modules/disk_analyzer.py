
import os, hashlib, logging, datetime
from pathlib import Path
from collections import defaultdict
from typing import Callable, Dict, List, Optional
log = logging.getLogger(__name__)

PROTECTED={n.lower() for n in ["documents","desktop","downloads","pictures","videos","music"]}
JUNK={".tmp",".temp",".bak",".old",".dmp",".cache",".chk",".gid"}

def _skip(p:Path)->bool:
    return any(part.lower() in PROTECTED for part in p.parts)

def large_files(root:str,min_mb=50,limit=200,cb:Optional[Callable]=None)->List[Dict]:
    res=[]; n=0; minb=int(min_mb*1e6)
    try:
        for f in Path(root).rglob("*"):
            if f.is_file() and not _skip(f):
                try:
                    sz=f.stat().st_size
                    if sz>=minb:
                        res.append({"name":f.name,"size":sz,"date":datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d"),"path":str(f)})
                except: pass
            n+=1
            if cb and n%500==0: cb(n,len(res))
    except Exception as e: log.error(f"large_files: {e}")
    res.sort(key=lambda x:x["size"],reverse=True)
    return res[:limit]

def old_files(root:str,days=365,limit=200,cb:Optional[Callable]=None)->List[Dict]:
    res=[]; n=0
    cutoff=datetime.datetime.now()-datetime.timedelta(days=days)
    try:
        for f in Path(root).rglob("*"):
            if f.is_file() and not _skip(f):
                try:
                    mt=datetime.datetime.fromtimestamp(f.stat().st_mtime)
                    if mt<cutoff:
                        res.append({"name":f.name,"size":f.stat().st_size,"date":mt.strftime("%Y-%m-%d"),"age":(datetime.datetime.now()-mt).days,"path":str(f)})
                except: pass
            n+=1
            if cb and n%500==0: cb(n,len(res))
    except Exception as e: log.error(f"old_files: {e}")
    res.sort(key=lambda x:x["age"],reverse=True)
    return res[:limit]

def junk_files(root:str,limit=500)->List[Dict]:
    res=[]
    try:
        for f in Path(root).rglob("*"):
            if f.is_file() and f.suffix.lower() in JUNK and not _skip(f):
                try: res.append({"name":f.name,"size":f.stat().st_size,"ext":f.suffix,"path":str(f)})
                except: pass
    except Exception as e: log.error(f"junk: {e}")
    res.sort(key=lambda x:x["size"],reverse=True)
    return res[:limit]

def duplicates(root:str,min_kb=1,cb:Optional[Callable]=None)->List[List[Dict]]:
    by_size=defaultdict(list); minb=int(min_kb*1024)
    try:
        for f in Path(root).rglob("*"):
            if f.is_file() and not _skip(f):
                try:
                    sz=f.stat().st_size
                    if sz>=minb: by_size[sz].append(f)
                except: pass
    except Exception as e: log.error(f"dupes pass1: {e}"); return []
    by_hash=defaultdict(list)
    cands=[f for files in by_size.values() if len(files)>1 for f in files]
    for i,f in enumerate(cands):
        h=_sha(f)
        if h: by_hash[h].append(f)
        if cb and i%50==0: cb(i,len(cands))
    groups=[]
    for h,files in by_hash.items():
        if len(files)>=2:
            groups.append([{"name":f.name,"size":f.stat().st_size,"hash":h[:16],"path":str(f)} for f in files])
    return groups

def _sha(p:Path)->Optional[str]:
    try:
        h=hashlib.sha256()
        with open(p,"rb") as f:
            while chunk:=f.read(65536): h.update(chunk)
        return h.hexdigest()
    except: return None

def fmt(b:int)->str:
    for u in ("B","KB","MB","GB"):
        if b<1024: return f"{b:.1f} {u}"
        b//=1024
    return f"{b:.1f} TB"
