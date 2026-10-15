"""Fail if any character shown on screen (string literals / JSON in src) is missing from the bundled fonts.

Noto Sans SC is the fallback of every font stack, so it must contain every displayed glyph;
ZCOOL KuaiLe (titles) may fall back to Noto per glyph, so gaps there are only reported.
"""
import glob
import os
import re
import sys

from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
chars = set()
for f in glob.glob(os.path.join(ROOT, "src", "**", "*.*"), recursive=True):
    if not f.endswith((".ts", ".tsx", ".json")):
        continue
    src = open(f, encoding="utf-8").read()
    if not f.endswith(".json"):
        src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
        src = re.sub(r"(^|[^:])//.*", r"\1", src)
    for lit in re.findall(r'"((?:[^"\\\n]|\\.)*)"|`([^`]*)`', src):
        for ch in "".join(lit):
            if ord(ch) > 0x7F:
                chars.add(ch)
bad = 0
for font in sorted(glob.glob(os.path.join(ROOT, "public", "fonts", "*.woff2"))):
    cmap = TTFont(font).getBestCmap()
    missing = sorted(c for c in chars if ord(c) not in cmap)
    name = os.path.basename(font)
    required = name.startswith("NotoSansSC")
    if missing and required:
        bad += 1
        print(f"  ✗ {name}: missing {''.join(missing)}")
    elif missing:
        print(f"  · {name}: {''.join(missing)} fall back to Noto Sans SC")
    else:
        print(f"  ✓ {name}: all {len(chars)} on-screen characters present")
sys.exit(1 if bad else 0)
