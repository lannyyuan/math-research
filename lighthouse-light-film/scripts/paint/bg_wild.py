"""场景 5、6、7：农场（谷仓 + 农舍）、结冰的河、悬崖边的雪路（暴风雪）。"""
from common import *

FARM_WIN = (1790, 700)   # 农舍窗户中心（世界坐标）：Remotion 在这里叠一团冷白色的光


def barn(L, x, y, w, h, seed):
    wall = rect(x - w / 2, y - h, x + w / 2, y)
    wash(L, wall, hexc('#7e8db0'), op=1.0, wob=1.2, seed=seed, smooth=0, tex_k=0.1, rim=0.12)
    planks(L, x - w / 2, y - h, x + w / 2, y, seed=seed + 1, col='#7b8aad', gap=30, hor=False)
    outline(L, wall, 1.8, 0.8, seed + 2)
    roof = np.array([[x - w / 2 - 20, y - h + 6], [x - w * 0.36, y - h - h * 0.5], [x + w * 0.36, y - h - h * 0.5], [x + w / 2 + 20, y - h + 6]], F)
    wash(L, roof, hexc('#46526f'), op=1.0, wob=1.2, seed=seed + 3, smooth=0, tex_k=0.14)
    outline(L, roof, 1.8, 0.8, seed + 4)
    cap = np.array([[x - w / 2 - 14, y - h + 4], [x - w * 0.36, y - h - h * 0.52], [x + w * 0.36, y - h - h * 0.52], [x + w / 2 + 14, y - h + 4], [x + w * 0.3, y - h + 20], [x, y - h + 10], [x - w * 0.3, y - h + 22]], F)
    wash(L, cap, P['snow'], op=1.0, wob=2.0, seed=seed + 5, smooth=2, tex_k=0.06)
    # 大门 + 白色交叉的门框
    door = rect(x - w * 0.16, y - h * 0.62, x + w * 0.16, y)
    wash(L, door, hexc('#3a4568'), op=1.0, wob=0.8, seed=seed + 6, smooth=0, tex_k=0.1)
    outline(L, door, 1.8, 0.85, seed + 7)
    ink(L, [(x - w * 0.16, y - h * 0.62), (x + w * 0.16, y)], w0=3, color=hexc('#e8eef8'), op=0.9, seed=seed + 8, wob=0.4)
    ink(L, [(x + w * 0.16, y - h * 0.62), (x - w * 0.16, y)], w0=3, color=hexc('#e8eef8'), op=0.9, seed=seed + 9, wob=0.4)


def hay(L, x, y, w, h, seed):
    pts = np.array([[x - w / 2, y], [x - w / 2 + 6, y - h], [x + w / 2 - 6, y - h], [x + w / 2, y]], F)
    wash(L, pts, hexc('#a9b4cc'), op=1.0, wob=1.5, seed=seed, smooth=2, tex_k=0.2)
    hatch(L, pts, 80, 7, 20, hexc('#6f7b9a'), op=0.4, w=1.1, seed=seed + 1)
    outline(L, pts, 1.4, 0.7, seed + 2)
    cap = np.array([[x - w / 2 - 4, y - h + 6], [x - w * 0.2, y - h - 14], [x + w * 0.2, y - h - 16], [x + w / 2 + 4, y - h + 6], [x, y - h + 16]], F)
    wash(L, cap, P['snow'], op=1.0, wob=1.5, seed=seed + 3, smooth=2, tex_k=0.06)


def farm_far():
    L = Canvas(W, H)
    hz = 500
    L.rgb[:] = sky(W, H, 'dusk', seed=21, horizon=hz / H, blotch=0.35)
    L.a[:] = 1
    hills(L, ridge_pts(0, W, hz + 10, 44, 51, 60), hz + 60, hexc('#7e92b8'), snow=True, seed=51, op=0.95)
    field(L, hz + 50, 840, seed=53)
    r = np.random.default_rng(7)
    for i in range(14):
        tree_pine(L, r.uniform(80, 1500) if i < 8 else r.uniform(2200, 2850), hz + 100 + r.uniform(0, 50), r.uniform(120, 230), seed=800 + i)
    grade(L, 'dusk')
    return L


def farm_near():
    L = Canvas(W, H)
    top = np.array([[-60, 800], [500, 790], [1200, 806], [1900, 812], [2400, 800], [2950, 796]], F)
    snow_ground(L, catmull(top, 8), 1120, seed=61)
    barn(L, 1060, 830, 520, 260, seed=700)
    hay(L, 1420, 836, 100, 76, 710)
    hay(L, 1500, 840, 96, 70, 713)
    house(L, 1960, 832, 560, 280, 0.55, seed=720, windows=2, door=True, chimney=True, wall='#eef2f8', roof_col='#566480')
    smoke(L, 2110, 540, n=5, seed=721, s=1.0, op=0.4)
    # 路 + 篱笆 + 树
    road = np.array([[-60, 900], [900, 892], [1600, 904], [2200, 912], [2950, 906], [2950, 980], [2200, 988], [1600, 984], [900, 976], [-60, 982]], F)
    wash(L, road, hexc('#c7d2e6'), op=0.5, wob=4, seed=62, smooth=2, tex_k=0.14)
    for k, dy in enumerate((18, 64)):
        pts = np.array([[-60, 900 + dy], [900, 892 + dy], [1600, 904 + dy], [2200, 912 + dy], [2950, 906 + dy]], F)
        ink(L, catmull(pts, 8), w0=3.0, color=P['snow_sh3'], op=0.35, seed=63 + k, wob=2.0, taper=0.05)
    for i in range(7):
        px = 120 + i * 180
        py = np.interp(px, top[:, 0], top[:, 1]) + 56
        post(L, px, py, 94, 32, seed=730 + i)
        if i:
            wire(L, (px - 180 + 6, py - 92), (px - 6, py - 90), sag=10, seed=750 + i)
    for i, (bx_, by_) in enumerate([(300, 800), (2700, 805)]):
        bush(L, bx_, by_, 250, 1.4, 11, seed=770 + i)
    for i, (bx_, by_) in enumerate([(160, 1050), (1250, 1070), (2300, 1060), (2780, 1040)]):
        bush(L, bx_, by_, 150, 1.0, 8, seed=780 + i)
    rocks(L, 760, 1060, 240, 80, seed=790)
    grade(L, 'night')
    return L


# ───────────── 结冰的河 ─────────────
ICE = dict(x0=900, x1=1980, y0=790, y1=1000)   # 冰面范围
HOLE = (1430, 868)                             # 冰窟窿（世界坐标，中心）


def ice_far():
    L = Canvas(W, H)
    hz = 470
    L.rgb[:] = sky(W, H, 'dusk', seed=31, horizon=hz / H, blotch=0.35)
    L.a[:] = 1
    hills(L, ridge_pts(0, W, hz + 12, 40, 61, 60), hz + 60, hexc('#7a8eb4'), snow=True, seed=61, op=0.95)
    field(L, hz + 50, 840, seed=63)
    # 远处的河：弯弯曲曲的一条淡蓝带子，越远越窄、越淡（S 形，免得看起来像个三角形）
    ys_ = np.linspace(840, 528, 40)
    cx_ = 1560 + 150 * np.sin((840 - ys_) / 95.0) * ((840 - ys_) / 312.0) ** 0.6 + (840 - ys_) * 0.0
    hw_ = 6 + (ys_ - 528) / 312.0 * 150
    left = np.stack([cx_ - hw_, ys_], 1)
    right = np.stack([cx_ + hw_, ys_], 1)
    ribbon = np.vstack([left, right[::-1]])
    wash(L, ribbon, hexc('#c1d0e8'), op=1.0, wob=2, seed=64, smooth=1, tex_k=0.08, rim=0.2)
    ink(L, left, w0=1.4, color=P['snow_sh3'], op=0.35, seed=65, wob=0.8, taper=0.2)
    ink(L, right, w0=1.4, color=P['snow_sh3'], op=0.35, seed=66, wob=0.8, taper=0.2)
    r = np.random.default_rng(9)
    for i in range(16):   # 两岸光秃秃的树 + 几棵松
        px = r.choice([r.uniform(100, 1150), r.uniform(1900, 2800)])
        by = hz + 110 + r.uniform(0, 80)
        if i % 3 == 0:
            tree_pine(L, px, by + 20, r.uniform(140, 240), seed=900 + i)
        else:
            bush(L, px, by + 40, r.uniform(150, 260), 1.1, 10, seed=920 + i, snow_cap=False)
    return L


def ice_near():
    L = Canvas(W, H)
    top = np.array([[-60, 800], [500, 800], [900, 818], [1000, 850]], F)
    # 两岸：左右各一块雪地，中间是河面
    left = np.array([[-60, 800], [500, 792], [900, 806], [1010, 836], [940, 940], [880, 1120], [-60, 1120]], F)
    right = np.array([[2950, 796], [2500, 796], [2100, 810], [1990, 840], [2040, 940], [2100, 1120], [2950, 1120]], F)
    for k, poly in enumerate((left, right)):
        wash(L, poly, P['snow'], op=1.0, wob=2.5, seed=70 + k, smooth=1, tex_k=0.07, rim=0.1)
    # 冰面：偏蓝的白，带深一点的冰纹
    ice = np.array([[900, 812], [1180, 800], [1500, 806], [1800, 802], [1990, 820], [2050, 900], [2100, 1010], [2110, 1140], [1700, 1150], [1300, 1150], [870, 1140], [880, 1010], [880, 920]], F)
    wash(L, ice, hexc('#b7cbe9'), op=1.0, wob=3, seed=73, smooth=2, tex_k=0.1, rim=0.22, rim_w=5)
    wash(L, ice + [0, 18], hexc('#9db6dc'), op=0.18, wob=3, seed=74, smooth=2, tex_k=0.1)
    r = np.random.default_rng(10)
    for i in range(9):   # 冰面上的亮条（反光）
        x = r.uniform(960, 1950); y = r.uniform(830, 1070)
        ink(L, [(x, y), (x + r.uniform(60, 180), y + r.normal(0, 3))], w0=r.uniform(3, 7), color=hexc('#eaf1fb'), op=0.55, seed=i + 80, wob=1.0, taper=0.5)
    for i in range(22):   # 细细的冰裂纹
        x = r.uniform(940, 1980); y = r.uniform(820, 1060)
        pts = [(x, y)]
        for j in range(r.integers(3, 6)):
            x += r.uniform(-34, 40); y += r.uniform(-18, 22)
            pts.append((x, y))
        ink(L, pts, w0=1.1, color=hexc('#6f86b3'), op=0.35, seed=i + 100, wob=0.6, taper=0.4)
    ink(L, catmull(ice[:6], 8), w0=2.0, color=INK, op=0.45, seed=120, wob=1.5, taper=0.1)
    # 岸边：雪堤 + 芦苇似的枯草 + 灌木
    for k, (x0_, y0_) in enumerate([(920, 1060), (2040, 1050)]):
        for j in range(9):
            xx = x0_ + (j - 4) * 12
            ink(L, [(xx, y0_ + 8), (xx + r.normal(0, 6), y0_ - r.uniform(40, 90))], w0=1.6, color=P['twig'], op=0.8, seed=130 + k * 20 + j, wob=0.6, taper=0.3)
    for i, (bx_, by_) in enumerate([(220, 880), (2600, 880)]):
        bush(L, bx_, by_, 230, 1.3, 11, seed=140 + i)
    for i, (bx_, by_) in enumerate([(160, 1050), (640, 1040), (2330, 1050), (2780, 1050)]):
        bush(L, bx_, by_, 150, 1.0, 8, seed=150 + i)
    rocks(L, 560, 1050, 260, 90, seed=160)
    rocks(L, 2480, 1060, 260, 90, seed=161)
    # 一根倒下的旧栏杆 / 断了的小木桥（Bud 想抄近路的原因）
    return L


def hole_assets():
    """冰窟窿（后）和窟窿前沿（前），单独存成小图，由 Remotion 摆放。返回 (back, front)。"""
    wd, ht = 380, 120
    B = Canvas(wd, ht)
    cx, cy = wd / 2, ht / 2
    r = np.random.default_rng(3)
    ring = []
    for a in np.linspace(0, 2 * math.pi, 22, endpoint=False):
        k = 1.0 + (0.1 if int(a * 3.1) % 2 else -0.03) + r.normal(0, 0.03)
        ring.append((cx + math.cos(a) * 170 * k, cy + math.sin(a) * 44 * k))
    wash(B, np.array(ring, F), hexc('#0f1b3a'), op=1.0, wob=1.2, seed=1, smooth=1, tex_k=0.12, rim=0.0)
    wash(B, np.array(ring, F) * [0.7, 0.5] + [cx * 0.3 + 12, cy * 0.5 + 10], hexc('#1c2f5c'), op=0.6, wob=1.0, seed=2, smooth=2, tex_k=0.12)
    for k in range(5):
        y = cy - 20 + k * 11
        ink(B, [(cx - 80 + k * 10, y), (cx - 10 + k * 14, y + 1), (cx + 90 - k * 6, y)], w0=1.6, color=hexc('#4f6fae'), op=0.5, seed=10 + k, wob=0.8, taper=0.5)
    ink(B, np.vstack([ring, ring[:1]]), w0=2.6, color=hexc('#e9f0fb'), op=0.95, seed=20, wob=1.2, taper=0.1, smooth=False)
    ink(B, np.vstack([ring, ring[:1]]) + [0, 2], w0=1.6, color=INK, op=0.55, seed=21, wob=1.2, taper=0.1, smooth=False)
    # 几块浮冰
    for k, (fx, fy, fw) in enumerate([(cx - 90, cy + 14, 40), (cx + 100, cy - 6, 34)]):
        pts = np.array([[fx - fw, fy], [fx - fw * 0.4, fy - 8], [fx + fw * 0.6, fy - 6], [fx + fw, fy + 3], [fx, fy + 9]], F)
        wash(B, pts, hexc('#dbe6f6'), op=1.0, wob=0.8, seed=30 + k, smooth=1, tex_k=0.08)
        outline(B, pts, 1.2, 0.5, 40 + k)
    # 前沿：窟窿的前半圈冰缘（盖在 Bud 腰上，让他像是泡在水里）
    F_ = Canvas(wd, ht)
    arc = [(cx + math.cos(a) * 170, cy + math.sin(a) * 44) for a in np.linspace(0.15, math.pi - 0.15, 14)]
    ink(F_, arc, w0=9, color=hexc('#0f1b3a'), op=0.95, seed=50, wob=1.0, taper=0.15)
    ink(F_, [(x, y + 1) for x, y in arc], w0=3.2, color=hexc('#e9f0fb'), op=0.95, seed=51, wob=1.0, taper=0.15)
    for k in range(5):
        x = cx - 120 + k * 60
        ink(F_, [(x, cy + 40), (x + 40, cy + 41)], w0=1.8, color=hexc('#9fb8e0'), op=0.6, seed=60 + k, wob=0.6, taper=0.5)
    for nm, C in (('ice_hole_back', B), ('ice_hole_front', F_)):
        (OUT.parent / 'props').mkdir(exist_ok=True)
        C.save(OUT.parent / 'props' / f'{nm}.png')


# ───────────── 悬崖边的雪路（暴风雪） ─────────────
EDGE_X = 2010   # 悬崖边（路到这里就没了）


def cliff_far():
    L = Canvas(W, H)
    hz = 470
    L.rgb[:] = sky(W, H, 'storm', seed=41, horizon=hz / H, blotch=0.4)
    L.a[:] = 1
    sea(L, hz + 10, H, seed=9, tone='night', strokes=700)
    r = np.random.default_rng(5)
    for i in range(60):   # 大浪的白头
        y = hz + 40 + r.random() ** 1.5 * 520
        x = r.uniform(1500, W)
        ln = r.uniform(60, 240) * (0.5 + (y - hz) / 420)
        ink(L, [(x, y), (x + ln / 2, y - 3), (x + ln, y + 1)], w0=1.6 + (y - hz) / 140, color=hexc('#dbe5f6'), op=0.45, seed=i + 400, wob=1.0, taper=0.5)
    hills(L, ridge_pts(0, 1500, hz + 4, 20, 71, 40), hz + 14, hexc('#2d4067'), snow=True, seed=71, op=1.0, snow_col=hexc('#6f83ab'))
    return L


def cliff_near():
    SH = 90   # 整张图往上抬 90 像素（路更高，角色的脚就在字幕上方）
    L = Canvas(W, H + SH)
    path = np.array([[-60, 880], [500, 872], [1000, 884], [1500, 878], [1900, 884], [EDGE_X, 892]], F)
    snow_ground(L, catmull(path, 8), 1300, seed=81)
    # 悬崖的断面：从边缘垂直落下去，岩壁 + 一道小小的窄台（Pebbles 的帽子落在这里）
    face = np.array([[EDGE_X - 10, 888], [EDGE_X + 16, 890], [EDGE_X + 40, 990], [EDGE_X + 30, 1100], [EDGE_X + 20, 1180], [EDGE_X - 160, 1180], [EDGE_X - 120, 1000]], F)
    wash(L, face, P['rock'], op=1.0, wob=2.0, seed=82, smooth=1, tex_k=0.22, rim=0.2)
    hatch(L, face, 80, 8, 26, P['rock_dk'], op=0.55, w=1.2, seed=83)
    ledge = np.array([[EDGE_X - 30, 972], [EDGE_X + 36, 966], [EDGE_X + 96, 976], [EDGE_X + 84, 992], [EDGE_X + 20, 996], [EDGE_X - 28, 990]], F)
    wash(L, ledge, P['snow'], op=1.0, wob=1.5, seed=84, smooth=2, tex_k=0.06)
    wash(L, ledge + [0, 5], P['snow_sh1'], op=0.4, wob=1.0, seed=85, smooth=2)
    # 雪檐：边缘上悬出一块
    lip = np.array([[EDGE_X - 120, 884], [EDGE_X - 20, 880], [EDGE_X + 30, 886], [EDGE_X + 50, 900], [EDGE_X + 10, 912], [EDGE_X - 80, 902]], F)
    wash(L, lip, P['snow'], op=1.0, wob=1.5, seed=86, smooth=2, tex_k=0.06)
    # 沿路的篱笆桩和一道旧绳子（到悬崖前就断了）
    for i in range(7):
        px = 120 + i * 270
        py = np.interp(px, path[:, 0], path[:, 1]) + 46
        post(L, px, py, 96 + (i % 3) * 8, 32, seed=840 + i)
        if i:
            wire(L, (px - 270 + 6, py - 94), (px - 6, py - 92), sag=14, seed=860 + i)
    for i, (bx_, by_) in enumerate([(300, 1050), (1250, 1060), (1750, 1070)]):
        bush(L, bx_, by_, 150, 1.0, 8, seed=880 + i)
    rocks(L, 760, 1060, 260, 90, seed=890)
    for i, rx in enumerate((200, 820, 1500)):
        rocks(L, rx, 902, 150, 38, seed=895 + i, n=2)
    grade(L, 'storm')
    out = Canvas(W, H)
    out.rgb = L.rgb[SH:].copy(); out.a = L.a[SH:].copy()
    return out


if __name__ == '__main__':
    save_pair('farm', farm_far(), farm_near())
    save_pair('ice', ice_far(), ice_near())
    hole_assets()
    save_pair('cliff', cliff_far(), cliff_near())
    print('ok')
