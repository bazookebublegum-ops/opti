
import sys, ctypes, logging
from pathlib import Path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

def is_admin():
    try: return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except: return False

def elevate():
    try:
        ctypes.windll.shell32.ShellExecuteW(None,"runas",sys.executable,f'"{__file__}"',None,1)
        sys.exit(0)
    except: pass

def setup_log():
    (BASE_DIR/"logs").mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.FileHandler(BASE_DIR/"logs"/"optimizer.log",encoding="utf-8"),
                  logging.StreamHandler()])
    return logging.getLogger("WOP")

def main():
    log = setup_log()
    log.info("="*50)
    log.info(f"Windows Optimizer Pro starting — Python {sys.version.split()[0]}")
    admin = is_admin()
    log.info(f"Admin: {admin}")
    if not admin:
        log.warning("Requesting admin elevation...")
        elevate()
    try:
        import customtkinter
    except ImportError:
        print("Missing: pip install customtkinter psutil")
        input("Press Enter..."); sys.exit(1)
    from ui.app import App
    App(BASE_DIR, admin).run()

if __name__ == "__main__":
    main()
