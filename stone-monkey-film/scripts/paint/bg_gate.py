"""主城的城门（S5）：青砖城墙 + 两层城门楼 + 关着的铜钉木门，墙前路面、右边街铺、左边树和拴马桩。2900×1080，far/mid/near。
用法：python3 bg_gate.py [far] [mid] [near]"""
from cn_arch import *
import sys
W, H = 2900, 1080
which = sys.argv[1:] or ['far', 'mid', 'near']
GX = 1500          # 城门洞中心
Y_TOP, Y_WALK, Y_GND = 400, 430, 832

# ───────── 远：天空 + 灰蒙蒙的远山
if 'far' in which:
    S = sky(W, H, hexc('#8d9eac'), hexc('#bcc8ce'), hexc('#e4e2d6'), seed=51, horizon=0.62, cloud=0.55, scale=470)
    r1 = ridge_y(W, 520, 330, 53, rough=0.5, scale=760)
    mountain(S, r1, 640, N['far3'], N['far1'], seed=14, tex=0.55, tex_op=0.24, haze=0.32)
    mist(S, 0, W, 470, 70, seed=15, op=0.65)
    r2 = ridge_y(W, 600, 220, 54, rough=0.55, scale=520)
    mountain(S, r2, 700, N['far2'], N['mid1'], seed=16, tex=0.7, tex_op=0.26, haze=0.2)
    mist(S, 0, W, 540, 60, seed=17, op=0.6)
    save2('gate_far', S, variants=('night', 'lit'), gain=0.6, keep=0.15)

# ───────── 中：城墙后面的城里——一片片灰瓦屋顶、鼓楼、树、远处的塔尖（隔着雾）
if 'mid' in which:
    M = Canvas(W, H)
    rng = np.random.default_rng(77)
    def town_roof(x, ye, w, h, seed, up=0.03):
        # 屋顶下的山墙（灰白）+ 屋顶
        rwash(M, x - w * 0.36, ye, x + w * 0.36, ye + 140, A['brick_lt'] * 0.96, op=1.0, wob=1.0, seed=seed, tex_k=0.15, rim=0.1)
        eave_roof(M, x, ye, w, h, seed=seed + 1, ridge_ratio=0.74, up=up, bells=False, orn=(w > 200), gap=10, under=0.03, under_span=w * 0.36, sag_p=1.8)
    # 后排（更远、更小、更淡），再前排
    xs = []
    x = 20
    while x < W:
        w = rng.uniform(120, 230)
        xs.append((x + w / 2, w))
        x += w * rng.uniform(0.7, 1.0)
    for i, (cx, w) in enumerate(xs):
        town_roof(cx, 360 + rng.uniform(-24, 30), w * 0.8, rng.uniform(30, 52), 300 + i, up=0.025)
    M.rgb = mix(M.rgb, N['mist'][None, None, :], (0.35 * M.a)[..., None]).astype(F)
    # 鼓楼（左）：两层、小
    # 远处的塔（x≈2330）：九层不必数得清，剪影
    mist(M, 0, W, 420, 50, seed=22, op=0.7, color=N['mist'])
    # 前排的屋顶（更大、更清楚），被城墙挡住下半
    xs2 = []
    x = -40
    while x < W:
        w = rng.uniform(210, 340)
        xs2.append((x + w / 2, w))
        x += w * rng.uniform(0.75, 1.0)
    for i, (cx, w) in enumerate(xs2):
        if abs(cx - GX) < 360:
            continue
        town_roof(cx, 408 + rng.uniform(-14, 18), w * 0.82, rng.uniform(46, 70), 400 + i, up=0.03)
    for i, x in enumerate([180, 900, 2800]):
        pine(M, x, 440, rng.uniform(120, 190), seed=500 + i, col=N['pine'], dark=N['pine_dk'])
    M.rgb = mix(M.rgb, N['mist'][None, None, :], (0.12 * M.a)[..., None]).astype(F)
    mist(M, 0, W, 440, 40, seed=23, op=0.5, color=N['mist'])
    save2('gate_mid', M, variants=('night', 'lit'), gain=0.58, keep=0.18)

# ───────── 近：城墙、城门楼、城门、路面、街铺、树、拴马桩
if 'near' in which:
    Nn = Canvas(W, H)
    lm = LightMap(W, H)
    gy = (Y_GND - 2 + 6 * np.sin(np.arange(W) / 260.0) + 3 * np.sin(np.arange(W) / 71.0)).astype(F)
    ground_strip(Nn, gy, 1080, N['earth_lt'], N['earth'], seed=7, tex=0.9)
    city_wall(Nn, 0, W, Y_TOP, Y_WALK, Y_GND, seed=5)
    gate_opening(Nn, GX, Y_GND, 260, 330, seed=6, lm=lm)
    gate_tower(Nn, GX, Y_WALK, seed=7, lm=lm)
    for k, sx in enumerate((-1, 1)):
        lantern(Nn, GX + sx * 188, 566, 17, seed=3 + k, lm=lm)
    for i, x in enumerate([250, 700, 1060, 1960, 2330, 2720]):
        banner(Nn, x, 232, 200, 118, 52, seed=20 + i, phase=i * 0.9, wave=11)
    # 墙前的路面：石板路（中间一条，向两边渐渐变成土路）
    rr = np.random.default_rng(9)
    road = [(1080, Y_GND - 3), (1920, Y_GND - 3), (2060, 1080), (940, 1080)]
    wash(Nn, road, N['stone_lt'], op=0.62, wob=3.0, seed=2, smooth=0, tex_k=0.2, rim=0.1)
    for k in range(9):
        t = (k / 9.0) ** 1.35
        yy = Y_GND + 2 + t * 240
        xl = 1080 - 140 * (yy - Y_GND) / 250
        xr = 1920 + 140 * (yy - Y_GND) / 250
        brush(Nn, [(xl, yy), ((xl + xr) / 2, yy + rr.normal(0, 1)), (xr, yy)], w0=2.0, color=INK, op=0.3, seed=800 + k, wob=0.8, taper=0.1, dry=0.45)
        nsl = 8 + k
        for j in range(nsl):
            xa = xl + (xr - xl) * (j + 0.5 * (k % 2)) / nsl
            yb = yy + 6 + 30 * ((k + 1) / 9.0) ** 1.3
            brush(Nn, [(xa, yy), (xa + (xa - 1500) * 0.03, yb)], w0=1.6, color=INK, op=0.26, seed=900 + k * 20 + j, wob=0.6, taper=0.2, dry=0.4)
    # 左边：一棵老树、拴马桩、石槽
    old_tree(Nn, 430, 842, 540, seed=33, col=N['wood_dk'] * 0.6, depth=5, spread=0.86, leaf=0.55, trunk_w=44)
    hitch_post(Nn, 700, 846, h=230, seed=3)
    rwash(Nn, 780, 818, 930, 846, A['slab'], op=1.0, wob=0.8, seed=11, tex_k=0.16, rim=0.16)
    rwash(Nn, 790, 822, 920, 832, A['slab_dk'], op=0.8, wob=0.6, seed=12, tex_k=0.1, rim=0.0)
    boxline(Nn, 780, 818, 930, 846, 2.6, 0.75, 13, 0.25)
    # 右边：街铺、板车、米摊
    shop_front(Nn, 2140, Y_GND + 2, 300, 280, seed=40, lm=lm, sign=True, cloth=True, rise=66)
    shop_front(Nn, 2460, Y_GND + 2, 270, 270, seed=41, lm=lm, sign=False, cloth=True, lantern_lit=True, rise=62)
    cart(Nn, 1930, Y_GND + 20, seed=50, face=1, lm=lm, s=1.35)
    rice_stall(Nn, 2735, Y_GND + 6, seed=60, lm=lm)
    grass_tufts(Nn, 0, W, gy, 120, seed=9, op=0.8)
    for i, (x, w, h) in enumerate([(120, 120, 60), (1000, 90, 46), (1990, 100, 52), (2610, 90, 44)]):
        rock(Nn, x, 852, w, h, seed=70 + i)
    save2('gate_near', Nn, variants=('night', 'lit'), gain=0.55, keep=0.2, lights=[(lm, WINDOW_LIGHT)])
