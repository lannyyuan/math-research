"""水相关画板（江 / 海滩 / 海底宫殿 / 泉眼）要用的笔法工具，建立在 pt.py / cn.py 之上。

约定同 cn.py：先用“中性淡彩”画明暗层次，夜色 / 光照由 grade 决定。
- 水：sea_rows（海面横向浪纹 + 浪花线）、river_flow（急流：长条水纹 + 回旋 + 白浪）、foam_line、ripple_rings、driftwood
- 岸 / 石：earth_mass（土石岸的一整块：地层、裂纹、苔）、stone_face
- 植物：willow2、bamboo2、reeds、bamboo shoots
- 桥：bamboo_pole、rope、plank、deck（桥面）、lashing（绳扎）
- 海底：seaweed、coral_antler、coral_fan、coral_mound、scallop、shell_scales（贝壳瓦片）、light_shafts、floaters
- Sub：把一组笔触裁进一个多边形里画（水面、岸体用）
"""
import math
import numpy as np
import cv2
from cn import *  # noqa  (带出 pt 的全部名字)

NW = {
    # 海 / 江（深、冷、灰蓝）
    'sea_hi': hexc('#9fb2bc'), 'sea': hexc('#6f8794'), 'sea_dk': hexc('#44596a'), 'sea_deep': hexc('#2c3d4c'),
    'foam': hexc('#f1efe7'), 'foam_dk': hexc('#c9d0d2'),
    # 水下（靛蓝灰、灰绿）
    'uw_hi': hexc('#a7bcbd'), 'uw': hexc('#7b989c'), 'uw_dk': hexc('#55737d'), 'uw_deep': hexc('#37505d'), 'uw_abyss': hexc('#27394a'),
    # 珠光
    'pearl': hexc('#eee9df'), 'pearl_dk': hexc('#cdc7bb'), 'pearl_sh': hexc('#a9b2bd'),
    'pink': hexc('#cdb5b0'), 'pink_dk': hexc('#a68d8b'), 'ochre': hexc('#c3ae88'), 'ochre_dk': hexc('#9b8863'),
    'slate': hexc('#8499b0'), 'slate_dk': hexc('#5e7388'), 'slate_lt': hexc('#aebccb'),
    # 竹木绳
    'bamboo': hexc('#93a595'), 'bamboo_dk': hexc('#5d7466'), 'bamboo_lt': hexc('#bccabb'),
    'plank': hexc('#b6a37d'), 'plank_dk': hexc('#85734f'), 'plank_lt': hexc('#d3c5a2'),
    'rope': hexc('#bcae96'), 'rope_dk': hexc('#85775f'),
    'shoot': hexc('#9a8159'), 'shoot_dk': hexc('#6a5538'),
    # 沙
    'sand': hexc('#c2b697'), 'sand_dk': hexc('#9d9074'), 'sand_wet': hexc('#7f8b8c'), 'sand_lt': hexc('#dcd3bb'),
    'basalt': hexc('#4a5054'), 'basalt_dk': hexc('#2a2f33'), 'basalt_lt': hexc('#7d8486'),
    'weed_dry': hexc('#8c8a72'), 'weed_dk': hexc('#5f6150'),
    'mud': hexc('#7b7b72'), 'mud_dk': hexc('#55564f'),
}

_SCR = {}


# ───────────────────────── 裁切作画 ─────────────────────────
class Sub:
    """with Sub(L, poly=[...]) as T: …在 T 上随便画…；退出时只把落在多边形（或 mask）里的部分合到 L。
    soft：蒙版边缘的虚化（像素），smooth/wob：多边形的圆滑和手抖。mask+bbox 可以直接给蒙版。"""

    def __init__(self, L, poly=None, mask=None, bbox=None, soft=0.0, smooth=1, wob=0.0, seed=0, keep=1.0):
        self.L = L
        self.ok = True
        self.keep = keep
        if poly is not None:
            p = np.asarray(poly, F)
            if smooth:
                p = chaikin(p, smooth, True)
            if wob:
                p = wobble_pts(p, wob, seed)
            r = poly_mask(p, L.w, L.h, pad=int(soft * 2) + 4)
            if r is None:
                self.ok = False
                self.y0 = self.y1 = self.x0 = self.x1 = 0
                self.m = None
                return
            self.y0, self.y1, self.x0, self.x1, m = r
            if soft > 0:
                m = cv2.GaussianBlur(m, (0, 0), soft)
            self.m = m
        else:
            self.x0, self.y0, self.x1, self.y1 = [int(v) for v in bbox]
            self.x0, self.y0 = max(self.x0, 0), max(self.y0, 0)
            self.x1, self.y1 = min(self.x1, L.w), min(self.y1, L.h)
            h, w = self.y1 - self.y0, self.x1 - self.x0
            self.m = np.ones((h, w), F) if mask is None else np.asarray(mask, F)[:h, :w]

    def __enter__(self):
        key = (self.L.w, self.L.h)
        if key not in _SCR:
            _SCR[key] = Canvas(self.L.w, self.L.h)
        T = _SCR[key]
        T.rgb[:] = 0
        T.a[:] = 0
        self.T = T
        return T

    def __exit__(self, *a):
        if not self.ok:
            return False
        T, L = self.T, self.L
        y0, y1, x0, x1 = self.y0, self.y1, self.x0, self.x1
        L.over(y0, y1, x0, x1, T.rgb[y0:y1, x0:x1], T.a[y0:y1, x0:x1] * self.m * self.keep)
        return False


def densify(poly, step=50):
    """多边形的长边加密（避免 chaikin 圆滑时把大块的直角削掉）。"""
    p = np.asarray(poly, F)
    out = []
    for a, b in zip(p, np.roll(p, -1, axis=0)):
        n = max(int(np.hypot(*(b - a)) / step), 1)
        for k in range(n):
            out.append(a + (b - a) * (k / n))
    return np.array(out, F)


def fill_region(L, x0, y0, x1, y1, top, bot, seed=0, mott=0.12, gamma=1.0, scale=170, alpha=None):
    """矩形里铺一块纵向渐变 + 水渍斑驳的底色。alpha 可以是 (h,w) 的数组。"""
    x0, y0 = max(int(x0), 0), max(int(y0), 0)
    x1, y1 = min(int(x1), L.w), min(int(y1), L.h)
    h, w = y1 - y0, x1 - x0
    if h <= 0 or w <= 0:
        return
    t = (np.linspace(0, 1, h, dtype=F) ** gamma)[:, None, None]
    base = mix(np.asarray(top, F), np.asarray(bot, F), t) * np.ones((1, w, 1), F)
    n = fbm(h, w, seed, scale, 4, 0.5, warp=scale * 0.25)
    base = base * (1 + (n[..., None] - 0.5) * mott * 2)
    a = np.ones((h, w), F) if alpha is None else np.asarray(alpha, F)
    L.over(y0, y1, x0, x1, np.clip(base, 0, 1).astype(F), a)


def vfade(h, a0, a1, p=1.0):
    return (np.linspace(a0, a1, h, dtype=F) ** p)[:, None]


# ───────────────────────── 浪 / 水 ─────────────────────────
def foam_dots(L, x0, x1, y0, y1, n, seed, col=None, op=0.8, rmin=0.8, rmax=2.4):
    col = NW['foam'] if col is None else col
    r = np.random.default_rng(seed)
    st = []
    for _ in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        ln = r.uniform(1.5, 5)
        st.append((x, y, x + ln, y + r.normal(0, 0.6), r.uniform(rmin, rmax), r.uniform(0.35, 1.0) * op))
    flicks(L, st, color=col)


def foam_line(L, pts, w=3.0, seed=0, op=0.85, col=None, spray=True, dry=0.35):
    """一条白色的浪花线：粗细不均、有飞白，再散一点泡沫碎点。"""
    col = NW['foam'] if col is None else col
    brush(L, pts, w0=w, color=col, op=op, seed=seed, wob=w * 0.5, taper=0.25, dry=dry)
    if spray:
        r = np.random.default_rng(seed + 1)
        p = np.asarray(catmull(np.asarray(pts, F), 6) if len(pts) >= 3 else pts, F)
        st = []
        for _ in range(int(len(p) * 0.7)):
            q = p[r.integers(len(p))]
            st.append((q[0] + r.normal(0, w * 1.4), q[1] + r.normal(0, w * 1.2), q[0] + r.normal(0, w * 2), q[1] + r.normal(0, w * 1.0), r.uniform(0.9, 2.2), r.uniform(0.3, 0.9) * op))
        flicks(L, st, color=col)


def sea_rows(L, x0, x1, y0, y1, seed, rows=34, p=1.6, hi=None, lo=None, foam=None, foam_k=0.5, len0=50, len1=420, dens=1.0, w0=1.2, w1=4.6, op=1.0, hook=1.0):
    """海面：从上（y0，远）到下（y1，近）一行行的浪纹——每道浪是“暗的谷 + 亮的脊 + 偶尔的白浪花”，越近越长越粗、行距越大。"""
    hi = NW['sea_hi'] if hi is None else np.asarray(hi, F)
    lo = NW['sea_deep'] if lo is None else np.asarray(lo, F)
    foam = NW['foam'] if foam is None else np.asarray(foam, F)
    r = np.random.default_rng(seed)
    Hh = y1 - y0
    for k in range(rows):
        d = (k + r.uniform(0.15, 0.85)) / rows
        y = y0 + Hh * d ** p
        lm = len0 + (len1 - len0) * d
        n = int((x1 - x0) / (lm * 0.8) * dens) + 1
        for _ in range(n):
            x = r.uniform(x0 - lm * 0.4, x1)
            ln = lm * r.uniform(0.45, 1.4)
            xe = min(x + ln, x1 + 4)
            xs = max(x, x0 - 4)
            if xe - xs < 8:
                continue
            ln = xe - xs
            hh = (1.2 + 7.5 * d) * r.uniform(0.6, 1.3) * hook
            yy = y + r.normal(0, 1 + 3 * d)
            # 谷：暗的一道，在脊的下面
            brush(L, [(xs, yy + hh * 0.9 + 2), (xs + ln * 0.5, yy + hh * 0.9 + 3 + r.normal(0, 1)), (xe, yy + hh * 0.6 + 2)], w0=(1.6 + 5.5 * d) * r.uniform(0.7, 1.3), color=lo, op=r.uniform(0.25, 0.55) * op, seed=int(r.integers(1e6)), wob=1.2, taper=0.4, dry=0.15)
            # 脊：亮的弧
            brush(L, [(xs, yy), (xs + ln * 0.35, yy - hh), (xs + ln * 0.75, yy - hh * 0.55), (xe, yy + hh * 0.25)], w0=(w0 + (w1 - w0) * d) * r.uniform(0.7, 1.2), color=hi, op=r.uniform(0.2, 0.55) * op, seed=int(r.integers(1e6)), wob=1.0, taper=0.35, dry=0.3)
            if r.random() < foam_k * (0.25 + d):
                ff = r.uniform(0.35, 0.7)
                fx0 = xs + ln * r.uniform(0.0, 0.3)
                brush(L, [(fx0, yy - hh * 0.9), (fx0 + ln * ff * 0.5, yy - hh * 1.2), (fx0 + ln * ff, yy - hh * 0.6)], w0=(0.9 + 3.0 * d) * r.uniform(0.7, 1.3), color=foam, op=r.uniform(0.45, 0.95) * op, seed=int(r.integers(1e6)), wob=0.8, taper=0.35, dry=0.45)


def sea_body(L, x0, y0, x1, y1, seed, top, bot, rows=34, p=1.6, hi=None, lo=None, foam_k=0.5, len0=50, len1=420, dens=1.0, w1=4.6, mott=0.14, gamma=0.9, swell=6, alpha=None, hook=1.0, op=1.0):
    """一整片海 / 水：底色渐变 → 几块宽的湿色块（涌）→ 浪纹行。"""
    fill_region(L, x0, y0, x1, y1, top, bot, seed=seed, mott=mott, gamma=gamma, alpha=alpha)
    r = np.random.default_rng(seed + 11)
    Hh = y1 - y0
    for _ in range(swell):
        d = r.random() ** 1.3
        yy = y0 + Hh * d
        x = r.uniform(x0 - 200, x1 - 200)
        ln = r.uniform(300, 900) * (0.5 + d)
        th = (10 + 40 * d) * r.uniform(0.6, 1.2)
        pts = [(x, yy), (x + ln * 0.3, yy - th * 0.6), (x + ln * 0.7, yy - th * 0.4), (x + ln, yy + th * 0.1), (x + ln * 0.6, yy + th), (x + ln * 0.2, yy + th * 0.8)]
        wash(L, pts, mix(np.asarray(top, F), np.asarray(bot, F), 0.35 + 0.4 * r.random()) * r.uniform(0.7, 1.2), op=r.uniform(0.12, 0.3), wob=3, seed=int(r.integers(1e6)), smooth=2, tex_k=0.12, rim=0.18, rim_w=5)
    sea_rows(L, x0, x1, y0, y1, seed + 3, rows=rows, p=p, hi=hi, lo=lo, foam_k=foam_k, len0=len0, len1=len1, dens=dens, w1=w1, hook=hook, op=op)


def river_flow(L, x0, y0, x1, y1, seed, n=520, hi=None, lo=None, foam=None, len0=90, len1=520, w1=5.0, ang=0.0, curve=0.06, foam_k=0.35):
    """急流：长长的、略带弯曲的水纹（暗脊 + 亮脊交错），顺着水流方向（ang 弧度，0=向右）。比海面更“拉丝”。"""
    hi = NW['sea_hi'] if hi is None else np.asarray(hi, F)
    lo = NW['sea_deep'] if lo is None else np.asarray(lo, F)
    foam = NW['foam'] if foam is None else np.asarray(foam, F)
    r = np.random.default_rng(seed)
    Hh = y1 - y0
    for _ in range(n):
        d = r.random() ** 1.15
        y = y0 + Hh * d
        x = r.uniform(x0 - 100, x1)
        ln = r.uniform(len0, len1) * (0.5 + 0.9 * d)
        a = ang + r.normal(0, 0.03)
        bend = r.normal(0, curve) * ln
        xe = x + math.cos(a) * ln
        ye = y + math.sin(a) * ln + bend
        pts = [(x, y), ((x + xe) / 2, (y + ye) / 2 + bend * 0.3 + r.normal(0, 2)), (xe, ye)]
        w = (1.2 + w1 * d) * r.uniform(0.6, 1.3)
        c = r.random()
        if c < 0.46:
            brush(L, pts, w0=w * 1.5, color=lo, op=r.uniform(0.18, 0.5), seed=int(r.integers(1e6)), wob=1.5, taper=0.4, dry=0.25)
        elif c < 0.9:
            brush(L, pts, w0=w, color=hi, op=r.uniform(0.14, 0.5), seed=int(r.integers(1e6)), wob=1.5, taper=0.4, dry=0.35)
        else:
            brush(L, pts, w0=w * 0.9, color=foam, op=r.uniform(0.35, 0.8), seed=int(r.integers(1e6)), wob=1.2, taper=0.4, dry=0.5)
        if r.random() < foam_k * d * 0.6:
            q = [(x + ln * 0.2, y + 3), (x + ln * 0.5, y + 1 + r.normal(0, 2)), (x + ln * 0.8, y + 4)]
            brush(L, q, w0=1.0 + 2.2 * d, color=foam, op=r.uniform(0.3, 0.7), seed=int(r.integers(1e6)), wob=1.0, taper=0.4, dry=0.5)


def whitecap(L, x, y, ln, h=10, seed=0, op=0.9, w=3.0):
    """急流里的白浪：一串翻起的浪头（折线 + 倒钩）+ 浪头下的泡沫碎点。"""
    r = np.random.default_rng(seed)
    pts = []
    nseg = max(int(ln / 26), 3)
    for i in range(nseg + 1):
        t = i / nseg
        pts.append((x + t * ln, y + math.sin(t * math.pi * 2.2 + seed) * h * 0.4 - (h if i % 2 else 0) * r.uniform(0.5, 1.0) * math.sin(t * math.pi)))
    brush(L, pts, w0=w, color=NW['foam'], op=op, seed=seed, wob=1.3, taper=0.3, dry=0.4, smooth=True)
    brush(L, [(px, py + 5) for px, py in pts], w0=w * 0.6, color=NW['foam_dk'], op=op * 0.5, seed=seed + 2, wob=1.3, taper=0.3, dry=0.5)
    foam_dots(L, x, x + ln, y - h * 0.4, y + h * 1.4, int(ln / 6), seed + 3, op=op * 0.9)


def eddy(L, cx, cy, rx, ry, seed=0, turns=2.2, col=None, op=0.5, w=2.6):
    """水里的回旋：一条向内收的螺旋（压扁的）。"""
    col = NW['sea_hi'] if col is None else col
    n = 36
    pts = []
    for i in range(n):
        t = i / (n - 1)
        a = t * turns * 2 * math.pi + seed
        rr = 1 - t * 0.85
        pts.append((cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr))
    brush(L, pts, w0=w, color=col, op=op, seed=seed, wob=0.8, taper=0.25, dry=0.35)
    brush(L, [(px + 1, py + 3) for px, py in pts[: n * 2 // 3]], w0=w * 1.2, color=NW['sea_deep'], op=op * 0.6, seed=seed + 1, wob=0.8, taper=0.3, dry=0.2)


def ripple_rings(L, cx, cy, rx, ry, n=5, seed=0, col=None, shade=None, op=0.7, w=2.2, gap=0.19, arcs=True):
    """同心的涟漪（压扁的椭圆，断断续续）：泉眼、桥脚、鱼跃处。"""
    col = NW['pearl'] if col is None else col
    shade = NW['uw_dk'] if shade is None else shade
    r = np.random.default_rng(seed)
    for k in range(n):
        f = (k + 1) / n
        rr, ry_ = rx * f, ry * f
        a0 = r.uniform(0, 2 * math.pi)
        span = 2 * math.pi * r.uniform(0.7, 0.95) if arcs else 2 * math.pi
        pts = [(cx + math.cos(a0 + t) * rr, cy + math.sin(a0 + t) * ry_) for t in np.linspace(0, span, 26)]
        brush(L, [(px + 1, py + 3.5) for px, py in pts], w0=w * 1.3, color=shade, op=op * 0.5 * (1 - 0.4 * f), seed=int(r.integers(1e6)), wob=0.7, taper=0.3, dry=0.1)
        brush(L, pts, w0=w * (1.2 - 0.4 * f), color=col, op=op * (1.0 - 0.45 * f), seed=int(r.integers(1e6)), wob=0.7, taper=0.3, dry=0.3)


def driftwood(L, x, y, ln, seed=0, ang=-0.05, col=None, th=24):
    """一根顺水漂的枯木：粗的一头 + 断枝 + 剥了皮的浅色纹 + 水线上的白泡沫。"""
    col = N['wood_dk'] * 0.85 if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda t, off=0: (x + ca * ln * t - sa * off, y + sa * ln * t + ca * off)
    top = [P(0, -th * 0.5), P(0.2, -th * 0.55), P(0.5, -th * 0.5), P(0.8, -th * 0.38), P(1.0, -th * 0.22)]
    bot = [P(1.0, th * 0.22), P(0.8, th * 0.4), P(0.5, th * 0.52), P(0.2, th * 0.58), P(0, th * 0.5)]
    # 水下的暗影
    wash(L, [P(0.02, th * 0.6), P(0.5, th * 1.1), P(0.98, th * 0.55), P(0.5, th * 0.7)], NW['sea_deep'], op=0.5, wob=2, seed=seed + 1, tex_k=0.1)
    wash(L, top + bot, col, op=0.97, wob=1.4, seed=seed, smooth=2, tex_k=0.22, rim=0.2)
    wash(L, [P(0.02, th * 0.1), P(0.3, th * 0.2), P(0.8, th * 0.15), P(0.97, th * 0.05), P(0.8, th * 0.4), P(0.3, th * 0.55), P(0.02, th * 0.48)], col * 0.55, op=0.55, wob=1.3, seed=seed + 2, tex_k=0.15)
    st = []
    for _ in range(26):
        t = r.uniform(0.02, 0.98)
        off = r.uniform(-th * 0.42, th * 0.42)
        p0 = P(t, off)
        p1 = P(min(t + r.uniform(0.04, 0.16), 1.0), off + r.normal(0, 1.5))
        st.append((p0[0], p0[1], p1[0], p1[1], r.uniform(0.8, 1.8), r.uniform(0.3, 0.7)))
    flicks(L, st, color=N['paper'] * 0.8 if r.random() < 2 else INK)
    brush(L, top, w0=2.4, color=INK, op=0.7, seed=seed + 3, wob=0.8, taper=0.15, dry=0.3)
    brush(L, bot[::-1], w0=2.0, color=INK, op=0.6, seed=seed + 4, wob=0.8, taper=0.15, dry=0.3)
    # 断枝：粗的一头
    for (t, side, ln2, a2) in [(0.18, -1, 46, 0.9), (0.62, -1, 30, 0.7), (0.4, 1, 24, 0.8)]:
        b0 = P(t, side * th * 0.45)
        b1 = (b0[0] + math.cos(ang + side * a2 + (math.pi if side < 0 else 0) * 0 - side * 0.0) * ln2 * 0.5 + (ln2 * 0.25), b0[1] + side * ln2 * 0.9)
        brush(L, [b0, ((b0[0] + b1[0]) / 2 + 2, (b0[1] + b1[1]) / 2), b1], w0=th * 0.3, w1=th * 0.1, color=col, op=0.95, seed=int(r.integers(1e6)), wob=1.0, taper=0.1)
    # 粗头的断口（年轮）
    ex, ey = P(0, 0)
    wash(L, [(ex + math.cos(a) * th * 0.18, ey + math.sin(a) * th * 0.5) for a in np.linspace(0, 2 * math.pi, 10, endpoint=False)], N['wood'] * 1.2, op=0.9, wob=0.8, seed=seed + 7, smooth=2)
    # 水线：泡沫
    for k in range(3):
        pts = [P(-0.1 + 0.06 * k, th * 0.62 + 4 * k), P(0.3, th * 0.7 + 5 + 3 * k), P(0.7, th * 0.66 + 3 + 3 * k), P(1.12, th * 0.4 + 2 * k)]
        foam_line(L, pts, w=2.4 - 0.3 * k, seed=seed + 20 + k, op=0.8 - 0.15 * k, spray=(k == 0))
    foam_line(L, [P(1.0, -th * 0.3), P(1.1, -th * 0.1 + 6), P(1.25, th * 0.15)], w=2.2, seed=seed + 30, op=0.7)


# ───────────────────────── 岸 / 石 ─────────────────────────
def earth_mass(L, poly, seed, y_top, y_bot, top_col=None, bot_col=None, strata=14, wall_dark=0.55, outline=True, soft=0.0, edge_pts=None, moss=0.5, cracks=22, ledge_col=None):
    """一整块土石岸：渐变底 + 横向地层 + 斜裂纹 + 零星的石块面 + 苔点 + 湿边。poly 是外轮廓（已含手抖）。
    edge_pts：沿这条折线（岸壁、岸顶）描一道断续的墨线。"""
    top_col = N['earth'] if top_col is None else np.asarray(top_col, F)
    bot_col = N['stone_dk'] if bot_col is None else np.asarray(bot_col, F)
    ledge_col = N['earth_lt'] if ledge_col is None else np.asarray(ledge_col, F)
    pa = np.asarray(poly, F)
    x0, x1 = int(pa[:, 0].min()) - 4, int(pa[:, 0].max()) + 4
    y0, y1 = int(pa[:, 1].min()) - 4, int(pa[:, 1].max()) + 4
    r = np.random.default_rng(seed)
    with Sub(L, poly=densify(poly, 40), smooth=1, wob=1.2, seed=seed, soft=soft) as T:
        fill_region(T, x0, y0, x1, y1, top_col, bot_col, seed=seed + 1, mott=0.16, gamma=0.8)
        # 地层：一条条起伏的暗带 / 亮带
        for k in range(strata):
            yy = y_top + (y_bot - y_top) * (k + r.uniform(0.2, 0.9)) / strata
            xa = x0 - 20
            while xa < x1:
                ln = r.uniform(120, 420)
                pts = [(xa, yy + r.normal(0, 3)), (xa + ln * 0.33, yy + r.normal(0, 6)), (xa + ln * 0.66, yy + r.normal(0, 6)), (xa + ln, yy + r.normal(0, 4))]
                dark = r.random() < 0.6
                brush(T, pts, w0=r.uniform(3, 12), color=mix(bot_col, INK, 0.3) if dark else ledge_col, op=r.uniform(0.12, 0.34), seed=int(r.integers(1e6)), wob=2.5, taper=0.4, dry=0.3)
                if r.random() < 0.55:
                    brush(T, [(px, py + 4) for px, py in pts], w0=1.6, color=INK, op=r.uniform(0.2, 0.45), seed=int(r.integers(1e6)), wob=1.5, taper=0.4, dry=0.35)
                xa += ln * r.uniform(0.75, 1.1)
        # 埋在岸里的大石：几块有明暗面的岩石（rock），被岸体的轮廓裁掉多出来的部分
        for _ in range(int((x1 - x0) * (y1 - y0) / 150000) + 1):
            cx, cy = r.uniform(x0 + 40, x1 - 40), r.uniform(y_top + 120, y1 - 40)
            w_, h_ = r.uniform(220, 420), r.uniform(120, 230)
            rock(T, cx, cy, w_, h_, seed=int(r.integers(1e6)), col=mix(bot_col, top_col, 0.35), dark=mix(bot_col, INK, 0.45), light=mix(top_col, ledge_col, 0.5), lit_dir=1, op=0.85)
        # 棱角分明的小石面
        for _ in range(int((x1 - x0) * (y1 - y0) / 60000)):
            cx, cy = r.uniform(x0, x1), r.uniform(y0, y1)
            n_ = int(r.integers(5, 8))
            ang = np.sort(r.uniform(0, 2 * math.pi, n_))
            w_, h_ = r.uniform(50, 130), r.uniform(26, 60)
            pts = [(cx + math.cos(a_) * w_ * r.uniform(0.5, 1.0), cy + math.sin(a_) * h_ * r.uniform(0.5, 1.0)) for a_ in ang]
            lt = r.random() < 0.4
            wash(T, pts, ledge_col if lt else bot_col * 0.8, op=r.uniform(0.08, 0.16), wob=1.5, seed=int(r.integers(1e6)), smooth=1, tex_k=0.18, rim=0.3, rim_w=3)
            brush(T, pts[:3], w0=1.8, color=INK, op=0.3, seed=int(r.integers(1e6)), wob=1.0, taper=0.3, dry=0.4)
            if not lt:
                hatch(T, pts, 72, 8, 22, INK, op=0.32, w=1.3, seed=int(r.integers(1e6)))
        # 底部、临水的一面压暗（湿、背光）
        wash(T, [(x0, y1 - (y1 - y_top) * 0.45), (x1, y1 - (y1 - y_top) * 0.55), (x1, y1 + 10), (x0, y1 + 10)], INK, op=0.28, wob=18, seed=seed + 9, smooth=2, tex_k=0.1, rim=0.0)
        # 裂纹：从上往下斜斜的折线
        st = []
        for _ in range(cracks):
            cx, cy = r.uniform(x0, x1), r.uniform(y_top + 30, y_bot)
            ln = r.uniform(40, 150)
            a = math.radians(r.normal(80, 18)) * (1 if r.random() < 0.5 else -1)
            pts = [(cx, cy), (cx + math.cos(a) * ln * 0.5 + r.normal(0, 5), cy + abs(math.sin(a)) * ln * 0.5), (cx + math.cos(a) * ln + r.normal(0, 6), cy + abs(math.sin(a)) * ln)]
            brush(T, pts, w0=r.uniform(1.4, 3.2), w1=0.6, color=INK, op=r.uniform(0.3, 0.6), seed=int(r.integers(1e6)), wob=1.5, taper=0.2, dry=0.25)
        # 皴擦
        st = []
        for _ in range(int((x1 - x0) * (y1 - y0) / 700)):
            px, py = r.uniform(x0, x1), r.uniform(y_top, y1)
            ln = r.uniform(8, 30)
            a = math.radians(r.normal(72, 14)) * (1 if r.random() < 0.5 else -1)
            st.append((px, py, px + math.cos(a) * ln * 0.5, py + abs(math.sin(a)) * ln, r.uniform(0.9, 2.2), r.uniform(0.12, 0.42)))
        flicks(T, st, color=INK)
        # 苔点：向上的短笔，偏灰绿
        st = []
        for _ in range(int((x1 - x0) * (y1 - y0) / 3000 * moss)):
            px, py = r.uniform(x0, x1), r.uniform(y_top, y1)
            st.append((px, py, px + r.normal(0, 3), py - r.uniform(2, 7), r.uniform(1.6, 3.4), r.uniform(0.15, 0.45)))
        flicks(T, st, color=N['grass_dk'])
    if edge_pts is not None:
        ep = np.asarray(edge_pts, F)
        i = 0
        while i < len(ep) - 3:
            ln = int(r.integers(5, 14))
            seg = ep[i:i + ln]
            if len(seg) >= 3:
                brush(L, seg, w0=r.uniform(2.4, 4.6), color=INK, op=r.uniform(0.55, 0.85), seed=int(r.integers(1e6)), wob=1.2, taper=0.2, dry=0.3)
            i += ln + int(r.integers(0, 3))


def hanging_roots(L, x, y, n, seed=0, ln=(30, 110), col=None, op=0.8):
    """从岸沿垂下来的细根。"""
    col = N['wood_dk'] * 0.7 if col is None else col
    r = np.random.default_rng(seed)
    for _ in range(n):
        px = x + r.normal(0, 40)
        l = r.uniform(*ln)
        brush(L, [(px, y), (px + r.normal(0, 6), y + l * 0.5), (px + r.normal(0, 12), y + l)], w0=r.uniform(1.5, 3.2), w1=0.6, color=col, op=op * r.uniform(0.5, 1), seed=int(r.integers(1e6)), wob=1.0, taper=0.15)


def tufts(L, x0, x1, ys, n, seed=0, col=None, op=0.75, hmin=12, hmax=40, spread=3.0):
    """草丛。ys 可以是数组或常数。"""
    col = N['grass_dk'] if col is None else col
    r = np.random.default_rng(seed)
    st = []
    for _ in range(n):
        x = r.uniform(x0, x1)
        y = (ys[int(min(max(x, 0), len(ys) - 1))] if hasattr(ys, '__len__') else ys) + r.uniform(-2, 12)
        for k in range(int(r.integers(3, 8))):
            ln = r.uniform(hmin, hmax)
            st.append((x + k * spread * 0.7, y, x + k * spread * 0.7 + r.normal(0, ln * 0.35), y - ln, r.uniform(0.9, 1.9), r.uniform(0.3, 0.85) * op))
    flicks(L, st, color=col)


def willow2(L, x, y, h, seed=0, col=None, op=1.0, lean=0.1, density=1.0):
    """柳：粗而弯的树干 + 一团树冠（半透明的水彩色块罩住短枝）+ 几道下垂的“帘” + 密密的细长条（墨线，浓淡不一）。"""
    col = N['grass'] if col is None else np.asarray(col, F)
    dk = N['grass_dk']
    wd = N['wood_dk'] * 0.6
    r = np.random.default_rng(seed)
    top = (x + h * lean, y - h * 0.62)
    # 干：下粗上细，根部张开，一侧暗、一侧有皴
    brush(L, [(x, y + 2), (x + h * 0.012, y - h * 0.2), (x + h * lean * 0.55, y - h * 0.42), top], w0=h * 0.095, w1=h * 0.04, color=wd, op=0.97 * op, seed=seed, wob=2.5, taper=0.05)
    brush(L, [(x + h * 0.028, y), (x + h * 0.034, y - h * 0.2), (x + h * lean * 0.55 + h * 0.018, y - h * 0.42), (top[0] + h * 0.01, top[1])], w0=h * 0.035, w1=h * 0.012, color=wd * 0.45, op=0.65 * op, seed=seed + 1, wob=2, taper=0.1)
    for s_ in (-1, 1):
        brush(L, [(x + s_ * h * 0.03, y - 6), (x + s_ * h * 0.08, y + 2), (x + s_ * h * 0.13, y + 6)], w0=h * 0.03, w1=2, color=wd, op=0.9 * op, seed=seed + 5 + s_, wob=1, taper=0.1)
    st = []
    for _ in range(int(h * 0.5)):
        t = r.uniform(0.0, 0.8)
        px = x + h * lean * 0.55 * t + r.uniform(-1, 1) * h * 0.04 * (1 - t * 0.6)
        py = y - h * 0.42 * t / 0.8 * 1.0
        st.append((px, py, px + r.normal(0, 1.2), py - r.uniform(8, 22), r.uniform(0.9, 1.9), r.uniform(0.25, 0.6) * op))
    flicks(L, st, color=INK)
    # 分枝：四五根，向外弯，枝端落成垂条的根
    ctr = []
    for k in range(6):
        a = (k / 5 - 0.5) * 2.4 + r.normal(0, 0.1)
        bx = top[0] + math.sin(a) * h * 0.27
        by = top[1] - h * 0.1 + abs(math.sin(a)) * h * 0.16 + r.uniform(-0.03, 0.03) * h
        brush(L, [(top[0], top[1] + 4), ((top[0] + bx) / 2, (top[1] + by) / 2 - h * 0.07), (bx, by)], w0=h * 0.026, w1=2, color=wd, op=0.9 * op, seed=int(r.integers(1e6)), wob=1.5, taper=0.08)
        ctr.append((bx, by))
    # 树冠团
    for (bx, by) in ctr:
        rx, ry = h * r.uniform(0.11, 0.17), h * r.uniform(0.06, 0.1)
        pts = [(bx + math.cos(a_) * rx * r.uniform(0.8, 1.15), by + math.sin(a_) * ry * r.uniform(0.8, 1.15)) for a_ in np.linspace(0, 2 * math.pi, 11, endpoint=False)]
        wash(L, pts, mix(col, dk, r.uniform(0.1, 0.4)), op=0.5 * op, wob=3, seed=int(r.integers(1e6)), smooth=2, tex_k=0.25, rim=0.2, rim_w=3)
    # 帘
    for (bx, by) in ctr:
        ln = r.uniform(0.34, 0.6) * h
        wdt = r.uniform(0.12, 0.2) * h
        pts = [(bx - wdt, by), (bx + wdt, by - 6)]
        for k in range(8):
            pts.append((bx + wdt * (1 - k / 7 * 2) * r.uniform(0.85, 1.1) + r.normal(0, 6), by + ln * r.uniform(0.6, 1.0)))
        wash(L, pts, mix(col, N['paper'], 0.1), op=0.28 * op, wob=5, seed=int(r.integers(1e6)), smooth=2, tex_k=0.22, rim=0.1)
    for _ in range(int(h * 0.85 * density)):
        bx, by = ctr[int(r.integers(len(ctr)))]
        bx += r.normal(0, h * 0.09)
        ln = r.uniform(0.3, 0.7) * h
        sw = r.normal(0, 10)
        brush(L, [(bx, by), (bx + sw * 0.3, by + ln * 0.5), (bx + sw, by + ln)], w0=r.uniform(1.4, 2.4), w1=0.6, color=mix(col, dk, r.uniform(0.0, 0.8)), op=r.uniform(0.3, 0.8) * op, seed=int(r.integers(1e6)), wob=1.4, taper=0.25)
    st = []
    for _ in range(int(h * 1.4 * density)):
        bx, by = ctr[int(r.integers(len(ctr)))]
        px = bx + r.normal(0, h * 0.12)
        py = by + r.uniform(0.05, 0.7) * h
        st.append((px, py, px + r.normal(0, 2), py + r.uniform(5, 14), r.uniform(1.8, 3.2), r.uniform(0.2, 0.55) * op))
    flicks(L, st, color=dk)


def bamboo2(L, x, y, h, seed=0, n=9, col=None, op=1.0, spread=0.18):
    """竹丛：几根竿（节、受光的亮线、背光的暗线）+ 竹叶（成簇的尖叶，一簇簇压在竿的上半截）。x 是丛的中点。"""
    col = NW['bamboo'] if col is None else np.asarray(col, F)
    dk = NW['bamboo_dk']
    r = np.random.default_rng(seed)
    culms = []
    for i in range(n):
        bx = x + (i - (n - 1) / 2) * h * spread / max(n - 1, 1) * 2 + r.normal(0, h * 0.02)
        bh = h * r.uniform(0.7, 1.08)
        lean = r.normal(0, 0.05) + (bx - x) / h * 0.15
        top = (bx + lean * bh, y - bh)
        mid = (bx + lean * bh * 0.4 + r.normal(0, 3), y - bh * 0.55)
        wd = h * r.uniform(0.016, 0.026)
        brush(L, [(bx, y), mid, top], w0=wd, w1=wd * 0.55, color=mix(col, N['paper'], 0.1), op=0.95 * op, seed=int(r.integers(1e6)), wob=1.0, taper=0.05)
        brush(L, [(bx - wd * 0.25, y), (mid[0] - wd * 0.25, mid[1]), (top[0] - wd * 0.15, top[1])], w0=wd * 0.28, w1=0.8, color=mix(col, N['paper'], 0.7), op=0.7 * op, seed=int(r.integers(1e6)), wob=1.0, taper=0.1, dry=0.2)
        brush(L, [(bx + wd * 0.38, y), (mid[0] + wd * 0.38, mid[1]), (top[0] + wd * 0.2, top[1])], w0=wd * 0.32, w1=0.8, color=dk, op=0.7 * op, seed=int(r.integers(1e6)), wob=1.0, taper=0.1)
        ny = y - r.uniform(30, 60)
        while ny > top[1] + 20:
            t = (y - ny) / bh
            nx = bx + (mid[0] - bx) * min(t / 0.55, 1) * 0.9 + (top[0] - mid[0]) * max(t - 0.55, 0) / 0.45 * 0.9
            brush(L, [(nx - wd * 0.7, ny), (nx + wd * 0.7, ny + 1.2)], w0=2.2, color=INK, op=0.7 * op, seed=int(r.integers(1e6)), taper=0.2, smooth=False)
            ny -= r.uniform(52, 90)
        culms.append((top, bh, wd))
    # 竹叶：成簇
    for (top, bh, wd) in culms:
        for _ in range(int(r.integers(3, 6))):
            ty = top[1] + r.uniform(0, bh * 0.4)
            tx = top[0] + r.normal(0, bh * 0.05)
            st = []
            dirx = r.choice([-1, 1])
            for k in range(int(r.integers(4, 8))):
                a = math.radians(r.uniform(10, 70)) * dirx + r.normal(0, 0.15)
                ln = r.uniform(30, 58)
                st.append((tx, ty, tx + math.cos(a) * ln, ty + math.sin(a) * ln * 0.6 + r.uniform(0, 12), r.uniform(3.0, 4.8), r.uniform(0.55, 0.92) * op))
            flicks(L, st, color=mix(dk, N['pine_dk'], r.uniform(0.2, 0.7)))


def reeds(L, x0, x1, y, n, seed=0, h=(40, 110), col=None, op=0.7):
    """水边的芦苇 / 荒草：细长的、微微弯的竿，带穗。"""
    col = N['grass_dk'] if col is None else col
    r = np.random.default_rng(seed)
    for _ in range(n):
        x = r.uniform(x0, x1)
        hh = r.uniform(*h)
        bend = r.normal(0, hh * 0.18)
        brush(L, [(x, y), (x + bend * 0.3, y - hh * 0.55), (x + bend, y - hh)], w0=r.uniform(1.4, 2.4), w1=0.7, color=col, op=op * r.uniform(0.5, 1), seed=int(r.integers(1e6)), wob=0.8, taper=0.1)
        if r.random() < 0.3:
            brush(L, [(x + bend, y - hh), (x + bend * 1.1, y - hh - 14)], w0=3.4, color=N['earth_dk'], op=op * 0.8, seed=int(r.integers(1e6)), taper=0.4)


# ───────────────────────── 竹 / 木 / 绳（桥和工具）─────────────────────────
def _poly_path(pts, step=5):
    p = np.asarray(pts, F)
    out = [p[0:1]]
    for a, b in zip(p[:-1], p[1:]):
        n = max(int(np.hypot(*(b - a)) / step), 1)
        out.append(a + (b - a) * (np.arange(1, n + 1)[:, None] / n))
    return np.vstack(out)


def bamboo_pole(L, p0, p1, w=16, seed=0, col=None, node=72, op=1.0, broken=False, ink=True):
    """一根竹竿：青灰的竿身、受光的亮线、背光的暗线、一节一节的竹节（暗线 + 小鼓包）、两头墨线。broken=True 时末端是参差的断口。"""
    col = NW['bamboo'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    p0, p1 = np.asarray(p0, F), np.asarray(p1, F)
    d = p1 - p0
    ln = float(np.hypot(*d)) + 1e-6
    t = d / ln
    nrm = np.array([-t[1], t[0]], F)
    if nrm[1] > 0:
        nrm = -nrm  # 指向“上”（亮的一侧）
    mid = (p0 + p1) / 2 + nrm * r.normal(0, 1.2)
    brush(L, [p0, mid, p1], w0=w, color=col, op=0.97 * op, seed=seed, wob=0.8, taper=0.02)
    brush(L, [p0 + nrm * w * 0.22, mid + nrm * w * 0.22, p1 + nrm * w * 0.22], w0=w * 0.24, color=NW['bamboo_lt'], op=0.75 * op, seed=seed + 1, wob=0.6, taper=0.1, dry=0.25)
    brush(L, [p0 - nrm * w * 0.34, mid - nrm * w * 0.34, p1 - nrm * w * 0.34], w0=w * 0.3, color=NW['bamboo_dk'], op=0.7 * op, seed=seed + 2, wob=0.6, taper=0.05)
    if ink:
        brush(L, [p0 - nrm * w * 0.5, mid - nrm * w * 0.5, p1 - nrm * w * 0.5], w0=1.6, color=INK, op=0.55 * op, seed=seed + 3, wob=0.6, taper=0.1, dry=0.25)
    s = r.uniform(0.15, 0.55) * node
    while s < ln - 8:
        c = p0 + t * s
        brush(L, [c - nrm * w * 0.56, c + nrm * w * 0.56 + t * 1.5], w0=2.8, color=INK, op=0.7 * op, seed=int(r.integers(1e6)), taper=0.25, smooth=False)
        brush(L, [c + t * 3.4 - nrm * w * 0.46, c + t * 3.4 + nrm * w * 0.46], w0=1.6, color=NW['bamboo_lt'], op=0.5 * op, seed=int(r.integers(1e6)), taper=0.3, smooth=False)
        s += node * r.uniform(0.8, 1.2)
    if broken:
        c = p1
        pts = [c - nrm * w * 0.55, c - nrm * w * 0.2 - t * w * 0.8, c + nrm * w * 0.05 + t * w * 0.2, c + nrm * w * 0.3 - t * w * 0.9, c + nrm * w * 0.55]
        wash(L, pts, NW['bamboo_lt'], op=0.9 * op, wob=0.6, seed=seed + 4, smooth=0, tex_k=0.1)
        brush(L, pts, w0=1.8, color=INK, op=0.6 * op, seed=seed + 5, wob=0.5, taper=0.1, smooth=False)


def rope(L, pts, w=9, seed=0, col=None, op=1.0, twist=True):
    """粗绳：浅灰褐的一股，斜向的捻纹，下侧一线暗影。"""
    col = NW['rope'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    p = catmull(np.asarray(pts, F), 8) if len(pts) >= 3 else _poly_path(pts, 6)
    brush(L, [(a + 0.8, b + w * 0.32) for a, b in p[::3]], w0=w * 0.9, color=NW['rope_dk'], op=0.55 * op, seed=seed + 1, wob=0.5, taper=0.03)
    brush(L, [(a, b) for a, b in p[::3]], w0=w, color=col, op=0.97 * op, seed=seed, wob=0.5, taper=0.03)
    if twist:
        path = _poly_path(p, w * 0.7)
        st = []
        for i in range(len(path) - 1):
            a, b = path[i], path[i + 1]
            tt = b - a
            tt = tt / (np.hypot(*tt) + 1e-6)
            nn = np.array([-tt[1], tt[0]], F)
            c = path[i]
            st.append((c[0] - nn[0] * w * 0.48 - tt[0] * 1, c[1] - nn[1] * w * 0.48 - tt[1] * 1, c[0] + nn[0] * w * 0.48 + tt[0] * w * 0.45, c[1] + nn[1] * w * 0.48 + tt[1] * w * 0.45, 1.3, 0.55 * op))
        flicks(L, st, color=NW['rope_dk'])
    brush(L, [(a, b - w * 0.28) for a, b in p[::3]], w0=w * 0.22, color=NW['plank_lt'], op=0.4 * op, seed=seed + 4, wob=0.5, taper=0.1, dry=0.4)


def rope_sag(L, p0, p1, sag, w=9, seed=0, n=14, **kw):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t + sag * (1 - (2 * t - 1) ** 2)))
    rope(L, pts, w=w, seed=seed, **kw)
    return pts


def lashing(L, x, y, w=22, seed=0, ang=0.0, op=1.0):
    """绳扎的结：几圈绕线 + 一个结头 + 垂下的线头。"""
    r = np.random.default_rng(seed)
    ca, sa = math.cos(ang), math.sin(ang)
    for k in range(4):
        o = (k - 1.5) * 4.2
        a = (x + ca * o - sa * (-w / 2), y + sa * o + ca * (-w / 2))
        b = (x + ca * (o + 2.5) - sa * (w / 2), y + sa * (o + 2.5) + ca * (w / 2))
        brush(L, [a, b], w0=3.4, color=NW['rope'], op=0.95 * op, seed=int(r.integers(1e6)), taper=0.2, smooth=False)
        brush(L, [(a[0] + 1.5, a[1] + 1), (b[0] + 1.5, b[1] + 1)], w0=1.2, color=NW['rope_dk'], op=0.7 * op, seed=int(r.integers(1e6)), taper=0.2, smooth=False)
    wash(L, [(x - 6, y - 5), (x + 6, y - 6), (x + 7, y + 5), (x - 5, y + 6)], NW['rope'], op=0.95 * op, wob=0.8, seed=seed + 5, smooth=1, tex_k=0.2, rim=0.3)
    brush(L, [(x - 6, y - 5), (x + 6, y + 5)], w0=1.3, color=INK, op=0.55 * op, seed=seed + 6, taper=0.3, smooth=False)
    brush(L, [(x + 3, y + 5), (x + 7, y + 18), (x + 4, y + 28)], w0=2.6, w1=1.2, color=NW['rope'], op=0.9 * op, seed=seed + 7, wob=1, taper=0.15)


def plank(L, x0, y0, x1, y1, th=24, seed=0, col=None, op=1.0, jag0=False, jag1=False, tilt=0.0):
    """一块木板（侧面看是细长条）：土黄灰、顺纹的细线、钉眼；jag0/jag1 表示左/右端是参差的断口。"""
    col = NW['plank'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    L0 = np.array([x0, y0], F)
    L1 = np.array([x1, y1], F)
    d = L1 - L0
    ln = float(np.hypot(*d))
    t = d / ln
    nn = np.array([-t[1], t[0]], F)
    top0, top1 = L0 - nn * th / 2, L1 - nn * th / 2
    bot0, bot1 = L0 + nn * th / 2, L1 + nn * th / 2

    def end(a, b, jag, sgn):
        if not jag:
            return []
        pts = []
        for k in range(1, 5):
            f = k / 5
            pts.append(a + (b - a) * f + t * sgn * r.uniform(-th * 0.9, th * 0.5) * (1 if k % 2 else -0.6))
        return pts
    poly = [top0, top0 + t * ln * 0.5 + nn * r.normal(0, 0.8), top1] + end(top1, bot1, jag1, -1) + [bot1, bot0 + t * ln * 0.5 + nn * r.normal(0, 0.8), bot0] + end(bot0, top0, jag0, 1)
    wash(L, poly, col, op=op, wob=0.7, seed=seed, smooth=0, tex_k=0.22, rim=0.25, rim_w=2.2)
    wash(L, [top0 + nn * th * 0.62, top1 + nn * th * 0.62, bot1 - nn * 0.5, bot0 - nn * 0.5], col * 0.78, op=0.5 * op, wob=0.6, seed=seed + 1, smooth=0, tex_k=0.1)
    st = []
    for _ in range(int(ln / 14)):
        s = r.uniform(0, ln)
        o = r.uniform(-th * 0.4, th * 0.4)
        a = L0 + t * s + nn * o
        b = a + t * r.uniform(10, 40)
        st.append((a[0], a[1], b[0], b[1] + r.normal(0, 0.5), r.uniform(0.8, 1.4), r.uniform(0.25, 0.55) * op))
    flicks(L, st, color=NW['plank_dk'])
    brush(L, [top0, top0 + t * ln * 0.5, top1], w0=2.2, color=INK, op=0.65 * op, seed=seed + 2, wob=0.6, taper=0.1, dry=0.3)
    brush(L, [bot0, bot0 + t * ln * 0.5, bot1], w0=1.8, color=INK, op=0.55 * op, seed=seed + 3, wob=0.6, taper=0.1, dry=0.3)
    if not jag0:
        brush(L, [top0, bot0], w0=1.6, color=INK, op=0.5 * op, seed=seed + 4, taper=0.3, smooth=False)
    if not jag1:
        brush(L, [top1, bot1], w0=1.6, color=INK, op=0.5 * op, seed=seed + 5, taper=0.3, smooth=False)
    return poly


def shoot(L, x, y, h, seed=0, op=1.0):
    """竹笋：尖尖的褐色小笋，一圈圈笋箨，尖头略带灰绿。"""
    r = np.random.default_rng(seed)
    w = h * 0.34
    lean = r.normal(0, h * 0.06)
    pts = [(x - w / 2, y), (x - w * 0.42 + lean * 0.3, y - h * 0.4), (x - w * 0.2 + lean * 0.7, y - h * 0.8), (x + lean, y - h), (x + w * 0.2 + lean * 0.7, y - h * 0.78), (x + w * 0.42 + lean * 0.3, y - h * 0.38), (x + w / 2, y)]
    wash(L, pts, NW['shoot'], op=op, wob=0.8, seed=seed, smooth=2, tex_k=0.22, rim=0.25, rim_w=2)
    wash(L, [(x + w * 0.05, y), (x + w * 0.1 + lean * 0.3, y - h * 0.4), (x + lean * 0.8, y - h * 0.95), (x + w * 0.2 + lean * 0.7, y - h * 0.78), (x + w * 0.42 + lean * 0.3, y - h * 0.38), (x + w / 2, y)], NW['shoot_dk'], op=0.55 * op, wob=0.8, seed=seed + 1, smooth=2, tex_k=0.15)
    wash(L, [(x - w * 0.1 + lean, y - h * 0.7), (x + lean, y - h), (x + w * 0.12 + lean, y - h * 0.72)], NW['bamboo'], op=0.55 * op, wob=0.5, seed=seed + 2, smooth=1)
    for k in range(1, 4):
        yy = y - h * 0.22 * k
        brush(L, [(x - w * (0.48 - 0.1 * k) + lean * 0.2 * k, yy + 2), (x + lean * 0.25 * k, yy - 3), (x + w * (0.48 - 0.1 * k) + lean * 0.2 * k, yy + 2)], w0=1.8, color=INK, op=0.55 * op, seed=int(r.integers(1e6)), taper=0.3, wob=0.5)
    brush(L, pts[:4], w0=1.8, color=INK, op=0.7 * op, seed=seed + 3, wob=0.6, taper=0.2, dry=0.3)
    brush(L, pts[3:][::-1][:4][::-1] if False else [pts[3], pts[4], pts[5], pts[6]], w0=1.6, color=INK, op=0.5 * op, seed=seed + 4, wob=0.6, taper=0.2, dry=0.3)


def saw(L, x, y, ln=150, seed=0, ang=-0.25, op=1.0):
    """锯：木柄 + 一条带齿的灰刃，靠在东西上。(x,y) 是柄端。"""
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda s, o=0: (x + ca * s - sa * o, y + sa * s + ca * o)
    brush(L, [P(0, 0), P(34, 0)], w0=10, color=N['wood'], op=0.95 * op, seed=seed, taper=0.1, wob=0.5)
    brush(L, [P(34, -1), P(ln, 0)], w0=12, w1=18, color=hexc('#a7adb0'), op=0.95 * op, seed=seed + 1, taper=0.04, wob=0.5)
    brush(L, [P(34, -6), P(ln, -8)], w0=1.8, color=INK, op=0.7 * op, seed=seed + 2, taper=0.1, wob=0.4, smooth=False)
    st = []
    for s in np.arange(38, ln - 4, 7):
        a, b = P(s, 8), P(s + 3.5, 14)
        st.append((a[0], a[1], b[0], b[1], 2.0, 0.85 * op))
    flicks(L, st, color=INK * 0.9)


def axe(L, x, y, ln=120, seed=0, ang=-0.9, op=1.0):
    """斧：木柄 + 楔形的灰斧头。(x,y) 是柄底端。"""
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda s, o=0: (x + ca * s - sa * o, y + sa * s + ca * o)
    brush(L, [P(0, 0), P(ln * 0.5, 0), P(ln, 0)], w0=8, w1=6, color=N['wood'], op=0.95 * op, seed=seed, wob=0.6, taper=0.08)
    wash(L, [P(ln - 6, -6), P(ln + 24, -22), P(ln + 30, 22), P(ln - 6, 8)], hexc('#9aa0a3'), op=0.97 * op, wob=0.6, seed=seed + 1, smooth=0, tex_k=0.15, rim=0.3)
    brush(L, [P(ln + 24, -22), P(ln + 30, 22)], w0=2.4, color=hexc('#e8e8e4'), op=0.8 * op, seed=seed + 2, taper=0.2, smooth=False)
    brush(L, [P(ln - 6, -6), P(ln + 24, -22), P(ln + 30, 22), P(ln - 6, 8), P(ln - 6, -6)], w0=1.8, color=INK, op=0.7 * op, seed=seed + 3, taper=0.1, smooth=False)


def rope_coil(L, cx, cy, rx, ry, turns=4, seed=0, w=9, op=1.0):
    """一圈圈盘好的粗绳（压扁的同心椭圆，叠起来）。"""
    r = np.random.default_rng(seed)
    for k in range(turns):
        f = 1 - k * 0.2
        yo = -k * w * 0.75
        pts = [(cx + math.cos(a) * rx * f, cy + yo + math.sin(a) * ry * f) for a in np.linspace(0, 2 * math.pi * 0.995, 30)]
        brush(L, [(a + 0.8, b + w * 0.35) for a, b in pts], w0=w * 1.0, color=NW['rope_dk'], op=0.55 * op, seed=int(r.integers(1e6)), wob=0.5, taper=0.02)
        brush(L, pts, w0=w, color=NW['rope'], op=0.97 * op, seed=int(r.integers(1e6)), wob=0.6, taper=0.02)
        st = []
        pp = _poly_path(pts, w * 0.8)
        for i in range(len(pp) - 1):
            c, d_ = pp[i], pp[i + 1]
            tt = (d_ - c) / (np.hypot(*(d_ - c)) + 1e-6)
            nn = np.array([-tt[1], tt[0]], F)
            st.append((c[0] - nn[0] * w * 0.48, c[1] - nn[1] * w * 0.48, c[0] + nn[0] * w * 0.48 + tt[0] * 3, c[1] + nn[1] * w * 0.48 + tt[1] * 3, 1.2, 0.5 * op))
        flicks(L, st, color=NW['rope_dk'])
    brush(L, [(cx + rx * 0.9, cy - turns * w * 0.6), (cx + rx * 1.3, cy + 6), (cx + rx * 1.6, cy + 14)], w0=w * 0.9, w1=w * 0.6, color=NW['rope'], op=0.95 * op, seed=seed + 50, wob=1.0, taper=0.1)


# ───────────────────────── 海底 ─────────────────────────
def seaweed(L, x, y, h, seed=0, n=5, col=None, dk=None, sway=0.35, op=1.0, width=1.0, dry=0.0):
    """海草：几条长长的、S 形摇曳的叶带（一边略暗），根部聚在 (x,y)。sway 控制弯曲的幅度。"""
    col = NW['uw'] * 0.8 if col is None else np.asarray(col, F)
    dk = NW['uw_deep'] if dk is None else np.asarray(dk, F)
    r = np.random.default_rng(seed)
    for i in range(n):
        bx = x + r.normal(0, h * 0.05) + (i - (n - 1) / 2) * h * 0.035
        hh = h * r.uniform(0.6, 1.1)
        ph = r.uniform(0, 6.28)
        k = int(10)
        pts = []
        for j in range(k + 1):
            t = j / k
            pts.append((bx + math.sin(t * 3.4 + ph) * hh * sway * t ** 0.9 * 0.5 + (i - (n - 1) / 2) * hh * 0.05 * t, y - hh * t))
        w0 = (h * 0.035 + 3) * r.uniform(0.7, 1.2) * width
        brush(L, pts, w0=w0, w1=w0 * 0.15, color=mix(col, dk, r.uniform(0, 0.5)), op=r.uniform(0.7, 0.95) * op, seed=int(r.integers(1e6)), wob=0.8, taper=0.12, dry=dry)
        brush(L, [(px + w0 * 0.22, py) for px, py in pts[: k * 3 // 4]], w0=w0 * 0.3, w1=0.8, color=dk, op=0.55 * op, seed=int(r.integers(1e6)), wob=0.8, taper=0.2)
        brush(L, [(px - w0 * 0.25, py) for px, py in pts[: k * 3 // 4]], w0=w0 * 0.2, w1=0.8, color=NW['uw_hi'], op=0.4 * op, seed=int(r.integers(1e6)), wob=0.8, taper=0.2, dry=0.3)


def coral_antler(L, x, y, h, seed=0, col=None, dk=None, depth=4, op=1.0, w=None, spread=0.6, tips=True):
    """鹿角珊瑚：粗而圆的分叉枝，枝端圆钝，一边暗一边亮，枝上细小的点孔。"""
    col = NW['pink'] if col is None else np.asarray(col, F)
    dk = NW['pink_dk'] if dk is None else np.asarray(dk, F)
    r = np.random.default_rng(seed)
    w = h * 0.075 if w is None else w

    def br(px, py, a, ln, wd, d):
        pts = [(px, py)]
        cx, cy = px, py
        aa = a
        for k in range(4):
            aa += r.normal(0, 0.12)
            cx += math.cos(aa) * ln / 4
            cy += math.sin(aa) * ln / 4
            pts.append((cx, cy))
        w1 = max(wd * 0.62, 2.6)
        brush(L, pts, w0=wd, w1=w1, color=dk, op=0.95 * op, seed=int(r.integers(1e6)), wob=0.8, taper=0.02, ss=2)
        brush(L, [(a_ - wd * 0.14, b_) for a_, b_ in pts], w0=wd * 0.72, w1=w1 * 0.7, color=col, op=0.97 * op, seed=int(r.integers(1e6)), wob=0.8, taper=0.04)
        brush(L, [(a_ - wd * 0.22, b_ - 1) for a_, b_ in pts[1:]], w0=wd * 0.22, w1=w1 * 0.2, color=NW['pearl'], op=0.55 * op, seed=int(r.integers(1e6)), wob=0.6, taper=0.2, dry=0.2)
        if tips and d >= depth:
            dots(L, [(cx, cy, w1 * 0.55)], col, op=0.95 * op)
            return
        n = 2 if r.random() < 0.8 else 3
        for s in range(n):
            da = (s - (n - 1) / 2) * spread * r.uniform(0.7, 1.2)
            br(cx, cy, aa + da, ln * r.uniform(0.66, 0.82), wd * 0.7, d + 1)

    for s in (-1, 0, 1):
        if s == 0 or r.random() < 0.75:
            br(x + s * w * 0.8, y, -math.pi / 2 + s * 0.5 + r.normal(0, 0.1), h * 0.34, w * (1.0 if s == 0 else 0.8), 1)
    st = []
    for _ in range(int(h * 0.5)):
        px, py = x + r.normal(0, h * 0.2), y - r.uniform(0.1, 0.9) * h
        st.append((px, py, px + 1.5, py + 1, r.uniform(1.4, 2.4), r.uniform(0.15, 0.4) * op))
    flicks(L, st, color=NW['pink_dk'] * 0.7)


def coral_fan(L, x, y, h, seed=0, col=None, op=1.0, w=None):
    """扇形珊瑚（海扇）：一根短茎 + 一面网状的扇，放射状的细枝加横向的细连线。"""
    col = NW['slate'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    w = h * 0.9 if w is None else w
    stem = (x + r.normal(0, 3), y - h * 0.18)
    brush(L, [(x, y), (x + r.normal(0, 2), y - h * 0.1), stem], w0=h * 0.05, w1=h * 0.03, color=col * 0.7, op=0.95 * op, seed=seed, wob=0.8, taper=0.1)
    n = 15
    tips = []
    for i in range(n):
        a = -math.pi / 2 + (i - (n - 1) / 2) / (n - 1) * 2.3
        ln = (h * 0.82) * (1 - 0.25 * abs(a + math.pi / 2) / 1.15) * r.uniform(0.9, 1.05)
        mid = (stem[0] + math.cos(a) * ln * 0.5 + r.normal(0, 2), stem[1] + math.sin(a) * ln * 0.5)
        end = (stem[0] + math.cos(a) * ln, stem[1] + math.sin(a) * ln)
        brush(L, [stem, mid, end], w0=h * 0.022, w1=1.0, color=mix(col, NW['pearl'], r.uniform(0, 0.3)), op=0.92 * op, seed=int(r.integers(1e6)), wob=1.0, taper=0.15)
        tips.append([(stem[0] + math.cos(a) * ln * f, stem[1] + math.sin(a) * ln * f) for f in (0.35, 0.55, 0.75, 0.95)])
    for f in range(4):
        pts = [t[f] for t in tips]
        brush(L, pts, w0=1.3, color=col * 0.85, op=0.6 * op, seed=int(r.integers(1e6)), wob=1.0, taper=0.1, dry=0.2)
    wash(L, [t[2] for t in tips] + [stem], col, op=0.2 * op, wob=1.5, seed=seed + 3, smooth=2, tex_k=0.12)


def coral_mound(L, x, y, w, h, seed=0, col=None, op=1.0):
    """脑纹珊瑚（圆丘）：一个半球，表面弯弯曲曲的沟纹。"""
    col = NW['ochre'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    pts = [(x + math.cos(a) * w / 2, y - math.sin(a) * h) for a in np.linspace(math.pi, 0, 18)] + [(x + w * 0.5, y), (x - w * 0.5, y)]
    wash(L, pts, col, op=op, wob=1.0, seed=seed, smooth=2, tex_k=0.2, rim=0.22)
    wash(L, [(x + math.cos(a) * w / 2, y - math.sin(a) * h) for a in np.linspace(math.pi * 0.35, 0, 8)] + [(x + w * 0.5, y), (x + w * 0.1, y)], col * 0.7, op=0.5 * op, wob=1.0, seed=seed + 1, smooth=2, tex_k=0.1)
    for k in range(int(w / 9)):
        a = r.uniform(0.15, math.pi - 0.15)
        rr = r.uniform(0.2, 0.95)
        px, py = x + math.cos(a) * w / 2 * rr, y - math.sin(a) * h * rr
        ln = r.uniform(10, 24)
        brush(L, [(px, py), (px + ln * 0.5, py - 3 + r.normal(0, 3)), (px + ln, py + r.normal(0, 3))], w0=1.8, color=col * 0.55, op=r.uniform(0.35, 0.7) * op, seed=int(r.integers(1e6)), wob=1.2, taper=0.3)
    brush(L, pts[:18], w0=2.0, color=INK, op=0.5 * op, seed=seed + 2, wob=0.8, taper=0.15, dry=0.35)


def scallop(L, x, y, r_, seed=0, col=None, op=1.0, tilt=0.0, ribs=9):
    """一枚扇贝：扇形的壳、放射的肋、底部一个小耳。(x,y) 是铰合处，开口朝上（tilt 弧度旋转）。"""
    col = NW['pearl'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    pts = [(x, y)]
    for a in np.linspace(-1.05, 1.05, 18):
        rr = r_ * (1 + 0.03 * math.sin(a * 9) + r.normal(0, 0.01))
        aa = a + tilt - math.pi / 2
        pts.append((x + math.cos(aa) * rr, y + math.sin(aa) * rr))
    wash(L, pts, col, op=op, wob=0.5, seed=seed, smooth=1, tex_k=0.12, rim=0.25, rim_w=2)
    for i in range(ribs):
        a = -1.0 + 2.0 * i / (ribs - 1) + tilt - math.pi / 2
        brush(L, [(x, y), (x + math.cos(a) * r_ * 0.5, y + math.sin(a) * r_ * 0.5), (x + math.cos(a) * r_ * 0.97, y + math.sin(a) * r_ * 0.97)], w0=max(r_ * 0.045, 1.2), w1=max(r_ * 0.06, 1.4), color=col * 0.72, op=0.6 * op, seed=int(r.integers(1e6)), wob=0.4, taper=0.1)
    brush(L, pts[1:], w0=max(r_ * 0.05, 1.4), color=INK, op=0.5 * op, seed=seed + 3, wob=0.5, taper=0.1, dry=0.3)
    wash(L, [(x - r_ * 0.2, y + 1), (x + r_ * 0.2, y + 1), (x + r_ * 0.12, y + r_ * 0.14), (x - r_ * 0.12, y + r_ * 0.14)], col * 0.8, op=op, wob=0.3, seed=seed + 4, smooth=0)


def spiral_shell(L, x, y, r_, seed=0, col=None, op=1.0):
    """螺（小的海螺）：一个圆锥形的螺，几道螺纹。"""
    col = NW['pearl_dk'] if col is None else np.asarray(col, F)
    pts = [(x - r_, y), (x - r_ * 0.7, y - r_ * 0.9), (x - r_ * 0.2, y - r_ * 1.7), (x + r_ * 0.1, y - r_ * 2.2), (x + r_ * 0.5, y - r_ * 1.5), (x + r_ * 0.9, y - r_ * 0.6), (x + r_ * 1.0, y)]
    wash(L, pts, col, op=op, wob=0.5, seed=seed, smooth=2, tex_k=0.12, rim=0.25, rim_w=1.5)
    for k in range(1, 4):
        yy = y - r_ * 0.5 * k
        brush(L, [(x - r_ * (1 - 0.2 * k), yy + 2), (x + r_ * 0.1, yy - 2), (x + r_ * (0.98 - 0.15 * k), yy + 3)], w0=1.4, color=INK, op=0.5 * op, seed=seed + k, taper=0.3, wob=0.4)
    brush(L, pts, w0=1.5, color=INK, op=0.5 * op, seed=seed + 9, wob=0.4, taper=0.1, dry=0.3)


def pebbles(L, x0, x1, ys, n, seed=0, col=None, dk=None, rmin=3, rmax=11, op=0.9, ink=0.5):
    """碎石：一堆小的扁圆石（带一笔高光 / 暗边）。ys 是 (y_min, y_max)。"""
    col = N['stone'] if col is None else np.asarray(col, F)
    dk = N['stone_dk'] if dk is None else np.asarray(dk, F)
    r = np.random.default_rng(seed)
    for _ in range(n):
        x, y = r.uniform(x0, x1), r.uniform(*ys)
        rr = r.uniform(rmin, rmax)
        hh = rr * r.uniform(0.45, 0.7)
        pts = [(x + math.cos(a) * rr * r.uniform(0.85, 1.1), y - math.sin(a) * hh * r.uniform(0.85, 1.1)) for a in np.linspace(math.pi, 0, 7)] + [(x + rr, y), (x - rr, y)]
        c = mix(col, dk, r.uniform(0, 0.6))
        wash(L, pts, c, op=op, wob=0.5, seed=int(r.integers(1e6)), smooth=1, tex_k=0.15, rim=0.2, rim_w=1.5)
        brush(L, [(x - rr * 0.5, y - hh * 0.55), (x, y - hh * 0.8), (x + rr * 0.3, y - hh * 0.6)], w0=1.3, color=N['paper'], op=0.35 * op, seed=int(r.integers(1e6)), taper=0.4)
        brush(L, [(x - rr, y), (x, y + 1.2), (x + rr, y)], w0=1.5, color=INK, op=ink * op, seed=int(r.integers(1e6)), taper=0.3, wob=0.3)


def light_shafts(L, shafts, col=None, op=0.22, seed=0, y1=None):
    """水里斜射下来的光柱：shafts = [(x_top, width_top, x_bottom, width_bottom, y_top, y_bottom, strength)]。边缘虚化 + 沿长度方向的斑驳。"""
    col = NW['pearl'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    for (xt, wt, xb, wb, yt, yb, s) in shafts:
        pts = [(xt - wt / 2, yt), (xt + wt / 2, yt), (xb + wb / 2, yb), (xb - wb / 2, yb)]
        pa = np.asarray(pts, F)
        x0, x1 = int(pa[:, 0].min()) - 40, int(pa[:, 0].max()) + 40
        y0, y1_ = int(yt), int(yb)
        x0, x1 = max(x0, 0), min(x1, L.w)
        h, w = y1_ - y0, x1 - x0
        if h <= 0 or w <= 0:
            continue
        big = np.zeros((h, w), np.uint8)
        cv2.fillPoly(big, [np.round(np.asarray([(px - x0, py - y0) for px, py in pts], F)).astype(np.int32)], 255, lineType=cv2.LINE_AA)
        m = cv2.GaussianBlur(big.astype(F) / 255.0, (0, 0), max(wt * 0.12, 6))
        yy = np.linspace(0, 1, h, dtype=F)[:, None]
        env = (1 - yy) ** 1.4 * np.clip(yy * 14, 0, 1)
        nz = fbm(h, w, int(r.integers(1e6)), 120, 3, 0.5, warp=30)
        a = m * env * (0.55 + 0.7 * nz) * s * op
        L.over(y0, y1_, x0, x1, col, np.clip(a, 0, 1).astype(F))


def floaters(L, x0, y0, x1, y1, n, seed=0, col=None, op=0.6, rmax=2.2):
    """水里悬浮的细粒（海雪）：稀稀落落的小亮点，大小深浅不一。"""
    col = NW['pearl'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    pts = []
    for _ in range(n):
        pts.append((r.uniform(x0, x1), r.uniform(y0, y1), r.uniform(0.7, rmax) * (1 if r.random() < 0.85 else 1.8)))
    for (x, y, rr) in pts:
        dots(L, [(x, y, rr)], col, op=op * r.uniform(0.25, 0.9))


def bubbles(L, x, y, n, seed=0, spread=14, rise=120, col=None, op=0.8):
    """一串往上冒的气泡（细圈 + 一点高光）。"""
    col = NW['pearl'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    for i in range(n):
        t = i / max(n - 1, 1)
        bx, by = x + r.normal(0, spread) * (0.4 + t), y - t * rise * r.uniform(0.7, 1.1)
        rr = r.uniform(2.5, 7) * (0.6 + t * 0.7)
        pts = [(bx + math.cos(a) * rr, by + math.sin(a) * rr) for a in np.linspace(0, 2 * math.pi, 14)]
        brush(L, pts, w0=1.3, color=col, op=op * r.uniform(0.5, 1), seed=int(r.integers(1e6)), wob=0.2, taper=0.05, smooth=True)
        dots(L, [(bx - rr * 0.35, by - rr * 0.35, max(rr * 0.2, 0.8))], col, op=op * 0.9)


def small_fish(L, x, y, ln, seed=0, col=None, op=1.0, side=1, belly=None):
    """一条很小的鱼，侧面（病恹恹地躺着）：纺锤形身体 + 小尾 + 一点眼 + 鳍线。"""
    col = NW['uw'] * 1.0 if col is None else np.asarray(col, F)
    belly = NW['pearl_dk'] if belly is None else belly
    h = ln * 0.3
    s = side
    pts = [(x - s * ln * 0.5, y), (x - s * ln * 0.25, y - h * 0.8), (x + s * ln * 0.15, y - h), (x + s * ln * 0.5, y - h * 0.15), (x + s * ln * 0.42, y + h * 0.3), (x + s * ln * 0.1, y + h * 0.75), (x - s * ln * 0.25, y + h * 0.65)]
    tail = [(x - s * ln * 0.48, y), (x - s * ln * 0.78, y - h * 0.8), (x - s * ln * 0.72, y), (x - s * ln * 0.8, y + h * 0.7)]
    wash(L, tail, col * 0.85, op=0.8 * op, wob=0.3, seed=seed + 1, smooth=1, tex_k=0.1)
    wash(L, pts, col, op=op, wob=0.4, seed=seed, smooth=2, tex_k=0.12, rim=0.25, rim_w=1.5)
    wash(L, [pts[3], pts[4], pts[5], pts[6], (x, y + h * 0.1)], belly, op=0.7 * op, wob=0.4, seed=seed + 2, smooth=2, tex_k=0.08)
    brush(L, pts + [pts[0]], w0=1.3, color=INK, op=0.6 * op, seed=seed + 3, wob=0.3, taper=0.1, dry=0.2)
    dots(L, [(x + s * ln * 0.3, y - h * 0.25, max(ln * 0.025, 1.0))], INK, op=0.9 * op)
    brush(L, [(x + s * ln * 0.05, y - h * 0.9), (x - s * ln * 0.05, y - h * 1.5), (x - s * ln * 0.2, y - h * 0.8)], w0=1.2, color=col * 0.7, op=0.7 * op, seed=seed + 4, taper=0.2, wob=0.3)


# ───────────────────────── 贝壳瓦片 / 珠光 ─────────────────────────
def shell_scales(L, poly, size=22, cols=None, seed=0, op=1.0, line=0.5, rows_shift=0.5, jitter=0.07, shade=None, soft=0.0):
    """把多边形铺满一片片的鱼鳞状贝壳瓦（每一片是个半圆，下沿一道暗线，上沿一笔高光，颜色在珠光色里轻微跳）。"""
    cols = [NW['pearl'], NW['pink'], NW['ochre'], NW['slate_lt']] if cols is None else cols
    cols = [np.asarray(c, F) for c in cols]
    r = np.random.default_rng(seed)
    pa = np.asarray(poly, F)
    x0, x1 = int(pa[:, 0].min()) - size, int(pa[:, 0].max()) + size
    y0, y1 = int(pa[:, 1].min()) - size, int(pa[:, 1].max()) + size
    with Sub(L, poly=poly, smooth=0, wob=0.0, soft=soft) as T:
        nrow = int((y1 - y0) / (size * 0.62)) + 2
        ncol = int((x1 - x0) / size) + 3
        # 低频的色调：让相邻的瓦成片地偏粉 / 偏灰 / 偏土黄
        low = fbm(y1 - y0 + 4, x1 - x0 + 4, seed + 5, size * 5, 3, 0.5, warp=size * 2)
        for ri in range(nrow):
            yy = y0 + ri * size * 0.62
            for ci in range(ncol):
                xx = x0 + (ci + (rows_shift if ri % 2 else 0)) * size + r.normal(0, size * jitter)
                yc = yy + r.normal(0, size * jitter * 0.7)
                lv = low[min(max(int(yc - y0), 0), low.shape[0] - 1), min(max(int(xx - x0), 0), low.shape[1] - 1)]
                ci_ = min(int(lv * len(cols) * 0.999), len(cols) - 1)
                if r.random() < 0.22:
                    ci_ = int(r.integers(len(cols)))
                c = cols[ci_] * r.uniform(0.93, 1.06)
                rr = size * 0.52
                pts = [(xx + math.cos(a) * rr, yc + math.sin(a) * rr * 0.95) for a in np.linspace(0, math.pi, 9)]
                pts = [(xx - rr, yc - size * 0.4)] + pts + [(xx + rr, yc - size * 0.4)]
                wash(T, pts, c, op=op, wob=0.3, seed=int(r.integers(1e6)), smooth=0, tex_k=0.1, rim=0.0)
                if line > 0:
                    brush(T, pts[1:-1], w0=max(size * 0.07, 1.2), color=(shade if shade is not None else mix(c, NW['slate_dk'], 0.55)), op=line * op * r.uniform(0.6, 1.0), seed=int(r.integers(1e6)), wob=0.3, taper=0.2, ss=2)
                    brush(T, [(xx - rr * 0.6, yc + rr * 0.45), (xx, yc + rr * 0.72), (xx + rr * 0.55, yc + rr * 0.5)], w0=max(size * 0.05, 1.0), color=NW['pearl'], op=0.5 * op, seed=int(r.integers(1e6)), wob=0.2, taper=0.3)


def caustics(L, x0, y0, x1, y1, seed, n=150, col=None, op=0.3, size=(30, 120)):
    """水底的光斑：透明的亮色小透镜（水彩）+ 细细的亮线连成网，沿横向铺开。"""
    col = NW['pearl'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    for _ in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        w = r.uniform(*size)
        h = w * r.uniform(0.10, 0.26)
        pts = [(x - w / 2, y), (x - w * 0.22, y - h), (x + w * 0.25, y - h * 0.9), (x + w / 2, y + h * 0.1), (x + w * 0.2, y + h), (x - w * 0.25, y + h * 0.8)]
        wash(L, pts, col, op=op * r.uniform(0.25, 0.8), wob=2, seed=int(r.integers(1e6)), smooth=2, tex_k=0.1, rim=0.0)
        if r.random() < 0.7:
            brush(L, [(x - w * 0.5, y + h * 0.2), (x, y - h * 0.3), (x + w * 0.5, y + h * 0.3)], w0=r.uniform(1.0, 2.2), color=col, op=op * r.uniform(0.8, 1.6), seed=int(r.integers(1e6)), wob=1.0, taper=0.4, dry=0.3)
