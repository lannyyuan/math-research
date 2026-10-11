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

# 5. 石娃坐姿用的两截：上身（到衣摆）+ 腿（可绕髋转到水平向前）。纸偶的“局部关节转动”
rgb, a = load('shiwa_side')
HIP = 238
up_rgb, up_a = rgb[:HIP + 2], a[:HIP + 2].copy()
up_a[HIP - 2:] *= np.linspace(1, 0, 4)[:up_a[HIP - 2:].shape[0], None]      # 下沿柔一点，盖在腿上
save('shiwa_side_up', up_rgb, up_a, anchor=(meta['shiwa_side']['ax'] + 8, HIP - 4))
leg_rgb, leg_a = rgb[HIP - 8:], a[HIP - 8:]
save('shiwa_side_leg', leg_rgb, leg_a, anchor=(meta['shiwa_side']['ax'] + 8, 10))
# 6. 石娃的近侧手臂单独成一块（绕肩转动：敲鼓、挥手、递东西），身体上把手臂的位置补成衣服
rgb, a = load('shiwa_side')
ARM = np.array([(50, 128), (80, 126), (87, 170), (89, 205), (92, 240), (88, 257), (62, 257), (56, 226), (42, 206), (45, 170)], np.float32)
am = np.zeros(a.shape, np.uint8)
cv2.fillPoly(am, [np.round(ARM).astype(np.int32)], 255, lineType=cv2.LINE_AA)
amf = cv2.GaussianBlur(am.astype(np.float32) / 255.0, (0, 0), 0.8)
arm_a = a * amf
ys, xs = np.where(arm_a > 0.02)
y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
arm_rgb = rgb[y0:y1, x0:x1]
save('shiwa_side_arm', arm_rgb, arm_a[y0:y1, x0:x1], anchor=(65.0 - x0, 138.0 - y0))      # 锚点 = 肩关节
hole = cv2.dilate(am, np.ones((3, 3), np.uint8))
fill0 = cv2.inpaint((rgb * 255).astype(np.uint8), hole, 6, cv2.INPAINT_TELEA).astype(np.float32) / 255.0
fill0 = cv2.GaussianBlur(fill0, (0, 0), 0.7)
# 用周围布料的平均色 + 噪点 + 几块深浅污渍去补躯干和手后面的那一块（比镜像平铺自然）
H_, W_ = rgb.shape[:2]
fillc = fill0.copy()
rr = np.random.default_rng(4)
def flat_fill(color, region_mask, noise=0.07, smudges=3, smudge_col=None):
    out = np.zeros_like(rgb) + color
    g = cv2.GaussianBlur(rr.standard_normal(rgb.shape[:2]).astype(np.float32), (0, 0), 0.9)[..., None] * noise
    out = out * (1 + g)
    for _ in range(smudges):
        cx, cy = rr.uniform(48, 84), rr.uniform(140, 205)
        m_ = np.zeros(rgb.shape[:2], np.float32)
        cv2.ellipse(m_, (int(cx), int(cy)), (int(rr.uniform(4, 9)), int(rr.uniform(5, 12))), rr.uniform(0, 180), 0, 360, 1.0, -1)
        m_ = cv2.GaussianBlur(m_, (0, 0), 2.0)[..., None] * 0.35
        out = out * (1 - m_) + (smudge_col if smudge_col is not None else color * 0.7) * m_
    return np.where(region_mask[..., None], out, 0)
yy_, xx_ = np.mgrid[0:H_, 0:W_]
reg_j = (hole > 0) & (yy_ < 213)
reg_h = (hole > 0) & (yy_ >= 213) & (yy_ < 228)
reg_p = (hole > 0) & (yy_ >= 228)
jc = np.median(rgb[138:172, 54:72].reshape(-1, 3), 0)
hc = np.median(rgb[216:226, 88:100].reshape(-1, 3), 0)
pc = np.median(rgb[246:268, 32:56].reshape(-1, 3), 0)
fillc = np.where(reg_j[..., None], flat_fill(jc, reg_j), fillc)
fillc = np.where(reg_h[..., None], flat_fill(hc, reg_h, 0.05, 1, hc * 0.8), fillc)
fillc = np.where(reg_p[..., None], flat_fill(pc, reg_p, 0.07, 2, pc * 0.7), fillc)
# 填补处和周围衣服的接缝：做个小羽化
hm = cv2.GaussianBlur(hole.astype(np.float32) / 255.0, (0, 0), 1.2)[..., None]
fillc = fillc * hm + rgb * (1 - hm)
fillc = np.where(hole[..., None] > 0, 0.85 * fillc + 0.15 * fill0, fillc)
body_a = a.copy()
nb = np.where(am[..., None] > 0, fillc, rgb)
save('shiwa_side_noarm', nb, body_a, anchor=(meta['shiwa_side']['ax'], meta['shiwa_side']['ay']))
(SP / 'sprites.json').write_text(json.dumps(meta, indent=1))
print(len(meta), 'sprites (derived)')
