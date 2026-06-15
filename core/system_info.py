
import logging, os
log = logging.getLogger(__name__)
try:
    import psutil
    HAS = True
except ImportError:
    HAS = False

def get_metrics():
    if not HAS:
        return dict(cpu=0,ram=0,ram_used=0,ram_total=8,disk=0,disk_used=0,disk_total=100,net_recv=0,score=50,label="Unknown")
    try:
        cpu  = psutil.cpu_percent(interval=0.2)
        ram  = psutil.virtual_memory()
        disk = psutil.disk_usage("C:/")
        net  = psutil.net_io_counters()
        sc   = max(0,min(100,int(100-cpu*0.3-ram.percent*0.3-disk.percent*0.4)))
        lbl  = "Excellent" if sc>=80 else "Good" if sc>=60 else "Average" if sc>=40 else "Needs Optimization"
        return dict(cpu=cpu,ram=ram.percent,ram_used=round(ram.used/1e9,1),
                    ram_total=round(ram.total/1e9,1),disk=disk.percent,
                    disk_used=round(disk.used/1e9,1),disk_total=round(disk.total/1e9,1),
                    net_recv=round(net.bytes_recv/1e6,1),score=sc,label=lbl)
    except Exception as e:
        log.error(f"metrics: {e}")
        return dict(cpu=0,ram=0,ram_used=0,ram_total=8,disk=0,disk_used=0,disk_total=100,net_recv=0,score=50,label="Unknown")

def get_startup():
    entries=[]
    try:
        import winreg
        for hn,hv,sk in [
            ("HKCU",winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            ("HKLM",winreg.HKEY_LOCAL_MACHINE,r"Software\Microsoft\Windows\CurrentVersion\Run"),
        ]:
            try:
                k=winreg.OpenKey(hv,sk,0,winreg.KEY_READ)
                i=0
                while True:
                    try:
                        n,v,_=winreg.EnumValue(k,i)
                        entries.append(dict(name=n,path=v,hive=hn,subkey=sk,enabled=True))
                        i+=1
                    except OSError: break
                winreg.CloseKey(k)
            except: pass
    except ImportError: pass
    return entries
