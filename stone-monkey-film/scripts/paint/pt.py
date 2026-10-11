"""程序化“墨线 + 透明水彩”画法（Python / OpenCV / numpy）。

和封面的画风对齐：靛蓝的、带水渍晕开的夜空；白雪带蓝灰色的阴影和细细的墨线排线；
光秃秃的灌木枝条；岩石；海面一条条横向的笔触。所有画面都画在 float32 RGBA 画布上，
最后存成 PNG / JPG，影片里只做平移和缩放（视差）。

约定：颜色是 0~1 的 sRGB；坐标是像素，原点在左上角。
"""
import math
import numpy as np
import cv2

F = np.float32


def hexc(s):
    s = s.lstrip('#')
    return np.array([int(s[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], F)


def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


# ───────────────────────── 噪声 ─────────────────────────
def fbm(h, w, seed, scale=200, octaves=5, persist=0.5, warp=0.0):
    """分形噪声 0~1。scale 是最粗那一层的“格子大小”（像素）。warp>0 时做域扭曲，更像水彩晕开。"""
    r = np.random.default_rng(seed)
    out = np.zeros((h, w), F)
    amp, tot = 1.0, 0.0
    cell = float(scale)
    for _ in range(octaves):
        gh, gw = max(int(h / cell) + 3, 3), max(int(w / cell) + 3, 3)
        g = r.random((gh, gw)).astype(F)
        up = cv2.resize(g, (int(gw * cell), int(gh * cell)), interpolation=cv2.INTER_CUBIC)
        out += amp * up[:h, :w]
        tot += amp
        amp *= persist
        cell = max(cell / 2.0, 2.0)
    out /= tot
    if warp > 0:
        n1 = fbm(h, w, seed + 101, scale * 0.8, 3, 0.5)
        n2 = fbm(h, w, seed + 202, scale * 0.8, 3, 0.5)
        yy, xx = np.mgrid[0:h, 0:w].astype(F)
        out = cv2.remap(out, xx + (n1 - 0.5) * warp, yy + (n2 - 0.5) * warp, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    lo, hi = np.percentile(out, 1), np.percentile(out, 99)
    return np.clip((out - lo) / (hi - lo + 1e-6), 0, 1)


def grain(h, w, seed, sigma=0.6):
    r = np.random.default_rng(seed)
    g = r.standard_normal((h, w)).astype(F)
    return cv2.GaussianBlur(g, (0, 0), sigma) * (0.5 / max(sigma, 0.3))


# ───────────────────────── 画布 ─────────────────────────
class Canvas:
    """straight-alpha RGBA 画布。"""

    def __init__(self, w, h, bg=None, alpha=0.0):
        self.w, self.h = w, h
        self.rgb = np.zeros((h, w, 3), F)
        self.a = np.full((h, w), alpha, F)
        if bg is not None:
            self.rgb[:] = bg
            self.a[:] = 1.0

    def over(self, y0, y1, x0, x1, rgb, a):
        """把 (rgb, a) 盖到 [y0:y1, x0:x1]。rgb 可以是 (3,) 颜色或 (h,w,3)。"""
        y0c, x0c = max(y0, 0), max(x0, 0)
        y1c, x1c = min(y1, self.h), min(x1, self.w)
        if y1c <= y0c or x1c <= x0c:
            return
        a = a[y0c - y0:y1c - y0, x0c - x0:x1c - x0]
        if rgb.ndim == 3:
            rgb = rgb[y0c - y0:y1c - y0, x0c - x0:x1c - x0]
        da = self.a[y0c:y1c, x0c:x1c]
        dr = self.rgb[y0c:y1c, x0c:x1c]
        na = a + da * (1 - a)
        sa = a[..., None]
        nrgb = (rgb * sa + dr * (da * (1 - a))[..., None]) / np.maximum(na, 1e-5)[..., None]
        self.rgb[y0c:y1c, x0c:x1c] = nrgb
        self.a[y0c:y1c, x0c:x1c] = na

    def flat(self, bg=(1, 1, 1)):
        bg = np.asarray(bg, F)
        return self.rgb * self.a[..., None] + bg * (1 - self.a[..., None])

    def save(self, path, jpg=False, q=93):
        if jpg:
            img = (np.clip(self.flat(), 0, 1) * 255 + 0.5).astype(np.uint8)
            cv2.imwrite(str(path), cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, q])
        else:
            img = (np.clip(np.dstack([self.rgb, self.a]), 0, 1) * 255 + 0.5).astype(np.uint8)
            cv2.imwrite(str(path), cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA))


# ───────────────────────── 形状 ─────────────────────────
def chaikin(pts, n=2, closed=True):
    p = np.asarray(pts, F)
    for _ in range(n):
        if closed:
            q = np.roll(p, -1, axis=0)
            new = np.empty((len(p) * 2, 2), F)
            new[0::2] = 0.75 * p + 0.25 * q
            new[1::2] = 0.25 * p + 0.75 * q
            p = new
        else:
            new = [p[0]]
            for i in range(len(p) - 1):
                new += [0.75 * p[i] + 0.25 * p[i + 1], 0.25 * p[i] + 0.75 * p[i + 1]]
            new.append(p[-1])
            p = np.array(new, F)
    return p


def catmull(pts, per=12, closed=False):
    p = np.asarray(pts, F)
    if len(p) < 3:
        return p
    if closed:
        p = np.vstack([p[-1], p, p[0], p[1]])
    else:
        p = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for t in np.linspace(0, 1, per, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(p[-2])
    return np.array(out, F)


def wobble_pts(pts, amp, seed, freq=0.05):
    """沿折线加缓慢的抖动（水彩边缘不规则）。"""
    p = np.asarray(pts, F)
    if amp <= 0 or len(p) < 2:
        return p
    r = np.random.default_rng(seed)
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    k = max(int(d[-1] * freq) + 3, 4)
    nx = cv2.resize(r.random((1, k)).astype(F) * 2 - 1, (len(p), 1), interpolation=cv2.INTER_CUBIC)[0]
    ny = cv2.resize(r.random((1, k)).astype(F) * 2 - 1, (len(p), 1), interpolation=cv2.INTER_CUBIC)[0]
    return p + np.stack([nx, ny], 1) * amp


def poly_mask(pts, W, H, ss=3, pad=4):
    """多边形 → (y0, y1, x0, x1, 抗锯齿蒙版)。只分配包围盒大小的数组。"""
    p = np.asarray(pts, F)
    x0, y0 = int(math.floor(p[:, 0].min())) - pad, int(math.floor(p[:, 1].min())) - pad
    x1, y1 = int(math.ceil(p[:, 0].max())) + pad, int(math.ceil(p[:, 1].max())) + pad
    x0c, y0c, x1c, y1c = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
    if x1c <= x0c or y1c <= y0c:
        return None
    w, h = x1c - x0c, y1c - y0c
    big = np.zeros((h * ss, w * ss), np.uint8)
    q = np.round((p - [x0c, y0c]) * ss).astype(np.int32)
    cv2.fillPoly(big, [q], 255, lineType=cv2.LINE_AA)
    m = cv2.resize(big, (w, h), interpolation=cv2.INTER_AREA).astype(F) / 255.0
    return y0c, y1c, x0c, x1c, m


_TEX_CACHE = {}


def tex_field(W, H, seed=7):
    """画布大小的颗粒 + 水渍底纹（缓存）：水彩颜料的颗粒感。"""
    key = (W, H, seed)
    if key not in _TEX_CACHE:
        g = grain(H, W, seed, 0.7)
        mid = fbm(H, W, seed + 3, 70, 3)
        _TEX_CACHE[key] = (0.5 + 0.5 * np.clip(g, -1.5, 1.5) / 1.5 * 0.55 + (mid - 0.5) * 0.5).astype(F)
    return _TEX_CACHE[key]


def wash(L, pts, color, op=1.0, wob=2.0, seed=0, smooth=2, tex_k=0.10, rim=0.16, rim_w=3.0, closed=True, tex=None, mask_mul=None):
    """透明水彩色块：边缘不规则 + 边缘积色（比中间深）+ 颗粒。"""
    p = np.asarray(pts, F)
    if smooth:
        p = chaikin(p, smooth, closed)
    p = wobble_pts(p, wob, seed)
    r = poly_mask(p, L.w, L.h)
    if r is None:
        return
    y0, y1, x0, x1, m = r
    if mask_mul is not None:
        m = m * mask_mul[y0:y1, x0:x1]
    col = np.asarray(color, F)
    if tex is None:
        tex = tex_field(L.w, L.h)
    t = tex[y0:y1, x0:x1]
    edge = np.clip(m - cv2.GaussianBlur(m, (0, 0), rim_w), 0, 1) * 2.2
    k = 1.0 + tex_k * (t - 0.5) * 2.0 - rim * np.clip(edge, 0, 1)
    rgb = np.clip(col * k[..., None], 0, 1)
    L.over(y0, y1, x0, x1, rgb, m * op)


def ink(L, pts, w0=2.0, w1=None, color=(0.1, 0.12, 0.22), op=0.9, seed=0, wob=0.8, taper=0.35, ss=3, smooth=True):
    """一笔墨线：宽度从 w0 渐变到 w1，两头收尖（taper 是收尖的比例），带缓慢的手抖。"""
    if smooth:
        p = catmull(np.asarray(pts, F), 10)
    else:   # 折线：保留尖角，每段按 ≤8px 加密（房子、窗、桌子的轮廓）
        q = np.asarray(pts, F)
        segs = [q[0:1]]
        for a, b in zip(q[:-1], q[1:]):
            n = max(int(np.hypot(*(b - a)) / 8), 1)
            segs.append(a + (b - a) * (np.arange(1, n + 1)[:, None] / n))
        p = np.vstack(segs)
    if len(p) < 2:
        return
    p = wobble_pts(p, wob, seed, 0.04)
    w1 = w0 if w1 is None else w1
    n = len(p)
    t = np.linspace(0, 1, n)
    prof = np.minimum(1, np.minimum(t, 1 - t) / max(taper, 1e-3))
    prof = 0.25 + 0.75 * np.sin(prof * math.pi / 2)
    wid = (w0 + (w1 - w0) * t) * prof
    r = np.random.default_rng(seed + 5)
    wid *= 1 + 0.18 * (cv2.resize(r.random((1, max(n // 6, 3))).astype(F), (n, 1), interpolation=cv2.INTER_CUBIC)[0] - 0.5) * 2
    x0, y0 = int(p[:, 0].min() - w0 * 2 - 3), int(p[:, 1].min() - w0 * 2 - 3)
    x1, y1 = int(p[:, 0].max() + w0 * 2 + 4), int(p[:, 1].max() + w0 * 2 + 4)
    x0c, y0c, x1c, y1c = max(x0, 0), max(y0, 0), min(x1, L.w), min(y1, L.h)
    if x1c <= x0c or y1c <= y0c:
        return
    w, h = x1c - x0c, y1c - y0c
    big = np.zeros((h * ss, w * ss), np.uint8)
    q = (p - [x0c, y0c]) * ss
    for i in range(n - 1):
        rad = max(wid[i] * ss / 2, 0.6)
        cv2.line(big, tuple(np.round(q[i]).astype(int)), tuple(np.round(q[i + 1]).astype(int)), 255, max(int(round(rad * 2)), 1), cv2.LINE_AA)
    m = cv2.resize(big, (w, h), interpolation=cv2.INTER_AREA).astype(F) / 255.0
    L.over(y0c, y1c, x0c, x1c, np.asarray(color, F), m * op)


def dots(L, pts_r, color, op=1.0, soft=0.7):
    """一批圆点（雪花、星星、灯光的亮点）：pts_r = [(x, y, r), ...]。"""
    for (x, y, r) in pts_r:
        rr = int(math.ceil(r * 2 + 3))
        x0, y0 = int(x) - rr, int(y) - rr
        yy, xx = np.mgrid[0:2 * rr + 1, 0:2 * rr + 1].astype(F)
        d = np.hypot(xx - (x - x0), yy - (y - y0))
        m = np.clip((r + soft - d) / (soft * 2), 0, 1)
        L.over(y0, y0 + 2 * rr + 1, x0, x0 + 2 * rr + 1, np.asarray(color, F), m * op)


def glow(L, x, y, r, color, op=0.6, power=2.0):
    """柔和的光晕（径向渐变），用在灯、窗、船灯上。"""
    rr = int(r)
    x0, y0 = int(x) - rr, int(y) - rr
    yy, xx = np.mgrid[0:2 * rr + 1, 0:2 * rr + 1].astype(F)
    d = np.hypot(xx - (x - x0), yy - (y - y0)) / r
    m = np.clip(1 - d, 0, 1) ** power
    L.over(y0, y0 + 2 * rr + 1, x0, x0 + 2 * rr + 1, np.asarray(color, F), m * op)


def hatch(L, pts, angle_deg, gap, length, color, op=0.5, w=1.2, seed=0, jitter=0.5):
    """在多边形里排一组墨线短线（雪地阴影、岩石的排线）。"""
    p = np.asarray(pts, F)
    r = poly_mask(p, L.w, L.h, ss=1)
    if r is None:
        return
    y0, y1, x0, x1, m = r
    rng = np.random.default_rng(seed)
    ang = math.radians(angle_deg)
    dx, dy = math.cos(ang), math.sin(ang)
    px, py = -dy, dx
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + length
    s = -R
    while s < R:
        t = -R
        while t < R:
            jx, jy = rng.normal(0, gap * jitter), rng.normal(0, gap * jitter)
            sx, sy = cx + px * s + dx * t + jx, cy + py * s + dy * t + jy
            ln = length * (0.5 + rng.random())
            ex, ey = sx + dx * ln, sy + dy * ln
            ix, iy = int(sx) - x0, int(sy) - y0
            if 0 <= ix < x1 - x0 and 0 <= iy < y1 - y0 and m[iy, ix] > 0.6:
                ink(L, [(sx, sy), ((sx + ex) / 2 + rng.normal(0, 0.6), (sy + ey) / 2 + rng.normal(0, 0.6)), (ex, ey)], w0=w, color=color, op=op * (0.5 + rng.random() * 0.7), seed=int(rng.integers(1e6)), wob=0.3, taper=0.5)
            t += length * (0.9 + rng.random() * 0.8)
        s += gap


def blur_edges(L, sigma):
    """整张画布轻微虚化（远景用）。"""
    L.rgb = cv2.GaussianBlur(L.rgb, (0, 0), sigma)
    L.a = cv2.GaussianBlur(L.a, (0, 0), sigma)
