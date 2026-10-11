"""场景 1、2：海边的小村子（圣诞前夜的早晨，阴天、下雪）。两层：远景（天 + 海 + 岬角 + 暗着的灯塔 + 港口）和近景（雪坡 + 小白房子 + 篱笆）。"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from objects import *
from world import *

OUT = pathlib.Path(__file__).resolve().parents[2] / 'public/bg'
OUT.mkdir(parents=True, exist_ok=True)
W, H = 2900, 1080
HZ = 470


def far():
    L = Canvas(W, H)
    L.rgb[:] = sky(W, H, 'day', seed=2, horizon=HZ / H, blotch=0.3)
    L.a[:] = 1
    # 远山（两层，越远越淡）
    hills(L, ridge_pts(0, W, HZ + 6, 38, 11, 60), HZ + 30, hexc('#9aabc6'), snow=True, seed=11, op=0.9)
    hills(L, ridge_pts(0, 1500, HZ + 14, 28, 12, 40, slope=-0.02), HZ + 50, hexc('#7f93b4'), snow=True, seed=12, op=0.95)
    sea(L, HZ + 20, H, seed=5, tone='grey', strokes=520)
    # 右边的岬角 + 灯塔（白天，灯是暗的）
    rock_base(L, 1850, HZ + 70, 1100, 150, seed=21)
    lighthouse(L, 1900, HZ + 22, 240, lit=False, seed=31)
    for i, (px, ph) in enumerate([(1620, 70), (1680, 55), (1750, 62)]):
        tree_pine(L, px, HZ + 40, ph * 1.2, seed=40 + i)
    # 对岸的小渔村（左边，小小的）
    for i, (hx, hw, hh) in enumerate([(240, 80, 50), (340, 70, 44), (440, 90, 54), (560, 76, 48), (660, 84, 52)]):
        house(L, hx, HZ + 60 + (i % 2) * 6, hw, hh, 0.55, seed=60 + i, windows=1, chimney=(i % 2 == 0), lit=None)
    # 港口：码头 + 几条小船
    pier_y = 688
    for k in range(8):
        post(L, 940 + k * 62, pier_y + 24, 44, 14, seed=70 + k)
    ink(L, [(925, pier_y - 22), (1400, pier_y - 22)], w0=3.0, color=INK, op=0.8, seed=80, wob=1.2)
    wash(L, np.array([[925, pier_y - 22], [1400, pier_y - 22], [1400, pier_y - 8], [925, pier_y - 8]], F), P['snow'], op=1.0, wob=2, seed=81, smooth=0)
    for i, (bx, by, bs) in enumerate([(1100, 735, 0.95), (1260, 750, 0.85), (1480, 725, 0.7), (780, 745, 0.8)]):
        boat(L, bx, by, bs, lit=False, seed=90 + i, hull=['#2a3a62', '#3a4a70', '#26335a', '#33436a'][i], flag=(i == 1))
    # 远处海面上的一条小船：爸爸的船（又小又远）
    boat(L, 1420, 566, 0.3, lit=False, seed=99, hull='#1f3b66', stripe='#e8eef8')
    return L


def near():
    L = Canvas(W, H)
    # 雪坡：从左上缓缓落向右下
    top = np.array([[-50, 790], [300, 780], [700, 800], [1100, 840], [1500, 880], [1900, 925], [2400, 960], [2950, 990]], F)
    snow_ground(L, catmull(top, 10), 1120, seed=5)
    # 小白房子（赫兹的家），在左边的坡上
    house(L, 470, 842, 430, 250, 0.55, seed=200, windows=2, door=True, chimney=True, wall='#eef2f8', roof_col='#566480')
    smoke(L, 565, 600, n=5, seed=201, s=1.0, op=0.45)
    # 篱笆：木桩 + 铁丝，沿坡一路下去
    for i in range(10):
        px = 780 + i * 190
        py = np.interp(px, top[:, 0], top[:, 1]) + 62 + i * 3
        post(L, px, py, 100 + (i % 3) * 8, 34, seed=300 + i)
        if i:
            wire(L, (px - 190 + 6, py - 104 - (i - 1) * 0), (px - 6, py - 98), sag=10, seed=330 + i)
    # 灌木 + 岩石
    for i, (bx, by) in enumerate([(120, 940), (640, 930), (1420, 1010), (2050, 1040), (2650, 1060)]):
        bush(L, bx, by, 150 + (i % 2) * 40, 1.0, 8, seed=400 + i)
    rocks(L, 900, 1040, 260, 90, seed=500)
    rocks(L, 2350, 1070, 280, 100, seed=501)
    return L


if __name__ == '__main__':
    f = far(); f.save(OUT / 's1_far.jpg', jpg=True, q=92)
    n = near(); n.save(OUT / 's1_near.png')
    comp = Canvas(W, H); comp.over(0, H, 0, W, f.rgb, f.a); comp.over(0, H, 0, W, n.rgb, n.a)
    import cv2
    img = (np.clip(comp.flat(), 0, 1) * 255).astype(np.uint8)
    cv2.imwrite('/tmp/claude-0/-home-user-math-research/747091a3-a05e-575b-b1ac-cb27e1adeb12/scratchpad/ref/s1_comp.png', cv2.cvtColor(cv2.resize(img, (1450, 540), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2BGR))
    print('ok')
