
import json, subprocess, logging, datetime
from pathlib import Path
from typing import Dict, List
log=logging.getLogger(__name__)

class BackupManager:
    def __init__(self,bdir:Path):
        self.dir=Path(bdir); self.dir.mkdir(parents=True,exist_ok=True)
        self._jfile=self.dir/"journal.json"; self._j=[]
        if self._jfile.exists():
            try: self._j=json.loads(self._jfile.read_text(encoding="utf-8"))
            except: pass

    def log_op(self,op:str,**kw):
        self._j.append({"ts":datetime.datetime.now().isoformat(),"op":op,**kw})
        try: self._jfile.write_text(json.dumps(self._j,indent=2),encoding="utf-8")
        except: pass

    def create_restore_point(self,desc="Windows Optimizer Pro")->bool:
        try:
            r=subprocess.run(["powershell","-NoProfile","-Command",
                f'Checkpoint-Computer -Description "{desc}" -RestorePointType "MODIFY_SETTINGS"'],
                capture_output=True,text=True,timeout=120)
            ok=r.returncode==0
            if ok: log.info(f"Restore point created: {desc}"); self.log_op("restore_point",desc=desc)
            else:  log.warning(f"Restore point failed: {r.stderr[:100]}")
            return ok
        except Exception as e: log.error(f"restore_point: {e}"); return False

    def export_reg(self,hive,subkey,label)->Path|None:
        ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out=self.dir/f"reg_{label}_{ts}.reg"
        try:
            r=subprocess.run(["reg","export",f"{hive}\\{subkey}",str(out),"/y"],
                             capture_output=True,timeout=20)
            if r.returncode==0: self.log_op("reg_backup",key=f"{hive}/{subkey}",file=str(out)); return out
        except Exception as e: log.warning(f"reg export: {e}")
        return None

    def restore_reg(self,reg_file:Path)->bool:
        try:
            r=subprocess.run(["reg","import",str(reg_file)],capture_output=True,timeout=20)
            ok=r.returncode==0
            if ok: self.log_op("reg_restore",file=str(reg_file))
            return ok
        except Exception as e: log.error(f"reg import: {e}"); return False

    def list_backups(self)->List[Dict]:
        res=[]
        for f in sorted(self.dir.iterdir(),reverse=True):
            if f.suffix in (".reg",".json") and f.name!="journal.json":
                mtime=datetime.datetime.fromtimestamp(f.stat().st_mtime)
                res.append({"name":f.name,"path":str(f),
                             "size_kb":max(1,f.stat().st_size//1024),
                             "modified":mtime.strftime("%Y-%m-%d %H:%M")})
        return res

    def get_journal(self)->List[Dict]: return list(self._j)
