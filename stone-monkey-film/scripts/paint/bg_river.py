"""江边断桥（S2 河边搭桥）：2900×1500。far（天 + 峡口的山 + 远处的江面和雾）/ mid（两侧的峡壁 + 雾）/ near（左右土石岸、急流、枯木、柳竹、左岸的一堆材料）
+ 三层桥 river_bridge_broken / low / high（透明 PNG，只画桥）。
坐标：地面线 y=832；桥跨 x 1080~1820；水面在豁口里 y≈1180 往下；枯木 (1400,1300)；左岸 柳 x430、竹 x160、材料堆 x 520~900；右岸 柳 x2480、竹 x2720。
用法：python3 bg_river.py [far mid near broken low high]"""
from ccommon import *
from cn_water import *
import sys

W, H = 2900, 1500
which = sys.argv[1:] or ['far', 'mid', 'near', 'broken', 'low', 'high']
XC = 1450          # 峡口 / 河道的中线
BANK_L, BANK_R = 1080, 1820


def gorge_env(W, c, half, floor=0.0):
    x = np.arange(W, dtype=F)
    return floor + (1 - floor) * (1 - np.exp(-(((x - c) / half) ** 2)))


# ═════════════════════════ far ═════════════════════════
if 'far' in which:
    S = sky(W, H, hexc('#8d9eac'), hexc('#bdc9cf'), hexc('#ebe5d5'), seed=51, horizon=0.5, cloud=0.55, scale=470)
    base = 705
    r1 = ridge_y(W, base, 250, 61, rough=0.5, scale=620)
    tot = (base - r1) / 250
    r1 = base - 250 * tot * gorge_env(W, XC, 520, 0.12)
    mountain(S, r1, 780, N['far3'], N['far1'], seed=11, tex=0.6, tex_op=0.26, snow=None, haze=0.32)
    mist(S, 0, W, 700, 70, seed=12, op=0.75)
    base = 760
    r2 = ridge_y(W, base, 210, 62, rough=0.52, scale=450)
    tot = (base - r2) / 210
    r2 = base - 210 * tot * gorge_env(W, XC, 430, 0.1)
    mountain(S, r2, 840, N['far2'], N['mid1'], seed=12, tex=0.8, tex_op=0.3, haze=0.2)
    mist(S, 0, W, 770, 60, seed=13, op=0.65)
    # 远处的江面：峡口 (1450,725) 流出来，越近越宽
    wy0 = 735
    al = np.ones((H - wy0, W), F) * vfade(H - wy0, 0, 1, 1.0)
    al = np.clip(al * 8, 0, 1) if False else np.clip(np.linspace(0, 1, H - wy0, dtype=F)[:, None] * 30, 0, 1) * np.ones((1, W), F)
    sea_body(S, 0, wy0, W, H, 71, hexc('#9fb1ba'), hexc('#3f5463'), rows=30, p=1.7, hi=hexc('#b9c6cc'), lo=hexc('#2c3d4c'), foam_k=0.5, len0=60, len1=520, dens=0.8, w1=4.2, alpha=al, swell=8)
    river_flow(S, 0, wy0 + 60, W, H, 72, n=260, len0=120, len1=700, w1=3.6, foam_k=0.3)
    mist(S, 0, W, 748, 40, seed=14, op=0.8, color=hexc('#eceae2'))
    mist(S, 0, W, 905, 80, seed=15, op=0.5, scale=340)
    mist(S, 0, W, 1060, 70, seed=16, op=0.32, scale=380)
    save_plate('river_far', S, variants=('night', 'lit'), gain=0.62, keep=0.16)

# ═════════════════════════ mid ═════════════════════════
if 'mid' in which:
    from scipy.ndimage import gaussian_filter1d
    M = Canvas(W, H)
    bottom = 1250
    xs = np.arange(W, dtype=F)
    c_l = 1 - smoothstep(640, 1300, xs)
    c_r = smoothstep(1620, 2250, xs) * 0.88
    cmask = np.maximum(c_l, c_r)
    tot = 1.0 - ridge_y(W, 1.0, 1.0, 81, rough=0.5, scale=560)
    tot = gaussian_filter1d(tot, 5)
    height = 900 * cmask ** 0.9 * (0.5 + 0.5 * tot)
    ridge = (bottom - height).astype(F)
    ymin = int(ridge.min()) - 6
    yy = np.arange(ymin, bottom + 2, dtype=F)[:, None]
    msk = np.clip((yy - ridge[None, :]) / 2.0, 0, 1) * np.clip((bottom - yy) / 8.0, 0, 1)
    with Sub(M, mask=msk, bbox=(0, ymin, W, bottom + 2)) as T:
        mountain(T, ridge, bottom, N['mid1'], N['mid2'], seed=21, tex=1.3, tex_op=0.4, lit_dir=1, glaze=0.6)
    # 崖上的松
    rng = np.random.default_rng(5)
    for i in range(30):
        x = rng.uniform(40, W - 40)
        if cmask[int(x)] < 0.35:
            continue
        yb = ridge[int(x)] + rng.uniform(14, 110)
        if yb > 800:
            continue
        pine(M, x, yb, rng.uniform(80, 150), seed=200 + i, col=N['pine'], dark=N['pine_dk'], lean=rng.normal(0, 0.03))
    mist(M, 0, W, 780, 80, seed=22, op=0.55, scale=320)
    mist(M, 0, W, 1000, 100, seed=23, op=0.5, scale=300)
    mist(M, 0, W, 1150, 90, seed=24, op=0.5, scale=300)
    save_plate('river_mid', M, variants=('night', 'lit'), gain=0.6, keep=0.18)

# ═════════════════════════ near ═════════════════════════
WATER_TOP = 1180


def bank_polys():
    xs = np.arange(0, BANK_L + 1, 40)
    topL = [(float(x), 832 + 5 * math.sin(x / 190.0) + 3 * math.sin(x / 61.0)) for x in xs]
    wallL = [(1090, 836), (1076, 872), (1098, 930), (1112, 990), (1138, 1040), (1128, 1092), (1162, 1140), (1198, 1190)]
    shoreL = [(1176, 1240), (1100, 1300), (1000, 1366), (890, 1430), (800, 1500)]
    polyL = [(-60, 832)] + topL + wallL + shoreL + [(760, 1560), (-60, 1560)]
    xs2 = np.arange(BANK_R, W + 1, 40)
    topR = [(float(x), 832 + 5 * math.sin(x / 210.0 + 1) + 3 * math.sin(x / 57.0)) for x in xs2]
    wallR = [(1810, 836), (1824, 872), (1806, 930), (1790, 990), (1762, 1040), (1770, 1098), (1736, 1150), (1702, 1196)]
    shoreR = [(1730, 1258), (1810, 1318), (1930, 1376), (2050, 1436), (2140, 1500)]
    polyR = [(W + 60, 832)] + topR[::-1] + wallR + shoreR + [(2160, 1560), (W + 60, 1560)]
    return polyL, polyR, topL, wallL, shoreL, topR, wallR, shoreR


if 'near' in which:
    Nn = Canvas(W, H)
    polyL, polyR, topL, wallL, shoreL, topR, wallR, shoreR = bank_polys()
    # ── 水（先画，岸盖在它上面）：顶边虚化进雾里
    wpoly = [(1100, 1160), (1800, 1160), (2400, 1500), (500, 1500)]
    sub = Sub(Nn, poly=wpoly, smooth=0, soft=2)
    ys_ = np.arange(sub.y0, sub.y1, dtype=F)[:, None]
    sub.m = sub.m * smoothstep(WATER_TOP - 10, WATER_TOP + 70, ys_)
    with sub as T:
        sea_body(T, 500, 1150, 2400, 1500, 91, hexc('#7f98a6'), hexc('#3a4e60'), rows=22, p=1.35, hi=hexc('#c6d3d8'), lo=hexc('#243342'), foam_k=0.6, len0=90, len1=520, dens=0.9, w1=6.0, swell=9, mott=0.18, gamma=0.8)
        river_flow(T, 500, 1170, 2400, 1500, 92, n=520, len0=120, len1=620, w1=6.0, foam_k=0.5)
        # 白浪：几条横跨河面的翻浪
        for i, (x, y, ln) in enumerate([(1180, 1236, 170), (1470, 1214, 150), (1640, 1262, 130), (1290, 1330, 230), (1560, 1360, 260), (1850, 1420, 220), (1000, 1430, 200), (1380, 1445, 180)]):
            whitecap(T, x, y, ln, h=8 + (y - 1200) * 0.03, seed=300 + i, op=0.9, w=2.4 + (y - 1200) * 0.01)
        for i, (x, y, rx, ry) in enumerate([(1330, 1280, 70, 14), (1720, 1330, 90, 17), (1180, 1390, 80, 18), (1580, 1450, 100, 20)]):
            eddy(T, x, y, rx, ry, seed=i * 3, op=0.55)
        driftwood(T, 1300, 1300, 190, seed=7, ang=-0.07, th=28, col=N['wood'] * 1.05)
    # ── 岸：土石体，岸壁的墨线
    earth_mass(Nn, polyL, 101, 832, 1500, top_col=N['earth'] * 0.98, bot_col=N['stone_dk'] * 0.85, edge_pts=wallL + shoreL[:3], strata=16, cracks=40)
    earth_mass(Nn, polyR, 102, 832, 1500, top_col=N['earth'] * 0.98, bot_col=N['stone_dk'] * 0.85, edge_pts=wallR + shoreR[:3], strata=16, cracks=40)
    # 岸壁挑檐下的阴影、垂根
    for (xa, xb, sgn) in [(980, 1096, 1), (1804, 1930, -1)]:
        wash(Nn, [(xa, 840), (xb, 840), (xb - sgn * 6, 930), (xa + (xb - xa) * 0.4, 905)], INK, op=0.26, wob=3, seed=int(xa), smooth=2, tex_k=0.1, rim=0.0)
    hanging_roots(Nn, 1040, 842, 14, seed=11)
    hanging_roots(Nn, 1860, 842, 12, seed=12)
    hanging_roots(Nn, 900, 842, 8, seed=13, ln=(20, 70))
    # 岸顶：浅色的土面（脚踩的地方）+ 草 + 断续的墨线
    for (poly_top, sd) in [(topL, 21), (topR, 22)]:
        pts = poly_top
        upper = [(x, y - 1) for x, y in pts]
        lower = [(x, y + 26 + 8 * math.sin(x / 90.0)) for x, y in pts[::-1]]
        wash(Nn, upper + lower, N['earth_lt'], op=0.55, wob=3, seed=sd, smooth=1, tex_k=0.2, rim=0.2, rim_w=4, closed=True)
        for k in range(0, len(pts) - 4, 5):
            brush(Nn, pts[k:k + 6], w0=3.2, color=INK, op=0.7, seed=sd * 10 + k, wob=1.0, taper=0.25, dry=0.3)
    gyL = np.array([832 + 5 * math.sin(x / 190.0) + 3 * math.sin(x / 61.0) for x in range(BANK_L + 1)], F)
    gyR = np.array([832 + 5 * math.sin(x / 210.0 + 1) + 3 * math.sin(x / 57.0) for x in range(W)], F)
    tufts(Nn, 0, 1060, gyL, 70, seed=31, op=0.8)
    tufts(Nn, 1840, W - 1, gyR, 70, seed=32, op=0.8)
    reeds(Nn, 960, 1086, 836, 18, seed=33, h=(30, 90))
    reeds(Nn, 1814, 1930, 836, 14, seed=34, h=(30, 80))
    # 岸脚的水线：泡沫 + 湿边
    for pts_, sd in [(wallL[-2:] + shoreL, 41), (wallR[-2:] + shoreR, 42)]:
        wash(Nn, [(x - 2, y) for x, y in pts_] + [(x + (22 if sd == 41 else -22), y + 12) for x, y in pts_[::-1]], NW['sea_deep'], op=0.3, wob=3, seed=sd, smooth=1, closed=True, rim=0.0)
        foam_line(Nn, pts_, w=4.0, seed=sd, op=0.9)
        foam_line(Nn, [(x + (12 if sd == 41 else -12), y + 8) for x, y in pts_], w=2.4, seed=sd + 1, op=0.6)
    # 石
    for i, (x, w, h) in enumerate([(300, 150, 80), (960, 120, 64), (1900, 130, 70), (2160, 170, 86), (2600, 110, 60)]):
        rock(Nn, x, 846, w, h, seed=60 + i)
    # ── 植物：左岸柳 x430 + 竹 x160；右岸柳 x2480 + 竹 x2720
    bamboo2(Nn, 160, 836, 380, seed=8, n=9)
    willow2(Nn, 430, 836, 430, seed=3)
    bamboo2(Nn, 2720, 836, 360, seed=9, n=8)
    willow2(Nn, 2480, 836, 420, seed=4, lean=-0.1)
    # ── 左岸的一堆材料（x 520~900）：靠在柳树上的竹竿、叠放的木板、一圈粗绳、锯和斧、竹下冒出的笋
    rr = np.random.default_rng(77)
    for k in range(8):
        bx = 548 + k * 11 + rr.normal(0, 3)
        by = 838 + rr.normal(0, 3)
        tx = 462 + k * 8 + rr.normal(0, 3)
        ty = 520 + rr.uniform(-30, 40) + k * 3
        bamboo_pole(Nn, (bx, by), (tx, ty), w=15 + rr.normal(0, 1), seed=500 + k, node=70)
    # 木板堆（侧面）：每层几块，错开
    sx0, sy = 700, 836
    for layer in range(5):
        y_ = sy - layer * 25 - 12
        x_a = sx0 + rr.uniform(-12, 18) - (layer % 2) * 10
        x_b = x_a + 205 + rr.uniform(-18, 22)
        plank(Nn, x_a, y_, x_b, y_ + rr.normal(0, 1.2), th=23, seed=600 + layer, jag0=(layer == 3), jag1=(layer % 2 == 1 and layer != 1))
    # 斜靠的两块板
    plank(Nn, 912, 836 - 10, 936, 836 - 175, th=24, seed=650, jag1=True)
    rope_coil(Nn, 800, 852, 52, 12, turns=3, seed=5)
    saw(Nn, 870, 820, ln=170, seed=3, ang=-0.55)
    axe(Nn, 664, 845, ln=116, seed=4, ang=-0.14)
    rope_sag(Nn, (922, 700), (1010, 842), 22, w=8, seed=9)
    # 笋：竹竿脚下冒出来
    for i, (x, h) in enumerate([(618, 70), (642, 48), (668, 62), (592, 40)]):
        shoot(Nn, x, 846, h, seed=700 + i)
    tufts(Nn, 520, 940, 846, 20, seed=35, op=0.8)
    save_plate('river_near', Nn, variants=('night', 'lit'), gain=0.66, keep=0.2)


# ═════════════════════════ 桥 ═════════════════════════
def deck(L, xa, xb, seed, jag_a=False, jag_b=False, y=832, lash=True, beam=True):
    """桥面：上面一条浅色的板面（有板缝），前面是一排板头（深一点），下面一根粗竹梁，几处绳扎。xa、xb 是桥面的两端；jag_a/b 表示该端是参差的断口。"""
    r = np.random.default_rng(seed)
    # 板面
    top = [(xa, y - 11)]
    bot = [(xa, y + 1)]
    if jag_a:
        top = [(xa + 6, y - 11), (xa - 8, y - 6), (xa + 8, y - 1)]
    pa = [(xa, y - 11), (xb, y - 11), (xb, y + 1), (xa, y + 1)]
    wash(L, pa, NW['plank_lt'], op=0.95, wob=0.6, seed=seed, smooth=0, tex_k=0.2, rim=0.2, rim_w=2)
    # 板头一排
    x = xa
    k = 0
    while x < xb - 6:
        wd = r.uniform(40, 50)
        x2 = min(x + wd, xb)
        c = mix(NW['plank'], NW['plank_dk'], r.uniform(0.0, 0.5))
        y0 = y + 1 + r.normal(0, 0.8)
        h = r.uniform(21, 25)
        last = x2 >= xb - 1
        first = k == 0
        pts = [(x + 1, y0), (x2 - 1, y0), (x2 - 1, y0 + h), (x + 1, y0 + h)]
        if (last and jag_b):
            dx = r.uniform(4, 14)
            pts = [(x + 1, y0), (x2 - 1, y0), (x2 - 1 - dx, y0 + h * 0.3), (x2 - 1 - dx * 2.2, y0 + h * 0.62), (x2 - 1 - dx * 0.8, y0 + h)] + [(x + 1, y0 + h)]
        if (first and jag_a):
            dx = r.uniform(4, 14)
            pts = [(x + 1 + dx * 0.8, y0), (x2 - 1, y0), (x2 - 1, y0 + h), (x + 1 + dx * 2.0, y0 + h * 0.66), (x + 1 + dx, y0 + h * 0.3)]
        wash(L, pts, c, op=0.97, wob=0.4, seed=int(r.integers(1e6)), smooth=0, tex_k=0.22, rim=0.3, rim_w=2)
        st = []
        for _ in range(5):
            px = r.uniform(x + 4, x2 - 4)
            st.append((px, y0 + 3, px + r.normal(0, 1), y0 + h - 3, r.uniform(0.8, 1.3), r.uniform(0.2, 0.5)))
        flicks(L, st, color=NW['plank_dk'])
        brush(L, pts + [pts[0]], w0=1.8, color=INK, op=0.65, seed=int(r.integers(1e6)), wob=0.4, taper=0.1, smooth=False)
        # 板面上的缝
        if not (last and jag_b) and not (first and jag_a):
            brush(L, [(x, y - 11), (x + r.uniform(-2, 4), y + 1)], w0=1.4, color=INK, op=0.4, seed=int(r.integers(1e6)), taper=0.3, smooth=False)
        x = x2 + r.uniform(1.5, 3.5)
        k += 1
    brush(L, [(xa, y - 11), ((xa + xb) / 2, y - 11.5), (xb, y - 11)], w0=2.0, color=INK, op=0.6, seed=seed + 3, wob=0.6, taper=0.05, dry=0.3)
    if beam:
        ax_ = xa - (0 if jag_a else 8)
        bx_ = xb + (0 if jag_b else 8)
        bamboo_pole(L, (ax_, y + 38), (bx_, y + 38), w=19, seed=seed + 7, node=84, broken=jag_b)
        if jag_a:
            wash(L, [(ax_, y + 29), (ax_ + 10, y + 34), (ax_ - 3, y + 40), (ax_ + 8, y + 47)], NW['bamboo_lt'], op=0.9, wob=0.4, smooth=0, tex_k=0.1)
    if lash:
        step = 190
        x = xa + 70
        while x < xb - 30:
            lashing(L, x, y + 22, w=22, seed=int(x), ang=0.0)
            x += step


def pier_pair(L, x, y_top, y_foot, spread, seed, w=15, ripple=True):
    """一对竹支脚（略向外撇），插进水里，脚边一圈白浪。"""
    for s, sd in ((-1, 0), (1, 1)):
        bamboo_pole(L, (x + s * spread * 0.28, y_top), (x + s * spread, y_foot), w=w, seed=seed + sd, node=66)
    # 横拉的小撑
    yb = y_top + (y_foot - y_top) * 0.45
    bamboo_pole(L, (x - spread * 0.62, yb), (x + spread * 0.62, yb + 4), w=9, seed=seed + 5, node=60)
    lashing(L, x - spread * 0.6, yb, w=16, seed=seed + 6)
    lashing(L, x + spread * 0.6, yb + 4, w=16, seed=seed + 7)
    if ripple:
        for s in (-1, 1):
            fx, fy = x + s * spread, y_foot
            foam_line(L, [(fx - 30, fy + 4), (fx, fy + 9), (fx + 30, fy + 3)], w=3.2, seed=seed + 20 + s, op=0.9)
            ripple_rings(L, fx, fy + 6, 52, 8, n=2, seed=seed + 30 + s, col=NW['foam'], shade=NW['sea_deep'], op=0.6, w=1.8)


def water_foot(L, x, y):
    foam_line(L, [(x - 34, y + 2), (x, y + 8), (x + 34, y + 2)], w=3.0, seed=int(x), op=0.9)
    ripple_rings(L, x, y + 6, 54, 8, n=2, seed=int(x) + 3, col=NW['foam'], shade=NW['sea_deep'], op=0.6, w=1.8)


def stake(L, x, y0, y1, w=22, seed=0, top_cut=True):
    """木桩：粗木头，顶上有绳勒出的槽。"""
    r = np.random.default_rng(seed)
    pts = [(x - w / 2, y0 + 4), (x - w * 0.45, y0), (x + w * 0.1, y0 - 3), (x + w / 2, y0 + 2), (x + w * 0.52, y1), (x - w * 0.5, y1)]
    wash(L, pts, N['wood'] * 1.05, op=0.97, wob=0.7, seed=seed, smooth=1, tex_k=0.25, rim=0.25, rim_w=2)
    wash(L, [(x + w * 0.05, y0 + 2), (x + w / 2, y0 + 2), (x + w * 0.52, y1), (x + w * 0.05, y1)], N['wood_dk'], op=0.5, wob=0.6, seed=seed + 1, smooth=0, tex_k=0.1)
    st = []
    for _ in range(int((y1 - y0) / 8)):
        px = x + r.uniform(-w * 0.4, w * 0.4)
        py = r.uniform(y0 + 4, y1 - 12)
        st.append((px, py, px + r.normal(0, 0.8), py + r.uniform(8, 22), r.uniform(0.9, 1.6), r.uniform(0.25, 0.6)))
    flicks(L, st, color=INK)
    brush(L, [(x - w * 0.5, y0 + 4), (x - w * 0.5, (y0 + y1) / 2), (x - w * 0.5, y1)], w0=2.0, color=INK, op=0.6, seed=seed + 2, wob=0.8, taper=0.1, dry=0.3)
    brush(L, [(x + w * 0.5, y0 + 4), (x + w * 0.52, (y0 + y1) / 2), (x + w * 0.52, y1)], w0=2.0, color=INK, op=0.6, seed=seed + 3, wob=0.8, taper=0.1, dry=0.3)
    brush(L, [(x - w * 0.5, y0 + 4), (x - w * 0.1, y0 - 1), (x + w * 0.5, y0 + 2)], w0=2.0, color=INK, op=0.6, seed=seed + 4, wob=0.5, taper=0.2)


if 'broken' in which:
    B = Canvas(W, H)
    # 两头残存的桥面
    deck(B, 1060, 1290, 810, jag_b=True)
    deck(B, 1610, 1840, 811, jag_a=True)
    # 残缺的竹桩：左边一根斜着、断了；右边两根
    bamboo_pole(B, (1200, 876), (1166, 1090), w=15, seed=820, node=64, broken=True)
    bamboo_pole(B, (1250, 878), (1272, 1010), w=15, seed=821, node=64, broken=True)
    bamboo_pole(B, (1100, 876), (1090, 1160), w=15, seed=822, node=64)
    water_foot(B, 1090, 1190)
    bamboo_pole(B, (1690, 878), (1740, 1060), w=15, seed=823, node=64, broken=True)
    bamboo_pole(B, (1790, 876), (1760, 1160), w=15, seed=824, node=64)
    water_foot(B, 1760, 1180)
    # 断口垂下来的碎竹
    bamboo_pole(B, (1290, 876), (1300, 940), w=15, seed=825, node=40, broken=True)
    bamboo_pole(B, (1612, 876), (1590, 928), w=15, seed=826, node=40, broken=True)
    # 桩子 + 两根粗绳（从两头的桩子上垂下来，微微下垂）
    stake(B, 1254, 780, 846, w=24, seed=830)
    stake(B, 1646, 780, 846, w=24, seed=831)
    lashing(B, 1254, 798, w=26, seed=840)
    lashing(B, 1646, 798, w=26, seed=841)
    lashing(B, 1254, 836, w=26, seed=842)
    lashing(B, 1646, 836, w=26, seed=843)
    pA = rope_sag(B, (1256, 800), (1644, 800), 118, w=10, seed=850)
    pB = rope_sag(B, (1258, 838), (1642, 838), 170, w=11, seed=851)
    # 挂在绳上的断板
    def hang_plank(rope_pts, t, ln, ang, seed):
        i = int(t * (len(rope_pts) - 1))
        x, y = rope_pts[i]
        ex, ey = x + math.cos(ang) * ln, y + math.sin(ang) * ln
        rope(B, [(x, y + 3), (x + 4, y + 22), ((x + ex) / 2 * 0 + x + math.cos(ang) * 14, y + math.sin(ang) * 14 + 8)], w=4, seed=seed + 9)
        plank(B, x + math.cos(ang) * 10, y + math.sin(ang) * 10 + 10, ex, ey + 10, th=22, seed=seed, jag1=True)
        lashing(B, x + math.cos(ang) * 8, y + math.sin(ang) * 8 + 8, w=20, seed=seed + 4, ang=ang)
    hang_plank(pB, 0.30, 130, math.radians(74), 860)
    hang_plank(pB, 0.66, 96, math.radians(98), 870)
    hang_plank(pA, 0.52, 110, math.radians(58), 880)
    save_plate('river_bridge_broken', B, variants=('night', 'lit'), gain=0.66, keep=0.2)

if 'low' in which:
    B = Canvas(W, H)
    deck(B, 1060, 1840, 900)
    # 竹支脚：几对，插进水里
    for i, (x, yf) in enumerate([(1180, 1226), (1450, 1262), (1720, 1232)]):
        pier_pair(B, x, 880, yf, 70, 910 + i * 10)
    # 一道低低的绳栏：桩 + 绳
    posts = [1092, 1230, 1370, 1510, 1650, 1790]
    for i, x in enumerate(posts):
        bamboo_pole(B, (x, 822), (x, 764), w=11, seed=930 + i, node=40)
        lashing(B, x, 826, w=16, seed=940 + i)
    for i in range(len(posts) - 1):
        rope_sag(B, (posts[i], 770), (posts[i + 1], 770), 10, w=6, seed=950 + i)
    save_plate('river_bridge_low', B, variants=('night', 'lit'), gain=0.66, keep=0.2)

if 'high' in which:
    B = Canvas(W, H)
    deck(B, 1060, 1840, 920)
    # 高大的支架：三座，每座两根立竹、几道横梁、交叉斜撑，一直下到水里
    piers = [(1190, 1228), (1450, 1262), (1710, 1232)]
    for i, (x, yf) in enumerate(piers):
        sp = 78
        ys = [880, 972, 1064, 1156, yf]
        # 立竹（略外撇）：分段，每段之间一道绳扎
        for s, sd in ((-1, 0), (1, 1)):
            bamboo_pole(B, (x + s * sp * 0.78, ys[0]), (x + s * sp * (0.78 + 0.06 * 4), yf), w=17, seed=1000 + i * 10 + sd, node=70)
        # 横梁 + 交叉斜撑
        for k in range(len(ys) - 1):
            ya, yb = ys[k], ys[k + 1]
            xa_l, xa_r = x - sp * (0.78 + 0.06 * k), x + sp * (0.78 + 0.06 * k)
            xb_l, xb_r = x - sp * (0.78 + 0.06 * (k + 1)), x + sp * (0.78 + 0.06 * (k + 1))
            bamboo_pole(B, (xa_l - 8, ya + 12), (xa_r + 8, ya + 12), w=11, seed=1100 + i * 10 + k, node=70)
            if k < len(ys) - 1:
                bamboo_pole(B, (xa_l, ya + 12), (xb_r, yb + 12), w=8, seed=1200 + i * 10 + k, node=70, ink=True)
                bamboo_pole(B, (xa_r, ya + 12), (xb_l, yb + 12), w=8, seed=1300 + i * 10 + k, node=70, ink=True)
            lashing(B, xa_l, ya + 12, w=18, seed=1400 + i * 10 + k)
            lashing(B, xa_r, ya + 12, w=18, seed=1500 + i * 10 + k)
            lashing(B, x, ya + 12, w=16, seed=1600 + i * 10 + k)
        for s in (-1, 1):
            fx = x + s * sp * (0.78 + 0.06 * 4)
            water_foot(B, fx, yf)
    # 竹栏杆：立柱 + 横杆 + 斜撑
    posts = [1092, 1210, 1330, 1450, 1570, 1690, 1810]
    ytop, ymid, yb = 712, 768, 912
    for i, x in enumerate(posts):
        bamboo_pole(B, (x, yb - 90), (x, ytop - 6), w=13, seed=1700 + i, node=44)
    for i in range(len(posts) - 1):
        a, b = posts[i], posts[i + 1]
        bamboo_pole(B, (a - 6, ytop + 4), (b + 6, ytop + 4), w=11, seed=1750 + i, node=60)
        bamboo_pole(B, (a, ymid), (b, ymid + 2), w=9, seed=1760 + i, node=60)
        bamboo_pole(B, (a, ymid + 4), (b, ytop + 6), w=7, seed=1770 + i, node=60)
    for i, x in enumerate(posts):
        lashing(B, x, ytop + 4, w=16, seed=1800 + i)
        lashing(B, x, ymid + 2, w=16, seed=1810 + i)
    save_plate('river_bridge_high', B, variants=('night', 'lit'), gain=0.66, keep=0.2)
