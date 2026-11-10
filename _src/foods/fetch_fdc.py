#!/usr/bin/env python3
"""Snapshot USDA FoodData Central values for _src/foods/foods.json into _src/foods/fdc.json.

The build reads only the snapshot, so pages never depend on the API being up. Calls go through the video
pipeline's FDC client (marketing/video-pipeline/lib/kcal_check.py: API key from Keychain or DEMO_KEY, shared
rate-limit guard), one batch request per 20 ids.

Usage: python3 _src/foods/fetch_fdc.py [--client <dir with kcal_check.py>]
"""
import argparse
import datetime as dt
import json
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CLIENT = Path.home() / "Projects/Calcalou/marketing/video-pipeline/lib"
NUTRIENTS = {"kcal": ("208", "958", "957"), "protein": ("203",), "fat": ("204",), "carbs": ("205",),
             "fiber": ("291",), "sugars": ("269", "269.3")}


def food_ids(foods):
    return sorted({f["fdc"] for f in foods} | {v["fdc"] for f in foods for v in f["variants"]})


def per_100g(food):
    found = {}
    for n in food.get("foodNutrients", []):
        nutrient = n.get("nutrient") or {}
        number, amount = str(nutrient.get("number", "")), n.get("amount")
        if amount is not None and (nutrient.get("unitName") or "").lower() in ("kcal", "g"):
            found.setdefault(number, float(amount))
    out = {}
    for key, numbers in NUTRIENTS.items():
        out[key] = next((found[n] for n in numbers if n in found), None)
    return out


def portion_label(p):
    unit = (p.get("measureUnit") or {}).get("name", "")
    parts = [p.get("portionDescription"), str(p["amount"]).removesuffix(".0") if p.get("amount") else None,
             unit if unit and unit != "undetermined" else None, p.get("modifier")]
    return " ".join(s for s in parts if s).strip()


def snapshot(food, fetched_at):
    return {"description": food["description"], "data_type": food["dataType"],
            "publication_date": food.get("publicationDate"), "per_100g": per_100g(food),
            "portions": [[portion_label(p), p["gramWeight"]] for p in food.get("foodPortions", [])
                         if p.get("gramWeight")],
            "fetched_at": fetched_at}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", type=Path, default=DEFAULT_CLIENT)
    args = parser.parse_args()
    sys.path.insert(0, str(args.client))
    import kcal_check  # noqa: E402

    foods = json.loads((HERE / "foods.json").read_text(encoding="utf-8"))["foods"]
    client = kcal_check.FdcClient()
    key = kcal_check.fdc_key()
    fetched_at = dt.date.today().isoformat()
    out = {}
    ids = food_ids(foods)
    for start in range(0, len(ids), 20):
        query = urllib.parse.urlencode({"fdcIds": ",".join(map(str, ids[start:start + 20])), "format": "full",
                                        "api_key": key})
        for food in client._call(f"{kcal_check.FDC}/foods?{query}") or []:
            out[str(food["fdcId"])] = snapshot(food, fetched_at)
    missing = [i for i in ids if str(i) not in out]
    if missing:
        raise SystemExit(f"FDC returned no data for {missing}")
    target = HERE / "fdc.json"
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {target.name}: {len(out)} foods, {client.calls} API calls")


if __name__ == "__main__":
    main()
