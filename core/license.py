"""
core/license.py - License verification
Free vs Premium key system with HMAC-SHA256 validation.
"""
import hmac, hashlib, json, logging
from pathlib import Path

log = logging.getLogger(__name__)

# Secret salt — change this to your own secret string
_SECRET = b"WOP-SECRET-2025-CHANGE-THIS"

# Features locked in Free version
FREE_FEATURES = {"dashboard", "cleanup", "monitoring"}
ALL_FEATURES  = {"dashboard","cleanup","disk","startup","registry",
                 "network","gaming","monitoring","reports","restore","settings"}

# Pre-generated valid key hashes (add more via admin panel logic)
# Format: HMAC-SHA256(key, _SECRET)[:16]
_VALID_PREMIUM_HASHES = set()  # populated at first run from keys file
_VALID_FREE_HASHES    = set()


def _hash_key(key: str) -> str:
    return hmac.new(_SECRET, key.encode(), hashlib.sha256).hexdigest()[:24]


def generate_key(key_type: str = "premium") -> str:
    """Generate a new valid key and save its hash."""
    import secrets, string
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace("O","").replace("0","").replace("I","").replace("1","")
    seg   = lambda: "".join(secrets.choice(chars) for _ in range(5))
    prefix = "WOP-PRO" if key_type == "premium" else "WOP-FREE"
    key = f"{prefix}-{seg()}-{seg()}-{seg()}"
    _register_key(key, key_type)
    return key


def _keys_file(base: Path) -> Path:
    return base / "backups" / ".keys.json"


def load_keys(base: Path):
    """Load saved keys into memory."""
    global _VALID_PREMIUM_HASHES, _VALID_FREE_HASHES
    f = _keys_file(base)
    if not f.exists():
        return
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        _VALID_PREMIUM_HASHES = set(data.get("premium", []))
        _VALID_FREE_HASHES    = set(data.get("free",    []))
    except Exception as e:
        log.warning(f"load_keys: {e}")


def _save_keys(base: Path):
    f = _keys_file(base)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({
        "premium": list(_VALID_PREMIUM_HASHES),
        "free":    list(_VALID_FREE_HASHES),
    }, indent=2), encoding="utf-8")


_BASE_REF = None

def init(base: Path):
    global _BASE_REF
    _BASE_REF = base
    load_keys(base)


def _register_key(key: str, key_type: str):
    h = _hash_key(key)
    if key_type == "premium":
        _VALID_PREMIUM_HASHES.add(h)
    else:
        _VALID_FREE_HASHES.add(h)
    if _BASE_REF:
        _save_keys(_BASE_REF)


def activate(key: str) -> dict:
    """
    Try to activate a key.
    Returns {"ok": bool, "type": "free"|"premium"|None, "message": str}
    """
    key = key.strip().upper()
    h   = _hash_key(key)

    if h in _VALID_PREMIUM_HASHES:
        log.info(f"Premium key activated: {key[:12]}***")
        return {"ok": True,  "type": "premium", "message": "Premium activated!"}

    if h in _VALID_FREE_HASHES:
        log.info(f"Free key activated: {key[:12]}***")
        return {"ok": True,  "type": "free",    "message": "Free version activated."}

    log.warning(f"Invalid key attempt: {key[:12]}***")
    return {"ok": False, "type": None, "message": "Invalid key. Please check and try again."}


def is_premium(license_type: str) -> bool:
    return license_type == "premium"


def feature_allowed(feature: str, license_type: str) -> bool:
    if license_type == "premium":
        return True
    return feature in FREE_FEATURES


LOCKED_MSG = "This feature requires Premium.\nUpgrade to unlock all features."
