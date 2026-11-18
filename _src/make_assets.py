#!/usr/bin/env python3
"""Import images into /assets from the Calcaloo project (approved mascot renders,
store screenshots, app icon, store badges). Re-run when the final store screenshots land:

    python3 _src/make_assets.py [--shots <dir with android-phone/<locale>/ and ios-iphone/en-US/>]
"""
import re
import argparse
import io
import json
import shutil
import zipfile
from pathlib import Path

from PIL import Image

SITE = Path(__file__).resolve().parent.parent
PROJECT = SITE.parent.parent
OUT = SITE / "assets" / "img"
MASCOT = PROJECT / "design" / "mascot" / "reference" / "3d-png"
MASCOT_CROP = (102, 132, 922, 900)
ICON_DIR = PROJECT / "design" / "icon-refresh" / "assets"
ICON_DRAFT = "D"
SHOTS_ANDROID = PROJECT / "qa-runs" / "1.4.0-65-store-screenshots" / "raw" / "android-phone"
SHOT_IOS_TODAY = PROJECT / "qa-runs" / "1.4.0-65-store-screenshots-v2" / "samples" / "ios-iphone" / "en-US" / "iphone69_01_today.png"
STORE_17 = PROJECT / "design" / "store-1.7"
HOME_RAW = STORE_17 / "v4" / "raw" / "ios" / "iphone-large" / "en-US"
HOME_ART = STORE_17 / "v4" / "out" / "ios"
TILE = (480, 720, 960)
HOME = {"today": (HOME_RAW / "01.png", (360, 540, 720, 1080), None),
        "card": (HOME_ART / "iphone-large" / "en-US" / "02.png", TILE, (0, 700, 1320, 1960)),
        "scan": (HOME_ART / "iphone-large" / "en-US" / "01.png", TILE, (0, 640, 1320, 2810)),
        "barcode": (HOME_ART / "iphone-medium" / "en-US" / "03.png", TILE, (0, 600, 1206, 2470)),
        "achievements": (HOME_ART / "iphone-large" / "en-US" / "05.png", TILE, (0, 900, 1320, 2560))}
BADGES = Path(__file__).resolve().parent / "vendor" / "badges"

LOCALES = {"en": "en-US", "de": "de-DE", "es": "es-ES", "fr": "fr-FR", "it": "it", "pl": "pl", "pt-BR": "pt-BR", "ru": "ru", "tr": "tr"}
MOODS = ["happy", "celebrating", "curious", "encouraging", "surprised", "shy"]
SHOTS = {"today": "phone_01_today.png", "add": "phone_08_add_entry.png", "achievements": "phone_03_achievements.png",
         "milestone": "phone_04_milestone.png", "weekly": "phone_05_weekly_summary.png", "stats": "phone_06_stats.png"}
WIDTHS = (320, 480, 640)


def save_both(img, stem, quality=80):
    img.save(OUT / f"{stem}.webp", quality=quality, method=6)
    img.save(OUT / f"{stem}.avif", quality=max(quality - 22, 40))


def resized(img, width):
    return img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)


def mascot():
    for mood in MOODS:
        img = Image.open(MASCOT / f"mascot_{mood}.png").convert("RGBA").crop(MASCOT_CROP)
        for w in (240, 480, 760):
            save_both(resized(img, w), f"lou-{mood}-{w}", 82)


def shots(android_root, ios_today):
    meta = {}
    for lang, folder in LOCALES.items():
        for key, name in SHOTS.items():
            src = ios_today if (lang == "en" and key == "today" and ios_today.exists()) else android_root / folder / name
            img = Image.open(src).convert("RGB")
            for w in WIDTHS:
                save_both(resized(img, w), f"shot-{lang}-{key}-{w}")
            meta[f"{lang}/{key}"] = [WIDTHS[-1], round(img.height * WIDTHS[-1] / img.width)]
    return meta


def home():
    meta = {}
    for key, (src, widths, box) in HOME.items():
        img = Image.open(src).convert("RGB")
        img = img.crop(box) if box else img
        if widths[-1] > img.width:
            raise SystemExit(f"{src}: {widths[-1]} px would upscale a {img.width} px source")
        for w in widths:
            save_both(resized(img, w), f"home-{key}-{w}", 82)
        meta[key] = [widths[-1], round(img.height * widths[-1] / img.width)]
    return meta


def badges():
    meta = {}
    shutil.copy(BADGES / "app-store-en.svg", OUT / "badge-app-store.svg")
    app_store = {}
    for svg in sorted(BADGES.glob("app-store-*.svg")):
        lang = svg.stem.replace("app-store-", "")
        shutil.copy(svg, OUT / f"badge-app-store-{lang}.svg")
        _, _, w, h = map(float, re.search(r'viewBox="([^"]+)"', svg.read_text()).group(1).split())
        app_store[lang] = [round(w * 50 / h), 50]
    for png in BADGES.glob("google-play-*.png"):
        img = Image.open(png).convert("RGBA")
        img = img.crop(img.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox())
        lang = png.stem.replace("google-play-", "")
        for height in (50, 100):
            scaled = img.resize((round(img.width * height / img.height), height), Image.LANCZOS)
            scaled.save(OUT / f"badge-google-play-{lang}-{height}.webp", quality=90, method=6)
        meta[lang] = [round(img.width * 50 / img.height), 50]
    return meta, app_store


def icons():
    masked = Image.open(ICON_DIR / f"{ICON_DRAFT}_ios_light_1024.png").convert("RGBA")
    full = Image.open(ICON_DIR / f"{ICON_DRAFT}_background_1024.png").convert("RGBA")
    full.alpha_composite(masked)
    full = full.convert("RGB")
    for size, name in ((180, "apple-touch-icon.png"), (96, "app-icon-96.png")):
        full.resize((size, size), Image.LANCZOS).save(OUT / name, optimize=True)
    for size in (32, 48):
        masked.resize((size, size), Image.LANCZOS).save(OUT / f"favicon-{size}.png", optimize=True)
    masked.save(SITE / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    return full


def refresh_press_kit(icon=None):
    """Swap the app icon (when given) and every lou/lou-<mood>.png from MASCOT inside
    /press/calcalou-press-kit.zip, keeping every other entry."""
    kit = SITE / "press" / "calcalou-press-kit.zip"
    if not kit.exists():
        return
    replacements = {}
    if icon:
        buf = io.BytesIO()
        icon.save(buf, "PNG", optimize=True)
        replacements["calcalou-press-kit/app-icon/calcalou-app-icon-1024.png"] = buf.getvalue()
    with zipfile.ZipFile(kit) as src:
        for name in src.namelist():
            if name.startswith("calcalou-press-kit/lou/lou-") and name.endswith(".png"):
                replacements[name] = (MASCOT / f"mascot_{Path(name).stem[4:]}.png").read_bytes()
        entries = [(info, replacements.get(info.filename, src.read(info))) for info in src.infolist()]
    with zipfile.ZipFile(kit, "w", zipfile.ZIP_DEFLATED) as dst:
        for info, data in entries:
            dst.writestr(info, data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--icons-only", action="store_true", help="refresh only the icon set")
    parser.add_argument("--home", action="store_true", help="refresh only the en home images (home-*)")
    parser.add_argument("--mascot", action="store_true", help="refresh only the Lou images (lou-*) and the press kit's Lou files")
    parser.add_argument("--badges", action="store_true", help="refresh only the store badges (App Store and Google Play)")
    parser.add_argument("--shots", type=Path, help="screenshot set root (android-phone/<locale>/, ios-iphone/en-US/)")
    args = parser.parse_args()
    android_root, ios_today = SHOTS_ANDROID, SHOT_IOS_TODAY
    if args.shots:
        android_root = args.shots / "android-phone"
        ios_today = args.shots / "ios-iphone" / "en-US" / "iphone69_01_today.png"
    OUT.mkdir(parents=True, exist_ok=True)
    assets_json = Path(__file__).resolve().parent / "assets.json"
    if args.home:
        meta = json.loads(assets_json.read_text())
        meta["home"] = home()
        assets_json.write_text(json.dumps(meta, indent=2) + "\n")
        return
    if args.badges:
        meta = json.loads(assets_json.read_text())
        meta["googlePlay"], meta["appStore"] = badges()
        assets_json.write_text(json.dumps(meta, indent=2) + "\n")
        return
    if args.mascot:
        mascot()
        refresh_press_kit()
        return
    refresh_press_kit(icons())
    if args.icons_only:
        return
    mascot()
    gp_badges, app_badges = badges()
    meta = {"shots": shots(android_root, ios_today), "googlePlay": gp_badges, "appStore": app_badges, "home": home(),
            "source": {"android": str(android_root.relative_to(PROJECT)), "iosToday": str(ios_today.relative_to(PROJECT))}}
    assets_json.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"assets written to {OUT.relative_to(SITE)}")


if __name__ == "__main__":
    main()
