"""Build the bundled Chinese web fonts used by every video in this project.

Downloads the OFL-licensed sources (Noto Sans SC variable, ZCOOL KuaiLe),
instantiates fixed weights and subsets them to GB2312 + ASCII + common
punctuation, so any simplified-Chinese text renders without tofu boxes.
Run:  python3 scripts/build_fonts.py   (needs: pip install fonttools brotli)
"""
import os
import sys
import urllib.request

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public", "fonts")
CACHE = os.path.join(ROOT, ".font-cache")

SOURCES = {
    "NotoSansSC.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf",
    "ZCOOLKuaiLe.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf",
}


def gb2312_chars() -> str:
    chars = []
    for hi in range(0xB0, 0xF8):
        for lo in range(0xA1, 0xFF):
            try:
                chars.append(bytes([hi, lo]).decode("gb2312"))
            except UnicodeDecodeError:
                pass
    # GB2312 symbol rows (full-width punctuation, digits, letters)
    for hi in range(0xA1, 0xAA):
        for lo in range(0xA1, 0xFF):
            try:
                chars.append(bytes([hi, lo]).decode("gb2312"))
            except UnicodeDecodeError:
                pass
    ascii_ = "".join(chr(c) for c in range(0x20, 0x7F))
    extra = "“”‘’…—–·•≈×÷＋＝→←↑↓★☆♪～！？。，、；：（）《》【】「」『』"
    return ascii_ + extra + "".join(chars)


def fetch(name: str) -> str:
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        print("downloading", SOURCES[name])
        urllib.request.urlretrieve(SOURCES[name], path)
    return path


def write_subset(font: TTFont, text: str, out_name: str) -> None:
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    path = os.path.join(OUT, out_name)
    font.flavor = "woff2"
    font.save(path)
    print(f"{out_name}: {os.path.getsize(path) / 1024:.0f} KiB")


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    text = gb2312_chars()
    noto = fetch("NotoSansSC.ttf")
    for wght in (500, 700, 900):
        f = instancer.instantiateVariableFont(TTFont(noto), {"wght": wght})
        write_subset(f, text, f"NotoSansSC-{wght}.woff2")
    write_subset(TTFont(fetch("ZCOOLKuaiLe.ttf")), text, "ZCOOLKuaiLe.woff2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
