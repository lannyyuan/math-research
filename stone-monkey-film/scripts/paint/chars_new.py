"""《小石猴点灯》新人物与小道具精灵（Agent P）。
用法：python3 chars_new.py girl herder ...   （不带参数 = 全部）；每个函数画一个精灵并登记到 sprites.json。
"""
import sys
from cn_people import *

REG = {}


def sprite(fn):
    REG[fn.__name__] = fn
    return fn


# ───────────────────────── 公共零件 ─────────────────────────
def hair_cap_front(L, cx, cy, a, b, seed=0, fringe=0.45, side=0.25, puff=1.12, col=None, messy=0, tuft=0):
    f = fringe
    pts = [(cx - a * 1.05, cy + b * (0.18 + side)), (cx - a * 1.1, cy - b * 0.2), (cx - a * 0.9, cy - b * 0.8 * puff), (cx - a * 0.5, cy - b * 1.1 * puff),
           (cx, cy - b * 1.16 * puff), (cx + a * 0.5, cy - b * 1.1 * puff), (cx + a * 0.9, cy - b * 0.8 * puff), (cx + a * 1.1, cy - b * 0.2),
           (cx + a * 1.05, cy + b * (0.18 + side)), (cx + a * 0.92, cy + b * 0.05), (cx + a * 0.8, cy - b * 0.22), (cx + a * 0.52, cy - b * (f - 0.14)),
           (cx + a * 0.24, cy - b * f), (cx - a * 0.05, cy - b * (f - 0.08)), (cx - a * 0.32, cy - b * (f + 0.02)), (cx - a * 0.58, cy - b * (f - 0.14)),
           (cx - a * 0.82, cy - b * 0.2), (cx - a * 0.92, cy + b * 0.05)]
    p = hair_mass(L, pts, col, seed, strands=int(a * 0.6), direction=90)
    ink_outline(L, p, seed, w=1.6, op=0.5, gaps=0.35, color=INK, minseg=30, maxseg=90)
    r = np.random.default_rng(seed + 4)
    for _ in range(tuft):   # 飞出来的发丝
        ang = math.radians(r.uniform(-150, -30))
        bx, by = cx + math.cos(ang) * a * 0.9, cy + math.sin(ang) * b * 1.0
        ln = r.uniform(10, 20)
        line(L, [(bx, by), (bx + math.cos(ang) * ln * 0.6 + r.normal(0, 3), by + math.sin(ang) * ln * 0.6), (bx + math.cos(ang) * ln + r.normal(0, 4), by + math.sin(ang) * ln + 3)], 1.6, INK, 0.8, int(r.integers(1e6)), 0.5, 0, 0.3)
    return p


def collar(L, cx, y, w, h, inner=None, seed=0, lapel_col=None):
    """交领：脖子下的一个 V（露出里衣）+ 两道衣襟线。"""
    inner = K['white'] if inner is None else np.asarray(inner, F)
    wash(L, [(cx - w * 0.55, y - 3), (cx + w * 0.55, y - 3), (cx + w * 0.12, y + h), (cx - w * 0.12, y + h * 0.75)], K['skin'] * 0.96, op=1.0, wob=0.4, seed=seed, smooth=1, tex_k=0.05, rim=0.15)
    lc = INKB if lapel_col is None else lapel_col
    line(L, [(cx - w * 0.6, y - 4), (cx - w * 0.15, y + h * 0.7), (cx + w * 0.55, y + h * 1.9)], 2.2, lc, 0.85, seed + 1, 0.2, 0.1, 0.4)
    line(L, [(cx + w * 0.6, y - 4), (cx + w * 0.3, y + h * 0.9), (cx + w * 0.55, y + h * 1.9)], 2.0, lc, 0.8, seed + 2, 0.2, 0.1, 0.4)
    # 里衣的白边
    line(L, [(cx - w * 0.5, y - 1), (cx - w * 0.14, y + h * 0.62)], 3.0, inner, 0.9, seed + 3, 0.2, 0.0, 0.3)
    line(L, [(cx + w * 0.5, y - 1), (cx + w * 0.14, y + h * 0.62)], 3.0, inner, 0.9, seed + 4, 0.2, 0.0, 0.3)


def neck(L, cx, y0, y1, w, seed=0, skin=None):
    skin = K['skin'] if skin is None else np.asarray(skin, F)
    pts = [(cx - w / 2, y0), (cx + w / 2, y0), (cx + w * 0.56, y1), (cx - w * 0.56, y1)]
    garment(L, pts, mix(skin, K['skin_sh'], 0.35), seed, wob=0.4, smooth=1, shade=0.4, shade_start=0.5, stain=0.0, flick=0, outline=False, tex_k=0.05, rim=0.15)
    # 下巴投在脖子上的影
    wash(L, [(cx - w * 0.5, y0), (cx + w * 0.5, y0), (cx + w * 0.5, y0 + (y1 - y0) * 0.5), (cx, y0 + (y1 - y0) * 0.65), (cx - w * 0.5, y0 + (y1 - y0) * 0.5)], K['skin_dk'], op=0.35, wob=0.5, seed=seed + 1, smooth=2, tex_k=0.05, rim=0.0)


def sleeve(L, path, w0, w1, col, seed=0, cuff=None, cuff_col=None, wmid=None, **kw):
    p = tube(path, w0, w1, wmid=wmid, cap0=0.9, cap1=0.0)
    res = garment(L, p, col, seed, smooth=1, wob=1.0, **kw)
    if cuff:
        pth = np.asarray(path, F)
        d = pth[-1] - pth[-2]
        d /= max(np.hypot(*d), 1e-6)
        a_ = pth[-1] - d * cuff
        cp = tube([a_, pth[-1]], w1 * 1.04, w1 * 1.06, cap=0.0)
        garment(L, cp, K['linen_lt'] if cuff_col is None else cuff_col, seed + 50, smooth=1, wob=0.8, shade=0.15, stain=0.2, flick=0.2, ink_w=1.8)
    return res


def leg(L, path, w0, w1, col, seed=0, wrap=None, **kw):
    p = tube(path, w0, w1, cap=0.0)
    return garment(L, p, col, seed, smooth=1, wob=1.0, **kw)


# ───────────────────────── 1. 小姑娘 ─────────────────────────
def girl_front_draw(cx=210, foot=400, H=340, bowl=False, seed=100):
    L = new_canvas(420, 440)
    top = foot - H
    cy, a, b = top + 68, 37, 48       # 头
    ground_shadow(L, cx, foot + 2, 120, 14, 0.28, seed)
    # 腿：灰褐的裤袜 + 绑腿
    legcol = mix(K['white_sh'], K['gb'], 0.5)
    for s_ in (-1, 1):
        leg(L, [(cx + s_ * 15, foot - 112), (cx + s_ * 17, foot - 60), (cx + s_ * 18, foot - 14)], 20, 17, legcol, seed + s_, shade=0.38, stain=0.42, flick=0.4, ink_w=1.9, shade_dir=1)
        leg(L, [(cx + s_ * 18, foot - 33), (cx + s_ * 18, foot - 14)], 22, 21, K['linen_lt'], seed + 5 + s_, shade=0.2, stain=0.3, flick=0.2, ink_w=1.4)
        shoe_front(L, cx + s_ * 20, foot, 36, 18, K['dark'], seed + 10 + s_, snow=0.9)
    # 红裙（面积不大）
    sy = cy + b + 9 + 50
    sk = [(cx - 28, sy), (cx + 28, sy), (cx + 33, sy + 18), (cx + 45, sy + 50), (cx + 33, sy + 55), (cx + 17, sy + 51), (cx + 2, sy + 56), (cx - 14, sy + 51), (cx - 30, sy + 56), (cx - 46, sy + 50), (cx - 33, sy + 18)]
    garment(L, sk, K['red'], seed + 20, shade=0.36, stain=0.34, worn=0.1, flick=0.5, fdir=75, ink_w=2.0, hem_dirt=0.3, dark=hexc('#5e1d18'), light=hexc('#d09a8c'), smooth=1, edge_dk=0.2,
            folds=[[(cx - 16, sy + 10), (cx - 20, sy + 32), (cx - 26, sy + 50)], [(cx + 2, sy + 12), (cx + 1, sy + 32), (cx + 3, sy + 52)], [(cx + 18, sy + 10), (cx + 22, sy + 32), (cx + 30, sy + 50)]])
    fringe(L, [(cx - 44, sy + 52), (cx - 18, sy + 53), (cx + 18, sy + 52), (cx + 43, sy + 51)], hexc('#7a2a22'), seed + 40, 8, (4, 8), 0.6)
    # 上衣：灰蓝（下摆稍微外撇，肩膀有斜度）
    jy = cy + b + 9      # 肩线
    jk = lathe(cx, [(jy - 6, 12, 12), (jy - 1, 22, 22), (jy + 8, 36, 36), (jy + 18, 41, 41), (jy + 36, 37, 37), (jy + 50, 38, 38), (jy + 66, 44, 44)])
    jk_poly, jk_mask = garment(L, jk, K['blue'], seed + 50, shade=0.4, stain=0.42, worn=0.12, flick=0.6, ink_w=2.3, hem_dirt=0.2, smooth=1, edge_dk=0.25,
                               folds=[[(cx - 10, jy + 34), (cx - 15, jy + 52), (cx - 13, jy + 64)], [(cx + 18, jy + 30), (cx + 20, jy + 48), (cx + 26, jy + 63)]])
    neck(L, cx, cy + b - 12, jy + 4, 17, seed + 60)
    collar(L, cx, jy - 2, 22, 18, K['white'], seed + 61)
    # 腰带（粗绳）
    by_ = jy + 42
    brush(L, [(cx - 39, by_ - 2), (cx, by_ + 3), (cx + 39, by_ - 2)], w0=5, color=K['rope'], op=0.95, seed=seed + 70, taper=0.15, wob=0.6)
    for k in range(7):
        x = cx - 32 + k * 10.5
        line(L, [(x, by_ - 3), (x + 4, by_ + 4)], 1.1, K['rope_dk'], 0.7, seed + 80 + k, 0.3, 0, 0.1, smooth=False)
    brush(L, [(cx + 12, by_ + 3), (cx + 18, by_ + 18), (cx + 14, by_ + 30)], w0=3.0, color=K['rope'], op=0.9, seed=seed + 90, taper=0.3, wob=0.6)
    brush(L, [(cx + 14, by_ + 3), (cx + 6, by_ + 16), (cx + 8, by_ + 26)], w0=2.6, color=K['rope'], op=0.9, seed=seed + 91, taper=0.3, wob=0.6)
    # 补丁
    patch(L, cx - 20, jy + 58, 17, 14, K['linen'], seed + 100, ang=0.12)
    patch(L, cx + 20, jy + 22, 13, 12, K['gb_lt'], seed + 101, ang=-0.2)
    # 袖（手臂略向外，肘部微弯）
    if bowl:
        arms = [((cx - 33, jy + 12), (cx - 47, jy + 38), (cx - 22, jy + 54)), ((cx + 33, jy + 12), (cx + 47, jy + 38), (cx + 22, jy + 54))]
    else:
        arms = [((cx - 33, jy + 12), (cx - 49, jy + 38), (cx - 52, jy + 70)), ((cx + 33, jy + 12), (cx + 49, jy + 38), (cx + 51, jy + 70))]
    for i, (sh, el, wr) in enumerate(arms):
        s_ = -1 if i == 0 else 1
        ap = tube([sh, el, wr], 25, 21, cap0=0.9, cap1=0.0)
        shadow_on(L, jk_mask, ap, -s_ * 4, 3, op=0.4)
        sleeve(L, [sh, el, wr], 25, 21, K['blue'], seed + 110 + i, cuff=9, shade=0.4, stain=0.4, worn=0.1, flick=0.5, shade_dir=1, edge_dk=0.2,
               folds=[[(el[0] - s_ * 6, el[1] - 8), (el[0] - s_ * 1, el[1] + 2), (el[0] - s_ * 7, el[1] + 10)]])
        if not bowl:
            hand(L, wr[0], wr[1] + 2, math.pi / 2 + s_ * 0.12, 15, seed=seed + 120 + i, kind='open', side=-s_)
    # 脸
    face_front(L, cx, cy, a, b, seed + 130, mood='smile', blush=0.55, eye_y=0.2, eye_sep=0.45, eye_r=0.105, mouth_w=0.2)
    # 头发：双丫髻
    for s_ in (-1, 1):
        bun = ellipse_pts(cx + s_ * 31, cy - b * 0.98, 16, 15, 14, jit=0.05, seed=seed + 140 + s_)
        hair_mass(L, bun, None, seed + 140 + s_, strands=10, direction=90)
        line(L, [(cx + s_ * 31 - 14, cy - b * 0.76), (cx + s_ * 31, cy - b * 0.7), (cx + s_ * 31 + 14, cy - b * 0.76)], 3.5, K['stone'], 0.95, seed + 150 + s_, 0.2, 0, 0.4)
    hair_cap_front(L, cx, cy, a, b, seed + 160, fringe=0.52, side=0.3, puff=1.08, tuft=3)
    return L, (cx, foot)


@sprite
def girl():
    L, anc = girl_front_draw()
    sheet_save(L, 'girl_front', anc, 11)


@sprite
def girl_bowl_front():
    L, anc = girl_front_draw(bowl=True)
    cx, foot = anc
    top = foot - 340
    # 碗
    bx, by = cx, top + 196
    pts = [(bx - 24, by - 8), (bx + 24, by - 8), (bx + 18, by + 14), (bx + 8, by + 20), (bx - 8, by + 20), (bx - 18, by + 14)]
    garment(L, pts, hexc('#a7a9aa'), 205, shade=0.35, stain=0.25, flick=0.3, ink_w=1.9, wob=0.6)
    wash(L, [(bx - 24, by - 9), (bx + 24, by - 9), (bx + 22, by - 5), (bx - 22, by - 5)], hexc('#d8dad8'), op=0.9, wob=0.5, seed=206, smooth=1)
    for k, (dx, ph) in enumerate([(-8, 0), (2, 1.5), (11, 3.0)]):  # 热气
        pts_ = [(bx + dx, by - 10 - t * 7 + math.sin(t * 1.2 + ph) * 5) for t in range(6)]
        line(L, pts_, 3.2, hexc('#f1efe8'), 0.8, 210 + k, 0.4, 0.2, 0.8, w1=1.2)
    # 手
    for s_ in (-1, 1):
        hand(L, bx + s_ * 19, by + 5, math.pi * (0.5 if s_ == 1 else 0.5) - s_ * 0.9 + 0.0, 13, seed=220 + s_, kind='open', side=s_)
    sheet_save(L, 'girl_bowl_front', anc, 12)


# ───────────────────────── 4. 牧人 ─────────────────────────
TAN = hexc('#cc9d7b')


def beard_front(L, cx, cy, a, b, col, seed=0, length=1.42, w=1.0, mouth=True, strands=44):
    outer = [(cx - a * 0.98, cy + b * 0.02), (cx - a * 0.94 * w, cy + b * 0.55), (cx - a * 0.62 * w, cy + b * 1.0), (cx - a * 0.28 * w, cy + b * (length - 0.1)), (cx, cy + b * length),
             (cx + a * 0.28 * w, cy + b * (length - 0.1)), (cx + a * 0.62 * w, cy + b * 1.0), (cx + a * 0.94 * w, cy + b * 0.55), (cx + a * 0.98, cy + b * 0.02)]
    inner = [(cx + a * 0.8, cy + b * 0.25), (cx + a * 0.5, cy + b * 0.4), (cx + a * 0.26, cy + b * 0.5), (cx + a * 0.12, cy + b * 0.53), (cx, cy + b * 0.5), (cx - a * 0.12, cy + b * 0.53), (cx - a * 0.26, cy + b * 0.5),
             (cx - a * 0.5, cy + b * 0.4), (cx - a * 0.8, cy + b * 0.25)]
    p = beard(L, outer + inner, col, seed, strands=strands, direction=90)
    ink_outline(L, p, seed, w=1.4, op=0.45, gaps=0.5, color=INK, minseg=20, maxseg=60)
    fuzz_edge(L, p, mix(col, INK, 0.3), seed + 1, n=30, ln=(3, 8), op=0.6, w=1.2)
    if mouth:
        my = cy + b * 0.7
        wash(L, [(cx - a * 0.2, my - 1), (cx, my + 2.5), (cx + a * 0.2, my - 1), (cx, my - 0.5)], hexc('#7f4538'), op=0.9, wob=0.2, seed=seed + 2, smooth=2, tex_k=0, rim=0)
    # 髭：从人中向两边垂下
    for s_ in (-1, 1):
        brush(L, [(cx + s_ * 2, cy + b * 0.5), (cx + s_ * a * 0.2, cy + b * 0.55), (cx + s_ * a * 0.42, cy + b * 0.68), (cx + s_ * a * 0.5, cy + b * 0.82)], w0=a * 0.2, w1=2, color=mix(col, INK, 0.25), op=0.95, seed=seed + 10 + s_, taper=0.3, wob=0.4)
        brush(L, [(cx + s_ * 4, cy + b * 0.49), (cx + s_ * a * 0.22, cy + b * 0.52), (cx + s_ * a * 0.4, cy + b * 0.64)], w0=1.5, color=mix(col, hexc('#efe9dc'), 0.6), op=0.7, seed=seed + 20 + s_, taper=0.4, wob=0.3)


def felt_hat_front(L, cx, yh, a, seed=0, col=None, band=None):
    """毡帽（正面）：圆顶 + 翻起的宽帽檐（皮毛边）。yh 是额头顶的 y。"""
    col = K['gb'] if col is None else np.asarray(col, F)
    band = K['gb_dk'] if band is None else np.asarray(band, F)
    crown = [(cx - a * 1.0, yh + 12), (cx - a * 0.95, yh - 8), (cx - a * 0.7, yh - 28), (cx - a * 0.3, yh - 38), (cx, yh - 40), (cx + a * 0.3, yh - 38), (cx + a * 0.7, yh - 28), (cx + a * 0.95, yh - 8), (cx + a * 1.0, yh + 12), (cx, yh + 18)]
    cp, cm = garment(L, crown, col, seed, shade=0.4, stain=0.4, flick=0.8, streak=0.6, ink_w=2.3, smooth=1, edge_dk=0.2, rough=0.5,
                     folds=[[(cx - a * 0.5, yh - 26), (cx - a * 0.55, yh - 6)], [(cx + a * 0.4, yh - 30), (cx + a * 0.5, yh - 4)]])
    brim = [(cx - a * 1.22, yh + 2), (cx - a * 1.1, yh + 20), (cx - a * 0.6, yh + 24), (cx, yh + 26), (cx + a * 0.6, yh + 24), (cx + a * 1.1, yh + 20), (cx + a * 1.22, yh + 2),
            (cx + a * 1.04, yh + 6), (cx + a * 0.6, yh + 11), (cx, yh + 13), (cx - a * 0.6, yh + 11), (cx - a * 1.04, yh + 6)]
    bp, bm = garment(L, brim, band, seed + 7, shade=0.35, stain=0.4, flick=1.2, fdir=100, ink_w=2.0, smooth=1, edge_dk=0.25, rough=1.0)
    fuzz_edge(L, bp, mix(band, K['fur_lt'], 0.3), seed + 8, n=60, ln=(3, 7), op=0.8)
    # 顶上的小结
    wash(L, ellipse_pts(cx, yh - 42, 6, 4, 8), mix(col, K['gb_dk'], 0.5), op=1.0, wob=0.4, seed=seed + 9, smooth=1)


def boot_front(L, cx, y, w=46, h=62, col=None, seed=0, tip=1):
    """靴子：上翘的靴尖（正面看就是一个宽宽的鞋头）。y 是靴底。"""
    col = K['dark2'] if col is None else np.asarray(col, F)
    pts = [(cx - w * 0.42, y - h), (cx + w * 0.42, y - h), (cx + w * 0.46, y - h * 0.4), (cx + w * 0.55, y - h * 0.12), (cx + w * 0.4, y), (cx - w * 0.4, y), (cx - w * 0.55, y - h * 0.12), (cx - w * 0.46, y - h * 0.4)]
    garment(L, pts, col, seed, shade=0.35, stain=0.45, flick=0.5, ink_w=2.2, smooth=1, edge_dk=0.15,
            folds=[[(cx - w * 0.3, y - h * 0.8), (cx - w * 0.2, y - h * 0.5)], [(cx + w * 0.2, y - h * 0.9), (cx + w * 0.3, y - h * 0.4)]])
    brush(L, [(cx - w * 0.5, y - 3), (cx, y + 0.5), (cx + w * 0.5, y - 3)], w0=2.6, color=K['sole'], op=0.75, seed=seed + 1, taper=0.2, wob=0.4)


def herder_front_draw(cx=280, foot=690, H=540, seed=300):
    L = new_canvas(560, 740)
    top = foot - H
    cy, a, b = top + 82, 40, 43
    ground_shadow(L, cx, foot + 2, 190, 16, 0.28, seed)
    coat_c = mix(K['gb'], K['fur'], 0.3)
    for s_ in (-1, 1):
        boot_front(L, cx + s_ * 34, foot, 46, 62, K['dark2'], seed + s_)
    # 袍子（一整块，下摆外撇）
    cy0 = cy + b + 8
    rows = [(cy0 - 4, 26, 26), (cy0 + 2, 50, 50), (cy0 + 14, 66, 66), (cy0 + 40, 70, 69), (cy0 + 70, 66, 65), (cy0 + 96, 58, 58), (cy0 + 112, 60, 60), (cy0 + 160, 64, 66), (cy0 + 230, 72, 74), (cy0 + 300, 80, 82), (cy0 + 345, 84, 86)]
    coat = lathe(cx, rows)
    cp, cm = garment(L, coat, coat_c, seed + 10, shade=0.42, shade_dir=1, stain=0.5, worn=0.15, flick=0.9, fdir=84, streak=0.7, ink_w=2.5, hem_dirt=0.3, smooth=1, edge_dk=0.22, rough=1.2, scale=30,
                     folds=[[(cx - 20, cy0 + 120), (cx - 26, cy0 + 200), (cx - 34, cy0 + 300)], [(cx + 12, cy0 + 110), (cx + 18, cy0 + 200), (cx + 28, cy0 + 310)], [(cx - 46, cy0 + 150), (cx - 54, cy0 + 230), (cx - 62, cy0 + 320)],
                            [(cx + 4, cy0 + 20), (cx + 10, cy0 + 70), (cx + 8, cy0 + 105)]], fold_op=0.55)
    # 衣襟：从右肩斜到腰（右衽）
    line(L, [(cx - 22, cy0 + 8), (cx - 8, cy0 + 50), (cx + 24, cy0 + 100), (cx + 40, cy0 + 150), (cx + 44, cy0 + 280), (cx + 50, cy0 + 340)], 2.2, INKB, 0.7, seed + 11, 0.2, 0.2, 0.5)
    # 下摆毛边
    hem = [(cx - 84, cy0 + 322), (cx - 50, cy0 + 328), (cx, cy0 + 332), (cx + 50, cy0 + 330), (cx + 86, cy0 + 324), (cx + 86, cy0 + 348), (cx + 40, cy0 + 350), (cx, cy0 + 352), (cx - 42, cy0 + 351), (cx - 84, cy0 + 346)]
    hp, hm = garment(L, hem, K['fur_lt'], seed + 12, shade=0.3, stain=0.35, flick=1.4, fdir=95, ink_w=1.8, smooth=1, rough=1.4, edge_dk=0.15)
    fuzz_edge(L, hp, K['fur'], seed + 13, n=90, ln=(3, 8), op=0.75)
    # 脖子 + 毛领
    neck(L, cx, cy + b - 10, cy0 + 8, 30, seed + 20, skin=TAN)
    fp = [(cx - 40, cy0 - 6), (cx - 54, cy0 + 16), (cx - 20, cy0 + 56), (cx, cy0 + 70), (cx + 20, cy0 + 56), (cx + 54, cy0 + 16), (cx + 40, cy0 - 6), (cx + 26, cy0 + 2), (cx + 10, cy0 + 34), (cx, cy0 + 40), (cx - 10, cy0 + 34), (cx - 26, cy0 + 2)]
    fp_, fm_ = garment(L, fp, K['fur_lt'], seed + 21, shade=0.35, stain=0.4, flick=1.6, fdir=70, ink_w=1.8, smooth=1, rough=1.2)
    fuzz_edge(L, fp_, K['fur'], seed + 22, n=70, ln=(3, 8), op=0.8)
    # 腰带：灰蓝的布腰带 + 结
    by_ = cy0 + 104
    belt = [(cx - 62, by_ - 12), (cx - 20, by_ - 8), (cx + 20, by_ - 8), (cx + 62, by_ - 12), (cx + 64, by_ + 12), (cx + 20, by_ + 16), (cx - 20, by_ + 16), (cx - 64, by_ + 12)]
    garment(L, belt, K['blue_dk'] * 0.9 + 0.04, seed + 30, shade=0.35, stain=0.45, flick=0.6, fdir=10, ink_w=2.0, smooth=1, rough=0.8)
    line(L, [(cx - 60, by_ - 2), (cx, by_ + 3), (cx + 60, by_ - 2)], 1.4, INK, 0.4, seed + 31, 0.3, 0.3, 0.5)
    brush(L, [(cx + 8, by_ + 4), (cx + 18, by_ + 30), (cx + 14, by_ + 62)], w0=9, w1=5, color=K['blue_dk'], op=0.95, seed=seed + 32, taper=0.15, wob=0.8, dry=0.1)
    brush(L, [(cx + 10, by_ + 4), (cx - 2, by_ + 28), (cx + 2, by_ + 52)], w0=8, w1=4, color=K['blue_dk'] * 0.85, op=0.95, seed=seed + 33, taper=0.15, wob=0.8, dry=0.1)
    # 补丁
    patch(L, cx - 40, cy0 + 220, 28, 24, K['linen'], seed + 40, ang=0.1)
    patch(L, cx + 46, cy0 + 170, 22, 20, K['gb_lt'], seed + 41, ang=-0.15)
    # 袖子
    for i, s_ in enumerate((-1, 1)):
        sh, el, wr = (cx + s_ * 58, cy0 + 22), (cx + s_ * 76, cy0 + 84), (cx + s_ * 72, cy0 + 150)
        ap = tube([sh, el, wr], 40, 34, cap0=0.9, cap1=0.0)
        shadow_on(L, cm, ap, -s_ * 6, 4, op=0.4)
        sleeve(L, [sh, el, wr], 38, 33, coat_c, seed + 50 + i, shade=0.45, stain=0.5, worn=0.1, flick=0.8, fdir=80, streak=0.5, shade_dir=1, ink_w=2.4, edge_dk=0.2, rough=1.0,
               folds=[[(el[0] - s_ * 10, el[1] - 12), (el[0] - s_ * 3, el[1] + 3), (el[0] - s_ * 11, el[1] + 14)], [(sh[0] - s_ * 4, sh[1] + 6), (el[0] - s_ * 3, el[1] - 20)]])
        # 毛袖口
        cuff = tube([(wr[0] - s_ * 3, wr[1] - 16), wr], 36, 36, cap=0.0)
        cpp, cmm = garment(L, cuff, K['fur_lt'], seed + 60 + i, shade=0.3, stain=0.4, flick=1.5, fdir=85, ink_w=1.7, smooth=1, rough=1.2)
        fuzz_edge(L, cpp, K['fur'], seed + 61 + i, n=40, ln=(3, 7), op=0.8)
        hand(L, wr[0], wr[1] + 2, math.pi / 2 + s_ * 0.1, 30, skin=TAN, seed=seed + 70 + i, kind='fist' if i == 0 else 'open', side=-s_)
    # 脸
    face_front(L, cx, cy, a, b, seed + 80, skin=TAN, mood='calm', blush=0.35, eye_y=0.02, eye_sep=0.45, eye_r=0.085, brow='soft', mouth_w=0.2, age=0.3)
    beard_front(L, cx, cy, a, b, mix(K['gb_lt'], hexc('#cfc8bc'), 0.45), seed + 90)
    felt_hat_front(L, cx, cy - b + 6, a, seed + 100)
    return L, (cx, foot)


@sprite
def herder():
    L, anc = herder_front_draw()
    sheet_save(L, 'herder_front', anc, 21)


# ───────────────────────── 2. 老婆婆 ─────────────────────────
GREY_HAIR = hexc('#cfcbc4')


def scarf_front(L, cx, cy, a, b, col, seed=0):
    """包头巾：从额头上方绕过头顶，在一侧打个结。"""
    pts = [(cx - a * 1.08, cy - b * 0.1), (cx - a * 1.0, cy - b * 0.72), (cx - a * 0.55, cy - b * 1.12), (cx, cy - b * 1.2), (cx + a * 0.55, cy - b * 1.12), (cx + a * 1.0, cy - b * 0.72), (cx + a * 1.08, cy - b * 0.1),
           (cx + a * 0.88, cy - b * 0.34), (cx + a * 0.5, cy - b * 0.58), (cx, cy - b * 0.66), (cx - a * 0.5, cy - b * 0.6), (cx - a * 0.88, cy - b * 0.34)]
    sp, sm = garment(L, pts, col, seed, shade=0.4, stain=0.4, worn=0.1, flick=0.8, ink_w=2.0, smooth=1, edge_dk=0.2, rough=0.8,
                     folds=[[(cx - a * 0.7, cy - b * 0.4), (cx - a * 0.2, cy - b * 0.9), (cx + a * 0.4, cy - b * 1.1)], [(cx + a * 0.3, cy - b * 0.55), (cx + a * 0.8, cy - b * 0.7)]])
    # 结 + 两个布角
    kx, ky = cx + a * 0.78, cy - b * 1.04
    wash(L, ellipse_pts(kx, ky, 9, 7, 10, jit=0.1, seed=seed), mix(col, K['blue_dk'], 0.3), op=1.0, wob=0.5, seed=seed + 1, smooth=1)
    for k, (dx, dy) in enumerate([(14, -6), (11, 12)]):
        brush(L, [(kx, ky), (kx + dx * 0.6, ky + dy * 0.4), (kx + dx, ky + dy)], w0=8, w1=3, color=col, op=0.95, seed=seed + 5 + k, taper=0.2, wob=0.5)
        line(L, [(kx, ky + 1), (kx + dx * 0.6, ky + dy * 0.4 + 1), (kx + dx, ky + dy + 1)], 1.5, INKB, 0.6, seed + 8 + k, 0.4, 0, 0.3)


def white_cloth(L, x, y, w, h, seed=0, tilt=0.0):
    """一块素白的巾，从手里垂下来。(x,y) 是上沿中点。"""
    pts = [(x - w * 0.5, y), (x + w * 0.5, y), (x + w * 0.56, y + h * 0.5), (x + w * 0.48, y + h), (x + w * 0.2, y + h * 0.94), (x - w * 0.05, y + h * 1.0), (x - w * 0.3, y + h * 0.95), (x - w * 0.52, y + h * 0.98), (x - w * 0.55, y + h * 0.5)]
    return garment(L, pts, K['white'] * 0.97, seed, shade=0.35, stain=0.3, worn=0.0, flick=0.5, ink_w=1.7, smooth=1, edge_dk=0.12, rough=1.0, dark=K['white_sh'] * 0.85, ink_op=0.7,
                   folds=[[(x - w * 0.2, y + 4), (x - w * 0.15, y + h * 0.5), (x - w * 0.22, y + h * 0.9)], [(x + w * 0.2, y + 3), (x + w * 0.24, y + h * 0.5), (x + w * 0.18, y + h * 0.88)]], fold_op=0.45)


def oldwoman_front_draw(cx=210, foot=400, H=330, seed=400):
    L = new_canvas(420, 440)
    T = foot - H
    cy, a, b = T + 52, 31, 37
    ground_shadow(L, cx, foot + 2, 110, 12, 0.28, seed)
    dark_c = hexc('#5a5249')
    # 裤脚 + 鞋
    for s_ in (-1, 1):
        leg(L, [(cx + s_ * 17, foot - 80), (cx + s_ * 18, foot - 50), (cx + s_ * 19, foot - 18)], 28, 22, dark_c, seed + s_, shade=0.4, stain=0.5, flick=0.5, ink_w=2.0, edge_dk=0.2, rough=1.0)
        leg(L, [(cx + s_ * 19, foot - 36), (cx + s_ * 19, foot - 17)], 24, 24, K['linen'], seed + 5 + s_, shade=0.25, stain=0.35, flick=0.3, ink_w=1.5)
        shoe_front(L, cx + s_ * 21, foot, 38, 19, K['dark'], seed + 10 + s_)
    # 长衣：深灰蓝粗布，下摆过膝
    jy = cy + b + 8
    rows = [(jy - 6, 13, 13), (jy - 1, 26, 26), (jy + 8, 42, 42), (jy + 24, 46, 46), (jy + 52, 43, 43), (jy + 90, 46, 47), (jy + 130, 50, 52), (jy + 150, 53, 55), (jy + 156, 54, 56)]
    robe_c = hexc('#4c566d')
    rp, rm = garment(L, lathe(cx, rows), robe_c, seed + 20, shade=0.42, stain=0.5, worn=0.15, flick=0.8, fdir=84, streak=0.6, ink_w=2.4, hem_dirt=0.3, smooth=1, edge_dk=0.22, rough=1.3,
                     folds=[[(cx - 14, jy + 70), (cx - 18, jy + 105), (cx - 22, jy + 146)], [(cx + 16, jy + 66), (cx + 20, jy + 100), (cx + 26, jy + 148)], [(cx - 36, jy + 80), (cx - 40, jy + 110), (cx - 46, jy + 148)]])
    neck(L, cx, cy + b - 10, jy + 4, 17, seed + 30, skin=K['skin_old'])
    collar(L, cx, jy - 2, 24, 22, K['white'] * 0.95, seed + 31)
    # 腰带
    by_ = jy + 54
    garment(L, [(cx - 44, by_ - 5), (cx + 44, by_ - 5), (cx + 46, by_ + 6), (cx - 46, by_ + 6)], K['gb_lt'], seed + 40, shade=0.3, stain=0.4, flick=0.3, fdir=0, ink_w=1.8, smooth=1, rough=0.6)
    patch(L, cx - 24, jy + 84, 20, 18, K['gb'], seed + 41, ang=0.1)
    patch(L, cx + 28, jy + 30, 15, 13, K['linen'], seed + 42, ang=-0.15)
    # 手里的白巾（先画布，再画手）
    white_cloth(L, cx + 2, by_ + 12, 40, 50, seed + 50)
    # 袖子：大袖口垂在身前，两手在腹前拢着
    for i, s_ in enumerate((-1, 1)):
        sh, el, wr = (cx + s_ * 38, jy + 12), (cx + s_ * 52, jy + 48), (cx + s_ * 16, by_ + 12)
        ap = tube([sh, el, wr], 28, 26, cap0=0.9, cap1=0.2)
        shadow_on(L, rm, ap, -s_ * 4, 3, op=0.4)
        sleeve(L, [sh, el, wr], 28, 26, robe_c, seed + 60 + i, cuff=10, cuff_col=K['gb_lt'], shade=0.42, stain=0.5, worn=0.1, flick=0.7, streak=0.4, edge_dk=0.2, rough=1.0,
               folds=[[(el[0] - s_ * 7, el[1] - 10), (el[0] - s_ * 2, el[1] + 2), (el[0] - s_ * 8, el[1] + 12)]])
    for i, s_ in enumerate((-1, 1)):
        hand(L, cx + s_ * 9, by_ + 6, math.pi / 2 + s_ * 0.5, 17, skin=K['skin_old'], seed=seed + 70 + i, kind='open', side=-s_)
    # 脸 + 头巾 + 白发
    face_front(L, cx, cy, a, b, seed + 80, skin=K['skin_old'], mood='calm', blush=0.25, eye_y=0.12, eye_sep=0.44, eye_r=0.09, brow='soft', mouth_w=0.18, age=0.9)
    # 额前的白发（中分）
    for s_ in (-1, 1):
        hp = [(cx + s_ * 2, cy - b * 0.72), (cx + s_ * a * 0.55, cy - b * 0.68), (cx + s_ * a * 0.92, cy - b * 0.28), (cx + s_ * a * 1.02, cy + b * 0.28), (cx + s_ * a * 0.88, cy + b * 0.2), (cx + s_ * a * 0.78, cy - b * 0.08), (cx + s_ * a * 0.4, cy - b * 0.42)]
        hair_mass(L, hp, GREY_HAIR, seed + 90 + s_, strands=10, direction=80, wob=0.8, smooth=2, sheen=0.2)
    scarf_front(L, cx, cy, a, b, hexc('#66738f'), seed + 100)
    return L, (cx, foot)


@sprite
def oldwoman():
    L, anc = oldwoman_front_draw()
    sheet_save(L, 'oldwoman_front', anc, 31)


# ───────────────────────── 侧面零件 ─────────────────────────
def hair_cap_side(L, cx, cy, a, b, seed=0, col=None, fringe=0.45, nape=0.45, puff=1.1, back=1.0, tuft=0):
    """侧面（朝右）的头发：盖住头顶和后脑，额前一排刘海，鬓角垂到耳前。cx,cy,a,b 同 face_side。"""
    def P(x, y):
        return (cx + x * a, cy + y * b)
    pts = [P(0.9, -0.34), P(0.84, -0.62), P(0.55, -0.92 * puff), P(0.1, -1.1 * puff), P(-0.4, -1.0 * puff), P(-0.82 * back, -0.7), P(-1.0 * back, -0.2), P(-1.0 * back, nape * 0.8), P(-0.78 * back, nape),
           P(-0.5, nape * 0.6), P(-0.3, 0.2), P(-0.12, 0.1), P(-0.1, -0.2), P(0.18, -0.38), P(0.5, -fringe + 0.02), P(0.72, -fringe + 0.1)]
    p = hair_mass(L, pts, col, seed, strands=int(a * 0.5), direction=100)
    ink_outline(L, p, seed, w=1.6, op=0.5, gaps=0.35, color=INK, minseg=30, maxseg=90)
    return p


def arm_side(L, path, w0, w1, col, seed, cuff=0, cuff_col=None, back=False, **kw):
    kw.setdefault('shade', 0.4)
    kw.setdefault('stain', 0.4)
    c = col if not back else mix(col, INK, 0.28)
    return sleeve(L, path, w0, w1, c, seed, cuff=cuff, cuff_col=cuff_col, **kw)


def girl_side_draw(cx=230, foot=400, H=340, seed=500):
    L = new_canvas(460, 440)
    T = foot - H
    cy, a, b = T + 76, 36, 48
    hx = cx + 6                      # 头略向前
    ground_shadow(L, cx + 4, foot + 2, 110, 13, 0.28, seed)
    legcol = mix(K['white_sh'], K['gb'], 0.5)
    # 后腿 / 前腿
    for k, (dx0, dx1, back) in enumerate([(-5, -7, True), (6, 12, False)]):
        col = mix(legcol, INK, 0.2) if back else legcol
        leg(L, [(cx + dx0, foot - 112), (cx + (dx0 + dx1) / 2, foot - 60), (cx + dx1, foot - 14)], 19, 16, col, seed + k, shade=0.38, stain=0.42, flick=0.4, ink_w=1.9)
        leg(L, [(cx + dx1, foot - 33), (cx + dx1, foot - 14)], 21, 20, K['linen_lt'] if not back else mix(K['linen_lt'], INK, 0.2), seed + 5 + k, shade=0.2, stain=0.3, flick=0.2, ink_w=1.4)
        shoe_side(L, cx + dx1 + 5, foot, 44, 18, K['dark'], seed + 10 + k, snow=0.9)
    jy = cy + b + 8
    # 远侧的手臂（躲在身后，颜色更暗）
    arm_side(L, [(cx + 4, jy + 14), (cx + 9, jy + 40), (cx + 15, jy + 62)], 20, 17, K['blue'], seed + 20, cuff=8, back=True, ink_w=2.0)
    hand(L, cx + 15, jy + 63, math.pi / 2 - 0.3, 14, seed=seed + 21, kind='open', side=1)
    # 裙
    sy = jy + 50
    sk = lathe(cx, [(sy, 25, 26), (sy + 14, 30, 33), (sy + 30, 36, 39), (sy + 50, 42, 46), (sy + 57, 41, 47)])
    garment(L, sk, K['red'], seed + 22, shade=0.36, shade_dir=1, stain=0.34, worn=0.1, flick=0.5, fdir=75, ink_w=2.0, hem_dirt=0.3, dark=hexc('#5e1d18'), light=hexc('#d09a8c'), smooth=1, edge_dk=0.2, rough=1.0,
            folds=[[(cx - 10, sy + 12), (cx - 16, sy + 34), (cx - 24, sy + 52)], [(cx + 8, sy + 12), (cx + 12, sy + 34), (cx + 20, sy + 52)]])
    # 上衣
    jk = lathe(cx, [(jy - 6, 11, 11), (jy - 1, 17, 18), (jy + 8, 24, 25), (jy + 22, 28, 30), (jy + 42, 25, 28), (jy + 56, 26, 29), (jy + 66, 30, 33)])
    jp, jm = garment(L, jk, K['blue'], seed + 30, shade=0.4, shade_dir=1, stain=0.42, worn=0.12, flick=0.6, ink_w=2.3, hem_dirt=0.2, smooth=1, edge_dk=0.25, rough=1.0,
                     folds=[[(cx - 4, jy + 34), (cx - 8, jy + 52), (cx - 6, jy + 64)]])
    by_ = jy + 42
    brush(L, [(cx - 25, by_ - 1), (cx, by_ + 3), (cx + 27, by_ - 1)], w0=5, color=K['rope'], op=0.95, seed=seed + 31, taper=0.2, wob=0.6)
    brush(L, [(cx + 10, by_ + 3), (cx + 16, by_ + 18), (cx + 12, by_ + 30)], w0=3.0, color=K['rope'], op=0.9, seed=seed + 32, taper=0.3, wob=0.6)
    patch(L, cx - 8, jy + 56, 15, 13, K['linen'], seed + 33, ang=0.1, clipmask=jm)
    neck(L, cx + 4, cy + b - 14, jy + 4, 24, seed + 40)
    # 近侧的手臂（垂在身侧，略向前）
    path = [(cx - 2, jy + 13), (cx + 1, jy + 40), (cx + 6, jy + 68)]
    ap = tube(path, 24, 21, cap0=0.9, cap1=0.0)
    shadow_on(L, jm, ap, -4, 3, op=0.4)
    arm_side(L, path, 24, 21, K['blue'], seed + 41, cuff=9, ink_w=2.2, edge_dk=0.2, folds=[[(path[1][0] - 7, path[1][1] - 8), (path[1][0], path[1][1] + 2), (path[1][0] - 7, path[1][1] + 12)]])
    hand(L, path[-1][0], path[-1][1] + 2, math.pi / 2 - 0.2, 15, seed=seed + 42, kind='open', side=1)
    # 头
    face_side(L, hx, cy, a, b, seed + 50, mood='smile', blush=0.5, nose=1.4, eye_y=0.2, chin=0.95)
    for bx, by2, r_ in [(hx - 14, cy - b * 1.0, 15), (hx + 10, cy - b * 1.02 - 1, 14)]:
        bun = ellipse_pts(bx, by2, r_, r_ - 1, 14, jit=0.05, seed=seed + 60 + int(bx))
        hair_mass(L, bun, None, seed + 60 + int(bx), strands=10, direction=90)
        line(L, [(bx - 12, by2 + r_ * 0.75), (bx, by2 + r_ * 0.9), (bx + 12, by2 + r_ * 0.75)], 3.2, K['stone'], 0.95, seed + 70 + int(bx), 0.2, 0, 0.4)
    hair_cap_side(L, hx, cy, a, b, seed + 80, fringe=0.28, nape=0.5, puff=1.04, back=1.1)
    return L, (cx + 4, foot)


@sprite
def girl_side():
    L, anc = girl_side_draw()
    sheet_save(L, 'girl_side', anc, 13)


# ───────────────────────── 牧人 侧面 ─────────────────────────
def boot_side(L, cx, y, w=70, h=64, col=None, seed=0):
    """靴子（侧面，靴尖朝右、微微上翘）。cx 是脚踝中线，y 是靴底。"""
    col = K['dark2'] if col is None else np.asarray(col, F)
    pts = [(cx - 0.2 * w, y - h), (cx + 0.24 * w, y - h), (cx + 0.26 * w, y - 0.4 * h), (cx + 0.5 * w, y - 0.28 * h), (cx + 0.66 * w, y - 0.36 * h), (cx + 0.66 * w, y - 0.12 * h), (cx + 0.46 * w, y), (cx - 0.28 * w, y), (cx - 0.3 * w, y - 0.3 * h)]
    garment(L, pts, col, seed, shade=0.35, stain=0.45, flick=0.5, ink_w=2.2, smooth=1, edge_dk=0.15, folds=[[(cx - 0.05 * w, y - h * 0.8), (cx + 0.0 * w, y - h * 0.5)], [(cx + 0.2 * w, y - 0.38 * h), (cx + 0.1 * w, y - 0.2 * h)]])
    brush(L, [(cx - 0.28 * w, y - 2), (cx + 0.2 * w, y + 0.5), (cx + 0.64 * w, y - 0.1 * h)], w0=2.6, color=K['sole'], op=0.75, seed=seed + 1, taper=0.2, wob=0.4)


def beard_side(L, cx, cy, a, b, col, seed=0, length=1.4, strands=36):
    """侧面的络腮胡（脸朝右）：沿下颌从耳下包到下巴，嘴上一撇髭。"""
    def P(x, y):
        return (cx + x * a, cy + y * b)
    outer = [P(-0.1, -0.05), P(-0.62, 0.28), P(-0.66, 0.74), P(-0.2, 1.1), P(0.35, length), P(0.78, length - 0.12), P(0.98, 1.0), P(1.0, 0.66), P(0.98, 0.5)]
    inner = [P(0.72, 0.42), P(0.5, 0.36), P(0.25, 0.26), P(0.0, 0.06)]
    p = beard(L, outer + inner, col, seed, strands=strands, direction=95)
    ink_outline(L, p, seed, w=1.4, op=0.45, gaps=0.5, color=INK, minseg=20, maxseg=60)
    fuzz_edge(L, p, mix(col, INK, 0.3), seed + 1, n=26, ln=(3, 8), op=0.6, w=1.2)
    brush(L, [P(0.98, 0.5), P(0.82, 0.46), P(0.62, 0.52), P(0.5, 0.64)], w0=a * 0.2, w1=2, color=mix(col, INK, 0.25), op=0.95, seed=seed + 10, taper=0.3, wob=0.4)
    wash(L, [P(0.96, 0.62), P(0.86, 0.7), P(0.74, 0.64)], hexc('#7f4538'), op=0.85, wob=0.1, seed=seed + 3, smooth=2, tex_k=0, rim=0)
    return p


def herder_side_draw(cx=300, foot=690, H=540, seed=600):
    L = new_canvas(600, 740)
    T = foot - H
    cy, a, b = T + 82, 40, 43
    hx = cx + 10
    ground_shadow(L, cx + 8, foot + 2, 190, 16, 0.28, seed)
    coat_c = mix(K['gb'], K['fur'], 0.3)
    boot_side(L, cx - 14, foot, 72, 62, K['dark2'] * 0.8, seed + 1)
    boot_side(L, cx + 14, foot, 72, 62, K['dark2'], seed + 2)
    cy0 = cy + b + 8
    # 远侧的手臂
    sh, el, wr = (cx + 4, cy0 + 22), (cx + 22, cy0 + 82), (cx + 40, cy0 + 138)
    sleeve(L, [sh, el, wr], 36, 31, mix(coat_c, INK, 0.28), seed + 5, shade=0.4, stain=0.5, flick=0.6, ink_w=2.2, rough=1.0)
    hand(L, wr[0], wr[1] + 2, math.pi / 2 - 0.3, 28, skin=TAN * 0.85, seed=seed + 6, kind='open', side=1)
    # 袍子
    rows = [(cy0 - 4, 24, 26), (cy0 + 2, 42, 40), (cy0 + 14, 52, 50), (cy0 + 40, 56, 56), (cy0 + 70, 52, 58), (cy0 + 96, 50, 58), (cy0 + 112, 54, 58), (cy0 + 160, 58, 62), (cy0 + 230, 66, 68), (cy0 + 300, 74, 74), (cy0 + 345, 78, 78)]
    coat = lathe(cx, rows)
    cp, cm = garment(L, coat, coat_c, seed + 10, shade=0.42, shade_dir=1, stain=0.5, worn=0.15, flick=0.9, fdir=84, streak=0.7, ink_w=2.5, hem_dirt=0.3, smooth=1, edge_dk=0.22, rough=1.2, scale=30,
                     folds=[[(cx - 12, cy0 + 120), (cx - 18, cy0 + 200), (cx - 26, cy0 + 300)], [(cx + 22, cy0 + 110), (cx + 28, cy0 + 200), (cx + 38, cy0 + 310)], [(cx - 40, cy0 + 150), (cx - 48, cy0 + 230), (cx - 56, cy0 + 320)]], fold_op=0.55)
    hem = [(cx - 78, cy0 + 322), (cx, cy0 + 330), (cx + 78, cy0 + 324), (cx + 80, cy0 + 348), (cx, cy0 + 352), (cx - 80, cy0 + 346)]
    hp, hm = garment(L, hem, K['fur_lt'], seed + 12, shade=0.3, stain=0.35, flick=1.4, fdir=95, ink_w=1.8, smooth=1, rough=1.4, edge_dk=0.15)
    fuzz_edge(L, hp, K['fur'], seed + 13, n=80, ln=(3, 8), op=0.75)
    neck(L, hx - 4, cy + b - 10, cy0 + 8, 34, seed + 20, skin=TAN)
    # 毛领（侧面是一圈）
    fp = [(cx - 40, cy0 - 8), (cx - 48, cy0 + 12), (cx - 24, cy0 + 28), (cx + 20, cy0 + 34), (cx + 50, cy0 + 20), (cx + 52, cy0 - 4), (cx + 30, cy0 - 12), (cx, cy0 - 6)]
    fp_, fm_ = garment(L, fp, K['fur_lt'], seed + 21, shade=0.35, stain=0.4, flick=1.6, fdir=70, ink_w=1.8, smooth=1, rough=1.2)
    fuzz_edge(L, fp_, K['fur'], seed + 22, n=60, ln=(3, 8), op=0.8)
    by_ = cy0 + 104
    belt = [(cx - 54, by_ - 12), (cx + 56, by_ - 12), (cx + 60, by_ + 14), (cx - 56, by_ + 14)]
    garment(L, belt, K['blue_dk'] * 0.9 + 0.04, seed + 30, shade=0.35, stain=0.45, flick=0.6, fdir=10, ink_w=2.0, smooth=1, rough=0.8)
    brush(L, [(cx + 30, by_ + 4), (cx + 36, by_ + 30), (cx + 33, by_ + 62)], w0=9, w1=5, color=K['blue_dk'], op=0.95, seed=seed + 32, taper=0.15, wob=0.8, dry=0.1)
    patch(L, cx - 30, cy0 + 220, 26, 22, K['linen'], seed + 40, ang=0.1, clipmask=cm)
    # 近侧手臂
    sh, el, wr = (cx - 4, cy0 + 24), (cx + 8, cy0 + 86), (cx + 22, cy0 + 146)
    ap = tube([sh, el, wr], 38, 33, cap0=0.9, cap1=0.0)
    shadow_on(L, cm, ap, -5, 4, op=0.4)
    sleeve(L, [sh, el, wr], 38, 33, coat_c, seed + 50, shade=0.45, stain=0.5, worn=0.1, flick=0.8, fdir=80, streak=0.5, ink_w=2.4, edge_dk=0.2, rough=1.0,
           folds=[[(el[0] - 10, el[1] - 12), (el[0] - 3, el[1] + 3), (el[0] - 11, el[1] + 14)], [(sh[0] - 4, sh[1] + 6), (el[0] - 3, el[1] - 20)]])
    cuff = tube([(wr[0] - 3, wr[1] - 16), wr], 36, 36, cap=0.0)
    cpp, cmm = garment(L, cuff, K['fur_lt'], seed + 60, shade=0.3, stain=0.4, flick=1.5, fdir=85, ink_w=1.7, smooth=1, rough=1.2)
    fuzz_edge(L, cpp, K['fur'], seed + 61, n=40, ln=(3, 7), op=0.8)
    hand(L, wr[0], wr[1] + 2, math.pi / 2 - 0.2, 30, skin=TAN, seed=seed + 70, kind='fist', side=1)
    # 头
    face_side(L, hx, cy, a, b, seed + 80, skin=TAN, mood='calm', blush=0.3, nose=1.7, eye_y=0.02, chin=0.95, age=0.3, browr=1.05)
    beard_side(L, hx, cy, a, b, mix(K['gb_lt'], hexc('#cfc8bc'), 0.45), seed + 90, length=1.4)
    felt_hat_front(L, hx - 4, cy - b + 6, a, seed + 100)
    return L, (cx + 8, foot)


@sprite
def herder_side():
    L, anc = herder_side_draw()
    sheet_save(L, 'herder_side', anc, 22)
