"""山、林、雪、草原、室内的笔法工具（Agent M）：建立在 pt.py / cn.py 之上，不改它们。

- 树：pine_ink（松：松针团 + 鳞皴树干）、fir_ink（杉）、cypress_ink（柏）、birch_ink（桦）、plum_ink（老梅）、tree_trunk（近景粗树干）
- 雪：drift（雪堆）、snow_field（雪地）、tracks（兔脚印）、frost（白霜厚点）
- 小景物：puddle（水洼）、web（蛛网 + 露珠）、dry_grass（枯草）、grass_blades（草叶）、stone_ring（火塘石圈）、bush（灌木）
- 建筑/器物：snow_hut（雪屋）、felt_yurt（毡包）、sheep（羊）、lake（暗湖）、plank_wall、beam、window_paper、bell_hung、drum_wall、table、bench、guqin、stove、jar、gourd、corn…
- 收尾：save_plate2（水彩化 + 夜色/光照版 + 纸白冷光的窗/灯层）
"""
from ccommon import *   # noqa: F401,F403  (ccommon 已 import cn / pt / grade)
import math
import numpy as np
import cv2

COOL = hexc('#e9eef2')          # 窗里的光：冷白（夜色里落到纸白 #EFE8D8，不偏黄）
INKB = INK * 0.85


def U(r, a, b):
    return float(r.uniform(a, b))


# ───────────────────────── 白霜 / 积雪的点 ─────────────────────────
def frost(L, pts, op=0.85, size=(2.2, 4.2), col=None, seed=0, ln=(3, 8)):
    """白霜：厚而短的白点苔（沿着给定的点撒），点苔是水平略斜的短笔。pts=[(x,y)...]"""
    col = N['snow'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    st = []
    for (x, y) in pts:
        l = U(r, *ln)
        a = r.normal(0, 0.35)
        st.append((x - l / 2 * math.cos(a), y - l / 2 * math.sin(a), x + l / 2 * math.cos(a), y + l / 2 * math.sin(a), U(r, *size), U(r, 0.55, 1.0) * op))
    flicks(L, st, color=col)


# ───────────────────────── 松 ─────────────────────────
def needle_pom(L, cx, cy, rx, r, col, dark, frost_k=0.0, op=1.0, flat=0.5, droop=0.5):
    """松针团：两三块错开的淡色团（透明水彩，轮廓参差）+ 一团深色的核 + 密密放射的针形细笔，上沿缀白霜。"""
    ry = rx * flat
    for k in range(2 if rx < 30 else 3):
        ox, oy = U(r, -0.3, 0.3) * rx, U(r, -0.2, 0.15) * ry
        sc = U(r, 0.62, 0.9)
        n = 12
        pts = []
        for a in np.linspace(0, 2 * math.pi, n, endpoint=False):
            j = U(r, 0.72, 1.2)
            pts.append((cx + ox + math.cos(a) * rx * j * sc, cy + oy + math.sin(a) * ry * j * sc * (0.95 if math.sin(a) < 0 else 0.62)))
        wash(L, pts, mix(col, dark, U(r, 0.05, 0.5)), op=(0.5 if rx >= 26 else 0.78) * op, wob=rx * 0.05 + 1, seed=int(r.integers(1e6)), smooth=2, tex_k=0.3, rim=0.22, rim_w=2.5)
    # 深色的核
    core = [(cx + math.cos(a) * rx * 0.28 * U(r, 0.7, 1.2), cy + 0.1 * ry + math.sin(a) * ry * 0.3 * U(r, 0.7, 1.2)) for a in np.linspace(0, 2 * math.pi, 7, endpoint=False)]
    wash(L, core, dark, op=0.55 * op, wob=1.0, seed=int(r.integers(1e6)), smooth=2, tex_k=0.2, rim=0.1)
    # 放射的松针：上半扇形（长）+ 向下垂的短针
    cnt = int(max(rx * 3.4, 22)) if rx >= 26 else int(max(rx * 1.7, 9))
    st, st2 = [], []
    for _ in range(cnt):
        up = r.random() < 0.7
        u_ = U(r, -1, 1)
        a = (-math.pi / 2 + math.copysign(1, u_) * (math.pi / 2) * (abs(u_) ** 0.6) * 1.02) if up else U(r, 0.05, math.pi - 0.05)
        lenk = U(r, 0.5, 1.18) if up else U(r, 0.25, 0.75) * (0.6 + droop)
        sx, sy = cx + math.cos(a) * rx * 0.1, cy + math.sin(a) * ry * 0.1
        ex, ey = cx + math.cos(a) * rx * lenk, cy + math.sin(a) * ry * lenk * (1.0 if up else 1.7)
        wd = max(U(r, 0.9, 1.9) * min(1.0, rx / 45 + 0.4), 0.8)
        (st if r.random() < 0.72 else st2).append((sx, sy, ex, ey, wd, U(r, 0.4, 0.9) * op))
    flicks(L, st, color=dark)
    flicks(L, st2, color=mix(col, dark, 0.15))
    if frost_k > 0:
        fp = []
        for _ in range(int(rx * 0.7 * frost_k) + 3):
            a = U(r, -math.pi * 1.02, 0.02)
            q = U(r, 0.3, 1.0)
            fp.append((cx + math.cos(a) * rx * q * 0.95, cy + math.sin(a) * ry * q * 0.95 + U(r, -1, 3)))
        frost(L, fp, op=0.92 * op * min(frost_k, 1.0), size=(max(1.6, rx * 0.04), max(2.8, rx * 0.075)), seed=int(r.integers(1e6)), ln=(max(3, rx * 0.06), max(6, rx * 0.18)))


def bark_scales(L, pts, wd, r, col, op=0.5, step=9):
    """鳞片状的树皮皴：沿树干中线，每隔一小段画一对弧形短笔（松皮）。pts 是树干中线（密点）。"""
    st = []
    for i in range(0, len(pts) - 1, 1):
        if r.random() > 0.7:
            continue
        x, y = pts[i]
        w = wd[i]
        for s_ in (-1, 1):
            if r.random() < 0.6:
                ox = x + s_ * w * U(r, 0.05, 0.4)
                ln = U(r, 0.35, 0.9) * w
                st.append((ox - ln * 0.4, y, ox + ln * 0.5, y + U(r, 2, 6), U(r, 0.8, 1.8), U(r, 0.3, 0.8) * op))
    flicks(L, st, color=col)


def trunk_curve(p0, p1, bend, n=24, wob=0.0, seed=0, lean_pow=1.0):
    """从 p0 到 p1 的弯曲树干中线（带 S 形弯）。返回 (pts[n,2])。"""
    r = np.random.default_rng(seed)
    t = np.linspace(0, 1, n, dtype=F)
    x = p0[0] + (p1[0] - p0[0]) * t ** lean_pow + bend * np.sin(t * math.pi * 1.6 + r.uniform(0, 1.2)) * (1 - t * 0.3)
    y = p0[1] + (p1[1] - p0[1]) * t
    return np.stack([x, y], 1).astype(F)


def pine_ink(L, x, y, h, seed=0, col=None, dark=None, frost_k=0.0, lean=0.0, op=1.0, nb=None, spread=0.4, trunk_col=None, flat=0.42, crown=1.0, bare=0.17, bend=0.07):
    """水墨的松：S 形弯曲、下粗上细的干（鳞皴、枯枝桩）+ 一层层横出的虬枝（有的上扬有的下垂）+ 枝头一团团放射的松针 + 偏向一侧的树冠。
    x,y 是树脚，h 树高。frost_k>0：松针团上缀白霜。"""
    col = N['pine'] if col is None else np.asarray(col, F)
    dark = N['pine_dk'] if dark is None else np.asarray(dark, F)
    tc = N['wood_dk'] * 0.55 if trunk_col is None else np.asarray(trunk_col, F)
    r = np.random.default_rng(seed)
    side0 = 1 if r.random() < 0.5 else -1
    tw = max(h * 0.046, 2.4)
    n = 28
    t = np.linspace(0, 1, n, dtype=F)
    ph = r.uniform(0, 1.5)
    xo = h * bend * side0 * (np.sin(t * math.pi * 1.5 + ph) - math.sin(ph)) + h * bend * 0.35 * np.sin(t * math.pi * 3.1 + ph * 2) * t
    pts = np.stack([x + lean * h * t ** 1.15 + xo, y - h * 0.97 * t], 1).astype(F)
    wid = tw * (1.0 - 0.72 * t ** 0.8) + tw * 0.5 * np.clip(1 - t / 0.08, 0, 1)
    brush(L, pts, w0=tw * 1.3, w1=max(tw * 0.28, 1.0), color=tc, op=0.92 * op, seed=seed, wob=h * 0.006, taper=0.05)
    brush(L, pts + np.array([tw * 0.3, 0], F), w0=tw * 0.35, w1=0.8, color=tc * 0.5, op=0.45 * op, seed=seed + 1, wob=h * 0.006, taper=0.1, dry=0.25)
    brush(L, pts + np.array([-tw * 0.3, 0], F), w0=tw * 0.2, w1=0.6, color=N['stone_lt'] * 0.7, op=0.35 * op, seed=seed + 2, wob=h * 0.006, taper=0.2, dry=0.5)
    if h > 120:
        bark_scales(L, pts, wid, r, INK, op=0.55 * op)
    nb = nb or (4 + int(h / 75))
    nb = min(nb, 10)
    if h < 200:
        bare = min(bare, 0.12)
    for k in range(nb):
        f = bare + (0.93 - bare) * (k + U(r, 0.0, 0.8)) / nb
        f = min(f, 0.93)
        i = int(f * (len(pts) - 1))
        tx, ty = pts[i]
        side = (-1 if (k + (side0 > 0)) % 2 == 0 else 1)
        if r.random() < 0.2:
            side = -side
        ln = h * spread * U(r, 0.6, 1.25) * (1.2 - 0.75 * f)
        mode = r.random()
        if mode < 0.3:      # 下垂的枝
            bp = [(tx, ty), (tx + side * ln * 0.4, ty + ln * 0.02), (tx + side * ln * 0.75, ty + ln * 0.14), (tx + side * ln, ty + ln * 0.24)]
        elif mode < 0.6:    # 上扬的枝
            bp = [(tx, ty), (tx + side * ln * 0.4, ty - ln * 0.02), (tx + side * ln * 0.75, ty - ln * 0.12), (tx + side * ln, ty - ln * 0.26)]
        else:               # 平出再微微上翘
            bp = [(tx, ty), (tx + side * ln * 0.4, ty + ln * 0.04), (tx + side * ln * 0.72, ty + ln * 0.06), (tx + side * ln, ty - ln * 0.08)]
        brush(L, bp, w0=max(wid[i] * 0.55, 1.3), w1=max(tw * 0.1, 0.8), color=tc, op=0.88 * op, seed=int(r.integers(1e6)), wob=ln * 0.02, taper=0.12, dry=0.1)
        rx = h * U(r, 0.075, 0.115) * (1.15 - 0.4 * f) * (1 + max(0.0, (220 - h) / 220) * 0.7) + 4
        needle_pom(L, bp[-1][0], bp[-1][1] - rx * 0.1, rx, r, col, dark, frost_k=frost_k, op=op, flat=flat)
        if ln > h * 0.12 and r.random() < 0.75:
            mx, my = bp[2][0], bp[2][1]
            needle_pom(L, mx, my - rx * 0.08, rx * 0.62, r, col, dark, frost_k=frost_k, op=op, flat=flat)
        if r.random() < 0.3:    # 枯枝桩
            brush(L, [(tx, ty), (tx - side * ln * 0.12, ty - ln * 0.08)], w0=max(tw * 0.18, 1.1), w1=0.6, color=tc, op=0.8 * op, seed=int(r.integers(1e6)), taper=0.3, wob=0.4)
    # 树冠：偏向一侧的几团
    cx, cy = pts[-1]
    rr = h * 0.15 * crown + 5
    needle_pom(L, cx, cy + rr * 0.05, rr, r, col, dark, frost_k=frost_k, op=op, flat=flat * 1.1)
    needle_pom(L, cx + side0 * rr * 1.1, cy + rr * 0.6, rr * 0.75, r, col, dark, frost_k=frost_k, op=op, flat=flat)
    needle_pom(L, cx - side0 * rr * 0.9, cy + rr * 0.9, rr * 0.6, r, col, dark, frost_k=frost_k, op=op, flat=flat)


# ───────────────────────── 杉 / 柏 / 桦 ─────────────────────────
def fir_ink(L, x, y, h, seed=0, col=None, dark=None, frost_k=0.0, lean=0.0, op=1.0, trunk_col=None):
    """杉：又高又瘦、不对称。每层枝是一条下弯的墨笔，枝下挂一串短针（笔触），层与层高低错落、长短不齐，树顶歪着；
    枝梢缀霜。不是圣诞树：轮廓参差，底部露出一截树干。"""
    col = N['pine'] if col is None else np.asarray(col, F)
    dark = N['pine_dk'] if dark is None else np.asarray(dark, F)
    tc = N['wood_dk'] * 0.5 if trunk_col is None else np.asarray(trunk_col, F)
    r = np.random.default_rng(seed)
    tw = max(h * 0.03, 2.0)
    pts = trunk_curve((x, y), (x + lean * h, y - h), h * 0.022 * (1 if r.random() < 0.5 else -1), 22, seed=seed)
    brush(L, pts, w0=tw, w1=max(tw * 0.2, 0.9), color=tc, op=0.9 * op, seed=seed, wob=h * 0.004, taper=0.04)
    sc = min(1.0, h / 200 + 0.35)
    # 先罩一层淡的灰绿，让枝丛连成片（水彩的积色），形状不规则
    for k in range(4):
        f0 = 0.26 + 0.17 * k + U(r, -0.03, 0.03)
        i = int(min(f0, 0.97) * (len(pts) - 1))
        tx, ty = pts[i]
        ww = h * 0.15 * (1 - f0) ** 0.9 + 4
        poly = [(tx - ww * U(r, 0.5, 1.0), ty - h * 0.03), (tx + ww * U(r, -0.2, 0.2), ty - h * 0.15), (tx + ww * U(r, 0.5, 1.0), ty - h * 0.02), (tx + ww * U(r, 0.6, 1.0), ty + h * 0.1), (tx + ww * 0.2, ty + h * 0.15), (tx - ww * U(r, 0.6, 1.0), ty + h * 0.12)]
        wash(L, poly, mix(col, dark, U(r, 0.3, 0.6)), op=0.42 * op, wob=3, seed=int(r.integers(1e6)), smooth=2, tex_k=0.3, rim=0.22)
    nb = int(h / 13)
    st, st2, fr = [], [], []
    for k in range(nb):
        f = 0.16 + 0.8 * (k / nb) + U(r, -0.012, 0.012)
        i = int(min(f, 0.99) * (len(pts) - 1))
        tx, ty = pts[i]
        wid = h * (0.17 * (1 - f) ** 0.85 + 0.01) * U(r, 0.5, 1.25)   # 越往上越窄，但参差
        if r.random() < 0.15:
            wid *= 0.4
        for s_ in (-1, 1):
            if r.random() < 0.1:
                continue
            w_ = wid * U(r, 0.5, 1.1)
            sag = w_ * U(r, 0.35, 0.8)
            mx_, my_ = tx + s_ * w_ * 0.55, ty + sag * 0.12
            ex, ey = tx + s_ * w_, ty + sag
            brush(L, [(tx, ty), (mx_, my_), (ex, ey)], w0=1.7 * sc, w1=0.7, color=dark, op=U(r, 0.5, 0.9) * op, seed=int(r.integers(1e6)), taper=0.25, wob=0.5)
            # 枝下挂的一串短针
            for j in range(int(w_ / 7) + 1):
                q = U(r, 0.25, 1.0)
                px, py = tx + (mx_ - tx) * min(q * 2, 1) + (ex - mx_) * max(q * 2 - 1, 0), ty + (my_ - ty) * min(q * 2, 1) + (ey - my_) * max(q * 2 - 1, 0)
                ln = U(r, 5, 15) * sc * (0.6 + wid / (h * 0.1))
                st.append((px, py, px + s_ * U(r, 0, 3), py + ln, U(r, 1.0, 2.0) * sc, U(r, 0.4, 0.85) * op))
            if frost_k > 0 and r.random() < 0.8 * frost_k:
                for q in (0.4, 0.7, 1.0):
                    fr.append((tx + s_ * w_ * q, ty + sag * q * q - 1.5))
    flicks(L, st, color=dark)
    if frost_k > 0:
        frost(L, fr, op=0.9 * min(frost_k, 1), size=(1.6 * sc + 0.4, 3.2 * sc + 0.6), seed=seed + 4, ln=(3, 8))
    # 树尖：几根细笔，歪着
    tx, ty = pts[-1]
    brush(L, [(tx, ty + h * 0.06), (tx + h * 0.01, ty), (tx + h * 0.02 * (1 if r.random() < 0.5 else -1), ty - h * 0.05)], w0=2.0 * sc, w1=0.6, color=dark, op=0.85 * op, seed=seed + 9, taper=0.3, wob=0.6)


def cypress_ink(L, x, y, h, seed=0, col=None, dark=None, frost_k=0.0, op=1.0, lean=0.0, trunk_col=None):
    """柏：粗壮的柱状树冠，浓暗的团块叠成一条“烟柱”，虬曲，冠上杂着枯枝；缀霜。"""
    col = N['pine'] if col is None else np.asarray(col, F)
    dark = N['pine_dk'] if dark is None else np.asarray(dark, F)
    tc = N['wood_dk'] * 0.5 if trunk_col is None else np.asarray(trunk_col, F)
    r = np.random.default_rng(seed)
    tw = max(h * 0.05, 2.6)
    pts = trunk_curve((x, y), (x + lean * h, y - h * 0.94), h * 0.03, 20, seed=seed)
    brush(L, pts, w0=tw, w1=max(tw * 0.3, 1.0), color=tc, op=0.92 * op, seed=seed, wob=h * 0.005, taper=0.04)
    n = int(h / 42) + 3
    for k in range(n):
        f = 0.2 + 0.78 * k / (n - 1)
        i = int(min(f, 0.98) * (len(pts) - 1))
        tx, ty = pts[i]
        rx = h * (0.1 * (1 - f * 0.6)) * U(r, 0.75, 1.2) + 4
        ry = rx * U(r, 1.1, 1.7)
        ox = r.normal(0, rx * 0.25)
        pp = [(tx + ox + math.cos(a) * rx * U(r, 0.8, 1.15), ty + math.sin(a) * ry * U(r, 0.8, 1.15)) for a in np.linspace(0, 2 * math.pi, 10, endpoint=False)]
        wash(L, pp, mix(col, dark, U(r, 0.2, 0.7)), op=0.78 * op, wob=2.2, seed=int(r.integers(1e6)), smooth=2, tex_k=0.3, rim=0.25, rim_w=3)
        st = []
        for _ in range(int(rx * 1.2)):
            a = U(r, 0, 2 * math.pi)
            q = U(r, 0.6, 1.1)
            px, py = tx + ox + math.cos(a) * rx * q, ty + math.sin(a) * ry * q
            st.append((px, py, px + r.normal(0, 3), py + U(r, 3, 9), U(r, 1.2, 2.4), U(r, 0.3, 0.8) * op))
        flicks(L, st, color=dark)
        if frost_k > 0:
            fp = [(tx + ox + math.cos(a) * rx * U(r, 0.55, 1.0), ty + math.sin(a) * ry * U(r, 0.55, 1.0)) for a in [U(r, -math.pi * 1.0, -0.05) for _ in range(int(rx * 0.4 * frost_k) + 2)]]
            frost(L, fp, op=0.85 * min(frost_k, 1), size=(1.6, 3.4), seed=int(r.integers(1e6)), ln=(3, 7))
    # 顶上几根枯枝
    topx, topy = pts[-1]
    for s_ in (-1, 0, 1):
        brush(L, [(topx, topy + 10), (topx + s_ * h * 0.03, topy - h * 0.04), (topx + s_ * h * 0.05 + r.normal(0, 3), topy - h * 0.09)], w0=2.0, w1=0.7, color=tc, op=0.8 * op, seed=int(r.integers(1e6)), taper=0.3, wob=0.8)


def birch_ink(L, x, y, h, seed=0, col=None, frost_k=0.0, op=1.0, lean=0.0, twigs=1.0):
    """桦：白的树干（纸白）+ 横向的黑斑（桦皮的眼）+ 细而斜上、参差不齐的枯枝，枝上缀霜。"""
    r = np.random.default_rng(seed)
    pale = mix(N['paper'], N['stone_lt'], 0.3) if col is None else np.asarray(col, F)
    tw = max(h * 0.03, 2.4)
    pts = trunk_curve((x, y), (x + lean * h, y - h), h * 0.016 * (1 if r.random() < 0.5 else -1), 20, seed=seed)
    brush(L, pts, w0=tw, w1=max(tw * 0.35, 1.0), color=pale, op=0.95 * op, seed=seed, wob=h * 0.003, taper=0.03)
    brush(L, pts + np.array([tw * 0.28, 0], F), w0=tw * 0.32, w1=0.8, color=N['stone'] * 0.6, op=0.55 * op, seed=seed + 1, wob=h * 0.003, taper=0.1, dry=0.2)
    st = []
    for i in range(1, len(pts) - 1):
        for _ in range(int(r.integers(0, 3))):
            px, py = pts[i]
            wdt = tw * (1.0 - 0.65 * i / len(pts))
            ox = U(r, -0.4, 0.4) * wdt
            ln = U(r, 0.45, 1.0) * wdt
            st.append((px + ox - ln / 2, py + U(r, -4, 4), px + ox + ln / 2, py + U(r, -3, 3), U(r, 1.4, 3.0) * min(1, tw / 5), U(r, 0.55, 0.95) * op))
    flicks(L, st, color=INK)
    fr = []
    nt = int(h / 16 * twigs)
    for _ in range(nt):
        f = U(r, 0.3, 0.99) ** 0.8
        i = int(f * (len(pts) - 1))
        tx, ty = pts[i]
        s_ = 1 if r.random() < 0.5 else -1
        ln = h * U(r, 0.05, 0.2) * (1.15 - 0.6 * f)
        ang = -math.pi / 2 + s_ * U(r, 0.35, 1.25)          # 斜上
        mx_, my_ = tx + math.cos(ang) * ln * 0.55 + r.normal(0, 2), ty + math.sin(ang) * ln * 0.55
        ex, ey = mx_ + math.cos(ang + s_ * U(r, -0.3, 0.5)) * ln * 0.5, my_ + math.sin(ang + s_ * U(r, -0.3, 0.5)) * ln * 0.5
        brush(L, [(tx, ty), (mx_, my_), (ex, ey)], w0=max(0.42 * tw, 1.1), w1=0.5, color=INK, op=U(r, 0.5, 0.85) * op, seed=int(r.integers(1e6)), taper=0.25, wob=0.5)
        if r.random() < 0.55:
            ex2, ey2 = ex + s_ * ln * 0.25, ey - ln * 0.25
            brush(L, [(mx_, my_), ((mx_ + ex2) / 2, (my_ + ey2) / 2 - 2), (ex2, ey2)], w0=0.9, w1=0.5, color=INK, op=U(r, 0.4, 0.7) * op, seed=int(r.integers(1e6)), taper=0.3, wob=0.4)
        if frost_k > 0 and r.random() < frost_k:
            for q in (0.55, 1.0):
                fr.append((tx + (ex - tx) * q, ty + (ey - ty) * q - 1.5))
    if frost_k > 0:
        frost(L, fr, op=0.92 * min(frost_k, 1), size=(1.5, 3), seed=seed + 8, ln=(3, 7))


def plum_ink(L, x, y, h, seed=0, col=None, snow=0.8, op=1.0, trunk_w=None, flower=None, roots=True):
    """老梅：虬曲的粗干（皴、一侧深色、苔点）+ 折线般硬朗的枝（倒“之”字、斜出）+ 枝上积雪；flower=(x,y) 处一朵小白花。"""
    col = N['wood_dk'] * 0.55 if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    tw = trunk_w or h * 0.085

    def twig(px, py, ang, ln, wd, d, maxd):
        # 折线般的枝：每一小段方向有 ±0.45 rad 的变化
        n = 4
        pts = [(px, py)]
        a = ang
        cx_, cy_ = px, py
        for k in range(n):
            a += r.normal(0, 0.38)
            a = a * 0.9 + (-math.pi / 2) * 0.1 * (1 if d > 1 else 0)   # 渐渐向上
            cx_ += math.cos(a) * ln / n
            cy_ += math.sin(a) * ln / n
            pts.append((cx_, cy_))
        brush(L, pts, w0=wd, w1=max(wd * 0.45, 0.9), color=col, op=0.95 * op, seed=int(r.integers(1e6)), wob=ln * 0.02, taper=0.1 if d < 2 else 0.3, dry=0.0, smooth=(r.random() < 0.5))
        if wd > 4.5:
            brush(L, [(p[0] + wd * 0.2, p[1]) for p in pts], w0=wd * 0.3, w1=0.8, color=col * 0.5, op=0.5 * op, seed=int(r.integers(1e6)), wob=ln * 0.02, taper=0.2, dry=0.25)
        if snow > 0 and wd > 1.5:
            for q in np.linspace(0.15, 0.95, 3):
                i = min(int(q * n), n - 1)
                sx = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * (q * n - i)
                sy = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * (q * n - i)
                if r.random() < 0.75:
                    L_ = U(r, 10, 24) * (0.6 + wd / 12)
                    brush(L, [(sx - L_ / 2, sy - wd * 0.4 + 1), (sx, sy - wd * 0.5 - 1.5), (sx + L_ / 2, sy - wd * 0.3 + 1)], w0=max(wd * 0.55, 2.4), w1=None, color=N['snow'], op=snow * op, seed=int(r.integers(1e6)), taper=0.4, wob=0.5)
        if d >= maxd:
            return
        for s_ in (-1, 1):
            if r.random() < 0.8:
                twig(cx_, cy_, a + s_ * U(r, 0.35, 0.95), ln * U(r, 0.55, 0.78), wd * 0.6, d + 1, maxd)
        if r.random() < 0.4:
            twig(cx_, cy_, a + r.normal(0, 0.15), ln * 0.6, wd * 0.5, d + 1, maxd)

    # 树干：S 形，向一侧倾；底部盘根
    pts = trunk_curve((x, y), (x + h * 0.04, y - h * 0.42), tw * 0.9, 16, seed=seed)
    brush(L, pts, w0=tw * 1.55, w1=tw * 0.9, color=col, op=0.97 * op, seed=seed, wob=2.5, taper=0.04)
    brush(L, pts + np.array([tw * 0.4, 0], F), w0=tw * 0.55, w1=tw * 0.3, color=col * 0.5, op=0.55 * op, seed=seed + 3, wob=2.5, taper=0.1, dry=0.2)
    brush(L, pts - np.array([tw * 0.45, 0], F), w0=tw * 0.3, w1=tw * 0.15, color=N['stone_lt'] * 0.6, op=0.4 * op, seed=seed + 4, wob=2.5, taper=0.1, dry=0.5)
    for s_ in ((-1, 1) if roots else ()):
        brush(L, [(x + s_ * tw * 0.4, y - 10), (x + s_ * tw * 1.0, y + 3), (x + s_ * tw * 1.9, y + 8)], w0=tw * 0.55, w1=2, color=col, op=0.88 * op, seed=seed + 5 + s_, wob=2.0, taper=0.1)
    st = []
    for _ in range(int(h * 0.28)):
        t = U(r, 0.0, 0.8)
        i = int(t * (len(pts) - 1))
        px = pts[i][0] + U(r, -tw * 0.7, 0.7 * tw)
        py = pts[i][1]
        st.append((px, py, px + r.normal(0, 2), py - U(r, 6, 22), U(r, 0.9, 1.8), U(r, 0.25, 0.65) * op))
    flicks(L, st, color=col * 0.4)
    # 树洞（墨点）
    hx, hy = pts[4][0] - tw * 0.1, pts[4][1]
    wash(L, [(hx - 7, hy - 18), (hx + 6, hy - 14), (hx + 8, hy + 8), (hx - 4, hy + 14), (hx - 9, hy)], INK * 0.8, op=0.7 * op, wob=1.2, seed=seed + 9, smooth=2)
    ex, ey = pts[-1]
    # 主枝：三四根，向上斜出
    for s_, ang, ln in ((-1, -math.pi / 2 - 0.9, h * 0.34), (0, -math.pi / 2 - 0.15, h * 0.4), (1, -math.pi / 2 + 0.7, h * 0.36), (1, -math.pi / 2 + 1.25, h * 0.3)):
        twig(ex + s_ * tw * 0.2, ey + 4, ang, ln, tw * 0.62, 1, 4)
    # 低处再出两根横枝
    for s_, hf in ((-1, 0.24), (1, 0.3)):
        i = int(hf / 0.42 * (len(pts) - 1))
        twig(pts[i][0], pts[i][1], -math.pi / 2 + s_ * 1.2, h * 0.3, tw * 0.45, 1, 3)
    if flower is not None:
        fx, fy = flower
        flower_small(L, fx, fy, 11, seed=seed + 20)


def flower_small(L, x, y, r_, seed=0, col=None):
    """一朵小白花（梅）：五瓣白色水彩小圆 + 花心几点淡墨 + 细蕊。"""
    col = hexc('#f4f1ea') if col is None else np.asarray(col, F)
    rng = np.random.default_rng(seed)
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5 + U(rng, -0.1, 0.1)
        px, py = x + math.cos(a) * r_ * 0.72, y + math.sin(a) * r_ * 0.72
        pp = [(px + math.cos(t) * r_ * 0.62 * U(rng, 0.9, 1.1), py + math.sin(t) * r_ * 0.6 * U(rng, 0.9, 1.1)) for t in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
        wash(L, pp, col, op=0.98, wob=0.4, seed=int(rng.integers(1e6)), smooth=2, tex_k=0.04, rim=0.28, rim_w=1.5)
    for k in range(7):
        a = k * 2 * math.pi / 7
        brush(L, [(x, y), (x + math.cos(a) * r_ * 0.55, y + math.sin(a) * r_ * 0.55)], w0=0.9, color=INK, op=0.6, seed=int(rng.integers(1e6)), smooth=False, taper=0.3)
        dots(L, [(x + math.cos(a) * r_ * 0.6, y + math.sin(a) * r_ * 0.6, 0.9)], INK, op=0.6)


def tree_trunk(L, x, y_top, y_bot, w_bot, w_top=None, seed=0, col=None, op=1.0, lean=0.0, bark=1.0, frost_k=0.0, moss=0.0, mid_col=None):
    """近景的粗树干：竖直通天，墨色，竖向的树皮皴 + 裂纹 + 一侧受光的淡边 + 疤。可挂白霜 / 积雪的痕。x 为树干中线。"""
    col = N['wood_dk'] * 0.5 if col is None else np.asarray(col, F)
    w_top = w_bot * 0.8 if w_top is None else w_top
    r = np.random.default_rng(seed)
    n = 14
    t = np.linspace(0, 1, n)
    ys = y_bot + (y_top - y_bot) * t
    xs = x + lean * (y_bot - ys) + np.sin(t * 5 + seed) * w_bot * 0.04
    ws = w_bot + (w_top - w_bot) * t
    left = [(xs[i] - ws[i] / 2 + r.normal(0, 1.5), ys[i]) for i in range(n)]
    right = [(xs[i] + ws[i] / 2 + r.normal(0, 1.5), ys[i]) for i in range(n)]
    poly = left + right[::-1]
    wash(L, poly, col, op=0.97 * op, wob=1.6, seed=seed, smooth=1, tex_k=0.3, rim=0.3, rim_w=4)
    # 受光侧的灰边（月光）
    wash(L, [(xs[i] - ws[i] / 2 + ws[i] * 0.04, ys[i]) for i in range(n)] + [(xs[i] - ws[i] / 2 + ws[i] * 0.2, ys[i]) for i in range(n)][::-1], mix(col, N['stone_lt'], 0.45), op=0.5 * op, wob=1.5, seed=seed + 1, smooth=1, tex_k=0.3, rim=0.0)
    # 背光侧压暗
    wash(L, [(xs[i] + ws[i] / 2 - ws[i] * 0.3, ys[i]) for i in range(n)] + [(xs[i] + ws[i] / 2, ys[i]) for i in range(n)][::-1], INK * 0.7, op=0.5 * op, wob=1.5, seed=seed + 2, smooth=1, tex_k=0.3, rim=0.0)
    st = []
    for _ in range(int(abs(y_bot - y_top) * w_bot / 160 * bark)):
        tt = r.random()
        i = min(int(tt * (n - 1)), n - 2)
        px = xs[i] + U(r, -0.46, 0.46) * ws[i]
        py = ys[i]
        ln = U(r, 20, 90)
        st.append((px, py, px + r.normal(0, 3), py - ln, U(r, 1.0, 2.6), U(r, 0.2, 0.7) * op))
    flicks(L, st, color=INK)
    st2 = []
    for _ in range(int(abs(y_bot - y_top) * w_bot / 500 * bark)):
        tt = r.random()
        i = min(int(tt * (n - 1)), n - 2)
        px = xs[i] + U(r, -0.4, 0.4) * ws[i]
        py = ys[i]
        ln = U(r, 10, 40)
        st2.append((px, py, px + r.normal(0, 3), py - ln, U(r, 1.0, 2.0), U(r, 0.2, 0.5) * op))
    flicks(L, st2, color=N['stone_lt'] * 0.8)
    # 裂纹（粗的断续墨线）
    for _ in range(int(3 + w_bot / 30)):
        px = x + U(r, -0.4, 0.4) * w_bot
        py0 = U(r, y_top, y_bot - 80)
        ln = U(r, 120, 380)
        brush(L, [(px, py0), (px + r.normal(0, 4), py0 + ln * 0.5), (px + r.normal(0, 7), py0 + ln)], w0=U(r, 2.2, 4.5), w1=1.0, color=INK, op=U(r, 0.4, 0.75) * op, seed=int(r.integers(1e6)), taper=0.3, dry=0.3, wob=1.5)
    # 轮廓
    brush(L, left, w0=3.5, color=INK, op=0.75 * op, seed=seed + 4, wob=1.2, taper=0.05, dry=0.35)
    brush(L, right, w0=3.5, color=INK, op=0.75 * op, seed=seed + 5, wob=1.2, taper=0.05, dry=0.35)
    if frost_k > 0:
        fp = []
        for _ in range(int(abs(y_bot - y_top) * w_bot / 700 * frost_k)):
            tt = r.random()
            i = min(int(tt * (n - 1)), n - 2)
            fp.append((xs[i] + U(r, -0.45, 0.45) * ws[i], ys[i]))
        frost(L, fp, op=0.85, size=(2.5, 5), seed=seed + 6, ln=(5, 14))


# ───────────────────────── 灌木 / 枯草 / 草叶 ─────────────────────────
def bush(L, cx, by, w, h, seed=0, col=None, dark=None, op=1.0, frost_k=0.0, bare=False):
    """一丛灌木：几团暗色 + 点苔；bare=True 是冬天的枯枝丛（细枝乱出）。"""
    col = N['pine'] if col is None else np.asarray(col, F)
    dark = N['pine_dk'] if dark is None else np.asarray(dark, F)
    r = np.random.default_rng(seed)
    if bare:
        fr = []
        for _ in range(int(w / 5)):
            sx = cx + U(r, -w * 0.35, w * 0.35)
            a = -math.pi / 2 + r.normal(0, 0.55)
            ln = U(r, 0.4, 1.0) * h
            ex, ey = sx + math.cos(a) * ln, by + math.sin(a) * ln
            brush(L, [(sx, by), ((sx + ex) / 2 + r.normal(0, 4), (by + ey) / 2), (ex, ey)], w0=U(r, 1.4, 2.6), w1=0.6, color=dark, op=U(r, 0.5, 0.9) * op, seed=int(r.integers(1e6)), taper=0.3, wob=0.8)
            if r.random() < 0.7:
                fr.append((ex, ey))
        if frost_k > 0:
            frost(L, fr, op=0.9, size=(1.5, 2.8), seed=seed + 3)
        return
    n = max(int(w / 40), 2)
    for i in range(n):
        px = cx + (i - (n - 1) / 2) * w / n * 0.9 + r.normal(0, w * 0.03)
        rx = w / n * U(r, 0.65, 0.95)
        ry = h * U(r, 0.45, 0.8)
        pts = [(px + math.cos(a) * rx * U(r, 0.82, 1.1), by - ry * 0.5 + math.sin(a) * ry * 0.5 * U(r, 0.8, 1.1)) for a in np.linspace(0, 2 * math.pi, 10, endpoint=False)]
        wash(L, pts, mix(col, dark, U(r, 0.1, 0.6)), op=0.85 * op, wob=1.8, seed=int(r.integers(1e6)), smooth=2, tex_k=0.3, rim=0.25, rim_w=2.5)
        st = []
        for _ in range(int(rx * 0.7)):
            a = U(r, math.pi, 2 * math.pi)
            q = U(r, 0.6, 1.1)
            qx, qy = px + math.cos(a) * rx * q, by - ry * 0.5 + math.sin(a) * ry * 0.5 * q
            st.append((qx, qy, qx + r.normal(0, 2), qy + U(r, 2, 6), U(r, 1.2, 2.4), U(r, 0.4, 0.85) * op))
        flicks(L, st, color=dark)
        if frost_k > 0:
            frost(L, [(px + math.cos(a) * rx * U(r, 0.5, 1.0), by - ry * 0.5 + math.sin(a) * ry * 0.5 * U(r, 0.5, 1.0)) for a in [U(r, math.pi * 1.05, math.pi * 1.95) for _ in range(int(rx * 0.25))]], op=0.85, size=(1.6, 3), seed=int(r.integers(1e6)))


def dry_grass(L, x0, x1, y_arr, n, seed=0, col=None, op=0.8, hmin=24, hmax=70, frost_k=0.0, lean=0.25, tip_col=None):
    """枯草丛：一束束向上略弯、有点分叉的细笔，穗头缀霜。y_arr 是每列地面 y（也可以是常数）。"""
    col = N['earth_dk'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    ya = np.broadcast_to(np.asarray(y_arr, F), (L.w,)) if np.ndim(y_arr) == 0 else np.asarray(y_arr, F)
    st, fr = [], []
    for _ in range(n):
        x = U(r, x0, x1)
        y = float(ya[int(min(max(x, 0), len(ya) - 1))]) + U(r, 0, 12)
        for k in range(int(r.integers(4, 10))):
            ln = U(r, hmin, hmax)
            a = -math.pi / 2 + r.normal(0, 0.35) + lean * r.normal(0, 1)
            sx = x + U(r, -6, 6)
            ex, ey = sx + math.cos(a) * ln, y + math.sin(a) * ln
            mx_, my_ = (sx + ex) / 2 + r.normal(0, ln * 0.08), (y + ey) / 2
            st.append((sx, y, mx_, my_, U(r, 1.0, 1.9), U(r, 0.3, 0.8) * op))
            st.append((mx_, my_, ex, ey, U(r, 0.8, 1.5), U(r, 0.3, 0.8) * op))
            if frost_k > 0 and r.random() < 0.6 * frost_k:
                fr.append((ex, ey - 1))
    flicks(L, st, color=col)
    if frost_k > 0:
        frost(L, fr, op=0.9, size=(1.4, 2.8), seed=seed + 5, ln=(2.5, 6))


def grass_blades(L, x0, x1, y0, y1, n, seed=0, col=None, op=0.7, hmin=12, hmax=40, lean=0.18):
    """草原的草：一片片细长的叶，向上略弯。散布在 [x0,x1]×[y0,y1]。远处（y 小）的更短更淡。"""
    col = N['grass_dk'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    st = []
    for _ in range(n):
        x = U(r, x0, x1)
        d = r.random()
        y = y0 + (y1 - y0) * d
        s = 0.5 + 0.9 * d
        ln = U(r, hmin, hmax) * s
        a = -math.pi / 2 + r.normal(0, 0.28) + lean
        ex, ey = x + math.cos(a) * ln, y + math.sin(a) * ln
        st.append((x, y, ex, ey, U(r, 1.0, 1.9) * s, U(r, 0.25, 0.8) * op * (0.55 + 0.6 * d)))
    flicks(L, st, color=col)


def puddle(L, cx, cy, w, h, seed=0, col=None, sky_col=None, op=1.0, rim_col=None):
    """路上的水洼：椭圆的浅色水面（映一点天光）+ 边缘一圈湿暗 + 几笔横向的水纹和高光。"""
    col = N['water_dk'] if col is None else np.asarray(col, F)
    sky_col = N['far1'] if sky_col is None else np.asarray(sky_col, F)
    r = np.random.default_rng(seed)
    n = 14
    pts = [(cx + math.cos(a) * w / 2 * U(r, 0.88, 1.08), cy + math.sin(a) * h / 2 * U(r, 0.85, 1.12)) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]
    # 湿暗的外圈
    out = [(cx + (p[0] - cx) * 1.13, cy + (p[1] - cy) * 1.28) for p in pts]
    wash(L, out, N['earth_dk'] * 0.8, op=0.4 * op, wob=1.6, seed=seed + 1, smooth=2, tex_k=0.2, rim=0.0)
    wash(L, pts, col, op=0.95 * op, wob=1.0, seed=seed, smooth=2, tex_k=0.1, rim=0.3, rim_w=2.5)
    # 天光：上部浅色
    inner = [(cx + (p[0] - cx) * 0.78, cy - h * 0.06 + (p[1] - cy) * 0.5) for p in pts]
    wash(L, inner, sky_col, op=0.7 * op, wob=1.2, seed=seed + 2, smooth=2, tex_k=0.08, rim=0.0)
    for k in range(3):
        yy = cy + (k - 1) * h * 0.22
        ww = w * U(r, 0.25, 0.5)
        xx = cx + U(r, -w * 0.15, w * 0.15)
        brush(L, [(xx - ww / 2, yy), (xx + ww / 2, yy + r.normal(0, 0.6))], w0=1.4, color=N['paper'], op=U(r, 0.35, 0.7) * op, seed=int(r.integers(1e6)), taper=0.4, smooth=False)
    brush(L, pts[:n // 2 + 1], w0=1.8, color=INK, op=0.45 * op, seed=seed + 3, taper=0.2, dry=0.4, wob=0.6)


def stone_ring(L, cx, cy, d, seed=0, n=13, col=None, dark=None, light=None):
    """火塘：一圈石头围着一块焦黑的地。圈是压扁的椭圆（透视），后面的石头在上、先画；前面的在下、后画。"""
    r = np.random.default_rng(seed)
    rx, ry = d / 2, d / 2 * 0.3
    # 焦黑的灰烬地
    pts = [(cx + math.cos(a) * rx * 0.9 * U(r, 0.92, 1.05), cy + math.sin(a) * ry * 0.85 * U(r, 0.9, 1.08)) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)]
    wash(L, [(cx + (p[0] - cx) * 1.35, cy + (p[1] - cy) * 1.5) for p in pts], N['earth_dk'] * 0.7, op=0.35, wob=3, seed=seed + 1, smooth=2, tex_k=0.3, rim=0.0)
    wash(L, pts, INK * 0.7, op=0.92, wob=1.5, seed=seed, smooth=2, tex_k=0.3, rim=0.1)
    angs = np.sort(np.linspace(0, 2 * math.pi, n, endpoint=False) + r.normal(0, 0.06, n))
    order = sorted(range(n), key=lambda i: math.sin(angs[i]))   # 先画后面的（sin 小 → y 小）
    for i in order:
        a = angs[i]
        sx, sy = cx + math.cos(a) * rx, cy + math.sin(a) * ry
        w_ = U(r, 0.2, 0.3) * d * (0.9 + 0.25 * math.sin(a))
        h_ = w_ * U(r, 0.55, 0.85)
        rock(L, sx, sy + h_ * 0.35, w_, h_, seed=int(r.integers(1e6)), col=col, dark=dark, light=light, lit_dir=1, op=1.0)


# ───────────────────────── 雪 ─────────────────────────
def drift(L, x0, x1, yb, h, seed=0, op=1.0, shade=0.55, line=0.35, peak=0.5, lit_col=None, sh_col=None, bottom=None):
    """一道雪堆（雪垄）：上沿是平滑起伏的曲线（受光、白），下沿落在 yb；背阴的一侧有蓝灰的罩染；上沿一道断续的细墨线（封面里雪的画法）。
    peak∈[0,1]：最高点在 x0..x1 的相对位置。"""
    lit_col = N['snow'] if lit_col is None else np.asarray(lit_col, F)
    sh_col = N['snow_sh'] if sh_col is None else np.asarray(sh_col, F)
    r = np.random.default_rng(seed)
    n = max(int((x1 - x0) / 30), 6)
    xs = np.linspace(x0, x1, n)
    t = (xs - x0) / max(x1 - x0, 1)
    prof = np.sin(np.clip(t, 0, 1) ** (math.log(0.5) / math.log(max(min(peak, 0.95), 0.05))) * math.pi)
    prof = prof ** 0.8 * (1 + 0.1 * r.normal(0, 1, n))
    top = [(float(x), float(yb - h * max(p, 0.0))) for x, p in zip(xs, prof)]
    bottom = yb + h * 0.1 if bottom is None else bottom
    poly = top + [(x1, bottom), (x0, bottom)]
    wash(L, poly, lit_col, op=op, wob=1.6, seed=seed, smooth=2, tex_k=0.08, rim=0.1, rim_w=3)
    # 背阴：从顶线下 0.18h 起，往下一块蓝灰（偏向一侧）
    sh = [(x, y + h * 0.12 + (0.0 if i % 2 else 3.0)) for i, (x, y) in enumerate(top[int(n * 0.25):])]
    if len(sh) >= 3:
        sh_poly = sh + [(sh[-1][0], bottom), (sh[0][0], bottom)]
        wash(L, sh_poly, sh_col, op=shade * op, wob=2.2, seed=seed + 1, smooth=2, tex_k=0.12, rim=0.1, rim_w=3)
    if line > 0:
        # 断续的上沿线
        seg = 0
        while seg < n - 3:
            ln = int(r.integers(4, 9))
            sl = top[seg:seg + ln]
            if len(sl) >= 3:
                brush(L, sl, w0=U(r, 1.4, 2.4), color=N['stone_dk'], op=line * U(r, 0.5, 1.0) * op, seed=int(r.integers(1e6)), wob=0.6, taper=0.3, dry=0.35)
            seg += ln + int(r.integers(0, 3))
    # 雪面上的几道细排线（横向）
    hs = []
    for _ in range(int((x1 - x0) / 22)):
        px = U(r, x0 + (x1 - x0) * 0.1, x1 - (x1 - x0) * 0.1)
        i = min(int((px - x0) / (x1 - x0) * (n - 1)), n - 1)
        py = top[i][1] + U(r, 0.2, 0.85) * (bottom - top[i][1])
        hs.append((px, py, px + U(r, 10, 36), py + r.normal(0, 0.8), U(r, 0.9, 1.6), U(r, 0.12, 0.34) * op))
    flicks(L, hs, color=N['stone_dk'])


def snow_field(L, y_arr, bottom, seed=0, x0=0, x1=None, lit_col=None, sh_col=None, tex=1.0, ink_col=None, base_dark=0.0):
    """雪地：从 y_arr（上沿）向下铺满。颜色 = 受光的白 → 往下渐渐蓝灰；起伏的雪垄阴影、横向排线、风纹、少量沙粒点。"""
    x1 = L.w if x1 is None else x1
    W = x1 - x0
    lit_col = N['snow'] if lit_col is None else np.asarray(lit_col, F)
    sh_col = N['snow_sh'] if sh_col is None else np.asarray(sh_col, F)
    ink_col = N['stone_dk'] if ink_col is None else np.asarray(ink_col, F)
    y_arr = np.asarray(y_arr, F)[x0:x1]
    ymin = int(max(y_arr.min() - 4, 0)); ymax = int(min(bottom, L.h))
    h = ymax - ymin
    yy = np.arange(ymin, ymax, dtype=F)[:, None]
    depth = np.clip((yy - y_arr[None, :]) / max(bottom - y_arr.min(), 1), 0, 1)
    base = mix(lit_col, mix(lit_col, sh_col, 0.6), (depth ** 0.9)[..., None])
    n = fbm(h, W, seed + 2, 150, 5, 0.55, warp=50)
    stretch = fbm(h, W, seed + 7, 90, 3, 0.5)
    base = base * (0.93 + 0.12 * n[..., None]) 
    # 蓝灰的大片阴影（水渍）
    shm = np.clip((n - 0.52) * 2.4, 0, 1) * 0.55
    base = mix(base, sh_col * 0.92, shm[..., None] * 0.6)
    base = base * (1 - base_dark) + grain(h, W, seed + 4, 0.9)[..., None] * 0.012
    a = np.clip((yy - y_arr[None, :]) / 2.5, 0, 1)
    L.over(ymin, ymax, x0, x1, np.clip(base, 0, 1).astype(F), a.astype(F))
    r = np.random.default_rng(seed + 9)
    st = []
    for _ in range(int(W * (ymax - ymin) / 5200 * tex)):
        x = U(r, 0, W)
        d = r.random() ** 1.2
        y = y_arr[int(x)] + d * (bottom - y_arr[int(x)])
        ln = U(r, 12, 60) * (0.5 + d)
        st.append((x + x0, y, x + x0 + ln, y + r.normal(0, 1.2), U(r, 0.9, 1.8), U(r, 0.08, 0.26)))
    flicks(L, st, color=ink_col)
    # 沙粒/冰碴小点
    dd = []
    for _ in range(int(W * (ymax - ymin) / 26000 * tex)):
        x = U(r, 0, W)
        d = r.random()
        y = y_arr[int(x)] + 6 + d * (bottom - y_arr[int(x)])
        dd.append((x + x0, y, U(r, 0.6, 1.5)))
    dots(L, dd, ink_col, op=0.3)
    # 上沿的断续墨线
    seg = 0
    while seg < W - 30:
        ln = int(U(r, 120, 420))
        pts = np.stack([np.arange(seg, min(seg + ln, W)) + x0, y_arr[seg:seg + ln]], 1)[::16]
        if len(pts) >= 3:
            brush(L, pts, w0=U(r, 1.6, 3.0), color=ink_col, op=0.42 * U(r, 0.6, 1.0), seed=int(r.integers(1e6)), wob=0.8, taper=0.25, dry=0.35)
        seg += ln + int(U(r, -10, 80))


def snow_dust(L, x0, x1, y0, y1, n, seed=0, col=None, op=0.5):
    """飘着的、落在物上的小雪点（静态）。"""
    col = N['snow'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    dots(L, [(U(r, x0, x1), U(r, y0, y1), U(r, 1.0, 2.4)) for _ in range(n)], col, op=op)


def tracks(L, x0, x1, y, seed=0, step=44, col=None, op=0.55, wav=14, size=1.0):
    """兔子的小脚印：一串串“∴”——两只大的后脚并排在前，两只小的前脚前后错开，一跳一跳，沿一条弯曲的线向右。
    每个脚印是一个小的椭圆凹坑（蓝灰），上缘有一点亮边。"""
    col = N['snow_sh'] * 0.72 if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    x = x0
    k = 0
    while x < x1:
        yc = y + wav * math.sin(x / 90.0 + seed) + wav * 0.4 * math.sin(x / 31.0)
        hop = step * U(r, 0.85, 1.2)
        # 前脚（先落地的小脚）
        for dy_, dx_ in ((-4, 0), (4, 6)):
            px, py = x + dx_, yc + dy_
            wash(L, [(px - 4 * size, py - 2.4 * size), (px + 4 * size, py - 2.6 * size), (px + 4.6 * size, py + 2.2 * size), (px - 3.8 * size, py + 2.5 * size)], col, op=op, wob=0.4, seed=int(r.integers(1e6)), smooth=2, tex_k=0.1, rim=0.1, rim_w=1.5)
        # 后脚
        for dy_, dx_ in ((-6, hop * 0.5), (6, hop * 0.55)):
            px, py = x + dx_, yc + dy_
            wash(L, [(px - 7 * size, py - 3.4 * size), (px + 6 * size, py - 3.2 * size), (px + 7.4 * size, py + 3.2 * size), (px - 6.4 * size, py + 3.6 * size)], col, op=op * 1.05, wob=0.5, seed=int(r.integers(1e6)), smooth=2, tex_k=0.1, rim=0.1, rim_w=1.5)
        x += hop * 1.35
        k += 1


# ───────────────────────── 蛛网 ─────────────────────────
def web(L, cx, cy, R, seed=0, col=None, op=0.6, anchors=(), dew=True, dew_col=None, rays=13, spokes=9):
    """蛛网：放射的丝（不等长、略下垂）+ 螺旋的丝 + 几根锚丝 + 一串露珠（小白点，带暗边和高光）。"""
    col = N['paper'] if col is None else np.asarray(col, F)
    dew_col = N['snow'] if dew_col is None else np.asarray(dew_col, F)
    r = np.random.default_rng(seed)
    angs = np.sort(np.linspace(0, 2 * math.pi, rays, endpoint=False) + r.normal(0, 0.1, rays))
    rr = [R * U(r, 0.88, 1.05) for _ in angs]
    ends = []
    for a, rad in zip(angs, rr):
        ex, ey = cx + math.cos(a) * rad, cy + math.sin(a) * rad * 1.02 + (rad * 0.04 if math.sin(a) > 0 else 0)
        ends.append((ex, ey))
        brush(L, [(cx, cy), ((cx + ex) / 2 + r.normal(0, 0.6), (cy + ey) / 2 + 0.8), (ex, ey)], w0=1.1, color=col, op=op * U(r, 0.7, 1.0), seed=int(r.integers(1e6)), taper=0.15, wob=0.2)
    # 螺旋丝：每圈在相邻放射丝之间略微下垂（悬链）
    dewp = []
    for k in range(spokes):
        f = 0.14 + 0.86 * (k / (spokes - 1)) ** 0.95
        pts = []
        for i, a in enumerate(angs):
            pts.append((cx + math.cos(a) * rr[i] * f, cy + math.sin(a) * rr[i] * f * 1.02))
        pts.append(pts[0])
        for i in range(len(pts) - 1):
            p0, p1 = pts[i], pts[i + 1]
            if i == len(pts) - 2 and False:
                continue
            mx_, my_ = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            sag = R * 0.045 * f
            mx_ += (cx - mx_) * 0.06
            my_ += sag * 0.7
            brush(L, [p0, (mx_, my_), p1], w0=0.9, color=col, op=op * U(r, 0.55, 0.9) * (0.7 + 0.3 * f), seed=int(r.integers(1e6)), taper=0.1, wob=0.15)
            if dew:
                for q in (0.33, 0.66):
                    if r.random() < 0.45 + 0.4 * f:
                        t = q
                        bx = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * mx_ + t * t * p1[0]
                        by = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * my_ + t * t * p1[1]
                        dewp.append((bx, by, U(r, 1.6, 3.0)))
    for (px, py) in anchors:
        # 向外的锚丝，连到枝上
        i = int(np.argmin([math.hypot(px - e[0], py - e[1]) for e in ends]))
        ex, ey = ends[i]
        brush(L, [(ex, ey), ((ex + px) / 2 + r.normal(0, 1), (ey + py) / 2 + 2), (px, py)], w0=1.1, color=col, op=op * 0.9, seed=int(r.integers(1e6)), taper=0.1, wob=0.3)
    if dew:
        for (bx, by, rd) in dewp:
            dots(L, [(bx + 0.5, by + 0.8, rd * 1.15)], N['stone_dk'], op=0.35, soft=0.6)   # 露珠的暗边
            dots(L, [(bx, by, rd)], dew_col, op=0.95, soft=0.6)
            dots(L, [(bx - rd * 0.3, by - rd * 0.3, max(rd * 0.35, 0.7))], hexc('#ffffff'), op=0.9, soft=0.4)


# ───────────────────────── 器物与建筑 ─────────────────────────
def plank_wall(L, x0, y0, x1, y1, seed=0, col=None, dark=None, plank_h=46, vertical=False, op=1.0, grain_k=1.0, wear=1.0):
    """木板墙：一块块横（或竖）排的板，每块颜色略有深浅，板缝是粗细不匀的墨线，板上有木纹皴擦、节疤。"""
    col = N['wood'] if col is None else np.asarray(col, F)
    dark = N['wood_dk'] if dark is None else np.asarray(dark, F)
    r = np.random.default_rng(seed)
    if not vertical:
        y = y0
        k = 0
        while y < y1:
            hh = plank_h * U(r, 0.85, 1.15)
            yb = min(y + hh, y1)
            wash(L, rect(x0, y, x1, yb), mix(col, dark, U(r, 0.0, 0.55)), op=op, wob=0.6, seed=int(r.integers(1e6)), smooth=0, tex_k=0.22, rim=0.15, rim_w=2.5)
            # 板缝
            brush(L, [(x0, yb), ((x0 + x1) / 2, yb + r.normal(0, 0.8)), (x1, yb)], w0=U(r, 2.2, 3.6), color=INK, op=0.7 * op, seed=int(r.integers(1e6)), taper=0.02, wob=0.6, dry=0.15)
            # 木纹
            st = []
            for _ in range(int((x1 - x0) / 12 * grain_k)):
                px = U(r, x0, x1)
                py = y + U(r, 0.1, 0.9) * (yb - y)
                st.append((px, py, px + U(r, 30, 150), py + r.normal(0, 0.7), U(r, 0.8, 1.6), U(r, 0.1, 0.35) * op))
            flicks(L, st, color=INK)
            # 节疤
            if r.random() < 0.35:
                kx = U(r, x0 + 40, x1 - 40)
                ky = y + (yb - y) * U(r, 0.35, 0.65)
                wash(L, [(kx + math.cos(a) * 9 * U(r, 0.8, 1.2), ky + math.sin(a) * 4 * U(r, 0.8, 1.2)) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)], dark * 0.6, op=0.7 * op, wob=0.5, seed=int(r.integers(1e6)), smooth=2, tex_k=0.1, rim=0.3)
                brush(L, [(kx - 22, ky - 4), (kx, ky - 7), (kx + 22, ky - 4)], w0=1.2, color=INK, op=0.35 * op, seed=int(r.integers(1e6)), taper=0.4, wob=0.3)
            y = yb
            k += 1
    else:
        x = x0
        while x < x1:
            ww = plank_h * U(r, 0.85, 1.15)
            xb = min(x + ww, x1)
            wash(L, rect(x, y0, xb, y1), mix(col, dark, U(r, 0.0, 0.55)), op=op, wob=0.6, seed=int(r.integers(1e6)), smooth=0, tex_k=0.22, rim=0.15, rim_w=2.5)
            brush(L, [(xb, y0), (xb + r.normal(0, 0.8), (y0 + y1) / 2), (xb, y1)], w0=U(r, 2.2, 3.6), color=INK, op=0.7 * op, seed=int(r.integers(1e6)), taper=0.02, wob=0.6, dry=0.15)
            st = []
            for _ in range(int((y1 - y0) / 12 * grain_k)):
                py = U(r, y0, y1)
                px = x + U(r, 0.1, 0.9) * (xb - x)
                st.append((px, py, px + r.normal(0, 0.7), py + U(r, 30, 150), U(r, 0.8, 1.6), U(r, 0.1, 0.35) * op))
            flicks(L, st, color=INK)
            x = xb


def beam(L, x0, y0, x1, y1, seed=0, col=None, op=1.0, w_end=None, round_=True):
    """一根粗木梁/柱（水平或竖直）：两道轮廓墨线 + 受光的亮边 + 裂纹 + 皴擦。(x0,y0)-(x1,y1) 是外接矩形。"""
    col = N['wood_dk'] if col is None else np.asarray(col, F)
    r = np.random.default_rng(seed)
    wash(L, rect(x0, y0, x1, y1), col, op=op, wob=1.0, seed=seed, smooth=0, tex_k=0.28, rim=0.2, rim_w=3)
    horiz = (x1 - x0) > (y1 - y0)
    if horiz:
        hh = y1 - y0
        wash(L, rect(x0, y0 + hh * 0.05, x1, y0 + hh * 0.3), mix(col, N['stone_lt'], 0.3), op=0.4 * op, wob=1.0, seed=seed + 1, smooth=0, tex_k=0.2, rim=0.0)
        wash(L, rect(x0, y1 - hh * 0.32, x1, y1), INK * 0.8, op=0.45 * op, wob=1.0, seed=seed + 2, smooth=0, tex_k=0.2, rim=0.0)
        for yy in (y0, y1):
            brush(L, [(x0, yy), ((x0 + x1) / 2, yy + r.normal(0, 0.8)), (x1, yy)], w0=3.0, color=INK, op=0.8 * op, seed=int(r.integers(1e6)), taper=0.03, wob=0.7, dry=0.25)
        st = []
        for _ in range(int((x1 - x0) / 9)):
            px = U(r, x0, x1)
            st.append((px, U(r, y0 + 3, y1 - 3), px + U(r, 40, 200), 0, U(r, 0.9, 2.0), U(r, 0.15, 0.45) * op))
        st = [(a, b, c_, b + r.normal(0, 0.8), w, o) for (a, b, c_, d, w, o) in st]
        flicks(L, st, color=INK)
        for _ in range(int(2 + (x1 - x0) / 400)):
            cx = U(r, x0 + 20, x1 - 120)
            cy = U(r, y0 + hh * 0.3, y1 - hh * 0.3)
            brush(L, [(cx, cy), (cx + 40, cy + r.normal(0, 2)), (cx + U(r, 70, 160), cy + r.normal(0, 3))], w0=U(r, 2.0, 3.5), w1=0.8, color=INK, op=0.55 * op, seed=int(r.integers(1e6)), taper=0.3, wob=0.8, dry=0.3)
    else:
        ww = x1 - x0
        wash(L, rect(x0 + ww * 0.05, y0, x0 + ww * 0.3, y1), mix(col, N['stone_lt'], 0.3), op=0.4 * op, wob=1.0, seed=seed + 1, smooth=0, tex_k=0.2, rim=0.0)
        wash(L, rect(x1 - ww * 0.32, y0, x1, y1), INK * 0.8, op=0.45 * op, wob=1.0, seed=seed + 2, smooth=0, tex_k=0.2, rim=0.0)
        for xx in (x0, x1):
            brush(L, [(xx, y0), (xx + r.normal(0, 0.8), (y0 + y1) / 2), (xx, y1)], w0=3.0, color=INK, op=0.8 * op, seed=int(r.integers(1e6)), taper=0.03, wob=0.7, dry=0.25)
        st = []
        for _ in range(int((y1 - y0) / 9)):
            py = U(r, y0, y1)
            px = U(r, x0 + 3, x1 - 3)
            st.append((px, py, px + r.normal(0, 0.8), py + U(r, 40, 200), U(r, 0.9, 2.0), U(r, 0.15, 0.45) * op))
        flicks(L, st, color=INK)


def window_paper(L, x, y, w, h, seed=0, frame_col=None, paper=None, grid=(3, 4), op=1.0, glow=None):
    """纸糊的格窗：木框 + 窗棂（横竖细木条）+ 纸面（冷白）+ 纸上的几处破口/水渍。(x,y) 窗中心。
    返回窗纸区域的 mask 外框 (x0,y0,x1,y1) 以便 save_plate2 的 glow 层复用。"""
    frame_col = N['wood_dk'] if frame_col is None else np.asarray(frame_col, F)
    paper = COOL if paper is None else np.asarray(paper, F)
    r = np.random.default_rng(seed)
    x0, y0, x1, y1 = x - w / 2, y - h / 2, x + w / 2, y + h / 2
    wash(L, rect(x0 - 12, y0 - 12, x1 + 12, y1 + 12), frame_col * 0.85, op=op, wob=1.0, seed=seed, smooth=0, tex_k=0.25, rim=0.2, rim_w=3)
    wash(L, rect(x0, y0, x1, y1), paper, op=op, wob=0.7, seed=seed + 1, smooth=0, tex_k=0.1, rim=0.1, rim_w=2)
    # 窗纸上淡淡的暗斑（纸旧了）
    for _ in range(4):
        px, py = U(r, x0 + 12, x1 - 12), U(r, y0 + 12, y1 - 12)
        wash(L, [(px + math.cos(a) * U(r, 8, 20), py + math.sin(a) * U(r, 8, 24)) for a in np.linspace(0, 2 * math.pi, 7, endpoint=False)], paper * 0.86, op=0.35 * op, wob=2, seed=int(r.integers(1e6)), smooth=2, tex_k=0.15, rim=0.0)
    cols, rows = grid
    for i in range(1, cols):
        xx = x0 + (x1 - x0) * i / cols
        brush(L, [(xx, y0), (xx + r.normal(0, 0.6), y1)], w0=4.0, color=frame_col * 0.8, op=0.95 * op, seed=int(r.integers(1e6)), smooth=False, taper=0.02, wob=0.4)
    for j in range(1, rows):
        yy = y0 + (y1 - y0) * j / rows
        brush(L, [(x0, yy), (x1, yy + r.normal(0, 0.6))], w0=4.0, color=frame_col * 0.8, op=0.95 * op, seed=int(r.integers(1e6)), smooth=False, taper=0.02, wob=0.4)
    brush(L, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], w0=3.0, color=INK, op=0.85 * op, seed=seed + 5, smooth=False, taper=0.01, wob=0.4)
    brush(L, [(x0 - 12, y0 - 12), (x1 + 12, y0 - 12), (x1 + 12, y1 + 12), (x0 - 12, y1 + 12), (x0 - 12, y0 - 12)], w0=3.4, color=INK, op=0.85 * op, seed=seed + 6, smooth=False, taper=0.01, wob=0.6, dry=0.2)
    return (x0, y0, x1, y1)


# ───────────────────────── 收尾 ─────────────────────────
def save_plate2(name, L, glow=None, variants=('night', 'lit'), gain=0.7, keep=0.2, glow_lit=0.9, wc=True, **kw):
    """先做水彩化，再生成夜色 / 光照版；glow 是一张“冷白光”画布（直接是最终色，如窗/灯 #EFE8D8），叠在夜色版上（不被压暗）；
    在光照版里也叠上（略淡）。其余同 ccommon.save_plate。"""
    if wc:
        import zlib
        watercolorize(L, seed=zlib.crc32(name.encode()) % 1000)
    ov = {}
    if glow is not None:
        for v in variants:
            if v == 'night':
                C = Canvas(L.w, L.h)
                C.rgb = grade.night(L.rgb, keep=keep, gain=gain).astype(F)
                C.a = L.a.copy()
                k = 1.0
            elif v == 'lit':
                C = Canvas(L.w, L.h)
                C.rgb = grade.lit(L.rgb).astype(F)
                C.a = L.a.copy()
                k = glow_lit
            else:
                continue
            a = glow.a * k
            C.rgb = (glow.rgb * a[..., None] + C.rgb * (1 - a[..., None])).astype(F)
            C.a = np.maximum(C.a, a).astype(F) if L.a.min() < 0.999 else C.a
            ov[v] = C
    save_plate(name, L, variants=variants, gain=gain, keep=keep, overrides=ov or None, wc=False, **kw)
    ensure_manifest(name, variants, L)


# ───────────────────────── 平大石 / 路 ─────────────────────────
def slab(L, cx, by, w, h, top_h=None, seed=0, col=None, dark=None, light=None, op=1.0, snow=0.0):
    """一块平顶的大石（可以坐人）：顶面是一块亮面（略带透视，边缘参差），前脸往下收窄、一层层的岩理、崩口和苔痕；cx,by 是底边中点，h 是总高。"""
    col = N['stone'] if col is None else np.asarray(col, F)
    dark = N['stone_dk'] if dark is None else np.asarray(dark, F)
    light = mix(N['stone_lt'], N['paper'], 0.35) if light is None else np.asarray(light, F)
    r = np.random.default_rng(seed)
    top_h = h * 0.26 if top_h is None else top_h
    x0, x1 = cx - w / 2, cx + w / 2
    yt = by - h

    def J(pts, a):
        return [(px + r.normal(0, a), py + r.normal(0, a * 0.7)) for (px, py) in pts]

    # 顶面（后沿 → 前沿）
    back = [(x0 + w * 0.05, yt + top_h * 0.3), (x0 + w * 0.16, yt + top_h * 0.06), (x0 + w * 0.36, yt - top_h * 0.03), (x0 + w * 0.6, yt + top_h * 0.0), (x0 + w * 0.84, yt + top_h * 0.1), (x1 - w * 0.01, yt + top_h * 0.34)]
    front_top = [(x1 + 3, yt + top_h * 0.8), (x1 - w * 0.2, yt + top_h * 1.0), (x0 + w * 0.55, yt + top_h * 1.04), (x0 + w * 0.22, yt + top_h * 1.0), (x0 - 3, yt + top_h * 0.82)]
    top = J(back + front_top, 1.6)
    # 前脸
    face = J(front_top[::-1][::-1], 0.0) + J([(x1 - 2, yt + top_h * 1.7), (x1 - w * 0.03, by - h * 0.25), (x1 - w * 0.06, by - 3), (x1 - w * 0.2, by + 1), (x0 + w * 0.5, by - 4), (x0 + w * 0.12, by + 2), (x0 + w * 0.05, by - h * 0.22), (x0 + 1, yt + top_h * 1.7)], 2.2)
    wash(L, face, col, op=op, wob=1.6, seed=seed, smooth=1, tex_k=0.28, rim=0.25, rim_w=3)
    # 前脸右半、下半压暗
    wash(L, [(x0 + w * 0.55, yt + top_h * 1.04), (x1 - w * 0.2, yt + top_h * 1.0), (x1 + 3, yt + top_h * 0.8), (x1 - 2, yt + top_h * 1.7), (x1 - w * 0.03, by - h * 0.25), (x1 - w * 0.06, by - 3), (x0 + w * 0.5, by - 4)], dark, op=0.5 * op, wob=2.0, seed=seed + 1, smooth=2, tex_k=0.2, rim=0.1)
    wash(L, [(x0 + 2, by - h * 0.22), (x1 - w * 0.06, by - h * 0.22), (x1 - w * 0.06, by - 3), (x0 + w * 0.12, by + 2)], dark, op=0.35 * op, wob=2.0, seed=seed + 11, smooth=2, tex_k=0.2, rim=0.0)
    wash(L, top, mix(col, light, 0.85), op=op, wob=1.2, seed=seed + 2, smooth=1, tex_k=0.2, rim=0.2, rim_w=2.5)
    # 顶面上一层积灰 / 水渍
    wash(L, [(x0 + w * 0.2, yt + top_h * 0.6), (x0 + w * 0.45, yt + top_h * 0.22), (x1 - w * 0.2, yt + top_h * 0.35), (x0 + w * 0.6, yt + top_h * 0.8)], N['paper'], op=0.35 * op, wob=2, seed=seed + 3, smooth=2, tex_k=0.1, rim=0.0)
    # 岩理
    for k in range(3):
        yy = yt + top_h * 1.5 + k * (by - yt - top_h * 1.5) / 3.0 + U(r, -4, 4)
        brush(L, [(x0 + w * U(r, 0.04, 0.2), yy), (cx + U(r, -w * 0.2, w * 0.2), yy + U(r, -3, 4)), (x1 - w * U(r, 0.04, 0.2), yy + U(r, -3, 3))], w0=U(r, 1.6, 3.0), color=INK, op=0.5 * op, seed=int(r.integers(1e6)), taper=0.3, wob=1.0, dry=0.4)
    for k in range(4):
        px = x0 + w * U(r, 0.1, 0.9)
        py0 = yt + top_h * 1.1
        brush(L, [(px, py0), (px + r.normal(0, 3), py0 + (by - py0) * 0.55), (px + r.normal(0, 5), py0 + (by - py0) * U(r, 0.8, 1.0))], w0=U(r, 1.6, 3.4), w1=0.8, color=INK, op=0.5 * op, seed=int(r.integers(1e6)), taper=0.3, wob=1.2, dry=0.3)
    st = []
    for _ in range(int(w * h / 380)):
        px = U(r, x0 + 6, x1 - 6)
        py = U(r, yt + top_h * 1.1, by - 3)
        st.append((px, py, px + U(r, 8, 26), py + U(r, -3, 5), U(r, 0.9, 1.9), U(r, 0.15, 0.5) * op))
    flicks(L, st, color=INK)
    # 苔痕：下沿几笔灰绿的点
    mp = [(U(r, x0 + 10, x1 - 10), by - U(r, 0, h * 0.25)) for _ in range(int(w / 14))]
    frost(L, mp, op=0.5 * op, size=(1.6, 3), col=N['grass_dk'], seed=seed + 12, ln=(4, 12))
    # 轮廓：顶面外沿（粗）、顶面前沿、前脸两侧和底边
    brush(L, back + [front_top[0]], w0=3.0, color=INK, op=0.75 * op, seed=seed + 5, wob=1.0, taper=0.1, dry=0.3)
    brush(L, front_top[::-1], w0=2.8, color=INK, op=0.7 * op, seed=seed + 6, wob=1.0, taper=0.1, dry=0.3)
    brush(L, [front_top[-1], (x0 + 1, yt + top_h * 1.7), (x0 + w * 0.05, by - h * 0.22), (x0 + w * 0.12, by + 2)], w0=2.8, color=INK, op=0.7 * op, seed=seed + 7, wob=1.0, taper=0.1, dry=0.3)
    brush(L, [front_top[0], (x1 - 2, yt + top_h * 1.7), (x1 - w * 0.03, by - h * 0.25), (x1 - w * 0.06, by - 3)], w0=2.8, color=INK, op=0.7 * op, seed=seed + 8, wob=1.0, taper=0.1, dry=0.3)
    brush(L, [(x0 + w * 0.12, by + 2), (cx, by - 3), (x1 - w * 0.2, by + 1)], w0=3.0, color=INK, op=0.5 * op, seed=seed + 9, wob=0.8, taper=0.15, dry=0.4)
    if snow > 0:
        wash(L, top, N['snow'], op=snow * op, wob=2, seed=seed + 8, smooth=2, tex_k=0.08, rim=0.1)


def path_ribbon(L, y_top, y_bot, seed=0, x0=0, x1=None, top_col=None, bot_col=None, ruts=True, pebbles=True, edge_op=0.55):
    """土路：一条上下沿不规则的浅色带（y_top/y_bot 是每列的上下沿），上沿暗（路肩的阴影）、中间亮；两道车辙、碎石、路沿的墨线。"""
    x1 = L.w if x1 is None else x1
    W = x1 - x0
    top_col = N['earth_lt'] if top_col is None else np.asarray(top_col, F)
    bot_col = N['earth'] if bot_col is None else np.asarray(bot_col, F)
    yt = np.asarray(y_top, F)[x0:x1]
    yb = np.asarray(y_bot, F)[x0:x1]
    ymin, ymax = int(yt.min() - 4), int(yb.max() + 4)
    h = ymax - ymin
    yy = np.arange(ymin, ymax, dtype=F)[:, None]
    t = np.clip((yy - yt[None, :]) / np.maximum(yb - yt, 1)[None, :], 0, 1)
    base = mix(top_col, bot_col, (t ** 0.9)[..., None])
    n = fbm(h, W, seed + 2, 100, 5, 0.55, warp=40)
    base = base * (0.9 + 0.2 * n[..., None]) + grain(h, W, seed + 4, 0.9)[..., None] * 0.014
    # 上沿的暗（路肩）
    base = base * (1 - 0.25 * np.exp(-((yy - yt[None, :]) / 10.0) ** 2))[..., None] if True else base
    a = np.clip((yy - yt[None, :]) / 3.0, 0, 1) * np.clip((yb[None, :] - yy) / 4.0, 0, 1)
    L.over(ymin, ymax, x0, x1, np.clip(base, 0, 1).astype(F), a.astype(F))
    r = np.random.default_rng(seed + 9)
    if ruts:
        for k, f in enumerate((0.38, 0.72)):
            ys = yt + (yb - yt) * f
            seg = 0
            while seg < W - 60:
                ln = int(U(r, 150, 420))
                pts = np.stack([np.arange(seg, min(seg + ln, W)) + x0, ys[seg:seg + ln] + 3 * np.sin(np.arange(seg, min(seg + ln, W)) / 55.0 + k)], 1)[::16]
                if len(pts) >= 3:
                    brush(L, pts, w0=U(r, 2.0, 4.0), color=N['earth_dk'], op=0.4 * U(r, 0.6, 1.0), seed=int(r.integers(1e6)), wob=0.9, taper=0.3, dry=0.4)
                seg += ln + int(U(r, 10, 90))
    for edge_y, flip in ((yt, 1), (yb, -1)):
        seg = 0
        while seg < W - 60:
            ln = int(U(r, 100, 360))
            pts = np.stack([np.arange(seg, min(seg + ln, W)) + x0, edge_y[seg:seg + ln]], 1)[::14]
            if len(pts) >= 3:
                brush(L, pts, w0=U(r, 1.6, 3.2), color=INK, op=edge_op * U(r, 0.4, 0.9), seed=int(r.integers(1e6)), wob=0.9, taper=0.3, dry=0.4)
            seg += ln + int(U(r, -10, 80))
    if pebbles:
        for _ in range(int(W / 14)):
            x = U(r, 0, W)
            i = int(min(x, W - 1))
            y = yt[i] + (yb[i] - yt[i]) * U(r, 0.1, 0.9)
            s = U(r, 3, 9)
            wash(L, [(x - s, y), (x - s * 0.3, y - s * 0.55), (x + s * 0.8, y - s * 0.35), (x + s, y + s * 0.15), (x - s * 0.4, y + s * 0.4)], mix(N['stone'], N['earth'], U(r, 0, 0.6)), op=U(r, 0.5, 0.9), wob=0.3, seed=int(r.integers(1e6)), smooth=1, tex_k=0.12, rim=0.25, rim_w=1.5)
            if r.random() < 0.7:
                brush(L, [(x - s * 0.9, y + s * 0.4), (x + s * 0.2, y + s * 0.5), (x + s * 1.1, y + s * 0.2)], w0=1.3, color=INK, op=0.5, seed=int(r.integers(1e6)), taper=0.4, wob=0.3)


# ───────────────────────── 山（更柔的水墨山：没有硬边的罩染） ─────────────────────────
def _vstretch_noise(h, W, seed, sx=44, sy=420, octaves=4, k=6):
    """竖向拉长的噪声（山沟、岩壁的竖纹）：先在 1/k 的高度上生成再竖向拉伸。"""
    hh = max(h // k, 4)
    n = fbm(hh, W, seed, sx, octaves, 0.55, warp=sx * 0.6)
    return cv2.resize(n, (W, h), interpolation=cv2.INTER_CUBIC)


def mountain2(L, ridge, bottom, top_col, bot_col, seed=0, tex=0.6, tex_col=INK, tex_op=0.3, snow=None, snow_from=0.3, haze=0.0, haze_col=None,
              lit_dir=1, shade=0.45, ink_op=0.5, rim_w=2.4, gully=0.6, shade_col=None, snow_col=None):
    """一列山：渐变底色 + 竖向的山沟/岩壁明暗（噪声，不是多边形，没有硬边）+ 沿坡的皴笔 + 断续的山脊墨线 + 雪盖（可选）。"""
    W, H = L.w, L.h
    ridge = np.asarray(ridge, F)
    bottom = np.broadcast_to(np.asarray(bottom, F), (W,)).copy()
    top_col, bot_col = np.asarray(top_col, F), np.asarray(bot_col, F)
    shade_col = mix(top_col, INK, 0.5) if shade_col is None else np.asarray(shade_col, F)
    ymin = int(max(ridge.min() - 4, 0)); ymax = int(min(bottom.max() + 2, H))
    h = ymax - ymin
    yy = np.arange(ymin, ymax, dtype=F)[:, None]
    depth = np.clip((yy - ridge[None, :]) / np.maximum(bottom - ridge, 1)[None, :], 0, 1)
    base = mix(top_col, bot_col, (depth ** 0.85)[..., None])
    n = fbm(h, W, seed + 1, 160, 5, 0.55, warp=40)
    base = base * (0.92 + 0.16 * n[..., None]) + grain(h, W, seed + 8, 0.9)[..., None] * 0.012
    # 山脊的坡度：光从左来 → 右下坡（背光）暗
    slope = np.gradient(cv2.GaussianBlur(ridge.reshape(1, -1), (0, 0), 6)[0])
    sl = np.clip(slope * lit_dir / 2.2, -1, 1)            # y 向下为正：lit_dir=1 时，往右下降的坡 slope>0 → 背光
    sl = cv2.GaussianBlur(sl.reshape(1, -1).astype(F), (0, 0), 18)[0]
    gul = _vstretch_noise(h, W, seed + 3, 36, 380)
    gul2 = _vstretch_noise(h, W, seed + 4, 90, 500)
    ridged = 1 - np.abs(2 * gul - 1)                       # 山沟：窄的暗带
    shade_amt = np.clip(0.45 + 0.9 * sl[None, :], 0, 1) * (0.55 + 0.9 * (gul2 - 0.5)) + gully * 0.55 * np.clip(ridged - 0.55, 0, 1) * 2.0
    shade_amt = np.clip(shade_amt, 0, 1) * (1 - depth ** 1.6 * 0.6) * shade
    base = mix(base, shade_col, shade_amt[..., None])
    if haze > 0:
        hc = np.asarray(N['mist'] if haze_col is None else haze_col, F)
        base = mix(base, hc, (haze * (1 - depth ** 0.5))[..., None])
    a = np.clip((yy - ridge[None, :]) / 2.5, 0, 1) * np.clip((bottom[None, :] - yy) / 24.0, 0, 1)
    L.over(ymin, ymax, 0, W, np.clip(base, 0, 1).astype(F), a.astype(F))
    rng = np.random.default_rng(seed + 7)
    # 皴笔：沿山沟方向的长笔（披麻皴 / 斧劈皴），暗面更密
    if tex > 0:
        count = int(W * (ymax - ymin) / 4200 * tex)
        xs = np.clip(rng.uniform(0, W, count).astype(int), 0, W - 1)
        d = rng.random(count) ** 1.5 * 0.9
        ys = ridge[xs] + d * (bottom[xs] - ridge[xs])
        sh_at = np.clip(0.45 + 0.9 * sl[xs], 0, 1)
        keep = rng.random(count) < (0.35 + 0.65 * sh_at)
        xs, ys, d = xs[keep], ys[keep], d[keep]
        c = len(xs)
        ang = np.radians(rng.normal(80, 9, c)) * np.where(rng.random(c) < 0.5, 1, -1)
        ln = rng.uniform(12, 60, c) * (1 + (1 - d) * 0.4)
        wd = rng.uniform(0.9, 2.4, c)
        op = rng.uniform(0.3, 1.0, c) * tex_op * (1.0 - d * 0.5)
        st = np.stack([xs, ys, xs + np.cos(ang) * ln, ys + np.abs(np.sin(ang)) * ln, wd, op], 1)
        flicks(L, st, color=tex_col)
    # 山脊墨线
    seg = 0
    xs_all = np.arange(W)
    while seg < W - 30:
        ln = int(rng.uniform(140, 440))
        sl_ = slice(seg, min(seg + ln, W))
        pts = np.stack([xs_all[sl_], ridge[sl_]], 1)[::14]
        if len(pts) >= 3:
            brush(L, pts, w0=rim_w * rng.uniform(0.8, 1.5), color=tex_col, op=ink_op * rng.uniform(0.55, 1.0), seed=int(rng.integers(1e6)), wob=0.8, taper=0.25, dry=0.3)
        seg += ln + int(rng.uniform(-20, 60))
    if snow is not None:
        sc_ = np.asarray(snow, F)
        rel = (np.arange(ymin, ymax, dtype=F)[:, None] - ridge[None, :]) / np.maximum(bottom - ridge, 1)[None, :]
        nn = fbm(h, W, seed + 33, 80, 5, 0.6, warp=30)
        edge = snow_from * (0.45 + 0.9 * nn) * (1 + 0.5 * (gul - 0.5))
        sm = (1 - smoothstep(edge - 0.05, edge + 0.01, rel)) * (rel >= 0)
        # 雪盖的背光面蓝灰
        sc2 = mix(sc_, N['snow_sh'], np.clip(0.2 + 0.6 * sh_at_cols(sl, W)[None, :], 0, 0.7)[..., None] * 0.6)
        L.over(ymin, ymax, 0, W, np.clip(sc2 * (0.95 + 0.07 * nn[..., None]), 0, 1).astype(F), np.clip(sm * a, 0, 1).astype(F) * 0.95)


def sh_at_cols(sl, W):
    return np.clip(0.45 + 0.9 * sl, 0, 1)


def grove(rng, n, x0, x1, clusters=None, spread=130):
    """林子的 x 位置：成丛（几个中心 + 高斯散开），不是等距。返回排序后的 x 列表。"""
    k = clusters or max(n // 5, 2)
    cs = rng.uniform(x0, x1, k)
    xs = []
    for _ in range(n):
        c = cs[int(rng.integers(0, k))]
        xs.append(float(np.clip(c + rng.normal(0, spread), x0, x1)))
    return sorted(xs)


def pine_mass(L, x, y, h, seed=0, col=None, dark=None, frost_k=0.0, lean=0.0, op=1.0, tiers=None, width=1.0, trunk_col=None):
    """中景/远景的松：细干 + 几层参差的“云片”树冠（每片：圆顶、下沿略垂的不规则色块，边缘一排短促的点苔，顶上一笔淡亮）。
    比 pine_ink 更紧凑，成林时像一团团水墨的树影。"""
    col = N['pine'] if col is None else np.asarray(col, F)
    dark = N['pine_dk'] if dark is None else np.asarray(dark, F)
    tc = N['wood_dk'] * 0.55 if trunk_col is None else np.asarray(trunk_col, F)
    r = np.random.default_rng(seed)
    side0 = 1 if r.random() < 0.5 else -1
    pts = trunk_curve((x, y), (x + lean * h, y - h * 0.97), h * 0.03 * side0, 18, seed=seed)
    brush(L, pts, w0=max(h * 0.04, 2.0), w1=max(h * 0.012, 0.9), color=tc, op=0.9 * op, seed=seed, wob=h * 0.005, taper=0.05)
    nt = tiers or (3 + int(h / 120))
    nt = min(nt, 7)
    sc = min(1.0, h / 160 + 0.3)
    for k in range(nt):
        f = 0.34 + 0.62 * k / max(nt - 1, 1) + U(r, -0.025, 0.025)
        i = int(min(f, 0.97) * (len(pts) - 1))
        cx, cy = pts[i]
        cx += U(r, -0.2, 0.2) * h * 0.05
        w = h * (0.24 * (1 - f) ** 0.6 + 0.07) * U(r, 0.85, 1.25) * width
        t = h * U(r, 0.05, 0.085) * (1.1 - 0.4 * f)
        top = []
        n = 9
        for j in range(n):
            u = -1 + 2 * j / (n - 1)
            top.append((cx + u * w, cy - t * (1 - abs(u) ** 2.2) * U(r, 0.8, 1.15) + abs(u) ** 3 * t * 0.5))
        bot = []
        for j in range(n):
            u = 1 - 2 * j / (n - 1)
            bot.append((cx + u * w * U(r, 0.88, 1.0), cy + t * 0.35 * (1 - abs(u) ** 1.5) + abs(u) ** 2 * t * 0.45 + U(r, -1, 1.5)))
        poly = top + bot
        wash(L, poly, mix(col, dark, U(r, 0.05, 0.55)), op=0.88 * op, wob=1.4 * sc, seed=int(r.integers(1e6)), smooth=2, tex_k=0.3, rim=0.24, rim_w=2.2)
        # 顶上淡亮一笔
        wash(L, [(cx - w * 0.6, cy - t * 0.1), (cx - w * 0.2, cy - t * 0.85), (cx + w * 0.4, cy - t * 0.7), (cx + w * 0.1, cy - t * 0.2)], mix(col, N['paper'], 0.3), op=0.3 * op, wob=1, seed=int(r.integers(1e6)), smooth=2, tex_k=0.1, rim=0.0)
        # 下沿的点苔：一排短促下垂的笔
        st = []
        for j in range(int(w / 3.5) + 3):
            u = U(r, -0.95, 0.95)
            px, py = cx + u * w, cy + t * 0.35 * (1 - abs(u) ** 1.5) + abs(u) ** 2 * t * 0.45
            st.append((px, py - 1, px + r.normal(0, 1.5), py + U(r, 2, 6.5) * sc, U(r, 1.3, 2.6) * sc, U(r, 0.4, 0.85) * op))
        flicks(L, st, color=dark)
        if frost_k > 0:
            frost(L, [(cx + U(r, -0.9, 0.9) * w, cy - t * U(r, 0.2, 0.95) * (1 - abs(0) ** 2)) for _ in range(int(w / 5 * frost_k) + 2)], op=0.9 * op * min(frost_k, 1), size=(1.5 * sc + 0.4, 3.2 * sc + 0.6), seed=int(r.integers(1e6)), ln=(3, 8))


def conifer_dab(L, x, y, h, seed=0, col=None, dark=None, op=1.0, w=None, frost_k=0.0, lean=0.0):
    """远/中景的一株针叶树：一团瘦长、参差的深色“水墨团”（尖顶略弯，两侧一级级的锯齿，左右不对称），底下露一小截细干；
    边缘缀着几笔短促的点苔。比圣诞树松散得多，成片时像林子的暗影。"""
    col = N['pine'] if col is None else np.asarray(col, F)
    dark = N['pine_dk'] if dark is None else np.asarray(dark, F)
    r = np.random.default_rng(seed)
    w = h * U(r, 0.13, 0.23) if w is None else w
    lean = lean + U(r, -0.06, 0.06)
    tx = x + lean * h
    left, right = [], []
    n = int(h / 16) + 4
    for k in range(n):
        f = k / (n - 1)                        # 0 顶 → 1 底
        wl = w * (f ** 0.65) * U(r, 0.35, 1.15) * (1 + 0.35 * math.sin(f * 11 + seed))
        wr = w * (f ** 0.65) * U(r, 0.35, 1.15) * (1 + 0.35 * math.cos(f * 9 + seed))
        yy = y - h * 0.9 + f * h * 0.78
        cx = tx + (x - tx) * f + math.sin(f * 4 + seed) * w * 0.12
        # 每一级：先向外探出，再收回一点（锯齿）
        left += [(cx - wl, yy), (cx - wl * 0.55, yy + h * 0.02)]
        right += [(cx + wr, yy), (cx + wr * 0.55, yy + h * 0.02)]
    tip = (tx + w * 0.1 * U(r, -1, 1), y - h)
    poly = [tip] + right + [(x + w * 0.4, y - h * 0.1), (x - w * 0.4, y - h * 0.1)] + left[::-1]
    wash(L, poly, mix(col, dark, U(r, 0.2, 0.7)), op=0.92 * op, wob=1.0 + h * 0.01, seed=int(r.integers(1e6)), smooth=1, tex_k=0.35, rim=0.22, rim_w=2.2)
    # 小干
    brush(L, [(x, y), (x + r.normal(0, 1), y - h * 0.12)], w0=max(h * 0.03, 1.6), color=dark, op=0.9 * op, seed=int(r.integers(1e6)), taper=0.1, wob=0.4)
    st = []
    for _ in range(int(h / 5)):
        k = int(r.integers(0, len(left)))
        pxy = left[k] if r.random() < 0.5 else right[k % len(right)]
        st.append((pxy[0], pxy[1], pxy[0] + r.normal(0, 2), pxy[1] + U(r, 3, 9), U(r, 1.4, 2.8), U(r, 0.35, 0.8) * op))
    flicks(L, st, color=dark * 0.8)
    if frost_k > 0:
        pts = []
        for _ in range(int(h / 9 * frost_k)):
            k = int(r.integers(0, len(left)))
            pxy = left[k] if r.random() < 0.5 else right[k % len(right)]
            pts.append((pxy[0] + U(r, -4, 4), pxy[1] - 1))
        frost(L, pts, op=0.9 * min(frost_k, 1), size=(1.6, 3.0), seed=seed + 5, ln=(3, 7))


# ───────────────────────── 木屋 / 雪屋 ─────────────────────────
def log_wall(L, x0, y0, x1, y1, seed=0, col=None, dark=None, log_h=40, op=1.0, ends=True):
    """圆木垒的墙：一道道横木（颜色深浅不一，上缘一笔亮、下缘一道深缝，木纹皴擦），两端的圆木头从墙角伸出来（年轮圈）。"""
    col = N['wood'] if col is None else np.asarray(col, F)
    dark = N['wood_dk'] if dark is None else np.asarray(dark, F)
    r = np.random.default_rng(seed)
    y = y1
    k = 0
    while y > y0 + 6:
        hh = log_h * U(r, 0.88, 1.12)
        yt = max(y - hh, y0)
        c = mix(col, dark, U(r, 0.0, 0.6))
        wash(L, rect(x0, yt, x1, y), c, op=op, wob=0.8, seed=int(r.integers(1e6)), smooth=0, tex_k=0.25, rim=0.2, rim_w=2.5)
        wash(L, rect(x0, yt + 2, x1, yt + hh * 0.3), mix(c, N['stone_lt'], 0.28), op=0.45 * op, wob=0.8, seed=int(r.integers(1e6)), smooth=0, tex_k=0.1, rim=0.0)
        brush(L, [(x0, yt), ((x0 + x1) / 2, yt + r.normal(0, 1)), (x1, yt)], w0=U(r, 2.4, 3.8), color=INK, op=0.75 * op, seed=int(r.integers(1e6)), taper=0.02, wob=0.8, dry=0.15)
        st = []
        for _ in range(int((x1 - x0) / 14)):
            px = U(r, x0, x1)
            py = U(r, yt + 4, y - 4)
            st.append((px, py, px + U(r, 20, 120), py + r.normal(0, 0.8), U(r, 0.8, 1.8), U(r, 0.12, 0.4) * op))
        flicks(L, st, color=INK)
        if ends:
            for xe, sgn in ((x0, -1), (x1, 1)):
                ex_ = xe + sgn * U(r, 6, 14) * (1 if k % 2 == 0 else 0.4)
                rr = hh * 0.5
                cy_ = (yt + y) / 2
                wash(L, [(ex_ + math.cos(a) * rr * 0.55, cy_ + math.sin(a) * rr * 0.92) for a in np.linspace(0, 2 * math.pi, 9, endpoint=False)], mix(c, N['earth_lt'], 0.3), op=op, wob=0.5, seed=int(r.integers(1e6)), smooth=2, tex_k=0.1, rim=0.3, rim_w=1.5)
                brush(L, [(ex_ + math.cos(a) * rr * 0.28, cy_ + math.sin(a) * rr * 0.5) for a in np.linspace(0, 2 * math.pi * 1.0, 10)], w0=1.2, color=INK, op=0.45 * op, seed=int(r.integers(1e6)), taper=0.1, wob=0.3)
        y = yt
        k += 1
    for xx in (x0, x1):
        brush(L, [(xx, y1), (xx + r.normal(0, 1), (y0 + y1) / 2), (xx, y0)], w0=3.0, color=INK, op=0.6 * op, seed=int(r.integers(1e6)), taper=0.03, wob=0.8, dry=0.3)


def snow_roof(L, cx, y_eave, half_w, rise, seed=0, thatch=None, thatch_dk=None, snow=1.0, thick=34):
    """盖着厚雪的草顶：宽檐，两侧微凹；草束的竖笔从檐下露出；屋顶上一层厚雪（下沿起伏的圆弧、檐口堆出圆滚滚的雪檐、屋脊压得平平的），背阴处蓝灰；檐口挂几根冰凌。
    返回 (屋顶多边形 roof, 屋脊 y)"""
    thatch = N['thatch'] if thatch is None else np.asarray(thatch, F)
    thatch_dk = N['thatch_dk'] if thatch_dk is None else np.asarray(thatch_dk, F)
    r = np.random.default_rng(seed)
    ex = half_w
    top = y_eave
    rh = rise
    roof = [(cx - ex, top + 22), (cx - ex * 0.8, top - rh * 0.26), (cx - ex * 0.5, top - rh * 0.78), (cx - ex * 0.3, top - rh), (cx + ex * 0.3, top - rh), (cx + ex * 0.5, top - rh * 0.78), (cx + ex * 0.8, top - rh * 0.26), (cx + ex, top + 22)]
    wash(L, roof, thatch, op=1.0, wob=2.0, seed=seed + 1, smooth=2, tex_k=0.28, rim=0.25, rim_w=3)
    wash(L, [(cx - ex, top + 22), (cx - ex * 0.82, top - rh * 0.1), (cx + ex * 0.82, top - rh * 0.1), (cx + ex, top + 22), (cx + ex * 0.6, top + 30), (cx - ex * 0.6, top + 30)], thatch_dk, op=0.6, wob=2.0, seed=seed + 2, smooth=2, tex_k=0.2, rim=0.0)
    st, st2 = [], []
    for _ in range(int(ex * rh / 30)):
        px = cx + U(r, -ex * 0.97, ex * 0.97)
        edge = abs(px - cx) / ex
        top_edge = top - rh * (1 - edge ** 1.7) * 0.97 + 12 * edge
        py = U(r, top_edge, top + 18)
        ln = U(r, 14, 40)
        (st if r.random() < 0.6 else st2).append((px, py, px + r.normal(0, 2.5) + (px - cx) * 0.04, py + ln, U(r, 1.0, 2.3), U(r, 0.25, 0.7)))
    flicks(L, st, color=thatch_dk * 0.8)
    flicks(L, st2, color=mix(thatch, N['paper'], 0.4))
    # 檐口下垂的草梢
    st = []
    for _ in range(int(ex / 4)):
        px = cx + U(r, -ex, ex)
        base = top + 22 + 8 * (1 - abs(px - cx) / ex) * 0
        st.append((px, base - 4, px + r.normal(0, 2), base + U(r, 6, 22), U(r, 1.2, 2.4), U(r, 0.35, 0.8)))
    flicks(L, st, color=thatch_dk * 0.7)
    brush(L, [roof[0], roof[1], roof[2], roof[3]], w0=2.6, color=INK, op=0.7, seed=seed + 4, wob=1.2, dry=0.3, taper=0.15)
    brush(L, [roof[7], roof[6], roof[5], roof[4]], w0=2.6, color=INK, op=0.7, seed=seed + 5, wob=1.2, dry=0.3, taper=0.15)
    brush(L, [(cx - ex, top + 25), (cx, top + 34), (cx + ex, top + 25)], w0=3.6, color=INK, op=0.5, seed=seed + 6, wob=1.2, dry=0.4, taper=0.1)
    if snow > 0:
        # 雪层：盖满整个屋顶，只在檐口露出一圈草梢；下沿低低地起伏
        eave_y = top + 22
        lowpath = []
        n = 16
        for i in range(n + 1):
            t = i / n
            xx = cx - ex * 1.0 + t * ex * 2.0
            edge = abs(xx - cx) / ex
            fr = (26 + 12 * math.sin(i * 1.15 + seed) + 8 * math.sin(i * 2.9)) * (1 - edge ** 2.2) + 6
            lowpath.append((xx, eave_y - fr + U(r, -2, 2)))
        uppath = [(cx + ex * 0.99, top + 6), (cx + ex * 0.8, top - rh * 0.3), (cx + ex * 0.52, top - rh * 0.82), (cx + ex * 0.31, top - rh * 1.05), (cx - ex * 0.31, top - rh * 1.05), (cx - ex * 0.52, top - rh * 0.82), (cx - ex * 0.8, top - rh * 0.3), (cx - ex * 0.99, top + 6)]
        sp = lowpath + uppath
        wash(L, sp, N['snow'], op=snow, wob=2.2, seed=seed + 7, smooth=2, tex_k=0.08, rim=0.12, rim_w=3)
        # 檐口：两端圆滚滚的雪檐
        for sgn in (-1, 1):
            wash(L, [(cx + sgn * ex * 0.84, top - 6), (cx + sgn * ex * 1.0, top - 4), (cx + sgn * ex * 1.05, top + 20), (cx + sgn * ex * 0.97, top + 36), (cx + sgn * ex * 0.82, top + 28), (cx + sgn * ex * 0.74, top + 10)], N['snow'], op=snow, wob=1.6, seed=seed + 8 + sgn, smooth=2, tex_k=0.06, rim=0.2, rim_w=3)
        # 背阴：屋顶下半一条蓝灰、右半更深（光从左上来）
        low2 = [(p[0], p[1] - (p[1] - (top - rh * 0.55)) * 0.45) for p in lowpath[1:-1]]
        wash(L, low2 + lowpath[1:-1][::-1], N['snow_sh'], op=0.65 * snow, wob=2.5, seed=seed + 9, smooth=2, tex_k=0.12, rim=0.0)
        wash(L, [(cx + ex * 0.3, top - rh * 1.0), (cx + ex * 0.5, top - rh * 0.8), (cx + ex * 0.97, top + 4), (cx + ex * 0.6, top + 6), (cx + ex * 0.32, top - rh * 0.5)], N['snow_sh'], op=0.5 * snow, wob=2.5, seed=seed + 19, smooth=2, tex_k=0.12, rim=0.0)
        # 雪檐下的阴影落在草上
        wash(L, [(p[0], p[1] + 1) for p in lowpath[1:-1]] + [(p[0], p[1] + 13) for p in lowpath[1:-1]][::-1], thatch_dk * 0.6, op=0.5, wob=2.0, seed=seed + 10, smooth=2, tex_k=0.1, rim=0.0)
        # 雪面排线 + 上沿断续的线
        hs = []
        for _ in range(int(ex / 6)):
            px = cx + U(r, -ex * 0.8, ex * 0.8)
            edge = abs(px - cx) / ex
            py = top - rh * (1 - edge ** 1.7) * 0.9 + U(r, 4, 46)
            hs.append((px, py, px + U(r, 14, 44), py + U(r, -2, 5), U(r, 0.9, 1.6), U(r, 0.12, 0.34)))
        flicks(L, hs, color=N['stone_dk'])
        for a_ in range(0, len(uppath) - 2, 2):
            brush(L, uppath[a_:a_ + 3], w0=U(r, 1.6, 2.6), color=N['stone_dk'], op=0.45, seed=int(r.integers(1e6)), wob=0.6, taper=0.3, dry=0.35)
        brush(L, lowpath[1:-1], w0=2.0, color=N['stone_dk'], op=0.35, seed=seed + 31, wob=0.8, taper=0.2, dry=0.4)
        # 冰凌
        for _ in range(int(ex / 22)):
            px = cx + U(r, -ex * 0.92, ex * 0.92)
            by_ = top + 22 + 8
            ln = U(r, 10, 30)
            wash(L, [(px - 2.6, by_), (px + 2.6, by_), (px + U(r, -0.6, 0.6), by_ + ln)], hexc('#e4ecf0'), op=0.85, wob=0.2, seed=int(r.integers(1e6)), smooth=0, tex_k=0.05, rim=0.35, rim_w=1.2)
    return roof, top - rh


def snow_hut(L, x, y, w, wall_h, rise, door_x, door_w=140, door_h=350, seed=0, snow_roof_k=1.0, window=True, lit_door=False):
    """雪山小屋（正面）：圆木墙（下面一圈石基）+ 盖雪的草顶 + 一扇厚木门（door_x 是门中心）+ 一扇小窗；x,y 是墙脚中点。雪堆由调用者另画。"""
    r = np.random.default_rng(seed)
    x0, x1 = x - w / 2, x + w / 2
    top = y - wall_h
    # 石基
    wash(L, rect(x0 - 8, y - 70, x1 + 8, y + 4), N['stone'], op=1.0, wob=1.6, seed=seed, smooth=0, tex_k=0.28, rim=0.2, rim_w=3)
    stn = []
    xx = x0 - 8
    while xx < x1 + 8:
        ww = U(r, 40, 90)
        hh = U(r, 28, 44)
        yy = y - 70 + U(r, 0, 4)
        for row in range(2):
            wash(L, [(xx, yy + row * hh), (xx + ww * 0.9, yy + row * hh - 1), (xx + ww, yy + row * hh + hh * 0.5), (xx + ww * 0.9, yy + row * hh + hh), (xx + 3, yy + row * hh + hh * 0.95)], mix(N['stone'], N['stone_dk'], U(r, 0, 0.5)), op=0.8, wob=0.8, seed=int(r.integers(1e6)), smooth=1, tex_k=0.25, rim=0.3, rim_w=2)
            xx_ = xx
        xx += ww + U(r, 2, 6)
    brush(L, [(x0 - 8, y - 70), (x, y - 69), (x1 + 8, y - 70)], w0=3.0, color=INK, op=0.7, seed=seed + 1, wob=0.8, taper=0.05, dry=0.3)
    log_wall(L, x0, top, x1, y - 70, seed=seed + 2, log_h=38)
    # 门：粗木框 + 立板 + 横栓
    dx0, dx1 = door_x - door_w / 2, door_x + door_w / 2
    dtop = y - door_h
    wash(L, rect(dx0 - 14, dtop - 18, dx1 + 14, y + 2), N['wood_dk'] * 0.8, op=1.0, wob=1.0, seed=seed + 3, smooth=0, tex_k=0.25, rim=0.2, rim_w=3)
    wash(L, rect(dx0, dtop, dx1, y), N['wood'] * 0.62 if not lit_door else COOL, op=1.0, wob=1.0, seed=seed + 4, smooth=0, tex_k=0.22, rim=0.2, rim_w=2.5)
    for k in range(1, 5):
        xx = dx0 + door_w * k / 5
        brush(L, [(xx, dtop), (xx + r.normal(0, 0.6), y)], w0=2.4, color=INK, op=0.6, seed=int(r.integers(1e6)), taper=0.03, smooth=False, wob=0.4)
    st = []
    for _ in range(40):
        px = U(r, dx0 + 4, dx1 - 4)
        py = U(r, dtop + 6, y - 4)
        st.append((px, py, px + r.normal(0, 0.6), py + U(r, 20, 80), U(r, 0.8, 1.6), U(r, 0.12, 0.35)))
    flicks(L, st, color=INK)
    for yy in (dtop + door_h * 0.18, y - door_h * 0.2):
        beam(L, dx0 - 4, yy - 9, dx1 + 4, yy + 9, seed=int(r.integers(1e6)), col=N['wood_dk'] * 0.9)
    # 门环 / 拉手
    wash(L, [(door_x - door_w * 0.34 + math.cos(a) * 9, dtop + door_h * 0.5 + math.sin(a) * 9) for a in np.linspace(0, 2 * math.pi, 9, endpoint=False)], N['stone_dk'], op=0.9, wob=0.3, seed=seed + 20, smooth=2, tex_k=0.1)
    brush(L, [(dx0 - 14, dtop - 18), (dx1 + 14, dtop - 18), (dx1 + 14, y + 2)], w0=3.4, color=INK, op=0.8, seed=seed + 5, smooth=False, taper=0.03, wob=0.8, dry=0.2)
    brush(L, [(dx0 - 14, y + 2), (dx0 - 14, dtop - 18)], w0=3.4, color=INK, op=0.8, seed=seed + 6, smooth=False, taper=0.03, wob=0.8, dry=0.2)
    # 窗
    if window:
        wx, wy = x - w * 0.3, top + wall_h * 0.4
        ww, wh = 96, 84
        wash(L, rect(wx - ww / 2 - 8, wy - wh / 2 - 8, wx + ww / 2 + 8, wy + wh / 2 + 8), N['wood_dk'] * 0.8, op=1.0, wob=0.8, seed=seed + 7, smooth=0, tex_k=0.2, rim=0.2)
        wash(L, rect(wx - ww / 2, wy - wh / 2, wx + ww / 2, wy + wh / 2), N['stone_dk'] * 0.8, op=1.0, wob=0.6, seed=seed + 8, smooth=0, tex_k=0.1)
        brush(L, [(wx, wy - wh / 2), (wx, wy + wh / 2)], w0=3.4, color=N['wood_dk'] * 0.8, op=0.95, seed=seed + 9, smooth=False, taper=0.02, wob=0.3)
        brush(L, [(wx - ww / 2, wy), (wx + ww / 2, wy)], w0=3.4, color=N['wood_dk'] * 0.8, op=0.95, seed=seed + 10, smooth=False, taper=0.02, wob=0.3)
        brush(L, [(wx - ww / 2 - 8, wy - wh / 2 - 8), (wx + ww / 2 + 8, wy - wh / 2 - 8), (wx + ww / 2 + 8, wy + wh / 2 + 8), (wx - ww / 2 - 8, wy + wh / 2 + 8), (wx - ww / 2 - 8, wy - wh / 2 - 8)], w0=3.0, color=INK, op=0.8, seed=seed + 11, smooth=False, taper=0.01, wob=0.6)
        # 窗台上的一小条雪
        wash(L, [(wx - ww / 2 - 12, wy + wh / 2 + 8), (wx - ww / 2 - 4, wy + wh / 2 + 1), (wx + ww / 2 + 4, wy + wh / 2 + 1), (wx + ww / 2 + 12, wy + wh / 2 + 8), (wx, wy + wh / 2 + 12)], N['snow'], op=0.95, wob=0.8, seed=seed + 12, smooth=2, tex_k=0.05, rim=0.2)
    return top


# ───────────────────────── 雪屋的堆雪 ─────────────────────────
def bank(L, x0, x1, yb, h, seed=0, peak=0.5, op=1.0, line=0.35):
    return drift(L, x0, x1, yb, h, seed=seed, op=op, peak=peak, line=line)


def ensure_manifest(name, variants, L, ext=None):
    """manifest.json 是几位画师共用的、读-改-写没有加锁：并发保存时别人可能把我刚登记的条目覆盖掉。
    这里在 save_plate 之后再检查一次，缺了就补回（先重新读、合并后原子替换）。"""
    import os, tempfile
    mf_path = BG / 'manifest.json'
    for _ in range(3):
        try:
            mf = json.loads(mf_path.read_text())
        except Exception:
            mf = {}
        if name in mf and list(mf[name].get('variants', [])) == list(variants):
            return
        opaque = float(L.a.min()) > 0.999
        mf[name] = {'variants': list(variants), 'ext': ext or ('jpg' if opaque else 'png'), 'w': L.w, 'h': L.h}
        fd, tmp = tempfile.mkstemp(dir=str(BG), suffix='.json')
        with os.fdopen(fd, 'w') as f:
            f.write(json.dumps(mf, indent=1))
        os.replace(tmp, mf_path)


def lumpy_top(x0, x1, yb, h, seed=0, step=16, lumps=None, hmin=0.45):
    """一条起伏不平的雪垄上沿（从左到右）：几个大的隆起 + 小的抖动；两端落到 yb。"""
    r = np.random.default_rng(seed)
    n = max(int((x1 - x0) / step), 4)
    xs = np.linspace(x0, x1, n + 1)
    t = np.linspace(0, 1, n + 1)
    k = lumps or max(int((x1 - x0) / 220), 1)
    c = r.uniform(0.1, 0.9, k)
    wdt = r.uniform(0.08, 0.2, k) * (1.0 + 2.0 / k)
    amp = r.uniform(hmin, 1.0, k)
    prof = np.zeros_like(t)
    for ci, wi, ai in zip(c, wdt, amp):
        prof = np.maximum(prof, ai * np.exp(-((t - ci) / wi) ** 2))
    env = np.sin(np.clip(t, 0, 1) * math.pi) ** 0.5
    ys = yb - h * prof * env - h * 0.06 * r.random(n + 1) * env
    return [(float(x), float(y)) for x, y in zip(xs, ys)]


def snow_heap(L, top_pts, yb, seed=0, op=1.0, shade=0.6, lean=1, line=0.45, bottom=None, hatch_k=1.6):
    """按给定的上沿折线（从左到右）画一个/一道雪堆：受光的白；轮廓下降的那几段（右下坡，背光）罩蓝灰；顺着坡面的弧形排线；上沿断续的墨线。"""
    r = np.random.default_rng(seed)
    pts = [(float(x), float(y)) for x, y in top_pts]
    bottom = yb + 6 if bottom is None else bottom
    poly = pts + [(pts[-1][0], bottom), (pts[0][0], bottom)]
    wash(L, poly, N['snow'], op=op, wob=1.8, seed=seed, smooth=2, tex_k=0.08, rim=0.12, rim_w=3)
    # 背光面：轮廓往下走（lean=1）的连续几段
    i = 0
    while i < len(pts) - 1:
        desc = (pts[i + 1][1] - pts[i][1]) * lean > 0.4
        if not desc:
            i += 1
            continue
        j = i
        while j < len(pts) - 1 and (pts[j + 1][1] - pts[j][1]) * lean > 0.2:
            j += 1
        seg = pts[i:j + 1]
        if len(seg) >= 2 and abs(seg[-1][1] - seg[0][1]) > 6:
            depth = lambda y: (yb - y) * U(r, 0.45, 0.7)
            inner = [(x - lean * 6 * (k / max(len(seg) - 1, 1)), y + depth(y)) for k, (x, y) in enumerate(seg)]
            wash(L, [(x, y + 3) for (x, y) in seg] + inner[::-1], N['snow_sh'], op=shade * op, wob=2.0, seed=int(r.integers(1e6)), smooth=2, tex_k=0.12, rim=0.0)
        i = j + 1
    # 顺坡的弧线
    for _ in range(int(len(pts) * hatch_k)):
        i = int(r.integers(1, len(pts) - 1))
        x, y = pts[i]
        d = U(r, 0.15, 0.85) * (yb - y)
        ln = U(r, 18, 64)
        brush(L, [(x - ln * 0.4, y + d + 3), (x, y + d), (x + ln * 0.6, y + d + 6 * lean)], w0=U(r, 1.0, 1.8), color=N['stone_dk'], op=U(r, 0.1, 0.28) * op, seed=int(r.integers(1e6)), taper=0.4, wob=0.5, dry=0.3)
    if line > 0:
        a_ = 0
        while a_ < len(pts) - 3:
            ln = int(r.integers(3, 7))
            brush(L, pts[a_:a_ + ln], w0=U(r, 1.6, 2.6), color=N['stone_dk'], op=line * U(r, 0.55, 1.0) * op, seed=int(r.integers(1e6)), wob=0.6, taper=0.3, dry=0.35)
            a_ += ln + int(r.integers(0, 2))
