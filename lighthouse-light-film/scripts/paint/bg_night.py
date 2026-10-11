"""场景 9：暴风雪过去的夜里，海湾（灯塔的光柱扫过海面，船沿着光回港）和 码头（爸爸的船靠岸）。
 灯塔灯室、港口的窗和路灯是暖色——这是全片允许的暖色。光柱本身由 Remotion 的 Beam 叠。"""
from common import *

BAY_LH = (2300, 600, 330)       # 灯塔：塔底中点 x, y，塔高
BAY_LANTERN = (2300, 600 - 330 - 0.0 * 330 + 8)   # 灯室中心（光柱的起点）
HARBOUR_Y = 640


def bay_far():
    L = Canvas(W, H)
    hz = 470
    L.rgb[:] = sky(W, H, 'storm', seed=61, horizon=hz / H, blotch=0.4)
    L.a[:] = 1
    r = np.random.default_rng(4)
    # 云缝里露出的几颗星（暴风雪刚刚过去）
    for i in range(46):
        x, y = r.uniform(0, W), r.uniform(10, hz - 120)
        dots(L, [(x, y, r.uniform(1.2, 2.4))], hexc('#dce6fa'), r.uniform(0.5, 0.95))
    sea(L, hz + 8, H, seed=17, tone='night', strokes=640)
    for i in range(36):
        y = hz + 50 + r.random() ** 1.4 * 440
        x = r.uniform(0, W)
        ln = r.uniform(60, 200) * (0.5 + (y - hz) / 420)
        ink(L, [(x, y), (x + ln / 2, y - 2), (x + ln, y + 1)], w0=1.5 + (y - hz) / 150, color=hexc('#c6d5f0'), op=0.28, seed=i + 500, wob=0.8, taper=0.5)
    # 右边的岬角 + 灯塔（夜里，灯室会被 Remotion 点亮）
    rock_base(L, 2260, hz + 150, 1000, 190, seed=21)
    lx, ly, lh = BAY_LH
    lighthouse(L, lx, ly, lh, lit=False, seed=31, cottage=True)
    for i, (px, ph) in enumerate([(1900, 80), (1960, 62), (2040, 74)]):
        tree_pine(L, px, hz + 100, ph * 1.3, seed=40 + i)
    # 左边的港口：几座小房子，窗里亮着暖色的灯；码头上有一盏路灯
    land(L, 60, 940, HARBOUR_Y - 26, HARBOUR_Y + 20, seed=3)
    for i, (hx, hw, hh) in enumerate([(160, 160, 100), (330, 140, 90), (500, 170, 110), (690, 140, 96), (850, 150, 100)]):
        house(L, hx, HARBOUR_Y - 20 + (i % 2) * 6, hw, hh, 0.5, seed=60 + i, windows=2, chimney=(i % 2 == 0), door=True, lit=hexc('#ffd978'))
    # 码头
    pier_y = HARBOUR_Y + 42
    wash(L, rect(60, pier_y - 14, 1180, pier_y + 8), hexc('#5d6c90'), op=1.0, wob=1.5, seed=70, smooth=0, tex_k=0.12)
    outline(L, rect(60, pier_y - 14, 1180, pier_y + 8), 1.6, 0.8, 71)
    for k in range(14):
        post(L, 100 + k * 80, pier_y + 40, 52, 16, seed=80 + k)
    for lx_ in (180, 640, 1100):   # 码头的路灯：暖色
        ink(L, [(lx_, pier_y - 12), (lx_, pier_y - 140)], w0=6, color=hexc('#8fa2c8'), op=0.95, seed=lx_, wob=0.5)
        wash(L, rect(lx_ - 10, pier_y - 162, lx_ + 10, pier_y - 140), hexc('#fff3c4'), op=1.0, wob=0.3, seed=lx_ + 1, smooth=0)
        outline(L, rect(lx_ - 10, pier_y - 162, lx_ + 10, pier_y - 140), 1.4, 0.9, lx_ + 2)
        wash(L, np.array([[lx_ - 14, pier_y - 160], [lx_, pier_y - 176], [lx_ + 14, pier_y - 160]], F), hexc('#8fa2c8'), op=1.0, wob=0.3, seed=lx_ + 3, smooth=0)
        glow(L, lx_, pier_y - 152, 70, WARM['mid'], 0.5, 1.8)
    # 泊着的小船（亮着暖灯）
    for i, (bx, by, bs) in enumerate([(300, 718, 1.0), (760, 724, 0.9), (1010, 716, 0.8)]):
        boat(L, bx, by, bs, lit=True, seed=90 + i, hull=['#2a3a62', '#33436a', '#26335a'][i], flag=(i == 1))
    return L


def bay_near():
    L = Canvas(W, H)
    top = np.array([[-60, 990], [500, 980], [1100, 1000], [1700, 1010], [2300, 1000], [2950, 1010]], F)
    snow_ground(L, catmull(top, 8), 1200, seed=91)
    for i, (bx_, by_) in enumerate([(160, 1070), (1400, 1075), (2650, 1070)]):
        bush(L, bx_, by_, 120, 1.0, 8, seed=420 + i)
    rocks(L, 800, 1075, 240, 70, seed=520)
    grade(L, 'storm')
    return L


# ───────────── 码头 ─────────────
DECK_Y = 880    # 码头甲板的前沿（角色的脚踩在这一带）
WATER_Y = 760


def dock_far():
    L = Canvas(W, H)
    hz = 430
    L.rgb[:] = sky(W, H, 'storm', seed=71, horizon=hz / H, blotch=0.4)
    L.a[:] = 1
    r = np.random.default_rng(4)
    for i in range(36):
        x, y = r.uniform(0, W), r.uniform(10, hz - 100)
        dots(L, [(x, y, r.uniform(1.2, 2.4))], hexc('#dce6fa'), r.uniform(0.5, 0.95))
    sea(L, hz + 8, H, seed=19, tone='night', strokes=520)
    # 远处的灯塔（右边，远远的）：灯室暖色由 Remotion 叠
    rock_base(L, 2350, hz + 120, 700, 130, seed=22)
    lighthouse(L, 2380, hz + 70, 250, lit=False, seed=32, cottage=False)
    # 对岸的房子（窗里的暖光）
    land(L, 220, 740, hz + 78, hz + 112, seed=4)
    land(L, 1420, 1760, hz + 78, hz + 112, seed=5)
    for i, (hx, hw, hh) in enumerate([(300, 130, 80), (460, 120, 74), (620, 140, 84), (1500, 120, 76), (1650, 130, 80)]):
        house(L, hx, hz + 85 + (i % 2) * 6, hw, hh, 0.5, seed=60 + i, windows=2, chimney=(i % 2 == 0), door=False, lit=hexc('#ffd978'))
    return L


def dock_near():
    L = Canvas(W, H)
    # 水面前的码头甲板：宽宽的一条木板，边缘一排粗木桩 + 缆绳 + 一盏暖色路灯
    deck = rect(-40, WATER_Y + 40, W + 40, 1120)
    planks(L, -40, WATER_Y + 40, W + 40, 1120, seed=3, col='#58678c', gap=44, hor=True)
    wash(L, rect(-40, WATER_Y + 30, W + 40, WATER_Y + 62), hexc('#7a89ad'), op=1.0, wob=1.0, seed=4, smooth=0, tex_k=0.1)
    ink(L, [(-40, WATER_Y + 62), (W + 40, WATER_Y + 62)], w0=3, color=INK, op=0.8, seed=5, wob=1.0)
    wash(L, np.array([[-40, WATER_Y + 22], [W + 40, WATER_Y + 22], [W + 40, WATER_Y + 40], [-40, WATER_Y + 40]], F), P['snow'], op=0.95, wob=2.0, seed=6, smooth=1, tex_k=0.06)
    for k in range(12):
        px = 80 + k * 240
        wash(L, rect(px - 18, WATER_Y - 40, px + 18, WATER_Y + 40), hexc('#3a4668'), op=1.0, wob=1.0, seed=10 + k, smooth=1, tex_k=0.16)
        outline(L, rect(px - 18, WATER_Y - 40, px + 18, WATER_Y + 40), 1.4, 0.8, 30 + k)
        wash(L, np.array([[px - 24, WATER_Y - 36], [px - 10, WATER_Y - 54], [px + 12, WATER_Y - 54], [px + 24, WATER_Y - 36], [px, WATER_Y - 30]], F), P['snow'], op=1.0, wob=1.0, seed=50 + k, smooth=2, tex_k=0.06)
    for k in range(11):
        wire(L, (80 + k * 240 + 18, WATER_Y - 30), (80 + (k + 1) * 240 - 18, WATER_Y - 30), sag=24, seed=70 + k)
    # 路灯（暖色）：码头的灯
    lx = 560
    ink(L, [(lx, WATER_Y + 40), (lx, WATER_Y - 330)], w0=8, color=hexc('#2a3552'), op=0.95, seed=90, wob=0.5)
    wash(L, np.array([[lx - 26, WATER_Y - 330], [lx + 26, WATER_Y - 330], [lx + 20, WATER_Y - 392], [lx - 20, WATER_Y - 392]], F), hexc('#fff3c4'), op=1.0, wob=0.4, seed=91, smooth=0)
    outline(L, np.array([[lx - 26, WATER_Y - 330], [lx + 26, WATER_Y - 330], [lx + 20, WATER_Y - 392], [lx - 20, WATER_Y - 392]], F), 1.8, 0.9, 92)
    wash(L, np.array([[lx - 34, WATER_Y - 388], [lx, WATER_Y - 420], [lx + 34, WATER_Y - 388]], F), hexc('#2a3552'), op=1.0, wob=0.4, seed=93, smooth=0)
    glow(L, lx, WATER_Y - 360, 240, WARM['mid'], 0.55, 1.6)
    glow(L, lx, WATER_Y - 360, 90, WARM['core'], 0.55, 1.5)
    for i, (bx_, by_) in enumerate([(120, 1060), (2600, 1060)]):
        bush(L, bx_, by_, 120, 1.0, 8, seed=430 + i)
    grade(L, 'storm')
    return L


if __name__ == '__main__':
    save_pair('bay', bay_far(), bay_near())
    save_pair('dock', dock_far(), dock_near(), w=2900)
    print('ok')
