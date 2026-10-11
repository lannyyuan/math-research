"""场景 10：圣诞节早上的客厅（天光明亮，没有暖色的灯）和 夜里 Hazel 的卧室（窗外远处灯塔在转）。"""
from common import *
from bg_workshop import cog

WW = 2400
LF = 790   # 墙和地板的交界


def wallpaper(L, y1, col, seed):
    wash(L, rect(0, 0, WW, y1), hexc(col), op=1.0, wob=0.5, seed=seed, smooth=0, tex_k=0.05)
    r = np.random.default_rng(seed)
    for x in range(40, WW, 120):   # 淡淡的竖条纹
        ink(L, [(x, 0), (x + r.normal(0, 1.5), y1)], w0=2.0, color=hexc(col) * 0.88, op=0.28, seed=seed + x, wob=0.5, taper=0.02)
    for x in range(100, WW, 240):  # 小小的雪花花纹
        for y in range(100, y1 - 150, 200):
            for a in range(3):
                ang = a * math.pi / 3
                ink(L, [(x - math.cos(ang) * 9, y - math.sin(ang) * 9), (x + math.cos(ang) * 9, y + math.sin(ang) * 9)], w0=1.4, color=hexc(col) * 0.82, op=0.35, seed=seed + x + y + a, wob=0.1, taper=0.3)


def wainscot(L, y0, y1, col, seed):
    wash(L, rect(0, y0, WW, y1), hexc(col), op=1.0, wob=0.6, seed=seed, smooth=0, tex_k=0.05)
    for x in range(0, WW, 200):
        outline(L, rect(x + 14, y0 + 30, x + 186, y1 - 14), 1.2, 0.35, seed + x)
    ink(L, [(0, y0), (WW, y0)], w0=3, color=INK, op=0.55, seed=seed + 1, wob=0.8)
    ink(L, [(0, y0 + 14), (WW, y0 + 14)], w0=2, color=INK, op=0.3, seed=seed + 2, wob=0.8)


def curtain(L, x0, x1, y0, y1, col, seed, side='l'):
    r = np.random.default_rng(seed)
    n = 5
    for k in range(n):
        xa = x0 + (x1 - x0) * k / n
        xb = x0 + (x1 - x0) * (k + 1) / n
        pts = np.array([[xa, y0], [xb, y0], [xb + (6 if side == 'l' else -6) * (k + 1), y1], [xa + (6 if side == 'l' else -6) * k, y1]], F)
        wash(L, pts, hexc(col) * (0.88 + 0.12 * (k % 2)), op=1.0, wob=1.0, seed=seed + k, smooth=1, tex_k=0.1)
    ink(L, [(x0, y0), (x1, y0)], w0=6, color=hexc('#445273'), op=0.9, seed=seed + 20, wob=0.4)


def present(L, x, y, w, h, col, rib, seed):
    wash(L, rect(x - w / 2, y - h, x + w / 2, y), hexc(col), op=1.0, wob=0.8, seed=seed, smooth=0, tex_k=0.12)
    outline(L, rect(x - w / 2, y - h, x + w / 2, y), 1.4, 0.7, seed + 1)
    wash(L, rect(x - 6, y - h, x + 6, y), hexc(rib), op=1.0, wob=0.4, seed=seed + 2, smooth=0)
    wash(L, rect(x - w / 2, y - h * 0.55 - 6, x + w / 2, y - h * 0.55 + 6), hexc(rib), op=1.0, wob=0.4, seed=seed + 3, smooth=0)
    ink(L, [(x, y - h), (x - 22, y - h - 22), (x - 6, y - h - 4)], w0=3.2, color=hexc(rib), op=1.0, seed=seed + 4, wob=0.3)
    ink(L, [(x, y - h), (x + 22, y - h - 22), (x + 6, y - h - 4)], w0=3.2, color=hexc(rib), op=1.0, seed=seed + 5, wob=0.3)


def star(L, x, y, r, col, seed):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    wash(L, np.array(pts, F), hexc(col), op=1.0, wob=0.4, seed=seed, smooth=0, tex_k=0.08)
    outline(L, pts, 1.2, 0.6, seed + 1)


def tree(L, x, y, h, seed):
    r = np.random.default_rng(seed)
    wash(L, rect(x - 18, y - 60, x + 18, y), hexc('#4b4650'), op=1.0, wob=0.8, seed=seed, smooth=0)
    layers = 6
    for i in range(layers):
        t = i / layers
        yy = y - h * (0.12 + 0.74 * t)
        ww = h * 0.36 * (1 - t * 0.74)
        hh = h * 0.24
        tri = np.array([[x - ww, yy], [x - ww * 0.5, yy - hh * 0.55], [x, yy - hh], [x + ww * 0.5, yy - hh * 0.55], [x + ww, yy], [x, yy + hh * 0.1]], F)
        wash(L, tri, rgbmix(hexc('#2b5658'), hexc('#3b6c6a'), r.random()), op=1.0, wob=2.0, seed=int(r.integers(1e6)), smooth=1, tex_k=0.2)
        ink(L, np.vstack([tri, tri[:1]]), w0=1.4, color=INK, op=0.5, seed=int(r.integers(1e6)), wob=0.8, taper=0.2)
    # 挂饰：星形、心形、菱形、月牙、半圆、五边形——只用银白和淡蓝（没有暖色）
    cols = ['#f4f7fd', '#a9c2ea', '#d6e0f5', '#8fb0e2', '#ffffff', '#c3d3ee']
    for i in range(14):
        t = r.uniform(0.1, 0.8)
        yy = y - h * (0.12 + 0.74 * t) + r.uniform(-30, 10)
        ww = h * 0.36 * (1 - t * 0.74)
        xx = x + r.uniform(-0.65, 0.65) * ww
        c = cols[i % len(cols)]
        k = i % 6
        if k == 0:
            star(L, xx, yy, 14, c, 300 + i)
        elif k == 1:   # 心
            pts = [(xx, yy + 12), (xx - 13, yy - 2), (xx - 8, yy - 12), (xx, yy - 6), (xx + 8, yy - 12), (xx + 13, yy - 2)]
            wash(L, np.array(pts, F), hexc(c), op=1.0, wob=0.4, seed=300 + i, smooth=2, tex_k=0.08)
            outline(L, pts, 1.1, 0.5, 340 + i)
        elif k == 2:   # 菱形
            pts = [(xx, yy - 14), (xx + 10, yy), (xx, yy + 14), (xx - 10, yy)]
            wash(L, np.array(pts, F), hexc(c), op=1.0, wob=0.3, seed=300 + i, smooth=0)
            outline(L, pts, 1.1, 0.5, 340 + i)
        elif k == 3:   # 月牙
            dots(L, [(xx, yy, 12)], hexc(c), 1.0)
            dots(L, [(xx + 6, yy - 3, 10)], hexc('#2f5a5d'), 1.0)
        elif k == 4:   # 半圆
            pts = [(xx + math.cos(a) * 13, yy + math.sin(a) * 13) for a in np.linspace(0, math.pi, 8)]
            wash(L, np.array(pts, F), hexc(c), op=1.0, wob=0.3, seed=300 + i, smooth=1)
            outline(L, pts, 1.1, 0.5, 340 + i)
        else:          # 五边形
            pts = [(xx + math.cos(-math.pi / 2 + j * 2 * math.pi / 5) * 12, yy + math.sin(-math.pi / 2 + j * 2 * math.pi / 5) * 12) for j in range(5)]
            wash(L, np.array(pts, F), hexc(c), op=1.0, wob=0.3, seed=300 + i, smooth=0)
            outline(L, pts, 1.1, 0.5, 340 + i)
    star(L, x, y - h - 4, 30, '#f2f6ff', 399)
    # 树上的雪的反光
    dots(L, [(x, y - h - 4, 5)], hexc('#ffffff'), 0.9)


def living_far():
    L = Canvas(WW, H)
    wallpaper(L, LF - 120, '#c1cbe0', 1)
    wainscot(L, LF - 120, LF, '#e9eef7', 2)
    planks(L, 0, LF, WW, H, seed=3, col='#8f98b3', gap=58, hor=True)
    # 窗：明亮的蓝天 + 积雪的窗台（阳光照在雪上，白里带淡蓝）
    wx0, wy0, wx1, wy1 = 200, 110, 700, 560
    wash(L, rect(wx0, wy0, wx1, wy1), hexc('#cfe0f6'), op=1.0, wob=0.4, seed=5, smooth=0)
    sk = sky(wx1 - wx0, wy1 - wy0, 'morning', seed=3, horizon=0.95, blotch=0.15)
    L.over(wy0, wy1, wx0, wx1, sk, np.ones((wy1 - wy0, wx1 - wx0), F))
    hills(L, ridge_pts(wx0, wx1, wy1 - 70, 24, 7, 20), wy1, hexc('#a7bce0'), snow=True, seed=7, op=1.0)
    wash(L, rect(wx0, wy1 - 70, wx1, wy1), P['snow'], op=0.95, wob=2.0, seed=8, smooth=0, tex_k=0.05)
    for k, (a, b) in enumerate([((wx0, wy0), (wx1, wy0)), ((wx1, wy0), (wx1, wy1)), ((wx1, wy1), (wx0, wy1)), ((wx0, wy1), (wx0, wy0))]):
        ink(L, [a, b], w0=12, color=hexc('#e5ebf6'), op=1.0, seed=10 + k, wob=0.5, taper=0.02)
        ink(L, [a, b], w0=2, color=INK, op=0.55, seed=20 + k, wob=0.5, taper=0.02)
    ink(L, [((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], w0=10, color=hexc('#e5ebf6'), op=1.0, seed=30, wob=0.4)
    ink(L, [(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], w0=10, color=hexc('#e5ebf6'), op=1.0, seed=31, wob=0.4)
    curtain(L, wx0 - 90, wx0 - 6, wy0 - 30, wy1 + 90, '#7d8fb8', 40)
    curtain(L, wx1 + 6, wx1 + 90, wy0 - 30, wy1 + 90, '#7d8fb8', 50, side='r')
    wash(L, rect(wx0 - 30, wy1, wx1 + 30, wy1 + 20), hexc('#e5ebf6'), op=1.0, wob=0.6, seed=60, smooth=0)
    outline(L, rect(wx0 - 30, wy1, wx1 + 30, wy1 + 20), 1.4, 0.6, 61)
    glow(L, 450, 880, 420, hexc('#f2f7ff'), 0.22, 1.7)
    # 墙上的画框：一幅小小的灯塔画
    wash(L, rect(1030, 160, 1230, 340), hexc('#e8eef8'), op=1.0, wob=0.6, seed=70, smooth=0)
    outline(L, rect(1030, 160, 1230, 340), 4, 0.8, 71, col=hexc('#445273'))
    sk2 = sky(180, 160, 'dusk', seed=3, horizon=0.8, blotch=0.2)
    L.over(170, 330, 1040, 1220, sk2, np.ones((160, 180), F))
    lighthouse(L, 1180, 316, 90, lit=False, seed=71, cottage=False)
    # 圣诞树 + 树下的礼物（形状各异：方的、锥的、金字塔、椭圆……全用银白淡蓝色的纸）
    tree(L, 1950, 840, 640, 5)
    present(L, 1780, 850, 110, 80, '#a9c2ea', '#f4f7fd', 80)
    present(L, 1900, 856, 90, 60, '#f4f7fd', '#8fb0e2', 90)
    present(L, 2020, 856, 130, 70, '#c3d3ee', '#ffffff', 100)
    present(L, 2150, 852, 80, 96, '#8fb0e2', '#e9f0fb', 110)
    grade(L, 'dusk')
    return L


def living_near():
    L = Canvas(WW, H)
    # 圆桌（在 Bolts 和人的前面不遮挡：桌子本身在 far 之后、角色之前；这里只画桌子的前沿和桌布垂边，角色站在桌后）
    return L


WIN = (1560, 130, 2060, 560)   # 卧室的窗（世界坐标）


def bed_far():
    L = Canvas(WW, H)
    wallpaper(L, LF - 40, '#34436e', 1)
    planks(L, 0, LF - 40, WW, H, seed=3, col='#303c5f', gap=58, hor=True)
    # 窗：夜里的海湾，远处灯塔（暖色的灯在转，光柱由 Remotion 叠）
    wx0, wy0, wx1, wy1 = WIN
    ww, wh = wx1 - wx0, wy1 - wy0
    C = Canvas(ww, wh)
    C.rgb[:] = sky(ww, wh, 'night', seed=13, horizon=0.76, blotch=0.35)
    C.a[:] = 1
    r = np.random.default_rng(3)
    for i in range(30):
        dots(C, [(r.uniform(6, ww - 6), r.uniform(6, 250), r.uniform(1.1, 2.2))], hexc('#dce6fa'), r.uniform(0.5, 0.95))
    hz = 320
    sea(C, hz, wh, seed=23, tone='night', strokes=60)
    lighthouse(C, 380, hz + 6, 110, lit=False, seed=33, cottage=False)
    L.over(wy0, wy1, wx0, wx1, C.rgb, C.a)
    for k, (a_, b_) in enumerate([((wx0, wy0), (wx1, wy0)), ((wx1, wy0), (wx1, wy1)), ((wx1, wy1), (wx0, wy1)), ((wx0, wy1), (wx0, wy0))]):
        ink(L, [a_, b_], w0=14, color=hexc('#1c2749'), op=1.0, seed=10 + k, wob=0.5, taper=0.02)
    ink(L, [((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], w0=10, color=hexc('#1c2749'), op=1.0, seed=30, wob=0.4)
    ink(L, [(wx0, wy0 + 250), (wx1, wy0 + 250)], w0=10, color=hexc('#1c2749'), op=1.0, seed=31, wob=0.4)
    curtain(L, wx0 - 100, wx0 - 6, wy0 - 30, wy1 + 120, '#3d4c7c', 40)
    curtain(L, wx1 + 6, wx1 + 100, wy0 - 30, wy1 + 120, '#3d4c7c', 50, side='r')
    wash(L, rect(wx0 - 30, wy1, wx1 + 30, wy1 + 20), hexc('#4a5a88'), op=1.0, wob=0.6, seed=60, smooth=0)
    # 门（左边）：走廊的冷白光从门里透出来，Mum 站在门口
    dx0, dx1, dy0 = 90, 330, 230
    wash(L, rect(dx0, dy0, dx1, LF - 40), hexc('#d9e4f6'), op=1.0, wob=0.6, seed=65, smooth=0, tex_k=0.05)
    outline(L, rect(dx0, dy0, dx1, LF - 40), 5, 0.85, 66, col=hexc('#222d52'))
    # 墙上的小书架
    wash(L, rect(1110, 330, 1510, 350), hexc('#455585'), op=1.0, wob=0.6, seed=70, smooth=0, tex_k=0.12)
    for i, (bw, bh) in enumerate([(30, 80), (24, 100), (34, 70), (28, 92), (26, 84), (36, 76)]):
        bx = 1140 + i * 40
        wash(L, rect(bx, 330 - bh, bx + bw, 330), hexc(['#6e82b4', '#8b9dc8', '#566a9c', '#a1b2d8', '#7a8ec0', '#5d71a4'][i]), op=1.0, wob=0.5, seed=80 + i, smooth=0, tex_k=0.1)
        outline(L, rect(bx, 330 - bh, bx + bw, 330), 1.1, 0.6, 90 + i)
    # 床头板 + 枕头（Hazel 坐在床上，靠着枕头；被子在前景层里盖住她的下半身）
    hb = np.array([[560, 700], [560, 420], [600, 360], [1020, 360], [1060, 420], [1060, 700]], F)
    hb2 = np.array([[540, 740], [540, 400], [590, 330], [1030, 330], [1080, 400], [1080, 740]], F)
    wash(L, hb2, hexc('#46568a'), op=1.0, wob=1.2, seed=100, smooth=2, tex_k=0.12)
    outline(L, hb2, 1.8, 0.8, 101)
    wash(L, np.array([[620, 600], [700, 520], [900, 510], [990, 540], [1000, 640], [640, 650]], F), hexc('#cbd7f0'), op=1.0, wob=1.5, seed=103, smooth=2, tex_k=0.08)
    outline(L, np.array([[620, 600], [700, 520], [900, 510], [990, 540], [1000, 640], [640, 650]], F), 1.4, 0.6, 104)
    # 床头柜（右边）+ 台灯：灯罩是冷白的
    tx = 1330
    wash(L, rect(tx - 100, 700, tx + 100, LF + 80), hexc('#455585'), op=1.0, wob=1.0, seed=110, smooth=0, tex_k=0.14)
    outline(L, rect(tx - 100, 700, tx + 100, LF + 80), 1.6, 0.8, 111)
    wash(L, rect(tx - 84, 750, tx + 84, 790), hexc('#52639a'), op=1.0, wob=0.6, seed=112, smooth=0)
    dots(L, [(tx, 770, 5)], hexc('#aab9d8'), 1.0)
    wash(L, rect(tx - 14, 600, tx + 14, 700), hexc('#3a4a7a'), op=1.0, wob=0.5, seed=113, smooth=0)
    shade = np.array([[tx - 60, 600], [tx + 60, 600], [tx + 34, 520], [tx - 34, 520]], F)
    wash(L, shade, hexc('#eaf1fc'), op=1.0, wob=0.6, seed=114, smooth=0, tex_k=0.06)
    outline(L, shade, 1.5, 0.7, 115)
    grade(L, 'dusk')
    return L


def bed_near():
    """前景：盖在 Hazel 腿上的被子（淡蓝，绗缝的小格子）。"""
    L = Canvas(WW, H)
    quilt = np.array([[500, 760], [540, 690], [700, 676], [900, 672], [1080, 680], [1120, 700], [1140, 800], [1160, 900], [1100, 960], [560, 962], [480, 900]], F)
    wash(L, quilt, hexc('#8fa2cf'), op=1.0, wob=2.5, seed=120, smooth=2, tex_k=0.1, rim=0.2)
    wash(L, np.array([[540, 700], [1100, 700], [1130, 760], [520, 760]], F), hexc('#b2c2e6'), op=0.7, wob=2.5, seed=121, smooth=2, tex_k=0.08)
    for i in range(7):   # 绗缝的格子
        ink(L, [(520 + i * 95, 690), (505 + i * 100, 950)], w0=1.6, color=hexc('#5b6fa8'), op=0.45, seed=130 + i, wob=1.0, taper=0.2)
    for j in range(4):
        ink(L, [(500, 740 + j * 60), (1140, 742 + j * 62)], w0=1.6, color=hexc('#5b6fa8'), op=0.45, seed=140 + j, wob=1.0, taper=0.2)
    ink(L, np.vstack([quilt, quilt[:1]]), w0=2.2, color=INK, op=0.7, seed=150, wob=1.5, taper=0.1)
    grade(L, 'dusk')
    return L


def shift_cols(L, x0, dx):
    """把 x0 右边的内容整体向左挪 dx 像素（右边缺的部分用最右侧的列补）：让门和窗之间的距离小于一屏宽。"""
    for arr in (L.rgb, L.a):
        tail = arr[:, -dx:].copy()
        arr[:, x0:-dx] = arr[:, x0 + dx:].copy()
        arr[:, -dx:] = tail
    return L


if __name__ == '__main__':
    save_pair('living', living_far(), living_near())
    save_pair('bed', shift_cols(bed_far(), 330, 100), shift_cols(bed_near(), 330, 100))
    print('ok')
