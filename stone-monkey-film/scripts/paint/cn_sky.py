"""cn_sky.py —— 云、烟、汽的水墨笔法（补 cn_arch 文档里提到、但没实现的 cloud_mass / smoke）。
云：一团团叠起的圆鼓鼓的云头（光栅蒙版 → 淡彩 + 上缘亮带 + 下缘积墨 + 断断续续的墨线 + 卷云纹），不是“筋斗云”造型。
约定同 cn.py：用中性淡彩画，夜色 / 光照 / 晨光交给 grade。"""
import math
import numpy as np
import cv2
from cn_arch import *   # noqa


def _spiral(cx, cy, r0, turns=1.6, flip=1, n=40, rot=0.0):
    pts = []
    for i in range(n + 1):
        t = i / n
        a = rot + flip * t * turns * 2 * math.pi
        rr = r0 * (1 - 0.82 * t)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.9))
    return pts


def cloud_mass(L, cx, by, w, h, seed=0, col=None, sh=None, hi=None, ink=0.5, op=1.0, flat=0.22, curls=2, bumps=None, skew=0.0, soft=1.4):
    """一团云：底边在 y=by（比较平，略有起伏），宽 w、最高 h。ink = 墨线的浓淡（0 = 不描）。"""
    col = A['cloud'] if col is None else np.asarray(col, F)
    sh = A['cloud_sh'] if sh is None else np.asarray(sh, F)
    hi = mix(col, np.ones(3, F), 0.45) if hi is None else np.asarray(hi, F)
    r = np.random.default_rng(seed)
    pad = int(h * 0.25 + 24)
    x0, y0 = int(cx - w / 2 - pad), int(by - h - pad)
    x1, y1 = int(cx + w / 2 + pad), int(by + pad)
    mw, mh = x1 - x0, y1 - y0
    m = np.zeros((mh, mw), np.uint8)
    n = bumps or max(4, int(w / 95))
    for i in range(n):
        t = (i + 0.5) / n
        env = math.sin(math.pi * min(max(t + skew * (t - 0.5), 0.02), 0.98)) ** 0.8
        rr = h * (0.22 + 0.34 * env * r.uniform(0.7, 1.0))
        bx = cx - w / 2 + t * w + r.normal(0, w * 0.012)
        byc = by - rr * r.uniform(0.55, 0.85) - h * 0.1 * env
        cv2.circle(m, (int(bx - x0), int(byc - y0)), max(int(rr), 4), 255, -1, cv2.LINE_AA)
    # 比较平的底
    cv2.rectangle(m, (int(cx - w * 0.47 - x0), int(by - h * flat - y0)), (int(cx + w * 0.47 - x0), int(by - y0)), 255, -1)
    mf = cv2.GaussianBlur(m.astype(F) / 255.0, (0, 0), 4.0)
    mf = np.clip((mf - 0.5) * 3.0 + 0.5, 0, 1)
    mf = cv2.GaussianBlur(mf, (0, 0), soft)
    d = max(int(h * 0.16), 6)
    mb = (mf > 0.5).astype(np.uint8)
    top = mb * (1 - np.roll(mb, d, axis=0))
    bot = mb * (1 - np.roll(mb, -d, axis=0))
    topf = cv2.GaussianBlur(top.astype(F), (0, 0), d * 0.45)
    botf = cv2.GaussianBlur(bot.astype(F), (0, 0), d * 0.55)
    # 低频的斑驳（水渍）
    nz = fbm(mh, mw, seed + 3, max(w * 0.18, 30), 3, 0.55, warp=14)
    tex = 0.94 + 0.12 * nz
    rgb = np.empty((mh, mw, 3), F)
    rgb[:] = col
    rgb = rgb * tex[..., None]
    rgb = mix(rgb, hi, np.clip(topf * 1.2, 0, 1)[..., None] * 0.8)
    rgb = mix(rgb, sh, np.clip(botf * 1.3, 0, 1)[..., None] * 0.9)
    a = np.clip(mf * op, 0, 1).astype(F)
    L.over(y0, y1, x0, x1, rgb.astype(F), a)
    # 墨线：沿轮廓断断续续地描，下缘更浓（积墨）
    if ink > 0:
        cs, _ = cv2.findContours(mb, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for c in cs:
            if len(c) < 30:
                continue
            pts = [(float(p[0][0] + x0), float(p[0][1] + y0)) for p in c[::5]]
            i = 0
            while i < len(pts) - 3:
                ln = int(r.integers(4, 11))
                seg = pts[i:i + ln]
                if len(seg) >= 3 and r.random() < 0.72:
                    yb = np.mean([p[1] for p in seg])
                    k = 0.55 + 0.6 * np.clip((yb - (by - h * 0.5)) / (h * 0.5), 0, 1)
                    brush(L, seg, w0=r.uniform(1.6, 3.0), color=INK, op=ink * op * k * r.uniform(0.6, 1.0), seed=int(r.integers(1e6)), wob=0.8, taper=0.3, dry=0.35, smooth=True)
                i += ln + int(r.integers(1, 4))
    # 卷云纹
    for k in range(curls):
        sx = cx + r.uniform(-0.3, 0.3) * w
        sy = by - h * r.uniform(0.35, 0.65)
        brush(L, _spiral(sx, sy, h * r.uniform(0.10, 0.18), turns=r.uniform(1.3, 1.9), flip=1 if r.random() < 0.5 else -1, rot=r.uniform(0, 6.28)), w0=r.uniform(1.6, 2.6), color=sh * 0.75, op=0.55 * op, seed=int(r.integers(1e6)), wob=0.6, taper=0.35, dry=0.2)


def cloud_bank(L, x0, x1, by, h, seed=0, n=None, col=None, sh=None, ink=0.45, op=1.0, wmin=260, wmax=520, hscale=(0.7, 1.15), y_jit=14, curls=1, hi=None):
    """沿一条横带铺一排云（云海 / 云墙）。"""
    r = np.random.default_rng(seed)
    x = x0 - wmin * 0.3
    i = 0
    while x < x1 + wmin * 0.3:
        w = r.uniform(wmin, wmax)
        cloud_mass(L, x + w / 2, by + r.normal(0, y_jit), w, h * r.uniform(*hscale), seed=seed * 31 + i, col=col, sh=sh, hi=hi, ink=ink, op=op, curls=curls)
        x += w * r.uniform(0.5, 0.78)
        i += 1


def smoke_column(L, x_base, y_base, x_top, y_top, w0, w1, seed=0, col=None, op=0.8, n=26, ink=0.0):
    """一柱烟：从 (x_base,y_base) 蜿蜒升到 (x_top,y_top)，越往上越宽越淡，由一串逐渐变大的云团堆成。"""
    col = A['smoke'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    for i in range(n):
        t = i / (n - 1)
        x = x_base + (x_top - x_base) * t ** 1.3 + math.sin(t * 5.0 + seed) * (w0 + w1 * t) * 0.55
        y = y_base + (y_top - y_base) * t
        w = (w0 + (w1 - w0) * t) * r.uniform(0.9, 1.2)
        cloud_mass(L, x, y + w * 0.3, w * 1.5, w * 0.95, seed=seed * 17 + i, col=mix(col, A['cloud'], t * 0.45), sh=mix(col, INK, 0.25), hi=mix(col, A['cloud'], 0.35 + 0.3 * t), ink=ink, op=op * (1 - 0.55 * t), curls=0, flat=0.0, soft=2.0)


def steam(L, x, y, h, seed=0, w=26, col=None, op=0.5, n=5):
    """石缝里冒出的几缕热气：细长的 S 形淡带。"""
    col = hexc('#d9dcdc') if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    for i in range(n):
        bx = x + r.normal(0, w * 0.5)
        hh = h * r.uniform(0.6, 1.1)
        ph = r.uniform(0, 6.28)
        pts = [(bx + math.sin(t * 3.2 + ph) * w * (0.4 + t), y - hh * t) for t in np.linspace(0, 1, 12)]
        brush(L, pts, w0=w * r.uniform(0.35, 0.6), w1=1.0, color=col, op=op * r.uniform(0.5, 1.0), seed=int(r.integers(1e6)), wob=1.2, taper=0.5, dry=0.25)
