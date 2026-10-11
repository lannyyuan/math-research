"""场景里要用的“东西”：天空、海、山、雪地、灌木、岩石、篱笆桩、房子、灯塔、船……全用 pt.py 的画法画。"""
import math
import numpy as np
import cv2
from pt import *  # noqa

# ───────────── 调色盘（取自封面） ─────────────
P = {
    'ink': hexc('#1d2447'), 'ink_br': hexc('#3a2f2a'),
    'snow': hexc('#f4f6fb'), 'snow_lit': hexc('#fbfcff'),
    'snow_sh1': hexc('#c9d4ea'), 'snow_sh2': hexc('#9fb2d3'), 'snow_sh3': hexc('#7f95bf'),
    'rock': hexc('#4b5262'), 'rock_dk': hexc('#2c3140'), 'rock_lt': hexc('#7b8396'),
    'twig': hexc('#5b524e'), 'twig_dk': hexc('#3b3434'),
    'sea_dk': hexc('#162547'), 'sea_md': hexc('#223a68'), 'sea_lt': hexc('#3f5d92'),
    'warm_core': hexc('#fff3c4'), 'warm_mid': hexc('#ffd978'), 'warm_out': hexc('#f2b04a'),
}


def rgbmix(a, b, t):
    return a + (b - a) * t


# ───────────── 天空 ─────────────
SKIES = {
    # 上、中、地平线 三色 + 云的亮度
    'night': ('#1a2d5c', '#2a4478', '#4c6a9e', 0.16),
    'storm': ('#141f45', '#22345f', '#3d5584', 0.10),
    'dusk': ('#2a3f72', '#4f6a9c', '#9fb2d1', 0.09),
    'day': ('#7e93b8', '#a9b9d2', '#d3dbe8', 0.12),
    'morning': ('#6f93c9', '#a4bfe0', '#e3ecf6', 0.20),
    'indoor_night': ('#18264f', '#243a6c', '#3a5688', 0.08),
}


def sky(W, H, kind='night', seed=1, horizon=0.78, blotch=0.55, snow_flecks=0):
    top, mid, hor, cl = hexc(SKIES[kind][0]), hexc(SKIES[kind][1]), hexc(SKIES[kind][2]), SKIES[kind][3]
    y = np.linspace(0, 1, H, dtype=F)[:, None]
    t1 = np.clip(y / horizon, 0, 1)
    base = np.where(t1[..., None] < 0.55, rgbmix(top, mid, np.clip(t1 / 0.55, 0, 1)[..., None] ** 1.1), rgbmix(mid, hor, np.clip((t1 - 0.55) / 0.45, 0, 1)[..., None] ** 1.6))
    base = np.broadcast_to(base, (H, W, 3)).copy()
    n1 = fbm(H, W, seed, 340, 5, 0.55, warp=60)
    n2 = fbm(H, W, seed + 11, 130, 4, 0.5, warp=60)
    n3 = fbm(H, W, seed + 23, 40, 3, 0.5)
    # 深色水渍 + 亮色云团（靠近地平线更多）
    dark = smoothstep(0.52, 0.82, n1)
    light = smoothstep(0.50, 0.80, n2) * (0.35 + 0.65 * np.clip(y / horizon, 0, 1)) * cl * 3.0
    ring = np.exp(-((n1 - 0.62) / 0.03) ** 2) * 0.025
    k = 1 - blotch * 0.18 * dark - ring + (n3 - 0.5) * 0.06
    out = base * k[..., None]
    out = out + (light[..., None] * (hor - top) * 0.55)
    out += (grain(H, W, seed + 5, 0.6)[..., None] * 0.012)
    return np.clip(out, 0, 1)


def flakes(L, n, seed, rmin=1.0, rmax=3.2, region=None, color=(1, 1, 1), op=0.9, sparkle=0.04):
    r = np.random.default_rng(seed)
    x0, y0, x1, y1 = region or (0, 0, L.w, L.h)
    pts = [(r.uniform(x0, x1), r.uniform(y0, y1), r.uniform(rmin, rmax) ** 1.0) for _ in range(n)]
    dots(L, pts, color, op)
    for _ in range(int(n * sparkle)):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        s = r.uniform(6, 13)
        for ang in (0, 90):
            a = math.radians(ang)
            ink(L, [(x - math.cos(a) * s, y - math.sin(a) * s), (x, y), (x + math.cos(a) * s, y + math.sin(a) * s)], w0=1.6, color=color, op=0.85, wob=0, taper=0.5)


# ───────────── 山 / 岬角 ─────────────
def ridge_pts(x0, x1, y_base, amp, seed, n=40, rough=0.5, slope=0.0):
    r = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, n)
    ys = np.zeros(n)
    k = 1
    for o in range(4):
        ph = r.uniform(0, 6.28)
        ys += np.sin(xs / (x1 - x0) * math.pi * (1.3 + o * 1.7) * k + ph) * amp / (1 + o * 1.4)
    ys += slope * (xs - x0)
    ys += r.normal(0, amp * 0.03 * rough, n)
    return np.stack([xs, y_base - ys], 1)


def hills(L, pts, base_y, color, snow=True, seed=0, op=1.0, snow_col=None, haze=0.0):
    poly = np.vstack([pts, [pts[-1][0], base_y], [pts[0][0], base_y]])
    wash(L, poly, color, op=op, wob=2.5, seed=seed, smooth=1, tex_k=0.12)
    if snow:
        # 山脊上的积雪：沿山脊一条不规则的白带
        r = np.random.default_rng(seed + 9)
        top = pts.copy()
        low = top + np.stack([np.zeros(len(top)), r.uniform(10, 36, len(top)) * (0.5 + 0.8 * (np.sin(np.arange(len(top)) * 0.9 + seed) > 0))], 1)
        band = np.vstack([top, low[::-1]])
        wash(L, band, snow_col if snow_col is not None else rgbmix(P['snow_sh1'], P['snow'], 0.4), op=0.9 * op, wob=2.0, seed=seed + 3, smooth=1, tex_k=0.1)


def sea(L, y0, y1, seed=3, lit_x=None, lit_color=None, lit_op=0.0, tone='night', strokes=260):
    """海：深蓝底 + 一道道横向的亮笔触；lit_x 处有灯光的倒影（暖色，只在灯光场景用）。"""
    W = L.w
    if tone == 'night':
        c_dk, c_md, c_lt = P['sea_dk'], P['sea_md'], P['sea_lt']
    elif tone == 'grey':
        c_dk, c_md, c_lt = hexc('#5d708f'), hexc('#7e92b1'), hexc('#a7b8d0')
    else:
        c_dk, c_md, c_lt = hexc('#10203f'), hexc('#1b3160'), hexc('#2f4c80')
    # 底：越近越深
    ys = np.linspace(0, 1, y1 - y0, dtype=F)[:, None, None]
    base = rgbmix(c_md, c_dk, np.clip(ys * 1.1, 0, 1))
    n = fbm(y1 - y0, W, seed, 160, 4, 0.55, warp=50)[..., None]
    img = base * (0.9 + 0.2 * n) + (grain(y1 - y0, W, seed + 1, 0.8)[..., None] * 0.015)
    L.over(y0, y1, 0, W, np.clip(np.broadcast_to(img, (y1 - y0, W, 3)), 0, 1).copy(), np.ones((y1 - y0, W), F))
    r = np.random.default_rng(seed + 4)
    for _ in range(strokes):
        y = y0 + (r.random() ** 1.6) * (y1 - y0)
        d = (y - y0) / max(y1 - y0, 1)
        ln = r.uniform(30, 160) * (0.4 + d * 1.4)
        x = r.uniform(-50, W)
        ink(L, [(x, y), (x + ln * 0.5, y + r.normal(0, 0.8)), (x + ln, y + r.normal(0, 1.2))], w0=1.0 + 2.2 * d, color=c_lt, op=0.18 + 0.2 * r.random(), seed=int(r.integers(1e6)), wob=0.5, taper=0.5)
    if lit_x is not None and lit_op > 0:
        col = lit_color if lit_color is not None else P['warm_mid']
        for i in range(70):
            y = y0 + (r.random() ** 1.3) * (y1 - y0)
            d = (y - y0) / max(y1 - y0, 1)
            sp = (40 + 160 * d)
            x = lit_x + r.normal(0, sp * 0.35)
            ln = r.uniform(20, 90) * (0.5 + d)
            ink(L, [(x - ln / 2, y), (x + ln / 2, y + r.normal(0, 0.5))], w0=1.6 + 2.5 * d, color=col, op=lit_op * (0.5 + r.random() * 0.8), seed=int(r.integers(1e6)), wob=0.2, taper=0.5)


# ───────────── 雪地 ─────────────
def snow_ground(L, top_pts, bottom_y, seed=0, shade=True, lit=1.0, tone='cool'):
    """一块雪坡：top_pts 是坡顶那条线（左→右），往下铺到 bottom_y。带蓝灰色的阴影块 + 排线 + 脚印的小窝。"""
    poly = np.vstack([top_pts, [top_pts[-1][0], bottom_y], [top_pts[0][0], bottom_y]])
    base = P['snow'] if tone == 'cool' else P['snow_lit']
    wash(L, poly, base, op=1.0, wob=2.5, seed=seed, smooth=1, tex_k=0.07, rim=0.10)
    if not shade:
        return poly
    r = np.random.default_rng(seed + 31)
    xs0, xs1 = top_pts[:, 0].min(), top_pts[:, 0].max()
    xs = np.linspace(xs0, xs1, 60)
    ytop = np.interp(xs, top_pts[:, 0], top_pts[:, 1])
    # 沿坡面“等高线”的阴影带：一条条长长的、两头收尖的蓝灰色雪堆阴影，带细细的排线
    nb = 9
    for k in range(nb):
        t = (k + 0.7) / (nb + 0.3)
        base = ytop + t * (bottom_y - ytop) * 0.92 + np.interp(xs, np.linspace(xs0, xs1, 12), r.normal(0, 16, 12))
        for seg in range(int(r.integers(2, 4))):
            a0 = r.uniform(0, 0.8)
            a1 = min(a0 + r.uniform(0.2, 0.5), 1.0)
            i0, i1 = int(a0 * 59), max(int(a1 * 59), int(a0 * 59) + 4)
            sel = np.arange(i0, i1)
            th = np.sin(np.linspace(0, math.pi, len(sel))) ** 0.8 * r.uniform(14, 46) * (0.5 + t)
            upper = np.stack([xs[sel], base[sel]], 1)
            lower = np.stack([xs[sel], base[sel] + th], 1)
            band = np.vstack([upper, lower[::-1]])
            col = rgbmix(P['snow_sh1'], P['snow_sh2'], r.random() * 0.9)
            wash(L, band, col, op=0.35 + 0.35 * r.random(), wob=2.5, seed=int(r.integers(1e6)), smooth=2, tex_k=0.16)
            if r.random() < 0.8:
                hatch(L, band, r.uniform(-18, 18), 7, 18, P['snow_sh3'], op=0.22, w=1.0, seed=int(r.integers(1e6)), jitter=0.3)
    # 零星的小雪窝
    for i in range(int((xs1 - xs0) / 260) + 3):
        cx = r.uniform(xs0, xs1)
        cy = np.interp(cx, top_pts[:, 0], top_pts[:, 1]) + r.uniform(40, bottom_y - np.interp(cx, top_pts[:, 0], top_pts[:, 1]) - 20)
        wd, ht = r.uniform(30, 90), r.uniform(8, 18)
        blob = np.array([[cx - wd / 2, cy], [cx - wd * 0.15, cy - ht], [cx + wd * 0.3, cy - ht * 0.6], [cx + wd / 2, cy + ht * 0.2], [cx, cy + ht]], F)
        wash(L, blob, P['snow_sh2'], op=0.4, wob=1.5, seed=int(r.integers(1e6)), smooth=2, tex_k=0.14)
    return poly


def drift_line(L, pts, seed=0, op=0.7, w=2.0):
    ink(L, pts, w0=w, color=P['snow_sh3'], op=op, seed=seed, wob=2.0, taper=0.3)


def footprints(L, pts, s=1.0, color=None, seed=0, op=0.6):
    """脚印：一串小小的蓝灰色椭圆。"""
    col = color if color is not None else P['snow_sh2']
    r = np.random.default_rng(seed)
    for i, (x, y) in enumerate(pts):
        side = -1 if i % 2 else 1
        cx, cy = x + side * 5 * s, y
        poly = np.array([[cx - 10 * s, cy], [cx - 6 * s, cy - 6 * s], [cx + 7 * s, cy - 5 * s], [cx + 11 * s, cy + 1 * s], [cx + 4 * s, cy + 6 * s], [cx - 8 * s, cy + 5 * s]], F)
        wash(L, poly, col, op=op, wob=0.8, seed=int(r.integers(1e6)), smooth=1, tex_k=0.1)


# ───────────── 灌木 / 枝条 ─────────────
def twig(L, x, y, ang, length, w, depth, seed, col=None, snow=0.0):
    r = np.random.default_rng(seed)
    col = col if col is not None else P['twig']
    pts = [(x, y)]
    cx, cy, a = x, y, ang
    n = max(int(length / 14), 2)
    for i in range(n):
        a += r.normal(0, 0.16)
        cx += math.cos(a) * length / n
        cy += math.sin(a) * length / n
        pts.append((cx, cy))
    ink(L, pts, w0=w, w1=max(w * 0.35, 0.8), color=col, op=0.92, seed=seed, wob=0.7, taper=0.15)
    if depth > 0:
        for j in range(int(r.integers(2, 4))):
            k = int(r.integers(1, max(len(pts) - 1, 2)))
            bx, by = pts[k]
            side = 1 if r.random() < 0.5 else -1
            twig(L, bx, by, a + side * r.uniform(0.35, 0.9), length * r.uniform(0.35, 0.6), w * 0.6, depth - 1, int(r.integers(1e6)), col, snow)
    return pts


def bush(L, x, y, h=160, spread=1.0, n=7, seed=0, snow_cap=True, col=None):
    """光秃秃的灌木：从 (x, y) 向上放射的一束枝条，枝头小杈；底部有一堆雪。"""
    r = np.random.default_rng(seed)
    for i in range(n):
        a = -math.pi / 2 + r.normal(0, 0.45 * spread)
        twig(L, x + r.normal(0, 8 * spread), y, a, h * r.uniform(0.6, 1.1), 3.0, 2, int(r.integers(1e6)), col)
    if snow_cap:
        poly = np.array([[x - 55 * spread, y + 6], [x - 40 * spread, y - 16], [x - 10, y - 24], [x + 28 * spread, y - 18], [x + 58 * spread, y + 4], [x + 20, y + 14], [x - 20, y + 14]], F)
        wash(L, poly, P['snow'], op=1.0, wob=2.0, seed=seed + 2, smooth=2, tex_k=0.08)
        wash(L, poly + [0, 6], P['snow_sh1'], op=0.35, wob=2.0, seed=seed + 3, smooth=2, tex_k=0.12)


def rocks(L, x, y, w, h, seed=0, snow=True, n=3):
    """一堆岩石：深灰的棱块 + 顶上的雪帽 + 细细的排线。"""
    r = np.random.default_rng(seed)
    for i in range(n):
        cx = x + (i - (n - 1) / 2) * w / n * 0.9 + r.normal(0, 6)
        rw, rh = w / n * r.uniform(0.8, 1.2), h * r.uniform(0.6, 1.0)
        pts = np.array([[cx - rw / 2, y], [cx - rw * 0.42, y - rh * 0.55], [cx - rw * 0.15, y - rh], [cx + rw * 0.25, y - rh * 0.9], [cx + rw * 0.5, y - rh * 0.35], [cx + rw * 0.45, y]], F)
        wash(L, pts, rgbmix(P['rock'], P['rock_dk'], r.random() * 0.5), op=1.0, wob=2.0, seed=int(r.integers(1e6)), smooth=1, tex_k=0.18)
        hatch(L, pts, 70, 7, 16, P['rock_dk'], op=0.5, w=1.1, seed=int(r.integers(1e6)))
        ink(L, np.vstack([pts, pts[:1]]), w0=1.6, color=P['ink'], op=0.7, seed=int(r.integers(1e6)), wob=1.0, taper=0.2)
        if snow:
            cap = np.array([[cx - rw * 0.5, y - rh * 0.5], [cx - rw * 0.3, y - rh * 0.85], [cx, y - rh * 1.08], [cx + rw * 0.3, y - rh * 0.98], [cx + rw * 0.55, y - rh * 0.5], [cx + rw * 0.2, y - rh * 0.62], [cx - rw * 0.1, y - rh * 0.55]], F)
            wash(L, cap, P['snow'], op=1.0, wob=2.0, seed=int(r.integers(1e6)), smooth=2, tex_k=0.07)
            wash(L, cap + [0, 5], P['snow_sh1'], op=0.3, wob=2.0, seed=int(r.integers(1e6)), smooth=2)


def post(L, x, y, h=120, w=34, seed=0):
    """篱笆桩：深灰的木桩 + 顶上圆圆的雪帽。"""
    pts = np.array([[x - w / 2, y], [x - w / 2 + 2, y - h], [x + w / 2 - 2, y - h - 4], [x + w / 2, y]], F)
    wash(L, pts, rgbmix(P['rock'], hexc('#5a4f4a'), 0.5), op=1.0, wob=1.5, seed=seed, smooth=1, tex_k=0.2)
    for i in range(5):
        ink(L, [(x - w / 2 + 6 + i * w / 6, y - 4), (x - w / 2 + 7 + i * w / 6, y - h * 0.6), (x - w / 2 + 6 + i * w / 6, y - h + 6)], w0=1.1, color=P['rock_dk'], op=0.5, seed=seed + i, wob=1.0)
    cap = np.array([[x - w * 0.75, y - h + 8], [x - w * 0.55, y - h - 14], [x, y - h - 26], [x + w * 0.6, y - h - 14], [x + w * 0.8, y - h + 8], [x, y - h + 14]], F)
    wash(L, cap, P['snow'], op=1.0, wob=1.5, seed=seed + 7, smooth=2, tex_k=0.07)
    wash(L, cap + [0, 6], P['snow_sh1'], op=0.35, wob=1.5, seed=seed + 8, smooth=2)


def wire(L, p0, p1, sag=14, seed=0, col=None):
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + sag)
    ink(L, [p0, mid, p1], w0=1.4, color=col if col is not None else P['rock_dk'], op=0.7, seed=seed, wob=0.5, taper=0.1)
