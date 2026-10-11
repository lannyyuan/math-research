"""九层砖塔（S5：爬塔）。1920×3400：far（天空 + 远山 + 城里的屋顶）/ mid（几缕云）/ near（塔 + 台阶 + 石栏 + 地面）。
塔正中 x=960，塔基（地面）y=3230，严格九层，逐层收小，塔刹在 y≈330~560，顶上是带栏杆的平台 y≈600。
用法：python3 bg_pagoda.py [far] [mid] [near]"""
from cn_arch import *
import sys
W, H = 1920, 3400
which = sys.argv[1:] or ['far', 'mid', 'near']
CX, GROUND = 960, 3230

if 'far' in which:
    S = sky(W, H, hexc('#75869a'), hexc('#a9b8c4'), hexc('#dedcd0'), seed=61, horizon=0.93, cloud=0.5, scale=560, stretch=2.2)
    # 夜空：上部几朵大一点的云（水墨的云团）
    rng = np.random.default_rng(5)
    # 远山（塔基以下，一层层）
    r1 = ridge_y(W, 3130, 520, 71, rough=0.5, scale=640)
    mountain(S, r1, 3260, N['far3'], N['far1'], seed=21, tex=0.5, tex_op=0.24, haze=0.3)
    mist(S, 0, W, 3040, 80, seed=22, op=0.7)
    r2 = ridge_y(W, 3190, 280, 72, rough=0.55, scale=420)
    mountain(S, r2, 3290, N['far2'], N['mid1'], seed=23, tex=0.7, tex_op=0.26, haze=0.2)
    mist(S, 0, W, 3130, 60, seed=24, op=0.6)
    # 城里的屋顶（塔基四周）：一排排灰瓦顶，隔着雾
    R = Canvas(W, H)
    x = -60
    i = 0
    while x < W + 60:
        w = rng.uniform(170, 300)
        ye = 3190 + rng.uniform(-30, 30)
        rwash(R, x + w * 0.1, ye, x + w * 0.9, ye + 100, A['brick_lt'], op=1.0, wob=1.0, seed=800 + i, tex_k=0.15, rim=0.1)
        eave_roof(R, x + w / 2, ye, w * 0.9, rng.uniform(40, 62), seed=900 + i, ridge_ratio=0.74, up=0.03, bells=False, orn=(w > 230), gap=10, under=0.03, under_span=w * 0.4, sag_p=1.8)
        x += w * rng.uniform(0.7, 0.95)
        i += 1
    R.rgb = mix(R.rgb, N['mist'][None, None, :], (0.4 * R.a)[..., None]).astype(F)
    S.over(0, H, 0, W, R.rgb, R.a)
    mist(S, 0, W, 3225, 40, seed=25, op=0.75)
    # 一段远处的城墙 + 垛口（在屋顶之前）
    def post(v, C):
        if v != 'night':
            return
        r = np.random.default_rng(3)
        pts = []
        for _ in range(170):
            y = r.uniform(30, 2700) ** 1.0
            pts.append((r.uniform(10, W - 10), y, r.choice([1.2, 1.5, 1.8, 2.2], p=[0.4, 0.3, 0.2, 0.1])))
        pts = [p for p in pts]
        dots(C, pts, hexc('#EFE8D8'), op=0.55)
    save2('pagoda_far', S, variants=('night', 'lit'), gain=0.6, keep=0.15, post=post)

if 'mid' in which:
    M = Canvas(W, H)
    # 几缕云：横向的雾带，从塔后飘过（塔在 near 层，会盖住它们）
    for k, (y, th, op_, sd) in enumerate([(250, 90, 0.55, 31), (780, 110, 0.6, 32), (1350, 100, 0.55, 33), (1880, 120, 0.6, 34), (2400, 110, 0.55, 35), (2900, 90, 0.6, 36)]):
        mist(M, 0, W, y, th, seed=sd, op=op_, scale=300, color=N['mist'])
    # 几团水墨的云（侧边，小）
    save2('pagoda_mid', M, variants=('night', 'lit'), gain=0.58, keep=0.15)

if 'near' in which:
    Nn = Canvas(W, H)
    lm = LightMap(W, H)
    gy = (GROUND - 2 + 4 * np.sin(np.arange(W) / 190.0)).astype(F)
    ground_strip(Nn, gy, H, N['earth_lt'], N['earth'], seed=7, tex=0.9, x0=0, x1=W)
    info, deck = pagoda_tower(Nn, CX, GROUND, lm=lm, seed=11, t_first=310)
    print('tiers', [(d['k'], round(d['eave']), round(d['roof_top'])) for d in info], 'deck', deck)
    # 顶：栏杆平台 + 塔刹
    top = info[-1]
    # 平台板 + 塔刹 + 刹链
    rwash(Nn, CX - 112, deck - 6, CX + 112, deck + 6, A['slab_lt'], op=1.0, wob=0.6, seed=51, tex_k=0.12, rim=0.14)
    line(Nn, [(CX - 112, deck - 6), (CX + 112, deck - 6)], 2.6, 0.75, INK, 52, dry=0.25)
    tip = stupa_finial(Nn, CX, deck - 6, seed=53)
    print('finial tip', tip)
    for sg in (-1, 1):
        ex = CX + sg * top['eave_w'] / 2
        ey = top['eave'] - 0.052 * top['eave_w']
        brush(Nn, [(CX + sg * 6, deck - 6 - 175), (CX + sg * top['eave_w'] * 0.25, deck - 6 - 120), (ex, ey)], w0=1.8, color=INK, op=0.55, seed=60 + sg, wob=0.8, taper=0.1, dry=0.0)
    balustrade(Nn, CX - 96, CX + 96, deck + 2, h=40, post_gap=32, seed=70)
    # 台阶 + 石栏
    stair_front(Nn, CX, GROUND - 60, GROUND + 2, 230, 290, steps=4, seed=31)
    balustrade(Nn, 700, 828 + 0, GROUND - 60 + 8, h=58, post_gap=47, seed=40) if False else None
    balustrade(Nn, 696, 836, GROUND - 56, h=60, post_gap=46.5, seed=40)
    balustrade(Nn, 1084, 1224, GROUND - 56, h=60, post_gap=46.5, seed=41)
    save2('pagoda_near', Nn, variants=('night', 'lit'), gain=0.55, keep=0.2, lights=[(lm, WINDOW_LIGHT)])
