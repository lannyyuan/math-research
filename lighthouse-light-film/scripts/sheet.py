#!/usr/bin/env python3
"""把若干张静帧拼成一张联系表（带文件名），用来一眼检查多个镜头。
用法： python3 scripts/sheet.py out/sheet.png out/stills/a.png out/stills/b.png ... [--cols=2] [--w=800]"""
import sys, pathlib
from PIL import Image, ImageDraw
args = [a for a in sys.argv[1:] if not a.startswith('--')]
opt = dict(a[2:].split('=') for a in sys.argv[1:] if a.startswith('--'))
out, files = args[0], args[1:]
cols = int(opt.get('cols', 2)); tw = int(opt.get('w', 800))
ims = []
for f in files:
    im = Image.open(f).convert('RGB'); r = tw / im.width
    im = im.resize((tw, int(im.height * r)), Image.LANCZOS)
    ImageDraw.Draw(im).text((8, 6), pathlib.Path(f).stem, fill=(255, 255, 0))
    ims.append(im)
rows = (len(ims) + cols - 1) // cols
th = max(i.height for i in ims)
sheet = Image.new('RGB', (cols * tw + (cols + 1) * 6, rows * th + (rows + 1) * 6), (20, 20, 30))
for k, im in enumerate(ims):
    sheet.paste(im, (6 + (k % cols) * (tw + 6), 6 + (k // cols) * (th + 6)))
sheet.save(out)
print(out, sheet.size)
