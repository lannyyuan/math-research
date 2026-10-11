"""山脚的小村：远（天 + 雪山）/ 中（山、河、田、小村）/ 近（地面、大茅屋、老树 + 怪石）。2900×1080。变体：夜色 / 光照 / 白天 / 晨光。"""
from ccommon import *
import sys
W, H = 2900, 1080
which = sys.argv[1:] or ['far', 'mid', 'near']

# ───────── 远：天 + 雪山 + 灯盘的位置留空（灯由影片里叠上去）
if 'far' in which:
    S = sky(W, H, hexc('#8fa0ae'), hexc('#c0cbd0'), hexc('#ece6d6'), seed=31, horizon=0.78, cloud=0.5, scale=460)
    r1 = ridge_y(W, 700, 400, 41, rough=0.5, scale=700)
    mountain(S, r1, 760, N['far3'], N['far1'], seed=11, tex=0.6, tex_op=0.26, snow=N['snow'], snow_from=0.26, haze=0.3)
    mist(S, 0, W, 690, 80, seed=12, op=0.7)
    r2 = ridge_y(W, 770, 250, 52, rough=0.55, scale=480)
    mountain(S, r2, 840, N['far2'], N['mid1'], seed=12, tex=0.8, tex_op=0.28, haze=0.22)
    mist(S, 0, W, 780, 70, seed=13, op=0.6)
    save_plate('village_far', S, variants=('night', 'lit', 'day', 'dawn'), gain=0.6, keep=0.15)

# ───────── 中：近山 + 河 + 田 + 小村
if 'mid' in which:
    M = Canvas(W, H)
    r3 = ridge_y(W, 790, 130, 61, rough=0.5, scale=360)
    mountain(M, r3, 900, N['mid2'], N['mid3'], seed=21, tex=1.0, tex_op=0.34)
    for i in range(26):
        x = 80 + i * 112 + (i * 61) % 70
        yb = r3[int(min(x, W - 1))] + 26 + (i % 3) * 12
        pine(M, x, yb, 70 + (i * 41) % 60, seed=100 + i, col=N['pine'], dark=N['pine_dk'], lean=((i % 5) - 2) * 0.02)
    mist(M, 0, W, 850, 60, seed=22, op=0.55)
    # 河（一条带子，从右上蜿蜒到左下）
    ys = np.full(W, 872.0, np.float32)
    water(M, 862, 925, seed=5, strokes=220)
    # 田：河和山之间，一块块梯田（横向弧线）
    ground_strip(M, np.full(W, 925.0, np.float32), 1000, N['earth_lt'], N['earth'], seed=3, tex=0.6)
    for k in range(7):
        y = 930 + k * 11
        pts = [(x, y + 4 * math.sin(x / 130 + k)) for x in range(0, W, 60)]
        brush(M, pts, w0=2.0, color=N['earth_dk'], op=0.28, seed=300 + k, wob=1.0, taper=0.05, dry=0.3)
    # 小村：几户茅屋（远）
    for i, (x, y, w) in enumerate([(1060, 905, 120), (1220, 915, 150), (1400, 902, 110), (1540, 912, 140), (1710, 903, 105)]):
        thatch_hut(M, x, y, w, w * 0.72, seed=40 + i, wall=N['stone_lt'], snow=0.0, door=True, window=(i % 2 == 0))
    for i, x in enumerate([990, 1330, 1620, 1800]):
        willow(M, x, 915 + (i % 2) * 8, 120 + 30 * (i % 3), seed=70 + i)
    save_plate('village_mid', M, variants=('night', 'lit', 'day', 'dawn'), gain=0.55, keep=0.18)

# ───────── 近：地面 + 大茅屋 + 老树 + 怪石 + 前景
if 'near' in which:
    Nn = Canvas(W, H)
    gy = 820 + 10 * np.sin(np.arange(W) / 240.0).astype(np.float32) + 6 * np.sin(np.arange(W) / 83.0).astype(np.float32)
    ground_strip(Nn, gy, 1080, N['earth_lt'], N['earth'], seed=7, tex=1.0)
    # 路：一条浅色的小路，从左下蜿蜒到右
    # 大茅屋（奶奶家）x≈560
    thatch_hut(Nn, 640, 828, 640, 640, seed=2, wall=N['stone'], snow=0.0, door=True, window=True, roof_rise=0.3)
    # 屋边的几棵树、篱笆
    bamboo(Nn, 250, 832, 300, seed=8, n=4)
    for i in range(9):
        x = 1000 + i * 70
        brush(Nn, [(x, 842), (x + 3, 800), (x + 1, 770)], w0=4, color=N['wood_dk'], op=0.8, seed=500 + i, taper=0.2)
    brush(Nn, [(1000, 806), (1560, 806)], w0=3, color=N['wood_dk'], op=0.7, seed=520, taper=0.1, dry=0.2)
    brush(Nn, [(1000, 782), (1560, 782)], w0=3, color=N['wood_dk'], op=0.7, seed=521, taper=0.1, dry=0.2)
    # 老树 x≈2060，树脚 y≈830
    old_tree(Nn, 2160, 838, 700, seed=14, col=N['wood_dk'] * 0.55, depth=6, spread=0.82, trunk_w=54, snow=0.5)
    # 怪石：上头尖，下头圆，有道弯口（像一只蹲着的石猴的头）
    rock(Nn, 1960, 848, 190, 300, seed=17, snow=0.25)
    brush(Nn, [(1900, 730), (1935, 745), (1980, 741), (2010, 720)], w0=3.4, color=INK, op=0.9, seed=31, wob=0.6, taper=0.2)   # 弯口
    for i, (x, w, h) in enumerate([(2400, 120, 70), (2560, 90, 50), (2760, 160, 90), (120, 140, 80)]):
        rock(Nn, x, 850, w, h, seed=60 + i, snow=0.2)
    grass_tufts(Nn, 0, W, gy, 90, seed=9, op=0.8)
    save_plate('village_near', Nn, variants=('night', 'lit', 'day', 'dawn'), gain=0.55, keep=0.2)


# ───────── 近（空旷版）：没有大屋和老树的前景，给“远眺山谷”的镜头用
if 'near2' in which:
    V = Canvas(W, H)
    gy = 860 + 10 * np.sin(np.arange(W) / 240.0).astype(np.float32) + 6 * np.sin(np.arange(W) / 83.0).astype(np.float32)
    ground_strip(V, gy, 1080, N['earth_lt'], N['earth'], seed=17, tex=1.0)
    for i, (x, w, h) in enumerate([(300, 150, 80), (900, 110, 60), (2300, 170, 90), (2650, 120, 70)]):
        rock(V, x, 880, w, h, seed=80 + i, snow=0.2)
    bamboo(V, 120, 880, 280, seed=18, n=4)
    grass_tufts(V, 0, W, gy, 80, seed=19, op=0.8)
    save_plate('village_near2', V, variants=('night', 'lit', 'day', 'dawn'), gain=0.55, keep=0.2)
