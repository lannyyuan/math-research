"""人物 / 动物 / 小道具的“水墨水彩”小工具（在 pt.py + cn.py 之上，Agent P）。

思路：每个人拆成 衣服块（wash 平涂 + 一层偏暗的罩染 + 污渍 + 皴擦 + 补丁 + 断续墨线）、手、脸（几笔）、头发/帽子。
所有 *_clip 的细节（污渍、皴擦、补丁）都画在一张临时画布上，再按衣服的形状裁剪后盖回去，所以不会画出衣服外面。
坐标：像素，原点左上角，y 向下。侧面一律脸朝右。
"""
import math, json, pathlib, sys
import numpy as np
import cv2

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from cn import *  # noqa  (pt.* / N / INK / brush / flicks / mix ...)

ROOT = pathlib.Path(__file__).resolve().parents[2]
SPR = ROOT / 'public/sprites'
SCR = pathlib.Path('/tmp/claude-0/-home-user-math-research/747091a3-a05e-575b-b1ac-cb27e1adeb12/scratchpad/prev')
SCR.mkdir(parents=True, exist_ok=True)

# ───────────────────────── 色板（已降饱和；只有 RED 是允许的红）─────────────────────────
K = {k: hexc(v) for k, v in dict(
    skin='#e2b48f', skin_sh='#bd8b6a', skin_dk='#9a6a4e', cheek='#e0957f', skin_old='#d6a987',
    hair='#2c2724', hair_hi='#55535a', grey='#d3cfc7', grey_sh='#9a9ea6', white='#e8e3d6', white_sh='#b3bcc8',
    blue='#5d6a88', blue_dk='#3f4966', blue_lt='#8794ad', stone='#738f9f', stone_dk='#51697a', stone_lt='#a3b8c2',
    gb='#6f6357', gb_dk='#4a4139', gb_lt='#9d8f7c', fur='#85775f', fur_lt='#b5a68c', dark='#3a3836', dark2='#2d2c2e',
    linen='#b9a98a', linen_lt='#d3c6a8', rope='#a88e65', rope_dk='#7d6746', wood='#8a7558', wood_dk='#5a4a38', wood_lt='#b9a47e',
    red='#B8382E', gold='#cfc29a', gold_dk='#a09672', gold_lt='#e2d9b8', jade='#bcd2cc', jade_dk='#8fb0a8',
    ink='#2a2622', inkb='#3a302a', snow='#f0eee8', sole='#d9d2c0', bamboo='#8d9878', bamboo_dk='#66745a',
    horse='#7c6a58', horse_dk='#4f4237', horse_lt='#a8967c',
).items()}
INKB = K['inkb']


# ───────────────────────── 几何 ─────────────────────────
def proc(pts, wob=1.4, seed=0, smooth=2, closed=True):
    p = np.asarray(pts, F)
    if smooth:
        p = chaikin(p, smooth, closed)
    if wob > 0:
        p = wobble_pts(p, wob, seed)
    return p


def roughen(p, amp=1.0, seed=0, step=3.0, closed=True):
    """沿法线方向加一点高频的抖动：像剪刀剪出来/撕出来的不齐的布边。"""
    p = np.asarray(p, F)
    if closed:
        p = np.vstack([p, p[:1]])
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    n = max(int(d[-1] / step), 4)
    ts = np.linspace(0, d[-1], n)
    q = np.stack([np.interp(ts, d, p[:, 0]), np.interp(ts, d, p[:, 1])], 1)
    t = np.gradient(q, axis=0)
    t /= np.maximum(np.hypot(t[:, 0], t[:, 1]), 1e-6)[:, None]
    nrm = np.stack([-t[:, 1], t[:, 0]], 1)
    r = np.random.default_rng(seed + 123)
    k = r.normal(0, 1, n)
    k = np.convolve(k, [0.25, 0.5, 0.25], 'same') * amp
    q = q + nrm * k[:, None]
    return q[:-1] if closed else q


def mask_of(L, p):
    m = np.zeros((L.h, L.w), F)
    r = poly_mask(p, L.w, L.h)
    if r is not None:
        y0, y1, x0, x1, mm = r
        m[y0:y1, x0:x1] = mm
    return m


def bbox_of(L, p, pad=2):
    p = np.asarray(p, F)
    x0 = int(max(p[:, 0].min() - pad, 0)); x1 = int(min(p[:, 0].max() + pad + 1, L.w))
    y0 = int(max(p[:, 1].min() - pad, 0)); y1 = int(min(p[:, 1].max() + pad + 1, L.h))
    return y0, y1, x0, x1


def tube(path, w0, w1=None, wmid=None, cap=0.7, seed=0, per=8, cap0=None, cap1=None):
    """沿路径的一条“管子”（袖子、腿、手臂）：宽度 w0→w1（可在中间鼓一下 wmid）。返回闭合多边形点。"""
    pth = np.asarray(path, F)
    if len(pth) >= 3:
        pth = catmull(pth, per)
    else:
        n = per * 2
        pth = pth[0] + (pth[-1] - pth[0]) * np.linspace(0, 1, n)[:, None]
    w1 = w0 if w1 is None else w1
    n = len(pth)
    t = np.linspace(0, 1, n)
    w = w0 + (w1 - w0) * t
    if wmid is not None:
        w = w + (wmid - (w0 + w1) / 2) * np.sin(t * math.pi)
    d = np.gradient(pth, axis=0)
    d /= np.maximum(np.hypot(d[:, 0], d[:, 1]), 1e-6)[:, None]
    nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    left = pth + nrm * (w / 2)[:, None]
    right = pth - nrm * (w / 2)[:, None]
    c0 = pth[0] - d[0] * w[0] * (cap if cap0 is None else cap0) / 2
    c1 = pth[-1] + d[-1] * w[-1] * (cap if cap1 is None else cap1) / 2
    return np.vstack([[c0], left, [c1], right[::-1]])


def lathe(cx, rows):
    """对称/不对称的“车削”轮廓：rows = [(y, 左半宽, 右半宽), ...]（从上到下），返回闭合多边形。"""
    L_ = [(cx - l, y) for (y, l, r) in rows]
    R_ = [(cx + r, y) for (y, l, r) in rows]
    return R_ + L_[::-1]


def ellipse_pts(cx, cy, rx, ry, n=16, rot=0.0, jit=0.0, seed=0):
    r = np.random.default_rng(seed)
    out = []
    for a in np.linspace(0, 2 * math.pi, n, endpoint=False):
        j = 1 + (r.uniform(-jit, jit) if jit else 0)
        x, y = math.cos(a) * rx * j, math.sin(a) * ry * j
        out.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return out


def rot_rect(cx, cy, w, h, ang=0.0):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]


def rng_of(seed):
    return np.random.default_rng(seed)


# ───────────────────────── 裁剪层 ─────────────────────────
class Clip:
    """with Clip(L, mask) as T: 在 T 上随便画（pt/cn 的函数都行），退出时按 mask 盖回 L。"""

    def __init__(self, L, mask, bb=None):
        self.L, self.mask = L, mask
        self.bb = bb

    def __enter__(self):
        self.T = Canvas(self.L.w, self.L.h)
        return self.T

    def __exit__(self, *a):
        L = self.L
        if self.bb is None:
            ys, xs = np.nonzero(self.mask > 0.01)
            if len(ys) == 0:
                return
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        else:
            y0, y1, x0, x1 = self.bb
        L.over(y0, y1, x0, x1, self.T.rgb[y0:y1, x0:x1], (self.T.a * self.mask)[y0:y1, x0:x1])


def blotch(T, bb, col, seed, scale=22, lo=0.6, hi=0.8, op=0.3, warp=14, octv=4):
    """一片片的水渍/污渍：噪声阈值化。bb=(y0,y1,x0,x1)。"""
    y0, y1, x0, x1 = bb
    h, w = y1 - y0, x1 - x0
    if h < 4 or w < 4:
        return
    n = fbm(h, w, seed, scale, octv, 0.55, warp=warp)
    a = smoothstep(lo, hi, n) * op
    T.over(y0, y1, x0, x1, np.asarray(col, F), a.astype(F))


def side_glaze(T, bb, col, seed, direction=1, start=0.6, amt=0.35, noise=0.3, scale=60, vertical=False):
    """偏暗的一层罩染（背光那一侧），边界不规则，像水彩罩色。direction=1 表示右侧背光。"""
    y0, y1, x0, x1 = bb
    h, w = y1 - y0, x1 - x0
    if h < 4 or w < 4:
        return
    n = fbm(h, w, seed, scale, 3, 0.5, warp=20)
    if vertical:
        u = np.linspace(0, 1, h, dtype=F)[:, None] * np.ones((1, w), F)
    else:
        u = np.linspace(0, 1, w, dtype=F)[None, :] * np.ones((h, 1), F)
    if direction < 0:
        u = 1 - u
    v = u + (n - 0.5) * noise
    a = smoothstep(start - 0.015, start + 0.03, v) * amt
    T.over(y0, y1, x0, x1, np.asarray(col, F), a.astype(F))


def ink_outline(L, p, seed=0, w=2.2, op=0.8, gaps=0.22, color=None, dry=0.15, closed=True, minseg=60, maxseg=200):
    """断续的墨线沿着多边形走：每段长度随机，段间留缺口，粗细略有变化。"""
    color = INKB if color is None else np.asarray(color, F)
    p = np.asarray(p, F)
    if closed:
        p = np.vstack([p, p[:1]])
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    tot = d[-1]
    r = np.random.default_rng(seed + 77)
    s = r.uniform(0, 40)
    while s < tot - 8:
        ln = r.uniform(minseg, maxseg)
        e = min(s + ln, tot)
        i0, i1 = np.searchsorted(d, s), np.searchsorted(d, e)
        seg = p[i0:i1 + 1]
        if len(seg) >= 3:
            seg = seg[::max(len(seg) // 14, 1)] if len(seg) > 16 else seg
            if len(seg) >= 3:
                brush(L, seg, w0=w * r.uniform(0.75, 1.3), color=color, op=op * r.uniform(0.6, 1.0), seed=int(r.integers(1e6)), wob=0.5, taper=0.3, dry=dry * r.uniform(0.4, 1.4))
        s = e + (r.uniform(6, 28) if r.random() < gaps * 2.5 else r.uniform(-4, 3))


def line(L, pts, w=2.0, col=None, op=0.85, seed=0, taper=0.3, dry=0.0, wob=0.6, smooth=True, w1=None):
    brush(L, pts, w0=w, w1=w1, color=INKB if col is None else np.asarray(col, F), op=op, seed=seed, wob=wob, taper=taper, dry=dry, smooth=smooth)


# ───────────────────────── 衣服块 ─────────────────────────
def garment(L, pts, col, seed=0, wob=1.3, smooth=2, shade=0.34, shade_dir=1, shade_start=0.62, stain=0.34, worn=0.0, flick=0.5,
            fdir=80.0, outline=True, ink_w=2.2, ink_op=0.85, dark=None, light=None, hem_dirt=0.0, tex_k=0.13, rim=0.22,
            op=1.0, gaps=0.14, closed=True, vertical_shade=False, scale=26, ink_col=None, folds=None, fold_op=0.5, streak=0.0, cast=None, rough=0.7, speck=0.5, edge_dk=0.0):
    """一块衣服：平涂 + 背光侧罩染 + 污渍 + 磨白处 + 皴擦 + 断续墨线。返回 (多边形点, 蒙版)。"""
    col = np.asarray(col, F)
    dark = mix(col, INK, 0.45) if dark is None else np.asarray(dark, F)
    light = mix(col, hexc('#f0ead8'), 0.5) if light is None else np.asarray(light, F)
    p = proc(pts, wob, seed, smooth, closed)
    if rough > 0:
        p = roughen(p, rough, seed, 3.0, closed)
    wash(L, p, col, op=op, wob=0, seed=seed, smooth=0, tex_k=tex_k, rim=rim, rim_w=2.8)
    m = mask_of(L, p) * op
    bb = bbox_of(L, p)
    r = np.random.default_rng(seed + 31)
    y0, y1, x0, x1 = bb
    with Clip(L, m, bb) as T:
        if shade > 0:
            side_glaze(T, bb, mix(col, dark, 0.8), seed + 1, shade_dir, shade_start, shade, 0.35, 70, vertical_shade)
        if stain > 0:
            blotch(T, bb, dark, seed + 2, scale, 0.60, 0.80, stain)
            blotch(T, bb, mix(dark, col, 0.4), seed + 3, scale * 2.2, 0.55, 0.8, stain * 0.6, 30)
        if worn > 0:
            blotch(T, bb, light, seed + 4, scale * 1.2, 0.66, 0.84, worn)
        if hem_dirt > 0:
            side_glaze(T, bb, dark, seed + 5, 1, 0.78, hem_dirt, 0.25, 40, True)
        if edge_dk > 0:   # 边缘积色（颜料在边上聚成深色的一圈）
            ring = np.clip(m - cv2.GaussianBlur(m, (0, 0), 3.5), 0, 1)
            nn = fbm(L.h, L.w, seed + 8, 30, 3, 0.5) if False else None
            T.over(y0, y1, x0, x1, dark, np.clip(ring[y0:y1, x0:x1] * 2.5, 0, 1) * edge_dk)
        if speck > 0:   # 细碎的污点
            area = (y1 - y0) * (x1 - x0)
            st = []
            for _ in range(int(area / 260 * speck)):
                x, y = r.uniform(x0, x1), r.uniform(y0, y1)
                st.append((x, y, x + r.normal(0, 0.8), y + r.uniform(0.6, 2.4), r.uniform(1.0, 2.2), r.uniform(0.25, 0.65)))
            flicks(T, st, color=mix(dark, INK, 0.4))
        if cast is not None:   # 上面一件衣服投下来的影子：cast = (多边形点, dx, dy)
            cp, cdx, cdy = cast
            wash(T, np.asarray(cp, F) + [cdx, cdy], dark, op=0.42, wob=0, seed=seed + 6, smooth=0, tex_k=0.1, rim=0.1)
        if folds:
            for k, fl in enumerate(folds):
                brush(T, fl, w0=r.uniform(1.4, 2.4), w1=0.8, color=dark, op=fold_op * r.uniform(0.7, 1.0), seed=seed + 40 + k, wob=0.8, taper=0.35, dry=0.2)
        if streak > 0:   # 干笔的顺纹飞白
            n = int((y1 - y0) * (x1 - x0) / 900 * streak)
            st = []
            for _ in range(n):
                x, y = r.uniform(x0, x1), r.uniform(y0, y1)
                ang = math.radians(fdir + r.normal(0, 8))
                ln = r.uniform(14, 38)
                st.append((x, y, x + math.cos(ang) * ln * 0.2, y + math.sin(ang) * ln, r.uniform(0.8, 1.4), r.uniform(0.12, 0.3)))
            flicks(T, st, color=light)
        if flick > 0:
            area = (y1 - y0) * (x1 - x0)
            n = int(area / 520 * flick)
            st = []
            for _ in range(n):
                x, y = r.uniform(x0, x1), r.uniform(y0, y1)
                ang = math.radians(fdir + r.normal(0, 14)) * (1 if r.random() < 0.5 else -1)
                ln = r.uniform(5, 18)
                st.append((x, y, x + math.cos(ang) * ln, y + abs(math.sin(ang)) * ln, r.uniform(0.9, 1.7), r.uniform(0.14, 0.4)))
            flicks(T, st, color=dark)
    if outline:
        ink_outline(L, p, seed, w=ink_w, op=ink_op, gaps=gaps, color=ink_col, closed=closed)
    return p, m


def patch(L, cx, cy, w, h, col, seed=0, ang=0.0, stitch=True, op=0.95, edge=None, frayed=0.0, clipmask=None):
    r = np.random.default_rng(seed)
    pts = rot_rect(cx, cy, w, h, ang)
    pts = [(x + r.normal(0, 1.4), y + r.normal(0, 1.4)) for x, y in pts]
    p = proc(pts, 1.0, seed, 0)
    # 补丁不裁剪（本来就小），但可以被 clipmask 限制
    col = np.asarray(col, F)
    wash(L, p, col, op=op, wob=0, seed=seed, smooth=0, tex_k=0.16, rim=0.3, rim_w=2.2, mask_mul=clipmask)
    if stitch:
        c, s = math.cos(ang), math.sin(ang)
        st = []
        corners = rot_rect(cx, cy, w - 4, h - 4, ang)
        for i in range(4):
            a_, b_ = np.array(corners[i], F), np.array(corners[(i + 1) % 4], F)
            ln = np.hypot(*(b_ - a_))
            k = max(int(ln / 6), 1)
            for j in range(k):
                q = a_ + (b_ - a_) * ((j + 0.5) / k)
                dx, dy = (b_ - a_) / max(ln, 1e-6)
                nx, ny = -dy, dx
                st.append((q[0] - nx * 1.6, q[1] - ny * 1.6, q[0] + nx * 1.6, q[1] + ny * 1.6, 1.0, 0.55))
        flicks(L, st, color=mix(col, INK, 0.65))
    if edge is not False:
        ink_outline(L, p, seed, w=1.3, op=0.45, gaps=0.5, color=mix(col, INK, 0.7), minseg=18, maxseg=60)


def shadow_on(L, target_mask, poly, dx=4, dy=3, col=None, op=0.35, blur=2.0):
    """poly 投在 target（衣服/身体）上的影子：poly 平移 (dx,dy) 后与 target 相交，一层偏暗的水彩。"""
    col = mix(K['gb_dk'], INK, 0.6) if col is None else np.asarray(col, F)
    sp = np.asarray(poly, F) + [dx, dy]
    m = mask_of(L, sp)
    if blur:
        m = cv2.GaussianBlur(m, (0, 0), blur)
    m = m * target_mask * op
    ys, xs = np.nonzero(m > 0.01)
    if len(ys) == 0:
        return
    L.over(ys.min(), ys.max() + 1, xs.min(), xs.max() + 1, col, m[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def fringe(L, pts, col, seed=0, n=12, ln=(6, 16), op=0.7, w=1.3, dirv=(0, 1)):
    """撕破的下摆毛边：沿折线 pts 垂下一些短短的纤维。"""
    r = np.random.default_rng(seed)
    p = np.asarray(pts, F)
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    st = []
    for _ in range(n):
        s = r.uniform(0, d[-1])
        i = min(np.searchsorted(d, s), len(p) - 1)
        x, y = p[i]
        l_ = r.uniform(*ln)
        st.append((x, y - 1, x + dirv[0] * l_ + r.normal(0, 1.5), y + dirv[1] * l_, w * r.uniform(0.8, 1.4), op * r.uniform(0.5, 1)))
    flicks(L, st, color=np.asarray(col, F))


def fuzz_edge(L, p, col, seed=0, n=60, ln=(4, 10), op=0.7, w=1.4, inward=2.0):
    """沿多边形边缘向外长出毛：皮毛、胡须、毛领的毛边。"""
    p = np.asarray(p, F)
    c = p.mean(0)
    pp = np.vstack([p, p[:1]])
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(pp, axis=0).T))]
    r = np.random.default_rng(seed + 5)
    st = []
    for _ in range(n):
        s_ = r.uniform(0, d[-1])
        i = min(np.searchsorted(d, s_), len(p) - 1)
        q = p[i]
        t = p[(i + 1) % len(p)] - p[i - 1]
        t /= max(np.hypot(*t), 1e-6)
        nrm = np.array([-t[1], t[0]], F)
        if np.dot(nrm, q - c) < 0:
            nrm = -nrm
        l_ = r.uniform(*ln)
        ang = r.normal(0, 0.35)
        ca, sa = math.cos(ang), math.sin(ang)
        nr2 = np.array([nrm[0] * ca - nrm[1] * sa, nrm[0] * sa + nrm[1] * ca], F)
        st.append((q[0] - nrm[0] * inward, q[1] - nrm[1] * inward, q[0] + nr2[0] * l_, q[1] + nr2[1] * l_, w * r.uniform(0.8, 1.5), op * r.uniform(0.5, 1.0)))
    flicks(L, st, color=np.asarray(col, F))


def ground_shadow(L, cx, y, w, h=10, op=0.28, seed=0, col=None):
    col = hexc('#7d7f84') if col is None else np.asarray(col, F)
    pts = ellipse_pts(cx, y, w / 2, h / 2, 18, jit=0.06, seed=seed)
    wash(L, pts, col, op=op, wob=1.5, seed=seed, smooth=1, tex_k=0.1, rim=0.0)


# ───────────────────────── 手 / 脚 ─────────────────────────
def hand(L, x, y, ang, s, skin=None, seed=0, kind='open', side=1):
    """手：x,y 是手腕；ang 是手指指向的方向（弧度，0=向右，π/2=向下）；s 是手长（像素）。kind: open / fist / point。"""
    skin = K['skin'] if skin is None else np.asarray(skin, F)
    c, sn = math.cos(ang), math.sin(ang)
    nx, ny = -sn, c

    def P(u, v):
        return (x + c * u * s + nx * v * s * side, y + sn * u * s + ny * v * s * side)
    if kind == 'fist':
        pts = [P(0, -0.28), P(0.35, -0.38), P(0.8, -0.34), P(1.0, -0.1), P(0.95, 0.2), P(0.55, 0.38), P(0.1, 0.3)]
    elif kind == 'point':
        pts = [P(0, -0.26), P(0.4, -0.34), P(0.7, -0.3), P(1.4, -0.1), P(0.75, -0.02), P(0.9, 0.3), P(0.4, 0.38), P(0.05, 0.28)]
    else:
        pts = [P(0, -0.3), P(0.3, -0.42), P(0.55, -0.4), P(1.0, -0.3), P(1.12, -0.12), P(1.02, 0.1), P(0.7, 0.34), P(0.3, 0.42), P(0.0, 0.3)]
    p = proc(pts, 0.4, seed, 2)
    wash(L, p, skin, op=1.0, wob=0, seed=seed, smooth=0, tex_k=0.08, rim=0.2, rim_w=1.8)
    ink_outline(L, p, seed, w=1.3, op=0.65, gaps=0.3, color=K['skin_dk'] * 0.55, minseg=14, maxseg=40)
    if kind == 'open':
        for k in (-0.1, 0.08, 0.24):
            line(L, [P(0.55, k), P(0.85, k + 0.02)], 0.9, K['skin_dk'] * 0.6, 0.5, seed + int(k * 50), 0.3)


def shoe_front(L, cx, y, w, h, col=None, seed=0, snow=0.0, flip=1):
    """布鞋（正面）：y 是鞋底。"""
    col = K['dark'] if col is None else np.asarray(col, F)
    pts = [(cx - w * 0.5, y - h * 0.35), (cx - w * 0.38, y - h * 0.9), (cx + w * 0.1, y - h), (cx + w * 0.45, y - h * 0.6), (cx + w * 0.52, y - h * 0.1), (cx + w * 0.3, y), (cx - w * 0.45, y - h * 0.02)]
    garment(L, pts, col, seed, wob=0.8, smooth=2, shade=0.25, stain=0.2, flick=0.3, ink_w=1.8, tex_k=0.1)
    brush(L, [(cx - w * 0.47, y - h * 0.1), (cx, y + 0.5), (cx + w * 0.5, y - h * 0.08)], w0=2.4, color=K['sole'], op=0.8, seed=seed + 1, taper=0.15, wob=0.5)
    if snow > 0:
        wash(L, [(cx - w * 0.45, y - h * 0.5), (cx - w * 0.1, y - h * 1.0), (cx + w * 0.3, y - h * 0.8), (cx + w * 0.5, y - h * 0.3), (cx, y - h * 0.4)], K['snow'], op=snow, wob=1.0, seed=seed + 2, smooth=2, tex_k=0.05, rim=0.1)


def shoe_side(L, cx, y, w, h, col=None, seed=0, snow=0.0, toe=1):
    """布鞋（侧面，脚尖朝 toe 方向）。cx 是脚的中点。"""
    col = K['dark'] if col is None else np.asarray(col, F)
    t = toe
    pts = [(cx - t * w * 0.5, y - h * 0.9), (cx - t * w * 0.1, y - h * 1.0), (cx + t * w * 0.2, y - h * 0.8), (cx + t * w * 0.45, y - h * 0.4), (cx + t * w * 0.52, y - h * 0.1), (cx + t * w * 0.3, y), (cx - t * w * 0.5, y)]
    garment(L, pts, col, seed, wob=0.8, smooth=2, shade=0.25, stain=0.2, flick=0.3, ink_w=1.8, tex_k=0.1)
    brush(L, [(cx - t * w * 0.5, y - 1), (cx, y + 0.5), (cx + t * w * 0.52, y - h * 0.1)], w0=2.6, color=K['sole'], op=0.85, seed=seed + 1, taper=0.15, wob=0.5)
    if snow > 0:
        wash(L, [(cx - t * w * 0.2, y - h * 0.8), (cx + t * w * 0.2, y - h * 0.7), (cx + t * w * 0.5, y - h * 0.2), (cx, y - h * 0.4)], K['snow'], op=snow, wob=1.0, seed=seed + 2, smooth=2, tex_k=0.05, rim=0.1)


# ───────────────────────── 脸 ─────────────────────────
def head_pts(cx, cy, a, b, jaw=1.0):
    u = [(0, -1), (0.60, -0.9), (0.94, -0.5), (1.0, -0.05), (0.94, 0.36), (0.74 * jaw, 0.78), (0.38 * jaw, 0.96), (0, 1.0)]
    right = [(cx + x * a, cy + y * b) for x, y in u]
    left = [(cx - x * a, cy + y * b) for x, y in u[::-1][1:-1]]
    return right + left


def eye_dot(L, x, y, rx, ry, seed=0, col=None, hi=True, op=0.95):
    col = INK if col is None else np.asarray(col, F)
    pts = ellipse_pts(x, y, rx, ry, 10)
    wash(L, pts, col, op=op, wob=0.1, seed=seed, smooth=1, tex_k=0.0, rim=0.0)
    if hi and rx >= 2.4:
        dots(L, [(x - rx * 0.25, y - ry * 0.35, max(rx * 0.28, 0.7))], hexc('#f5efe4'), op=0.85, soft=0.4)


def face_front(L, cx, cy, a, b, seed=0, skin=None, mood='smile', age=0.0, blush=0.5, ears=True, eye_y=0.12, eye_sep=0.42,
               brow='plain', nose=True, jaw=1.0, eye_r=0.085, closed_eyes=False, light=1, cheek_col=None, mouth_w=0.2, look=(0, 0)):
    """正脸：脸型 + 耳 + 脸侧淡淡的阴影 + 腮红 + 点睛 + 眉 + 鼻 + 嘴。age 0~1 加皱纹。"""
    skin = K['skin'] if skin is None else np.asarray(skin, F)
    sk_sh = mix(skin, K['skin_sh'], 0.9)
    r = np.random.default_rng(seed + 5)
    if ears:
        for s_ in (-1, 1):
            ep = ellipse_pts(cx + s_ * a * 0.99, cy + b * 0.1, a * 0.14, b * 0.17, 10, jit=0.05, seed=seed + s_)
            wash(L, ep, mix(skin, sk_sh, 0.2), op=1.0, wob=0.3, seed=seed + 11, smooth=1, tex_k=0.05, rim=0.25, rim_w=1.5)
            brush(L, [(cx + s_ * a * 1.02, cy + b * 0.02), (cx + s_ * a * 1.12, cy + b * 0.1), (cx + s_ * a * 1.04, cy + b * 0.24)], w0=1.1, color=K['skin_dk'] * 0.6, op=0.55, seed=seed + 12 + s_, taper=0.4, wob=0.2)
    p = proc(head_pts(cx, cy, a, b, jaw), 0.7, seed, 2)
    wash(L, p, skin, op=1.0, wob=0, seed=seed, smooth=0, tex_k=0.07, rim=0.22, rim_w=2.2)
    m = mask_of(L, p)
    bb = bbox_of(L, p)
    with Clip(L, m, bb) as T:
        side_glaze(T, bb, sk_sh, seed + 3, light, 0.74, 0.5, 0.2, 40)
        # 腮红
        cc = K['cheek'] if cheek_col is None else np.asarray(cheek_col, F)
        for s_ in (-1, 1):
            glow(T, cx + s_ * a * 0.58, cy + b * (eye_y + 0.38), a * 0.3, cc, op=blush, power=1.4)
        # 下巴/脖子上的淡影
        side_glaze(T, bb, sk_sh, seed + 4, 1, 0.9, 0.3, 0.1, 30, True)
    ink_outline(L, p, seed, w=1.3, op=0.6, gaps=0.5, color=K['skin_dk'] * 0.5, minseg=20, maxseg=70)
    ey = cy + b * eye_y
    ex = a * eye_sep
    er = max(a * eye_r, 1.8)
    for s_ in (-1, 1):
        if closed_eyes:
            brush(L, [(cx + s_ * ex - er * 1.6, ey), (cx + s_ * ex, ey + er * 0.9), (cx + s_ * ex + er * 1.6, ey)], w0=1.6, color=INK, op=0.85, seed=seed + 20 + s_, taper=0.35, wob=0.2)
        else:
            eye_dot(L, cx + s_ * ex + look[0], ey + look[1], er, er * 1.15, seed + s_)
            brush(L, [(cx + s_ * ex - er * 1.5, ey - er * 0.2), (cx + s_ * ex, ey - er * 1.5), (cx + s_ * ex + er * 1.5, ey - er * 0.3)], w0=1.3, color=INK, op=0.7, seed=seed + 25 + s_, taper=0.45, wob=0.1)
        # 眉
        by = ey - b * 0.19
        if brow == 'plain':
            brush(L, [(cx + s_ * ex - er * 1.6, by + 1.5 * s_ * 0), (cx + s_ * ex, by - 1.4), (cx + s_ * ex + er * 1.7, by + 0.6)], w0=1.7, color=INK * 1.0, op=0.8, seed=seed + 30 + s_, taper=0.45, wob=0.2)
        elif brow == 'stern':   # 板着但不凶：近乎水平的粗眉，内端只低一点点
            brush(L, [(cx + s_ * ex - s_ * er * 1.9, by - 0.6), (cx + s_ * ex, by - 1.0), (cx + s_ * ex + s_ * er * 1.8, by + 0.9)], w0=2.6, color=INK, op=0.9, seed=seed + 30 + s_, taper=0.4, wob=0.2)
        elif brow == 'soft':
            brush(L, [(cx + s_ * ex - er * 1.7, by + 1.2), (cx + s_ * ex, by - 1.8), (cx + s_ * ex + er * 1.8, by + 1.4)], w0=1.6, color=INK * 1.0, op=0.7, seed=seed + 30 + s_, taper=0.45, wob=0.2)
        elif brow == 'white':
            brush(L, [(cx + s_ * ex - er * 1.8, by + 1.2), (cx + s_ * ex, by - 2.0), (cx + s_ * ex + er * 2.0, by + 1.4)], w0=2.6, color=hexc('#c9c8c6'), op=0.9, seed=seed + 30 + s_, taper=0.45, wob=0.2)
            brush(L, [(cx + s_ * ex - er * 1.8, by + 1.2), (cx + s_ * ex, by - 2.0), (cx + s_ * ex + er * 2.0, by + 1.4)], w0=1.0, color=K['grey_sh'], op=0.5, seed=seed + 33 + s_, taper=0.45, wob=0.2)
    if nose:
        ny = cy + b * (eye_y + 0.34)
        brush(L, [(cx - a * 0.04, ny - b * 0.12), (cx + a * 0.06, ny + b * 0.02), (cx - a * 0.04, ny + b * 0.06)], w0=1.2, color=K['skin_dk'] * 0.65, op=0.7, seed=seed + 40, taper=0.4, wob=0.2)
    my = cy + b * (eye_y + 0.62)
    mw = a * mouth_w
    if mood == 'smile':
        brush(L, [(cx - mw, my - 1.2), (cx, my + mw * 0.55), (cx + mw, my - 1.4)], w0=1.7, color=hexc('#6a3b30'), op=0.85, seed=seed + 50, taper=0.45, wob=0.2)
    elif mood == 'grin':
        pts = [(cx - mw * 1.1, my - 1), (cx, my + mw * 0.7), (cx + mw * 1.1, my - 1.2), (cx, my + mw * 0.15)]
        wash(L, pts, hexc('#6f3f35'), op=0.9, wob=0.1, seed=seed + 51, smooth=2, tex_k=0, rim=0)
    elif mood == 'calm':
        brush(L, [(cx - mw * 0.8, my), (cx, my + 0.8), (cx + mw * 0.8, my - 0.2)], w0=1.6, color=hexc('#6a3b30'), op=0.8, seed=seed + 50, taper=0.45, wob=0.2)
    elif mood == 'stern':
        brush(L, [(cx - mw * 0.9, my + 0.4), (cx, my), (cx + mw * 0.9, my + 0.4)], w0=1.9, color=hexc('#5a3329'), op=0.85, seed=seed + 50, taper=0.4, wob=0.2)
    elif mood == 'open':
        wash(L, ellipse_pts(cx, my + 1, mw * 0.7, mw * 0.8, 10), hexc('#6f3f35'), op=0.9, wob=0.1, seed=seed + 51, smooth=1, tex_k=0, rim=0)
    if age > 0:
        n = int(age * 5)
        for k in range(n):
            s_ = -1 if k % 2 == 0 else 1
            yy = ey + b * (0.05 + 0.05 * k)
            brush(L, [(cx + s_ * a * 0.75, yy), (cx + s_ * a * 0.7, yy + 3), (cx + s_ * a * 0.6, yy + 6)], w0=1.0, color=K['skin_dk'] * 0.7, op=0.4 * age + 0.2, seed=seed + 60 + k, taper=0.4, wob=0.2)
        brush(L, [(cx - a * 0.45, my - b * 0.1), (cx - a * 0.5, my + b * 0.08)], w0=1.0, color=K['skin_dk'] * 0.7, op=0.5 * age, seed=seed + 70, taper=0.4, wob=0.2)
        brush(L, [(cx + a * 0.45, my - b * 0.1), (cx + a * 0.5, my + b * 0.08)], w0=1.0, color=K['skin_dk'] * 0.7, op=0.5 * age, seed=seed + 71, taper=0.4, wob=0.2)
        for yy in (-0.62, -0.5):
            brush(L, [(cx - a * 0.4, cy + b * yy), (cx, cy + b * (yy - 0.03)), (cx + a * 0.4, cy + b * yy)], w0=0.9, color=K['skin_dk'] * 0.7, op=0.3 * age, seed=seed + 80, taper=0.4, wob=0.3)
    return p


def profile_pts(cx, cy, a, b, nose=1.0, chin=1.0, jaw=1.0, brow=1.0, lip=1.0):
    """侧脸（脸朝右）多边形：从头顶开始顺时针。a=半宽，b=半高。nose 鼻子突出量，chin 下巴前伸，brow 眉骨。"""
    u = [(-0.1, -1.0), (0.4, -0.97), (0.74, -0.74), (0.9 * brow, -0.42), (0.93 * brow, -0.2), (0.89, -0.05), (0.92 + 0.2 * nose, 0.17), (0.95, 0.27),
         (0.98 * lip, 0.36), (0.93, 0.44), (0.95 * lip, 0.53), (0.87 * chin, 0.7), (0.72 * chin, 0.92), (0.38, 1.0), (-0.1, 0.96 * jaw), (-0.55, 0.72), (-0.9, 0.3), (-0.98, -0.2), (-0.8, -0.72)]
    return [(cx + x * a, cy + y * b) for x, y in u]


def face_side(L, cx, cy, a, b, seed=0, skin=None, mood='smile', age=0.0, blush=0.45, nose=1.0, chin=1.0, eye_y=0.0, brow='plain', jaw=1.0, mouth_w=0.2, ear=True, look=0.0, browr=1.0, lip=1.0):
    """侧脸（朝右）：头型 + 耳 + 眼 + 眉 + 鼻 + 嘴。"""
    skin = K['skin'] if skin is None else np.asarray(skin, F)
    sk_sh = mix(skin, K['skin_sh'], 0.9)
    p = proc(profile_pts(cx, cy, a, b, nose, chin, jaw, browr, lip), 0.6, seed, 2)
    wash(L, p, skin, op=1.0, wob=0, seed=seed, smooth=0, tex_k=0.07, rim=0.22, rim_w=2.2)
    m = mask_of(L, p)
    bb = bbox_of(L, p)
    with Clip(L, m, bb) as T:
        side_glaze(T, bb, sk_sh, seed + 3, -1, 0.7, 0.45, 0.2, 40)
        glow(T, cx + a * 0.5, cy + b * (eye_y + 0.38), a * 0.3, K['cheek'], op=blush, power=1.4)
        side_glaze(T, bb, sk_sh, seed + 4, 1, 0.9, 0.3, 0.1, 30, True)
    ink_outline(L, p, seed, w=1.3, op=0.65, gaps=0.4, color=K['skin_dk'] * 0.5, minseg=20, maxseg=70)
    ey = cy + b * eye_y
    ex = cx + a * 0.56
    er = max(a * 0.085, 1.8)
    eye_dot(L, ex + look, ey, er * 0.95, er * 1.15, seed + 1)
    brush(L, [(ex - er * 1.8, ey - b * 0.17), (ex, ey - b * 0.22), (ex + er * 1.7, ey - b * 0.15)], w0=1.8, color=INK, op=0.8, seed=seed + 2, taper=0.45, wob=0.2)
    if ear:
        ep = ellipse_pts(cx - a * 0.12, cy + b * 0.1, a * 0.14, b * 0.2, 10)
        wash(L, ep, mix(skin, sk_sh, 0.35), op=1.0, wob=0.3, seed=seed + 11, smooth=1, tex_k=0.05, rim=0.3, rim_w=1.5)
        brush(L, [(cx - a * 0.16, cy + b * 0.0), (cx - a * 0.08, cy + b * 0.1), (cx - a * 0.16, cy + b * 0.2)], w0=1.0, color=K['skin_dk'] * 0.6, op=0.5, seed=seed + 12, taper=0.4, wob=0.2)
    # 鼻
    brush(L, [(cx + a * (0.92 + 0.12 * nose), cy + b * 0.2), (cx + a * 0.97, cy + b * 0.25), (cx + a * 0.88, cy + b * 0.25)], w0=1.1, color=K['skin_dk'] * 0.7, op=0.6, seed=seed + 3, taper=0.4, wob=0.1)
    brush(L, [(ex - er * 1.6, ey - er * 0.1), (ex + er * 0.2, ey - er * 1.5), (ex + er * 1.5, ey - er * 0.2)], w0=1.2, color=INK, op=0.7, seed=seed + 4, taper=0.45, wob=0.1)
    my = cy + b * 0.52
    mx = cx + a * 0.86
    mw = a * mouth_w
    if mood == 'smile':
        brush(L, [(mx - mw * 1.2, my - 0.6), (mx - mw * 0.4, my + mw * 0.5), (mx + mw * 0.1, my - 0.4)], w0=1.6, color=hexc('#6a3b30'), op=0.85, seed=seed + 50, taper=0.45, wob=0.1)
    elif mood == 'stern':
        brush(L, [(mx - mw * 1.2, my), (mx - mw * 0.3, my + 0.5), (mx + mw * 0.1, my)], w0=1.7, color=hexc('#5a3329'), op=0.85, seed=seed + 50, taper=0.4, wob=0.1)
    else:
        brush(L, [(mx - mw * 1.1, my), (mx - mw * 0.3, my + 0.6), (mx + mw * 0.1, my - 0.2)], w0=1.5, color=hexc('#6a3b30'), op=0.8, seed=seed + 50, taper=0.45, wob=0.1)
    if age > 0:
        for k in range(int(age * 4)):
            yy = ey + b * (0.08 + 0.07 * k)
            brush(L, [(ex - a * 0.1, yy), (ex - a * 0.3, yy + 3)], w0=1.0, color=K['skin_dk'] * 0.7, op=0.35 + 0.2 * age, seed=seed + 60 + k, taper=0.4, wob=0.2)
    return p


# ───────────────────────── 头发 / 胡须 / 帽 ─────────────────────────
def hair_mass(L, pts, col=None, seed=0, strands=14, hi=True, outline=True, wob=1.2, smooth=2, sheen=0.5, flick_out=0, direction=None):
    """一团头发：墨黑的平涂 + 一点灰蓝高光笔 + 顺发流的细线 + 几根飞出来的发丝。"""
    col = K['hair'] if col is None else np.asarray(col, F)
    p = proc(pts, wob, seed, smooth)
    wash(L, p, col, op=1.0, wob=0, seed=seed, smooth=0, tex_k=0.18, rim=0.18, rim_w=2.2)
    m = mask_of(L, p)
    bb = bbox_of(L, p)
    r = np.random.default_rng(seed + 9)
    y0, y1, x0, x1 = bb
    light = mix(col, hexc('#8d94a3'), 0.55)
    with Clip(L, m, bb) as T:
        if hi:
            side_glaze(T, bb, light, seed + 2, -1, 0.5, 0.22 * sheen, 0.4, 30)
        st = []
        for _ in range(strands):
            x = r.uniform(x0, x1); y = r.uniform(y0, y1)
            if direction is None:
                ang = math.radians(90 + r.normal(0, 30))
            else:
                ang = math.radians(direction + r.normal(0, 20))
            ln = r.uniform(10, 28)
            st.append((x, y, x + math.cos(ang) * ln, y + math.sin(ang) * ln, r.uniform(1.0, 1.8), r.uniform(0.2, 0.45)))
        flicks(T, st, color=light)
    return p


def beard(L, pts, col, seed=0, strands=30, direction=90):
    p = proc(pts, 1.0, seed, 2)
    col = np.asarray(col, F)
    wash(L, p, col, op=1.0, wob=0, seed=seed, smooth=0, tex_k=0.2, rim=0.15, rim_w=2.0)
    m = mask_of(L, p)
    bb = bbox_of(L, p)
    r = np.random.default_rng(seed + 3)
    y0, y1, x0, x1 = bb
    dk = mix(col, INK, 0.5)
    lt = mix(col, hexc('#f0ead8'), 0.45)
    with Clip(L, m, bb) as T:
        st, st2 = [], []
        for _ in range(strands):
            x = r.uniform(x0, x1); y = r.uniform(y0, y1)
            ang = math.radians(direction + r.normal(0, 12))
            ln = r.uniform(10, 26)
            (st if r.random() < 0.55 else st2).append((x, y, x + math.cos(ang) * ln, y + math.sin(ang) * ln, r.uniform(1.0, 1.7), r.uniform(0.25, 0.55)))
        flicks(T, st, color=dk)
        flicks(T, st2, color=lt)
    return p


def ground_cloth_fold(L, a, b, col, seed=0, w=1.6, op=0.5):
    line(L, [a, ((a[0] + b[0]) / 2 + 2, (a[1] + b[1]) / 2), b], w, col, op, seed, 0.4, 0.2, 0.6)


# ───────────────────────── 收尾 ─────────────────────────
def bleed_rgb(L, sigma=5):
    """把有颜色的边缘“渗”到透明区域里，避免 watercolorize 在轮廓处出现黑边/亮边。"""
    a = L.a
    pm = L.rgb * a[..., None]
    num = cv2.GaussianBlur(pm, (0, 0), sigma)
    den = cv2.GaussianBlur(a, (0, 0), sigma)
    fill = num / np.maximum(den, 1e-4)[..., None]
    w = np.clip(1 - a * 2, 0, 1)[..., None]
    L.rgb = (L.rgb * (1 - w) + fill * w).astype(F)


def sheet_save(L, name, anchor, wc_seed=1, pad=4, meta=True, wc=True, wc_kw=None):
    """水彩化 → 裁到外框 + pad → 存 PNG → 写 sprites.json（只加/更新自己的键，重新读一遍最新内容）。anchor=(x,y) 是画布坐标里的脚底/底边中点。"""
    if wc:
        bleed_rgb(L)
        kw = dict(grain_k=0.04, pool_k=0.07, edge_k=0.30, wobble=0.0)
        if wc_kw:
            kw.update(wc_kw)
        watercolorize(L, seed=wc_seed, **kw)
        L.rgb[L.a < 0.004] = 0
    ys, xs = np.nonzero(L.a > 0.02)
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + 1 + pad, L.w)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + 1 + pad, L.h)
    C = Canvas(x1 - x0, y1 - y0)
    C.rgb = L.rgb[y0:y1, x0:x1].copy()
    C.a = L.a[y0:y1, x0:x1].copy()
    SPR.mkdir(parents=True, exist_ok=True)
    C.save(SPR / f'{name}.png')
    ax, ay = anchor[0] - x0, anchor[1] - y0
    info = {'w': int(C.w), 'h': int(C.h), 'ax': round(float(ax), 1), 'ay': int(round(ay))}
    if meta:
        register(name, info)
    print(name, info)
    return info


def register(name, info):
    """sprites.json 是共享文件：写之前重新读最新内容，只更新自己的键。"""
    path = SPR / 'sprites.json'
    d = json.loads(path.read_text()) if path.exists() else {}
    old = d.get(name, {})
    new = dict(info)
    # 保留已有的 night 标记之外的字段；改了图就让 make_night 重新生成（它比较 mtime）
    for k, v in old.items():
        new.setdefault(k, v)
    d[name] = new
    path.write_text(json.dumps(d, indent=1))


def new_canvas(w, h):
    return Canvas(w, h)


# ───────────────────────── 甲片 / 小物 ─────────────────────────
def scale_pattern(L, mask, bb, col, seed=0, dx=17.0, dy=13.0, dark=None, op=1.0, edge=0.42):
    """鱼鳞/札甲的甲片纹：逐像素算出每片甲的位置，亮暗 + 边线，按 mask 裁剪。"""
    y0, y1, x0, x1 = bb
    h, w = y1 - y0, x1 - x0
    col = np.asarray(col, F)
    dark = mix(col, INK, 0.55) if dark is None else np.asarray(dark, F)
    yy, xx = np.mgrid[0:h, 0:w].astype(F)
    wn = fbm(h, w, seed + 1, 24, 3, 0.5)
    wn2 = fbm(h, w, seed + 2, 24, 3, 0.5)
    xx = xx + (wn - 0.5) * dx * 0.5
    yy = yy + (wn2 - 0.5) * dy * 0.5
    v = yy / dy
    row = np.floor(v)
    fv = v - row
    u = (xx + x0) / dx - 0.5 * (row % 2)
    cell = np.floor(u)
    fu = u - cell
    rr = np.random.default_rng(seed)
    tab = rr.random(4096).astype(F)
    h_ = tab[((cell.astype(np.int64) * 73 + row.astype(np.int64) * 151) % 4096)]
    tone = 0.82 + 0.3 * h_
    shade = 1.0 - 0.28 * fv ** 2
    lineA = np.clip(1 - np.minimum(fu, 1 - fu) / 0.07, 0, 1)            # 竖边
    bot = 0.80 + 0.22 * (1 - (2 * fu - 1) ** 2)                         # 底边（拱形）
    lineB = np.clip(1 - np.abs(fv - bot) / 0.09, 0, 1)
    ln = np.clip(np.maximum(lineA, lineB), 0, 1) * edge
    rgb = col[None, None, :] * (tone * shade)[..., None]
    rgb = rgb * (1 - ln[..., None]) + dark[None, None, :] * ln[..., None]
    a = np.ones((h, w), F)
    m = mask[y0:y1, x0:x1] * op
    L.over(y0, y1, x0, x1, np.clip(rgb, 0, 1).astype(F), m)


def paste_layer(L, U, pivot, deg=0.0, dx=0.0, dy=0.0, scale=1.0):
    """把临时画布 U 绕 pivot 旋转 deg 度（顺时针为正，即向右倾）后盖到 L 上，可再平移。用来画“前倾”“歪头”。"""
    M = cv2.getRotationMatrix2D((float(pivot[0]), float(pivot[1])), -deg, scale)
    M[0, 2] += dx
    M[1, 2] += dy
    pm = (U.rgb * U.a[..., None]).astype(F)
    pm2 = cv2.warpAffine(pm, M, (L.w, L.h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    a2 = cv2.warpAffine(U.a, M, (L.w, L.h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    rgb = pm2 / np.maximum(a2, 1e-5)[..., None]
    L.over(0, L.h, 0, L.w, np.clip(rgb, 0, 1).astype(F), a2)
