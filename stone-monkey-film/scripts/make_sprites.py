#!/usr/bin/env python3
"""在 extract_sprites.py 抠出来的精灵之上做派生：
  · pearl：从设定表里取出宝珠的球体（去掉下面的黑石头）；
  · drum：金鼓降饱和（任务书：金鼓不能抢光源，往灰金走），红穗子也压成土红；
  · *_red：奶奶的红头绳（红色是允许的暖色之一，夜色里也要保留）；
  · houzi_*_eyes：龟甲眼睛里的火星（夜色里也亮）；
  · 每个精灵的夜色版 <name>_night.png（靛蓝色带），写进 sprites.json。
"""
import json, pathlib, sys
import numpy as np, cv2
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts/paint'))
import grade
SP = ROOT / 'public/sprites'
meta = json.loads((SP / 'sprites.json').read_text())
sheet = cv2.cvtColor(cv2.imread(str(ROOT / 'out/sheet_retouched.png')), cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0


def load(n):
    im = cv2.cvtColor(cv2.imread(str(SP / f'{n}.png'), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA).astype(np.float32) / 255.0
    return im[..., :3], im[..., 3]


def save(n, rgb, a, anchor=None, night=True):
    out = (np.clip(np.dstack([rgb, a]), 0, 1) * 255 + 0.5).astype(np.uint8)
    cv2.imwrite(str(SP / f'{n}.png'), cv2.cvtColor(out, cv2.COLOR_RGBA2BGRA))
    h, w = a.shape
    m = meta.get(n, {})
    m.update({'w': w, 'h': h})
    if anchor:
        m['ax'], m['ay'] = anchor
    m['night'] = night
    meta[n] = m


def lum(rgb):
    return rgb @ np.array([0.299, 0.587, 0.114], np.float32)


# 1. 宝珠：圆心 (203,708) 半径 72
cx, cy, R = 203.0, 708.0, 72.5
x0, y0 = int(cx - R - 3), int(cy - R - 3)
crop = sheet[y0:y0 + 156, x0:x0 + 156].copy()
yy, xx = np.mgrid[0:crop.shape[0], 0:crop.shape[1]]
d = np.hypot(xx + x0 - cx, yy + y0 - cy)
circle = np.clip((R + 1.0 - d) / 2.0, 0, 1).astype(np.float32)
dark = (lum(crop) < 0.62) & (yy + y0 > cy + 0.25 * R) & (d < R + 4)
dark = cv2.dilate(dark.astype(np.uint8), np.ones((5, 5), np.uint8))
fixed = cv2.inpaint((crop * 255).astype(np.uint8), dark, 9, cv2.INPAINT_TELEA).astype(np.float32) / 255.0
fixed = cv2.GaussianBlur(fixed, (0, 0), 0.6) * dark[..., None] + crop * (1 - dark[..., None])
save('pearl', fixed, circle, anchor=(crop.shape[1] / 2, crop.shape[0] / 2), night=False)

# 2. 金鼓降饱和
rgb, a = load('drum')
l = lum(rgb)[..., None]
rgb2 = l + (rgb - l) * 0.46
rgb2 = rgb2 * np.array([0.97, 0.96, 0.93], np.float32)
save('drum', rgb2, a)

# 3. 红色（奶奶的头绳）
for n in ('nainai_front', 'nainai_side'):
    rgb, a = load(n)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    red = np.clip((r - np.maximum(g, b) * 1.45 - 0.05) / 0.12, 0, 1) * a
    red = cv2.GaussianBlur(red, (0, 0), 0.6)
    save(n + '_red', rgb, red, anchor=(meta[n]['ax'], meta[n]['ay']), night=False)

# 4. 龟甲眼睛的火星
for n in ('houzi_front', 'houzi_side'):
    rgb, a = load(n)
    hsv = cv2.cvtColor((rgb * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[..., 0] * 2, hsv[..., 1] / 255, hsv[..., 2] / 255
    eye = ((h > 28) & (h < 58) & (s > 0.5) & (v > 0.6)).astype(np.float32) * a
    eye = cv2.GaussianBlur(eye, (0, 0), 0.7)
    # 往“火星色”偏一点（橙黄）
    rgb2 = np.clip(rgb * np.array([1.0, 0.9, 0.7], np.float32), 0, 1)
    save(n + '_eyes', rgb2, eye, anchor=(meta[n]['ax'], meta[n]['ay']), night=False)

(SP / 'sprites.json').write_text(json.dumps(meta, indent=1))
print(len(meta), 'sprites (derived)')
