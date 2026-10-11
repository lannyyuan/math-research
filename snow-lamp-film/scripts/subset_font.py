"""把开源字体「霞鹜文楷」(LXGW WenKai, SIL OFL 1.1) 裁成只含字幕用字的小文件。

需要：pip install fonttools brotli ；以及 npm i（装好 lxgw-wenkai-webfont）。
输入：story/subtitle-chars.txt（由 scripts/check-subtitles.mjs 生成）
输出：public/fonts/WenKai-subtitle.woff2 + public/fonts/OFL.txt
"""
import io, re, sys, pathlib
from fontTools.ttLib import TTFont
from fontTools import subset, merge

root = pathlib.Path(__file__).resolve().parent.parent
pkg = root / "node_modules/lxgw-wenkai-webfont"
chars = set((root / "story/subtitle-chars.txt").read_text(encoding="utf-8"))
chars |= set("0123456789：；、“”‘’（）—· ") | set("雪地里的那盏灯")

css = (pkg / "lxgwwenkai-regular.css").read_text(encoding="utf-8")
slices = []  # (file, set(codepoints))
for m in re.finditer(r"url\('\./files/([^']+)'\).*?unicode-range:\s*([^}]+)\}", css, re.S):
    cps = set()
    for part in m.group(2).strip().rstrip(";").split(","):
        part = part.strip().lstrip("Uu+")
        if "-" in part:
            a, b = part.split("-")
            cps.update(range(int(a, 16), int(b, 16) + 1))
        elif part:
            cps.add(int(part, 16))
    slices.append((m.group(1), cps))

need = {}
missing = []
for ch in sorted(chars):
    cp = ord(ch)
    for f, cps in slices:
        if cp in cps:
            need.setdefault(f, set()).add(cp)
            break
    else:
        missing.append(ch)
print("需要的切片:", len(need), "缺字:", missing)

parts = []
for f, cps in need.items():
    font = TTFont(str(pkg / "files" / f))
    opts = subset.Options()
    opts.layout_features = ["*"]
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=sorted(cps))
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = None
    font.save(buf)
    buf.seek(0)
    parts.append(buf)

# fontTools.merge 需要文件路径
import tempfile, os
tmp = []
for i, b in enumerate(parts):
    p = pathlib.Path(tempfile.gettempdir()) / f"wk_part_{i}.ttf"
    p.write_bytes(b.getvalue())
    tmp.append(str(p))
merged = merge.Merger().merge(tmp)
merged.flavor = "woff2"
out = root / "public/fonts"
out.mkdir(parents=True, exist_ok=True)
merged.save(str(out / "WenKai-subtitle.woff2"))
(out / "OFL.txt").write_text((pkg / "OFL.txt").read_text(encoding="utf-8"), encoding="utf-8")
for p in tmp:
    os.remove(p)
print("写出", out / "WenKai-subtitle.woff2", (out / "WenKai-subtitle.woff2").stat().st_size, "bytes")
