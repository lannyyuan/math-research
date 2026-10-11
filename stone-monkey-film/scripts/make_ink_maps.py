#!/usr/bin/env python3
"""水墨晕染转场用的“显现图”：灰度图，值越小越早显现。从某个点开始，像墨滴在宣纸上洇开（带噪声的边缘）。"""
import sys, pathlib
import numpy as np, cv2
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts/paint'))
from pt import fbm
W, H = 960, 540
OUT = ROOT / 'public/props'
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
specs = {'a': [(0.12, 0.85)], 'b': [(0.5, 0.5)], 'c': [(0.9, 0.3)], 'd': [(0.2, 0.2), (0.8, 0.8)]}
for k, seeds in specs.items():
    d = np.full((H, W), 1e9, np.float32)
    for (sx, sy) in seeds:
        d = np.minimum(d, np.hypot((xx - sx * W) / W, (yy - sy * H) / W))
    d = d / d.max()
    def gn(sig, seed):
        rr = np.random.default_rng(seed)
        a = cv2.GaussianBlur(rr.standard_normal((H, W)).astype(np.float32), (0, 0), sig)
        return (a - a.min()) / (a.max() - a.min())
    n1 = 0.55 * gn(38, 11 + ord(k)) + 0.3 * gn(16, 21 + ord(k)) + 0.15 * gn(6, 31 + ord(k))
    # 域扭曲：让边缘像水渍一样不规则
    wx, wy = gn(30, 5 + ord(k)) - 0.5, gn(30, 9 + ord(k)) - 0.5
    d = cv2.remap(d, xx + wx * 60, yy + wy * 60, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    r = d * 0.62 + n1 * 0.38
    r = (r - r.min()) / (r.max() - r.min())
    cv2.imwrite(str(OUT / f'ink_{k}.png'), (r * 255).astype(np.uint8))
print('ink maps ok')
