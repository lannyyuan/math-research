"""雪山小屋（S4）：2900×1080，far / mid / near + near_clear（门前的雪铲开了）。
锚点：地面线 y=832；小屋 x≈1800（墙 x 1500~2100）；门 x≈1880、宽 140、高 350（y 482~832）；
默认 near：门前的雪堆得很深，把门埋了一半；老梅 x≈1150（高 520，只有一朵小白花在 (1200,560)）；雪地上只有兔子的小脚印。
near_clear：门前铲出一条深色小路（从门 x≈1880 向右到 x=2900，y 770~920，宽≈150），雪堆在路两边。"""
from cn_land import *
import sys
W, H = 2900, 1080
which = sys.argv[1:] or ['far', 'mid', 'near', 'near_clear']
XS = np.arange(W)

HUT_X, DOOR_X = 1800, 1880
FLOWER = (1200, 560)


# ───────── 远：天 + 银白的雪山
if 'far' in which:
    S = sky(W, H, hexc('#76879a'), hexc('#a4b2be'), hexc('#d6dad4'), seed=81, horizon=0.8, cloud=0.5, scale=460)
    r1 = ridge_y(W, 650, 330, 91, rough=0.5, scale=800)
    mountain2(S, r1, 760, N['far3'], N['far1'], seed=51, tex=0.55, tex_op=0.26, haze=0.25, shade=0.6, gully=0.7, snow=N['snow'], snow_from=0.36)
    mist(S, 0, W, 650, 80, seed=52, op=0.75)
    r2 = ridge_y(W, 740, 220, 92, rough=0.55, scale=520)
    mountain2(S, r2, 820, N['far2'], N['mid1'], seed=53, tex=0.8, tex_op=0.3, haze=0.2, shade=0.65, gully=0.7, snow=N['snow'], snow_from=0.2)
    mist(S, 0, W, 770, 70, seed=54, op=0.7)
    save_plate2('snow_hut_far', S, variants=('night', 'lit'), gain=0.62, keep=0.14)

# ───────── 中：雪坡上的松林
if 'mid' in which:
    M = Canvas(W, H)
    rr = ridge_y(W, 790, 100, 93, rough=0.5, scale=420)
    mountain2(M, rr, 900, N['far2'], N['mid1'], seed=55, tex=0.8, tex_op=0.3, shade=0.6, snow=N['snow'], snow_from=0.55)
    rng = np.random.default_rng(15)
    for i, x in enumerate(grove(rng, 46, 20, W - 20, clusters=9, spread=110)):
        yb = float(rr[int(x)]) + 14 + (i % 4) * 14
        conifer_dab(M, x, yb, 70 + (i * 37) % 70, seed=800 + i, col=N['pine'], dark=N['pine_dk'], op=0.85, frost_k=0.9)
    mist(M, 0, W, 805, 50, seed=56, op=0.55)
    for i, x in enumerate(grove(rng, 20, 40, W - 40, clusters=7, spread=90)):
        if 1450 < x < 2150 or 900 < x < 1450:      # 小屋和老梅的背后别画得太满
            continue
        yb = 836 + (i % 4) * 5
        pine_ink(M, x, yb, 200 + (i * 53) % 190, seed=350 + i, col=N['pine'], dark=N['pine_dk'], lean=((i % 5) - 2) * 0.02, frost_k=1.0)
    mist(M, 0, W, 846, 50, seed=57, op=0.65)
    save_plate2('snow_hut_mid', M, variants=('night', 'lit'), gain=0.6, keep=0.15)


def draw_near(clear):
    Nn = Canvas(W, H)
    gy = 828 + 6 * np.sin(XS / 300.0).astype(np.float32) + 3 * np.sin(XS / 83.0).astype(np.float32)
    snow_field(Nn, gy, 1080, seed=61, tex=1.0)
    # 雪地的起伏：低低的雪垄（蓝灰的背阴 + 上沿的墨线）
    for k, (xa, xb, yb_, hh) in enumerate([(120, 700, 880, 22), (900, 1500, 905, 26), (1500, 2100, 925, 24), (2000, 2700, 890, 22), (300, 1000, 960, 28), (1100, 1900, 990, 24), (1800, 2600, 1010, 30), (-50, 600, 1040, 26)]):
        tp = lumpy_top(xa, xb, yb_, hh, seed=900 + k, lumps=2, hmin=0.5)
        snow_heap(Nn, tp, yb_, seed=950 + k, shade=0.4, lean=1, line=0.35, hatch_k=0.8)
    # 远处的雪垄（起伏）
    drift(Nn, 40, 520, 850, 40, seed=1, peak=0.4, line=0.3)
    drift(Nn, 520, 1000, 856, 34, seed=2, peak=0.55, line=0.3)
    drift(Nn, 2250, 2700, 852, 46, seed=3, peak=0.4, line=0.3)
    # 兔子的脚印（从左边来，绕过梅树）
    tracks(Nn, 120, 1000, 846, seed=3, step=46)
    tracks(Nn, 330, 760, 884, seed=8, step=40, op=0.45, size=0.8)
    # 老梅 x≈1150
    plum_ink(Nn, 1150, 820, 520, seed=5, flower=None, roots=False)
    brush(Nn, [(1172, 616), (1190, 590), (1204, 566)], w0=3.2, w1=1.2, color=N['wood_dk'] * 0.55, op=0.95, seed=77, wob=0.6, taper=0.2)
    flower_small(Nn, FLOWER[0], FLOWER[1], 11, seed=21)
    # 梅树脚下的雪窝
    drift(Nn, 1040, 1280, 846, 34, seed=4, peak=0.5, line=0.3)
    # 小屋
    roof_y = 832 - 392
    snow_hut(Nn, HUT_X, 832, 600, 392, 200, DOOR_X, seed=9)
    snow_roof(Nn, HUT_X, roof_y, 420, 205, seed=13, snow=1.0)
    # 墙根的雪（门左一小段）
    drift(Nn, 1420, 1790, 842, 70, seed=6, peak=0.6, line=0.35)
    if not clear:
        # 门前的雪堆：很深，把门埋了一半（顶 y≈650）
        # 一道被风吹成的雪垄：贴着门的一侧高（顶 y≈655），向右缓缓拖长，上沿有小起伏
        top_pts = [(1690, 806), (1730, 770), (1770, 735), (1800, 700), (1830, 676), (1862, 660), (1900, 654), (1940, 662), (1985, 684), (2030, 716), (2080, 750), (2140, 782), (2210, 806), (2300, 824), (2400, 836)]
        top_pts = [(x, y + 5 * math.sin(x / 23.0)) for x, y in top_pts]
        snow_heap(Nn, top_pts, 846, seed=7, shade=0.6, lean=1, line=0.5)
        # 紧贴门的一个小雪包（压在垄上）
        snow_heap(Nn, [(1800, 740), (1830, 712), (1866, 700), (1900, 706), (1932, 724), (1962, 752)], 790, seed=17, shade=0.35, lean=1, line=0.25, bottom=800, op=0.9)
    else:
        # 门前铲出的小路：深色，从门向右直到右边缘；雪堆在两侧
        yt = 770 + 8 * np.sin(XS / 140.0 + 1).astype(np.float32) + 4 * np.sin(XS / 47.0).astype(np.float32)
        yb = 917 + 8 * np.sin(XS / 170.0).astype(np.float32) + 4 * np.sin(XS / 53.0).astype(np.float32)
        ytc, ybc = yt.copy(), yb.copy()
        # 路在门口收拢：从门左边缘 x=1810 起；之前不画
        ramp = np.clip((XS - 1800) / 130.0, 0, 1).astype(np.float32); ramp = ramp * ramp * (3 - 2 * ramp)
        ytc = yt + (1 - ramp) * 160
        ybc = yb - (1 - ramp) * 200 + 0
        ybc = np.maximum(ybc, ytc + 4)
        path_ribbon(Nn, ytc, ybc, x0=1780, seed=31, top_col=N['earth_dk'] * 0.75, bot_col=N['earth_dk'] * 0.9, ruts=False, pebbles=False, edge_op=0.5)
        # 铲痕
        rng2 = np.random.default_rng(3)
        for k in range(14):
            xx = rng2.uniform(1900, 2850)
            i = int(xx)
            yy = ytc[i] + (ybc[i] - ytc[i]) * rng2.uniform(0.15, 0.85)
            brush(Nn, [(xx, yy), (xx + rng2.uniform(60, 180), yy + rng2.normal(0, 3))], w0=2.2, color=N['earth'], op=0.4, seed=int(rng2.integers(1e6)), taper=0.4, wob=0.8, dry=0.4)
        # 路里的碎雪
        for k in range(26):
            xx = rng2.uniform(1860, 2880)
            i = int(xx)
            yy = ytc[i] + (ybc[i] - ytc[i]) * rng2.uniform(0.1, 0.9)
            s_ = rng2.uniform(4, 11)
            wash(Nn, [(xx - s_, yy), (xx - s_ * 0.2, yy - s_ * 0.5), (xx + s_ * 0.9, yy - s_ * 0.3), (xx + s_, yy + s_ * 0.2), (xx - s_ * 0.3, yy + s_ * 0.4)], N['snow'], op=0.85, wob=0.3, seed=int(rng2.integers(1e6)), smooth=1, tex_k=0.05, rim=0.2, rim_w=1.5)
        # 门槛：横在门口的一根厚木
        slab(Nn, DOOR_X, 852, 190, 30, top_h=12, seed=44, col=N['stone'], light=N['stone_lt'])
        # 两侧堆起的雪（铲上去的）：后面一道（y≈775 以上）、前面一道（y≈920 以下），起伏不一
        for (xa, xb, kind) in ((1950, W + 40, 'back'), (1790, W + 40, 'front')):
            x = xa
            k = 0
            while x < xb:
                ww = rng2.uniform(240, 420)
                x1_ = min(x + ww, xb)
                ymid = float((ytc if kind == 'back' else ybc)[min(int((x + x1_) / 2), W - 1)])
                yb_ = ymid + (8 if kind == 'back' else 26)
                hh = rng2.uniform(40, 84) if kind == 'back' else rng2.uniform(34, 70)
                tp = lumpy_top(x, x1_, yb_, hh, seed=400 + k + (50 if kind == 'front' else 0), lumps=int(rng2.integers(1, 3)))
                snow_heap(Nn, tp, yb_, seed=500 + k, shade=0.55, lean=1, line=0.4)
                x += ww * rng2.uniform(0.62, 0.85)
                k += 1
        # 门左的雪（铲到墙边）
        snow_heap(Nn, lumpy_top(1620, 1840, 846, 96, seed=8, lumps=2), 846, seed=8, shade=0.55, lean=1, line=0.4)
    dry_grass(Nn, 0, 1000, 846, 12, seed=71, op=0.7, frost_k=1.0, hmin=18, hmax=44)
    dry_grass(Nn, 2250, W, 850, 10, seed=72, op=0.7, frost_k=1.0, hmin=18, hmax=44)
    snow_dust(Nn, 0, W, 560, 830, 40, seed=5, op=0.25)
    return Nn


if 'near' in which:
    save_plate2('snow_hut_near', draw_near(False), variants=('night', 'lit'), gain=0.8, keep=0.18)
if 'near_clear' in which:
    save_plate2('snow_hut_near_clear', draw_near(True), variants=('night', 'lit'), gain=0.8, keep=0.18)
