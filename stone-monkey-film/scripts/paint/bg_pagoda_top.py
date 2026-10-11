"""塔顶（S5/S6：金鼓）。2400×1080，far + near。平台地面 y=832，四周木柱/栏杆（柱 x≈200 与 x≈2200，栏杆高≈120），
中央 x≈1200 的鼓架（高≈120，鼓放在上面），顶上的飞檐伸出一角；栏杆外是夜空、远处的城市屋顶和云。
用法：python3 bg_pagoda_top.py [far] [near]"""
from cn_arch import *
import sys
W, H = 2400, 1080
which = sys.argv[1:] or ['far', 'near']
FLOOR_BACK = 802       # 栏杆脚（平台后沿）

if 'far' in which:
    S = sky(W, H, hexc('#76879a'), hexc('#a5b4c0'), hexc('#d6d6cb'), seed=81, horizon=0.72, cloud=0.55, scale=420)
    r1 = ridge_y(W, 625, 150, 82, rough=0.5, scale=820)
    mountain(S, r1, 700, N['far3'], N['far1'], seed=31, tex=0.5, tex_op=0.22, haze=0.35, glaze=0.28)
    mist(S, 0, W, 610, 60, seed=32, op=0.6)
    # 脚下的城：一层层小屋顶（越远越小），隔着雾
    rng = np.random.default_rng(12)
    R = Canvas(W, H)
    for row, (yb, wlo, whi, hh) in enumerate([(630, 16, 34, 6), (644, 22, 46, 9), (658, 30, 62, 12), (674, 40, 80, 16)]):
        x = -30
        i = 0
        while x < W + 40:
            w = rng.uniform(wlo, whi)
            ye = yb + rng.uniform(-6, 6)
            rwash(R, x + w * 0.1, ye, x + w * 0.9, ye + 20, A['brick_lt'], op=1.0, wob=0.6, seed=1000 + row * 100 + i, tex_k=0.12, rim=0.08)
            eave_roof(R, x + w / 2, ye, w * 0.95, hh * rng.uniform(0.8, 1.1), seed=1100 + row * 100 + i, ridge_ratio=0.7, up=0.04, bells=False, orn=False, gap=8, under=0.0, sag_p=1.8, ink=0.6)
            x += w * rng.uniform(0.8, 1.05)
            i += 1
        R.rgb = mix(R.rgb, N['mist'][None, None, :], (0.30 - row * 0.06) * (R.a)[..., None]).astype(F)
        S.over(0, H, 0, W, R.rgb, R.a)
        R = Canvas(W, H)
        mist(S, 0, W, yb + 14, 16, seed=40 + row, op=0.5)

    def post(v, C):
        r = np.random.default_rng(8)
        if v == 'night':
            pts = [(r.uniform(10, W - 10), r.uniform(150, 560), r.choice([1.2, 1.6, 2.0, 2.6], p=[0.4, 0.3, 0.2, 0.1])) for _ in range(120)]
            dots(C, pts, hexc('#EFE8D8'), op=0.6)
        # 城里零星的窗光（纸白，很小）
        if v in ('night', 'lit'):
            pts = [(r.uniform(20, W - 20), r.uniform(640, 676), r.uniform(0.9, 1.5)) for _ in range(40)]
            dots(C, pts, hexc('#EFE8D8'), op=0.7)
    save2('pagoda_top_far', S, variants=('night', 'lit'), gain=0.6, keep=0.15, post=post)

if 'near' in which:
    Nn = Canvas(W, H)
    lm = LightMap(W, H)
    # 地面：青砖的方砖
    floor_surface(Nn, 0, FLOOR_BACK - 4, W, H, A['brick'] * 0.95, vp=(1200, 380), tile_px=118, tile_h_px=46, seed=5, var=0.08)
    rwash(Nn, 0, FLOOR_BACK - 6, W, FLOOR_BACK + 6, A['wood_dk'], op=0.95, wob=0.8, seed=6, tex_k=0.1, rim=0.0)     # 栏杆下的踢脚
    line(Nn, [(0, FLOOR_BACK + 6), (W, FLOOR_BACK + 6)], 2.4, 0.65, INK, 7, dry=0.3)
    # 栏杆（后沿）
    pg = 2000 / 13
    wood_railing(Nn, 200 - 2 * pg, 2200 + 2 * pg, FLOOR_BACK, h=124, post_gap=pg, seed=10)
    # 屋檐：檐口 + 额枋斗拱 + 椽底
    roof_underside(Nn, -10, W + 10, 0, 58, seed=20)
    dougong(Nn, -10, W + 10, 58, 86, pitch=74, seed=21)
    # 柱子
    for k, x in enumerate((200, 2200)):
        column(Nn, x, 144, FLOOR_BACK + 12, 112, seed=30 + k, base=True, base_h=40, grain_n=90)
    # 灯笼（挂在额枋下）
    for k, x in enumerate((690, 1710)):
        lantern(Nn, x, 262, 22, seed=40 + k, lm=lm, cord=118)
    # 鼓架
    drum_stand(Nn, 1200, 832, h=120, span=290, seed=50)
    # 地上的尘与裂
    rr = np.random.default_rng(3)
    for c in range(8):
        x0 = rr.uniform(100, 2300); y0 = rr.uniform(850, 1040)
        brush(Nn, [(x0, y0), (x0 + rr.normal(0, 30), y0 + rr.normal(0, 6)), (x0 + rr.normal(0, 60), y0 + rr.normal(0, 8))], w0=2.0, color=INK, op=0.25, seed=70 + c, wob=0.6, taper=0.3, dry=0.5)
    save2('pagoda_top_near', Nn, variants=('night', 'lit'), gain=0.58, keep=0.2, lights=[(lm, WINDOW_LIGHT)])
