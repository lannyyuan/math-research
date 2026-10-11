"""室外/天空四块补板：sky_gate（云缝 + 云海 + cloud_road，含晨光版）、lamp_sky（天上的灯座）、volcano（南方火山）、grassland（草原）。全部 2900×1080。
锚点见 PLATES.md：地面线 y=832；sky_gate 云缝 x≈1700、y 200~420（灰金 #cfc29a）；cloud_road 从左 x≈250 到右 x≈2900，路面 832 → 780；
lamp_sky 灯座在 x≈1450（灯盘直径≈760，盘沿 y≈400，盘心灯芯断成两截）；volcano 火山在 x≈1900（底宽≈1100，高≈620，顶 y≈210）、x 900~1500 平地；
grassland 毡包 x≈600、小湖 x 1700~2500、火塘石圈 x≈1250（周围 x 1000~1500 留空）。
用法：python3 bg_sky_extra.py [gate] [lamp] [volcano] [grass]"""
from cn_sky import *
from cn_sky import _spiral
from cn_land import stone_ring, grass_blades, dry_grass, puddle
import sys

W, H = 2900, 1080
GY = 832
which = sys.argv[1:] or ['gate', 'lamp', 'volcano', 'grass']
ROSE, LILAC = hexc('#E9A38C'), hexc('#9C86B8')
SEAM = hexc('#cfc29a')          # 云缝里漏出来的灰金（降了饱和度）
FIRE = hexc('#E8873A')


def ell(cx, cy, rx, ry, n=22):
    return [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]


def outline(L, pts, w=2.4, op=0.65, seed=0, dry=0.3):
    brush(L, pts, w0=w, color=INK, op=op, seed=seed, wob=0.7, taper=0.1, dry=dry, smooth=False)


def dawn_wash(C, kind):
    """灯亮以后的晨光：天边红霞（#E9A38C）、高处淡紫霞（#9C86B8），仍然是透明的水彩 + 留白。直接叠在调好色的画布上。"""
    yy = (np.arange(C.h, dtype=F) / C.h)[:, None, None]
    xx = (np.arange(C.w, dtype=F) / C.w)[None, :, None]
    rgb = C.rgb
    if kind == 'far':
        glow_ = np.exp(-(((yy - 0.62) / 0.22) ** 2)) * (0.5 + 0.5 * np.exp(-(((xx - 0.52) / 0.38) ** 2)))
        high = np.clip((0.6 - yy) / 0.6, 0, 1) ** 1.1
        a_rose, a_lilac = np.clip(glow_ * 0.58, 0, 0.66), np.clip(high * 0.36, 0, 0.42)
        rgb = rgb * (1 - a_lilac) + LILAC * a_lilac
        rgb = rgb * (1 - a_rose) + ROSE * a_rose
    elif kind == 'mid':
        k = 0.24 * np.exp(-(((yy - 0.72) / 0.25) ** 2))
        rgb = rgb * (1 - k) + ROSE * k
    else:
        k = 0.12 * np.exp(-(((yy - 0.8) / 0.3) ** 2))
        rgb = rgb * (1 - k) + ROSE * k
    C.rgb = np.clip(rgb * np.array([1.03, 1.0, 0.97], F), 0, 1).astype(F)


# ═════════════════════════ sky_gate ═════════════════════════
if 'gate' in which:
    VARS = ('night', 'lit', 'dawn')
    S = sky(W, H, hexc('#59636f'), hexc('#79848f'), hexc('#a1a8ad'), seed=1101, horizon=0.86, cloud=0.45, scale=500)
    cloud_bank(S, -250, W + 250, 250, 230, seed=11, col=A['cloud_dk'], sh=A['smoke_dk'], hi=A['cloud_sh'], ink=0.55, wmin=380, wmax=640, hscale=(0.8, 1.2), curls=2)
    cloud_bank(S, -250, W + 250, 460, 260, seed=12, col=A['cloud_sh'], sh=A['cloud_dk'], hi=A['cloud'], ink=0.5, wmin=360, wmax=620, hscale=(0.8, 1.25), curls=2)
    cloud_bank(S, -250, W + 250, 640, 260, seed=13, col=mix(A['cloud_sh'], A['cloud'], 0.35), sh=A['cloud_sh'], ink=0.45, wmin=340, wmax=600, curls=2)
    cloud_bank(S, -250, W + 250, 790, 210, seed=14, col=A['cloud'], sh=A['cloud_sh'], ink=0.4, wmin=320, wmax=540, curls=1)
    # 云缝（x≈1700，y 200~420）：一道窄窄的、亮的缝
    seam = [(1706, 190), (1713, 232), (1721, 262), (1716, 296), (1726, 330), (1717, 372), (1708, 428), (1699, 384), (1690, 346), (1698, 310), (1686, 276), (1695, 238)]
    wash(S, seam, A['cloud'] * 1.1, op=0.95, wob=1.2, seed=1111, smooth=2, rim=0.0)
    for sd, side in ((1112, -1), (1113, 1)):
        outline(S, [(1705 + side * 4, 196), (1705 + side * 17, 250), (1705 + side * 21, 320), (1705 + side * 13, 392), (1704, 430)], w=3.0, op=0.7, seed=sd, dry=0.4)

    def post_far(v, C):
        wash(C, seam, SEAM, op=0.92, wob=1.0, seed=1114, smooth=2, rim=0.0)
        glow(C, 1705, 320, 120, SEAM, op=0.36, power=2.0)
        wash(C, [(1700, 430), (1713, 430), (1790, 840), (1650, 840)], SEAM, op=0.07, wob=6, seed=1115, smooth=2, rim=0.0)        # 一缕极细的光，从缝里落下来
        wash(C, [(1704, 430), (1710, 430), (1732, 840), (1700, 840)], SEAM, op=0.07, wob=3, seed=1116, smooth=2, rim=0.0)
        if v == 'dawn':
            dawn_wash(C, 'far')
    save2('sky_gate_far', S, variants=VARS, gain=0.62, keep=0.16, post=post_far)

    M = Canvas(W, H)
    cloud_bank(M, -250, W + 250, 770, 160, seed=21, col=A['cloud_sh'], sh=A['cloud_dk'], ink=0.4, op=0.8, wmin=360, wmax=640, curls=1)
    cloud_bank(M, -250, W + 250, 835, 120, seed=22, col=A['cloud'], sh=A['cloud_sh'], ink=0.4, op=0.9, wmin=340, wmax=580, curls=1)
    save2('sky_gate_mid', M, variants=VARS, gain=0.7, keep=0.18, post=lambda v, C: dawn_wash(C, 'mid') if v == 'dawn' else None)

    Nn = Canvas(W, H)      # 脚下的云海平台：顶面在 y≈832，厚厚的、层层卷起，不是“筋斗云”
    for row, (by, hh, sd, col_) in enumerate([(888, 74, 35, A['cloud']), (934, 96, 31, A['cloud']), (990, 126, 32, A['cloud']), (1050, 150, 33, mix(A['cloud'], A['cloud_sh'], 0.25)), (1125, 170, 34, A['cloud_sh'])]):
        cloud_bank(Nn, -250, W + 250, by, hh, seed=sd, col=col_, sh=A['cloud_sh'], ink=0.5, wmin=420, wmax=700, hscale=(0.75, 1.1), y_jit=10, curls=2)
    save2('sky_gate_near', Nn, variants=VARS, gain=0.78, keep=0.2, post=lambda v, C: dawn_wash(C, 'near') if v == 'dawn' else None)

    R = Canvas(W, H)      # cloud_road：一块块云石板连成的路，从左 x≈250 到右 x≈2900，越往右越窄越高
    xs_ = np.linspace(250, 2820, 9)
    for i, x in enumerate(xs_):
        t = i / (len(xs_) - 1)
        wd = 340 - 150 * t
        yy = 840 - 58 * t ** 1.2
        wash(R, ell(x, yy + 16, wd * 0.5, 15 - 5 * t, 20), A['cloud_dk'], op=0.55, wob=3, seed=1190 + i, smooth=2, rim=0.0)      # 石板底下的投影
        cloud_mass(R, x, yy + 34, wd, 100 - 34 * t, seed=1200 + i, col=mix(A['cloud'], hexc('#f0ead8'), 0.7), sh=mix(A['cloud_sh'], A['cloud_dk'], 0.3), hi=hexc('#fbf7ea'), ink=1.0, curls=1, flat=0.5, bumps=max(3, int(wd / 120)))
    save2('cloud_road', R, variants=VARS, gain=0.92, keep=0.25, post=lambda v, C: dawn_wash(C, 'near') if v == 'dawn' else None)


# ═════════════════════════ lamp_sky ═════════════════════════
if 'lamp' in which:
    VARS = ('night', 'lit', 'dawn')
    S = sky(W, H, hexc('#3e4958'), hexc('#566273'), hexc('#7a8593'), seed=1301, horizon=0.9, cloud=0.25, scale=520)
    cloud_bank(S, -250, W + 250, 700, 150, seed=41, col=A['cloud_sh'], sh=A['cloud_dk'], ink=0.35, op=0.6, wmin=360, wmax=640, curls=1)

    def post_far2(v, C):
        r = np.random.default_rng(1302)
        if v == 'night':
            pts = [(r.uniform(10, W - 10), r.uniform(20, 640), r.choice([1.2, 1.7, 2.3, 3.0], p=[0.4, 0.3, 0.2, 0.1])) for _ in range(150)]
            dots(C, pts, hexc('#EFE8D8'), op=0.65)
        if v == 'dawn':
            dawn_wash(C, 'far')
    save2('lamp_sky_far', S, variants=VARS, gain=0.58, keep=0.15, post=post_far2)

    Nn = Canvas(W, H)
    for row, (by, hh, sd, col_) in enumerate([(888, 74, 55, A['cloud']), (934, 96, 51, A['cloud']), (990, 126, 52, A['cloud']), (1050, 150, 53, mix(A['cloud'], A['cloud_sh'], 0.25)), (1125, 170, 54, A['cloud_sh'])]):
        cloud_bank(Nn, -250, W + 250, by, hh, seed=sd, col=col_, sh=A['cloud_sh'], ink=0.5, wmin=420, wmax=700, hscale=(0.75, 1.1), y_jit=10, curls=2)
    # 灯座：青铜 / 石质的高脚底座，雕云纹，托着一只宽大的灯盘（盘心的灯芯断成两截）
    cx = 1450
    brz, brz_dk, brz_lt = A['bronze'], A['bronze_dk'], A['bronze_lt']
    foot = [(cx - 215, GY + 6), (cx - 190, GY - 40), (cx + 190, GY - 40), (cx + 215, GY + 6)]
    wash(Nn, foot, brz_dk, op=0.98, wob=1.0, seed=1401, smooth=0, tex_k=0.22, rim=0.22)
    outline(Nn, foot + [foot[0]], w=3.0, op=0.7, seed=1402)
    stem = [(cx - 160, GY - 40), (cx - 104, GY - 150), (cx - 84, GY - 270), (cx + 84, GY - 270), (cx + 104, GY - 150), (cx + 160, GY - 40)]
    wash(Nn, stem, brz, op=0.98, wob=1.2, seed=1403, smooth=1, tex_k=0.24, rim=0.25)
    wash(Nn, [(cx - 150, GY - 44), (cx - 100, GY - 150), (cx - 82, GY - 268), (cx - 40, GY - 268), (cx - 52, GY - 150), (cx - 96, GY - 44)], brz_lt, op=0.5, wob=1.0, seed=1404, smooth=1, rim=0.0)
    outline(Nn, stem, w=3.2, op=0.7, seed=1405)
    for k, yb in enumerate((GY - 120, GY - 190)):      # 柄上的箍
        brush(Nn, [(cx - 118 + k * 22, yb), (cx + 118 - k * 22, yb)], w0=9, color=brz_dk, op=0.95, seed=1410 + k, taper=0.04, wob=0.6)
    for k, (dx, yy) in enumerate(((-56, GY - 100), (56, GY - 100), (0, GY - 215))):    # 雕的云纹
        for flip in (1, -1):
            brush(Nn, _spiral(cx + dx + flip * 14, yy, 22, turns=1.5, flip=flip, rot=k), w0=2.6, color=brz_dk, op=0.8, seed=1420 + k * 2 + (flip > 0), wob=0.5, taper=0.3)
    # 灯盘：外沿椭圆（盘沿 y≈394）+ 盘身 + 盘里的暗
    dcx, dcy, drx, dry = cx, 440, 380, 46
    bowl = [(dcx - drx, dcy)] + [(dcx + drx * math.cos(a), dcy + 120 * math.sin(a) ** 0.9 + dry * 0.2) for a in np.linspace(math.pi, 0, 32)] + [(dcx + drx, dcy)]
    wash(Nn, bowl, brz, op=0.98, wob=1.2, seed=1430, smooth=1, tex_k=0.24, rim=0.25)
    wash(Nn, [(dcx - drx + 20, dcy + 10), (dcx - 250, dcy + 78), (dcx - 150, dcy + 112), (dcx - 120, dcy + 60)], brz_lt, op=0.45, wob=1.0, seed=1431, smooth=1, rim=0.0)
    outline(Nn, bowl, w=3.4, op=0.7, seed=1432)
    wash(Nn, ell(dcx, dcy, drx, dry, 40), brz_lt, op=0.98, wob=1.0, seed=1433, smooth=2, tex_k=0.14, rim=0.3)      # 盘沿
    wash(Nn, ell(dcx, dcy + 4, drx - 32, dry - 12, 40), brz_dk * 0.6, op=0.98, wob=1.0, seed=1434, smooth=2, tex_k=0.1, rim=0.1)  # 盘里（空着，暗）
    outline(Nn, ell(dcx, dcy, drx, dry, 40) + [ell(dcx, dcy, drx, dry, 40)[0]], w=3.4, op=0.7, seed=1435)
    outline(Nn, ell(dcx, dcy + 4, drx - 32, dry - 12, 40) + [ell(dcx, dcy + 4, drx - 32, dry - 12, 40)[0]], w=2.2, op=0.5, seed=1436)
    for k in range(9):      # 盘身外沿的云纹
        px = dcx - 300 + k * 75
        brush(Nn, _spiral(px, dcy + 56 + 10 * math.sin(k), 18, turns=1.4, flip=1 if k % 2 else -1, rot=k), w0=2.2, color=brz_dk, op=0.75, seed=1440 + k, wob=0.5, taper=0.3)
    # 盘心的灯芯座 + 断成两截的灯芯桩
    solid_pts = [(dcx - 26, dcy + 6), (dcx - 16, dcy - 14), (dcx + 16, dcy - 14), (dcx + 26, dcy + 6)]
    wash(Nn, solid_pts, brz_lt, op=0.98, wob=0.6, seed=1450, smooth=0, rim=0.25)
    outline(Nn, solid_pts + [solid_pts[0]], w=2.2, op=0.65, seed=1451)
    for sgn, ln, tilt in ((-1, 34, -0.35), (1, 26, 0.55)):
        top = (dcx + sgn * 7 + tilt * ln, dcy - 14 - ln)
        brush(Nn, [(dcx + sgn * 7, dcy - 12), top], w0=9, w1=7, color=hexc('#d8d2c0'), op=0.98, seed=1455 + sgn, taper=0.05, wob=0.5)
        brush(Nn, [(top[0] - 4, top[1] + 3), (top[0], top[1] - 3), (top[0] + 4, top[1] + 2)], w0=2.0, color=INK, op=0.6, seed=1457 + sgn, wob=1.0, taper=0.3)       # 断口毛糙
    save2('lamp_sky_near', Nn, variants=VARS, gain=0.72, keep=0.2, post=lambda v, C: dawn_wash(C, 'near') if v == 'dawn' else None)


# ═════════════════════════ volcano ═════════════════════════
if 'volcano' in which:
    S = sky(W, H, hexc('#4f5459'), hexc('#6a6e72'), hexc('#8f9291'), seed=1501, horizon=0.86, cloud=0.5, scale=520)
    r1 = ridge_y(W, 780, 190, 1511, rough=0.55, scale=420)
    mountain(S, r1, 880, N['far3'] * 0.8, N['far2'] * 0.7, seed=61, tex=0.5, tex_op=0.25, haze=0.35, glaze=0.3)
    mist(S, 0, W, 720, 80, seed=62, op=0.5, color=A['smoke'])
    # 灰黑的烟云
    cloud_bank(S, -250, W + 250, 330, 200, seed=63, col=A['smoke'], sh=A['smoke_dk'], hi=A['cloud_dk'], ink=0.35, op=0.8, wmin=380, wmax=620, curls=1)
    save_plate('volcano_far', S, variants=('night', 'lit'), gain=0.58, keep=0.15)

    M = Canvas(W, H)
    cx, top_y = 1900, 210
    ys_ = np.linspace(top_y, 842, 15)
    half = lambda y: 62 + 488 * ((y - top_y) / (842 - top_y)) ** 1.55
    cone = [(1900 - half(y) + 6 * math.sin(y * 0.05), y) for y in ys_[::-1]][::-1]
    cone = [(1900 - half(y) + 5 * math.sin(y * 0.07), float(y)) for y in ys_] + [(1900 + half(y) + 5 * math.sin(y * 0.06 + 2), float(y)) for y in ys_[::-1]]
    wash(M, cone, A['basalt_lt'], op=0.99, wob=2.0, seed=1520, smooth=1, tex_k=0.22, rim=0.25)
    wash(M, [(1900 + 20 + (half(y) - 40) * 0.0, float(y)) for y in ys_[:3]] + [(1900 + half(y) + 5 * math.sin(y * 0.06 + 2), float(y)) for y in ys_[2:]] + [(1900 + half(y) * 0.28, float(y)) for y in ys_[::-1][:-2]], A['basalt'], op=0.78, wob=2.0, seed=1521, smooth=1, rim=0.0)      # 背光的一面
    outline(M, cone, w=3.4, op=0.75, seed=1523, dry=0.35)
    r = np.random.default_rng(1524)
    for i in range(46):       # 山坡上顺着坡面的皴擦
        t0 = r.uniform(0.0, 1.0)
        side = -1 if r.random() < 0.55 else 1
        yb = r.uniform(300, 830)
        half = 70 + (yb - 215) * 0.88
        xb = cx + side * half * r.uniform(0.15, 0.95)
        brush(M, [(xb, yb), (xb + side * r.uniform(14, 40), yb + r.uniform(40, 110))], w0=r.uniform(2, 4), color=INK, op=r.uniform(0.2, 0.45), seed=1530 + i, wob=1.5, taper=0.4, dry=0.5)
    # 火山口：一个椭圆的口，里面是暗红灰（火光由 post 叠上）
    wash(M, ell(1900, top_y + 4, 70, 14, 20), A['smoke_dk'], op=0.95, wob=1.0, seed=1540, smooth=2, rim=0.2)
    smoke_column(M, 1900, top_y - 4, 1450, 20, 56, 190, seed=7, col=A['smoke'], op=0.85, n=30)
    mist(M, 0, W, 830, 40, seed=64, op=0.5, color=A['smoke'])

    def post_volcano(v, C):
        glow(C, 1900, top_y + 6, 170, FIRE, op=0.30, power=2.0)
        rr = np.random.default_rng(1550)
        for k in range(6):       # 火山口的几条火苗（只有这里和山石边，克制）
            bx = 1862 + k * 15 + rr.normal(0, 3)
            hh = rr.uniform(24, 62)
            flame = [(bx - 8, top_y + 6), (bx - 6, top_y - hh * 0.4), (bx + rr.normal(0, 4), top_y - hh), (bx + 5, top_y - hh * 0.35), (bx + 8, top_y + 6)]
            wash(C, flame, FIRE, op=0.9, wob=1.0, seed=1560 + k, smooth=2, rim=0.0)
            wash(C, [(bx - 4, top_y + 5), (bx, top_y - hh * 0.55), (bx + 4, top_y + 5)], hexc('#ffe2aa'), op=0.8, wob=0.6, seed=1570 + k, smooth=2, rim=0.0)
        for k in range(10):      # 飘起的火星
            dots(C, [(1900 + rr.normal(0, 55), top_y - rr.uniform(30, 190), rr.uniform(1.2, 2.6))], FIRE, op=0.7)
    save2('volcano_mid', M, variants=('night', 'lit'), gain=0.6, keep=0.15, post=post_volcano)

    Nn = Canvas(W, H)
    xs = np.arange(W, dtype=F)
    gy = GY + 4 * np.sin(xs / 210.0) + 3 * np.sin(xs / 61.0)
    ground_strip(Nn, gy, 1080, A['basalt_lt'] * 0.8, A['basalt_dk'], seed=1601, tex=1.2, tex_col=A['basalt_dk'])
    for i in range(20):
        x = r.uniform(0, W)
        if 880 < x < 1540:
            continue       # 平地要空着：人和马站在这里
        rock(Nn, x, r.uniform(850, 1030), r.uniform(100, 260), r.uniform(60, 150), seed=1610 + i, col=A['basalt'], dark=A['basalt_dk'], light=A['basalt_lt'])
    for i in range(14):
        x, y = r.uniform(80, W - 80), r.uniform(870, 1050)
        brush(Nn, [(x, y), (x + r.uniform(30, 90), y + r.normal(0, 6))], w0=r.uniform(2, 4), color=INK, op=0.5, seed=1640 + i, wob=1.0, taper=0.4, dry=0.4)    # 热裂缝
        steam(Nn, x + 20, y, r.uniform(70, 150), seed=1660 + i, w=22, op=0.4, n=3)
    save2('volcano_near', Nn, variants=('night', 'lit'), gain=0.6, keep=0.15)


# ═════════════════════════ grassland ═════════════════════════
if 'grass' in which:
    S = sky(W, H, hexc('#4b5564'), hexc('#6b7685'), hexc('#9ca3a8'), seed=1701, horizon=0.84, cloud=0.35, scale=560)
    # “天像一口黑锅扣在头顶”：四周往中间压暗，再叠一层低低的云
    yy = (np.arange(H, dtype=F) / H)[:, None, None]
    xx = (np.arange(W, dtype=F) / W)[None, :, None]
    vig = np.clip(0.12 + 0.55 * (1 - np.exp(-((yy / 0.55) ** 2))) * 0.0 + 0.38 * np.exp(-(((yy - 0.15) / 0.28) ** 2)) + 0.18 * np.abs(xx - 0.5), 0, 0.75)
    S.rgb = np.clip(S.rgb * (1 - vig * 0.55), 0, 1).astype(F)
    r1 = ridge_y(W, 790, 70, 1711, rough=0.5, scale=700)
    mountain(S, r1, 870, N['far3'] * 0.85, N['far2'] * 0.8, seed=71, tex=0.5, tex_op=0.2, haze=0.35, glaze=0.3)
    mist(S, 0, W, 760, 70, seed=72, op=0.55)
    r2 = ridge_y(W, 825, 38, 1712, rough=0.5, scale=500)
    mountain(S, r2, 900, N['mid1'] * 0.9, N['mid2'] * 0.9, seed=73, tex=0.7, tex_op=0.25, haze=0.2, glaze=0.4)
    save_plate('grassland_far', S, variants=('night', 'lit'), gain=0.58, keep=0.15)

    M = Canvas(W, H)
    # 小湖（x 1700~2500，y 690~790）：又黑又静，倒映一点点天光
    lake = [(1700, 770), (1790, 730), (1960, 705), (2160, 698), (2360, 712), (2500, 745), (2470, 790), (2200, 800), (1900, 796)]
    wash(M, lake, hexc('#53626a'), op=0.98, wob=3, seed=1720, smooth=2, tex_k=0.1, rim=0.35, rim_w=4)
    wash(M, [(1980, 724), (2300, 722), (2260, 740), (2010, 742)], hexc('#aab6bb'), op=0.45, wob=4, seed=1721, smooth=2, rim=0.0)
    for i in range(9):
        x = 1760 + i * 78
        brush(M, [(x, 748 + (i % 3) * 14), (x + 60, 750 + (i % 3) * 14)], w0=1.8, color=hexc('#d7dfe0'), op=0.45, seed=1722 + i, taper=0.5, dry=0.4)
    # 毡包（x≈600，灰色，直径≈360，高≈260）
    yx = 600
    wall = [(yx - 178, GY + 2), (yx - 178, GY - 120), (yx + 178, GY - 120), (yx + 178, GY + 2)]
    wash(M, wall, A['cloth'], op=0.98, wob=1.0, seed=1730, smooth=0, tex_k=0.2, rim=0.25)
    dome = [(yx - 186, GY - 118)] + [(yx + 186 * math.cos(a), GY - 118 - 148 * math.sin(a) ** 0.85) for a in np.linspace(math.pi, 0, 30)] + [(yx + 186, GY - 118)]
    wash(M, dome, A['cloth'] * 1.05, op=0.98, wob=1.2, seed=1731, smooth=1, tex_k=0.2, rim=0.25)
    wash(M, [(yx + 40, GY - 118)] + [(yx + 186 * math.cos(a), GY - 118 - 148 * math.sin(a) ** 0.85) for a in np.linspace(math.pi * 0.28, 0, 12)] + [(yx + 186, GY + 2), (yx + 60, GY + 2)], A['cloth_dk'], op=0.55, wob=1.2, seed=1732, smooth=1, rim=0.0)
    outline(M, wall[:1] + wall[1:3] + wall[3:], w=3.0, op=0.7, seed=1733)
    outline(M, dome, w=3.2, op=0.7, seed=1734)
    brush(M, [(yx - 182, GY - 120), (yx + 182, GY - 120)], w0=6, color=A['cloth_dk'], op=0.85, seed=1735, taper=0.03, wob=0.6)       # 腰带（绳）
    for k in range(7):      # 毡面的竖向接缝
        a = math.pi * (k + 1) / 8
        brush(M, [(yx + 186 * math.cos(a), GY - 120 - 4), (yx + 30 * math.cos(a), GY - 118 - 148 * math.sin(a) ** 0.85 * 0.98)], w0=1.6, color=A['cloth_dk'], op=0.5, seed=1736 + k, wob=0.8, taper=0.3, dry=0.3)
    wash(M, [(yx - 36, GY + 2), (yx - 36, GY - 100), (yx + 36, GY - 100), (yx + 36, GY + 2)], A['basalt_dk'], op=0.95, wob=0.8, seed=1750, smooth=0, rim=0.25)    # 门
    outline(M, [(yx - 36, GY + 2), (yx - 36, GY - 100), (yx + 36, GY - 100), (yx + 36, GY + 2)], w=2.6, op=0.7, seed=1751)
    # 几只羊（小的剪影，6~8 只，分散）
    for i, (x, y, s_) in enumerate([(220, 826, 1.0), (330, 838, 0.9), (930, 812, 0.7), (1010, 820, 0.75), (1480, 806, 0.6), (2180, 836, 0.9), (2640, 824, 1.0), (2760, 836, 0.85)]):
        wash(M, ell(x, y - 24 * s_, 34 * s_, 20 * s_, 14), A['cloth'] * 1.1, op=0.98, wob=1.2, seed=1760 + i, smooth=2, tex_k=0.3, rim=0.3)
        wash(M, ell(x + 36 * s_, y - 36 * s_, 11 * s_, 9 * s_, 10), A['cloth_dk'], op=0.98, wob=0.6, seed=1780 + i, smooth=2, rim=0.2)
        for lx in (-18, -6, 10, 22):
            brush(M, [(x + lx * s_, y - 10 * s_), (x + lx * s_, y + 2)], w0=3.0 * s_, color=A['cloth_dk'], op=0.95, seed=1790 + i + lx, taper=0.05)
        outline(M, ell(x, y - 24 * s_, 34 * s_, 20 * s_, 14) + [ell(x, y - 24 * s_, 34 * s_, 20 * s_, 14)[0]], w=1.8, op=0.5, seed=1800 + i)
    save_plate('grassland_mid', M, variants=('night', 'lit'), gain=0.62, keep=0.18)

    Nn = Canvas(W, H)
    xs = np.arange(W, dtype=F)
    gy = GY + 6 * np.sin(xs / 280.0) + 3 * np.sin(xs / 73.0 + 1)
    ground_strip(Nn, gy, 1080, N['grass'], N['grass_dk'], seed=1801, tex=1.0)
    rr = np.random.default_rng(1802)
    for x0_, x1_ in ((0, 980), (1520, W)):
        grass_blades(Nn, x0_, x1_, 840, 1060, 120, seed=int(x0_) + 5, col=N['grass_dk'], op=0.7, hmin=18, hmax=64)
        dry_grass(Nn, x0_, x1_, gy + 30, 40, seed=int(x0_) + 9, op=0.75, hmin=20, hmax=58)
    wash(Nn, ell(1250, GY + 10, 150, 26, 24), N['earth_dk'], op=0.55, wob=3, seed=1803, smooth=2, rim=0.1)       # 火塘的焦土
    stone_ring(Nn, 1250, GY + 4, 160, seed=1804)
    for i in range(10):
        x = rr.uniform(60, W - 60)
        if 960 < x < 1540:
            continue
        rock(Nn, x, rr.uniform(880, 1040), rr.uniform(50, 110), rr.uniform(28, 56), seed=1810 + i)
    save_plate('grassland_near', Nn, variants=('night', 'lit'), gain=0.62, keep=0.2)
