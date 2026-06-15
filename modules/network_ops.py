
import subprocess, socket, logging
from typing import Dict, List
log = logging.getLogger(__name__)

def _cmd(cmd,label,timeout=60)->Dict:
    try:
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
        ok=r.returncode==0
        if ok: log.info(f"OK: {label}")
        else:  log.warning(f"FAIL: {label} — {r.stderr[:80]}")
        return {"label":label,"ok":ok,"out":r.stdout.strip()[:400],"err":r.stderr.strip()[:200]}
    except subprocess.TimeoutExpired: return {"label":label,"ok":False,"out":"","err":"Timeout"}
    except Exception as e:            return {"label":label,"ok":False,"out":"","err":str(e)}

def flush_dns():     return _cmd(["ipconfig","/flushdns"],       "Flush DNS Cache")
def reset_winsock(): return _cmd(["netsh","winsock","reset"],    "Reset Winsock")
def reset_tcpip():   return _cmd(["netsh","int","ip","reset"],   "Reset TCP/IP")
def release_ip():    return _cmd(["ipconfig","/release"],        "Release IP")
def renew_ip():      return _cmd(["ipconfig","/renew"],          "Renew IP")

DNS = {"Cloudflare":("1.1.1.1","1.0.0.1"),"Google":("8.8.8.8","8.8.4.4"),
       "Quad9":("9.9.9.9","149.112.112.112"),"OpenDNS":("208.67.222.222","208.67.220.220")}

def set_dns(adapter,primary,secondary)->Dict:
    r1=_cmd(["netsh","interface","ip","set","dns",f"name={adapter}","static",primary],f"Set DNS {primary}")
    r2=_cmd(["netsh","interface","ip","add","dns",f"name={adapter}",secondary,"index=2"],f"Set DNS2 {secondary}")
    return {"ok":r1["ok"] and r2["ok"],"out":r1["out"]+r2["out"]}

def ping(host,count=4)->Dict:
    r=_cmd(["ping","-n",str(count),host],f"Ping {host}",timeout=20)
    avg=None
    for line in r["out"].splitlines():
        if "Average" in line:
            try: avg=float(line.split("=")[-1].replace("ms","").strip())
            except: pass
    return {**r,"avg_ms":avg}

def get_adapters()->List[Dict]:
    try:
        import psutil, socket as s
        out=[]
        for name,st in psutil.net_if_stats().items():
            ip=next((a.address for a in psutil.net_if_addrs().get(name,[]) if a.family==s.AF_INET),"")
            out.append({"name":name,"up":st.isup,"speed":st.speed,"ip":ip})
        return out
    except: return []
