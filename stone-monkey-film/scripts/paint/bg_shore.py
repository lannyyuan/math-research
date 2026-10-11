"""东海边（S3 开头）：2900×1080。far（无月的夜空 + 黑色的海 + 远处小岛）/ mid（海面的浪、礁石）/ near（左半沙滩 + 黑礁石 + 海藻贝壳；x≥1450 一条贴着海面的窄窄的干路；路前的近海）
+ shore_water_cover（覆盖干路的海水带 x1400~2900, y≈790~885，带透明）。
坐标：沙滩地面线 y=832（x<1450）；干路 x 1450~2900，路面 y≈819~853（宽≈34）；海天线 y≈610；小岛 x≈2300。
用法：python3 bg_shore.py [far mid near cover]"""
from ccommon import *
from cn_water import *
import sys

W, H = 2900, 1080
which = sys.argv[1:] or ['far', 'mid', 'near', 'cover']
HOR = 610
ROAD_X0 = 1450
ROAD_T, ROAD_B = 819, 853


def road_edges(x):
    """路面上下沿：中线缓缓起伏，宽度 28~42 之间变化。"""
    x = np.asarray(x, F)
    c = 836 + 5 * np.sin(x / 420.0 + 1) + 3 * np.sin(x / 131.0) + 1.2 * np.sin(x / 37.0)
    w = 34 + 5.5 * np.sin(x / 173.0 + 2) + 2.5 * np.sin(x / 49.0)
    return c - w / 2, c + w / 2


def sand_ripples(L, x0, x1, y0, y1, n, seed, op=0.4):
    """沙面上被潮水留下的波纹：一道道弯弯的短线（亮一道暗一道）。"""
    r = np.random.default_rng(seed)
    for _ in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        ln = r.uniform(40, 150)
        bend = r.normal(0, 3)
        pts = [(x, y), (x + ln * 0.5, y + bend), (x + ln, y + r.normal(0, 2))]
        brush(L, pts, w0=r.uniform(1.4, 3.0), color=NW['sand_dk'] * 0.8, op=op * r.uniform(0.5, 1.0), seed=int(r.integers(1e6)), wob=1.0, taper=0.4, dry=0.3)
        brush(L, [(a, b + 3) for a, b in pts], w0=r.uniform(1.0, 2.0), color=NW['sand_lt'], op=op * r.uniform(0.5, 1.1), seed=int(r.integers(1e6)), wob=1.0, taper=0.4, dry=0.35)


def kelp_tangle(L, x, y, n, seed, spread=90):
    """搁浅的海藻：几条深橄榄色的带子，扭着、缠着，躺在沙上。"""
    r = np.random.default_rng(seed)
    for _ in range(n):
        x0 = x + r.normal(0, spread * 0.5)
        y0 = y + r.normal(0, 5)
        a = r.uniform(-0.5, 0.5) + (0 if r.random() < 0.7 else math.pi)
        pts = [(x0, y0)]
        for k in range(6):
            a += r.normal(0, 0.55)
            x0 += math.cos(a) * r.uniform(12, 26)
            y0 += math.sin(a) * r.uniform(5, 11)
            pts.append((x0, y0))
        brush(L, pts, w0=r.uniform(3.5, 6.5), w1=1.4, color=mix(NW['weed_dk'], NW['basalt_dk'], r.uniform(0.2, 0.7)), op=0.92, seed=int(r.integers(1e6)), wob=0.8, taper=0.2)
        brush(L, [(a_ - 1, b_ - 1.5) for a_, b_ in pts[1:]], w0=1.4, color=NW['weed_dry'], op=0.5, seed=int(r.integers(1e6)), taper=0.3, wob=0.6, dry=0.3)
    # 几个小气囊
    st = []
    for _ in range(n * 2):
        px, py = x + r.normal(0, spread * 0.5), y + r.normal(0, 7)
        st.append((px, py, px + 2, py, r.uniform(3.0, 5.0), 0.8))
    flicks(L, st, color=NW['weed_dry'])


def reef_rock(L, cx, by, w, h, seed, foam=True):
    """黑礁石：玄武岩，硬朗的棱面，顶上几笔受光的亮边；脚下一圈白浪。"""
    rock(L, cx, by, w, h, seed=seed, col=NW['basalt'], dark=NW['basalt_dk'], light=NW['basalt_lt'], lit_dir=1)
    rng = np.random.default_rng(seed + 3)
    st = []
    for _ in range(int(w * h / 600)):
        px = cx + rng.uniform(-w * 0.42, w * 0.42)
        py = by - rng.uniform(0.1, 0.92) * h * (1 - abs(px - cx) / (w * 0.62))
        ln = rng.uniform(8, 26)
        st.append((px, py, px + rng.normal(0, 3), py + ln, rng.uniform(0.9, 1.8), rng.uniform(0.15, 0.4)))
    flicks(L, st, color=NW['sand_lt'] * 0.8)
    if foam:
        foam_line(L, [(cx - w * 0.62, by + 2), (cx - w * 0.3, by + 9), (cx + w * 0.3, by + 8), (cx + w * 0.64, by + 1)], w=3.0, seed=seed + 7, op=0.85)
        foam_line(L, [(cx - w * 0.5, by + 12), (cx, by + 17), (cx + w * 0.55, by + 11)], w=2.0, seed=seed + 8, op=0.55, spray=False)


# ═════════════════════════ far ═════════════════════════
if 'far' in which:
    S = sky(W, H, hexc('#76869a'), hexc('#97a4af'), hexc('#cdd0cc'), seed=61, horizon=0.58, cloud=0.9, scale=500)
    # 稀疏的星（云缝里）
    rs = np.random.default_rng(3)
    for _ in range(46):
        x, y = rs.uniform(30, W - 30), rs.uniform(20, 430) ** 1.0
        dots(S, [(x, y, rs.uniform(0.9, 1.9))], N['paper'], op=rs.uniform(0.45, 0.95))
    mist(S, 0, W, HOR - 10, 36, seed=62, op=0.7, color=hexc('#e4e4de'))
    # 海：黑的，海天线清楚，越往下越深
    al = np.clip(np.linspace(0, 1, H - HOR, dtype=F)[:, None] * 120, 0, 1) * np.ones((1, W), F)
    sea_body(S, 0, HOR, W, H, 63, hexc('#6a7d8c'), hexc('#1f2d3a'), rows=30, p=1.9, hi=hexc('#9fb1bc'), lo=hexc('#17222d'), foam_k=0.45, len0=40, len1=420, dens=1.0, w1=4.4, alpha=al, swell=7, mott=0.12)
    # 小岛 x≈2300：矮矮的黑色石包，上面一两棵歪树
    ix, iy = 2300, HOR + 2
    isl = [(ix - 95, iy), (ix - 70, iy - 14), (ix - 38, iy - 26), (ix - 8, iy - 30), (ix + 28, iy - 24), (ix + 60, iy - 13), (ix + 92, iy)]
    wash(S, isl, hexc('#3d4c58'), op=0.97, wob=1.2, seed=64, smooth=2, tex_k=0.25, rim=0.25, rim_w=2)
    wash(S, [(ix + 5, iy), (ix + 18, iy - 27), (ix + 40, iy - 21), (ix + 66, iy - 12), (ix + 92, iy)], hexc('#222f3a'), op=0.6, wob=1, seed=65, smooth=1)
    brush(S, isl, w0=2.0, color=INK, op=0.7, seed=66, wob=0.6, taper=0.2, dry=0.3)
    old_tree(S, ix - 18, iy - 27, 62, seed=67, col=INK * 0.9, depth=3, spread=0.9, trunk_w=5)
    old_tree(S, ix + 34, iy - 21, 44, seed=68, col=INK * 0.9, depth=3, spread=0.9, trunk_w=4)
    foam_line(S, [(ix - 100, iy + 3), (ix - 40, iy + 6), (ix + 40, iy + 6), (ix + 100, iy + 3)], w=2.2, seed=69, op=0.7, spray=False)
    mist(S, ix - 300, ix + 300, iy - 2, 18, seed=70, op=0.5, color=hexc('#dfe0da'), scale=120)
    save_plate('shore_far', S, variants=('night', 'lit'), gain=0.6, keep=0.15)

# ═════════════════════════ mid ═════════════════════════
if 'mid' in which:
    M = Canvas(W, H)
    # 路后面的海：浪纹 + 白浪（越近越大）
    sea_rows(M, 0, W, 640, 842, 71, rows=26, p=1.55, hi=hexc('#a9bac4'), lo=hexc('#141e29'), foam_k=0.85, len0=40, len1=380, dens=1.0, w1=4.6)
    # 几处翻起的白浪
    for i, (x, y, ln) in enumerate([(300, 735, 180), (860, 770, 220), (1560, 750, 200), (2050, 790, 240), (2560, 800, 220), (1180, 805, 260)]):
        whitecap(M, x, y, ln, h=7 + (y - 700) * 0.04, seed=200 + i, op=0.8, w=1.8 + (y - 700) * 0.012)
    # 浪的“涌”：宽的、颜色略浅的湿色块
    r = np.random.default_rng(72)
    for _ in range(9):
        y = r.uniform(680, 810)
        x = r.uniform(-100, W - 200)
        ln = r.uniform(300, 800) * (0.6 + (y - 680) / 200)
        th = 6 + (y - 680) * 0.12
        wash(M, [(x, y), (x + ln * 0.3, y - th), (x + ln * 0.7, y - th * 0.7), (x + ln, y), (x + ln * 0.5, y + th * 0.8)], hexc('#8fa3b0'), op=0.12, wob=3, seed=int(r.integers(1e6)), smooth=2, tex_k=0.1, rim=0.18, rim_w=4)
    # 沙滩背后（x<1450）水里的礁石
    for i, (x, w, h, y) in enumerate([(640, 90, 38, 812), (1010, 70, 28, 806), (1340, 110, 46, 818)]):
        reef_rock(M, x, y, w, h, 80 + i)
    mist(M, 0, W, 640, 40, seed=73, op=0.35, color=hexc('#dcdfdc'), scale=300)
    save_plate('shore_mid', M, variants=('night', 'lit'), gain=0.6, keep=0.15)

# ═════════════════════════ near ═════════════════════════
if 'near' in which:
    Nn = Canvas(W, H)
    xs = np.arange(W, dtype=F)
    # ── 路前的近海（先画，沙和路盖在上面）
    shore = [(1470, 846), (1440, 880), (1380, 915), (1330, 960), (1290, 1010), (1240, 1060), (1190, 1130)]
    sea_poly = [(1480, 840), (W + 60, 840), (W + 60, H + 40)] + [(1190, H + 40)] + shore[::-1][1:]
    sub = Sub(Nn, poly=densify(sea_poly, 60), smooth=0, soft=1.5)
    ys_ = np.arange(sub.y0, sub.y1, dtype=F)[:, None]
    with sub as T:
        sea_body(T, 1180, 840, W + 40, H + 10, 91, hexc('#5b7080'), hexc('#1c2a36'), rows=15, p=1.25, hi=hexc('#a9bbc6'), lo=hexc('#101a24'), foam_k=0.75, len0=90, len1=620, dens=1.0, w1=7.5, swell=8, mott=0.14, hook=1.3)
        for i, (x, y, ln) in enumerate([(1620, 905, 260), (2000, 940, 330), (2480, 925, 280), (1800, 1010, 380), (2300, 1030, 360), (1450, 1050, 300)]):
            whitecap(T, x, y, ln, h=12 + (y - 900) * 0.04, seed=500 + i, op=0.92, w=3.0 + (y - 900) * 0.01)
    # ── 沙滩：背面（y≈832）是海，右前是海岸线
    top = []
    for x in range(-60, ROAD_X0 + 41, 40):
        dune = 62 * math.exp(-(((x - 110) / 250.0) ** 2))
        top.append((float(x), 832 + 5 * math.sin(x / 150.0) + 3 * math.sin(x / 41.0) - dune))
    sand_poly = top + shore + [(1190, 1140), (-60, 1140)]
    with Sub(Nn, poly=densify(sand_poly, 40), smooth=1, wob=1.0, seed=3) as T:
        fill_region(T, -60, 740, 1500, 1140, hexc('#b0a88e'), hexc('#bfb393'), seed=95, mott=0.14, gamma=1.0)
        # 湿沙：靠海的一圈深而发亮
        for pts_, sd in [([(x, y + 4) for x, y in top], 1)]:
            wash(T, [(x, y - 10) for x, y in top] + [(x, y + 34 + 6 * math.sin(x / 70)) for x, y in top[::-1]], NW['sand_wet'], op=0.55, wob=3, seed=96, smooth=1, tex_k=0.15, rim=0.0)
        wash(T, [(1480, 846), (1190, 1140), (1250, 1140), (1500, 870)], NW['sand_wet'], op=0.0, wob=1, seed=97)
        wash(T, shore + [(1190 - 40, 1140), (1190 - 90, 1140)] + [(x - 90 + (y - 846) * 0.1, y + 10) for x, y in shore[::-1]], NW['sand_wet'], op=0.5, wob=4, seed=98, smooth=1, tex_k=0.15, rim=0.0)
        sand_ripples(T, -60, 1450, 850, 1110, 120, 99)
        # 沙粒的点苔
        r = np.random.default_rng(100)
        st = []
        for _ in range(900):
            px, py = r.uniform(-40, 1480), r.uniform(840, 1130)
            st.append((px, py, px + r.uniform(1, 3), py + r.normal(0, 0.8), r.uniform(1.0, 2.0), r.uniform(0.15, 0.45)))
        flicks(T, st, color=NW['sand_dk'])
        pebbles(T, 0, 1450, (860, 1100), 70, seed=101, col=NW['sand_dk'], dk=NW['basalt'], rmin=2.5, rmax=8)
    # 沙滩背面的水线：一道白浪 + 湿边的墨线
    for k in range(0, len(top) - 4, 5):
        brush(Nn, top[k:k + 6], w0=2.4, color=INK, op=0.5, seed=300 + k, wob=0.8, taper=0.3, dry=0.4)
    foam_line(Nn, [(x, y + 3) for x, y in top[1:]], w=3.4, seed=102, op=0.7)
    foam_line(Nn, [(x + 4, y + 11) for x, y in top[6:]], w=2.0, seed=103, op=0.5, spray=False)
    # 近海岸线上的泡沫
    foam_line(Nn, shore, w=4.4, seed=104, op=0.9)
    foam_line(Nn, [(x - 14, y + 10) for x, y in shore], w=2.6, seed=105, op=0.65)
    brush(Nn, [(x - 20, y + 22) for x, y in shore], w0=2.0, color=NW['sea_hi'], op=0.4, seed=106, wob=1.5, taper=0.3, dry=0.4)
    # 沙上的东西：黑礁石、海藻、贝壳
    for i, (x, w, h, y) in enumerate([(250, 250, 190, 880), (120, 130, 92, 910), (385, 130, 84, 896), (760, 150, 82, 872), (822, 76, 44, 882), (1010, 120, 64, 880), (1296, 190, 104, 868), (1385, 84, 50, 884), (60, 120, 70, 960)]):
        reef_rock(Nn, x, y, w, h, 120 + i, foam=False)
        wash(Nn, [(x - w * 0.55, y + 2), (x + w * 0.6, y + 2), (x + w * 0.75, y + 14), (x - w * 0.7, y + 14)], NW['sand_wet'], op=0.4, wob=2, seed=130 + i, smooth=1, rim=0.0)
    kelp_tangle(Nn, 520, 900, 5, 140)
    kelp_tangle(Nn, 1100, 960, 4, 141)
    kelp_tangle(Nn, 880, 1040, 3, 142, spread=60)
    kelp_tangle(Nn, 1370, 905, 3, 143, spread=50)
    for i, (x, y, rr, kind) in enumerate([(440, 940, 14, 's'), (610, 1000, 12, 'c'), (700, 925, 9, 's'), (930, 975, 15, 's'), (1180, 930, 10, 'c'), (1050, 1060, 13, 's'), (330, 1010, 16, 's')]):
        if kind == 's':
            scallop(Nn, x, y, rr, seed=150 + i, col=NW['sand_lt'], tilt=0.4 * (i - 3) / 3)
        else:
            spiral_shell(Nn, x, y, rr * 0.5, seed=160 + i, col=NW['sand_lt'])
    # 沙丘上的枯草
    reeds(Nn, 0, 330, 800, 34, seed=170, h=(40, 120), col=NW['weed_dry'] * 0.8)
    # ── 干路：x 1450~2900，窄窄的一条，两侧湿润发亮
    xr = np.arange(ROAD_X0 - 6, W + 20, dtype=F)
    rt, rb = road_edges(xr)
    taper = np.clip((xr - ROAD_X0) / 60.0, 0.0, 1.0)      # 左端从沙滩里长出来
    rt = rt + (1 - taper) * 6
    rb = rb - (1 - taper) * 6
    # 两侧的湿沙（暗、发亮）
    wash(Nn, list(zip(xr[::18], rt[::18] - 6)) + list(zip(xr[::18][::-1], (rb[::18] + 12)[::-1])), NW['sand_wet'], op=0.7, wob=1.2, seed=180, smooth=1, tex_k=0.12, rim=0.0)
    # 路面：一块块不规则的石板 / 压实的沙
    r = np.random.default_rng(182)
    x = float(ROAD_X0 - 6)
    k = 0
    while x < W + 10:
        ln = r.uniform(46, 150)
        x2 = x + ln
        t1, b1 = road_edges(np.array([x, x2], F))
        sk = r.uniform(-6, 6)
        quad = [(x, t1[0] + r.normal(0, 0.8)), (x2, t1[1] + r.normal(0, 0.8)), (x2 + sk, b1[1] + r.normal(0, 0.8)), (x + sk * 0.6, b1[0] + r.normal(0, 0.8))]
        c = mix(NW['sand'] * 0.84, NW['sand_wet'], r.uniform(0.05, 0.5)) * r.uniform(0.94, 1.06)
        wash(Nn, quad, c, op=0.98, wob=0.9, seed=int(r.integers(1e6)), smooth=1, tex_k=0.22, rim=0.25, rim_w=2.0)
        # 板面上一线受光
        wash(Nn, [quad[0], quad[1], (quad[1][0], quad[1][1] + 6), (quad[0][0], quad[0][1] + 5)], NW['sand_lt'], op=0.35, wob=0.8, seed=int(r.integers(1e6)), smooth=0, rim=0.0)
        brush(Nn, [quad[1], quad[2]], w0=1.8, color=INK, op=r.uniform(0.35, 0.6), seed=int(r.integers(1e6)), taper=0.3, wob=0.5, smooth=False)
        # 裂纹、苔点
        if r.random() < 0.5:
            px = x + r.uniform(8, ln - 8)
            brush(Nn, [(px, t1[0] + 5), (px + r.normal(0, 4), (t1[0] + b1[0]) / 2 + 4), (px + r.normal(0, 5), b1[0] - 3)], w0=1.2, color=INK, op=0.35, seed=int(r.integers(1e6)), taper=0.3, wob=0.6)
        x = x2 + r.uniform(-1, 2)
        k += 1
    st = []
    for _ in range(420):
        px = r.uniform(ROAD_X0, W)
        t_, b_ = road_edges(np.array([px], F))
        py = r.uniform(t_[0] + 2, b_[0] - 2)
        st.append((px, py, px + r.uniform(2, 8), py + r.normal(0, 0.5), r.uniform(0.9, 1.5), r.uniform(0.2, 0.5)))
    flicks(Nn, st, color=NW['sand_dk'])
    # 路的上沿 / 下沿：墨线（断续）
    segx = np.arange(ROAD_X0, W + 20, 12, dtype=F)
    st_, sb_ = road_edges(segx)
    k = 0
    while k < len(segx) - 6:
        ln = int(r.integers(8, 22))
        brush(Nn, list(zip(segx[k:k + ln], st_[k:k + ln])), w0=r.uniform(2.0, 3.2), color=INK, op=r.uniform(0.5, 0.8), seed=int(r.integers(1e6)), wob=0.6, taper=0.3, dry=0.35)
        brush(Nn, list(zip(segx[k:k + ln], sb_[k:k + ln] + 1)), w0=r.uniform(2.6, 4.0), color=INK, op=r.uniform(0.45, 0.75), seed=int(r.integers(1e6)), wob=0.6, taper=0.3, dry=0.35)
        k += ln + int(r.integers(1, 4))
    # 水光：贴着路两边的一道道湿亮的细线 + 路面上的几处反光
    for _ in range(150):
        x = r.uniform(ROAD_X0 + 20, W)
        side = r.choice([-1, 1])
        t_, b_ = road_edges(np.array([x], F))
        y = (t_[0] - r.uniform(2, 10)) if side < 0 else (b_[0] + r.uniform(3, 14))
        ln = r.uniform(30, 120)
        brush(Nn, [(x, y), (x + ln / 2, y + r.normal(0, 1)), (x + ln, y + r.normal(0, 1))], w0=r.uniform(1.4, 3.0), color=NW['foam'], op=r.uniform(0.35, 0.85), seed=int(r.integers(1e6)), wob=0.5, taper=0.4, dry=0.35)
    # 水里的倒影：路脚下一小段发白的竖纹
    for _ in range(40):
        x = r.uniform(ROAD_X0 + 40, W)
        t_, b_ = road_edges(np.array([x], F))
        brush(Nn, [(x, b_[0] + 8), (x + r.normal(0, 2), b_[0] + r.uniform(16, 34))], w0=r.uniform(1.6, 3.0), color=NW['sand_lt'], op=r.uniform(0.15, 0.35), seed=int(r.integers(1e6)), taper=0.5, wob=0.6, dry=0.3)
    # 路脚下的暗影
    brush(Nn, [(x, b + 9) for x, b in zip(segx[::3], sb_[::3])], w0=8, color=NW['sea_deep'], op=0.5, seed=184, wob=1.5, taper=0.05, dry=0.2)
    # 路上零星的小石、贝壳
    for i in range(14):
        x = r.uniform(ROAD_X0 + 60, W - 40)
        t_, b_ = road_edges(np.array([x], F))
        pebbles(Nn, x - 3, x + 3, (t_[0] + 8, b_[0] - 4), 1, seed=int(r.integers(1e6)), col=NW['sand_dk'], dk=NW['basalt'], rmin=2.5, rmax=5)
    save_plate('shore_near', Nn, variants=('night', 'lit'), gain=0.62, keep=0.18)

# ═════════════════════════ 覆盖干路的海水 ═════════════════════════
if 'cover' in which:
    C = Canvas(W, H)
    x0, x1 = 1380, W
    yy0, yy1 = 770, 905
    xs = np.arange(x0, x1, dtype=F)
    ytop = 806 + 8 * np.sin(xs / 70.0) + 6 * np.sin(xs / 23.0 + 1) + 5 * np.sin(xs / 190.0 + 2)
    ybot = 878 + 7 * np.sin(xs / 83.0 + 1) + 5 * np.sin(xs / 29.0) + 5 * np.sin(xs / 150.0)
    Y = np.arange(yy0, yy1, dtype=F)[:, None]
    m = smoothstep(ytop[None, :] - 16, ytop[None, :] + 8, Y) * (1 - smoothstep(ybot[None, :] - 6, ybot[None, :] + 14, Y))
    m = m * smoothstep(1370, 1448, xs)[None, :]
    with Sub(C, mask=m, bbox=(x0, yy0, x1, yy1)) as T:
        fill_region(T, x0, yy0, x1, yy1, hexc('#6a8190'), hexc('#34485a'), seed=191, mott=0.16, gamma=0.9)
        sea_rows(T, x0, x1, yy0 + 24, yy1 - 24, 192, rows=7, p=1.0, hi=hexc('#b5c5ce'), lo=hexc('#17222d'), foam_k=0.9, len0=120, len1=360, dens=1.2, w1=5.5, hook=1.6)
        river_flow(T, x0, yy0 + 20, x1, yy1 - 20, 193, n=90, len0=100, len1=360, w1=4, foam_k=0.8, hi=hexc('#b5c5ce'), lo=hexc('#1d2b38'))
        r = np.random.default_rng(194)
        # 翻起的浪头：沿着带子的上沿和下沿各一条白浪，中间几团泡沫
        for i in range(0, int(x1 - x0), 170):
            x = x0 + i + r.uniform(-20, 20)
            whitecap(T, x, 811 + 6 * math.sin(x / 70.0) + r.normal(0, 3), r.uniform(150, 230), h=11, seed=700 + i, op=0.95, w=3.4)
            whitecap(T, x + 70, 874 + 5 * math.sin(x / 83.0) + r.normal(0, 3), r.uniform(150, 230), h=10, seed=900 + i, op=0.9, w=3.0)
        for i in range(0, int(x1 - x0), 260):
            x = x0 + i + r.uniform(-20, 40)
            whitecap(T, x, 840 + r.normal(0, 6), r.uniform(120, 220), h=9, seed=1100 + i, op=0.85, w=2.6)
        foam_dots(T, x0, x1, 800, 885, 380, 195, op=0.8)
    # 带子边缘的浪沫线（在蒙版之外也有一点飞沫）
    for edge, off in ((ytop, -6), (ybot, 8)):
        pts = [(float(x), float(y) + off) for x, y in zip(xs[::22], edge[::22])]
        pts = [p for p in pts if p[0] > 1450]
        foam_line(C, pts, w=3.4, seed=196 + off, op=0.8)
    save_plate('shore_water_cover', C, variants=('night', 'lit'), gain=0.62, keep=0.18)
