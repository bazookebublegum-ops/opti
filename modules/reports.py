import datetime, logging
from pathlib import Path
from typing import Dict, List, Any
log = logging.getLogger(__name__)

class Reporter:
    def __init__(self, rdir: Path):
        self.dir = Path(rdir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def save(self, title: str, sections: List[Dict[str, Any]], fmt: str = "html") -> Path:
        ts = datetime.datetime.now()
        out = self.dir / f"report_{ts.strftime('%Y%m%d_%H%M%S')}.{fmt}"
        text = self._html(title, sections, ts) if fmt == "html" else self._txt(title, sections, ts)
        out.write_text(text, encoding="utf-8")
        log.info(f"Report saved: {out}")
        return out

    def list_reports(self) -> List[Dict]:
        res = []
        for f in sorted(self.dir.iterdir(), reverse=True):
            if f.suffix in (".html", ".txt"):
                mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime)
                res.append({
                    "name":     f.name,
                    "path":     str(f),
                    "fmt":      f.suffix[1:].upper(),
                    "size_kb":  max(1, f.stat().st_size // 1024),
                    "modified": mtime.strftime("%Y-%m-%d %H:%M"),
                })
        return res

    def _html(self, title, sections, ts) -> str:
        rows = ""
        for s in sections:
            rows += f"<h2>{s.get('heading','')}</h2><table>"
            for item in s.get("items", []):
                rows += f"<tr><td>{item['key']}</td><td><b>{item['value']}</b></td></tr>"
            rows += "</table>"
        style = (
            "body{font-family:'Segoe UI',sans-serif;background:#0D0F14;color:#E8EAF6;padding:20px}"
            "h1{color:#4F8EF7}h2{color:#2DD4A7;margin-top:24px}"
            "table{border-collapse:collapse;width:100%;max-width:800px}"
            "td{padding:8px 12px;border:1px solid #252A3D}"
            "tr:nth-child(even){background:#1A1E2E}"
            ".meta{color:#8A92B2;font-size:12px;margin-bottom:16px}"
        )
        meta = ts.strftime("%Y-%m-%d %H:%M:%S")
        return (
            f'<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{title}</title>'
            f"<style>{style}</style></head>"
            f'<body><h1>Windows Optimizer Pro</h1>'
            f'<h2>{title}</h2>'
            f'<div class="meta">Generated: {meta}</div>'
            f"{rows}</body></html>"
        )

    def _txt(self, title, sections, ts) -> str:
        lines = ["=" * 60, f"  {title}", f"  {ts.strftime('%Y-%m-%d %H:%M:%S')}", "=" * 60, ""]
        for s in sections:
            lines += ["", f"-- {s.get('heading','')} --"]
            for i in s.get("items", []):
                lines.append(f"  {i['key']:<30} {i['value']}")
        lines += ["", "=" * 60]
        return "\n".join(lines)
