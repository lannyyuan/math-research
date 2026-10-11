"""绘本网页的补充插图背景（影片里没有的章节）：城里、城堡、害怕的夜、冬天的游乐场、大篷车、梦里的海边、春天。
每幅 1920×1080 一张图（角色在 Remotion 的 Plate 合成里叠上去），同一套画笔、同一套调色盘。"""
import sys
from common import *

BW, BH = 1920, 1080


def new(kind=None, hz=0.5, seed=1, blotch=0.3):
    L = Canvas(BW, BH)
    if kind:
        L.rgb[:] = sky(BW, BH, kind, seed=seed, horizon=hz, blotch=blotch)
        L.a[:] = 1
    return L


# ───────────── 第三章：城里 ─────────────
def city():
    L = new('day', 0.55, seed=31)
    hz = 520
    hills(L, ridge_pts(0, BW, hz + 20, 30, 33, 40), hz + 60, hexc('#9aabc6'), snow=True, seed=33, op=0.9)
    field(L, hz + 40, 820, seed=35)
    r = np.random.default_rng(5)
    # 一排排的楼：错落、白墙、蓝灰屋顶，一楼是店铺（橱窗是冷白的）
    x = -20
    k = 0
    cols = ['#e7ecf6', '#d9e1f0', '#eceff7', '#cfd9ec', '#e2e8f4']
    while x < BW + 40:
        w = r.uniform(250, 330)
        h = r.uniform(300, 470)
        base = 800
        wall = rect(x, base - h, x + w, base)
        wash(L, wall, hexc(cols[k % 5]), op=1.0, wob=1.2, seed=100 + k, smooth=0, tex_k=0.1, rim=0.12)
        sh = rect(x + w * 0.74, base - h, x + w, base)
        wash(L, sh, P['snow_sh2'], op=0.32, wob=1.0, seed=110 + k, smooth=0, tex_k=0.12)
        outline(L, wall, 1.7, 0.75, 120 + k)
        roof = np.array([[x - 8, base - h + 4], [x + w * 0.5, base - h - 60 - r.uniform(0, 30)], [x + w + 8, base - h + 4]], F)
        wash(L, roof, hexc(['#566480', '#4b5876', '#62708f'][k % 3]), op=1.0, wob=1.0, seed=130 + k, smooth=0, tex_k=0.15)
        outline(L, roof, 1.6, 0.8, 140 + k)
        cap = np.array([[x - 6, base - h + 2], [x + w * 0.5, base - h - 64], [x + w + 6, base - h + 2], [x + w * 0.5, base - h - 38]], F)
        wash(L, cap, P['snow'], op=1.0, wob=1.5, seed=150 + k, smooth=1, tex_k=0.06)
        # 窗：两到三排
        for row in range(int((h - 190) // 95)):
            for c in range(3):
                window(L, x + w * (0.12 + 0.3 * c), base - h + 36 + row * 95, w * 0.17, 56, seed=200 + k * 20 + row * 3 + c)
        # 一楼店铺：大橱窗 + 条纹遮阳篷
        wash(L, rect(x + 14, base - 150, x + w - 14, base - 12), hexc('#dfeaf9'), op=1.0, wob=0.8, seed=300 + k, smooth=0, tex_k=0.05)
        outline(L, rect(x + 14, base - 150, x + w - 14, base - 12), 1.6, 0.8, 310 + k)
        for j in range(5):
            wash(L, rect(x + 14 + j * (w - 28) / 5, base - 176, x + 14 + (j + 0.5) * (w - 28) / 5, base - 150), hexc(['#6f84b5', '#eef2fa'][j % 2]), op=1.0, wob=0.4, seed=320 + k * 5 + j, smooth=0)
            wash(L, rect(x + 14 + (j + 0.5) * (w - 28) / 5, base - 176, x + 14 + (j + 1) * (w - 28) / 5, base - 150), hexc(['#eef2fa', '#6f84b5'][j % 2]), op=1.0, wob=0.4, seed=330 + k * 5 + j, smooth=0)
        # 橱窗里的小东西（冷色）：一棵小树、几个礼物
        wash(L, np.array([[x + w * 0.3, base - 20], [x + w * 0.3 + 26, base - 110], [x + w * 0.3 + 52, base - 20]], F), hexc('#4f7a7a'), op=1.0, wob=0.5, seed=340 + k, smooth=0)
        x += w + r.uniform(6, 20)
        k += 1
    # 钟楼
    cx = 1330
    wash(L, rect(cx - 62, 160, cx + 62, 520), hexc('#cdd8ec'), op=1.0, wob=1.0, seed=400, smooth=0, tex_k=0.1)
    outline(L, rect(cx - 62, 160, cx + 62, 520), 1.8, 0.8, 401)
    wash(L, np.array([[cx - 78, 164], [cx, 40], [cx + 78, 164]], F), hexc('#4b5876'), op=1.0, wob=1.0, seed=402, smooth=0, tex_k=0.15)
    outline(L, np.array([[cx - 78, 164], [cx, 40], [cx + 78, 164]], F), 1.8, 0.85, 403)
    dots(L, [(cx, 250, 40)], hexc('#f4f7fd'), 1.0)
    ink(L, np.array([[cx + math.cos(a) * 40, 250 + math.sin(a) * 40] for a in np.linspace(0, 6.4, 24)], F), w0=2.4, color=INK, op=0.85, seed=404, wob=0.4)
    ink(L, [(cx, 250), (cx, 222)], w0=3, color=INK, op=0.9, seed=405, wob=0.2)
    ink(L, [(cx, 250), (cx + 18, 258)], w0=3, color=INK, op=0.9, seed=406, wob=0.2)
    # 路：雪被轧成灰蓝的带，两道车辙；人行道的边沿
    top = np.array([[-40, 800], [700, 798], [1400, 804], [1960, 800]], F)
    snow_ground(L, catmull(top, 6), 1200, seed=51)
    road = np.array([[-40, 870], [900, 862], [1960, 866], [1960, 1000], [900, 1004], [-40, 1008]], F)
    wash(L, road, hexc('#c7d2e6'), op=0.55, wob=4, seed=52, smooth=2, tex_k=0.14)
    for k2, dy in enumerate((20, 80)):
        ink(L, catmull(np.array([[-40, 870 + dy], [900, 862 + dy], [1960, 866 + dy]], F), 6), w0=3.0, color=P['snow_sh3'], op=0.35, seed=60 + k2, wob=2.0, taper=0.05)
    # 路灯杆（灭着）和停着的一辆蓝灰色公交车
    from bg_town import lamp_post
    for i, lx in enumerate((220, 760, 1700)):
        lamp_post(L, lx, 840 + i * 4, 340, 70 + i * 9)
    bx, by = 1060, 842
    body = rect(bx - 200, by - 150, bx + 200, by)
    wash(L, body, hexc('#8497c2'), op=1.0, wob=1.0, seed=70, smooth=1, tex_k=0.12)
    outline(L, body, 1.8, 0.85, 71)
    for j in range(6):
        wash(L, rect(bx - 184 + j * 62, by - 126, bx - 140 + j * 62, by - 80), hexc('#e6eefb'), op=1.0, wob=0.5, seed=72 + j, smooth=0)
        outline(L, rect(bx - 184 + j * 62, by - 126, bx - 140 + j * 62, by - 80), 1.3, 0.7, 80 + j)
    wash(L, rect(bx - 200, by - 40, bx + 200, by - 30), hexc('#eef2fa'), op=1.0, wob=0.4, seed=90, smooth=0)
    for wx in (bx - 120, bx + 120):
        dots(L, [(wx, by + 2, 30)], hexc('#2f3a5c'), 1.0)
        dots(L, [(wx, by + 2, 13)], hexc('#aab6d2'), 1.0)
    for i, (bx_, by_) in enumerate([(100, 1060), (1500, 1070)]):
        bush(L, bx_, by_, 130, 1.0, 8, seed=420 + i)
    grade(L, 'dusk')
    return L


# ───────────── 第九章：山顶的古堡 ─────────────
def castle():
    L = new('storm', 0.5, seed=41, blotch=0.4)
    hz = 520
    hills(L, ridge_pts(0, BW, hz + 10, 40, 43, 40), hz + 80, hexc('#2d4067'), snow=True, seed=43, op=1.0, snow_col=hexc('#6f83ab'))
    # 一座岩石山坡，顶上是古堡
    hill = np.array([[-40, 1100], [-40, 760], [380, 620], [760, 470], [1100, 330], [1500, 380], [1960, 520], [1960, 1100]], F)
    wash(L, hill, P['rock'], op=1.0, wob=3, seed=44, smooth=2, tex_k=0.2, rim=0.2)
    hatch(L, hill, 72, 10, 24, P['rock_dk'], op=0.5, w=1.2, seed=45)
    sn = np.array([[-40, 1100], [-40, 800], [380, 690], [760, 540], [1100, 400], [1500, 450], [1960, 600], [1960, 1100]], F)
    wash(L, sn, P['snow'], op=1.0, wob=3, seed=46, smooth=2, tex_k=0.07)
    wash(L, sn + [0, 14], P['snow_sh1'], op=0.28, wob=2, seed=47, smooth=2)
    # 古堡：断了的墙 + 一座圆塔
    wall_col = hexc('#7b88a8')
    segs = [(700, 300, 960, 420), (980, 240, 1130, 420), (1130, 330, 1420, 420)]
    for k, (x0, y0, x1, y1) in enumerate(segs):
        pts = np.array([[x0, y1], [x0, y0 + 30], [x0 + (x1 - x0) * 0.2, y0], [x0 + (x1 - x0) * 0.35, y0 + 40], [x0 + (x1 - x0) * 0.55, y0 + 10], [x0 + (x1 - x0) * 0.8, y0 + 50], [x1, y0 + 20], [x1, y1]], F)
        wash(L, pts, wall_col, op=1.0, wob=1.5, seed=200 + k, smooth=0, tex_k=0.2, rim=0.16)
        hatch(L, pts, 0, 14, 40, hexc('#4d5876'), op=0.35, w=1.2, seed=210 + k)
        outline(L, pts, 1.8, 0.85, 220 + k)
    # 圆塔（中间，高）：屋顶没了，有个窗洞
    tx0, tx1, ty0 = 1000, 1130, 150
    tower = np.array([[tx0, 430], [tx0 - 6, ty0 + 20], [tx0 + 20, ty0 - 8], [tx0 + 44, ty0 + 24], [tx0 + 66, ty0 - 4], [tx1 - 10, ty0 + 30], [tx1 + 6, ty0 + 14], [tx1 + 10, 430]], F)
    wash(L, tower, hexc('#8794b4'), op=1.0, wob=1.2, seed=230, smooth=0, tex_k=0.18, rim=0.16)
    hatch(L, tower, 0, 13, 36, hexc('#4d5876'), op=0.35, w=1.2, seed=231)
    outline(L, tower, 2.0, 0.85, 232)
    wash(L, np.array([[1040, 250], [1040, 210], [1064, 190], [1088, 210], [1088, 250]], F), hexc('#1a2547'), op=1.0, wob=0.6, seed=233, smooth=1, tex_k=0.1)
    outline(L, np.array([[1040, 250], [1040, 210], [1064, 190], [1088, 210], [1088, 250]], F), 1.6, 0.85, 234)
    for k, (cx, cy, w_) in enumerate([(990, 160, 50), (1120, 178, 40)]):   # 墙头的雪
        wash(L, np.array([[cx - w_, cy + 8], [cx - w_ * 0.5, cy - 10], [cx, cy - 16], [cx + w_ * 0.5, cy - 8], [cx + w_, cy + 8], [cx, cy + 12]], F), P['snow'], op=1.0, wob=1.0, seed=240 + k, smooth=2, tex_k=0.06)
    # 松树 + 灌木
    r = np.random.default_rng(3)
    for i in range(12):
        px = r.choice([r.uniform(-20, 560), r.uniform(1500, 1940)])
        py = np.interp(px, [-40, 380, 760, 1100, 1500, 1960], [820, 700, 560, 440, 480, 620]) + r.uniform(20, 120)
        tree_pine(L, px, py, r.uniform(120, 240), seed=300 + i)
    # 前景：雪地和上山的小路
    path = np.array([[-40, 960], [600, 940], [1300, 960], [1960, 940]], F)
    snow_ground(L, catmull(path, 6), 1300, seed=57)
    for i, (bx_, by_) in enumerate([(160, 1060), (900, 1070), (1700, 1060)]):
        bush(L, bx_, by_, 150, 1.0, 8, seed=420 + i)
    grade(L, 'storm')
    return L


# ───────────── 第十章：塔里的夜（害怕）─────────────
def castle_in():
    L = Canvas(BW, BH)
    wash(L, rect(0, 0, BW, BH), hexc('#566785'), op=1.0, wob=0.5, seed=1, smooth=0, tex_k=0.05)
    stones(L, 0, 0, BW, 790, seed=3, col='#74839f', row=64, bw=150)
    planks(L, 0, 790, BW, BH, seed=4, col='#47546f', gap=60, hor=True)
    ink(L, [(0, 790), (BW, 790)], w0=3, color=INK, op=0.8, seed=5, wob=1.0)
    # 拱形的窗：外面是暴风雪的夜
    wx0, wy0, wx1, wy1 = 1380, 170, 1640, 560
    C = Canvas(wx1 - wx0, wy1 - wy0)
    C.rgb[:] = sky(wx1 - wx0, wy1 - wy0, 'storm', seed=9, horizon=0.9, blotch=0.2)
    C.a[:] = 1
    flakes(C, 40, 3, 1.6, 3.4, color=(0.95, 0.97, 1), op=0.95, sparkle=0)
    arch = np.array([[wx0, wy1], [wx0, wy0 + 120], [wx0 + 30, wy0 + 40], [wx0 + 130, wy0], [wx1 - 30, wy0 + 40], [wx1, wy0 + 120], [wx1, wy1]], F)
    S = Canvas(BW, BH)
    S.rgb[wy0:wy1, wx0:wx1] = C.rgb
    S.a[wy0:wy1, wx0:wx1] = 1
    m = poly_mask(chaikin(arch, 2, True), BW, BH)
    if m is not None:
        y0, y1, x0, x1, mm = m
        L.over(y0, y1, x0, x1, S.rgb[y0:y1, x0:x1], mm * S.a[y0:y1, x0:x1])
    ink(L, np.vstack([arch, arch[:1]]), w0=8, color=hexc('#2f3b5b'), op=0.95, seed=10, wob=0.6, taper=0.05)
    wash(L, rect(wx0 - 30, wy1, wx1 + 30, wy1 + 22), hexc('#98a6c4'), op=1.0, wob=0.6, seed=11, smooth=0)
    wash(L, np.array([[wx0 - 20, wy1 + 2], [wx1 + 20, wy1 + 2], [wx1, wy1 - 16], [wx0, wy1 - 16]], F), P['snow'], op=1.0, wob=1.5, seed=12, smooth=2, tex_k=0.06)
    # 蜘蛛网 / 倒挂的蝙蝠（在天花板的暗角里；没有翅膀的轮廓：缩成一团的小黑影）
    for k in range(4):
        ink(L, [(240 + k * 14, 0), (160 + k * 38, 120 + k * 10)], w0=1.0, color=hexc('#aab6d2'), op=0.5, seed=20 + k, wob=0.6, taper=0.3)
    ink(L, [(680, 0), (680, 76)], w0=2, color=hexc('#2f3b5b'), op=0.8, seed=30, wob=0.2)
    wash(L, np.array([[680 + math.cos(a) * 22, 100 + math.sin(a) * 30] for a in np.linspace(0, 6.28, 12, endpoint=False)], F), hexc('#2a3050'), op=1.0, wob=0.5, seed=31, smooth=2)
    dots(L, [(672, 86, 3.4), (688, 86, 3.4)], hexc('#2a3050'), 1.0)
    ink(L, [(668, 80), (664, 66)], w0=3, color=hexc('#2a3050'), op=1.0, seed=32, wob=0.2)
    ink(L, [(692, 80), (696, 66)], w0=3, color=hexc('#2a3050'), op=1.0, seed=33, wob=0.2)
    # 手电筒的光：墙上一个大圆（冷白）
    glow(L, 700, 300, 420, hexc('#eaf2ff'), 0.55, 1.6)
    glow(L, 700, 300, 230, hexc('#ffffff'), 0.5, 1.4)
    grade(L, 'dusk')
    return L


# ───────────── 第十一章：冬天的游乐场 ─────────────
def fairground():
    L = new('storm', 0.46, seed=51, blotch=0.35)
    hz = 500
    hills(L, ridge_pts(0, BW, hz + 12, 36, 53, 40), hz + 60, hexc('#34476f'), snow=True, seed=53, op=1.0, snow_col=hexc('#7d90b6'))
    field(L, hz + 50, 840, seed=55, top='#aebbd6', bot='#dfe6f4')
    # 摩天轮（关着，黑黑的，圈上有雪）
    cx, cy, R = 1380, 400, 250
    ink(L, [(cx - 110, 800), (cx, cy + 20), (cx + 110, 800)], w0=10, color=hexc('#2f3b5b'), op=0.95, seed=60, wob=0.8)
    for a in np.linspace(0, math.pi, 8, endpoint=False):
        ink(L, [(cx + math.cos(a) * R, cy + math.sin(a) * R), (cx - math.cos(a) * R, cy - math.sin(a) * R)], w0=2.4, color=hexc('#4a5778'), op=0.85, seed=int(a * 100), wob=0.5)
    ink(L, np.array([[cx + math.cos(a) * R, cy + math.sin(a) * R] for a in np.linspace(0, 6.4, 60)], F), w0=7, color=hexc('#2f3b5b'), op=0.95, seed=61, wob=0.8)
    for a in np.linspace(0, 2 * math.pi, 12, endpoint=False):
        gx, gy = cx + math.cos(a) * R, cy + math.sin(a) * R
        wash(L, rect(gx - 20, gy, gx + 20, gy + 34), hexc(['#8da2d0', '#c4d0ea', '#7c8fc0'][int(a * 3) % 3]), op=1.0, wob=0.5, seed=int(a * 70), smooth=0)
        outline(L, rect(gx - 20, gy, gx + 20, gy + 34), 1.3, 0.8, int(a * 70) + 1)
        wash(L, np.array([[gx - 22, gy + 2], [gx, gy - 12], [gx + 22, gy + 2]], F), P['snow'], op=1.0, wob=0.5, seed=int(a * 70) + 2, smooth=1)
    dots(L, [(cx, cy, 16)], hexc('#2f3b5b'), 1.0)
    # 滑梯塔（螺旋滑梯，白的）
    hx = 330
    tower = np.array([[hx - 70, 800], [hx - 40, 300], [hx + 40, 300], [hx + 70, 800]], F)
    wash(L, tower, hexc('#e8eef8'), op=1.0, wob=1.0, seed=70, smooth=0, tex_k=0.08, rim=0.14)
    for k in range(5):
        y = 360 + k * 90
        ink(L, [(hx - 60 + k * 2, y), (hx, y + 30), (hx + 60 - k * 2, y + 6)], w0=14, color=hexc('#8da2d0'), op=0.9, seed=80 + k, wob=0.6)
    outline(L, tower, 1.8, 0.8, 90)
    wash(L, np.array([[hx - 60, 306], [hx, 220], [hx + 60, 306]], F), hexc('#566480'), op=1.0, wob=0.6, seed=91, smooth=0, tex_k=0.15)
    wash(L, np.array([[hx - 66, 312], [hx - 20, 266], [hx + 20, 262], [hx + 66, 312], [hx, 300]], F), P['snow'], op=1.0, wob=0.8, seed=92, smooth=2, tex_k=0.06)
    # 大帐篷：蓝白条纹
    bx0, bx1, by = 700, 1080, 800
    for k in range(8):
        x0 = bx0 + k * (bx1 - bx0) / 8
        x1 = bx0 + (k + 1) * (bx1 - bx0) / 8
        peak = (bx0 + bx1) / 2
        tri = np.array([[x0, by], [x0 + (peak - x0) * 0.55, 470], [x1 + (peak - x1) * 0.55, 470], [x1, by]], F)
        wash(L, tri, hexc(['#6f84b5', '#eef2fa'][k % 2]), op=1.0, wob=0.8, seed=100 + k, smooth=0, tex_k=0.08)
    top = np.array([[bx0 + 120, 480], [(bx0 + bx1) / 2, 330], [bx1 - 120, 480]], F)
    wash(L, top, hexc('#6f84b5'), op=1.0, wob=0.6, seed=110, smooth=0)
    outline(L, np.array([[bx0, by], [bx0 + 118, 480], [(bx0 + bx1) / 2, 330], [bx1 - 118, 480], [bx1, by]], F), 1.8, 0.85, 111)
    wash(L, np.array([[bx0 + 120, 480], [(bx0 + bx1) / 2, 322], [bx1 - 120, 480], [(bx0 + bx1) / 2, 470]], F), P['snow'], op=1.0, wob=1.2, seed=112, smooth=2, tex_k=0.06)
    wash(L, np.array([[820, 800], [860, 590], [920, 590], [960, 800]], F), hexc('#1d2a49'), op=1.0, wob=0.6, seed=113, smooth=0, tex_k=0.1)
    ink(L, [((bx0 + bx1) / 2, 330), ((bx0 + bx1) / 2, 280)], w0=2.4, color=INK, op=0.9, seed=114, wob=0.2)
    wash(L, np.array([[(bx0 + bx1) / 2, 284], [(bx0 + bx1) / 2 + 46, 296], [(bx0 + bx1) / 2, 308]], F), hexc('#8da2d0'), op=1.0, wob=0.4, seed=115, smooth=0)
    # 摊位（旋转木马、小摊）
    for i, (sx, sw) in enumerate([(1620, 200), (1860, 160)]):
        wash(L, rect(sx - sw / 2, 700, sx + sw / 2, 800), hexc('#9aa8c8'), op=1.0, wob=0.8, seed=120 + i, smooth=0, tex_k=0.15)
        outline(L, rect(sx - sw / 2, 700, sx + sw / 2, 800), 1.6, 0.8, 130 + i)
        wash(L, np.array([[sx - sw / 2 - 10, 704], [sx, 660], [sx + sw / 2 + 10, 704]], F), hexc('#566480'), op=1.0, wob=0.6, seed=140 + i, smooth=0)
        wash(L, np.array([[sx - sw / 2 - 6, 706], [sx, 664], [sx + sw / 2 + 6, 706], [sx, 688]], F), P['snow'], op=1.0, wob=0.8, seed=150 + i, smooth=1, tex_k=0.06)
    # 前景：雪地 + 大门（拱门，敞着）+ 篱笆
    top2 = np.array([[-40, 830], [800, 826], [1500, 834], [1960, 830]], F)
    snow_ground(L, catmull(top2, 6), 1300, seed=157)
    for px in (120, 1800):
        wash(L, rect(px - 26, 560, px + 26, 880), hexc('#566480'), op=1.0, wob=1.0, seed=160 + px % 7, smooth=0, tex_k=0.15)
        outline(L, rect(px - 26, 560, px + 26, 880), 1.8, 0.85, 170 + px % 7)
        wash(L, np.array([[px - 40, 566], [px, 520], [px + 40, 566], [px, 574]], F), P['snow'], op=1.0, wob=0.8, seed=180 + px % 5, smooth=1, tex_k=0.06)
    wash(L, rect(120, 580, 1800, 626), hexc('#8da2d0'), op=0.0, wob=0.1, seed=1, smooth=0)
    for i, (bx_, by_) in enumerate([(300, 1060), (1000, 1070), (1560, 1060)]):
        bush(L, bx_, by_, 130, 1.0, 8, seed=430 + i)
    grade(L, 'storm')
    return L


# ───────────── 第十三章：大篷车里面 ─────────────
def caravan():
    L = Canvas(BW, BH)
    planks(L, 0, 0, BW, 800, seed=1, col='#9aa6c0', gap=62, hor=False)
    planks(L, 0, 800, BW, BH, seed=2, col='#5f6b88', gap=56, hor=True)
    ink(L, [(0, 800), (BW, 800)], w0=3, color=INK, op=0.8, seed=3, wob=0.8)
    # 小窗：夜里的雪
    wx0, wy0, wx1, wy1 = 760, 160, 1080, 460
    S = Canvas(wx1 - wx0, wy1 - wy0)
    S.rgb[:] = sky(wx1 - wx0, wy1 - wy0, 'storm', seed=4, horizon=0.9, blotch=0.2)
    S.a[:] = 1
    flakes(S, 50, 2, 1.6, 3.4, color=(0.96, 0.98, 1), op=0.95, sparkle=0)
    L.over(wy0, wy1, wx0, wx1, S.rgb, S.a)
    outline(L, rect(wx0, wy0, wx1, wy1), 9, 0.95, 5, col=hexc('#3a466a'))
    ink(L, [((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], w0=7, color=hexc('#3a466a'), op=0.95, seed=6, wob=0.3)
    wash(L, rect(wx0 - 24, wy1, wx1 + 24, wy1 + 18), hexc('#aab6d2'), op=1.0, wob=0.6, seed=7, smooth=0)
    # 窗帘（冷色格子布）
    for side, (x0, x1) in enumerate([(wx0 - 110, wx0 - 6), (wx1 + 6, wx1 + 110)]):
        for k in range(4):
            xa = x0 + (x1 - x0) * k / 4
            wash(L, rect(xa, wy0 - 20, xa + (x1 - x0) / 4, wy1 + 140), hexc('#7d8fb8') * (0.9 + 0.1 * (k % 2)), op=1.0, wob=1.0, seed=10 + side * 5 + k, smooth=0, tex_k=0.1)
    # 左边：小炉子（蓝白色的小火苗，冷色）+ 水槽台面
    wash(L, rect(120, 560, 520, 800), hexc('#8795b4'), op=1.0, wob=1.0, seed=20, smooth=0, tex_k=0.14)
    outline(L, rect(120, 560, 520, 800), 1.8, 0.85, 21)
    wash(L, rect(110, 540, 530, 570), hexc('#c6d0e6'), op=1.0, wob=0.8, seed=22, smooth=0, tex_k=0.08)
    stove = rect(250, 600, 420, 780)
    wash(L, stove, hexc('#3f4b6b'), op=1.0, wob=0.8, seed=23, smooth=0, tex_k=0.14)
    outline(L, stove, 2.0, 0.9, 24)
    wash(L, rect(276, 640, 394, 740), hexc('#1a2547'), op=1.0, wob=0.5, seed=25, smooth=0)
    glow(L, 335, 700, 150, hexc('#cfe3ff'), 0.6, 1.6)
    wash(L, np.array([[318, 740], [326, 690], [336, 716], [346, 684], [354, 740]], F), hexc('#dcebff'), op=0.95, wob=0.4, seed=26, smooth=2)
    ink(L, [(335, 600), (335, 480), (370, 440)], w0=18, color=hexc('#3f4b6b'), op=0.95, seed=27, wob=0.6, taper=0.02)
    # 右边：上下铺（两层）+ 被子
    for k, yy in enumerate((520, 700)):
        wash(L, rect(1350, yy, 1900, yy + 60), hexc('#8795b4'), op=1.0, wob=1.0, seed=30 + k, smooth=0, tex_k=0.14)
        outline(L, rect(1350, yy, 1900, yy + 60), 1.8, 0.85, 40 + k)
        wash(L, rect(1360, yy - 36, 1540, yy + 2), hexc('#d7e1f3'), op=1.0, wob=1.2, seed=50 + k, smooth=1, tex_k=0.08)   # 枕头
        wash(L, rect(1500, yy - 26, 1890, yy + 6), hexc(['#a9bde6', '#8fa8da'][k]), op=1.0, wob=1.6, seed=60 + k, smooth=1, tex_k=0.1)  # 被子
    for lx in (1350, 1890):
        ink(L, [(lx, 460), (lx, 800)], w0=10, color=hexc('#4a5778'), op=0.95, seed=lx, wob=0.5)
    # 小桌子 + 热巧克力（冷色的杯子，白色的雾气）
    wash(L, rect(620, 690, 1100, 716), hexc('#aab6d2'), op=1.0, wob=0.8, seed=70, smooth=0, tex_k=0.1)
    outline(L, rect(620, 690, 1100, 716), 1.6, 0.8, 71)
    ink(L, [(700, 716), (700, 800)], w0=10, color=hexc('#4a5778'), op=0.95, seed=72, wob=0.4)
    ink(L, [(1020, 716), (1020, 800)], w0=10, color=hexc('#4a5778'), op=0.95, seed=73, wob=0.4)
    for k, mx in enumerate((800, 900, 1000)):
        wash(L, rect(mx - 22, 650, mx + 22, 690), hexc(['#eef2fa', '#c4d0ea', '#eef2fa'][k]), op=1.0, wob=0.5, seed=80 + k, smooth=0)
        outline(L, rect(mx - 22, 650, mx + 22, 690), 1.3, 0.8, 85 + k)
        ink(L, [(mx - 4, 640), (mx - 10, 612), (mx, 590)], w0=2.4, color=hexc('#f4f7fd'), op=0.8, seed=90 + k, wob=0.8, taper=0.5)
    # 墙上：一块小黑板似的告示板 + 一只挂钟
    wash(L, rect(1180, 190, 1300, 300), hexc('#c4d0ea'), op=1.0, wob=0.6, seed=100, smooth=0)
    outline(L, rect(1180, 190, 1300, 300), 3, 0.8, 101, col=hexc('#4a5778'))
    glow(L, 400, 700, 520, hexc('#dbe8ff'), 0.16, 1.6)
    grade(L, 'dusk')
    return L


# ───────────── 第十四章：梦里的海边（夏天）─────────────
def dream():
    L = new('morning', 0.62, seed=61, blotch=0.15)
    hz = 480
    # 淡淡的云 + 很白的太阳（不是暖色）
    glow(L, 1500, 190, 260, hexc('#ffffff'), 0.55, 1.6)
    dots(L, [(1500, 190, 46)], hexc('#ffffff'), 0.95)
    sea(L, hz, 760, seed=62, tone='grey', strokes=420)
    L.rgb[hz:760] = np.clip(L.rgb[hz:760] * np.array([0.82, 1.08, 1.18], F), 0, 1)   # 梦里的海，青蓝色
    r = np.random.default_rng(6)
    for i in range(30):
        y = hz + 20 + r.random() ** 1.3 * 240
        x = r.uniform(0, BW)
        ink(L, [(x, y), (x + r.uniform(40, 120), y)], w0=2.0, color=hexc('#f4f9ff'), op=0.55, seed=i + 700, wob=0.6, taper=0.5)
    # 海上的船：帆船、划艇、渡轮、大油轮（全是白/蓝的）
    boat(L, 520, 600, 1.1, lit=False, seed=71, hull='#eef2fa', stripe='#6f84b5')
    boat(L, 1020, 560, 0.7, lit=False, seed=72, hull='#6f84b5', stripe='#eef2fa', flag=True)
    boat(L, 1380, 640, 0.9, lit=False, seed=73, hull='#dfe7f6', stripe='#8da2d0')
    wash(L, np.array([[1620, 560], [1840, 560], [1810, 590], [1650, 590]], F), hexc('#4a5778'), op=1.0, wob=0.8, seed=74, smooth=0)   # 远处的油轮
    wash(L, rect(1680, 530, 1760, 560), hexc('#eef2fa'), op=1.0, wob=0.5, seed=75, smooth=0)
    # 沙滩：淡蓝的白沙
    sand = np.array([[-300, 760], [-40, 760], [500, 750], [1000, 770], [1500, 755], [1960, 765], [2300, 760], [2300, 1400], [-300, 1400]], F)
    wash(L, sand, hexc('#e6edf8'), op=1.0, wob=3, seed=76, smooth=2, tex_k=0.1, rim=0.12)
    wash(L, sand + [0, 40], hexc('#d3deef'), op=0.4, wob=3, seed=77, smooth=2, tex_k=0.1)
    ink(L, catmull(sand[1:7], 8), w0=3, color=hexc('#f4f9ff'), op=0.9, seed=78, wob=2.0, taper=0.05)
    # 阳伞（蓝白条纹）、沙堡、风筝（不是鸟）
    for i, (ux, uy) in enumerate([(300, 840), (1620, 870)]):
        ink(L, [(ux, uy), (ux + 6, uy - 150)], w0=6, color=hexc('#4a5778'), op=0.95, seed=80 + i, wob=0.4)
        for k in range(6):
            a0 = math.pi + k * math.pi / 6
            a1 = a0 + math.pi / 6
            pts = np.array([[ux + 6, uy - 150], [ux + 6 + math.cos(a0) * 130, uy - 150 + math.sin(a0) * 60], [ux + 6 + math.cos(a1) * 130, uy - 150 + math.sin(a1) * 60]], F)
            wash(L, pts, hexc(['#6f84b5', '#eef2fa'][k % 2]), op=1.0, wob=0.5, seed=90 + i * 6 + k, smooth=0)
        outline(L, np.array([[ux - 124, uy - 150], [ux + 6, uy - 210], [ux + 136, uy - 150]], F), 1.4, 0.8, 100 + i)
    for i, (sx, sy, sw) in enumerate([(780, 930, 120), (900, 950, 90), (1180, 940, 130)]):
        wash(L, np.array([[sx - sw / 2, sy], [sx - sw * 0.4, sy - sw * 0.5], [sx + sw * 0.4, sy - sw * 0.5], [sx + sw / 2, sy]], F), hexc('#cad6ea'), op=1.0, wob=1.0, seed=110 + i, smooth=1, tex_k=0.1)
        for t in range(3):
            wash(L, rect(sx - sw * 0.46 + t * sw * 0.3, sy - sw * 0.66, sx - sw * 0.46 + t * sw * 0.3 + 18, sy - sw * 0.5), hexc('#cad6ea'), op=1.0, wob=0.4, seed=120 + i * 3 + t, smooth=0)
        outline(L, np.array([[sx - sw / 2, sy], [sx - sw * 0.4, sy - sw * 0.5], [sx + sw * 0.4, sy - sw * 0.5], [sx + sw / 2, sy]], F), 1.2, 0.6, 130 + i)
    for i, (kx, ky) in enumerate([(1120, 230), (1250, 330), (440, 280)]):
        d = np.array([[kx, ky - 40], [kx + 30, ky], [kx, ky + 40], [kx - 30, ky]], F)
        wash(L, d, hexc(['#eef2fa', '#a9bde6', '#d6e0f5'][i]), op=1.0, wob=0.4, seed=140 + i, smooth=0)
        outline(L, d, 1.4, 0.8, 150 + i)
        ink(L, [(kx, ky + 40), (kx + 30, ky + 90), (kx - 10, ky + 150), (kx + 20, ky + 210)], w0=1.4, color=hexc('#4a5778'), op=0.8, seed=160 + i, wob=1.0, taper=0.2)
    # 岩石 + 潮水池
    rocks(L, 140, 1020, 240, 80, seed=170, snow=False)
    rocks(L, 1800, 1040, 260, 90, seed=171, snow=False)
    grade(L, 'dusk') if False else None
    return L


# ───────────── 尾声：春天 ─────────────
def spring():
    L = new('morning', 0.58, seed=71, blotch=0.12)
    hz = 520
    hills(L, ridge_pts(0, BW, hz + 10, 40, 73, 40), hz + 60, hexc('#8fb0b6'), snow=False, seed=73, op=0.95)
    hills(L, ridge_pts(0, BW, hz + 60, 50, 74, 40, slope=0.01), hz + 140, hexc('#7aa3a0'), snow=False, seed=74, op=0.97)
    # 草地：青绿的渐变 + 草笔触
    g = np.array([[-300, hz + 124], [-40, hz + 120], [600, hz + 100], [1300, hz + 118], [1960, hz + 104], [2300, hz + 110], [2300, 1400], [-300, 1400]], F)
    wash(L, g, hexc('#8dbf9a'), op=1.0, wob=3, seed=75, smooth=2, tex_k=0.12, rim=0.1)
    wash(L, g + [0, 90], hexc('#6fa87e'), op=0.5, wob=3, seed=76, smooth=2, tex_k=0.12)
    r = np.random.default_rng(8)
    for i in range(420):
        x, y = r.uniform(0, BW), r.uniform(hz + 130, 1080)
        ln = 8 + (y - hz) / 18
        ink(L, [(x, y), (x + r.normal(0, 3), y - ln)], w0=1.4, color=hexc(['#4f8f66', '#6fb583', '#9ed1a8'][i % 3]), op=0.7, seed=i + 800, wob=0.3, taper=0.5)
    # 还没化完的雪块
    for sx, sy, sw in [(180, 960, 150), (1700, 900, 120), (1260, 1000, 100)]:
        wash(L, np.array([[sx - sw, sy], [sx - sw * 0.5, sy - 22], [sx + sw * 0.4, sy - 18], [sx + sw, sy + 4], [sx, sy + 20]], F), P['snow'], op=1.0, wob=1.5, seed=int(sx), smooth=2, tex_k=0.06)
    # 开花的树（白色的花，没有暖色）
    def blossom(tx, ty, sc, seed):
        ink(L, [(tx, ty), (tx - 6, ty - 150 * sc), (tx + 10, ty - 240 * sc)], w0=14 * sc, color=hexc('#5b524e'), op=0.95, seed=seed, wob=1.0)
        for k in range(5):
            ink(L, [(tx, ty - 160 * sc), (tx + (k - 2) * 60 * sc, ty - 250 * sc - abs(k - 2) * -10)], w0=6 * sc, color=hexc('#5b524e'), op=0.9, seed=seed + k, wob=1.0)
        rr = np.random.default_rng(seed)
        for k in range(150):
            a = rr.uniform(0, 6.28); d = rr.uniform(0, 1) ** 0.6 * 150 * sc
            dots(L, [(tx + math.cos(a) * d * 1.3, ty - 280 * sc + math.sin(a) * d * 0.75, rr.uniform(6, 13) * sc)], hexc(['#f6f8ff', '#e7ecfa', '#d9e0f6'][k % 3]), 0.9, soft=1.2)
    blossom(300, 760, 1.2, 800)
    blossom(1560, 740, 1.0, 900)
    # 池塘（有青蛙）+ 紫色的花
    pond = np.array([[1000 + math.cos(a) * 190, 900 + math.sin(a) * 52] for a in np.linspace(0, 6.28, 20, endpoint=False)], F)
    wash(L, pond, hexc('#9fc2e0'), op=1.0, wob=1.5, seed=77, smooth=2, tex_k=0.08, rim=0.2)
    ink(L, np.vstack([pond, pond[:1]]), w0=2, color=hexc('#4f8f66'), op=0.8, seed=78, wob=1.0, taper=0.1, smooth=False)
    wash(L, np.array([[1060 + math.cos(a) * 20, 892 + math.sin(a) * 12] for a in np.linspace(0, 6.28, 10, endpoint=False)], F), hexc('#5fa56e'), op=1.0, wob=0.4, seed=79, smooth=2)
    dots(L, [(1054, 884, 4), (1066, 884, 4)], hexc('#f4f9ff'), 1.0)
    dots(L, [(1054, 884, 1.8), (1066, 884, 1.8)], hexc('#1d2447'), 1.0)
    for i, (fx, fy) in enumerate([(560, 1000), (640, 1030), (1380, 1010), (1450, 990), (760, 960), (1800, 1040)]):
        for k in range(5):
            a = k * 2 * math.pi / 5
            dots(L, [(fx + math.cos(a) * 9, fy - 20 + math.sin(a) * 9, 7)], hexc('#b9a7e6'), 0.95, soft=1.0)
        dots(L, [(fx, fy - 20, 5)], hexc('#f1eefc'), 1.0)
        ink(L, [(fx, fy - 12), (fx + 2, fy + 18)], w0=2.0, color=hexc('#4f8f66'), op=0.9, seed=i + 950, wob=0.3, taper=0.3)
    # 刺猬的小木屋（花园里，有稻草铺的床）
    hx, hy = 560, 880
    wash(L, rect(hx - 90, hy - 80, hx + 90, hy), hexc('#9ca7c2'), op=1.0, wob=1.0, seed=300, smooth=0, tex_k=0.16)
    outline(L, rect(hx - 90, hy - 80, hx + 90, hy), 1.8, 0.85, 301)
    wash(L, np.array([[hx - 110, hy - 76], [hx, hy - 150], [hx + 110, hy - 76]], F), hexc('#566480'), op=1.0, wob=0.8, seed=302, smooth=0, tex_k=0.15)
    outline(L, np.array([[hx - 110, hy - 76], [hx, hy - 150], [hx + 110, hy - 76]], F), 1.8, 0.85, 303)
    wash(L, np.array([[hx - 34, hy], [hx - 34, hy - 44], [hx, hy - 62], [hx + 34, hy - 44], [hx + 34, hy]], F), hexc('#202a4a'), op=1.0, wob=0.5, seed=304, smooth=1)
    for k in range(10):
        ink(L, [(hx - 28 + k * 6, hy - 4), (hx - 30 + k * 6 + r.normal(0, 4), hy - 18 - r.uniform(0, 14))], w0=1.6, color=hexc('#d6d1a8') if False else hexc('#cdd6b0'), op=0.9, seed=310 + k, wob=0.4, taper=0.4)
    return L


if __name__ == '__main__':
    names = sys.argv[1:] or ['city', 'castle', 'castle_in', 'fairground', 'caravan', 'dream', 'spring']
    for n in names:
        fn = globals()[n]
        L = fn()
        save_pair(f'book_{n}', L, None)
        print(n)
