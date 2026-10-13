"""把开源字体「霞鹜文楷」(LXGW WenKai, SIL OFL 1.1) 裁成只含绘本用字的 woff2。

用法：python3 webapp/subset_font.py <weight: regular|bold> <字符文件> <输出.woff2>
需要：pip install fonttools brotli ；npm i（装好 lxgw-wenkai-webfont）
"""
import io, re, sys, pathlib, tempfile, os
from fontTools.ttLib import TTFont
from fontTools import subset, merge

root = pathlib.Path(__file__).resolve().parent.parent
pkg = root / "node_modules/lxgw-wenkai-webfont"


def subset_font(weight: str, chars: set, out: pathlib.Path):
    css = (pkg / f"lxgwwenkai-{weight}.css").read_text(encoding="utf-8")
    slices = []
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
    need, missing = {}, []
    for ch in sorted(chars):
        cp = ord(ch)
        for f, cps in slices:
            if cp in cps:
                need.setdefault(f, set()).add(cp)
                break
        else:
            missing.append(ch)
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
        parts.append(buf.getvalue())
    tmp = []
    for i, b in enumerate(parts):
        p = pathlib.Path(tempfile.gettempdir()) / f"wkb_{weight}_{i}.ttf"
        p.write_bytes(b)
        tmp.append(str(p))
    merged = merge.Merger().merge(tmp)
    merged.flavor = "woff2"
    out.parent.mkdir(parents=True, exist_ok=True)
    merged.save(str(out))
    for p in tmp:
        os.remove(p)
    return missing


if __name__ == "__main__":
    weight, charfile, out = sys.argv[1:4]
    chars = set(pathlib.Path(charfile).read_text(encoding="utf-8"))
    miss = subset_font(weight, chars, pathlib.Path(out))
    print(f"{out}: {pathlib.Path(out).stat().st_size} bytes, 缺字 {miss}")
