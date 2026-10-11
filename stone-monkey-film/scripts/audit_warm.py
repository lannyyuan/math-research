#!/usr/bin/env python3
"""暖色审计：只出背景 + 光 + 发光的道具（chars=false：不画角色和字幕；宝珠、篝火、红布包仍然画），逐帧找“暖色像素”
（色相 8°~62°、饱和度 ≥ 0.30、明度 ≥ 0.42），把它们标成洋红色拼成联系表，人眼核对：
任务书允许的暖色只有：宝珠的光、龟甲的眼睛、篝火和火种、奶奶的红头绳和红布包、小姑娘的红裙（面积很小）；
其余东西（金鼓、国王的衣服、神的金光……）必须是低饱和的灰金/土黄。灯亮以后（第六部后半、尾声）解除夜色色板，红霞/紫霞是允许的，不在检查范围。
用法： python3 -I scripts/audit_warm.py out/audit"""
import json, subprocess, sys, pathlib, colorsys
import numpy as np
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'out/audit')
out.mkdir(parents=True, exist_ok=True)
tl = json.loads((ROOT / 'src/timeline.json').read_text())
jobs, labels = [], []
for sc in tl['scenes']:
    sid = sc['id'].split('-')[0]
    for f in (0.12, 0.3, 0.5, 0.7, 0.9):
        t = round(sc['len'] * f, 1)
        jobs.append(f'{sid}+{t}'); labels.append((sc['id'], t))
spec = 'Film:' + ','.join(jobs) + '@{"subtitles":false,"chars":false,"audio":false}'
subprocess.run(['node', 'scripts/stills.mjs', spec, '--scale=0.5', f'--out={out}'], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)

def warm_mask(rgb):
    x = rgb.astype(np.float32) / 255
    mx, mn = x.max(2), x.min(2)
    d = mx - mn + 1e-6
    s = d / (mx + 1e-6)
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return (h >= 8) & (h <= 62) & (s >= 0.30) & (mx >= 0.42)

tiles, rows = [], []
for (sid, t), j in zip(labels, jobs):
    key = j.split('+')[0]
    cand = sorted(out.glob(f'Film-*{key}*_{t}.png')) or sorted(out.glob(f'Film-*{key}*_{int(t)}.png'))
    cand = [c for c in cand if c.stem.split('_')[-1] in (str(t), str(int(t)) if t == int(t) else str(t))]
    if not cand:
        print('missing', j); continue
    im = np.array(Image.open(cand[0]).convert('RGB'))
    m = warm_mask(im)
    frac = m.mean() * 100
    rows.append((sid, t, frac))
    vis = (im * 0.45).astype(np.uint8)
    vis[m] = (255, 0, 255)
    tiles.append((Image.fromarray(vis), f'{sid} +{t}s  warm={frac:.2f}%'))
cols, tw = 4, 480
th = int(tw * 9 / 16)
sheet = Image.new('RGB', (cols * (tw + 4) + 4, ((len(tiles) + cols - 1) // cols) * (th + 4) + 4), (20, 20, 30))
for k, (im, lab) in enumerate(tiles):
    im = im.resize((tw, th))
    ImageDraw.Draw(im).text((6, 4), lab, fill=(255, 255, 0))
    sheet.paste(im, (4 + (k % cols) * (tw + 4), 4 + (k // cols) * (th + 4)))
sheet.save(out / 'warm-sheet.png')
print('\n'.join(f'{a:14s} +{b:5.1f}s  warm {c:5.2f}%' for a, b, c in rows))
print('->', out / 'warm-sheet.png')
