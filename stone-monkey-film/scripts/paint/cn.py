"""中国水墨水彩风的画法工具（在 pt.py 的画布/墨线/水彩块之上）：
天空和云、山脊 + 皴擦、雾带、松/老树/柳/竹、石头、水面、茅屋、桥、城墙……

约定
- 所有图先用“中性”的淡彩（灰绿、土黄、石灰、青灰）画在 float RGBA 画布上，重点是明暗层次；
- 再用 grade.py 变成 夜色（靛蓝 + 纸白 + 墨）/ 光照下的柔彩 / 晨光 三套；
- 坐标是像素，原点左上角；y 越大越近。
"""
import math
import numpy as np
import cv2
from pt import *  # noqa

INK = hexc('#2A2622')
NIGHT = hexc('#121A2E')
INDIGO = hexc('#1E2A44')
MIDBLUE = hexc('#5A6B86')
PAPER = hexc('#EFE8D8')

# 中性淡彩（只管明暗和大致的色相，最终颜色由 grade 决定）
N = {
    'paper': hexc('#efe8d8'), 'mist': hexc('#e6e4dc'),
    'far1': hexc('#c9d0d6'), 'far2': hexc('#aab5bf'), 'far3': hexc('#8a98a6'),
    'mid1': hexc('#7e8e90'), 'mid2': hexc('#65777a'), 'mid3': hexc('#4e5f64'),
    'near1': hexc('#5a6a62'), 'near2': hexc('#46544e'), 'near3': hexc('#2f3a38'),
    'earth': hexc('#9b8a68'), 'earth_dk': hexc('#6f6048'), 'earth_lt': hexc('#c3b48f'),
    'stone': hexc('#8c8f8e'), 'stone_dk': hexc('#4f5557'), 'stone_lt': hexc('#c2c3bd'),
    'grass': hexc('#8d9a73'), 'grass_dk': hexc('#5f6e55'),
    'pine': hexc('#3f5649'), 'pine_dk': hexc('#2a3a33'),
    'thatch': hexc('#a99568'), 'thatch_dk': hexc('#7c6c48'),
    'wood': hexc('#7a6650'), 'wood_dk': hexc('#4d3f32'),
    'water': hexc('#8fa4b0'), 'water_dk': hexc('#5e7584'),
    'snow': hexc('#f2f0ea'), 'snow_sh': hexc('#c3cbd6'),
    'cloth_blue': hexc('#566c8c'), 'cloth_grey': hexc('#8a8c8e'),
}


def mix(a, b, t):
    return a + (b - a) * t


def rect(x0, y0, x1, y1):
    return np.array([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], F)


# ───────────────────────── 笔触工具 ─────────────────────────
_DRY = {}


def dry_noise(W, H, seed=11):
    k = (W, H, seed)
    if k not in _DRY:
        a = fbm(H, W, seed, 9, 3, 0.6)
        b = fbm(H, W, seed + 5, 3, 3, 0.5)
        _DRY[k] = np.clip(0.65 * a + 0.35 * b, 0, 1).astype(F)
    return _DRY[k]


def brush(L, pts, w0=3.0, w1=None, color=INK, op=0.9, seed=0, wob=1.0, taper=0.3, dry=0.0, ss=2, smooth=True):
    """一笔：宽度渐变、两头收尖，可带飞白（dry 0~1：越大越“干”）。"""
    p = np.asarray(pts, F)
    if smooth and len(p) >= 3:
        p = catmull(p, 10)
    elif len(p) >= 2:
        segs = [p[0:1]]
        for a, b in zip(p[:-1], p[1:]):
            n = max(int(np.hypot(*(b - a)) / 6), 1)
            segs.append(a + (b - a) * (np.arange(1, n + 1)[:, None] / n))
        p = np.vstack(segs)
    if len(p) < 2:
        return
    p = wobble_pts(p, wob, seed, 0.04)
    w1 = w0 if w1 is None else w1
    n = len(p)
    t = np.linspace(0, 1, n)
    prof = np.minimum(1, np.minimum(t, 1 - t) / max(taper, 1e-3))
    prof = 0.2 + 0.8 * np.sin(prof * math.pi / 2)
    wid = (w0 + (w1 - w0) * t) * prof
    r = np.random.default_rng(seed + 5)
    wid *= 1 + 0.2 * (cv2.resize(r.random((1, max(n // 5, 3))).astype(F), (n, 1), interpolation=cv2.INTER_CUBIC)[0] - 0.5) * 2
    mx = max(w0, w1) * 2 + 4
    x0, y0 = int(p[:, 0].min() - mx), int(p[:, 1].min() - mx)
    x1, y1 = int(p[:, 0].max() + mx), int(p[:, 1].max() + mx)
    x0c, y0c, x1c, y1c = max(x0, 0), max(y0, 0), min(x1, L.w), min(y1, L.h)
    if x1c <= x0c or y1c <= y0c:
        return
    w, h = x1c - x0c, y1c - y0c
    big = np.zeros((h * ss, w * ss), np.uint8)
    q = (p - [x0c, y0c]) * ss
    for i in range(n - 1):
        rad = max(wid[i] * ss / 2, 0.5)
        cv2.line(big, tuple(np.round(q[i]).astype(int)), tuple(np.round(q[i + 1]).astype(int)), 255, max(int(round(rad * 2)), 1), cv2.LINE_AA)
    m = cv2.resize(big, (w, h), interpolation=cv2.INTER_AREA).astype(F) / 255.0
    if dry > 0:
        dn = dry_noise(L.w, L.h)[y0c:y1c, x0c:x1c]
        m = m * np.clip((dn - dry * 0.9) / (1.0 - dry * 0.9 + 1e-3) * 2.2, 0, 1)
    L.over(y0c, y1c, x0c, x1c, np.asarray(color, F), m * op)


def flicks(L, strokes, color=INK, ss=2):
    """批量画“短促的笔触”：strokes = [(x0,y0,x1,y1,width,opacity), ...]，一端粗一端尖（皴擦、苔点、草丛）。"""
    if not len(strokes):
        return
    S = np.asarray(strokes, F)
    pad = 6
    x0 = int(max(S[:, [0, 2]].min() - pad, 0)); x1 = int(min(S[:, [0, 2]].max() + pad, L.w))
    y0 = int(max(S[:, [1, 3]].min() - pad, 0)); y1 = int(min(S[:, [1, 3]].max() + pad, L.h))
    if x1 <= x0 or y1 <= y0:
        return
    w, h = x1 - x0, y1 - y0
    big = np.zeros((h * ss, w * ss), np.uint8)
    for (ax, ay, bx, by, wd, op) in S[np.argsort(S[:, 5])]:
        ax, ay, bx, by = (ax - x0) * ss, (ay - y0) * ss, (bx - x0) * ss, (by - y0) * ss
        dx, dy = bx - ax, by - ay
        ln = math.hypot(dx, dy) + 1e-6
        nx, ny = -dy / ln, dx / ln
        hw = max(wd * ss / 2, 0.5)
        mx_, my_ = (ax + bx) / 2 + nx * ln * 0.07, (ay + by) / 2 + ny * ln * 0.07
        poly = np.array([[ax + nx * hw, ay + ny * hw], [mx_ + nx * hw * 0.8, my_ + ny * hw * 0.8], [bx, by],
                         [mx_ - nx * hw * 0.8, my_ - ny * hw * 0.8], [ax - nx * hw, ay - ny * hw]], np.float32)
        cv2.fillPoly(big, [np.round(poly).astype(np.int32)], int(255 * min(max(op, 0.02), 1)), lineType=cv2.LINE_AA)
    m = cv2.resize(big, (w, h), interpolation=cv2.INTER_AREA).astype(F) / 255.0
    L.over(y0, y1, x0, x1, np.asarray(color, F), m)


# ───────────────────────── 天空 / 云 / 雾 ─────────────────────────
def sky(W, H, top, mid, bot, seed=1, horizon=0.8, cloud=0.35, cloud_col=None, scale=420, stretch=2.6):
    """天空：三色渐变 + 水渍似的斑驳 + 横向拉长的云带（亮的一面朝上）。返回不透明画布。"""
    L = Canvas(W, H, bg=0.0)
    y = np.linspace(0, 1, H, dtype=F)[:, None]
    t = np.clip(y / horizon, 0, 1)
    top, mid, bot = np.asarray(top, F), np.asarray(mid, F), np.asarray(bot, F)
    base = np.where(t[..., None] < 0.5, mix(top, mid, np.clip(t / 0.5, 0, 1)[..., None]), mix(mid, bot, np.clip((t - 0.5) / 0.5, 0, 1)[..., None] ** 1.3))
    base = np.broadcast_to(base, (H, W, 3)).copy()

    def stretched(sd, sc, octv=5, warp=0.0):
        w2 = max(int(W / stretch), 8)
        n = fbm(H, w2, sd, sc / stretch, octv, 0.55, warp=warp)
        return cv2.resize(n, (W, H), interpolation=cv2.INTER_CUBIC)

    n1 = stretched(seed, scale, 5, scale * 0.10)
    n2 = stretched(seed + 9, scale * 0.3, 4, 20)
    blotch = (n1 - 0.5) * 0.42 + (n2 - 0.5) * 0.16
    base = base * (1 + blotch[..., None] * 0.55)
    if cloud > 0:
        cc = np.asarray(cloud_col if cloud_col is not None else mix(mid, np.ones(3, F), 0.5), F)
        c = smoothstep(0.50, 0.78, stretched(seed + 21, scale * 0.9, 5, scale * 0.12))
        c = c * (1 - np.clip((y - horizon * 0.92) / 0.18, 0, 1))
        grad = cv2.GaussianBlur(c, (0, 0), 16)
        under = np.clip(cv2.GaussianBlur(np.roll(c, 14, axis=0), (0, 0), 10) - c, 0, 1)
        base = mix(base, cc, (c * cloud)[..., None] * 0.75)
        base = base * (1 - 0.22 * under[..., None] * cloud)
    base += grain(H, W, seed + 3, 0.8)[..., None] * 0.012
    L.rgb = np.clip(base, 0, 1).astype(F)
    L.a[:] = 1.0
    return L


def mist(L, x0, x1, yc, thick, seed=0, color=None, op=0.5, scale=260, squash=0.22):
    """一条横向的雾带：沿横向拉长的噪声 + 竖直方向的钟形包络（水墨里“留白”的云气）。"""
    color = N['mist'] if color is None else np.asarray(color, F)
    W = x1 - x0
    y0, y1 = int(yc - thick), int(yc + thick)
    h = y1 - y0
    if W <= 0 or h <= 0:
        return
    n = fbm(h, W, seed, scale, 4, 0.55, warp=40)
    # 竖直方向拉伸：同一个噪声沿 y 方向更“糊”
    n = cv2.resize(cv2.resize(n, (W, max(int(h * squash), 2)), interpolation=cv2.INTER_AREA), (W, h), interpolation=cv2.INTER_CUBIC)
    yy = (np.arange(h, dtype=F)[:, None] - h / 2) / (h / 2)
    env = np.exp(-(yy ** 2) * 2.2)
    a = np.clip((n - 0.38) * 2.2, 0, 1) * env
    a = cv2.GaussianBlur(a, (0, 0), 6)
    L.over(y0, y1, x0, x1, color, np.clip(a * op, 0, 1).astype(F))


# ───────────────────────── 山 ─────────────────────────
def ridge_y(W, base, amp, seed, rough=0.55, peaky=0.65, scale=520, x0=0):
    """山脊线 y(x)：低频起伏 + 尖峰（abs 噪声）+ 高频碎石。base 是山脚线的 y，amp 是最大山高（像素）。"""
    r = np.random.default_rng(seed)
    x = np.arange(W, dtype=F) + x0
    tot = np.zeros(W, F)
    amp_o, norm = 1.0, 0.0
    cell = scale
    for o in range(6):
        k = int((W + x0) / cell) + 4
        g = r.random(k + 1).astype(F)
        xs = x / cell
        i0 = np.floor(xs).astype(int)
        f = xs - i0
        f = f * f * (3 - 2 * f)
        v = g[i0] * (1 - f) + g[i0 + 1] * f
        if o in (1, 2):
            v = 1 - np.abs(2 * v - 1)   # 尖峰
            v = v ** 1.4
        tot += amp_o * v
        norm += amp_o
        amp_o *= rough
        cell = max(cell / 2.0, 6)
    tot /= norm
    tot = (tot - tot.min()) / (tot.max() - tot.min() + 1e-6)
    tot = tot ** (1.0 + (1 - peaky) * 0.0)
    return base - amp * tot


def peaks_of(ridge, min_prom=18):
    """山脊上的峰（局部最高点）：返回 [(x, y, 左谷x, 右谷x)]"""
    r = cv2.GaussianBlur(np.asarray(ridge, F).reshape(1, -1), (0, 0), 5)[0]
    W = len(r)
    out = []
    i = 8
    while i < W - 8:
        if r[i] < r[i - 1] and r[i] <= r[i + 1]:   # y 越小越高
            lo = i
            while lo > 0 and r[lo - 1] >= r[lo] - 0 and r[lo - 1] > r[i] - 1e9 and (r[lo - 1] <= r[lo] + 400):
                if r[lo - 1] < r[lo] - 0.01 and False:
                    break
                lo -= 1
                if lo <= 0 or (lo > 0 and r[lo - 1] < r[lo]):
                    break
            hi = i
            while hi < W - 1 and r[hi + 1] >= r[hi]:
                hi += 1
            if abs(r[lo] - r[i]) + abs(r[hi] - r[i]) > min_prom:
                out.append((i, float(ridge[i]), lo, hi))
            i = max(hi, i + 1)
        else:
            i += 1
    return out


def mountain(L, ridge, bottom, top_col, bot_col, seed=0, tex=0.5, tex_col=INK, tex_op=0.28, snow=None, snow_from=0.35, rim_w=2.2, rim_op=0.5, lit_dir=1, haze=0.0, haze_col=None, mist_amt=0.0, glaze=0.5, shade_col=None):
    """画一列山（水彩层层罩染的画法）：底色渐变 → 每座峰的背光面罩一层深色 + 山沟的竖向淡墨 → 沿山体的皴擦短笔 → 断续的山脊墨线 → 雪盖。
    ridge: 每列山脊 y（长度 = L.w）；bottom: 山脚 y。lit_dir=1 表示光从左来（右侧背光）。"""
    W, H = L.w, L.h
    ridge = np.asarray(ridge, F)
    bottom = np.broadcast_to(np.asarray(bottom, F), (W,)).copy()
    top_col, bot_col = np.asarray(top_col, F), np.asarray(bot_col, F)
    shade_col = mix(top_col, INK, 0.45) if shade_col is None else np.asarray(shade_col, F)
    ymin = int(max(ridge.min() - 4, 0)); ymax = int(min(bottom.max() + 2, H))
    h = ymax - ymin
    yy = np.arange(ymin, ymax, dtype=F)[:, None]
    depth = np.clip((yy - ridge[None, :]) / np.maximum(bottom - ridge, 1)[None, :], 0, 1)
    base = mix(top_col, bot_col, (depth ** 0.8)[..., None])
    n = fbm(h, W, seed + 1, 140, 5, 0.55, warp=30)
    base = base * (0.9 + 0.2 * n[..., None]) + grain(h, W, seed + 8, 0.9)[..., None] * 0.012
    if haze > 0:
        hc = np.asarray(N['mist'] if haze_col is None else haze_col, F)
        base = mix(base, hc, (haze * (1 - depth ** 0.5))[..., None])
    a = np.clip((yy - ridge[None, :]) / 3.0, 0, 1) * np.clip((bottom[None, :] - yy) / 20.0, 0, 1)
    L.over(ymin, ymax, 0, W, np.clip(base, 0, 1).astype(F), a.astype(F))
    rng = np.random.default_rng(seed + 7)
    pk = peaks_of(ridge)
    # 背光面罩染：每座峰朝背光一侧的斜面，一块多边形，边缘有水渍积色
    for (px, py, lo, hi) in pk:
        a_, b_ = (px, hi) if lit_dir > 0 else (lo, px)
        if b_ - a_ < 20:
            continue
        xs = np.arange(a_, b_ + 1)
        top_pts = [(float(x), float(ridge[x]) + 1.5) for x in xs[::max(len(xs) // 14, 1)]]
        hgt = float(np.mean(bottom[a_:b_ + 1]) - py)
        reach = rng.uniform(0.45, 0.8)
        inner_x = (a_ if lit_dir < 0 else b_)
        # 内侧边界：从峰顶斜下来
        inner = [(px + lit_dir * (b_ - a_) * 0.05 + rng.normal(0, 6), py + hgt * 0.08)]
        for k in range(1, 5):
            t = k / 4
            inner.append((px + lit_dir * (b_ - a_) * (0.1 + 0.35 * t) + rng.normal(0, 10), py + hgt * reach * t * rng.uniform(0.8, 1.1)))
        far = [(b_ if lit_dir > 0 else a_, float(ridge[b_ if lit_dir > 0 else a_]) + hgt * reach * 0.9)]
        poly = top_pts + far + inner[::-1] if lit_dir > 0 else top_pts[::-1] + far + inner[::-1]
        wash(L, poly, shade_col, op=glaze * rng.uniform(0.5, 0.9), wob=2.5, seed=int(rng.integers(1e6)), smooth=2, tex_k=0.2, rim=0.2, rim_w=3.0)
    # 山沟：从山脊垂下来的竖向淡墨，细长、顶端宽、渐渐收尖
    for (px, py, lo, hi) in pk:
        for _ in range(int(rng.integers(2, 6))):
            gx = px + rng.normal(0, (hi - lo) * 0.22)
            gx = float(np.clip(gx, 2, W - 3))
            gy = float(ridge[int(gx)]) + 4
            ln = rng.uniform(0.25, 0.7) * float(np.mean(bottom[max(lo, 0):hi + 1]) - py)
            lean = rng.normal(0, 0.16) + lit_dir * 0.1
            brush(L, [(gx, gy), (gx + lean * ln * 0.5, gy + ln * 0.5), (gx + lean * ln, gy + ln)], w0=rng.uniform(5, 14), w1=0.8, color=mix(shade_col, INK, 0.2), op=rng.uniform(0.16, 0.36) * (tex + 0.3), seed=int(rng.integers(1e6)), wob=2.0, taper=0.15, dry=0.2)
    # 皴擦：沿山体向下的短笔，顺着山势
    if tex > 0:
        count = int(W * (ymax - ymin) / 7000 * tex)
        xs = np.clip(rng.uniform(0, W, count).astype(int), 0, W - 1)
        d = rng.random(count) ** 1.6 * 0.85
        ys = ridge[xs] + d * (bottom[xs] - ridge[xs])
        ang = np.radians(rng.normal(70, 12, count)) * np.where(rng.random(count) < 0.5, 1, -1)
        ln = rng.uniform(10, 44, count) * (1 + (1 - d) * 0.5)
        wd = rng.uniform(0.9, 2.6, count)
        op = rng.uniform(0.3, 1.0, count) * tex_op * (1.0 - d * 0.6)
        st = np.stack([xs, ys, xs + np.cos(ang) * ln, ys + np.sin(np.abs(ang)) * ln, wd, op], 1)
        flicks(L, st, color=tex_col)
    # 山脊墨线（断续、有飞白）
    seg = 0
    xs_all = np.arange(W)
    while seg < W - 30:
        ln = int(rng.uniform(120, 420))
        sl_ = slice(seg, min(seg + ln, W))
        pts = np.stack([xs_all[sl_], ridge[sl_]], 1)[::14]
        if len(pts) >= 3:
            brush(L, pts, w0=rim_w * rng.uniform(0.8, 1.5), color=tex_col, op=rim_op * rng.uniform(0.6, 1.0), seed=int(rng.integers(1e6)), wob=0.8, taper=0.25, dry=0.3)
        seg += ln + int(rng.uniform(-20, 60))
    # 雪盖
    if snow is not None:
        snow_col = np.asarray(snow, F)
        rel = (np.arange(ymin, ymax, dtype=F)[:, None] - ridge[None, :]) / np.maximum(bottom - ridge, 1)[None, :]
        nn = fbm(h, W, seed + 33, 80, 5, 0.6, warp=30)
        edge = snow_from * (0.5 + 0.8 * nn)
        sm = (1 - smoothstep(edge - 0.05, edge + 0.01, rel)) * (rel >= 0)
        L.over(ymin, ymax, 0, W, np.clip(snow_col * (0.94 + 0.08 * nn[..., None]), 0, 1).astype(F), np.clip(sm * a, 0, 1).astype(F) * 0.95)
    if mist_amt > 0:
        mist(L, 0, W, float(np.mean(bottom)) - 20, 110, seed + 40, op=mist_amt)


# ───────────────────────── 植物 ─────────────────────────
def pine(L, x, y, h, seed=0, col=None, dark=None, snow=0.0, lean=0.0, op=1.0):
    """一棵松（水墨的画法）：细而弯的树干 + 几片参差的叶团（层层罩染 + 边缘的点苔），不画成圣诞树。x,y 是树脚。"""
    col = N['pine'] if col is None else np.asarray(col, F)
    dark = N['pine_dk'] if dark is None else np.asarray(dark, F)
    r = np.random.default_rng(seed)
    top = (x + lean * h, y - h)
    mid = (x + lean * h * 0.5 + r.normal(0, h * 0.05), y - h * 0.5)
    brush(L, [(x, y), mid, top], w0=max(h * 0.045, 2.2), w1=max(h * 0.012, 1.0), color=N['wood_dk'] * 0.55, op=0.9 * op, seed=seed, wob=h * 0.012, taper=0.08)
    nclump = 3 + int(h / 110)
    for i in range(nclump):
        f = 0.42 + 0.55 * (i / max(nclump - 1, 1)) + r.normal(0, 0.03)
        side = (-1 if i % 2 == 0 else 1) * r.uniform(0.0, 1.0)
        cx = x + lean * h * f + side * h * 0.1 * (1.15 - f)
        cy = y - h * f
        rx = h * (0.17 - 0.07 * f) * r.uniform(0.85, 1.25) + 5
        ry = rx * r.uniform(0.30, 0.42)
        n = 11
        pts = []
        for k, a in enumerate(np.linspace(0, 2 * math.pi, n, endpoint=False)):
            jit = r.uniform(0.78, 1.18)
            pts.append((cx + math.cos(a) * rx * jit, cy + math.sin(a) * ry * jit * (1.0 if math.sin(a) < 0 else 0.7)))
        wash(L, pts, mix(col, dark, r.uniform(0.0, 0.45)), op=0.9 * op, wob=2.2, seed=int(r.integers(1e6)), smooth=2, tex_k=0.25, rim=0.25, rim_w=2.5)
        # 上沿提亮一笔（受光的叶面）
        wash(L, [(cx - rx * 0.6, cy - ry * 0.1), (cx - rx * 0.1, cy - ry * 0.75), (cx + rx * 0.5, cy - ry * 0.6), (cx + rx * 0.1, cy - ry * 0.2)], mix(col, N['paper'], 0.28), op=0.4 * op, wob=1.5, seed=int(r.integers(1e6)), smooth=2, tex_k=0.1, rim=0.0)
        st = []
        for _ in range(int(rx * 0.9)):
            a = r.uniform(math.pi * 0.9, math.pi * 2.1)
            px, py = cx + math.cos(a) * rx * r.uniform(0.7, 1.12), cy + math.sin(a) * ry * r.uniform(0.7, 1.15)
            st.append((px, py, px + r.normal(0, 2.5), py + r.uniform(1.5, 6), r.uniform(1.4, 2.8), r.uniform(0.4, 0.85) * op))
        flicks(L, st, color=dark)
        # 垂下的枝
        brush(L, [(cx - rx * 0.9, cy + ry * 0.2), (cx - rx * 1.0, cy + ry * 1.0), (cx - rx * 0.95, cy + ry * 1.9)], w0=1.4, color=dark, op=0.6 * op, seed=int(r.integers(1e6)), taper=0.4, wob=0.8)
        if snow > 0:
            wash(L, [(cx - rx * 0.8, cy - ry * 0.25), (cx - rx * 0.2, cy - ry * 0.9), (cx + rx * 0.5, cy - ry * 0.75), (cx + rx * 0.8, cy - ry * 0.2), (cx, cy - ry * 0.35)], N['snow'], op=snow * op, wob=1.2, seed=int(r.integers(1e6)), smooth=2, tex_k=0.08)


def old_tree(L, x, y, h, seed=0, col=None, depth=5, spread=0.85, leaf=0.0, op=1.0, trunk_w=None, snow=0.0):
    """老树 / 光秃秃的树：粗而扭的树干（一侧加深、树皮的竖皴）+ 递归的细枝（下粗上细、收尖的墨线），枝头可挂一点叶/雪。"""
    col = N['wood_dk'] * 0.6 if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    tw = trunk_w or h * 0.07

    def branch(px, py, ang, ln, wd, d):
        n = 5
        pts = [(px, py)]
        a = ang
        cx, cy = px, py
        for k in range(n):
            a += r.normal(0, 0.2) - 0.05 * math.copysign(1, math.cos(a)) * (1 if d > 2 else 0)
            cx += math.cos(a) * ln / n
            cy += math.sin(a) * ln / n
            pts.append((cx, cy))
        brush(L, pts, w0=wd, w1=max(wd * 0.34, 0.9), color=col, op=0.95 * op, seed=int(r.integers(1e6)), wob=ln * 0.025, taper=0.06 if d < 2 else 0.25, dry=0.0)
        if wd > 5:
            brush(L, [(p[0] + wd * 0.18, p[1]) for p in pts], w0=wd * 0.35, w1=0.8, color=col * 0.6, op=0.55 * op, seed=int(r.integers(1e6)), wob=ln * 0.03, taper=0.2)
        if d >= depth:
            if snow > 0:
                brush(L, [(cx - 14, cy + 2), (cx, cy - 1), (cx + 14, cy + 2)], w0=3.0, color=N['snow'], op=snow * op, seed=int(r.integers(1e6)), taper=0.4)
            if leaf > 0:
                for _ in range(2):
                    wash(L, [(cx + r.normal(0, 6) + dx, cy + r.normal(0, 4) + dy) for dx, dy in ((-9, 0), (0, -7), (9, 0), (0, 6))], N['grass_dk'], op=leaf * op, wob=1.5, seed=int(r.integers(1e6)), smooth=2)
            return
        for s_ in (-1, 1):
            if r.random() < 0.9:
                branch(cx, cy, a + s_ * spread * r.uniform(0.45, 1.0), ln * r.uniform(0.6, 0.78), wd * 0.62, d + 1)
        if r.random() < 0.55:
            branch(cx, cy, a + r.normal(0, 0.2), ln * 0.66, wd * 0.55, d + 1)

    # 树干：弯曲，下粗上细，底部像盘根
    t0 = (x, y)
    t1 = (x + r.normal(0, h * 0.03), y - h * 0.2)
    t2 = (x + r.normal(0, h * 0.05), y - h * 0.4)
    brush(L, [t0, t1, t2], w0=tw * 1.7, w1=tw * 0.95, color=col, op=0.97 * op, seed=seed, wob=3.0, taper=0.04, dry=0.0)
    brush(L, [(x + tw * 0.45, y), (t1[0] + tw * 0.3, t1[1]), (t2[0] + tw * 0.2, t2[1])], w0=tw * 0.6, w1=tw * 0.35, color=col * 0.55, op=0.5 * op, seed=seed + 3, wob=3.0, taper=0.1)
    for s_ in (-1, 1):   # 树根
        brush(L, [(x + s_ * tw * 0.5, y - 8), (x + s_ * tw * 1.1, y + 2), (x + s_ * tw * 1.9, y + 6)], w0=tw * 0.5, w1=2, color=col, op=0.85 * op, seed=seed + 5 + s_, wob=2.0, taper=0.1)
    st = []
    for _ in range(int(h * 0.3)):
        t = r.uniform(0, 0.4)
        px = x + r.uniform(-tw * 0.75, tw * 0.75) * (1.3 - t)
        py = y - h * t
        st.append((px, py, px + r.normal(0, 2), py - r.uniform(8, 26), r.uniform(0.9, 1.9), r.uniform(0.25, 0.6) * op))
    flicks(L, st, color=col * 0.5)
    ex, ey = t2
    for s_ in (-1, 0, 1):
        branch(ex, ey, -math.pi / 2 + s_ * 0.6 + r.normal(0, 0.1), h * 0.44, tw * 0.6, 1)


def willow(L, x, y, h, seed=0, col=None, op=1.0):
    """柳：斜出的树干 + 一把把下垂的长条。"""
    col = N['grass'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    top = (x + h * 0.12, y - h)
    brush(L, [(x, y), (x + h * 0.02, y - h * 0.5), top], w0=h * 0.045, w1=h * 0.015, color=N['wood_dk'] * 0.6, op=0.9 * op, seed=seed, wob=2, taper=0.1)
    for _ in range(int(h / 6)):
        bx = top[0] + r.normal(0, h * 0.22)
        by = top[1] + r.uniform(-0.05, 0.22) * h
        ln = r.uniform(0.28, 0.6) * h
        brush(L, [(bx, by), (bx + r.normal(0, 8), by + ln * 0.5), (bx + r.normal(0, 14), by + ln)], w0=1.8, w1=0.8, color=mix(col, N['grass_dk'], r.uniform(0, 0.6)), op=r.uniform(0.35, 0.8) * op, seed=int(r.integers(1e6)), wob=1.2, taper=0.3)


def bamboo(L, x, y, h, seed=0, n=5, col=None, op=1.0):
    col = N['grass_dk'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    for i in range(n):
        bx = x + r.normal(0, h * 0.06) + i * h * 0.04
        bh = h * r.uniform(0.75, 1.1)
        brush(L, [(bx, y), (bx + r.normal(0, 3), y - bh * 0.5), (bx + r.normal(0, 6), y - bh)], w0=h * 0.022, w1=h * 0.016, color=mix(col, N['paper'], 0.15), op=0.85 * op, seed=int(r.integers(1e6)), wob=0.8, taper=0.05)
        for k in range(1, int(bh / 70) + 1):
            ny = y - k * 70 + r.normal(0, 4)
            brush(L, [(bx - 6, ny), (bx + 7, ny + 1)], w0=2.2, color=N['pine_dk'], op=0.7 * op, seed=int(r.integers(1e6)), taper=0.2, smooth=False)
        st = []
        for _ in range(int(bh / 16)):
            ty = y - bh * r.uniform(0.4, 1.0)
            tx = bx + r.normal(0, 4)
            dirx = r.choice([-1, 1])
            ln = r.uniform(30, 64)
            st.append((tx, ty, tx + dirx * ln, ty + r.uniform(8, 26), r.uniform(2.2, 3.6), r.uniform(0.5, 0.9) * op))
        flicks(L, st, color=mix(N['grass_dk'], N['pine_dk'], 0.5))


def grass_tufts(L, x0, x1, y_arr, n, seed=0, col=None, op=0.7, hmin=10, hmax=34):
    """地面上的草丛：一小簇细笔。y_arr 是每列的地面 y。"""
    col = N['grass_dk'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    st = []
    for _ in range(n):
        x = r.uniform(x0, x1)
        y = y_arr[int(min(max(x, 0), len(y_arr) - 1))] + r.uniform(0, 14)
        for k in range(r.integers(3, 7)):
            ln = r.uniform(hmin, hmax)
            st.append((x + k * 2.2, y, x + k * 2.2 + r.normal(0, ln * 0.35), y - ln, r.uniform(0.9, 1.7), r.uniform(0.3, 0.8) * op))
    flicks(L, st, color=col)


# ───────────────────────── 石头 ─────────────────────────
def rock(L, cx, by, w, h, seed=0, col=None, dark=None, light=None, snow=0.0, lit_dir=1, op=1.0, moss=0.0):
    """一块山石：不规则多边形 + 三个明暗面 + 沿面的皴擦 + 断续的墨线。cx,by 是底边中点。"""
    col = N['stone'] if col is None else np.asarray(col, F)
    dark = N['stone_dk'] if dark is None else np.asarray(dark, F)
    light = N['stone_lt'] if light is None else np.asarray(light, F)
    r = np.random.default_rng(seed)
    k = 9
    angs = np.linspace(math.pi, 2 * math.pi, k)   # 上半部分的轮廓
    top = [(cx + math.cos(a) * w / 2 * r.uniform(0.85, 1.05), by - h * (-math.sin(a)) * r.uniform(0.75, 1.1)) for a in angs]
    # 让顶部有棱角：随机拉高 1~2 个点
    for j in r.choice(range(2, k - 2), 2, replace=False):
        top[j] = (top[j][0] + r.normal(0, w * 0.04), top[j][1] - h * r.uniform(0.05, 0.2))
    pts = top + [(cx + w / 2 * 1.02, by), (cx - w / 2 * 1.02, by)]
    wash(L, pts, col, op=op, wob=2.0, seed=seed, smooth=1, tex_k=0.22, rim=0.2, rim_w=2.5)
    # 受光面（亮）
    lx = -lit_dir
    lp = [p for p in top[: k // 2 + 1]] if lit_dir > 0 else [p for p in top[k // 2:]]
    face = lp + [(cx + (-lit_dir) * w * 0.05, by - h * 0.12), (cx - lit_dir * (-w * 0.42), by - h * 0.02)]
    wash(L, face, light, op=0.55 * op, wob=2.5, seed=seed + 2, smooth=2, tex_k=0.15, rim=0.1)
    # 背光面（暗）
    dp = [p for p in top[k // 2:]] if lit_dir > 0 else [p for p in top[: k // 2 + 1]]
    face2 = dp + [(cx + lit_dir * w / 2 * 1.0, by), (cx + lit_dir * w * 0.1, by)]
    wash(L, face2, dark, op=0.6 * op, wob=2.5, seed=seed + 3, smooth=2, tex_k=0.15, rim=0.1)
    # 皴
    st = []
    for _ in range(int(w * h / 500)):
        px = cx + r.uniform(-w * 0.45, w * 0.45)
        py = by - r.uniform(0.05, 0.9) * h * (1 - abs(px - cx) / (w * 0.6)) 
        ln = r.uniform(8, 26)
        ang = math.radians(r.normal(70, 18) * (1 if lit_dir > 0 else -1) + (0 if r.random() > 0.2 else 90))
        st.append((px, py, px + math.cos(ang) * ln * 0.5, py - math.sin(ang) * ln, r.uniform(0.9, 2.0), r.uniform(0.2, 0.6) * op))
    flicks(L, st, color=INK)
    # 轮廓
    rr = np.random.default_rng(seed + 9)
    brush(L, top, w0=2.6, color=INK, op=0.7 * op, seed=seed + 4, wob=1.0, taper=0.15, dry=0.3)
    if snow > 0:
        sp = [(x_, y_ ) for (x_, y_) in top[1:-1]] + [(top[-2][0], top[-2][1] + h * 0.18), (top[len(top) // 2][0], top[len(top) // 2][1] + h * 0.3), (top[1][0], top[1][1] + h * 0.16)]
        wash(L, sp, N['snow'], op=snow * op, wob=2.0, seed=seed + 5, smooth=2, tex_k=0.08, rim=0.1)
    if moss > 0:
        flicks(L, [(cx + r.uniform(-w * .4, w * .4), by - r.uniform(0, h * .7), 0, 0, 2.2, 0.5 * moss) for _ in range(0)], color=N['grass_dk'])


# ───────────────────────── 地面 / 水 ─────────────────────────
def ground_strip(L, y_arr, bottom, top_col, bot_col, seed=0, x0=0, x1=None, rim_op=0.5, tex=0.5, tex_col=None):
    """一条地面：上沿是 y_arr（每列），向下渐变；带草丛/土面的横向短笔和一条断续的墨线。"""
    x1 = L.w if x1 is None else x1
    W = x1 - x0
    y_arr = np.asarray(y_arr, F)[x0:x1]
    ymin = int(max(y_arr.min() - 4, 0)); ymax = int(min(bottom, L.h))
    h = ymax - ymin
    yy = np.arange(ymin, ymax, dtype=F)[:, None]
    depth = np.clip((yy - y_arr[None, :]) / max(bottom - y_arr.min(), 1), 0, 1)
    base = mix(np.asarray(top_col, F), np.asarray(bot_col, F), depth[..., None] ** 0.8)
    n = fbm(h, W, seed + 2, 120, 5, 0.55, warp=50)
    base = base * (0.9 + 0.2 * n[..., None]) + grain(h, W, seed + 4, 0.9)[..., None] * 0.015
    a = np.clip((yy - y_arr[None, :]) / 2.5, 0, 1)
    L.over(ymin, ymax, x0, x1, np.clip(base, 0, 1).astype(F), a.astype(F))
    r = np.random.default_rng(seed + 9)
    tc = INK if tex_col is None else tex_col
    st = []
    for _ in range(int(W * (ymax - ymin) / 4500 * tex)):
        x = r.uniform(0, W)
        d = r.random() ** 1.3
        y = y_arr[int(x)] + d * (bottom - y_arr[int(x)])
        ln = r.uniform(10, 50) * (0.5 + d)
        st.append((x + x0, y, x + x0 + ln, y + r.normal(0, 1.4), r.uniform(0.9, 2.0), r.uniform(0.12, 0.4)))
    flicks(L, st, color=tc)
    seg = 0
    while seg < W - 30:
        ln = int(r.uniform(150, 500))
        pts = np.stack([np.arange(seg, min(seg + ln, W)) + x0, y_arr[seg:seg + ln]], 1)[::16]
        if len(pts) >= 3:
            brush(L, pts, w0=r.uniform(1.8, 3.4), color=INK, op=rim_op * r.uniform(0.6, 1.0), seed=int(r.integers(1e6)), wob=0.8, taper=0.25, dry=0.3)
        seg += ln + int(r.uniform(-10, 70))


def water(L, y0, y1, x0=0, x1=None, seed=0, top_col=None, bot_col=None, strokes=320, light_col=None, lit_x=None, lit_r=0, lit_col=None):
    """水面：渐变底 + 横向的长笔触（留出纸色的缝）+ 偶尔的亮色横线。"""
    x1 = L.w if x1 is None else x1
    W, h = x1 - x0, y1 - y0
    top_col = N['water'] if top_col is None else np.asarray(top_col, F)
    bot_col = N['water_dk'] if bot_col is None else np.asarray(bot_col, F)
    light_col = N['paper'] if light_col is None else np.asarray(light_col, F)
    yy = np.linspace(0, 1, h, dtype=F)[:, None, None]
    base = mix(top_col, bot_col, yy ** 0.9) * np.ones((1, W, 1), F)
    n = fbm(h, W, seed, 200, 4, 0.5, warp=40)
    base = base * (0.9 + 0.2 * n[..., None])
    L.over(y0, y1, x0, x1, np.clip(base, 0, 1).astype(F), np.ones((h, W), F))
    r = np.random.default_rng(seed + 3)
    st, lt = [], []
    for _ in range(strokes):
        d = r.random() ** 1.2
        y = y0 + d * h
        x = r.uniform(x0, x1)
        ln = r.uniform(30, 160) * (0.4 + d * 1.2)
        st.append((x, y, x + ln, y + r.normal(0, 0.8), r.uniform(1.2, 3.0) * (0.5 + d), r.uniform(0.12, 0.35)))
        if r.random() < 0.55:
            lt.append((x + ln * 0.2, y + 3, x + ln * 0.8, y + 3 + r.normal(0, 0.6), r.uniform(1.0, 2.0) * (0.5 + d), r.uniform(0.15, 0.5)))
    flicks(L, st, color=INK * 0.8 + 0.1 * bot_col)
    flicks(L, lt, color=light_col)
    if lit_x is not None and lit_r > 0:
        lc = N['paper'] if lit_col is None else np.asarray(lit_col, F)
        for _ in range(int(lit_r / 5)):
            xx = lit_x + r.normal(0, lit_r * 0.4)
            yy_ = y0 + r.random() * h
            ln = r.uniform(20, 80)
            brush(L, [(xx - ln / 2, yy_), (xx + ln / 2, yy_ + r.normal(0, 1))], w0=r.uniform(1.4, 3.0), color=lc, op=r.uniform(0.3, 0.8), seed=int(r.integers(1e6)), taper=0.4, smooth=False)


# ───────────────────────── 建筑 ─────────────────────────
def curve_roof(L, cx, y_eave, w, rise, seed=0, col=None, edge=None, thick=14, op=1.0, tiles=True, sag=0.12, up=0.18):
    """中式屋顶（正面）：中间微微下凹，两端飞檐翘起。cx 屋顶中线，y_eave 檐口的水平线。"""
    col = N['wood_dk'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    xs = np.linspace(-1, 1, 30)
    lower = [(cx + x * w / 2, y_eave + (x ** 2) * w * sag * 0.0 - (abs(x) ** 3.2) * w * up) for x in xs]
    # 上沿：屋脊（略高）
    upper = [(cx + x * w * 0.36, y_eave - rise + (abs(x) ** 3.0) * rise * 0.12) for x in xs[::-1]]
    pts = lower + upper
    wash(L, pts, col, op=op, wob=1.0, seed=seed, smooth=1, tex_k=0.18, rim=0.15, rim_w=2.0)
    if tiles:
        st = []
        for i in range(int(w / 7)):
            t = r.uniform(-0.95, 0.95)
            xx = cx + t * w / 2 * 0.9
            top_y = y_eave - rise * (1 - abs(t)) * 0.9 - 4
            bot_y = y_eave - (abs(t) ** 3.2) * w * up
            st.append((xx, top_y + r.uniform(0, rise * 0.1), xx + r.normal(0, 1.5), bot_y, r.uniform(0.8, 1.5), r.uniform(0.2, 0.5) * op))
        flicks(L, st, color=INK)
    brush(L, lower, w0=thick * 0.3, color=INK, op=0.85 * op, seed=seed + 1, wob=0.6, taper=0.1)
    brush(L, upper[::-1], w0=2.4, color=INK, op=0.8 * op, seed=seed + 2, wob=0.6, taper=0.1)


def thatch_hut(L, x, y, w, h, seed=0, wall=None, snow=0.0, door=True, window=True, op=1.0, lit=None, roof_rise=0.34, eave=0.62):
    """茅屋：矮的石/土墙 + 宽檐的草顶（层层的草束）+ 木门 + 小窗。x,y 是墙脚中点；h 是墙+屋顶的总高。lit 是窗/门的光色（None 表示不亮）。"""
    wall = N['stone'] if wall is None else np.asarray(wall, F)
    r = np.random.default_rng(seed)
    rh = w * roof_rise
    wh = max(h - rh, h * 0.45)
    top = y - wh
    wash(L, rect(x - w / 2, top, x + w / 2, y), wall, op=op, wob=1.6, seed=seed, smooth=0, tex_k=0.22, rim=0.18, rim_w=2.5)
    st = []
    for row in range(int(wh / 24)):
        yy = y - row * 24 - 10
        xx = x - w / 2 + r.uniform(0, 30)
        while xx < x + w / 2 - 20:
            ln = r.uniform(30, 70)
            st.append((xx, yy, min(xx + ln, x + w / 2 - 2), yy + r.normal(0, 1), r.uniform(1.0, 1.9), r.uniform(0.2, 0.45) * op))
            xx += ln + r.uniform(2, 12)
    flicks(L, st, color=INK)
    # 墙角两道竖线
    for sx in (-1, 1):
        brush(L, [(x + sx * w / 2, y), (x + sx * w / 2, top)], w0=2.6, color=INK, op=0.6 * op, seed=seed + 11 + sx, wob=0.8, taper=0.05, dry=0.2)
    # 草顶：宽檐，两侧微微下凹，屋脊略平
    ex = w * eave
    roof = [(x - ex, top + 18), (x - ex * 0.78, top - rh * 0.28), (x - w * 0.34, top - rh * 0.8), (x - w * 0.2, top - rh), (x + w * 0.2, top - rh), (x + w * 0.34, top - rh * 0.8), (x + ex * 0.78, top - rh * 0.28), (x + ex, top + 18)]
    wash(L, roof, N['thatch'], op=op, wob=2.0, seed=seed + 1, smooth=2, tex_k=0.28, rim=0.25, rim_w=3)
    # 檐下阴影带
    wash(L, [(x - ex, top + 18), (x - ex * 0.8, top - rh * 0.1), (x + ex * 0.8, top - rh * 0.1), (x + ex, top + 18), (x + ex * 0.6, top + 26), (x - ex * 0.6, top + 26)], N['thatch_dk'], op=0.55 * op, wob=2.0, seed=seed + 2, smooth=2, tex_k=0.2, rim=0.0)
    st, st2 = [], []
    for _ in range(int(ex * rh / 38)):
        px = x + r.uniform(-ex * 0.96, ex * 0.96)
        edge = abs(px - x) / ex
        top_edge = top - rh * (1 - edge ** 1.8) * 0.98 + 14 * edge
        py = r.uniform(top_edge, top + 16)
        ln = r.uniform(12, 34)
        a_ = (st if r.random() < 0.6 else st2)
        a_.append((px, py, px + r.normal(0, 2.5) + (px - x) * 0.04, py + ln, r.uniform(1.0, 2.2), r.uniform(0.25, 0.7) * op))
    flicks(L, st, color=N['thatch_dk'] * 0.8)
    flicks(L, st2, color=mix(N['thatch'], N['paper'], 0.45))
    # 屋脊：压着几根横杆
    brush(L, [(x - w * 0.22, top - rh + 4), (x, top - rh - 2), (x + w * 0.22, top - rh + 4)], w0=4.0, color=INK, op=0.7 * op, seed=seed + 3, wob=1.2, dry=0.3, taper=0.1)
    brush(L, [roof[0], roof[1], roof[2], roof[3]], w0=2.6, color=INK, op=0.7 * op, seed=seed + 4, wob=1.2, dry=0.3, taper=0.15)
    brush(L, [roof[7], roof[6], roof[5], roof[4]], w0=2.6, color=INK, op=0.7 * op, seed=seed + 5, wob=1.2, dry=0.3, taper=0.15)
    brush(L, [(x - ex, top + 22), (x, top + 30), (x + ex, top + 22)], w0=3.6, color=INK, op=0.55 * op, seed=seed + 6, wob=1.2, dry=0.4, taper=0.1)
    if snow > 0:
        sp = [roof[1], roof[2], roof[3], roof[4], roof[5], roof[6], (x + w * 0.3, top - rh * 0.55), (x, top - rh * 0.78), (x - w * 0.3, top - rh * 0.55)]
        wash(L, sp, N['snow'], op=snow * op, wob=3, seed=seed + 7, smooth=2, tex_k=0.08, rim=0.1)
    if door:
        dw, dh = w * 0.19, wh * 0.9
        dx = x + w * 0.08
        wash(L, rect(dx - dw / 2, y - dh, dx + dw / 2, y), N['wood'] * 0.8 if lit is None else np.asarray(lit, F), op=op, wob=1.0, seed=seed + 8, smooth=0, tex_k=0.15, rim=0.2)
        for k in range(1, 4):
            brush(L, [(dx - dw / 2 + dw * k / 4, y), (dx - dw / 2 + dw * k / 4, y - dh)], w0=1.4, color=INK, op=0.35 * op, seed=seed + 20 + k, taper=0.05, smooth=False)
        brush(L, [(dx - dw / 2 - 6, y), (dx - dw / 2 - 6, y - dh - 6), (dx + dw / 2 + 6, y - dh - 6), (dx + dw / 2 + 6, y)], w0=4.5, color=N['wood_dk'] * 0.8, op=0.9 * op, seed=seed + 9, smooth=False, taper=0.03)
    if window:
        ww = w * 0.12
        wx, wy = x - w * 0.27, y - wh * 0.6
        wash(L, rect(wx - ww / 2, wy - ww / 2, wx + ww / 2, wy + ww / 2), N['wood_dk'] if lit is None else np.asarray(lit, F), op=op, wob=0.8, seed=seed + 12, smooth=0, tex_k=0.1)
        for k in (0.5,):
            brush(L, [(wx - ww / 2, wy), (wx + ww / 2, wy)], w0=2.0, color=INK, op=0.7 * op, seed=seed + 13, smooth=False, taper=0.05)
            brush(L, [(wx, wy - ww / 2), (wx, wy + ww / 2)], w0=2.0, color=INK, op=0.7 * op, seed=seed + 14, smooth=False, taper=0.05)
        brush(L, [(wx - ww / 2, wy - ww / 2), (wx + ww / 2, wy - ww / 2), (wx + ww / 2, wy + ww / 2), (wx - ww / 2, wy + ww / 2), (wx - ww / 2, wy - ww / 2)], w0=3.0, color=N['wood_dk'] * 0.7, op=0.9 * op, seed=seed + 10, smooth=False, taper=0.05)


def finish(L, name, out_dir, jpg=False, q=92):
    (out_dir).mkdir(parents=True, exist_ok=True)
    L.save(out_dir / f'{name}.{"jpg" if jpg else "png"}', jpg=jpg, q=q)


# ───────────────────────── 星图灯盘 ─────────────────────────
def lamp_disc(L, cx, cy, r, seed=0, col=None, lit=0.0, rim=True, chart=True):
    """天上那盏灯：一个圆。灭着的时候是灰色的，带淡淡的星图（同心圆、刻度、星点连线）。"""
    col = hexc('#c3c6c8') if col is None else np.asarray(col, F)
    rng = np.random.default_rng(seed)
    n = 40
    pts = [(cx + math.cos(a) * r * (1 + 0.012 * math.sin(a * 5 + seed)), cy + math.sin(a) * r * (1 + 0.012 * math.cos(a * 4 + seed))) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]
    wash(L, pts, col, op=0.95, wob=2.5, seed=seed, smooth=2, tex_k=0.22, rim=0.32, rim_w=6.0)
    # 内部再罩两层，做出水渍的深浅
    for k in range(3):
        rr = r * rng.uniform(0.45, 0.8)
        ox, oy = rng.normal(0, r * 0.12), rng.normal(0, r * 0.12)
        p2 = [(cx + ox + math.cos(a) * rr * rng.uniform(0.9, 1.1), cy + oy + math.sin(a) * rr * rng.uniform(0.9, 1.1)) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)]
        wash(L, p2, mix(col, INK, 0.12 + 0.05 * k), op=0.28, wob=6, seed=seed + k + 1, smooth=2, tex_k=0.18, rim=0.2, rim_w=4)
    if chart:
        for k, f in enumerate((0.93, 0.74, 0.5, 0.26)):
            brush(L, [(cx + math.cos(a) * r * f, cy + math.sin(a) * r * f) for a in np.linspace(0.0, 2 * math.pi * 0.985, 28)], w0=1.6, color=INK, op=0.32, seed=seed + 20 + k, wob=0.8, taper=0.05, dry=0.35)
        for k in range(36):
            a = k * math.pi / 18 + rng.normal(0, 0.01)
            l0, l1 = (0.93, 0.98) if k % 3 else (0.9, 1.0)
            brush(L, [(cx + math.cos(a) * r * l0, cy + math.sin(a) * r * l0), (cx + math.cos(a) * r * l1, cy + math.sin(a) * r * l1)], w0=1.4, color=INK, op=0.3, seed=seed + 60 + k, smooth=False, taper=0.1)
        # 星点连线
        stars = [(cx + rng.normal(0, r * 0.38), cy + rng.normal(0, r * 0.38)) for _ in range(9)]
        stars = [s for s in stars if math.hypot(s[0] - cx, s[1] - cy) < r * 0.82]
        for a_, b_ in zip(stars[:-1], stars[1:]):
            brush(L, [a_, ((a_[0] + b_[0]) / 2 + rng.normal(0, 3), (a_[1] + b_[1]) / 2 + rng.normal(0, 3)), b_], w0=1.2, color=INK, op=0.28, seed=int(rng.integers(1e6)), taper=0.2)
        dots(L, [(x, y, rng.uniform(2.0, 3.8)) for x, y in stars], INK, op=0.55)
    if rim:
        brush(L, [(cx + math.cos(a) * r, cy + math.sin(a) * r) for a in np.linspace(0.2, 2 * math.pi * 0.96, 30)], w0=2.8, color=INK, op=0.5, seed=seed + 99, wob=1.2, taper=0.15, dry=0.4)


# ───────────────────────── 整张画的“水彩化” ─────────────────────────
def watercolorize(L, seed=1, grain_k=0.05, pool_k=0.06, edge_k=0.35, wobble=1.6):
    """整张画布的收尾：颜料颗粒、色块里的深浅积色、色块边缘的积色（湿边）、整体极轻微的手抖位移。只动 RGB，不动 alpha。"""
    h, w = L.h, L.w
    rgb = L.rgb
    fine = fbm(h, w, seed, 6, 2, 0.5)
    mid = fbm(h, w, seed + 1, 70, 4, 0.55, warp=25)
    big = fbm(h, w, seed + 2, 260, 3, 0.5)
    k = 1 + (fine - 0.5) * grain_k * 2 + (mid - 0.5) * pool_k * 2 + (big - 0.5) * pool_k
    rgb = rgb * k[..., None]
    lum = rgb @ np.array([0.299, 0.587, 0.114], F)
    e = cv2.GaussianBlur(lum, (0, 0), 1.0) - cv2.GaussianBlur(lum, (0, 0), 4.5)
    # 比周围暗一点的边（色块边缘）更暗一些；比周围亮的边略提亮——湿边
    rgb = rgb * (1 + np.clip(e, -0.12, 0.12)[..., None] * edge_k * 2.2)
    if wobble > 0:
        n1 = fbm(h, w, seed + 7, 140, 3, 0.5)
        n2 = fbm(h, w, seed + 8, 140, 3, 0.5)
        yy, xx = np.mgrid[0:h, 0:w].astype(F)
        mx, my = xx + (n1 - 0.5) * wobble * 2, yy + (n2 - 0.5) * wobble * 2
        rgb = cv2.remap(rgb, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        L.a = cv2.remap(L.a, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    L.rgb = np.clip(rgb, 0, 1).astype(F)
    return L
