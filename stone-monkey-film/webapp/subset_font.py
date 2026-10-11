"""把开源字体「霞鹜文楷」(LXGW WenKai, SIL OFL 1.1) 裁成只含绘本用字的小文件。

用法：python3 -I webapp/subset_font.py <weight: regular|bold> <字符文件> <输出.woff2>
需要：fonttools、brotli（pip）；node_modules/lxgw-wenkai-webfont（npm i 装好；本工程的 node_modules 指向 lighthouse-light-film 的）。
build.py 直接 import subset_font() / subset_ttf_bytes() 来用。
"""
import io, pathlib, re, sys, tempfile
from fontTools.ttLib import TTFont
from fontTools import subset, merge

root = pathlib.Path(__file__).resolve().parent.parent
pkg = root / "node_modules" / "lxgw-wenkai-webfont"


def _slices(weight: str):
    css = (pkg / f"lxgwwenkai-{weight}.css").read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"url\('\./files/([^']+)'\).*?unicode-range:\s*([^}]+)\}", css, re.S):
        cps = set()
        for part in m.group(2).strip().rstrip(";").split(","):
            part = part.strip().lstrip("Uu+")
            if "-" in part:
                a, b = part.split("-")
                cps.update(range(int(a, 16), int(b, 16) + 1))
            elif part:
                cps.add(int(part, 16))
        out.append((m.group(1), cps))
    return out


def subset_ttf_bytes(weight: str, chars: set):
    """→ (合并后的 TTF 字节, 字体里没有的字符列表)。"""
    slices = _slices(weight)
    need, missing = {}, []
    for ch in sorted(chars):
        cp = ord(ch)
        for f, cps in slices:
            if cp in cps:
                need.setdefault(f, set()).add(cp)
                break
        else:
            missing.append(ch)
    with tempfile.TemporaryDirectory() as td:
        files = []
        for i, (f, cps) in enumerate(need.items()):
            font = TTFont(str(pkg / "files" / f))
            opts = subset.Options()
            opts.layout_features = ["*"]
            opts.notdef_outline = True
            sub = subset.Subsetter(opts)
            sub.populate(unicodes=sorted(cps))
            sub.subset(font)
            p = pathlib.Path(td) / f"part{i}.ttf"
            font.flavor = None
            font.save(str(p))
            files.append(str(p))
        merged = merge.Merger().merge(files)
        merged.flavor = None
        buf = io.BytesIO()
        merged.save(buf)
    return buf.getvalue(), missing


def subset_font(weight: str, chars: set, out: pathlib.Path):
    """裁成 woff2 写到 out，返回缺字列表。"""
    data, missing = subset_ttf_bytes(weight, chars)
    f = TTFont(io.BytesIO(data))
    f.flavor = "woff2"
    out.parent.mkdir(parents=True, exist_ok=True)
    f.save(str(out))
    return missing


if __name__ == "__main__":
    weight, charfile, out = sys.argv[1:4]
    chars = set(pathlib.Path(charfile).read_text(encoding="utf-8"))
    miss = subset_font(weight, chars, pathlib.Path(out))
    print(f"{out}: {pathlib.Path(out).stat().st_size} bytes, 缺字 {miss}")
