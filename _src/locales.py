import json
from pathlib import Path

META_DIR = Path(__file__).resolve().parent / "i18n" / "meta"


def extra_locales():
    """Site languages added beyond the original ten, one i18n/meta/<code>.json each, sorted by code."""
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(META_DIR.glob("*.json"))]


def prefix(code):
    return f"/{code.lower()}/"
