#!/usr/bin/env python3
"""Check one new site language: python3 _src/tools/check_translation.py <code> [...]

Compares every translated file with its English twin: same keys and structure, same {placeholders}, links,
digits and brand names, no untranslated English, sane length, plus the i18n/meta/<code>.json slugs.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
I18N = SRC / "i18n"
FILES = ["", "home2/", "calc/", "deficit/", "protein/", "tdee/", "protein-landing/", "terms/", "acq/"]
BRANDS = ["Calcalou", "Lou"]
SLUGS = ["bmr", "tdee", "deficit", "protein", "what_is", "protein_landing"]
TOKEN = re.compile(r"\{[a-z_]+\}|\]\((?:/|https?://)[^)]*\)")
DIGITS = re.compile(r"\d+")
GROUPING = re.compile(r"(?<=\d)[.,\u00a0\u202f\u2009 ](?=\d)")
SKIP_SAME = re.compile(r"^[\W\d_]*$|^(Calcalou|Lou|GoodPick Media|App Store|Google Play|Premium|CSV|kcal|BMR|TDEE|AI|iOS|Android)\b[\w .,&:-]*$")


def english(name):
    if name == "acq/":
        return json.loads((SRC / "acquisition.json").read_text(encoding="utf-8"))["en"]
    return json.loads((I18N / f"{name}en.json").read_text(encoding="utf-8"))


def leaves(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from leaves(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, str(node)


def check(code):
    errors = []
    for name in FILES:
        target = I18N / f"{name}{code}.json"
        if not target.exists():
            errors.append(f"{name}{code}.json missing")
            continue
        en, tr = english(name), json.loads(target.read_text(encoding="utf-8"))
        if name in ("protein-landing/", "acq/"):
            for skip in ("path", "name", "home"):
                en.pop(skip, None)
                tr.pop(skip, None)
        en_leaves, tr_leaves = dict(leaves(en)), dict(leaves(tr))
        if set(en_leaves) != set(tr_leaves):
            errors.append(f"{name}{code}.json: structure differs ({len(set(en_leaves) ^ set(tr_leaves))} keys)")
            continue
        for key, source in en_leaves.items():
            value = tr_leaves[key]
            where = f"{name}{code}.json{key}"
            if not value.strip():
                errors.append(f"{where}: empty")
                continue
            if sorted(TOKEN.findall(source)) != sorted(TOKEN.findall(value)):
                errors.append(f"{where}: placeholders or links differ: {TOKEN.findall(source)} vs {TOKEN.findall(value)}")
            extra = Counter(DIGITS.findall(GROUPING.sub("", value))) - Counter(DIGITS.findall(GROUPING.sub("", source)))
            if extra:
                errors.append(f"{where}: numbers not in the English source: {sorted(extra)}")
            for brand in BRANDS:
                if re.search(rf"\b{brand}\b", source) and brand not in value:
                    errors.append(f"{where}: brand {brand} missing")
            if value == source and len(source.split()) >= 3 and not SKIP_SAME.match(source):
                errors.append(f"{where}: untranslated English")
            if len(source) > 30 and not 0.35 <= len(value) / len(source) <= 3.2:
                errors.append(f"{where}: length ratio {len(value) / len(source):.2f}")
            if re.search(r"<[a-z]", value) != re.search(r"<[a-z]", source):
                errors.append(f"{where}: markup differs")
    meta = I18N / "meta" / f"{code}.json"
    if meta.exists():
        m = json.loads(meta.read_text(encoding="utf-8"))
        for slug in SLUGS:
            value = m.get("slugs", {}).get(slug, "")
            if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", value):
                errors.append(f"meta/{code}.json: slug {slug} {value!r} is not ascii-kebab")
        if len({m["slugs"].get(s) for s in SLUGS}) != len(SLUGS):
            errors.append(f"meta/{code}.json: slugs not unique")
    return errors


if __name__ == "__main__":
    bad = 0
    for code in sys.argv[1:]:
        problems = check(code)
        bad += bool(problems)
        print(f"{code}: {'OK' if not problems else str(len(problems)) + ' problems'}")
        for p in problems[:40]:
            print("  ", p)
    sys.exit(1 if bad else 0)
