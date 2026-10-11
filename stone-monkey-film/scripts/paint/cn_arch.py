"""cn_arch.py —— 城、塔、天、火山的专用笔法（Agent C）。

在 pt.py / cn.py 的墨线 + 透明水彩之上，加：
  · 青砖/条石的砖缝纹理 brick_surface，中式屋顶 eave_roof（瓦垄、瓦当、鸱吻、翘角、檐铃），斗拱 dougong，
    柱 column，门（铜钉）door_leaf，旗 banner，城墙 city_wall，城门楼 gate_tower，九层砖塔 pagoda_tier …
  · 水墨的云 cloud_mass（卷云纹、积墨），烟 smoke_trail，火山 volcano_cone，铜灯 bronze_lamp …
  · 灯光 / 火光不走夜色色带（会被压成靛蓝），而是在调色之后按“最终颜色”叠上去：LightMap + save2()。
约定同 cn.py：先用中性淡彩（A 调色盘）画明暗，夜色/光照/晨光由 grade 得到。
"""
import math, zlib
import numpy as np
import cv2
from ccommon import *   # noqa  (cn / pt / grade / save_plate / Canvas / BG / PREV …)

# ───────────────────────── 调色盘（中性淡彩，降过饱和度）─────────────────────────
A = {
    'brick': hexc('#8d9699'), 'brick_dk': hexc('#5d686d'), 'brick_lt': hexc('#adb4b4'),
    'tile': hexc('#657077'), 'tile_dk': hexc('#414c54'), 'tile_lt': hexc('#8a9498'),
    'red': hexc('#93726a'), 'red_dk': hexc('#5f4a45'), 'red_lt': hexc('#ad9086'),      # 土红灰（降饱和）
    'gold': hexc('#aa9f7c'), 'gold_dk': hexc('#7b7156'), 'gold_lt': hexc('#c9bf9f'),    # 灰金/土黄
    'wood': hexc('#7b6d60'), 'wood_dk': hexc('#4b4038'), 'wood_lt': hexc('#9d8f80'),
    'plank': hexc('#8a7c68'), 'plank_dk': hexc('#5d5143'),
    'blue': hexc('#6d7f96'), 'blue_dk': hexc('#46566c'), 'blue_lt': hexc('#98a7b8'),
    'cloth': hexc('#8b95a1'), 'cloth_dk': hexc('#59636f'),
    'paper': hexc('#efe8d8'), 'ink': INK,
    'earth': hexc('#9a8f78'), 'earth_dk': hexc('#6a604e'), 'earth_lt': hexc('#bdb398'),
    'slab': hexc('#a9aca6'), 'slab_dk': hexc('#6f7573'), 'slab_lt': hexc('#cdd0c8'),
    'basalt': hexc('#4a4f55'), 'basalt_dk': hexc('#2a2e33'), 'basalt_lt': hexc('#737a80'),
    'bronze': hexc('#7f8a7c'), 'bronze_dk': hexc('#4c564f'), 'bronze_lt': hexc('#aab3a2'),
    'cloud': hexc('#d9dbd8'), 'cloud_sh': hexc('#a2aab4'), 'cloud_dk': hexc('#6d7886'),
    'smoke': hexc('#5d6169'), 'smoke_dk': hexc('#2f3238'),
}


def _hash(a):
    """确定性的 0~1 哈希噪声。"""
    return np.mod(np.sin(np.asarray(a, np.float64) * 12.9898) * 43758.5453, 1.0).astype(F)


def ci(v):
    return int(round(v))


# ───────────────────────── 灯光 / 火光 ─────────────────────────
class LightMap:
    """一张 0~1 的发光蒙版：窗、灯笼、灯光。画完在调色之后按“最终色”叠到画布上（夜色里的窗是纸白，不被压成靛蓝）。"""

    def __init__(self, W, H):
        self.W, self.H = W, H
        self.m = np.zeros((H, W), np.uint8)

    def rect(self, x0, y0, x1, y1, v=1.0):
        cv2.rectangle(self.m, (ci(x0), ci(y0)), (ci(x1), ci(y1)), int(255 * v), -1)

    def poly(self, pts, v=1.0):
        cv2.fillPoly(self.m, [np.round(np.asarray(pts, F)).astype(np.int32)], int(255 * v), lineType=cv2.LINE_AA)

    def disc(self, x, y, r, v=1.0):
        cv2.circle(self.m, (ci(x), ci(y)), max(ci(r), 1), int(255 * v), -1, cv2.LINE_AA)

    def ellipse(self, x, y, rx, ry, v=1.0, ang=0):
        cv2.ellipse(self.m, (ci(x), ci(y)), (max(ci(rx), 1), max(ci(ry), 1)), ang, 0, 360, int(255 * v), -1, cv2.LINE_AA)

    def line(self, a, b, w=2, v=1.0):
        cv2.line(self.m, (ci(a[0]), ci(a[1])), (ci(b[0]), ci(b[1])), int(255 * v), max(ci(w), 1), cv2.LINE_AA)

    def lattice(self, x0, y0, x1, y1, nx=3, ny=4, v=1.0, bar=2, frame=3, diamond=False):
        """一扇窗：亮的纸 + 暗的窗棂（从亮里挖掉）。"""
        self.rect(x0, y0, x1, y1, v)
        bars = []
        for i in range(1, nx):
            xx = x0 + (x1 - x0) * i / nx
            bars.append(((xx, y0), (xx, y1)))
        for j in range(1, ny):
            yy = y0 + (y1 - y0) * j / ny
            bars.append(((x0, yy), (x1, yy)))
        for a, b in bars:
            self.line(a, b, bar, 0.0)
        self.line((x0, y0), (x1, y0), frame, 0.0)
        self.line((x0, y1), (x1, y1), frame, 0.0)
        self.line((x0, y0), (x0, y1), frame, 0.0)
        self.line((x1, y0), (x1, y1), frame, 0.0)

    def apply(self, C, color, op=0.95, halo=((10, 0.32), (36, 0.16), (110, 0.07)), core_blur=0.9):
        m = self.m.astype(F) / 255.0
        if m.max() <= 0:
            return
        core = cv2.GaussianBlur(m, (0, 0), core_blur) if core_blur > 0 else m
        # 光晕只用“填充”（不含窗棂的暗缝）
        filled = cv2.dilate(m, np.ones((5, 5), np.uint8))
        hm = np.zeros_like(m)
        for s, k in halo:
            hm += k * cv2.GaussianBlur(filled, (0, 0), s)
        a = np.clip(core * op + hm * (1 - core * 0.6), 0, 1).astype(F)
        C.over(0, C.h, 0, C.w, np.asarray(color, F), a)


def save2(name, L, variants=('night', 'lit'), gain=0.6, keep=0.15, lights=None, post=None, ext=None):
    """和 save_plate 一样，但多了“调色之后”的叠加：
    lights = [(LightMap, {'night': (色, op), 'lit': (色, op)}, halo)]；post(variant, C) 可以再画任意东西（火苗、金光、晨霞）。"""
    seed = zlib.crc32(name.encode()) % 1000
    watercolorize(L, seed=seed)
    ov = {}
    for v in variants:
        C = Canvas(L.w, L.h)
        C.rgb = (VAR[v](L.rgb, gain, keep) if v == 'night' else VAR[v](L.rgb)).astype(F)
        C.a = L.a.copy()
        for item in (lights or []):
            lm, cols = item[0], item[1]
            halo = item[2] if len(item) > 2 else ((10, 0.32), (36, 0.16), (110, 0.07))
            c = cols.get(v) or cols.get('night')
            if c is not None:
                lm.apply(C, c[0], c[1], halo)
        if post is not None:
            post(v, C)
        ov[v] = C
    save_plate(name, L, variants=variants, gain=gain, keep=keep, overrides=ov, wc=False, ext=ext)


WINDOW_LIGHT = {'night': (hexc('#EFE8D8'), 0.93), 'lit': (hexc('#f2eee2'), 0.85), 'dawn': (hexc('#f4ecdc'), 0.7), 'day': (hexc('#f2eee2'), 0.5)}


# ───────────────────────── 基础：矩形/墨线 ─────────────────────────
def rwash(L, x0, y0, x1, y1, color, op=1.0, wob=1.0, seed=0, tex_k=0.16, rim=0.14, rim_w=2.5, mask_mul=None):
    wash(L, rect(x0, y0, x1, y1), color, op=op, wob=wob, seed=seed, smooth=0, tex_k=tex_k, rim=rim, rim_w=rim_w, mask_mul=mask_mul)


def line(L, pts, w=2.6, op=0.75, color=INK, seed=0, dry=0.25, wob=0.7, taper=0.06, smooth=False):
    brush(L, pts, w0=w, color=color, op=op, seed=abs(int(seed)), wob=wob, taper=taper, dry=dry, smooth=smooth)


def boxline(L, x0, y0, x1, y1, w=2.6, op=0.7, seed=0, dry=0.25, color=INK, sides='tblr'):
    """方框的墨线，四条边各一笔，略微出头、错开——松动的画法。"""
    r = np.random.default_rng(seed)
    j = lambda: r.normal(0, 1.2)
    if 't' in sides:
        line(L, [(x0 - 2 + j(), y0 + j()), (x1 + 2 + j(), y0 + j())], w, op, color, seed + 1, dry)
    if 'b' in sides:
        line(L, [(x0 - 1 + j(), y1 + j()), (x1 + 1 + j(), y1 + j())], w, op, color, seed + 2, dry)
    if 'l' in sides:
        line(L, [(x0 + j(), y0 - 2 + j()), (x0 + j(), y1 + 2)], w, op, color, seed + 3, dry)
    if 'r' in sides:
        line(L, [(x1 + j(), y0 - 1), (x1 + j(), y1 + 2)], w, op, color, seed + 4, dry)


# ───────────────────────── 青砖 / 条石 ─────────────────────────
def brick_surface(L, x0, y0, x1, y1, col, bw=46, bh=19, seed=0, var=0.07, joint_op=0.42, joint_w=1.4, mask=None, op=1.0,
                  shade=0.10, stain=0.10, streak=0.10, jcol=None, relief=0.07, run=True):
    """一面砖墙：错缝的砖、每块砖深浅不一、砖缝是断续的细墨线、顶光的立体感、雨水的竖向污渍。"""
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    h, w = y1 - y0, x1 - x0
    if h <= 2 or w <= 2:
        return
    col = np.asarray(col, F)
    jcol = col * 0.42 if jcol is None else np.asarray(jcol, F)
    yy, xx = np.mgrid[0:h, 0:w].astype(F)
    xx += x0
    yy += y0
    n1 = fbm(h, w, seed + 3, 46, 3)
    n2 = fbm(h, w, seed + 4, 46, 3)
    xw = xx + (n1 - 0.5) * bw * 0.08
    yw = yy + (n2 - 0.5) * bh * 0.10
    v = yw / bh
    ri = np.floor(v)
    off = ((ri % 2) * 0.5 + _hash(ri * 1.9 + seed) * 0.08) * bw if run else 0.0
    u = (xw + off) / bw
    cj = np.floor(u)
    fu, fv = u - cj, v - ri
    rnd = _hash(ri * 17.31 + cj * 3.77 + seed * 0.37)
    rnd2 = _hash(ri * 5.13 + cj * 11.9 + seed * 0.91)
    tone = 1 + (rnd - 0.5) * 2 * var
    # 偶尔有一块特别深/浅的砖
    odd = (rnd2 > 0.93).astype(F) * 0.07 - (rnd2 < 0.06).astype(F) * 0.06
    tone = tone + odd
    jy = np.minimum(fv, 1 - fv) * bh      # 到横缝的距离
    jx = np.minimum(fu, 1 - fu) * bw      # 到竖缝的距离
    n3 = fbm(h, w, seed + 5, 22, 3)
    jw = joint_w * (0.7 + 0.8 * n3)
    jh = np.clip(1 - jy / jw, 0, 1)
    jv = np.clip(1 - jx / jw, 0, 1)
    j = np.maximum(jh, jv * 0.85)
    drop = smoothstep(0.30, 0.52, fbm(h, w, seed + 6, 60, 3))     # 有的地方砖缝淡到看不见
    j = j * (0.18 + 0.82 * drop)
    # 立体：砖的上沿受光，下沿背光
    top_l = np.clip(1 - (fv * bh) / 4.5, 0, 1) * relief
    bot_d = np.clip(1 - ((1 - fv) * bh) / 4.0, 0, 1) * relief * 1.1
    k = tone + top_l - bot_d
    big = fbm(h, w, seed + 7, 190, 4, 0.55, warp=40)
    k = k * (1 + (big - 0.5) * stain * 2)
    # 雨水的竖向污渍
    sk = fbm(max(h // 10, 6), w, seed + 8, 34, 3)
    sk = cv2.resize(sk, (w, h), interpolation=cv2.INTER_CUBIC)
    k = k * (1 - streak * smoothstep(0.55, 0.9, sk) * (0.5 + 0.5 * np.clip((yy - y0) / max(h, 1), 0, 1)))
    # 整面砖上深下浅 / 顶光
    gy = np.linspace(1 + shade, 1 - shade, h, dtype=F)[:, None]
    k = k * gy
    rgb = col * k[..., None]
    rgb = rgb * (1 - j[..., None] * joint_op) + jcol * (j[..., None] * joint_op)
    a = np.ones((h, w), F) * op if mask is None else (mask * op).astype(F)
    L.over(y0, y1, x0, x1, np.clip(rgb, 0, 1).astype(F), a)


def poly_brick(L, pts, col, **kw):
    """多边形里的砖面。"""
    r = poly_mask(np.asarray(pts, F), L.w, L.h, ss=2)
    if r is None:
        return
    y0, y1, x0, x1, m = r
    brick_surface(L, x0, y0, x1, y1, col, mask=m, **kw)


# ───────────────────────── 木作：柱、斗拱、窗、门 ─────────────────────────
def column(L, x, y0, y1, w, col=None, dk=None, lt=None, seed=0, base=True, op=1.0, taper=0.07, ink=0.8, base_h=None, grain_n=None):
    """一根柱子：上细下粗、右侧背光、左侧一条亮边、竖向木纹、柱础。y0 柱顶，y1 柱脚。"""
    col = A['red'] if col is None else np.asarray(col, F)
    dk = A['red_dk'] if dk is None else np.asarray(dk, F)
    lt = A['red_lt'] if lt is None else np.asarray(lt, F)
    r = np.random.default_rng(seed)
    tw = w * (1 - taper)
    poly = [(x - tw / 2, y0), (x + tw / 2, y0), (x + w / 2, y1), (x - w / 2, y1)]
    wash(L, poly, col, op=op, wob=0.8, seed=seed, smooth=0, tex_k=0.16, rim=0.10)
    wash(L, [(x + tw * 0.08, y0), (x + tw / 2, y0), (x + w / 2, y1), (x + w * 0.1, y1)], dk, op=0.5 * op, wob=0.8, seed=seed + 1, smooth=0, tex_k=0.1, rim=0.0)
    wash(L, [(x - tw * 0.40, y0), (x - tw * 0.2, y0), (x - w * 0.2, y1), (x - w * 0.40, y1)], lt, op=0.42 * op, wob=0.8, seed=seed + 2, smooth=0, tex_k=0.1, rim=0.0)
    n = grain_n if grain_n is not None else int((y1 - y0) / 12 * max(w / 30, 0.6))
    st = []
    for _ in range(n):
        t = r.random()
        yy = y0 + (y1 - y0) * t
        xx = x + r.uniform(-0.45, 0.45) * (tw + (w - tw) * t)
        ln = r.uniform(10, 34)
        st.append((xx, yy, xx + r.normal(0, 0.8), yy + ln, r.uniform(0.7, 1.5), r.uniform(0.15, 0.4) * op))
    flicks(L, st, color=dk * 0.6)
    line(L, [(x - tw / 2, y0), (x - w / 2, y1)], max(w * 0.07, 1.8), 0.7 * ink * op, seed=seed + 3, dry=0.3, wob=0.6)
    line(L, [(x + tw / 2, y0), (x + w / 2, y1)], max(w * 0.08, 2.0), 0.8 * ink * op, seed=seed + 4, dry=0.2, wob=0.6)
    if base:
        bh = base_h or w * 0.55
        bw_ = w * 1.5
        pts = [(x - bw_ / 2, y1 + bh * 0.1), (x - bw_ * 0.42, y1 - bh * 0.7), (x + bw_ * 0.42, y1 - bh * 0.7), (x + bw_ / 2, y1 + bh * 0.1)]
        wash(L, pts, A['slab'], op=op, wob=0.8, seed=seed + 5, smooth=0, tex_k=0.18, rim=0.18)
        wash(L, [(x + bw_ * 0.05, y1 - bh * 0.7), (x + bw_ * 0.42, y1 - bh * 0.7), (x + bw_ / 2, y1 + bh * 0.1), (x + bw_ * 0.05, y1 + bh * 0.1)], A['slab_dk'], op=0.45 * op, wob=0.8, seed=seed + 6, smooth=0, rim=0.0)
        line(L, [(x - bw_ / 2, y1 + bh * 0.1), (x - bw_ * 0.42, y1 - bh * 0.7), (x + bw_ * 0.42, y1 - bh * 0.7), (x + bw_ / 2, y1 + bh * 0.1), (x - bw_ / 2, y1 + bh * 0.1)], max(w * 0.07, 1.8), 0.6 * op, seed=seed + 7, dry=0.3)


def dougong(L, x0, x1, y, h, pitch=40, col=None, dk=None, lt=None, seed=0, op=1.0):
    """斗拱的简化：下面一道额枋，上面一排“坐斗 + 层层出挑的拱 + 小升”，每组之间是暗的垫拱板。(y 是上沿，h 是总高)"""
    col = A['red'] if col is None else np.asarray(col, F)
    dk = A['red_dk'] if dk is None else np.asarray(dk, F)
    lt = A['red_lt'] if lt is None else np.asarray(lt, F)
    r = np.random.default_rng(seed)
    beam_h = h * 0.42
    by0 = y + h - beam_h
    # 垫拱板（暗）
    rwash(L, x0, y, x1, by0, dk * 0.75, op=0.85 * op, wob=0.7, seed=seed, tex_k=0.1, rim=0.0)
    # 额枋
    rwash(L, x0, by0, x1, y + h, col, op=op, wob=0.8, seed=seed + 1, tex_k=0.14, rim=0.1)
    rwash(L, x0, by0, x1, by0 + beam_h * 0.28, lt, op=0.4 * op, wob=0.6, seed=seed + 2, tex_k=0.1, rim=0.0)
    rwash(L, x0, y + h - beam_h * 0.3, x1, y + h, dk, op=0.45 * op, wob=0.6, seed=seed + 3, tex_k=0.1, rim=0.0)
    line(L, [(x0, by0), (x1, by0)], 2.0, 0.6 * op, seed=seed + 4, dry=0.3)
    line(L, [(x0, y + h), (x1, y + h)], 2.4, 0.7 * op, seed=seed + 5, dry=0.25)
    n = max(int((x1 - x0) / pitch), 1)
    pw = (x1 - x0) / n
    uh = by0 - y
    for i in range(n):
        cx = x0 + pw * (i + 0.5)
        # 坐斗
        dw, dh = pw * 0.30, uh * 0.30
        pts = [(cx - dw / 2, by0 - dh), (cx + dw / 2, by0 - dh), (cx + dw * 0.4, by0), (cx - dw * 0.4, by0)]
        wash(L, pts, lt, op=op, wob=0.5, seed=seed + 10 + i, smooth=0, tex_k=0.1, rim=0.12)
        # 第一层拱
        aw, ah = pw * 0.78, uh * 0.16
        rwash(L, cx - aw / 2, by0 - dh - ah, cx + aw / 2, by0 - dh, col, op=op, wob=0.4, seed=seed + 40 + i, tex_k=0.1, rim=0.12)
        # 小升
        for s_ in (-1, 1):
            sw, sh = pw * 0.14, uh * 0.13
            rwash(L, cx + s_ * aw * 0.36 - sw / 2, by0 - dh - ah - sh, cx + s_ * aw * 0.36 + sw / 2, by0 - dh - ah, lt, op=0.9 * op, wob=0.4, seed=seed + 70 + i * 2 + int(s_ > 0), tex_k=0.08, rim=0.1)
        # 第二层拱（更宽）
        aw2, ah2 = pw * 0.98, uh * 0.15
        yy2 = by0 - dh - ah - uh * 0.13
        rwash(L, cx - aw2 / 2, yy2 - ah2, cx + aw2 / 2, yy2, col, op=op, wob=0.4, seed=seed + 100 + i, tex_k=0.1, rim=0.12)
        rwash(L, cx - aw2 / 2, yy2 - ah2 * 0.35, cx + aw2 / 2, yy2, dk, op=0.35 * op, wob=0.4, seed=seed + 130 + i, tex_k=0.05, rim=0.0)
        line(L, [(cx - aw2 / 2, yy2 - ah2), (cx + aw2 / 2, yy2 - ah2)], 1.4, 0.45 * op, seed=seed + 160 + i, dry=0.3)
        # 昂：一道斜挑
        line(L, [(cx, by0 - dh * 0.4), (cx + pw * 0.22, by0 - dh - ah - uh * 0.28)], 1.6, 0.4 * op, seed=seed + 190 + i, dry=0.2)
    # 门屏两端的收口
    line(L, [(x0, y), (x0, y + h)], 2.0, 0.55 * op, seed=seed + 6, dry=0.3)
    line(L, [(x1, y), (x1, y + h)], 2.0, 0.55 * op, seed=seed + 7, dry=0.3)


def lattice_panel(L, x0, y0, x1, y1, nx=3, ny=5, wood=None, paper=None, seed=0, op=1.0, lm=None, light=1.0, diamond=False, bar=2.4):
    """格扇/窗：纸的底 + 窗棂。lm 是 LightMap（夜里窗是亮的）。"""
    wood = A['wood_dk'] if wood is None else np.asarray(wood, F)
    paper = A['paper'] * 0.9 if paper is None else np.asarray(paper, F)
    rwash(L, x0, y0, x1, y1, paper, op=op, wob=0.6, seed=seed, tex_k=0.1, rim=0.1)
    if lm is not None:
        lm.lattice(x0 + 1, y0 + 1, x1 - 1, y1 - 1, nx, ny, v=light, bar=ci(bar), frame=ci(bar + 1.5))
    for i in range(1, nx):
        xx = x0 + (x1 - x0) * i / nx
        line(L, [(xx, y0), (xx, y1)], bar, 0.8 * op, wood, seed + i, dry=0.1, wob=0.4)
    for j in range(1, ny):
        yy = y0 + (y1 - y0) * j / ny
        line(L, [(x0, yy), (x1, yy)], bar, 0.8 * op, wood, seed + 10 + j, dry=0.1, wob=0.4)
    if diamond:
        for i in range(nx):
            for j in range(ny):
                cx, cy = x0 + (x1 - x0) * (i + 0.5) / nx, y0 + (y1 - y0) * (j + 0.5) / ny
                dw, dh = (x1 - x0) / nx * 0.3, (y1 - y0) / ny * 0.3
                line(L, [(cx - dw, cy), (cx, cy - dh), (cx + dw, cy), (cx, cy + dh), (cx - dw, cy)], 1.2, 0.5 * op, wood, seed + 30 + i * 9 + j, dry=0.0, wob=0.2)
    boxline(L, x0, y0, x1, y1, bar + 1.6, 0.9 * op, seed + 99, 0.1, wood)


def door_leaf(L, x0, y0, x1, y1, seed=0, col=None, dk=None, stud_rows=7, stud_cols=6, op=1.0, studs=True, bands=3):
    """一扇厚木门：竖向的木板拼缝、横向的铁箍、铜钉（灰金）。"""
    col = A['wood'] * 0.78 if col is None else np.asarray(col, F)
    dk = A['wood_dk'] if dk is None else np.asarray(dk, F)
    r = np.random.default_rng(seed)
    rwash(L, x0, y0, x1, y1, col, op=op, wob=0.8, seed=seed, tex_k=0.18, rim=0.14)
    w = x1 - x0
    npl = max(int(w / 20), 3)
    for i in range(1, npl):
        xx = x0 + w * i / npl + r.normal(0, 0.8)
        line(L, [(xx, y0 + 4), (xx, y1 - 2)], 1.5, 0.5 * op, INK, seed + i, dry=0.3, wob=0.5)
    st = []
    for _ in range(int(w * (y1 - y0) / 700)):
        xx = r.uniform(x0 + 3, x1 - 3)
        yy = r.uniform(y0, y1 - 20)
        st.append((xx, yy, xx + r.normal(0, 0.6), yy + r.uniform(12, 40), r.uniform(0.7, 1.4), r.uniform(0.15, 0.35) * op))
    flicks(L, st, color=dk)
    # 铁箍
    for k in range(bands):
        yy = y0 + (y1 - y0) * (k + 0.5) / bands
        rwash(L, x0, yy - 7, x1, yy + 7, dk * 0.8, op=0.75 * op, wob=0.5, seed=seed + 50 + k, tex_k=0.08, rim=0.1)
    if studs:
        for rr in range(stud_rows):
            for cc in range(stud_cols):
                sx = x0 + w * (cc + 0.5) / stud_cols
                sy = y0 + 24 + (y1 - y0 - 48) * rr / max(stud_rows - 1, 1)
                rad = 4.6
                dots(L, [(sx + 0.8, sy + 1.2, rad)], dk * 0.6, op=0.7)
                dots(L, [(sx, sy, rad - 0.8)], A['gold'] * 0.95, op=op)
                dots(L, [(sx - 1.2, sy - 1.4, 1.4)], A['gold_lt'], op=0.8 * op)
    boxline(L, x0, y0, x1, y1, 3.4, 0.85 * op, seed + 77, 0.2)


def banner(L, x, y_top, pole_h, fl, fh, seed=0, col=None, dk=None, trim=None, wave=14, cycles=2.2, phase=0.0, dirn=1, op=1.0, tail=True, pole_w=4.5):
    """旗：一根杆，布旗在风里扬（波浪的上下沿 + 按折面深浅的色条 + 燕尾 + 灰金的边）。dirn=1 向右飘。"""
    col = A['cloth'] if col is None else np.asarray(col, F)
    dk = A['cloth_dk'] if dk is None else np.asarray(dk, F)
    trim = A['gold'] if trim is None else np.asarray(trim, F)
    r = np.random.default_rng(seed)
    ya = y_top + pole_h * 0.04
    # 杆
    line(L, [(x, y_top + pole_h), (x + 1, y_top)], pole_w, 0.85 * op, A['wood_dk'], seed, dry=0.1, wob=0.5, taper=0.03)
    dots(L, [(x + 1, y_top - 2, pole_w * 0.9)], A['gold_dk'], op=0.9 * op)
    n = 26
    ss = np.linspace(0, 1, n + 1)
    amp = lambda s: wave * (0.15 + 0.85 * s)
    top = [(x + dirn * s * fl, ya + amp(s) * math.sin(2 * math.pi * cycles * s + phase) + 6 * s) for s in ss]
    bot = [(x + dirn * s * fl, ya + fh + amp(s) * math.sin(2 * math.pi * cycles * s + phase + 0.45) + 6 * s) for s in ss]
    for i in range(n):
        t = 0.5 + 0.5 * math.cos(2 * math.pi * cycles * (ss[i] + ss[i + 1]) / 2 + phase)   # 折面的明暗
        c = mix(col, dk, 0.55 * (1 - t) + 0.05)
        poly = [top[i], top[i + 1], bot[i + 1], bot[i]]
        if tail and i == n - 1:
            notch = (top[-1][0] - dirn * fl * 0.2, (top[-1][1] + bot[-1][1]) / 2)
            poly = [top[i], top[i + 1], notch, bot[i + 1], bot[i]]
        wash(L, poly, c, op=op, wob=0.4, seed=seed + i, smooth=0, tex_k=0.1, rim=0.0)
    if tail:
        notch = (top[-1][0] - dirn * fl * 0.2, (top[-1][1] + bot[-1][1]) / 2)
        line(L, [top[-1], notch, bot[-1]], 2.0, 0.6 * op, INK, seed + 8, dry=0.3)
    line(L, top, 2.4, 0.7 * op, INK, seed + 3, dry=0.2, wob=0.5, taper=0.1, smooth=True)
    line(L, bot, 2.4, 0.65 * op, INK, seed + 4, dry=0.25, wob=0.5, taper=0.1, smooth=True)
    # 灰金的镶边（沿上沿一条细线）
    brush(L, [(p[0], p[1] + 5) for p in top], w0=2.4, color=trim, op=0.55 * op, seed=seed + 5, wob=0.5, taper=0.1, dry=0.2)
    line(L, [top[0], bot[0]], 2.4, 0.75 * op, INK, seed + 6)
    line(L, [top[-1], bot[-1]], 2.0, 0.6 * op, INK, seed + 7, dry=0.3)


# ───────────────────────── 屋顶 ─────────────────────────
def eave_roof(L, cx, y_eave, w, h, seed=0, tile=None, tile_dk=None, tile_lt=None, ridge_ratio=0.66, up=0.05, op=1.0, bells=True, orn=True,
              gap=11, under=0.04, ink=1.0, fascia=0.032, sag_p=2.0, ridge_h=0.03, under_span=None, tip_up=1.0):
    """中式屋顶（正面）。y_eave 是檐口（瓦的下沿）的水平线，w 是檐口全宽，h 是屋顶从檐口到正脊的高度。
    轮廓：檐口两端翘起、两侧的坡是内凹的曲线、正脊两端有鸱吻、瓦垄一条条、檐口一排瓦当、角上挂铃。"""
    tile = A['tile'] if tile is None else np.asarray(tile, F)
    tile_dk = A['tile_dk'] if tile_dk is None else np.asarray(tile_dk, F)
    tile_lt = A['tile_lt'] if tile_lt is None else np.asarray(tile_lt, F)
    r = np.random.default_rng(seed)
    n = 44
    ts = np.linspace(-1, 1, n)
    eave_y = lambda t: y_eave - up * w * np.abs(t) ** 4.2
    rx = ridge_ratio * w / 2
    y_tip = y_eave - up * w
    y_ridge = y_eave - h
    ridge_end_y = y_ridge - h * 0.035          # 吻兽处略翘
    bottom = [(cx + t * w / 2, float(eave_y(t))) for t in ts]

    def slope(sign):
        pts = []
        for s in np.linspace(0, 1, 20):     # s=0 檐角，s=1 屋脊端
            x = cx + sign * (w / 2 - (w / 2 - rx) * s)
            y = y_tip + (ridge_end_y - y_tip) * (s ** sag_p)
            pts.append((x, y))
        return pts

    right, left = slope(1), slope(-1)
    ridge = [(cx + t * rx, y_ridge - h * 0.035 * abs(t) ** 3) for t in np.linspace(1, -1, 14)]
    body = bottom + right[::-1][0:0] + right + ridge + left[::-1]
    # 屋面：底色 + 上亮下暗
    wash(L, body, tile, op=op, wob=0.8, seed=seed, smooth=0, tex_k=0.2, rim=0.16, rim_w=2.5)
    # 上半的受光
    up_poly = []
    for t in np.linspace(-1, 1, 16):
        xx = cx + t * w / 2 * 0.96
        yt = _roof_top(t, cx, w, rx, y_tip, ridge_end_y, y_ridge, sag_p, h)
        up_poly.append((xx, yt + 2))
    lower = [(p[0], p[1] + (float(eave_y((p[0] - cx) / (w / 2))) - p[1]) * 0.42) for p in up_poly[::-1]]
    wash(L, up_poly + lower, tile_lt, op=0.5 * op, wob=1.2, seed=seed + 1, smooth=1, tex_k=0.14, rim=0.0)
    # 下沿的暗（檐下的阴影在檐口以下，另画）
    tl = np.linspace(-0.88, 0.88, 30)
    low = [(cx + t * w / 2, float(eave_y(t)) - 1) for t in tl]
    low2 = [(p[0], p[1] - h * 0.26) for p in low[::-1]]
    wash(L, low + low2, tile_dk, op=0.42 * op, wob=1.2, seed=seed + 2, smooth=1, tex_k=0.12, rim=0.0)
    # 瓦垄
    st, st2 = [], []
    k = max(int(w / gap), 8)
    for i in range(k + 1):
        t = -0.97 + 1.94 * i / k
        xx = cx + t * w / 2
        yb = float(eave_y(t)) - 2
        yt = _roof_top(t, cx, w, rx, y_tip, ridge_end_y, y_ridge, sag_p, h) + 3
        if yb - yt < 6:
            continue
        # 瓦垄顺着屋面往外微微散开
        dx = (t * (yb - yt)) * 0.06
        st.append((xx, yt, xx + dx + r.normal(0, 0.5), yb, r.uniform(1.0, 1.7), r.uniform(0.35, 0.6) * op))
        st2.append((xx + gap * 0.5, yt + (yb - yt) * 0.05, xx + gap * 0.5 + dx, yb, r.uniform(0.8, 1.2), r.uniform(0.2, 0.4) * op))
    flicks(L, st, color=tile_dk * 0.75)
    flicks(L, st2, color=tile_lt)
    # 瓦当：檐口一排小圆
    if w > 110:
        dd = []
        nn = int(w / (gap * 1.0))
        for i in range(nn + 1):
            t = -0.98 + 1.96 * i / nn
            dd.append((cx + t * w / 2, float(eave_y(t)) - 3.2, 2.6))
        dots(L, dd, tile_lt, op=0.85 * op)
    # 檐口的飞椽带（深色的一条）
    tf = np.linspace(-0.9, 0.9, 36)
    fb = [(cx + t * w / 2, float(eave_y(t))) for t in tf]
    fa = [(cx + t * w / 2, float(eave_y(t)) - w * fascia) for t in tf]
    wash(L, fb + fa[::-1], tile_dk, op=0.55 * op, wob=0.6, seed=seed + 3, smooth=0, tex_k=0.1, rim=0.0)
    # 檐下阴影
    if under > 0:
        span = (under_span if under_span is not None else w * 0.46)
        tu = np.linspace(-span / (w / 2), span / (w / 2), 30)
        ub0 = [(cx + t * w / 2, float(eave_y(t))) for t in tu]
        ub = [(cx + t * w / 2, float(eave_y(t)) + w * under * (1 - 0.6 * abs(t) ** 2)) for t in tu]
        wash(L, ub0 + ub[::-1], INK * 1.0 + 0.0, op=0.55 * op, wob=0.8, seed=seed + 4, smooth=0, tex_k=0.1, rim=0.0)
    # 正脊：一条厚的脊 + 两端的鸱吻
    rh = max(h * ridge_h * 3.2, 5.0)
    rid_top = [(p[0], p[1] - rh * 0.5) for p in ridge]
    rid_bot = [(p[0], p[1] + rh * 0.5) for p in ridge[::-1]]
    wash(L, rid_top + rid_bot, tile_dk, op=op, wob=0.5, seed=seed + 5, smooth=0, tex_k=0.14, rim=0.14)
    wash(L, rid_top + [(p[0], p[1] - rh * 0.5 + rh * 0.3) for p in ridge[::-1]], tile_lt, op=0.5 * op, wob=0.5, seed=seed + 6, smooth=0, tex_k=0.1, rim=0.0)
    if orn:
        for sg in (-1, 1):
            ex, ey = cx + sg * rx, ridge_end_y
            s_ = max(w * 0.045, 10)
            # 鸱吻：一个弯向内侧的钩，身子厚、尖尖向内翘
            pts = [(ex + sg * s_ * 0.35, ey + s_ * 0.55), (ex + sg * s_ * 0.55, ey - s_ * 0.55), (ex + sg * s_ * 0.2, ey - s_ * 1.05),
                   (ex - sg * s_ * 0.35, ey - s_ * 1.0), (ex - sg * s_ * 0.62, ey - s_ * 0.55), (ex - sg * s_ * 0.2, ey - s_ * 0.55),
                   (ex - sg * s_ * 0.1, ey + s_ * 0.25)]
            wash(L, pts, tile_dk, op=op, wob=0.4, seed=seed + 20 + sg, smooth=1, tex_k=0.12, rim=0.14)
            line(L, pts + [pts[0]], 2.0, 0.8 * op, INK, seed + 30 + sg, dry=0.15, wob=0.3, smooth=True)
    # 轮廓墨线：垂脊（两侧坡）、檐口、正脊
    line(L, right[::-1][::-1], 3.0 * ink, 0.82 * op, INK, seed + 40, dry=0.2, wob=0.5, taper=0.12, smooth=True)
    line(L, left[::-1][::-1], 3.0 * ink, 0.82 * op, INK, seed + 41, dry=0.2, wob=0.5, taper=0.12, smooth=True)
    line(L, bottom, 3.2 * ink, 0.85 * op, INK, seed + 42, dry=0.15, wob=0.5, taper=0.04, smooth=True)
    line(L, ridge, 2.6 * ink, 0.8 * op, INK, seed + 43, dry=0.2, wob=0.4, taper=0.05, smooth=True)
    # 檐角的挂铃
    if bells and w > 150:
        for sg in (-1, 1):
            bx, by = cx + sg * w / 2, y_tip
            line(L, [(bx, by + 2), (bx, by + 15)], 1.5, 0.8 * op, INK, seed + 50 + sg, dry=0, wob=0.2)
            wash(L, [(bx - 4, by + 15), (bx + 4, by + 15), (bx + 6, by + 24), (bx - 6, by + 24)], A['gold_dk'], op=op, wob=0.3, seed=seed + 60 + sg, smooth=0, rim=0.1)
    return y_tip


def _roof_top(t, cx, w, rx, y_tip, ridge_end_y, y_ridge, sag_p, h):
    """屋面上沿在位置 t∈[-1,1] 的 y（屋脊内是脊线，屋脊外是内凹的坡）。"""
    ax = abs(t) * w / 2
    if ax <= rx:
        return y_ridge - h * 0.035 * (abs(t) * w / 2 / rx) ** 3
    s = (w / 2 - ax) / max(w / 2 - rx, 1e-3)
    return y_tip + (ridge_end_y - y_tip) * (s ** sag_p)


def under_eave(L, x0, x1, y, depth, seed=0, op=0.6):
    """檐下的暗影带（椽子的阴影）。"""
    rwash(L, x0, y, x1, y + depth, INK, op=op, wob=0.8, seed=seed, tex_k=0.05, rim=0.0)
    st = []
    r = np.random.default_rng(seed)
    n = int((x1 - x0) / 9)
    for i in range(n):
        xx = x0 + (x1 - x0) * (i + 0.5) / n
        st.append((xx, y + 1, xx + r.normal(0, 0.4), y + depth, 1.0, 0.25))
    flicks(L, st, color=A['wood_lt'])


# ───────────────────────── 城墙 / 城门 / 城门楼 ─────────────────────────
def city_wall(L, x0, x1, y_top, y_walk, y_base, seed=0, brick=None, merlon_w=36, merlon_gap=20, foot_h=46, op=1.0, cracks=6, moss=True):
    """青砖城墙：墙身（错缝砖）、墙脚的条石、叠涩的出檐线、垛口（带射孔）、雨水污渍、墙根的苔和裂缝。
    y_top 垛口顶，y_walk 垛口脚（墙顶面），y_base 地面。"""
    brick = A['brick'] if brick is None else np.asarray(brick, F)
    r = np.random.default_rng(seed)
    # 墙身
    brick_surface(L, x0, y_walk, x1, y_base - foot_h + 3, brick, bw=46, bh=19, seed=seed + 1, var=0.085, op=op, shade=0.12, stain=0.12, streak=0.16)
    # 墙脚：条石
    brick_surface(L, x0, y_base - foot_h, x1, y_base, A['slab'] * 0.88, bw=120, bh=foot_h / 1.4, seed=seed + 2, var=0.07, joint_op=0.5, joint_w=1.8, op=op, shade=0.05, stain=0.1, streak=0.0)
    line(L, [(x0, y_base - foot_h), (x1, y_base - foot_h)], 3.0, 0.7 * op, INK, seed + 3, dry=0.3, wob=0.6)
    rwash(L, x0, y_base - foot_h - 2, x1, y_base - foot_h + 8, A['brick_dk'], op=0.35 * op, wob=1.0, seed=seed + 4, tex_k=0.1, rim=0.0)
    # 叠涩出檐线
    rwash(L, x0, y_walk, x1, y_walk + 11, A['brick_dk'], op=0.9 * op, wob=0.8, seed=seed + 5, tex_k=0.14, rim=0.1)
    rwash(L, x0, y_walk + 11, x1, y_walk + 17, A['brick_lt'], op=0.55 * op, wob=0.8, seed=seed + 6, tex_k=0.1, rim=0.0)
    line(L, [(x0, y_walk), (x1, y_walk)], 3.4, 0.8 * op, INK, seed + 7, dry=0.25, wob=0.7)
    line(L, [(x0, y_walk + 11), (x1, y_walk + 11)], 2.0, 0.5 * op, INK, seed + 8, dry=0.3, wob=0.7)
    line(L, [(x0, y_walk + 17), (x1, y_walk + 17)], 2.6, 0.6 * op, INK, seed + 9, dry=0.35, wob=0.8)
    # 出檐线下的阴影
    sh = np.zeros((int(y_base - y_walk), 1), F)
    rwash(L, x0, y_walk + 17, x1, y_walk + 40, INK, op=0.2 * op, wob=1.5, seed=seed + 10, tex_k=0.05, rim=0.0)
    # 垛口
    x = x0 + r.uniform(0, merlon_w)
    k = 0
    while x < x1:
        mw = merlon_w * r.uniform(0.94, 1.06)
        xa, xb = x, min(x + mw, x1)
        brick_surface(L, xa, y_top + 5, xb, y_walk, brick * 0.97, bw=18, bh=15, seed=seed + 20 + k, var=0.08, joint_op=0.35, joint_w=1.2, op=op, shade=0.05, stain=0.06, streak=0.0)
        # 压顶
        rwash(L, xa - 2, y_top, xb + 2, y_top + 7, A['brick_lt'], op=op, wob=0.5, seed=seed + 30 + k, tex_k=0.1, rim=0.12)
        rwash(L, xa - 2, y_top + 5, xb + 2, y_top + 8, A['brick_dk'], op=0.5 * op, wob=0.4, seed=seed + 40 + k, tex_k=0.05, rim=0.0)
        boxline(L, xa, y_top, xb, y_walk, 2.4, 0.78 * op, seed + 50 + k, 0.25, sides='tlr')
        # 射孔
        sx = (xa + xb) / 2
        rwash(L, sx - 3, y_top + 11, sx + 3, y_top + 25, INK, op=0.85 * op, wob=0.3, seed=seed + 60 + k, tex_k=0.02, rim=0.0)
        x += mw + merlon_gap * r.uniform(0.9, 1.1)
        k += 1
    # 墙顶地面的细线
    # 裂缝与补过的砖
    for c in range(cracks):
        cx0 = r.uniform(x0 + 30, x1 - 30)
        cy0 = r.uniform(y_walk + 60, y_base - 120)
        pts = [(cx0, cy0)]
        for _ in range(int(r.integers(3, 6))):
            pts.append((pts[-1][0] + r.normal(0, 14), pts[-1][1] + r.uniform(10, 26)))
        brush(L, pts, w0=2.2, w1=0.8, color=INK, op=0.38 * op, seed=seed + 100 + c, wob=0.6, taper=0.2, dry=0.4, smooth=False)
    if moss:
        st = []
        for _ in range(int((x1 - x0) / 5)):
            xx = r.uniform(x0, x1)
            yy = y_base - foot_h + r.uniform(-14, 6)
            ln = r.uniform(5, 16)
            st.append((xx, yy, xx + r.normal(0, 2), yy - ln, r.uniform(1.0, 2.0), r.uniform(0.2, 0.5) * op))
        flicks(L, st, color=N['grass_dk'])


def lantern(L, x, y, r=15, seed=0, lm=None, col=None, op=1.0, cord=22):
    """纸灯笼：吊绳、上下两个木盖、圆鼓的纸身（夜里发白光）。(x,y) 是灯笼中心。"""
    col = A['paper'] * 0.88 if col is None else np.asarray(col, F)
    line(L, [(x, y - r * 1.05 - cord), (x, y - r * 1.05)], 1.6, 0.8 * op, INK, seed, dry=0, wob=0.2)
    rr = r * 1.0
    pts = [(x + math.cos(a) * rr * 0.86, y + math.sin(a) * rr * 1.02) for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)]
    wash(L, pts, col, op=op, wob=0.6, seed=seed + 1, smooth=2, tex_k=0.1, rim=0.2, rim_w=2.5)
    for k in (-0.45, 0, 0.45):      # 竹篾的横线
        yy = y + k * rr
        w_ = rr * 0.86 * math.sqrt(max(1 - (k * 1.0) ** 2, 0.05))
        line(L, [(x - w_, yy), (x, yy + 3), (x + w_, yy)], 1.1, 0.35 * op, A['wood_dk'], seed + 3, dry=0, wob=0.2, smooth=True)
    rwash(L, x - rr * 0.46, y - rr * 1.12, x + rr * 0.46, y - rr * 0.92, A['wood_dk'], op=op, wob=0.3, seed=seed + 4, tex_k=0.05, rim=0.0)
    rwash(L, x - rr * 0.4, y + rr * 0.92, x + rr * 0.4, y + rr * 1.1, A['wood_dk'], op=op, wob=0.3, seed=seed + 5, tex_k=0.05, rim=0.0)
    line(L, [(x, y + rr * 1.1), (x, y + rr * 1.1 + 12)], 1.2, 0.6 * op, INK, seed + 6, dry=0, wob=0.2)
    dots(L, [(x, y + rr * 1.1 + 14, 2.2)], A['gold_dk'], op=0.8 * op)
    if lm is not None:
        lm.ellipse(x, y, rr * 0.8, rr * 0.96, 1.0)


def gate_opening(L, cx, y_base, w=260, h=330, seed=0, lm=None, op=1.0, plaque=True):
    """城门：石框 + 过梁 + 两扇厚木门（铜钉、铁箍、兽面铺首）+ 门洞的纵深（顶、侧壁的暗）+ 门槛。"""
    x0, x1 = cx - w / 2, cx + w / 2
    y0 = y_base - h
    fw = 30
    # 石框
    brick_surface(L, x0 - fw, y0 - 42, x1 + fw, y_base, A['slab'] * 0.9, bw=60, bh=34, seed=seed, var=0.06, joint_op=0.5, joint_w=1.7, op=op, shade=0.04, stain=0.08, streak=0.05)
    # 门洞的暗（纵深）
    rwash(L, x0, y0, x1, y_base, INK * 1.6, op=op, wob=0.8, seed=seed + 1, tex_k=0.04, rim=0.0)
    # 两扇门，稍微缩进
    gx0, gx1 = x0 + 12, x1 - 12
    gy0 = y0 + 26
    door_leaf(L, gx0, gy0, cx - 1.5, y_base - 9, seed=seed + 2, stud_rows=7, stud_cols=5, op=op)
    door_leaf(L, cx + 1.5, gy0, gx1, y_base - 9, seed=seed + 3, stud_rows=7, stud_cols=5, op=op)
    # 门楣下的暗影和两侧的侧壁
    wash(L, [(x0, y0), (x1, y0), (x1 - 12, gy0 + 6), (x0 + 12, gy0 + 6)], INK, op=0.82 * op, wob=0.6, seed=seed + 4, smooth=0, tex_k=0.05, rim=0.0)
    wash(L, [(x0, y0), (x0 + 12, gy0), (x0 + 12, y_base), (x0, y_base)], INK, op=0.7 * op, wob=0.6, seed=seed + 5, smooth=0, tex_k=0.05, rim=0.0)
    wash(L, [(x1, y0), (x1 - 12, gy0), (x1 - 12, y_base), (x1, y_base)], INK, op=0.55 * op, wob=0.6, seed=seed + 6, smooth=0, tex_k=0.05, rim=0.0)
    rwash(L, gx0, gy0 + 4, gx1, gy0 + 26, INK, op=0.32 * op, wob=1.0, seed=seed + 7, tex_k=0.05, rim=0.0)
    # 铺首（兽面衔环）
    for sx in (cx - 22, cx + 22):
        dots(L, [(sx, y_base - 150, 11)], A['gold_dk'], op=op)
        dots(L, [(sx, y_base - 150, 8.5)], A['gold'], op=op)
        dots(L, [(sx - 2, y_base - 153, 2.4)], A['gold_lt'], op=0.9 * op)
        ang = np.linspace(0.25, 2 * math.pi - 0.25, 22)
        brush(L, [(sx + math.cos(a) * 16, y_base - 126 + math.sin(a) * 16) for a in ang], w0=3.0, color=A['gold_dk'], op=0.9 * op, seed=seed + 8, wob=0.3, taper=0.1, dry=0.0)
        line(L, [(sx, y_base - 142), (sx, y_base - 128)], 2.5, 0.8 * op, A['gold_dk'], seed + 9, dry=0, wob=0.2)
    # 石框的墨线
    boxline(L, x0 - fw, y0 - 42, x1 + fw, y_base, 3.6, 0.85 * op, seed + 10, 0.25, sides='tlr')
    boxline(L, x0, y0, x1, y_base, 3.0, 0.8 * op, seed + 11, 0.2, sides='tlr')
    line(L, [(x0 - fw - 6, y0 - 42), (x1 + fw + 6, y0 - 42)], 2.6, 0.7 * op, INK, seed + 12, dry=0.2)
    line(L, [(x0 - 4, y0), (x1 + 4, y0)], 2.6, 0.7 * op, INK, seed + 18, dry=0.2)
    # 门槛
    rwash(L, x0 - 8, y_base - 10, x1 + 8, y_base, A['slab_lt'], op=op, wob=0.6, seed=seed + 13, tex_k=0.12, rim=0.14)
    line(L, [(x0 - 8, y_base - 10), (x1 + 8, y_base - 10)], 2.4, 0.7 * op, INK, seed + 14, dry=0.3)
    # 过梁上的石匾（几笔抽象的字）
    if plaque:
        pw, ph = 124, 24
        py = y0 - 36
        rwash(L, cx - pw / 2, py, cx + pw / 2, py + ph, A['slab_dk'] * 0.8, op=op, wob=0.5, seed=seed + 15, tex_k=0.12, rim=0.15)
        boxline(L, cx - pw / 2, py, cx + pw / 2, py + ph, 2.4, 0.8 * op, seed + 16, 0.15)
        rr = np.random.default_rng(seed + 17)
        for i in range(3):
            gx = cx - pw / 2 + 20 + i * 42
            for k in range(int(rr.integers(3, 5))):
                a = (gx + rr.uniform(-9, 9), py + rr.uniform(5, 19))
                b = (gx + rr.uniform(-12, 12), py + rr.uniform(5, 19))
                brush(L, [a, ((a[0] + b[0]) / 2 + rr.normal(0, 2), (a[1] + b[1]) / 2 + rr.normal(0, 2)), b], w0=rr.uniform(1.8, 3.0), color=A['paper'] * 0.9, op=0.6, seed=int(rr.integers(1e6)), wob=0.4, taper=0.3, dry=0.2)


def storey(L, cx, y_base, w, h, bays, seed=0, lm=None, lit=(), wall=None, band_h=24, col_w=20, lattice=True, op=1.0, pitch=34):
    """一层楼阁（正面）：暗的后墙、等距的柱、格扇窗（lit 里的开间夜里透白光）、柱头的额枋斗拱。返回 (柱顶y)。"""
    wall = A['red_dk'] * 0.55 if wall is None else np.asarray(wall, F)
    r = np.random.default_rng(seed)
    x0 = cx - w / 2
    bw = w / bays
    ytop = y_base - h
    rwash(L, x0, ytop, x0 + w, y_base, wall, op=op, wob=0.8, seed=seed, tex_k=0.1, rim=0.0)
    # 栏板（窗下的矮墙）
    for i in range(bays):
        xa, xb = x0 + bw * i + col_w * 0.7, x0 + bw * (i + 1) - col_w * 0.7
        sill = 20
        if lattice:
            lattice_panel(L, xa, ytop + 10, xb, y_base - sill - 2, nx=3, ny=4, seed=seed + 10 + i, op=op, lm=lm if i in lit else None, diamond=False, bar=2.0)
        rwash(L, xa, y_base - sill, xb, y_base, A['wood'], op=op, wob=0.5, seed=seed + 30 + i, tex_k=0.12, rim=0.1)
        line(L, [(xa, y_base - sill), (xb, y_base - sill)], 2.2, 0.7 * op, INK, seed + 50 + i, dry=0.2)
    for i in range(bays + 1):
        column(L, x0 + bw * i, ytop - 2, y_base, col_w, seed=seed + 70 + i, base=True, op=op, base_h=col_w * 0.5)
    dougong(L, x0 - col_w * 0.6, x0 + w + col_w * 0.6, ytop - band_h, band_h + 2, pitch=pitch, seed=seed + 120, op=op)
    return ytop - band_h


def gate_tower(L, cx, y_walk, seed=0, lm=None, op=1.0, scale=1.0):
    """两层的城门楼：台基、下层（五开间）、腰檐、上层（三开间）、重檐的大屋顶（正脊两端鸱吻）。返回塔顶 y。"""
    s = scale
    # 台基
    rwash(L, cx - 330 * s, y_walk - 10, cx + 330 * s, y_walk + 2, A['slab_lt'], op=op, wob=0.6, seed=seed, tex_k=0.12, rim=0.12)
    line(L, [(cx - 330 * s, y_walk - 10), (cx + 330 * s, y_walk - 10)], 2.6, 0.75 * op, INK, seed + 1, dry=0.25)
    # 上层（先画，之后被腰檐盖住下半）
    yb2 = y_walk - 180 * s
    top2 = storey(L, cx, yb2, 360 * s, 100 * s, 3, seed=seed + 10, lm=lm, lit=(0, 1, 2), band_h=22 * s, col_w=19 * s, op=op, pitch=32)
    # 下层
    top1 = storey(L, cx, y_walk - 10, 500 * s, 100 * s, 5, seed=seed + 40, lm=lm, lit=(1, 3), band_h=22 * s, col_w=22 * s, op=op, pitch=34)
    # 腰檐
    ye1 = top1 - 1
    eave_roof(L, cx, ye1, 700 * s, 44 * s, seed=seed + 70, ridge_ratio=0.9, up=0.034, op=op, gap=12, under=0.03, orn=False, bells=True, under_span=250 * s)
    # 上层屋顶
    top2 = top2 - 2
    eave_roof(L, cx, top2 + 6 * s, 560 * s, 86 * s, seed=seed + 80, ridge_ratio=0.66, up=0.052, op=op, gap=11, under=0.035, under_span=180 * s)
    return top2 + 6 * s - 86 * s * 1.05


# ───────────────────────── 街边：店铺、板车、米摊、拴马桩 ─────────────────────────
def shop_front(L, x, y_base, w, h_wall=190, seed=0, lm=None, op=1.0, sign=True, cloth=True, lantern_lit=True, rise=58, tile_col=None):
    """木板门脸的小店：排门板、柱、额枋、横披窗（有的亮）、悬山的灰瓦顶、竖的招牌、挑出的布幌子、灯笼。x 是中心。"""
    r = np.random.default_rng(seed)
    x0, x1 = x - w / 2, x + w / 2
    yt = y_base - h_wall
    # 台阶/石脚
    rwash(L, x0 - 6, y_base - 12, x1 + 6, y_base, A['slab'], op=op, wob=0.8, seed=seed, tex_k=0.14, rim=0.14)
    line(L, [(x0 - 6, y_base - 12), (x1 + 6, y_base - 12)], 2.4, 0.7 * op, INK, seed + 1, dry=0.3)
    # 排门板
    rwash(L, x0, yt, x1, y_base - 12, A['plank'], op=op, wob=0.9, seed=seed + 2, tex_k=0.18, rim=0.14)
    npl = int(w / 26)
    for i in range(npl + 1):
        xx = x0 + w * i / npl
        line(L, [(xx, yt + 4), (xx + r.normal(0, 0.8), y_base - 13)], 1.7, 0.55 * op, INK, seed + 10 + i, dry=0.3, wob=0.5)
    st = []
    for _ in range(int(w * h_wall / 500)):
        xx = r.uniform(x0 + 4, x1 - 4)
        yy = r.uniform(yt + 20, y_base - 30)
        st.append((xx, yy, xx + r.normal(0, 0.6), yy + r.uniform(8, 30), r.uniform(0.7, 1.3), r.uniform(0.15, 0.35) * op))
    flicks(L, st, color=A['plank_dk'])
    # 横披窗（门脸上方一排窗）
    wy0, wy1 = yt + 14, yt + 56
    bw = w / 4
    for i in range(4):
        xa, xb = x0 + bw * i + 10, x0 + bw * (i + 1) - 10
        lattice_panel(L, xa, wy0, xb, wy1, nx=3, ny=2, seed=seed + 30 + i, op=op, lm=lm if i in (1,) else None, bar=2.0)
    # 大门（两扇中间的铺板，铁条加固）
    dx0, dx1 = x - w * 0.22, x + w * 0.22
    rwash(L, dx0, yt + 70, dx1, y_base - 12, A['plank_dk'], op=0.5 * op, wob=0.7, seed=seed + 40, tex_k=0.1, rim=0.0)
    for k in range(3):
        yy = yt + 90 + k * 36
        line(L, [(dx0, yy), (dx1, yy)], 2.2, 0.5 * op, INK, seed + 41 + k, dry=0.3)
    # 柱
    for k, xx in enumerate((x0 + 8, x - w * 0.22 - 4, x + w * 0.22 + 4, x1 - 8)):
        column(L, xx, yt - 4, y_base - 12, 15, seed=seed + 50 + k, base=False, op=op)
    # 额枋 + 屋顶
    rwash(L, x0 - 8, yt - 20, x1 + 8, yt - 2, A['red_dk'], op=op, wob=0.7, seed=seed + 60, tex_k=0.12, rim=0.1)
    line(L, [(x0 - 8, yt - 2), (x1 + 8, yt - 2)], 2.2, 0.7 * op, INK, seed + 61, dry=0.25)
    eave_roof(L, x, yt - 22, w + 70, rise, seed=seed + 70, tile=tile_col, ridge_ratio=0.80, up=0.028, op=op, gap=10, under=0.03, orn=False, bells=False, under_span=w / 2, sag_p=1.6)
    # 招牌（竖的，挂在一侧）
    if sign:
        sx = x1 + 4
        line(L, [(sx - 28, yt - 4), (sx - 8, yt - 4)], 3.0, 0.8 * op, A['wood_dk'], seed + 80, dry=0.1)
        rwash(L, sx - 22, yt, sx + 2, yt + 118, A['wood'], op=op, wob=0.6, seed=seed + 81, tex_k=0.14, rim=0.14)
        boxline(L, sx - 22, yt, sx + 2, yt + 118, 2.4, 0.8 * op, seed + 82, 0.2)
        rr = np.random.default_rng(seed + 83)
        for j in range(3):
            gy = yt + 20 + j * 32
            for k in range(3):
                a = (sx - 10 + rr.uniform(-6, 6), gy + rr.uniform(-9, 9))
                b = (sx - 10 + rr.uniform(-7, 7), gy + rr.uniform(-9, 9))
                brush(L, [a, b], w0=rr.uniform(1.6, 2.6), color=A['paper'] * 0.92, op=0.6, seed=int(rr.integers(1e6)), wob=0.3, taper=0.3, dry=0.2, smooth=False)
    # 布幌子（挑出的杆 + 竖的布条）
    if cloth:
        px = x0 - 16
        line(L, [(px + 24, yt - 6), (px - 18, yt - 18)], 3.2, 0.8 * op, A['wood_dk'], seed + 90, dry=0.1)
        c = np.asarray(A['cloth'], F)
        for kk in range(10):
            yy = yt - 14 + kk * 9
            xo = px - 18 + 3 * math.sin(kk * 0.7 + seed)
            wash(L, [(xo - 15, yy), (xo + 15, yy), (xo + 15 + 2 * math.sin(kk), yy + 9.5), (xo - 15 + 2 * math.sin(kk), yy + 9.5)], mix(c, A['cloth_dk'], 0.3 + 0.2 * math.sin(kk * 0.9)), op=op, wob=0.3, seed=seed + 92 + kk, smooth=0, tex_k=0.1, rim=0.0)
        brush(L, [(px - 33, yt - 14), (px - 33, yt + 78)], w0=2.0, color=INK, op=0.6 * op, seed=seed + 120, wob=0.5, taper=0.1, dry=0.2)
        brush(L, [(px - 3, yt - 14), (px - 3, yt + 78)], w0=2.0, color=INK, op=0.6 * op, seed=seed + 121, wob=0.5, taper=0.1, dry=0.2)
    if lantern_lit:
        lantern(L, x + w * 0.02, yt + 50 + 10, 14, seed=seed + 130, lm=lm, op=op, cord=14)


def cart(L, x, y_base, seed=0, op=1.0, face=-1, load=True, lm=None, s=1.0):
    """停着的板车（侧面）：大木轮（辐条）、平板车身、两条长的车辕斜落到地、车上几个麻袋。x 是车身中心，车辕朝 face 方向。s 是比例。"""
    r = np.random.default_rng(seed)
    wr = 54 * s
    wy = y_base - wr
    bed_y = wy - 8 * s
    bw = 250 * s
    for k, off in enumerate((-9, 9)):
        brush(L, [(x + face * 40 * s, bed_y + off * 0.3), (x + face * 200 * s, bed_y + 36 * s + off * 0.2), (x + face * 330 * s, y_base - 6 + off * 0.2)], w0=9 * s, w1=6 * s, color=A['wood'] * 0.8, op=op, seed=seed + k, wob=0.8, taper=0.04)
    rwash(L, x - bw / 2, bed_y - 12 * s, x + bw / 2, bed_y + 6 * s, A['plank'], op=op, wob=0.8, seed=seed + 3, tex_k=0.16, rim=0.14)
    for i in range(1, 8):
        xx = x - bw / 2 + bw * i / 8
        line(L, [(xx, bed_y - 12 * s), (xx, bed_y + 6 * s)], 1.4, 0.5 * op, INK, seed + 10 + i, dry=0.3)
    boxline(L, x - bw / 2, bed_y - 12 * s, x + bw / 2, bed_y + 6 * s, 2.6, 0.8 * op, seed + 20, 0.2)
    rwash(L, x - 70 * s, bed_y + 6 * s, x + 70 * s, bed_y + 18 * s, A['wood_dk'], op=op, wob=0.6, seed=seed + 21, tex_k=0.1, rim=0.1)
    ang = np.linspace(0, 2 * math.pi, 34)
    wash(L, [(x + math.cos(a) * wr, wy + math.sin(a) * wr) for a in ang[:-1]], A['wood'] * 0.9, op=op, wob=0.5, seed=seed + 30, smooth=2, tex_k=0.14, rim=0.2, rim_w=3)
    wash(L, [(x + math.cos(a) * (wr - 9 * s), wy + math.sin(a) * (wr - 9 * s)) for a in ang[:-1]], A['brick_dk'], op=0.5 * op, wob=0.5, seed=seed + 31, smooth=2, tex_k=0.1, rim=0.0)
    brush(L, [(x + math.cos(a) * wr, wy + math.sin(a) * wr) for a in ang], w0=3.6 * s, color=INK, op=0.85 * op, seed=seed + 32, wob=0.5, taper=0.02, dry=0.15)
    brush(L, [(x + math.cos(a) * (wr - 9 * s), wy + math.sin(a) * (wr - 9 * s)) for a in ang], w0=2.0 * s, color=INK, op=0.6 * op, seed=seed + 33, wob=0.5, taper=0.02, dry=0.25)
    for k in range(12):
        a = k * math.pi / 6 + 0.15
        line(L, [(x + math.cos(a) * 9 * s, wy + math.sin(a) * 9 * s), (x + math.cos(a) * (wr - 8 * s), wy + math.sin(a) * (wr - 8 * s))], 3.2 * s, 0.78 * op, A['wood_dk'], seed + 40 + k, dry=0.1, wob=0.3)
    dots(L, [(x, wy, 10 * s)], A['wood_dk'], op=op)
    dots(L, [(x, wy, 4.5 * s)], A['gold_dk'], op=0.9 * op)
    if load:
        for k, (sx, sw, sh) in enumerate([(-70, 78, 60), (10, 84, 72), (88, 62, 48)]):
            sx, sw, sh = sx * s, sw * s, sh * s
            sy = bed_y - 12 * s
            pts = [(x + sx - sw / 2, sy), (x + sx - sw * 0.55, sy - sh * 0.5), (x + sx - sw * 0.38, sy - sh), (x + sx + sw * 0.22, sy - sh * 1.04), (x + sx + sw * 0.52, sy - sh * 0.55), (x + sx + sw / 2, sy)]
            wash(L, pts, A['earth_lt'] * 0.98, op=op, wob=0.8, seed=seed + 60 + k, smooth=2, tex_k=0.2, rim=0.22, rim_w=3)
            wash(L, [(x + sx + sw * 0.1, sy - sh * 0.9), (x + sx + sw * 0.52, sy - sh * 0.55), (x + sx + sw / 2, sy), (x + sx + sw * 0.05, sy)], A['earth_dk'], op=0.35 * op, wob=0.8, seed=seed + 70 + k, smooth=1, rim=0.0)
            brush(L, pts + [pts[0]], w0=2.4, color=INK, op=0.7 * op, seed=seed + 80 + k, wob=0.8, taper=0.1, dry=0.25)
            brush(L, [(x + sx - sw * 0.25, sy - sh * 0.98), (x + sx, sy - sh * 0.75), (x + sx + sw * 0.2, sy - sh * 0.98)], w0=2.0, color=INK, op=0.55 * op, seed=seed + 90 + k, wob=0.6, taper=0.3)
        brush(L, [(x - bw / 2 + 20 * s, bed_y - 12 * s), (x - 20 * s, bed_y - 78 * s), (x + bw / 2 - 30 * s, bed_y - 14 * s)], w0=2.0, color=A['earth_dk'], op=0.8 * op, seed=seed + 100, wob=1.0, taper=0.1)


def rice_stall(L, x, y_base, seed=0, op=1.0, lm=None, s=1.0):
    """卖米的摊子：布棚（两根杆撑着）、木案（案面高≈110）、几只敞口的米袋（鼓着白米）、一只量米的木斗、秤、灯笼。x 是中心。"""
    r = np.random.default_rng(seed)
    tw = 230 * s
    ty = y_base - 108
    for dx in (-tw / 2 + 14, tw / 2 - 14):
        line(L, [(x + dx, ty), (x + dx + (4 if dx > 0 else -4), y_base)], 8, 0.9 * op, A['wood_dk'], seed + int(abs(dx)), dry=0.1, wob=0.5)
    line(L, [(x - tw / 2 + 14, y_base - 40), (x + tw / 2 - 14, y_base - 40)], 5, 0.7 * op, A['wood_dk'], seed + 3, dry=0.2, wob=0.6)
    rwash(L, x - tw / 2, ty - 12, x + tw / 2, ty + 7, A['plank'], op=op, wob=0.8, seed=seed + 5, tex_k=0.16, rim=0.14)
    boxline(L, x - tw / 2, ty - 12, x + tw / 2, ty + 7, 2.4, 0.8 * op, seed + 6, 0.2)
    for k, (sx, sw, sh) in enumerate([(-66 * s, 84 * s, 70 * s), (26 * s, 88 * s, 78 * s)]):
        sy = ty - 12
        pts = [(x + sx - sw / 2, sy), (x + sx - sw * 0.56, sy - sh * 0.45), (x + sx - sw * 0.46, sy - sh), (x + sx + sw * 0.46, sy - sh), (x + sx + sw * 0.56, sy - sh * 0.45), (x + sx + sw / 2, sy)]
        wash(L, pts, A['earth_lt'], op=op, wob=0.7, seed=seed + 10 + k, smooth=2, tex_k=0.2, rim=0.22, rim_w=3)
        wash(L, [(x + sx - sw * 0.5, sy - sh * 0.95), (x + sx - sw * 0.3, sy - sh * 1.28), (x + sx + sw * 0.1, sy - sh * 1.38), (x + sx + sw * 0.4, sy - sh * 1.22), (x + sx + sw * 0.5, sy - sh * 0.95)], A['paper'], op=op, wob=0.6, seed=seed + 20 + k, smooth=2, tex_k=0.08, rim=0.2)
        stt = []
        for _ in range(30):
            px = x + sx + r.uniform(-sw * 0.38, sw * 0.38)
            py = sy - sh * r.uniform(1.0, 1.32)
            stt.append((px, py, px + r.uniform(1, 3), py + r.uniform(0.5, 1.5), 1.3, r.uniform(0.2, 0.5)))
        flicks(L, stt, color=A['earth_dk'])
        brush(L, pts + [pts[0]], w0=2.4, color=INK, op=0.7 * op, seed=seed + 30 + k, wob=0.8, taper=0.1, dry=0.25)
        line(L, [(x + sx - sw * 0.46, sy - sh * 0.95), (x + sx, sy - sh * 0.82), (x + sx + sw * 0.46, sy - sh * 0.95)], 2.2, 0.6 * op, INK, seed + 40 + k, dry=0.2, smooth=True)
    bx = x + 94 * s
    wash(L, [(bx - 24, ty - 12), (bx + 24, ty - 12), (bx + 18, ty - 50), (bx - 18, ty - 50)], A['wood'], op=op, wob=0.5, seed=seed + 50, smooth=0, tex_k=0.14, rim=0.16)
    wash(L, [(bx - 18, ty - 50), (bx + 18, ty - 50), (bx + 13, ty - 56), (bx - 13, ty - 56)], A['paper'], op=op, wob=0.4, seed=seed + 51, smooth=0, rim=0.1)
    boxline(L, bx - 23, ty - 50, bx + 23, ty - 12, 2.2, 0.75 * op, seed + 52, 0.2, sides='lrb')
    pole_h = 410
    for dx in (-tw / 2 - 8, tw / 2 + 8):
        line(L, [(x + dx, y_base), (x + dx, y_base - pole_h)], 7, 0.9 * op, A['wood_dk'], seed + int(abs(dx)) + 7, dry=0.1, wob=0.6)
    ya, yb = y_base - pole_h + 8, y_base - pole_h + 80
    cloth_pts = [(x - tw / 2 - 40, ya), (x + tw / 2 + 40, ya + 6), (x + tw / 2 + 52, yb + 12), (x - tw / 2 - 52, yb)]
    wash(L, cloth_pts, A['cloth'], op=op, wob=1.0, seed=seed + 60, smooth=0, tex_k=0.14, rim=0.16)
    for i in range(1, 7):
        xx = x - tw / 2 - 40 + (tw + 80) * i / 7
        line(L, [(xx, ya + 3 * i / 7), (xx + (i - 3.5) * 1.6, yb + 12 * i / 7)], 1.5, 0.3 * op, INK, seed + 70 + i, dry=0.4, wob=0.5)
    wash(L, [(x - tw / 2 - 52, yb), (x + tw / 2 + 52, yb + 12), (x + tw / 2 + 48, yb + 28), (x - tw / 2 - 48, yb + 18)], A['cloth_dk'], op=op, wob=0.8, seed=seed + 80, smooth=0, tex_k=0.12, rim=0.1)
    for i in range(12):
        xx = x - tw / 2 - 48 + (tw + 96) * (i + 0.5) / 12
        wash(L, [(xx - 8, yb + 16 + i % 2), (xx + 8, yb + 16 + i % 2), (xx, yb + 30)], A['cloth_dk'], op=op, wob=0.3, seed=seed + 90 + i, smooth=0, rim=0.0)
    boxline(L, x - tw / 2 - 40, ya, x + tw / 2 + 50, yb + 12, 2.6, 0.75 * op, seed + 110, 0.3, sides='tb')
    line(L, [(x - 40, ya + 20), (x - 10, ya + 80), (x - 6, ya + 130)], 1.6, 0.7 * op, INK, seed + 120, dry=0.1, wob=0.5, smooth=True)
    line(L, [(x - 70, ya + 72), (x + 50, ya + 80)], 3.0, 0.75 * op, A['wood_dk'], seed + 121, dry=0.1, wob=0.5)
    dots(L, [(x - 6, ya + 132, 4)], A['gold_dk'], op=0.9 * op)
    lantern(L, x + 4, yb + 60, 14, seed=seed + 130, lm=lm, op=op, cord=22)


def hitch_post(L, x, y_base, h=190, seed=0, op=1.0):
    """拴马桩：一根石桩，顶上雕着一只蹲着的小兽（简化的圆头），颈上一个穿绳的孔，桩脚堆着基石。"""
    r = np.random.default_rng(seed)
    w = 34
    rwash(L, x - 30, y_base - 22, x + 30, y_base + 2, A['slab'], op=op, wob=0.8, seed=seed, tex_k=0.14, rim=0.15)
    wash(L, [(x - w / 2, y_base - 18), (x - w * 0.42, y_base - h + 36), (x + w * 0.42, y_base - h + 36), (x + w / 2, y_base - 18)], A['slab'] * 0.95, op=op, wob=0.8, seed=seed + 1, smooth=0, tex_k=0.2, rim=0.18)
    wash(L, [(x + w * 0.05, y_base - 18), (x + w * 0.05, y_base - h + 36), (x + w * 0.42, y_base - h + 36), (x + w / 2, y_base - 18)], A['slab_dk'], op=0.5 * op, wob=0.6, seed=seed + 2, smooth=0, rim=0.0)
    # 兽首
    hy = y_base - h + 36
    head = [(x - 19, hy), (x - 21, hy - 22), (x - 12, hy - 40), (x + 2, hy - 46), (x + 18, hy - 36), (x + 21, hy - 18), (x + 19, hy)]
    wash(L, head, A['slab_lt'] * 0.96, op=op, wob=0.6, seed=seed + 3, smooth=2, tex_k=0.18, rim=0.2)
    wash(L, [(x + 2, hy - 46), (x + 18, hy - 36), (x + 21, hy - 18), (x + 19, hy), (x + 4, hy)], A['slab_dk'], op=0.4 * op, wob=0.5, seed=seed + 4, smooth=1, rim=0.0)
    brush(L, head + [head[0]], w0=2.8, color=INK, op=0.8 * op, seed=seed + 5, wob=0.6, taper=0.1, dry=0.25)
    dots(L, [(x - 7, hy - 28, 3), (x + 8, hy - 26, 2.6)], INK, op=0.85 * op)
    brush(L, [(x - 5, hy - 14), (x + 4, hy - 11), (x + 12, hy - 15)], w0=2.0, color=INK, op=0.7 * op, seed=seed + 6, wob=0.3, taper=0.3)
    # 穿绳孔 + 绳
    dots(L, [(x, y_base - h * 0.45, 5.5)], INK, op=0.85 * op)
    brush(L, [(x, y_base - h * 0.45), (x + 14, y_base - h * 0.3), (x + 20, y_base - 8), (x + 46, y_base - 4)], w0=3.0, color=A['earth_dk'], op=0.85 * op, seed=seed + 7, wob=1.0, taper=0.1)
    st = []
    for _ in range(int(h * 0.2)):
        px = x + r.uniform(-w * 0.4, w * 0.4)
        py = y_base - r.uniform(30, h * 0.65)
        st.append((px, py, px + r.normal(0, 1), py + r.uniform(8, 22), r.uniform(0.8, 1.6), r.uniform(0.15, 0.4) * op))
    flicks(L, st, color=INK)
    line(L, [(x - w / 2, y_base - 18), (x - w * 0.42, hy)], 2.6, 0.75 * op, INK, seed + 8, dry=0.3)
    line(L, [(x + w / 2, y_base - 18), (x + w * 0.42, hy)], 2.6, 0.75 * op, INK, seed + 9, dry=0.3)


# ───────────────────────── 九层砖塔 ─────────────────────────
def balustrade(L, x0, x1, y, h=58, post_gap=64, seed=0, op=1.0, col=None):
    """石栏杆：望柱（柱头小圆）+ 寻杖 + 栏板（带一个凹的框）。y 是栏杆脚。"""
    col = A['slab'] if col is None else np.asarray(col, F)
    n = max(int(round((x1 - x0) / post_gap)), 1)
    pg = (x1 - x0) / n
    # 栏板
    for i in range(n):
        xa, xb = x0 + pg * i + 7, x0 + pg * (i + 1) - 7
        rwash(L, xa, y - h * 0.72, xb, y - 6, col * 0.97, op=op, wob=0.6, seed=seed + i, tex_k=0.14, rim=0.14)
        rwash(L, xa + 7, y - h * 0.6, xb - 7, y - 16, A['slab_dk'], op=0.28 * op, wob=0.5, seed=seed + 40 + i, tex_k=0.08, rim=0.0)
        boxline(L, xa, y - h * 0.72, xb, y - 6, 2.0, 0.65 * op, seed + 80 + i, 0.3)
    rwash(L, x0, y - h * 0.8, x1, y - h * 0.72, A['slab_lt'], op=op, wob=0.5, seed=seed + 120, tex_k=0.1, rim=0.12)
    line(L, [(x0, y - h * 0.8), (x1, y - h * 0.8)], 2.2, 0.7 * op, INK, seed + 121, dry=0.3)
    for i in range(n + 1):
        xx = x0 + pg * i
        rwash(L, xx - 6, y - h, xx + 6, y, col, op=op, wob=0.5, seed=seed + 130 + i, tex_k=0.14, rim=0.15)
        wash(L, [(xx - 6, y - h), (xx, y - h - 8), (xx + 6, y - h)], A['slab_lt'], op=op, wob=0.3, seed=seed + 160 + i, smooth=0, rim=0.1)
        boxline(L, xx - 6, y - h, xx + 6, y, 2.0, 0.7 * op, seed + 190 + i, 0.3, sides='lr')


def stupa_finial(L, cx, y_base, seed=0, op=1.0):
    """塔刹（宝顶）：刹座（须弥座）→ 覆钵 → 七重相轮（一层比一层小）→ 宝盖 → 宝珠，尖尖的但是中式；四条刹链斜落到屋角。返回塔尖 y。"""
    y = y_base
    # 刹座
    wash(L, [(cx - 44, y), (cx - 40, y - 12), (cx - 34, y - 12), (cx - 34, y - 26), (cx + 34, y - 26), (cx + 34, y - 12), (cx + 40, y - 12), (cx + 44, y)], A['slab'], op=op, wob=0.5, seed=seed, smooth=0, tex_k=0.16, rim=0.16)
    line(L, [(cx - 44, y), (cx - 40, y - 12), (cx - 34, y - 12), (cx - 34, y - 26), (cx + 34, y - 26), (cx + 34, y - 12), (cx + 40, y - 12), (cx + 44, y), (cx - 44, y)], 2.4, 0.8 * op, INK, seed + 1, dry=0.2)
    y -= 26
    # 覆钵（倒扣的钵）
    bowl = [(cx - 34, y)] + [(cx + math.cos(a) * 34, y - math.sin(a) * 38) for a in np.linspace(math.pi, 0, 14)[1:-1]] + [(cx + 34, y)]
    wash(L, bowl, A['brick_lt'], op=op, wob=0.5, seed=seed + 2, smooth=1, tex_k=0.16, rim=0.18)
    wash(L, [(cx + 8, y), (cx + 20, y - 30), (cx + 31, y - 20), (cx + 34, y)], A['brick_dk'], op=0.45 * op, wob=0.5, seed=seed + 3, smooth=1, rim=0.0)
    line(L, bowl, 2.6, 0.8 * op, INK, seed + 4, dry=0.2, smooth=True)
    y -= 36
    rwash(L, cx - 26, y - 6, cx + 26, y + 1, A['slab_dk'], op=op, wob=0.4, seed=seed + 5, tex_k=0.1, rim=0.1)
    y -= 6
    # 刹杆
    line(L, [(cx, y), (cx, y - 160)], 5, 0.85 * op, A['wood_dk'], seed + 6, dry=0.1, wob=0.3)
    # 七重相轮
    for k in range(7):
        wk = 52 - k * 4.5
        hk = 14
        wash(L, [(cx - wk / 2, y), (cx + wk / 2, y), (cx + wk / 2 - 3, y - hk), (cx - wk / 2 + 3, y - hk)], A['gold'] if k % 2 == 0 else A['gold_dk'], op=op, wob=0.3, seed=seed + 10 + k, smooth=0, tex_k=0.1, rim=0.14)
        line(L, [(cx - wk / 2, y), (cx + wk / 2, y)], 2.0, 0.75 * op, INK, seed + 30 + k, dry=0.2, wob=0.2)
        y -= hk + 1.5
    # 宝盖（上翘的圆盘）
    wash(L, [(cx - 46, y - 8), (cx - 24, y + 4), (cx + 24, y + 4), (cx + 46, y - 8), (cx + 26, y - 4), (cx - 26, y - 4)], A['gold_dk'], op=op, wob=0.4, seed=seed + 40, smooth=0, tex_k=0.1, rim=0.14)
    line(L, [(cx - 46, y - 8), (cx - 24, y + 4), (cx + 24, y + 4), (cx + 46, y - 8)], 2.2, 0.8 * op, INK, seed + 41, dry=0.2, smooth=True)
    y -= 12
    line(L, [(cx, y + 6), (cx, y - 30)], 3.5, 0.85 * op, A['wood_dk'], seed + 42, dry=0.1, wob=0.2)
    y -= 12
    # 宝珠（葫芦形）：下大上小 + 一道尖
    gourd = [(cx, y + 8), (cx - 14, y - 6), (cx - 12, y - 22), (cx - 5, y - 34), (cx, y - 46), (cx + 5, y - 34), (cx + 12, y - 22), (cx + 14, y - 6)]
    wash(L, gourd, A['gold_lt'], op=op, wob=0.3, seed=seed + 43, smooth=2, tex_k=0.08, rim=0.2)
    line(L, gourd + [gourd[0]], 2.2, 0.8 * op, INK, seed + 44, dry=0.15, smooth=True)
    line(L, [(cx, y - 46), (cx, y - 58)], 2.0, 0.8 * op, INK, seed + 45, dry=0.0, wob=0.2, taper=0.5)
    return y - 58


def pagoda_tower(L, cx, y_ground, lm=None, seed=0, tiers=9, base_w=700, top_w=330, t_first=306, t_step=5.25, op=1.0, deck_y=None):
    """严格九层的砖塔：每层＝青砖墙身（正中一个亮着冷白光的窗）+ 斗拱 + 灰瓦的飞檐（翘角、檐铃）。逐层收小，塔基、台阶、石栏，顶上是栏杆平台和塔刹。
    返回 dict：每层的 (eave_y, roof_top_y, body_w, eave_w)、塔尖 y、平台 y。"""
    info = []
    # ── 塔基（须弥座）
    by = y_ground
    plat_h = 60
    px0, px1 = cx - 330, cx + 330
    brick_surface(L, px0, by - plat_h, px1, by, A['slab'] * 0.92, bw=96, bh=30, seed=seed + 1, var=0.06, joint_op=0.5, joint_w=1.8, shade=0.06, stain=0.1, streak=0.06)
    rwash(L, px0 - 10, by - plat_h - 12, px1 + 10, by - plat_h + 2, A['slab_lt'], op=op, wob=0.7, seed=seed + 2, tex_k=0.12, rim=0.14)
    line(L, [(px0 - 10, by - plat_h - 12), (px1 + 10, by - plat_h - 12)], 3.0, 0.8 * op, INK, seed + 3, dry=0.25)
    line(L, [(px0 - 10, by - plat_h + 2), (px1 + 10, by - plat_h + 2)], 2.0, 0.6 * op, INK, seed + 4, dry=0.3)
    boxline(L, px0, by - plat_h, px1, by, 3.0, 0.8 * op, seed + 5, 0.25, sides='lrb')
    for k in range(7):    # 壶门（须弥座束腰的凹格）
        gx = px0 + 40 + (px1 - px0 - 80) * k / 6
        rwash(L, gx - 22, by - plat_h + 16, gx + 22, by - 14, A['slab_dk'], op=0.45 * op, wob=0.5, seed=seed + 10 + k, tex_k=0.08, rim=0.1)
        boxline(L, gx - 22, by - plat_h + 16, gx + 22, by - 14, 1.6, 0.45 * op, seed + 20 + k, 0.4)
    y_floor = by - plat_h - 12                     # 塔身脚
    # ── 九层
    y_base = y_floor
    for k in range(1, tiers + 1):
        T = t_first - t_step * (k - 1)
        we = base_w - (base_w - top_w) * (k - 1) / (tiers - 1)
        wb = we * 0.78
        r_h = T * 0.235                              # 屋面的高度
        b_h = T - r_h                                # 墙身高
        E = y_base - b_h                             # 檐口（瓦的下沿）y
        s_k = seed + 100 * k
        x0, x1 = cx - wb / 2, cx + wb / 2
        # 墙身：青砖
        brick_surface(L, x0, E - 6, x1, y_base + 4, A['brick'], bw=34, bh=14, seed=s_k + 1, var=0.085, joint_op=0.4, joint_w=1.2, op=op, shade=0.1, stain=0.1, streak=0.14)
        # 背光的一侧加深
        wash(L, [(cx + wb * 0.18, E), (x1, E), (x1, y_base), (cx + wb * 0.18, y_base)], A['brick_dk'], op=0.26 * op, wob=3, seed=s_k + 2, smooth=0, tex_k=0.1, rim=0.0)
        # 角柱 / 壁柱
        for sx in (-1, 1):
            column(L, cx + sx * (wb / 2 - 11), E - 2, y_base, 20, seed=s_k + 3 + sx, base=False, op=op, taper=0.0)
        # 腰线（叠涩的砖线）
        yy = y_base - b_h * 0.30
        rwash(L, x0, yy, x1, yy + 7, A['brick_dk'], op=0.6 * op, wob=0.6, seed=s_k + 6, tex_k=0.1, rim=0.1)
        line(L, [(x0, yy), (x1, yy)], 2.0, 0.55 * op, INK, seed + s_k + 7, dry=0.35)
        # 窗：石框 + 亮着的窗
        ww, wh = max(wb * 0.17, 34), b_h * 0.40
        wy1 = y_base - b_h * 0.34
        if k == 1:
            ww, wh, wy1 = wb * 0.2, b_h * 0.56, y_base - 2
        wy0 = wy1 - wh
        rwash(L, cx - ww / 2 - 9, wy0 - 11, cx + ww / 2 + 9, wy1 + 7, A['slab'], op=op, wob=0.5, seed=s_k + 8, tex_k=0.12, rim=0.14)
        lattice_panel(L, cx - ww / 2, wy0, cx + ww / 2, wy1, nx=2, ny=3, seed=s_k + 9, op=op, lm=lm, bar=2.4)
        boxline(L, cx - ww / 2 - 9, wy0 - 11, cx + ww / 2 + 9, wy1 + 7, 2.4, 0.75 * op, s_k + 10, 0.25)
        boxline(L, cx - ww / 2, wy0, cx + ww / 2, wy1, 2.4, 0.8 * op, s_k + 11, 0.15)
        # 两边的浅龛（暗的凹格）
        for sx in (-1, 1):
            nx_ = cx + sx * wb * 0.30
            rwash(L, nx_ - 22, wy0 + 10, nx_ + 22, wy1 - 4, A['brick_dk'], op=0.32 * op, wob=0.6, seed=s_k + 12 + sx, tex_k=0.1, rim=0.0)
            boxline(L, nx_ - 22, wy0 + 10, nx_ + 22, wy1 - 4, 1.6, 0.4 * op, s_k + 15 + sx, 0.4)
        # 斗拱
        dougong(L, x0 - 8, x1 + 8, E - 22, 24, pitch=26, seed=s_k + 20, op=op)
        # 瓦檐
        rr_ratio = min((we * 0.78 * 0.935) / we * 1.0 + 0.02, 0.96)
        eave_roof(L, cx, E, we, r_h, seed=s_k + 30, ridge_ratio=rr_ratio, up=0.052, op=op, gap=10, under=0.04, orn=False, bells=True, under_span=wb / 2 + 6, sag_p=1.6)
        info.append(dict(k=k, eave=E, roof_top=E - r_h, body_w=wb, eave_w=we, win=(wy0, wy1)))
        y_base = E - r_h + 5
    deck = info[-1]['roof_top']
    return info, deck


def stair_front(L, cx, y_top, y_bot, w_top, w_bot, steps=4, seed=0, op=1.0):
    """正面的台阶：一级级的石阶，两侧的垂带。"""
    sh = (y_bot - y_top) / steps
    for i in range(steps):
        yt_ = y_top + i * sh
        ww = w_top + (w_bot - w_top) * (i + 1) / steps
        rwash(L, cx - ww / 2, yt_, cx + ww / 2, yt_ + sh, A['slab_lt'] if i % 2 == 0 else A['slab'], op=op, wob=0.6, seed=seed + i, tex_k=0.14, rim=0.14)
        rwash(L, cx - ww / 2, yt_ + sh * 0.65, cx + ww / 2, yt_ + sh, INK, op=0.18 * op, wob=0.6, seed=seed + 20 + i, tex_k=0.05, rim=0.0)
        line(L, [(cx - ww / 2, yt_ + sh), (cx + ww / 2, yt_ + sh)], 2.2, 0.65 * op, INK, seed + 40 + i, dry=0.3)
    for sx in (-1, 1):
        line(L, [(cx + sx * w_top / 2, y_top), (cx + sx * w_bot / 2, y_bot)], 2.6, 0.7 * op, INK, seed + 60 + sx, dry=0.3)
