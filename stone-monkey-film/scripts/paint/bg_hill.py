"""山边小路（S4 开头：帮老奶奶捆柴）：夜里的山坡小路。2900×1080，far / mid / near。
锚点：地面线 y=832；x 1380~1700 空地；平的大石 x≈1650（宽 260，顶 y≈760）；左右 x≈150 / x≈2700 近景松树框住；路两侧有水洼。"""
from cn_land import *
import sys
W, H = 2900, 1080
which = sys.argv[1:] or ['far', 'mid', 'near']
XS = np.arange(W)

# ───────── 远：天 + 层层的山和雾
if 'far' in which:
    S = sky(W, H, hexc('#7a8b9a'), hexc('#a8b4be'), hexc('#d8d9d0'), seed=71, horizon=0.8, cloud=0.55, scale=470)
    r1 = ridge_y(W, 660, 330, 81, rough=0.5, scale=760)
    mountain2(S, r1, 760, N['far3'], N['far1'], seed=31, tex=0.6, tex_op=0.26, haze=0.3, shade=0.7, gully=0.8)
    mist(S, 0, W, 650, 90, seed=32, op=0.8)
    r2 = ridge_y(W, 740, 240, 82, rough=0.55, scale=520)
    mountain2(S, r2, 820, N['far2'], N['mid1'], seed=33, tex=0.8, tex_op=0.3, haze=0.18, shade=0.7, gully=0.8)
    for i in range(30):    # 远山脊上细小的树影
        x = 40 + i * 98 + (i * 37) % 60
        yb = float(r2[min(x, W - 1)]) + 10
        pine_ink(S, x, yb, 34 + (i * 29) % 26, seed=200 + i, col=N['mid2'], dark=N['mid3'], trunk_col=N['mid3'], nb=3, op=0.8)
    mist(S, 0, W, 770, 80, seed=34, op=0.75)
    r3 = ridge_y(W, 810, 160, 83, rough=0.55, scale=380)
    mountain2(S, r3, 890, N['mid1'], N['mid2'], seed=35, tex=1.0, tex_op=0.32, shade=0.6)
    mist(S, 0, W, 840, 60, seed=36, op=0.55)
    save_plate2('hill_far', S, variants=('night', 'lit'), gain=0.6, keep=0.15)

# ───────── 中：松林 + 灌木 + 山坡上的小径
if 'mid' in which:
    M = Canvas(W, H)
    rr = ridge_y(W, 790, 110, 91, rough=0.5, scale=420)
    mountain2(M, rr, 900, N['mid2'], N['mid3'], seed=41, tex=0.9, tex_op=0.32, shade=0.6)
    # 山坡上蜿蜒的小径（浅色细带）
    pts = [(120, 880), (420, 846), (760, 826), (1000, 838), (1260, 818), (1500, 806)]
    brush(M, pts, w0=26, w1=8, color=N['earth_lt'], op=0.5, seed=3, wob=3, taper=0.2, dry=0.2)
    rng = np.random.default_rng(5)
    # 后排：成片的小针叶树（暗影）
    for i, x in enumerate(grove(rng, 46, 20, W - 20, clusters=10, spread=110)):
        yb = float(rr[int(x)]) + 6 + (i % 4) * 8
        conifer_dab(M, x, yb, 70 + (i * 37) % 70, seed=700 + i, col=N['pine'], dark=N['pine_dk'], op=0.85)
    mist(M, 0, W, 800, 50, seed=43, op=0.55)
    # 前排：有姿态的松（成丛）
    for i, x in enumerate(grove(rng, 24, 40, W - 40, clusters=8, spread=90)):
        yb = float(rr[int(x)]) + 26 + (i % 3) * 14
        pine_ink(M, x, yb, 170 + (i * 53) % 150, seed=300 + i, col=N['pine'], dark=N['pine_dk'], lean=((i % 5) - 2) * 0.02)
    for i in range(16):
        x = 60 + i * 180 + (i * 41) % 90
        bush(M, x, float(rr[min(x, W - 1)]) + 50, 90 + (i * 31) % 70, 40 + (i * 13) % 30, seed=400 + i, col=N['pine'], dark=N['pine_dk'], op=0.9)
    mist(M, 0, W, 846, 50, seed=42, op=0.6)
    save_plate2('hill_mid', M, variants=('night', 'lit'), gain=0.55, keep=0.18)

# ───────── 近：路 + 石 + 水洼 + 框住的松
if 'near' in which:
    Nn = Canvas(W, H)
    gy = 826 + 7 * np.sin(XS / 260.0).astype(np.float32) + 4 * np.sin(XS / 71.0).astype(np.float32)
    # 路肩 / 山坡的泥土
    ground_strip(Nn, gy, 1080, N['earth'], N['earth_dk'], seed=7, tex=1.0)
    grass_tufts(Nn, 0, W, gy + 50, 90, seed=8, op=0.7)
    # 路
    yt = gy + 5 + 6 * np.sin(XS / 190.0 + 1).astype(np.float32)
    yb = 892 + 24 * np.sin(XS / 330.0 + 0.5).astype(np.float32) + 8 * np.sin(XS / 77.0).astype(np.float32)
    path_ribbon(Nn, yt, yb, seed=11, top_col=mix(N['earth_lt'], N['paper'], 0.3), bot_col=N['earth_lt'])
    # 水洼：路两侧细细的几处
    for i, (x, y, w, h) in enumerate([(380, 842, 150, 15), (760, 905, 190, 18), (1010, 849, 130, 12), (2050, 846, 170, 14), (2310, 910, 210, 18), (2560, 850, 140, 13)]):
        puddle(Nn, x, y, w, h, seed=60 + i)
    # 路边石头（x 1380~1700 空着，只放那块大石）
    for i, (x, w, h) in enumerate([(210, 150, 80), (560, 90, 46), (880, 120, 62), (1180, 70, 38), (2000, 100, 54), (2230, 160, 84), (2500, 80, 44), (2820, 150, 90)]):
        rock(Nn, x, 872 + (i % 3) * 8, w, h, seed=80 + i)
    slab(Nn, 1650, 838, 260, 80, seed=21)
    # 框住的松
    pine_ink(Nn, 150, 868, 860, seed=31, lean=0.07, flat=0.5)
    pine_ink(Nn, 2700, 872, 800, seed=32, lean=-0.06, flat=0.5)
    dry_grass(Nn, 0, W, gy + 40, 60, seed=14, op=0.8, hmin=20, hmax=60)
    for x0, x1 in ((0, 700), (2200, W)):
        grass_blades(Nn, x0, x1, 930, 1050, 90, seed=int(x0) + 3, col=N['earth_dk'], op=0.7, hmin=20, hmax=60)
    save_plate2('hill_near', Nn, variants=('night', 'lit'), gain=0.68, keep=0.2)
