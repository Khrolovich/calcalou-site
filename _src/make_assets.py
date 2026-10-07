#!/usr/bin/env python3
"""Import images into /assets from the Calcaloo project (approved mascot renders,
store screenshots, app icon, store badges). Re-run when the final store screenshots land:

    python3 _src/make_assets.py [--shots <dir with android-phone/<locale>/ and ios-iphone/en-US/>]
"""
import argparse
import json
import shutil
from pathlib import Path

from PIL import Image

SITE = Path(__file__).resolve().parent.parent
PROJECT = SITE.parent.parent
OUT = SITE / "assets" / "img"
MASCOT = PROJECT / "design" / "mascot" / "reference" / "3d-png"
ICON = PROJECT / "worktrees" / "release-1.4" / "ios" / "Runner" / "Assets.xcassets" / "AppIcon.appiconset" / "Icon-App-1024x1024@1x.png"
SHOTS_ANDROID = PROJECT / "qa-runs" / "1.4.0-65-store-screenshots" / "raw" / "android-phone"
SHOT_IOS_TODAY = PROJECT / "qa-runs" / "1.4.0-65-store-screenshots-v2" / "samples" / "ios-iphone" / "en-US" / "iphone69_01_today.png"
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
    union = None
    for f in MASCOT.glob("mascot_*.png"):
        b = Image.open(f).getbbox()
        union = b if union is None else (min(union[0], b[0]), min(union[1], b[1]), max(union[2], b[2]), max(union[3], b[3]))
    for mood in MOODS:
        img = Image.open(MASCOT / f"mascot_{mood}.png").convert("RGBA").crop(union)
        for w in (240, 480, 760):
            save_both(resized(img, w), f"lou-{mood}-{w}", 82)
    return union


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


def badges():
    meta = {}
    shutil.copy(BADGES / "app-store-en.svg", OUT / "badge-app-store.svg")
    for png in BADGES.glob("google-play-*.png"):
        img = Image.open(png).convert("RGBA")
        img = img.crop(img.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox())
        lang = png.stem.replace("google-play-", "")
        for height in (50, 100):
            scaled = img.resize((round(img.width * height / img.height), height), Image.LANCZOS)
            scaled.save(OUT / f"badge-google-play-{lang}-{height}.webp", quality=90, method=6)
        meta[lang] = [round(img.width * 50 / img.height), 50]
    return meta


def icons():
    icon = Image.open(ICON).convert("RGB")
    for size, name in ((48, "favicon-48.png"), (180, "apple-touch-icon.png"), (96, "app-icon-96.png")):
        icon.resize((size, size), Image.LANCZOS).save(OUT / name, optimize=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shots", type=Path, help="screenshot set root (android-phone/<locale>/, ios-iphone/en-US/)")
    args = parser.parse_args()
    android_root, ios_today = SHOTS_ANDROID, SHOT_IOS_TODAY
    if args.shots:
        android_root = args.shots / "android-phone"
        ios_today = args.shots / "ios-iphone" / "en-US" / "iphone69_01_today.png"
    OUT.mkdir(parents=True, exist_ok=True)
    mascot()
    icons()
    meta = {"shots": shots(android_root, ios_today), "googlePlay": badges(),
            "source": {"android": str(android_root.relative_to(PROJECT)), "iosToday": str(ios_today.relative_to(PROJECT))}}
    (Path(__file__).resolve().parent / "assets.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"assets written to {OUT.relative_to(SITE)}")


if __name__ == "__main__":
    main()
