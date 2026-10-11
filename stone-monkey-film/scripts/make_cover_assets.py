#!/usr/bin/env python3
"""从封面（ref/cover.png）里取出片名的书法字：Chinese title → 透明 PNG（奶白字），再做一张“墨晕开”的显现图。"""
import sys, pathlib, json
import numpy as np, cv2
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parent.parent
im = cv2.cvtColor(cv2.imread(str(ROOT / 'ref/cover.png')), cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
OUT = ROOT / 'public/props'; OUT.mkdir(parents=True, exist_ok=True)

def extract(box, name, thr_lo, thr_hi, grow=2):
    x0, y0, x1, y1 = box
    crop = im[y0:y1, x0:x1]
    lum = crop @ np.array([0.299, 0.587, 0.114], np.float32)
    bg = cv2.GaussianBlur(lum, (0, 0), 14)
    top = lum - bg                                    # 高通：只留比周围亮的笔画
    a = np.clip((top - thr_lo) / (thr_hi - thr_lo), 0, 1)
    a = np.maximum(a, np.clip((lum - 0.62) / 0.15, 0, 1))
    lab, n = ndi.label(a > 0.5)
    sizes = ndi.sum(a > 0.5, lab, range(1, n + 1))
    keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= 12])
    a = a * cv2.dilate(keep.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
    a = cv2.GaussianBlur(a, (0, 0), 0.5)
    col = np.array([0.94, 0.91, 0.84], np.float32)     # 纸白 #EFE8D8
    rgba = np.dstack([np.broadcast_to(col, crop.shape), a])
    out = (np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8)
    ys, xs = np.where(a > 0.05)
    ya, yb, xa, xb = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    out = out[ya:yb, xa:xb]
    cv2.imwrite(str(OUT / f'{name}.png'), cv2.cvtColor(out, cv2.COLOR_RGBA2BGRA))
    return a[ya:yb, xa:xb], (x0 + xa, y0 + ya)

a, pos = extract((200, 130, 960, 283), 'title_zh', 0.10, 0.26)
print('title_zh', a.shape, pos)
# 墨晕开的显现图：值越小越早显现。种子点撒在笔画里，按到最近种子的距离 + 噪声
rng = np.random.default_rng(3)
ys, xs = np.where(a > 0.5)
idx = rng.choice(len(ys), 26, replace=False)
seed = np.ones(a.shape, bool)
seed[ys[idx], xs[idx]] = False
d = ndi.distance_transform_edt(seed).astype(np.float32)
d = d / d.max()
sys.path.insert(0, str(pathlib.Path(__file__).parent / 'paint'))
from pt import fbm
n = fbm(a.shape[0], a.shape[1], 7, 28, 4, 0.55, warp=14)
reveal = np.clip(d * 0.78 + n * 0.30, 0, 1)
reveal = (reveal - reveal.min()) / (reveal.max() - reveal.min())
cv2.imwrite(str(OUT / 'title_zh_reveal.png'), (reveal * 255).astype(np.uint8))
b, pos2 = extract((300, 282, 820, 322), 'title_en', 0.08, 0.2)
print('title_en', b.shape, pos2)
meta = {'title_zh': {'w': int(a.shape[1]), 'h': int(a.shape[0]), 'src': [int(pos[0]), int(pos[1])]}, 'title_en': {'w': int(b.shape[1]), 'h': int(b.shape[0]), 'src': [int(pos2[0]), int(pos2[1])]}}
(OUT / 'title.json').write_text(json.dumps(meta, indent=1))
