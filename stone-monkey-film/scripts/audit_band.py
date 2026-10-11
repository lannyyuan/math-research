#!/usr/bin/env python3
"""字幕带审计：任务书要求“角色和关键动作不能进入字幕带”。
对每条字幕的中点时刻各出两张不带字幕的静帧：A = 全画（角色、道具、动作都在），B = 只有背景和光（chars='none'）。
两张图在字幕带区域（画面 y ≥ 845）的差异就是“压进带里的角色/动作”。差异像素 > 容忍值的字幕会被列出，并存一张对比图。
用法： python3 -I scripts/audit_band.py out/audit_band"""
import json, subprocess, sys, pathlib
import numpy as np
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'out/audit_band')
out.mkdir(parents=True, exist_ok=True)
tl = json.loads((ROOT / 'src/timeline.json').read_text())
# schedule：和 src/schedule.mjs 同一套规则
jobs = []
for sc in tl['scenes']:
    t = sc.get('lead', 1.5)
    for i, c in enumerate(sc['cues']):
        txt = ''.join(c['text'].split())
        d = c.get('d') or round(1.5 + 0.3 * len(txt) + 0.2, 2)
        if i > 0: t += c.get('gap', 0.5)
        if 'at' in c: t = c['at']
        for f in (0.2, 0.55, 0.9):
            jobs.append((sc['id'].split('-')[0], i, round(t + d * f, 2), c['text']))
        t += d
sid = lambda j: f'{j[0]}+{j[2]}'
specA = 'Film:' + ','.join(sid(j) for j in jobs) + '@{"subtitles":false,"chars":true,"audio":false}'
specB = 'Film:' + ','.join(sid(j) for j in jobs) + '@{"subtitles":false,"chars":"none","audio":false}'
for tag, spec in (('A', specA), ('B', specB)):
    d = out / tag
    d.mkdir(exist_ok=True)
    subprocess.run(['node', 'scripts/stills.mjs', spec, '--scale=0.5', f'--out={d}'], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)

def find(d, j):
    c = sorted(d.glob(f'Film-*_{j[0]}*_{j[2]}.png')) or sorted(d.glob(f'Film-*{j[0]}*_{j[2]:g}.png'))
    return c[0] if c else None

bad = []
for j in jobs:
    a, b = find(out / 'A', j), find(out / 'B', j)
    if not a or not b:
        print('missing', j); continue
    ia, ib = np.array(Image.open(a).convert('RGB')).astype(np.int16), np.array(Image.open(b).convert('RGB')).astype(np.int16)
    h = ia.shape[0]
    y0 = int(845 / 1080 * h)
    diff = (np.abs(ia[y0:] - ib[y0:]).max(2) > 28)
    n = int(diff.sum())
    if n > 60:
        bad.append((j, n))
        side = np.hstack([ia.astype(np.uint8), np.where(diff[..., None].repeat(3, 2), 255, 0).astype(np.uint8)[:0].reshape(0, 0, 3)]) if False else ia.astype(np.uint8)
        im = Image.fromarray(side)
        dr = ImageDraw.Draw(im); dr.line([(0, y0), (im.width, y0)], fill=(255, 0, 0), width=2)
        ys, xs = np.where(diff)
        for x, y in zip(xs[::max(len(xs) // 400, 1)], ys[::max(len(xs) // 400, 1)]):
            dr.point((x, y + y0), fill=(255, 0, 255))
        im.save(out / f'BAD_{j[0]}_{j[1]}_{j[2]}.png')
print(f'检查 {len(jobs)} 个时刻；字幕带里有角色/动作的：{len(bad)}')
for j, n in bad:
    print(f'  {j[0]} cue#{j[1]} t={j[2]}s  {n} px  「{j[3]}」')
sys.exit(1 if bad else 0)
