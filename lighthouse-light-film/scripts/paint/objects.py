"""场景里的“东西”（建筑、船、灯塔、雪人……），用 pt.py 画：水彩色块 + 细墨线 + 排线。"""
import math
import numpy as np
from pt import *  # noqa
from world import P, rgbmix, hills, ridge_pts, bush, rocks, post, wire

INK = P['ink']
WARM = {'core': P['warm_core'], 'mid': P['warm_mid'], 'out': P['warm_out']}


def outline(L, pts, w=1.6, op=0.75, seed=0, closed=True, col=None):
    p = np.asarray(pts, F)
    if closed:
        p = np.vstack([p, p[:1]])
    ink(L, p, w0=w, color=col if col is not None else INK, op=op, seed=seed, wob=0.6, taper=0.1, smooth=False)


def rect(x0, y0, x1, y1):
    return np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], F)


def window(L, x, y, w, h, seed=0, lit=None, cross=True):
    """窗：淡蓝的玻璃（冷色），lit 给定一个暖色时发光（只有港口的房子用）。"""
    col = lit if lit is not None else hexc('#cddaee')
    wash(L, rect(x, y, x + w, y + h), col, op=1.0, wob=0.5, seed=seed, smooth=0, tex_k=0.06, rim=0.1)
    outline(L, rect(x, y, x + w, y + h), 1.4, 0.8, seed + 1)
    if cross:
        ink(L, [(x + w / 2, y), (x + w / 2, y + h)], w0=1.2, color=INK, op=0.7, seed=seed + 2, wob=0.3)
        ink(L, [(x, y + h / 2), (x + w, y + h / 2)], w0=1.2, color=INK, op=0.7, seed=seed + 3, wob=0.3)
    if lit is not None:
        glow(L, x + w / 2, y + h / 2, max(w, h) * 1.6, WARM['mid'], 0.35, 2.0)


def house(L, x, y, w, h, roof=0.55, seed=0, wall='#e8edf6', roof_col='#55627f', windows=2, door=True, chimney=True, lit=None, snow_roof=1.0, side='r'):
    """一座小房子：墙（右边一块蓝灰阴影）+ 两坡屋顶（压着厚厚的雪）+ 窗 + 门 + 烟囱。(x, y) 是房子底边中点。"""
    r = np.random.default_rng(seed)
    x0, x1 = x - w / 2, x + w / 2
    wall_pts = rect(x0, y - h, x1, y)
    wash(L, wall_pts, hexc(wall), op=1.0, wob=1.2, seed=seed, smooth=0, tex_k=0.1, rim=0.12)
    sh = np.array([[x1 - w * 0.28, y - h], [x1, y - h], [x1, y], [x1 - w * 0.28, y]], F)
    wash(L, sh, P['snow_sh2'], op=0.38, wob=1.0, seed=seed + 1, smooth=0, tex_k=0.12)
    sh2 = rect(x0, y - h * 0.12, x1, y)
    wash(L, sh2, P['snow_sh2'], op=0.3, wob=1.0, seed=seed + 2, smooth=0, tex_k=0.12)
    outline(L, wall_pts, 1.7, 0.75, seed + 3)
    # 墙上的横向排线（木板 / 石头）
    hatch(L, wall_pts, 0, 11, 26, P['snow_sh3'], op=0.16, w=0.9, seed=seed + 4, jitter=0.2)
    # 屋顶
    rh = h * roof
    roof_pts = np.array([[x0 - w * 0.08, y - h + 6], [x - w * 0.05, y - h - rh], [x + w * 0.05, y - h - rh], [x1 + w * 0.08, y - h + 6]], F)
    wash(L, roof_pts, hexc(roof_col), op=1.0, wob=1.2, seed=seed + 5, smooth=0, tex_k=0.16, rim=0.14)
    hatch(L, roof_pts, 0, 9, 22, P['ink'], op=0.22, w=0.9, seed=seed + 6, jitter=0.2)
    outline(L, roof_pts, 1.7, 0.75, seed + 7)
    # 屋顶上的雪：沿屋脊厚厚一层，檐口垂下来几块
    cap = np.array([[x0 - w * 0.05, y - h + 2], [x - w * 0.06, y - h - rh - 8], [x + w * 0.06, y - h - rh - 8], [x1 + w * 0.05, y - h + 2], [x1 - w * 0.1, y - h + 14 * snow_roof], [x + w * 0.2, y - h + 5], [x - w * 0.15, y - h + 16 * snow_roof], [x0 + w * 0.08, y - h + 6]], F)
    wash(L, cap, P['snow'], op=1.0, wob=2.0, seed=seed + 8, smooth=2, tex_k=0.07)
    wash(L, cap + [0, 7], P['snow_sh1'], op=0.35, wob=2.0, seed=seed + 9, smooth=2)
    outline(L, cap, 1.2, 0.35, seed + 10)
    # 窗、门
    ww, wh = w * 0.16, h * 0.28
    n = windows
    for i in range(n):
        cx = x0 + w * (0.17 + 0.62 * i / max(n - 1, 1) * (1 if n > 2 else 0.52)) if n > 1 else x - w * 0.18
        window(L, cx - ww / 2, y - h * 0.68, ww, wh, seed + 20 + i, lit=lit)
    if door:
        dx = x + w * (0.3 if n == 2 else (0.36 if n > 2 else 0.18))
        wash(L, rect(dx - w * 0.07, y - h * 0.5, dx + w * 0.07, y), hexc('#3b4a68'), op=1.0, wob=0.8, seed=seed + 30, smooth=0, tex_k=0.1)
        outline(L, rect(dx - w * 0.07, y - h * 0.5, dx + w * 0.07, y), 1.4, 0.8, seed + 31)
    if chimney:
        cx = x + w * 0.22
        ch = rect(cx - w * 0.05, y - h - rh * 0.95, cx + w * 0.05, y - h - rh * 0.4)
        wash(L, ch, hexc('#7a869e'), op=1.0, wob=0.8, seed=seed + 40, smooth=0, tex_k=0.1)
        outline(L, ch, 1.4, 0.75, seed + 41)
        wash(L, rect(cx - w * 0.065, y - h - rh * 0.97, cx + w * 0.065, y - h - rh * 0.9), P['snow'], op=1.0, wob=0.8, seed=seed + 42, smooth=1)


def smoke(L, x, y, n=5, seed=0, s=1.0, col=None, op=0.4):
    r = np.random.default_rng(seed)
    c = col if col is not None else hexc('#dfe6f2')
    px, py = x, y
    for i in range(n):
        rad = (12 + i * 6) * s
        px += r.normal(10, 4) * s
        py -= (16 + i * 7) * s
        pts = [(px + math.cos(a) * rad * r.uniform(0.8, 1.2), py + math.sin(a) * rad * 0.7 * r.uniform(0.8, 1.2)) for a in np.linspace(0, 2 * math.pi, 9, endpoint=False)]
        wash(L, np.array(pts, F), c, op=op * (1 - i / (n + 1)), wob=3, seed=int(r.integers(1e6)), smooth=2, tex_k=0.1, rim=0.05)


def boat(L, x, y, s=1.0, lit=True, seed=0, hull='#1d2a4d', mast=True, flag=False, stripe=None):
    """小渔船：深色船身 + 船舱 + 桅杆 + 缆绳；lit 时船头挂一盏暖灯（港口和船上的灯）。(x, y) 是水线中点。"""
    r = np.random.default_rng(seed)
    hp = np.array([[x - 62 * s, y - 20 * s], [x + 56 * s, y - 22 * s], [x + 44 * s, y + 4 * s], [x - 40 * s, y + 6 * s]], F)
    wash(L, hp, hexc(hull), op=1.0, wob=1.0, seed=seed, smooth=1, tex_k=0.15)
    if stripe is not None:
        wash(L, np.array([[x - 60 * s, y - 14 * s], [x + 54 * s, y - 16 * s], [x + 52 * s, y - 10 * s], [x - 58 * s, y - 8 * s]], F), hexc(stripe), op=0.95, wob=0.6, seed=seed + 1, smooth=0)
    outline(L, hp, 1.4 * s, 0.7, seed + 2)
    cab = rect(x - 14 * s, y - 50 * s, x + 24 * s, y - 20 * s)
    wash(L, cab, hexc('#2a3a62'), op=1.0, wob=0.6, seed=seed + 3, smooth=0)
    outline(L, cab, 1.2 * s, 0.7, seed + 4)
    if mast:
        ink(L, [(x - 30 * s, y - 20 * s), (x - 32 * s, y - 130 * s)], w0=2.0 * s, color=INK, op=0.9, seed=seed + 5, wob=0.4)
        ink(L, [(x + 30 * s, y - 20 * s), (x + 28 * s, y - 100 * s)], w0=1.6 * s, color=INK, op=0.9, seed=seed + 6, wob=0.4)
        ink(L, [(x - 32 * s, y - 118 * s), (x - 70 * s, y - 20 * s)], w0=0.9 * s, color=INK, op=0.6, seed=seed + 7, wob=0.3)
        ink(L, [(x - 32 * s, y - 118 * s), (x + 28 * s, y - 96 * s)], w0=0.9 * s, color=INK, op=0.6, seed=seed + 8, wob=0.3)
    if flag:
        wash(L, np.array([[x + 28 * s, y - 100 * s], [x + 52 * s, y - 94 * s], [x + 28 * s, y - 86 * s]], F), hexc('#e8eef8'), op=1.0, wob=0.3, seed=seed + 9, smooth=0)
    if lit:
        glow(L, x - 4 * s, y - 36 * s, 54 * s, WARM['mid'], 0.55, 1.8)
        dots(L, [(x - 4 * s, y - 36 * s, 4.2 * s)], WARM['core'], 1.0)
    # 水线上的白浪
    ink(L, [(x - 80 * s, y + 8 * s), (x - 20 * s, y + 4 * s), (x + 70 * s, y + 8 * s)], w0=1.8 * s, color=hexc('#cfdcf0'), op=0.6, seed=seed + 10, wob=0.8, taper=0.5)


def lighthouse(L, x, y, h=300, lit=False, seed=0, cottage=True, body='#f1f3f8'):
    """灯塔：白色锥形塔身（带两道蓝灰色的箍）+ 挑台 + 灯室 + 深色圆顶；底下一座小屋。(x, y) 是塔底中点。
    lit=False：灯室是黑的（玻璃深蓝灰）；lit=True 在灯室处另外叠暖色光（见 beam）。"""
    w0, w1 = h * 0.23, h * 0.15
    ty = y - h
    tower = np.array([[x - w0 / 2, y], [x - w1 / 2, ty + h * 0.12], [x + w1 / 2, ty + h * 0.12], [x + w0 / 2, y]], F)
    wash(L, tower, hexc(body), op=1.0, wob=0.8, seed=seed, smooth=0, tex_k=0.1, rim=0.14)
    sh = np.array([[x + w0 * 0.12, y], [x + w1 * 0.12, ty + h * 0.12], [x + w1 / 2, ty + h * 0.12], [x + w0 / 2, y]], F)
    wash(L, sh, P['snow_sh2'], op=0.5, wob=0.6, seed=seed + 1, smooth=0, tex_k=0.1)
    for k, t in enumerate((0.36, 0.62)):  # 两道蓝灰的箍
        yy = y - h * (0.12 + 0.76 * t)
        ww = w0 + (w1 - w0) * (1 - (y - yy) / (h * 0.88))
        band = np.array([[x - ww / 2, yy], [x + ww / 2, yy], [x + ww / 2 * 0.97, yy - h * 0.05], [x - ww / 2 * 0.97, yy - h * 0.05]], F)
        wash(L, band, hexc('#6f7f9f'), op=0.85, wob=0.6, seed=seed + 2 + k, smooth=0, tex_k=0.12)
    outline(L, tower, 1.6, 0.75, seed + 5)
    # 挑台
    gal = rect(x - h * 0.13, ty + h * 0.085, x + h * 0.13, ty + h * 0.125)
    wash(L, gal, hexc('#2c3752'), op=1.0, wob=0.5, seed=seed + 6, smooth=0)
    for i in range(7):
        gx = x - h * 0.12 + i * h * 0.04
        ink(L, [(gx, ty + h * 0.085), (gx, ty + h * 0.02)], w0=1.0, color=INK, op=0.7, seed=seed + 7 + i, wob=0.2)
    ink(L, [(x - h * 0.125, ty + h * 0.02), (x + h * 0.125, ty + h * 0.02)], w0=1.2, color=INK, op=0.7, seed=seed + 15, wob=0.2)
    # 灯室
    lan = rect(x - h * 0.075, ty - h * 0.055, x + h * 0.075, ty + h * 0.02)
    wash(L, lan, hexc('#1d2a49') if not lit else WARM['core'], op=1.0, wob=0.4, seed=seed + 16, smooth=0, tex_k=0.1)
    outline(L, lan, 1.3, 0.85, seed + 17)
    for gx in (x - h * 0.025, x + h * 0.025):
        ink(L, [(gx, ty - h * 0.055), (gx, ty + h * 0.02)], w0=1.0, color=INK, op=0.7, seed=seed + 18, wob=0.2)
    # 圆顶
    dome = np.array([[x - h * 0.09, ty - h * 0.055], [x - h * 0.06, ty - h * 0.115], [x, ty - h * 0.15], [x + h * 0.06, ty - h * 0.115], [x + h * 0.09, ty - h * 0.055]], F)
    wash(L, dome, hexc('#2c3752'), op=1.0, wob=0.4, seed=seed + 19, smooth=2)
    outline(L, dome, 1.3, 0.8, seed + 20)
    ink(L, [(x, ty - h * 0.15), (x, ty - h * 0.2)], w0=1.4, color=INK, op=0.9, seed=seed + 21, wob=0.2)
    # 塔门
    wash(L, rect(x - h * 0.02, y - h * 0.075, x + h * 0.02, y), hexc('#2a3552'), op=1.0, wob=0.4, seed=seed + 22, smooth=0)
    # 底下的小屋
    if cottage:
        house(L, x + h * 0.38, y, h * 0.4, h * 0.2, 0.55, seed + 30, windows=1, door=True, chimney=True)
        house(L, x - h * 0.42, y + 2, h * 0.3, h * 0.15, 0.5, seed + 40, windows=1, door=False, chimney=False)
    if lit:
        glow(L, x, ty - h * 0.02, h * 0.45, WARM['mid'], 0.7, 1.6)


def rock_base(L, x, y, w, h, seed=0, snow=True):
    """灯塔脚下 / 岬角的岩石座：一大块深灰的岩石，顶上盖雪。"""
    r = np.random.default_rng(seed)
    n = 9
    xs = np.linspace(x - w / 2, x + w / 2, n)
    top = [(xx, y - h * (0.55 + 0.45 * math.sin((xx - x + w / 2) / w * math.pi)) + r.normal(0, h * 0.05)) for xx in xs]
    pts = np.array(top + [(x + w / 2 + w * 0.05, y), (x - w / 2 - w * 0.05, y)], F)
    wash(L, pts, P['rock'], op=1.0, wob=2.0, seed=seed, smooth=1, tex_k=0.2, rim=0.2)
    hatch(L, pts, 72, 8, 20, P['rock_dk'], op=0.5, w=1.2, seed=seed + 1)
    hatch(L, pts, 25, 12, 24, P['rock_lt'], op=0.22, w=1.0, seed=seed + 2)
    if snow:
        snow_pts = np.array([[px, py - 2] for px, py in top] + [(px, py + h * 0.14 * (0.6 + 0.8 * r.random())) for px, py in top[::-1]], F)
        wash(L, snow_pts, P['snow'], op=1.0, wob=2.5, seed=seed + 3, smooth=2, tex_k=0.07)
        wash(L, snow_pts + [0, 8], P['snow_sh1'], op=0.3, wob=2.0, seed=seed + 4, smooth=2)


def tree_pine(L, x, y, h=300, seed=0, snow=True):
    """松树：深青灰的层层枝叶 + 枝头的雪。"""
    r = np.random.default_rng(seed)
    ink(L, [(x, y), (x, y - h * 0.15)], w0=h * 0.03, color=hexc('#3a3532'), op=0.95, seed=seed, wob=0.5)
    layers = 5
    for i in range(layers):
        t = i / layers
        yy = y - h * (0.1 + 0.8 * t)
        ww = h * 0.38 * (1 - t * 0.78)
        hh = h * 0.28
        tri = np.array([[x - ww, yy], [x - ww * 0.55, yy - hh * 0.5], [x, yy - hh], [x + ww * 0.55, yy - hh * 0.5], [x + ww, yy], [x, yy + hh * 0.08]], F)
        wash(L, tri, rgbmix(hexc('#1f3a44'), hexc('#2d4b52'), r.random()), op=1.0, wob=2.0, seed=int(r.integers(1e6)), smooth=1, tex_k=0.2)
        if snow:
            cap = np.array([[x - ww * 0.9, yy - 2], [x - ww * 0.4, yy - hh * 0.55], [x, yy - hh * 0.95], [x + ww * 0.4, yy - hh * 0.55], [x + ww * 0.9, yy - 2], [x + ww * 0.4, yy - hh * 0.28], [x - ww * 0.3, yy - hh * 0.3]], F)
            wash(L, cap, P['snow'], op=0.95, wob=2.0, seed=int(r.integers(1e6)), smooth=2, tex_k=0.07)
