#!/usr/bin/env python3
"""Bud 的三种头饰状态（剧情要求前后一致）：
   · 戴棒球帽（第 1~2 章，之后把帽子给了雪人）  → bud_*_bare + bud_cap_*
   · 不戴帽子（第 2~7 章、第 8 章起）           → bud_*_bare（头发是我们补画的）
   · 戴毛线帽（农场里农夫给的，设定图的样子）   → bud_*_bare + bud_hat_*（就是设定图原样）
设定图里 Bud 只有“戴毛线帽”这一种，所以：把帽子的像素抠出来单独存成一层（bud_hat_*），
把露出来的头顶用水彩补画成头发（bud_*_bare）；棒球帽是另外画的一层（bud_cap_*）。
所有层的画布大小和原精灵一样，叠放时位置自然对上。
"""
import json, pathlib, sys
import numpy as np, cv2
sys.path.insert(0, str(pathlib.Path(__file__).parent / 'paint'))
from pt import *  # noqa
from world import rgbmix  # noqa

ROOT = pathlib.Path(__file__).resolve().parent.parent
SP = ROOT / 'public/sprites'

# ───── 多边形（精灵坐标）─────
FRONT_HAT = [(40, 128), (40, 100), (43, 80), (48, 60), (44, 40), (40, 20), (50, 0), (130, 0), (136, 22), (150, 30), (166, 46), (176, 66), (178, 86), (175, 108), (172, 128)]
FRONT_KEEP = [(58, 102), (66, 96), (70, 88), (76, 78), (86, 68), (100, 63), (114, 64), (128, 68), (140, 76), (150, 88), (156, 98), (164, 104), (171, 112), (169, 124), (158, 132), (150, 142), (130, 152), (100, 154), (76, 148), (66, 138), (60, 128), (56, 116)]
FRONT_HAIR = [(56, 112), (53, 92), (58, 70), (72, 52), (92, 40), (114, 37), (136, 43), (154, 58), (166, 80), (168, 108), (160, 108), (150, 90), (140, 78), (128, 70), (114, 66), (100, 66), (86, 72), (76, 82), (68, 94), (62, 106)]
SIDE_HAT = [(0, 0), (66, 0), (70, 20), (80, 18), (104, 16), (126, 20), (144, 32), (153, 50), (146, 62), (130, 78), (112, 96), (92, 112), (76, 126), (56, 134), (40, 132), (30, 110), (28, 84), (30, 70), (0, 100)]
SIDE_KEEP = [(150, 46), (132, 70), (114, 90), (94, 108), (74, 124), (56, 134), (64, 142), (110, 152), (152, 152), (162, 122), (163, 70), (158, 46)]
SIDE_HAIR = [(64, 130), (56, 112), (54, 92), (62, 70), (78, 54), (100, 44), (124, 42), (144, 46), (155, 52), (142, 62), (124, 78), (106, 96), (90, 112), (78, 126)]
HAIR_COL = hexc('#7a5431')


def load(name):
    im = cv2.cvtColor(cv2.imread(str(SP / f'{name}.png'), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA).astype(np.float32) / 255
    return im


def save(name, rgba):
    out = (np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8)
    cv2.imwrite(str(SP / f'{name}.png'), cv2.cvtColor(out, cv2.COLOR_RGBA2BGRA))


def polymask(h, w, pts, ss=4):
    big = np.zeros((h * ss, w * ss), np.uint8)
    cv2.fillPoly(big, [np.round(np.asarray(pts, np.float32) * ss).astype(np.int32)], 255, lineType=cv2.LINE_AA)
    return cv2.resize(big, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def paint_hair(L, poly, seed, base_col, dome_center):
    """头发：照原图里刘海的颜色，密密的两色发丝 + 细墨线轮廓 + 毛躁的外轮廓。"""
    r = np.random.default_rng(seed)
    P_ = np.asarray(poly, np.float32)
    cx, cy = dome_center
    # 外轮廓加一点不规则（毛躁）
    P2 = []
    for q in chaikin(P_, 2, True):
        d = q - np.array([cx, cy], np.float32)
        P2.append(q + d / (np.hypot(*d) + 1e-6) * r.normal(0, 2.2))
    P2 = np.array(P2, np.float32)
    dk = rgbmix(base_col, hexc('#2e1d10'), 0.55)
    lt = rgbmix(base_col, hexc('#d9a971'), 0.5)
    wash(L, P2, base_col, op=1.0, wob=0.8, seed=seed, smooth=0, tex_k=0.24, rim=0.2, rim_w=1.6)
    xs, ys = P_[:, 0], P_[:, 1]
    rx, ry = (xs.max() - xs.min()) / 2, (ys.max() - ys.min()) / 2
    for i in range(170):
        a = r.uniform(-math.pi * 1.05, math.pi * 0.05)
        r0, r1 = r.uniform(0.05, 0.6), r.uniform(0.75, 1.02)
        pts = [(cx + math.cos(a + t * 0.18) * rx * (r0 + (r1 - r0) * t), cy + math.sin(a + t * 0.18) * ry * (r0 + (r1 - r0) * t)) for t in (0, 0.5, 1)]
        col = dk if r.random() < 0.55 else lt
        ink(L, pts, w0=r.uniform(0.9, 1.6), color=col, op=r.uniform(0.35, 0.7), seed=int(r.integers(1e6)), wob=0.3, taper=0.45)
    ink(L, np.vstack([P2, P2[:1]]), w0=1.3, color=hexc('#3a2616'), op=0.8, seed=seed + 9, wob=0.5, taper=0.15)
    for i in range(10):
        k = int(r.integers(0, len(P2)))
        q = P2[k]
        out = q - np.array([cx, cy], np.float32); out = out / (np.hypot(*out) + 1e-6)
        ln = r.uniform(4, 9)
        ink(L, [q - out * 2, q + out * ln * 0.5 + np.array([r.normal(0, 1.5), 0]), q + out * ln], w0=1.5, color=hexc('#5a3a22'), op=0.9, seed=int(r.integers(1e6)), wob=0.3, taper=0.5)


def cap_front(h, w):
    L = Canvas(w, h)
    navy, navy_dk = hexc('#2f4172'), hexc('#1f2c52')
    dome = [(56, 78), (54, 58), (64, 40), (84, 27), (106, 22), (130, 27), (150, 40), (160, 58), (160, 78), (130, 74), (104, 72), (78, 74)]
    wash(L, dome, navy, op=1.0, wob=0.8, seed=3, smooth=2, tex_k=0.2, rim=0.2, rim_w=2.0)
    wash(L, [(104, 24), (130, 30), (150, 48), (156, 72), (140, 62), (122, 40)], hexc('#4b5f95'), op=0.45, wob=0.6, seed=4, smooth=2)
    for k, x in enumerate((78, 104, 130)):
        ink(L, [(104, 22), (104 + (x - 104) * 0.6, 50), (x, 86)], w0=1.0, color=navy_dk, op=0.55, seed=10 + k, wob=0.3)
    dots(L, [(104, 22, 4)], hexc('#4b5f95'), 1.0)
    brim = [(54, 72), (104, 80), (160, 72), (166, 78), (152, 85), (104, 89), (56, 85), (46, 78)]
    wash(L, brim, navy_dk, op=1.0, wob=0.7, seed=5, smooth=2, tex_k=0.2, rim=0.2, rim_w=2.0)
    ink(L, np.vstack([brim, brim[:1]]), w0=1.3, color=hexc('#141b36'), op=0.8, seed=6, wob=0.5, taper=0.1, smooth=False)
    ink(L, [(56, 74), (80, 78), (104, 80), (130, 78), (158, 74)], w0=1.0, color=hexc('#4b5f95'), op=0.5, seed=7, wob=0.3)
    return L


def cap_side(h, w):
    L = Canvas(w, h)
    navy, navy_dk = hexc('#2f4172'), hexc('#1f2c52')
    dome = [(56, 100), (50, 78), (58, 52), (80, 34), (108, 30), (132, 38), (148, 54), (150, 70), (130, 66), (100, 76), (76, 94)]
    wash(L, dome, navy, op=1.0, wob=0.8, seed=13, smooth=2, tex_k=0.2, rim=0.2, rim_w=2.0)
    wash(L, [(82, 36), (108, 32), (132, 40), (146, 56), (120, 48), (96, 52)], hexc('#4b5f95'), op=0.45, wob=0.6, seed=14, smooth=2)
    ink(L, [(108, 30), (100, 54), (80, 92)], w0=1.0, color=navy_dk, op=0.55, seed=15, wob=0.3)
    dots(L, [(108, 30, 4)], hexc('#4b5f95'), 1.0)
    brim = [(128, 62), (150, 64), (172, 74), (176, 84), (162, 84), (130, 76)]
    wash(L, brim, navy_dk, op=1.0, wob=0.6, seed=16, smooth=1, tex_k=0.2, rim=0.2, rim_w=2.0)
    ink(L, np.vstack([brim, brim[:1]]), w0=1.2, color=hexc('#141b36'), op=0.8, seed=17, wob=0.4, taper=0.1, smooth=False)
    return L


def pad(img, view):
    """侧面的层右边补 24px 透明（棒球帽的帽檐会伸出原精灵的画布）；左上不动，锚点不变。"""
    if view == 'side':
        return np.pad(img, ((0, 0), (0, 24), (0, 0)))
    return img


def make(view):
    spr = load(f'bud_{view}')
    h, w = spr.shape[:2]
    hat_poly, keep_poly, hair_poly = (FRONT_HAT, FRONT_KEEP, FRONT_HAIR) if view == 'front' else (SIDE_HAT, SIDE_KEEP, SIDE_HAIR)
    hat_m = polymask(h, w, hat_poly) * (1 - polymask(h, w, keep_poly))
    # 帽子层：只留帽子的像素
    hat = spr.copy()
    hat[..., 3] = spr[..., 3] * hat_m
    save(f'bud_hat_{view}', pad(hat, view))
    # 身体层：去掉帽子 → 补头发
    body = spr.copy()
    body[..., 3] = spr[..., 3] * (1 - hat_m)
    L = Canvas(w, h)
    ys_, xs_ = np.where((polymask(h, w, keep_poly) > 0.9) & (spr[..., 3] > 0.9))
    # 取刘海的颜色：KEEP 区域里偏棕、较暗的像素
    sel = spr[ys_, xs_, :3]
    brown = sel[(sel[:, 0] > sel[:, 2] + 0.12) & (sel[:, 0] < 0.62) & (sel[:, 1] < 0.45)]
    base_col = np.median(brown, axis=0) if len(brown) > 30 else HAIR_COL
    base_col = np.clip(base_col * 1.05, 0, 1)
    pts_ = np.asarray(hair_poly, np.float32)
    paint_hair(L, hair_poly, 21 if view == 'front' else 22, base_col, (pts_[:, 0].mean(), pts_[:, 1].mean() + (14 if view == 'front' else 8)))
    # 头发放在脸/刘海的“后面”，但在身体上面：先画头发，再盖回脸（KEEP 区域）
    out = Canvas(w, h)
    out.rgb = body[..., :3].copy(); out.a = body[..., 3].copy()
    keep_m = polymask(h, w, keep_poly)
    hair_a = L.a * (1 - keep_m)
    out.over(0, h, 0, w, L.rgb, hair_a)
    res = np.dstack([out.rgb, out.a])
    save(f'bud_{view}_bare', pad(res, view))
    # 棒球帽层
    cap = (cap_front if view == 'front' else cap_side)(h, w)
    save(f'bud_cap_{view}', pad(np.dstack([cap.rgb, cap.a]), view))


if __name__ == '__main__':
    for v in ('front', 'side'):
        make(v)
    print('done')
