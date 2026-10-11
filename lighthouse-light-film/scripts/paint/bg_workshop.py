"""场景 3：Mrs Mallet 的修理铺（室内，冷色的天光从窗里进来；不画任何暖色的灯）。
 far：后墙 + 窗 + 架子 + 挂板；near：工作台的前脸 + 台面上的小零件（角色站在台面上 / 台前时，叠在 near 之前或之后由 Remotion 决定）。"""
from common import *

WW = 2400
FLOOR = 840


def cog(L, x, y, r, seed, col='#8591ad', teeth=10):
    pts = []
    for i in range(teeth * 2):
        a = i / (teeth * 2) * 2 * math.pi
        rr = r * (1.0 if i % 2 == 0 else 0.8)
        pts += [(x + math.cos(a) * rr, y + math.sin(a) * rr), (x + math.cos(a + math.pi / teeth * 0.5) * rr, y + math.sin(a + math.pi / teeth * 0.5) * rr)]
    wash(L, np.array(pts, F), hexc(col), op=1.0, wob=0.6, seed=seed, smooth=0, tex_k=0.16)
    outline(L, pts, 1.2, 0.7, seed + 1)
    wash(L, np.array([[x + math.cos(a) * r * 0.28, y + math.sin(a) * r * 0.28] for a in np.linspace(0, 6.28, 10, endpoint=False)], F), hexc('#c9d3e6'), op=1.0, wob=0.3, seed=seed + 2, smooth=2)


def jar(L, x, y, w, h, seed, fill='#b9c8e2'):
    wash(L, rect(x - w / 2, y - h, x + w / 2, y), hexc('#d6e0f0'), op=0.8, wob=0.6, seed=seed, smooth=0, tex_k=0.06)
    wash(L, rect(x - w / 2 + 3, y - h * 0.65, x + w / 2 - 3, y - 2), hexc(fill), op=0.85, wob=0.5, seed=seed + 1, smooth=0, tex_k=0.14)
    outline(L, rect(x - w / 2, y - h, x + w / 2, y), 1.2, 0.7, seed + 2)
    wash(L, rect(x - w / 2 - 2, y - h - 8, x + w / 2 + 2, y - h), hexc('#566480'), op=1.0, wob=0.4, seed=seed + 3, smooth=0)


def far():
    L = Canvas(WW, H)
    # 后墙：竖木板 + 暗一点的踢脚；地板
    planks(L, 0, 0, WW, FLOOR, seed=1, col='#a4aec6', gap=70, hor=False)
    planks(L, 0, FLOOR, WW, H, seed=3, col='#6b7392', gap=54, hor=True)
    glow(L, 520, 700, 520, hexc('#eaf1fb'), 0.30, 1.6)
    ink(L, [(0, FLOOR), (WW, FLOOR)], w0=3, color=INK, op=0.7, seed=4, wob=1.0)
    # 窗：冷色的天光 + 外面的雪
    wx0, wy0, wx1, wy1 = 230, 150, 640, 560
    wash(L, rect(wx0, wy0, wx1, wy1), hexc('#d5e1f2'), op=1.0, wob=0.8, seed=5, smooth=0, tex_k=0.05)
    sk = sky(wx1 - wx0, wy1 - wy0, 'day', seed=3, horizon=0.9, blotch=0.25)
    L.over(wy0, wy1, wx0, wx1, sk, np.full((wy1 - wy0, wx1 - wx0), 0.95, F))
    flakes(L, 70, 7, 1.5, 3.4, region=(wx0, wy0, wx1, wy1), color=(0.98, 0.99, 1), op=0.95, sparkle=0.0)
    for k, (a, b) in enumerate([((wx0, wy0), (wx1, wy0)), ((wx1, wy0), (wx1, wy1)), ((wx1, wy1), (wx0, wy1)), ((wx0, wy1), (wx0, wy0))]):
        ink(L, [a, b], w0=9, color=hexc('#445273'), op=0.95, seed=10 + k, wob=0.5, taper=0.02)
    ink(L, [((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], w0=7, color=hexc('#445273'), op=0.95, seed=15, wob=0.4)
    ink(L, [(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], w0=7, color=hexc('#445273'), op=0.95, seed=16, wob=0.4)
    wash(L, rect(wx0 - 24, wy1, wx1 + 24, wy1 + 20), hexc('#566480'), op=1.0, wob=0.6, seed=17, smooth=0)
    wash(L, np.array([[wx0 - 10, wy1 + 2], [wx1 + 10, wy1 + 2], [wx1, wy1 - 14], [wx0, wy1 - 14]], F), P['snow'], op=1.0, wob=1.5, seed=18, smooth=2, tex_k=0.06)
    # 窗下落在地板上的一块淡光
    # 右边的架子：三层，摆着零件、罐子、齿轮、旧机器人的脑袋
    for k, sy in enumerate((250, 420, 590)):
        sx0, sx1 = 1500, 2300
        wash(L, rect(sx0, sy, sx1, sy + 18), hexc('#51608a'), op=1.0, wob=0.8, seed=30 + k, smooth=0, tex_k=0.2)
        outline(L, rect(sx0, sy, sx1, sy + 18), 1.3, 0.75, 33 + k)
        for bx in (sx0 + 40, sx1 - 40):
            ink(L, [(bx, sy + 18), (bx, sy + 70)], w0=4, color=INK, op=0.6, seed=36 + k, wob=0.4)
    r = np.random.default_rng(5)
    for i in range(6):
        jar(L, 1560 + i * 62 + r.normal(0, 6), 250, 40, 56 + r.uniform(0, 30), 100 + i, fill=['#b9c8e2', '#a3b5d6', '#c8d4ea'][i % 3])
    for i, (cx, rr) in enumerate([(1980, 38), (2040, 26), (2150, 44)]):
        cog(L, cx, 420 - rr, rr, 120 + i * 5, teeth=10 + i)
    # 一个灰蓝色的旧机器人头（架子上的老朋友）
    wash(L, rect(1580, 340, 1660, 420), hexc('#8d9bbb'), op=1.0, wob=0.8, seed=140, smooth=1, tex_k=0.18)
    outline(L, rect(1580, 340, 1660, 420), 1.4, 0.75, 141)
    dots(L, [(1605, 368, 6), (1636, 368, 6)], hexc('#d8e0ef'), 1.0)
    ink(L, [(1600, 396), (1642, 396)], w0=2, color=INK, op=0.8, seed=142, wob=0.4)
    ink(L, [(1620, 340), (1620, 316)], w0=2, color=INK, op=0.8, seed=143, wob=0.3)
    dots(L, [(1620, 312, 6)], hexc('#d8e0ef'), 1.0)
    for i in range(4):
        wash(L, rect(1760 + i * 66, 590 - 48 - 12 * (i % 2), 1800 + i * 66, 590), hexc(['#7587ae', '#96a6c6', '#6c7ca4', '#a7b6d2'][i]), op=1.0, wob=0.7, seed=150 + i, smooth=0, tex_k=0.16)
        outline(L, rect(1760 + i * 66, 590 - 48 - 12 * (i % 2), 1800 + i * 66, 590), 1.2, 0.7, 160 + i)
    # 工具挂板（后墙中间）：锤子、扳手、锯子的剪影挂在钉子上
    wash(L, rect(760, 200, 1360, 540), hexc('#8592b2'), op=0.95, wob=1.2, seed=170, smooth=0, tex_k=0.12)
    outline(L, rect(760, 200, 1360, 540), 1.5, 0.7, 171)
    tc = hexc('#2f3b5b')
    for i in range(3):   # 锤子
        x = 810 + i * 60
        ink(L, [(x, 250), (x, 400 - i * 30)], w0=8, color=tc, op=0.9, seed=180 + i, wob=0.4)
        wash(L, rect(x - 22, 244, x + 22, 270), tc, op=0.95, wob=0.5, seed=190 + i, smooth=0)
    for i in range(3):   # 扳手
        x = 1010 + i * 62
        ink(L, [(x, 270), (x, 450 - i * 22)], w0=9, color=tc, op=0.9, seed=200 + i, wob=0.4)
        ring = [(x + math.cos(a) * 17, 252 + math.sin(a) * 17) for a in np.linspace(0.6, 5.7, 12)]
        ink(L, ring, w0=8, color=tc, op=0.9, seed=210 + i, wob=0.3)
    saw = np.array([[1210, 250], [1330, 250], [1330, 262], [1230, 330], [1210, 330]], F)   # 锯子
    wash(L, saw, hexc('#c4cee2'), op=1.0, wob=0.6, seed=220, smooth=0, tex_k=0.1)
    outline(L, saw, 1.4, 0.8, 221)
    wash(L, rect(1198, 240, 1230, 340), tc, op=0.95, wob=0.5, seed=222, smooth=0)
    for x in (810, 870, 930, 1010, 1072, 1134, 1210):
        dots(L, [(x, 226, 3.2)], hexc('#d8e0ef'), 1.0)
    # 墙上的小地图似的黑板 / 纸条
    for i in range(3):
        wash(L, rect(1390 + i * 0, 200, 1390, 200), hexc('#ffffff'), op=0.0, seed=0)
        # 窗边的衣钩 + 挂着的围巾似的灰布
    ink(L, [(110, 160), (110, 330)], w0=3, color=INK, op=0.5, seed=230, wob=0.5)
    grade(L, 'dusk')
    return L


def near():
    L = Canvas(WW, H)
    # 工作台：厚台面 + 前脸（抽屉）+ 脚
    top_y = 730
    bx0, bx1 = 760, 2240
    for lx in (bx0 + 40, bx1 - 90):
        wash(L, rect(lx, top_y + 20, lx + 52, FLOOR + 36), hexc('#6b7897'), op=1.0, wob=0.8, seed=lx, smooth=0, tex_k=0.2)
        outline(L, rect(lx, top_y + 20, lx + 52, FLOOR + 36), 1.3, 0.7, lx + 1)
    front = rect(bx0, top_y + 10, bx1, top_y + 150)
    wash(L, front, hexc('#7684a6'), op=1.0, wob=1.0, seed=300, smooth=0, tex_k=0.2, rim=0.14)
    outline(L, front, 1.6, 0.75, 301)
    for k in range(4):
        dx0 = bx0 + 60 + k * 340
        dr = rect(dx0, top_y + 28, dx0 + 300, top_y + 134)
        wash(L, dr, hexc('#8794b4'), op=1.0, wob=0.8, seed=310 + k, smooth=0, tex_k=0.16)
        outline(L, dr, 1.3, 0.7, 320 + k)
        wash(L, rect(dx0 + 118, top_y + 70, dx0 + 182, top_y + 82), hexc('#2f3b5b'), op=1.0, wob=0.4, seed=330 + k, smooth=0)
    planks(L, bx0 - 20, top_y - 14, bx1 + 20, top_y + 12, seed=340, col='#98a4c2', gap=26, hor=True)
    ink(L, [(bx0 - 20, top_y - 14), (bx1 + 20, top_y - 14)], w0=2.4, color=INK, op=0.7, seed=341, wob=0.6)
    # 台面上的小东西：钳子、几颗螺丝、一圈电线、一个小盒子（不画灯）
    for i in range(8):
        sx = 880 + i * 24
        dots(L, [(sx, top_y - 20, 4)], hexc('#9aa9c8'), 1.0)
    for k in range(3):
        ink(L, [(1000 + k * 3, top_y - 6), (1040 + k * 5, top_y - 20 - k), (1100, top_y - 12), (1130, top_y - 6)], w0=2.2, color=hexc('#2f3b5b'), op=0.8, seed=350 + k, wob=0.6)
    # 左边：一只小木凳 + 一个装零件的木箱（留白处不堆东西）
    st = rect(250, 840, 380, 862)
    wash(L, st, hexc('#8794b4'), op=1.0, wob=0.8, seed=360, smooth=0, tex_k=0.18)
    outline(L, st, 1.4, 0.75, 361)
    for lx in (262, 358):
        ink(L, [(lx, 862), (lx - 8 if lx < 300 else lx + 8, 960)], w0=7, color=hexc('#586585'), op=0.95, seed=362, wob=0.4)
    cr = rect(150, 905, 330, 1010)
    wash(L, cr, hexc('#7d8aab'), op=1.0, wob=1.0, seed=370, smooth=0, tex_k=0.2)
    outline(L, cr, 1.5, 0.75, 371)
    for k in range(1, 4):
        ink(L, [(150, 905 + k * 26), (330, 905 + k * 26)], w0=1.4, color=INK, op=0.4, seed=372 + k, wob=0.5)
    for k in range(5):
        cog(L, 175 + k * 30, 900 - (k % 2) * 6, 13 + (k % 3) * 3, 380 + k, teeth=8)
    grade(L, 'dusk')
    return L


if __name__ == '__main__':
    f = far(); n = near()
    save_pair('workshop', f, n)
    print('ok')
