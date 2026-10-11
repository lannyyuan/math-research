"""霜林（S4）：2900×1080，far / mid / near。
锚点：地面线 y=832（小径从左穿到右）；近景两侧粗树干 x 90~230、x 2650~2800；蛛网在 x≈1900、y 560~700（网心 (1900,630)，半径≈72，网上一串露珠）。"""
from cn_land import *
import sys
W, H = 2900, 1080
which = sys.argv[1:] or ['far', 'mid', 'near']
XS = np.arange(W)

# ───────── 远：深色的天 + 一层层林子的暗影，浓雾
if 'far' in which:
    S = sky(W, H, hexc('#6a7a8a'), hexc('#8d9baa'), hexc('#b9c0c4'), seed=111, horizon=0.8, cloud=0.35, scale=420)
    r1 = ridge_y(W, 700, 150, 112, rough=0.5, scale=700)
    mountain2(S, r1, 800, N['far3'], N['far2'], seed=61, tex=0.4, tex_op=0.22, haze=0.35, shade=0.5)
    rng = np.random.default_rng(21)
    # 后排：淡淡的、成片的树干和树冠（离得远，被雾吃掉一半）
    for i, x in enumerate(grove(rng, 60, 0, W, clusters=14, spread=90)):
        h = 190 + (i * 59) % 190
        kind = i % 4
        yb = 800 + (i % 3) * 8
        if kind == 0:
            birch_ink(S, x, yb, h, seed=900 + i, frost_k=0.6, op=0.8)
        elif kind == 1:
            conifer_dab(S, x, yb, h, seed=900 + i, col=N['mid1'], dark=N['mid3'], op=0.85, frost_k=0.6)
        elif kind == 2:
            pine_ink(S, x, yb, h * 0.8, seed=900 + i, col=N['mid1'], dark=N['mid3'], trunk_col=N['mid3'], frost_k=0.6, op=0.85)
        else:
            conifer_dab(S, x, yb, h * 1.1, seed=900 + i, col=N['mid1'], dark=N['mid3'], op=0.85, frost_k=0.6)
    mist(S, 0, W, 660, 110, seed=62, op=0.6)
    mist(S, 0, W, 770, 90, seed=63, op=0.75)
    mist(S, 0, W, 830, 60, seed=64, op=0.7)
    save_plate2('frost_forest_far', S, variants=('night', 'lit'), gain=0.58, keep=0.14)

# ───────── 中：一排高大的松、柏、杉、桦，树干墨黑，枝上挂霜；林间的雾
if 'mid' in which:
    M = Canvas(W, H)
    rng = np.random.default_rng(33)
    x = 40
    i = 0
    row = []
    while x < W - 20:
        row.append(x)
        x += float(rng.uniform(120, 215))
    for i, x in enumerate(row):
        kind = (i * 7 + 2) % 5
        yb = 838 + (i % 3) * 5
        h = float(rng.uniform(430, 700))
        if kind in (0, 3):
            pine_ink(M, x, yb, h * 0.82, seed=1200 + i, col=N['pine'], dark=N['pine_dk'], trunk_col=N['wood_dk'] * 0.4, frost_k=1.0, lean=float(rng.uniform(-0.07, 0.07)), nb=8)
        elif kind == 1:
            fir_ink(M, x, yb, h * 1.05, seed=1200 + i, col=N['pine'], dark=N['pine_dk'], trunk_col=N['wood_dk'] * 0.4, frost_k=1.0, lean=float(rng.uniform(-0.03, 0.03)))
        elif kind == 2:
            birch_ink(M, x, yb, h * 0.95, seed=1200 + i, frost_k=1.0, lean=float(rng.uniform(-0.03, 0.03)))
        else:
            cypress_ink(M, x, yb, h * 0.75, seed=1200 + i, col=N['pine'], dark=N['pine_dk'], trunk_col=N['wood_dk'] * 0.4, frost_k=1.0)
        if i % 3 == 1:
            mist(M, int(x - 260), int(x + 260), 770 + (i % 2) * 40, 70, seed=1250 + i, op=0.45)
    # 林下的灌木、枯枝
    for i in range(22):
        bx = 30 + i * 135 + (i * 37) % 70
        bush(M, bx, 842, 80 + (i * 17) % 60, 46 + (i * 11) % 30, seed=1300 + i, col=N['pine_dk'], dark=N['pine_dk'], bare=(i % 2 == 0), frost_k=1.0, op=0.9)
    mist(M, 0, W, 810, 70, seed=66, op=0.6)
    mist(M, 0, W, 850, 50, seed=67, op=0.7)
    save_plate2('frost_forest_mid', M, variants=('night', 'lit'), gain=0.62, keep=0.15)

# ───────── 近：小径 + 积雪 + 枯草 + 两侧粗树干 + 蛛网
if 'near' in which:
    Nn = Canvas(W, H)
    gy = 828 + 6 * np.sin(XS / 280.0).astype(np.float32) + 3 * np.sin(XS / 77.0).astype(np.float32)
    ground_strip(Nn, gy, 1080, N['earth'], N['earth_dk'], seed=17, tex=1.0, tex_col=INK)
    # 小径：略浅的一条带，上头星星点点的积雪
    yt = gy + 6
    yb = 905 + 20 * np.sin(XS / 330.0 + 0.5).astype(np.float32) + 6 * np.sin(XS / 61.0).astype(np.float32)
    path_ribbon(Nn, yt, yb, seed=18, top_col=N['earth'], bot_col=N['earth_lt'], ruts=True, pebbles=True, edge_op=0.4)
    rng = np.random.default_rng(41)
    for k in range(40):
        cx = float(rng.uniform(100, W - 100))
        cy = float(rng.uniform(836, 940))
        snow_patch(Nn, cx, cy, float(rng.uniform(26, 120)), float(rng.uniform(6, 16)), seed=2000 + k, op=0.95 if k % 3 else 0.75)
    # 路边的石、枯草
    for i, (x, w, h) in enumerate([(380, 110, 54), (860, 80, 40), (1260, 70, 36), (2150, 100, 48), (2420, 120, 60)]):
        rock(Nn, x, 884 + (i % 2) * 10, w, h, seed=3000 + i, snow=0.7)
    dry_grass(Nn, 0, W, gy + 24, 70, seed=19, op=0.85, hmin=26, hmax=80, frost_k=1.0)
    dry_grass(Nn, 0, W, 905, 40, seed=20, op=0.85, hmin=30, hmax=90, frost_k=1.0)
    # 蛛网的支架：一株枯小树（x≈1815）+ 一根枯草秆（x≈1990）+ 一根弯过来的枝
    sp1 = dead_sapling(Nn, 1812, 850, 400, seed=51, lean=0.02, twigs=10)
    sp2 = dead_sapling(Nn, 1995, 850, 330, seed=52, lean=-0.03, twigs=6)
    # 一根斜枝从小树上伸向网的上方
    brush(Nn, [(1822, 520), (1860, 502), (1915, 494), (1960, 506)], w0=3.0, w1=1.0, color=N['wood_dk'] * 0.45, op=0.95, seed=53, taper=0.2, wob=0.8)
    web(Nn, 1900, 630, 72, seed=7, anchors=[(1824, 614), (1914, 496), (1992, 640), (1930, 700)], rays=13, spokes=8)
    brush(Nn, [(1930, 700), (1936, 760), (1933, 830)], w0=1.6, w1=1.0, color=N['paper'], op=0.5, seed=54, taper=0.2, wob=0.4)
    # 近景两侧的粗树干
    tree_trunk(Nn, 160, -40, 868, 140, w_top=118, seed=71, frost_k=1.0, lean=0.01, moss=1.0, snow_side=1)
    tree_trunk(Nn, 2725, -40, 872, 150, w_top=124, seed=72, frost_k=1.0, lean=-0.012, moss=1.0, snow_side=-1)
    # 粗干上伸出的几根枯枝（向画面里，顶端挂霜）
    for (bx, by, sgn, sd) in [(215, 250, 1, 5), (205, 470, 1, 6), (2660, 190, -1, 7), (2670, 400, -1, 8)]:
        pts = [(bx, by), (bx + sgn * 70, by - 26), (bx + sgn * 150, by - 40), (bx + sgn * 230, by - 36)]
        brush(Nn, pts, w0=14, w1=2.0, color=N['wood_dk'] * 0.45, op=0.97, seed=sd, wob=1.2, taper=0.05)
        frost(Nn, [(bx + sgn * q, by - 26 - 14 * (q / 80)) for q in range(30, 220, 24)], op=0.9, size=(2, 4), seed=sd + 3, ln=(5, 12))
        for k2 in range(3):
            q = 80 + k2 * 50
            brush(Nn, [(bx + sgn * q, by - 33), (bx + sgn * (q + 28), by - 33 - 28), (bx + sgn * (q + 40), by - 33 - 38)], w0=3.0, w1=0.8, color=N['wood_dk'] * 0.45, op=0.9, seed=sd * 10 + k2, taper=0.3, wob=0.6)
    save_plate2('frost_forest_near', Nn, variants=('night', 'lit'), gain=0.72, keep=0.18)
