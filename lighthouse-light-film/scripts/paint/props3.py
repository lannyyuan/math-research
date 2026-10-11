"""第三批小道具：新灯泡（单个）。"""
import json
from props import *   # noqa


def bulb():
    L = Canvas(160, 220)
    cx, cy, r = 80, 80, 56
    glass = np.array([[cx + math.cos(a) * r, cy + math.sin(a) * r * 1.05] for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)], F)
    wash(L, glass, hexc('#dfeaf8'), op=0.6, wob=0.8, seed=5, smooth=2, tex_k=0.06, rim=0.25, rim_w=4)
    neck = np.array([[cx - 22, cy + 46], [cx + 22, cy + 46], [cx + 18, cy + 84], [cx - 18, cy + 84]], F)
    wash(L, neck, hexc('#dfeaf8'), op=0.6, wob=0.5, seed=6, smooth=1, tex_k=0.06)
    base = np.array([[cx - 24, cy + 84], [cx + 24, cy + 84], [cx + 24, cy + 128], [cx - 24, cy + 128]], F)
    wash(L, base, hexc('#8d9bbd'), op=1.0, wob=0.5, seed=7, smooth=0, tex_k=0.14)
    for k in range(3):
        ink(L, [(cx - 24, cy + 92 + k * 12), (cx + 24, cy + 96 + k * 12)], w0=1.4, color=hexc('#3a4668'), op=0.8, seed=8 + k, wob=0.3)
    outline(L, base, 1.4, 0.85, 12)
    ink(L, np.vstack([glass, glass[:1]]), w0=1.6, color=hexc('#6f86b3'), op=0.8, seed=13, wob=0.6, taper=0.1, smooth=False)
    ink(L, [(cx - 12, cy + 44), (cx - 8, cy + 6), (cx, cy - 12), (cx + 8, cy + 6), (cx + 12, cy + 44)], w0=1.4, color=hexc('#4a5a86'), op=0.8, seed=14, wob=0.3)
    ink(L, [(cx - 30, cy - 36), (cx - 18, cy - 46)], w0=3.0, color=hexc('#ffffff'), op=0.9, seed=15, wob=0.2)
    finish(L, 'bulb')


def table():
    L = Canvas(600, 380)
    cx = 300
    cloth = [[cx - 250, 80], [cx - 262, 330], [cx - 200, 346], [cx - 120, 332], [cx - 40, 348], [cx + 40, 332], [cx + 120, 348], [cx + 200, 332], [cx + 262, 330], [cx + 250, 80]]
    wash(L, np.array(cloth, F), hexc('#eef2f9'), op=1.0, wob=1.2, seed=3, smooth=2, tex_k=0.08, rim=0.14)
    wash(L, np.array([[cx + 120, 90], [cx + 250, 80], [cx + 262, 330], [cx + 200, 332], [cx + 150, 320]], F), hexc('#c9d4ea'), op=0.7, wob=1.0, seed=4, smooth=2, tex_k=0.1)
    for k in range(7):
        x = cx - 210 + k * 70
        ink(L, [(x, 110), (x - 4, 330)], w0=1.2, color=hexc('#9fb2d3'), op=0.5, seed=10 + k, wob=0.8, taper=0.3)
    ink(L, np.vstack([np.array(cloth, F), np.array(cloth[:1], F)]), w0=1.3, color=hexc('#7d89a6'), op=0.5, seed=20, wob=0.8, taper=0.1)
    top = np.array([[cx + math.cos(a) * 258, 80 + math.sin(a) * 46] for a in np.linspace(0, 2 * math.pi, 30, endpoint=False)], F)
    wash(L, top, hexc('#f8faff'), op=1.0, wob=0.8, seed=5, smooth=2, tex_k=0.05, rim=0.16, rim_w=3)
    ink(L, np.vstack([top, top[:1]]), w0=1.5, color=hexc('#7d89a6'), op=0.6, seed=6, wob=0.6, taper=0.1, smooth=False)
    for k, (px, py) in enumerate([(cx - 120, 90), (cx + 60, 100)]):   # 盘子（白色）
        wash(L, np.array([[px + math.cos(a) * 46, py + math.sin(a) * 12] for a in np.linspace(0, 6.28, 14, endpoint=False)], F), hexc('#e1e8f4'), op=1.0, wob=0.4, seed=30 + k, smooth=2, tex_k=0.05)
        ink(L, [(px - 46, py), (px, py + 12), (px + 46, py)], w0=1.2, color=hexc('#9fb2d3'), op=0.6, seed=40 + k, wob=0.3)
    finish(L, 'table')


if __name__ == '__main__':
    old = json.loads((OUT / 'props.json').read_text())
    META.clear(); META.update(old)
    bulb(); table()
    (OUT / 'props.json').write_text(json.dumps(META, indent=1))
    print(META['bulb'], META['table'])
