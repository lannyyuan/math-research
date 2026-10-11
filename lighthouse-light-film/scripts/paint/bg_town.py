"""场景 4：城里的车站（公交站牌 + 火车站，都停了），以及走回村子的雪路（原野 / 农场）。傍晚，下着雪，没有一盏暖色的灯。"""
from common import *

# 牌子的位置（世界坐标 x, y, w, h）：Remotion 在上面叠英文字
SIGN_BUS = (1110, 560, 340, 150)
SIGN_TRAIN = (2010, 520, 300, 120)


def sign_board(L, x, y, w, h, seed, post_h=300):
    ink(L, [(x + w / 2, y + h), (x + w / 2, y + h + post_h)], w0=9, color=hexc('#3a4668'), op=0.95, seed=seed, wob=0.6)
    wash(L, rect(x, y, x + w, y + h), hexc('#f2f4fa'), op=1.0, wob=1.0, seed=seed + 1, smooth=0, tex_k=0.05, rim=0.12)
    wash(L, rect(x + 5, y + 5, x + w - 5, y + h - 5), hexc('#f7f9fd'), op=1.0, wob=0.6, seed=seed + 2, smooth=0, tex_k=0.04)
    outline(L, rect(x, y, x + w, y + h), 3.0, 0.9, seed + 3)
    # 雪积在牌子的上沿
    cap = np.array([[x - 8, y + 4], [x + w * 0.2, y - 18], [x + w * 0.6, y - 24], [x + w + 8, y - 8], [x + w + 4, y + 8], [x + w * 0.5, y + 4], [x, y + 12]], F)
    wash(L, cap, P['snow'], op=1.0, wob=2.0, seed=seed + 4, smooth=2, tex_k=0.06)
    wash(L, cap + [0, 6], P['snow_sh1'], op=0.35, wob=1.5, seed=seed + 5, smooth=2)


def lamp_post(L, x, y, h, seed):
    """路灯杆：深灰的杆子 + 灯罩 + 帽上的雪（灯是灭的）。"""
    ink(L, [(x, y), (x, y - h)], w0=7, color=hexc('#313c5e'), op=0.95, seed=seed, wob=0.6)
    wash(L, np.array([[x - 20, y - h + 26], [x + 20, y - h + 26], [x + 26, y - h - 14], [x - 26, y - h - 14]], F), hexc('#8b9ab8'), op=0.95, wob=0.8, seed=seed + 1, smooth=0, tex_k=0.12)
    outline(L, np.array([[x - 20, y - h + 26], [x + 20, y - h + 26], [x + 26, y - h - 14], [x - 26, y - h - 14]], F), 1.5, 0.8, seed + 2)
    wash(L, np.array([[x - 32, y - h - 12], [x - 6, y - h - 34], [x + 8, y - h - 34], [x + 32, y - h - 12], [x, y - h - 4]], F), P['snow'], op=1.0, wob=1.0, seed=seed + 3, smooth=2, tex_k=0.06)


def town_far():
    L = Canvas(W, H)
    hz = 520
    L.rgb[:] = sky(W, H, 'dusk', seed=12, horizon=hz / H, blotch=0.3)
    L.a[:] = 1
    hills(L, ridge_pts(0, W, hz + 8, 46, 31, 60), hz + 40, hexc('#8a9dc0'), snow=True, seed=31, op=0.95)
    field(L, hz + 60, 840, seed=33)
    # 远处城里的屋顶：一排排白房子，错落
    r = np.random.default_rng(8)
    for i in range(18):
        hx = 80 + i * 160 + r.normal(0, 22)
        hw, hh = r.uniform(90, 150), r.uniform(60, 110)
        house(L, hx, hz + 90 + r.uniform(-8, 24), hw, hh, 0.5, seed=60 + i, windows=1 + (i % 2), chimney=(i % 3 == 0), door=False, lit=None, wall=['#e6ebf4', '#dfe5f1', '#eaeef6'][i % 3])
    # 教堂尖塔
    wash(L, rect(1300, hz - 60, 1352, hz + 96), hexc('#e1e7f2'), op=1.0, wob=0.8, seed=90, smooth=0, tex_k=0.08)
    outline(L, rect(1300, hz - 60, 1352, hz + 96), 1.5, 0.75, 91)
    wash(L, np.array([[1292, hz - 58], [1326, hz - 170], [1360, hz - 58]], F), hexc('#566480'), op=1.0, wob=0.8, seed=92, smooth=0, tex_k=0.14)
    outline(L, np.array([[1292, hz - 58], [1326, hz - 170], [1360, hz - 58]], F), 1.5, 0.8, 93)
    wash(L, rect(1316, hz - 30, 1336, hz + 10), hexc('#7d8cb0'), op=1.0, wob=0.5, seed=94, smooth=0)
    # 车站这边的铁轨：从右边远处斜着铺过来的两条线 + 枕木
    return L


def town_near():
    L = Canvas(W, H)
    top = np.array([[-60, 800], [600, 796], [1300, 806], [2000, 812], [2950, 806]], F)
    snow_ground(L, catmull(top, 8), 1120, seed=41)
    # 路：中间一条被轧过的灰蓝色带 + 两道车辙
    road = np.array([[-60, 880], [800, 872], [1500, 884], [2300, 890], [2950, 884], [2950, 960], [2300, 968], [1500, 962], [800, 956], [-60, 962]], F)
    wash(L, road, hexc('#c7d2e6'), op=0.55, wob=4, seed=42, smooth=2, tex_k=0.14)
    for k, dy in enumerate((16, 56)):
        pts = np.array([[-60, 880 + dy], [800, 872 + dy], [1500, 884 + dy], [2300, 890 + dy], [2950, 884 + dy]], F)
        ink(L, catmull(pts, 8), w0=3.0, color=P['snow_sh3'], op=0.35, seed=43 + k, wob=2.0, taper=0.05)
    # 公交站：顶棚 + 长椅 + 站牌
    bx = 650
    wash(L, rect(bx - 170, 600, bx + 170, 626), hexc('#5d6c90'), op=1.0, wob=0.8, seed=50, smooth=0, tex_k=0.14)
    outline(L, rect(bx - 170, 600, bx + 170, 626), 1.6, 0.8, 51)
    cap = np.array([[bx - 190, 606], [bx - 120, 570], [bx + 90, 566], [bx + 190, 606], [bx + 120, 610], [bx - 100, 612]], F)
    wash(L, cap, P['snow'], op=1.0, wob=2.0, seed=52, smooth=2, tex_k=0.06)
    wash(L, cap + [0, 8], P['snow_sh1'], op=0.3, wob=1.5, seed=53, smooth=2)
    for lx in (bx - 150, bx + 150):
        ink(L, [(lx, 626), (lx, 830)], w0=8, color=hexc('#3a4668'), op=0.95, seed=54 + int(lx), wob=0.6)
    wash(L, rect(bx - 150, 640, bx + 150, 760), hexc('#c8d4e8'), op=0.5, wob=1.0, seed=56, smooth=0, tex_k=0.06)
    outline(L, rect(bx - 150, 640, bx + 150, 760), 1.4, 0.7, 57)
    wash(L, rect(bx - 130, 770, bx + 130, 790), hexc('#5d6c90'), op=1.0, wob=0.8, seed=58, smooth=0, tex_k=0.14)
    outline(L, rect(bx - 130, 770, bx + 130, 790), 1.4, 0.8, 59)
    for lx in (bx - 110, bx + 110):
        ink(L, [(lx, 790), (lx, 830)], w0=6, color=hexc('#3a4668'), op=0.9, seed=60 + int(lx), wob=0.4)
    wash(L, np.array([[bx - 134, 776], [bx - 40, 758], [bx + 60, 762], [bx + 134, 776], [bx + 110, 780], [bx, 772], [bx - 100, 782]], F), P['snow'], op=1.0, wob=1.5, seed=62, smooth=2, tex_k=0.06)
    sign_board(L, *SIGN_BUS, seed=70, post_h=270)
    # 火车站：长长的白色平房 + 站台 + 关着的栅栏门 + 牌子
    sx = 1800
    house(L, sx, 812, 760, 280, 0.3, seed=80, windows=3, door=True, chimney=True, wall='#e9eef7', roof_col='#4f5c7c')
    # 站台边：一条低矮的石沿
    wash(L, rect(1300, 812, 2400, 840), hexc('#7d8cae'), op=1.0, wob=1.0, seed=81, smooth=0, tex_k=0.14)
    wash(L, np.array([[1296, 812], [2404, 812], [2404, 822], [1296, 822]], F), P['snow'], op=1.0, wob=1.0, seed=82, smooth=1, tex_k=0.05)
    outline(L, rect(1300, 812, 2400, 840), 1.5, 0.75, 83)
    # 栅栏门（关着）
    for gx in range(2420, 2700, 28):
        ink(L, [(gx, 830), (gx, 690)], w0=4, color=hexc('#2f3a5c'), op=0.9, seed=90 + gx % 7, wob=0.3)
    ink(L, [(2420, 720), (2690, 720)], w0=4, color=hexc('#2f3a5c'), op=0.9, seed=100, wob=0.3)
    ink(L, [(2420, 800), (2690, 800)], w0=4, color=hexc('#2f3a5c'), op=0.9, seed=101, wob=0.3)
    wash(L, np.array([[2410, 690], [2700, 690], [2700, 706], [2410, 706]], F), P['snow'], op=1.0, wob=1.0, seed=102, smooth=1, tex_k=0.05)
    sign_board(L, *SIGN_TRAIN, seed=110, post_h=210)
    # 路灯杆（灭的），沿路
    for i, lx in enumerate((200, 1150, 2250)):
        lamp_post(L, lx, 860 + i * 6, 360, 120 + i * 10)
    for i, (bx_, by_) in enumerate([(120, 1040), (1400, 1070), (2700, 1050)]):
        bush(L, bx_, by_, 150, 1.0, 8, seed=420 + i)
    rocks(L, 980, 1050, 240, 80, seed=520)
    return L


def country_far():
    L = Canvas(W, H)
    hz = 500
    L.rgb[:] = sky(W, H, 'dusk', seed=14, horizon=hz / H, blotch=0.3)
    L.a[:] = 1
    hills(L, ridge_pts(0, W, hz + 10, 50, 41, 60), hz + 60, hexc('#8497bb'), snow=True, seed=41, op=0.95)
    hills(L, ridge_pts(0, W, hz + 70, 60, 42, 60, slope=0.012), hz + 160, hexc('#6f84ab'), snow=True, seed=43, op=0.97)
    field(L, hz + 150, 840, seed=45)
    r = np.random.default_rng(12)
    for i in range(16):   # 山脚的松林
        px = r.uniform(80, W - 80)
        tree_pine(L, px, hz + 112 + r.uniform(0, 40), r.uniform(120, 220), seed=300 + i)
    return L


def country_near():
    L = Canvas(W, H)
    top = np.array([[-60, 760], [500, 745], [1100, 775], [1700, 790], [2300, 780], [2950, 770]], F)
    snow_ground(L, catmull(top, 8), 1120, seed=51)
    # 路：一条淡淡的、从左到右的车辙路
    road = np.array([[-60, 850], [700, 842], [1500, 856], [2200, 850], [2950, 840], [2950, 928], [2200, 938], [1500, 944], [700, 930], [-60, 936]], F)
    wash(L, road, hexc('#c7d2e6'), op=0.5, wob=4, seed=52, smooth=2, tex_k=0.14)
    for k, dy in enumerate((16, 62)):
        pts = np.array([[-60, 850 + dy], [700, 842 + dy], [1500, 856 + dy], [2200, 850 + dy], [2950, 840 + dy]], F)
        ink(L, catmull(pts, 8), w0=3.0, color=P['snow_sh3'], op=0.35, seed=53 + k, wob=2.0, taper=0.05)
    # 路边的篱笆桩 + 铁丝（后面）
    for i in range(14):
        px = 80 + i * 210
        py = np.interp(px, top[:, 0], top[:, 1]) + 62
        post(L, px, py, 96 + (i % 3) * 8, 32, seed=600 + i)
        if i:
            wire(L, (px - 210 + 6, py - 94), (px - 6, py - 92), sag=10, seed=630 + i)
    # 光秃秃的大树 + 灌木 + 石头
    for i, (bx_, by_) in enumerate([(300, 760), (1500, 790), (2500, 775)]):
        bush(L, bx_, by_, 260, 1.4, 11, seed=700 + i)
    for i, (bx_, by_) in enumerate([(100, 1050), (1000, 1060), (1900, 1070), (2700, 1050)]):
        bush(L, bx_, by_, 150, 1.0, 8, seed=420 + i)
    rocks(L, 640, 1050, 240, 80, seed=720)
    rocks(L, 2150, 1060, 260, 90, seed=721)
    return L


if __name__ == '__main__':
    save_pair('town', town_far(), town_near())
    save_pair('country', country_far(), country_near())
    print('ok')
