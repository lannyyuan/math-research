"""室内三块补板：kitchen（奶奶家的灶间，S2）、hut_in（雪山小屋里，S4，+ hut_in_clean 扫净后的叠层）、hall_king（殿上，S5）。
全部 2400×1080，far + near，地面线 y=832；窗光 / 灯光是纸白冷光（LightMap + save2，调色之后叠上去，不被压成靛蓝）。
锚点见 PLATES.md：灶间 灶 x≈420、大桌 x≈1250（桌面 y≈720，宽 520）、窗 x≈1700,y≈380、水缸 x≈2050、x 850~1150 留空；
小屋 桌 x≈1200（桌面 y≈690，宽 560，中央留空放铜铃）、古琴 x≈1700、鼓 x≈420、窗 x≈700,y≈380；
殿 宝座在 x≈1200（三级台阶高台，座面 y≈640）、立柱 x≈330 / x≈2070、官员站位 x≈600 / x≈1800。
用法：python3 bg_interiors.py [kitchen] [hut] [hall]"""
from cn_arch import *
from cn_land import plank_wall, beam, window_paper, ground_strip
import sys

W, H = 2400, 1080
GY = 832
which = sys.argv[1:] or ['kitchen', 'hut', 'hall']


def ell(cx, cy, rx, ry, n=22):
    return [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]


def outline(L, pts, w=2.4, op=0.65, seed=0, dry=0.3):
    brush(L, pts, w0=w, color=INK, op=op, seed=seed, wob=0.7, taper=0.1, dry=dry, smooth=False)


def solid(L, pts, col, seed=0, ink=0.65, w=2.4, op=0.98, tex=0.22, closed=True):
    wash(L, pts, col, op=op, wob=1.0, seed=seed, smooth=0, tex_k=tex, rim=0.22)
    if ink > 0:
        outline(L, list(pts) + ([pts[0]] if closed else []), w=w, op=ink, seed=seed + 1)


def leg(L, x, y0, y1, w, seed):
    """桌/凳的腿：一条窄木条 + 两边墨线（不用 beam，它的皴擦笔触会比短腿还长，拖到地线下面）。"""
    wash(L, [(x - w / 2, y0), (x + w / 2, y0), (x + w / 2 - 1, y1), (x - w / 2 + 1, y1)], A['wood_dk'], op=0.98, wob=0.6, seed=seed, smooth=0, tex_k=0.25, rim=0.2)
    wash(L, [(x - w / 2, y0), (x - w / 2 + w * 0.3, y0), (x - w / 2 + w * 0.3, y1), (x - w / 2 + 1, y1)], A['wood_lt'], op=0.3, wob=0.5, seed=seed + 1, smooth=0, rim=0.0)
    outline(L, [(x - w / 2, y0), (x - w / 2 + 1, y1)], w=2.0, op=0.7, seed=seed + 2)
    outline(L, [(x + w / 2, y0), (x + w / 2 - 1, y1)], w=2.0, op=0.7, seed=seed + 3)


def table(L, cx, top_y, w, seed, top_col=None, dust=0.0, h_top=26):
    """一张方桌（正面）：桌面（一条厚板）+ 桌裙 + 四条腿（外侧两条粗，里侧两条细、略短）。返回桌面上沿 y。"""
    top_col = A['wood'] if top_col is None else top_col
    x0, x1 = cx - w / 2, cx + w / 2
    for (lx, sd, lw) in ((x0 + 22, 1, 20), (x1 - 22, 2, 20), (x0 + w * 0.2, 3, 14), (x1 - w * 0.2, 4, 14)):
        leg(L, lx, top_y + h_top, GY + (6 if lw > 15 else 0), lw, seed + sd)
    solid(L, [(x0 - 14, top_y + 8), (x1 + 14, top_y + 8), (x1 + 8, top_y + h_top), (x0 - 8, top_y + h_top)], A['wood_dk'], seed=seed + 5, w=2.6)     # 桌裙
    solid(L, [(x0 - 20, top_y - 4), (x1 + 20, top_y - 4), (x1 + 14, top_y + 10), (x0 - 14, top_y + 10)], top_col, seed=seed + 6, w=2.8)                  # 桌面板
    wash(L, [(x0 - 18, top_y - 4), (x1 + 18, top_y - 4), (x1 + 18, top_y + 1), (x0 - 18, top_y + 1)], A['wood_lt'], op=0.55, wob=0.6, seed=seed + 7, smooth=0, rim=0.0)
    if dust > 0:
        r = np.random.default_rng(seed + 8)
        for i in range(8):
            wash(L, ell(r.uniform(x0, x1), top_y - 2, r.uniform(30, 90), 5, 10), hexc('#d8d4c8'), op=dust * r.uniform(0.5, 1.0), wob=2, seed=seed + 20 + i, smooth=2, rim=0.0)
    return top_y - 4


def bench(L, cx, y, w, seed):
    solid(L, [(cx - w / 2, y), (cx + w / 2, y), (cx + w / 2 - 4, y + 18), (cx - w / 2 + 4, y + 18)], A['plank'], seed=seed, w=2.4)
    for sx in (-1, 1):
        leg(L, cx + sx * (w / 2 - 22), y + 18, GY + 8, 16, seed + 1 + (sx > 0))


def jar(L, cx, by, w, h, seed, col=None, lid=True):
    """水缸 / 陶罐：鼓肚、窄口、深色的口沿。"""
    col = A['earth_dk'] if col is None else col
    pts = [(cx - w * 0.30, by - h)] + [(cx - w * 0.5 * math.sin(t) * (1.0 if t < 1.6 else 0.9), by - h * 0.95 + h * 0.95 * (t / math.pi) * 0.98) for t in np.linspace(0.5, math.pi - 0.45, 12)] \
        + [(cx + w * 0.5 * math.sin(t), by - h * 0.95 + h * 0.95 * (t / math.pi) * 0.98) for t in np.linspace(math.pi - 0.45, 0.5, 12)] + [(cx + w * 0.30, by - h)]
    solid(L, pts, col, seed=seed, w=2.6)
    wash(L, [(cx - w * 0.5, by - h * 0.7), (cx - w * 0.3, by - h * 0.72), (cx - w * 0.28, by - h * 0.15), (cx - w * 0.42, by - h * 0.2)], A['earth_lt'], op=0.35, wob=1, seed=seed + 2, smooth=2, rim=0.0)
    solid(L, ell(cx, by - h, w * 0.32, 9, 18), A['basalt_dk'], seed=seed + 3, w=2.4)
    if lid:
        brush(L, [(cx - w * 0.5, by - h * 0.55), (cx, by - h * 0.5), (cx + w * 0.5, by - h * 0.55)], w0=2.0, color=INK, op=0.35, seed=seed + 4, wob=0.5, taper=0.2)


def bowl(L, cx, y, w, seed, col=None):
    col = A['cloth'] if col is None else col
    pts = [(cx - w / 2, y - w * 0.28)] + [(cx + w / 2 * math.cos(a), y - w * 0.28 + w * 0.4 * math.sin(a)) for a in np.linspace(math.pi, 0, 14)] + [(cx + w / 2, y - w * 0.28)]
    solid(L, pts, col, seed=seed, w=1.8)
    wash(L, ell(cx, y - w * 0.28, w / 2, w * 0.09, 14), A['basalt'], op=0.85, wob=0.4, seed=seed + 1, smooth=2, rim=0.0)


# ═════════════════════════ 灶间 ═════════════════════════
if 'kitchen' in which:
    S = Canvas(W, H, bg=hexc('#7d7466'))
    plank_wall(S, 0, 0, W, 832, seed=601, col=A['earth'], dark=A['earth_dk'], plank_h=70, grain_k=0.5)    # 土坯 / 木板的夯墙
    wash(S, rect(0, 0, W, 832), hexc('#6b6458'), op=0.30, wob=1, seed=602, smooth=0, rim=0.0)
    lm = LightMap(W, H)
    # 房梁
    beam(S, 0, 60, W, 150, seed=610, col=A['wood_dk'])
    beam(S, 0, 200, W, 232, seed=611, col=A['wood_dk'])
    for x_ in (360, 1150, 1950):
        beam(S, x_ - 26, 150, x_ + 26, 832, seed=620 + x_ // 100, col=A['wood_dk'])
    # 窗：纸糊的小窗（窗外夜色，窗里透进冷白的光）
    box = window_paper(S, 1700, 380, 160, 200, seed=630, grid=(3, 4))
    lm.rect(box[0] + 4, box[1] + 4, box[2] - 4, box[3] - 4, 0.95)
    for (gx, gy_, gr, sd) in ((560, 330, 30, 640), (610, 380, 24, 641)):
        brush(S, [(gx, 260), (gx, gy_ - gr)], w0=2.0, color=A['wood_dk'], op=0.8, seed=sd, taper=0.1)
        solid(S, ell(gx, gy_, gr * 0.8, gr, 14), A['gold'], seed=sd + 1, w=2.0)
        solid(S, ell(gx, gy_ - gr * 1.1, gr * 0.5, gr * 0.5, 12), A['gold'], seed=sd + 2, w=2.0)
    for k in range(5):      # 一串玉米
        solid(S, ell(1010 + (k % 2) * 6, 300 + k * 46, 11, 24, 12), A['gold_lt'], seed=650 + k, w=1.8)
    brush(S, [(1010, 240), (1010, 300 + 5 * 46)], w0=2.0, color=A['wood_dk'], op=0.85, seed=660, taper=0.05)
    for (hx, sd) in ((1400, 670), (1480, 671)):      # 挂着的农具：锄 / 镰
        brush(S, [(hx, 250), (hx, 560)], w0=7, color=A['wood'], op=0.95, seed=sd, taper=0.04, wob=0.6)
        solid(S, [(hx - 4, 548), (hx + 56, 560), (hx + 60, 590), (hx - 2, 572)], A['basalt_lt'], seed=sd + 1, w=2.0)
    save2('kitchen_far', S, variants=('night', 'lit'), gain=0.62, keep=0.22, lights=[(lm, WINDOW_LIGHT)])

    Nn = Canvas(W, H)
    xs = np.arange(W, dtype=F)
    gy = GY + 2.5 * np.sin(xs / 230.0)
    ground_strip(Nn, gy, 1080, A['earth'], A['earth_dk'], seed=701, tex=1.0, tex_col=A['earth_dk'])        # 夯实的泥地
    r = np.random.default_rng(702)
    for i in range(30):
        x, y = r.uniform(0, W), r.uniform(850, 1070)
        brush(Nn, [(x, y), (x + r.uniform(40, 160), y + r.normal(0, 4))], w0=r.uniform(1.6, 3.4), color=A['earth_dk'], op=0.3, seed=703 + i, wob=1.0, taper=0.4, dry=0.35)
    # 灶：土灶（灶台高≈200，灶口黑），灶上一口锅
    sx = 420
    solid(Nn, [(sx - 150, GY + 8), (sx - 126, GY - 200), (sx + 130, GY - 200), (sx + 156, GY + 8)], A['earth'], seed=710, w=3.0)
    wash(Nn, [(sx - 126, GY - 200), (sx + 130, GY - 200), (sx + 136, GY - 178), (sx - 132, GY - 178)], A['earth_lt'], op=0.7, wob=1, seed=711, smooth=0, rim=0.0)
    wash(Nn, [(sx - 70, GY + 4), (sx - 64, GY - 96)] + [(sx + 4 * math.cos(a), GY - 96 - 30 * math.sin(a) * 0) for a in []] + [(sx + 64, GY - 96), (sx + 70, GY + 4)], hexc('#1a1d20'), op=0.95, wob=1.0, seed=712, smooth=0, rim=0.0)
    wash(Nn, ell(sx, GY - 96, 64, 22, 18), hexc('#1a1d20'), op=0.95, wob=0.8, seed=713, smooth=2, rim=0.0)                # 灶口（黑）
    outline(Nn, [(sx - 70, GY + 4), (sx - 64, GY - 96)] + ell(sx, GY - 96, 64, 22, 18)[2:10] + [(sx + 64, GY - 96), (sx + 70, GY + 4)], w=2.6, op=0.6, seed=714)
    pot = [(sx - 82, GY - 200)] + [(sx + 90 * math.cos(a), GY - 200 + 74 * math.sin(a)) for a in np.linspace(math.pi, 0, 14)][::-1] + [(sx + 82, GY - 200)]
    pot = [(sx - 88, GY - 232)] + [(sx - 88 * math.cos(a), GY - 232 + 62 * math.sin(a)) for a in np.linspace(0, math.pi, 14)] + [(sx + 88, GY - 232)]
    solid(Nn, pot, A['basalt_dk'], seed=715, w=3.0)
    solid(Nn, ell(sx, GY - 232, 88, 14, 18), A['basalt'], seed=716, w=2.6)
    solid(Nn, [(sx + 70, GY - 150), (sx + 120, GY - 250), (sx + 134, GY - 246), (sx + 80, GY - 142)], A['earth_dk'], seed=717, w=2.0)      # 灶后的烟囱根
    # 大桌（x≈1250，桌面 y≈720，宽 520）+ 桌上小件 + 两条长凳
    tt = table(Nn, 1250, 720, 520, seed=720, dust=0.0)
    bowl(Nn, 1130, tt, 56, seed=730)
    bowl(Nn, 1200, tt, 50, seed=731, col=A['cloth_dk'])
    solid(Nn, ell(1312, tt - 14, 15, 19, 14), hexc('#e4dfd0'), seed=732, w=1.8)                                        # 一个蛋
    for k in range(3):       # 萝卜干
        solid(Nn, [(1380 + k * 26, tt - 3), (1396 + k * 26, tt - 12), (1404 + k * 26, tt - 3)], A['gold_lt'], seed=735 + k, w=1.6)
    bench(Nn, 1130, 772, 400, seed=740)
    bench(Nn, 1390, 772, 400, seed=741)
    # 水缸（x≈2050）
    jar(Nn, 2050, GY + 8, 210, 270, seed=750)
    # 墙脚的柴堆
    for i in range(9):
        a = i * 0.7
        brush(Nn, [(120 + 30 * (i % 4) - 40, GY + 20 - 14 * (i // 4)), (200 + 30 * (i % 4) - 40, GY + 14 - 14 * (i // 4))], w0=15, color=A['wood'], op=0.95, seed=760 + i, wob=0.5, taper=0.05)
    save2('kitchen_near', Nn, variants=('night', 'lit'), gain=0.66, keep=0.22)


# ═════════════════════════ 小屋里 ═════════════════════════
if 'hut' in which:
    S = Canvas(W, H, bg=hexc('#6f685c'))
    plank_wall(S, 0, 0, W, 832, seed=801, col=A['plank'], dark=A['plank_dk'], plank_h=58, grain_k=0.7)
    wash(S, rect(0, 0, W, 832), hexc('#5f6672'), op=0.32, wob=1, seed=802, smooth=0, rim=0.0)
    lm = LightMap(W, H)
    beam(S, 0, 50, W, 130, seed=810, col=A['wood_dk'])                 # 屋顶横梁
    beam(S, 0, 180, W, 212, seed=811, col=A['wood_dk'])
    for x_ in (200, 1000, 1800):
        beam(S, x_ - 24, 130, x_ + 24, 832, seed=820 + x_ // 100, col=A['wood_dk'])
    box = window_paper(S, 700, 380, 200, 240, seed=830, grid=(3, 4))      # 窗纸透进雪夜的冷白光
    lm.rect(box[0] + 4, box[1] + 4, box[2] - 4, box[3] - 4, 0.95)
    # 左墙上挂着一口钟和一面鼓（x≈420，y 400~620）
    brush(S, [(380, 130), (380, 360)], w0=3.0, color=A['wood_dk'], op=0.85, seed=840, taper=0.05)
    bell_ = [(344, 470), (352, 380), (380, 358), (408, 380), (416, 470)]
    solid(S, bell_, A['bronze'], seed=841, w=2.8)
    wash(S, [(356, 470), (360, 392), (372, 380), (370, 470)], A['bronze_lt'], op=0.5, wob=1, seed=842, smooth=2, rim=0.0)
    solid(S, ell(380, 474, 38, 8, 14), A['bronze_dk'], seed=843, w=2.2)
    solid(S, ell(480, 520, 78, 92, 26), A['red_dk'], seed=844, w=3.0)                    # 鼓：土红灰（降过饱和）
    solid(S, ell(480, 520, 58, 70, 26), A['red'], seed=845, w=2.0)
    for k in range(10):
        a = k / 10 * 2 * math.pi
        dots(S, [(480 + 71 * math.cos(a), 520 + 84 * math.sin(a), 2.6)], A['gold_lt'], op=0.85)
    save2('hut_in_far', S, variants=('night', 'lit'), gain=0.66, keep=0.22, lights=[(lm, WINDOW_LIGHT)])

    Nn = Canvas(W, H)
    xs = np.arange(W, dtype=F)
    ground_strip(Nn, GY + 2.5 * np.sin(xs / 210.0), 1080, A['plank'], A['plank_dk'], seed=851, tex=0.8, tex_col=A['plank_dk'])
    for x0_ in np.linspace(-300, 2700, 17):
        brush(Nn, [(1200 + (x0_ - 1200) * 0.5, 840), (x0_, 1080)], w0=2.4, color=INK, op=0.35, seed=int(x0_) % 913 + 20, taper=0.02, wob=0.8, dry=0.3, smooth=False)
    r = np.random.default_rng(852)
    for i in range(16):    # 地上的尘土
        wash(Nn, ell(r.uniform(60, W - 60), r.uniform(860, 1060), r.uniform(40, 130), r.uniform(8, 18), 12), hexc('#cfcbbd'), op=r.uniform(0.25, 0.5), wob=3, seed=860 + i, smooth=2, rim=0.0)
    # 桌子（x≈1200，桌面 y≈690，宽 560），桌面积灰；桌上：几张纸、一本书、一支笔；中央 x≈1200 留空放铜铃
    tt = table(Nn, 1200, 690, 560, seed=870, dust=0.55)
    for (px, py, pw, sd) in ((990, tt - 3, 90, 880), (1010, tt - 6, 80, 881)):
        solid(Nn, [(px - pw / 2, py), (px + pw / 2, py - 4), (px + pw / 2 + 4, py + 4), (px - pw / 2 + 2, py + 6)], hexc('#d9d4c6'), seed=sd, w=1.5, tex=0.1)
    solid(Nn, [(1400, tt), (1480, tt - 2), (1484, tt - 22), (1404, tt - 20)], A['cloth_dk'], seed=885, w=2.0)          # 一本书
    wash(Nn, [(1404, tt - 18), (1480, tt - 20), (1480, tt - 8), (1404, tt - 8)], hexc('#d9d4c6'), op=0.9, wob=0.5, seed=886, smooth=0, rim=0.0)
    brush(Nn, [(1330, tt - 5), (1380, tt - 9)], w0=4, color=A['wood_dk'], op=0.95, seed=887, taper=0.1)                      # 一支笔
    # 古琴：横在 x≈1700 的矮几上
    solid(Nn, [(1560, GY - 70), (1840, GY - 70), (1840, GY - 52), (1560, GY - 52)], A['wood'], seed=890, w=2.4)
    for lx in (1580, 1820):
        leg(Nn, lx, GY - 52, GY + 6, 16, 891 + lx % 7)
    qin = [(1530, GY - 120), (1870, GY - 124), (1880, GY - 100), (1860, GY - 76), (1540, GY - 74), (1520, GY - 98)]
    solid(Nn, qin, A['wood_dk'], seed=895, w=2.8)
    for k in range(7):
        brush(Nn, [(1550, GY - 114 + k * 4.4), (1860, GY - 117 + k * 4.4)], w0=1.0, color=hexc('#e3dfd0'), op=0.7, seed=896 + k, taper=0.05, smooth=False)
    for k in range(9):
        dots(Nn, [(1600 + k * 28, GY - 122, 2.2)], hexc('#e3dfd0'), op=0.8)
    save2('hut_in_near', Nn, variants=('night', 'lit'), gain=0.68, keep=0.24)

    # hut_in_clean：叠在 near 上的一层（扫净的地面、刷干净的桌面、擦亮的鼓）——用整片不透明的新地面盖住尘土
    Cn = Canvas(W, H)
    ground_strip(Cn, GY + 2.5 * np.sin(xs / 210.0), 1080, mix(A['plank'], A['paper'], 0.18), A['plank'], seed=851, tex=0.6, tex_col=A['plank_dk'])
    for x0_ in np.linspace(-300, 2700, 17):
        brush(Cn, [(1200 + (x0_ - 1200) * 0.5, 840), (x0_, 1080)], w0=2.0, color=INK, op=0.28, seed=int(x0_) % 913 + 20, taper=0.02, wob=0.8, dry=0.3, smooth=False)
    wash(Cn, [(940, 686), (1460, 686), (1470, 700), (930, 700)], mix(A['wood_lt'], A['paper'], 0.35), op=0.9, wob=0.6, seed=905, smooth=0, rim=0.15)       # 桌面刷净
    glow(Cn, 480, 500, 110, hexc('#ffffff'), op=0.0, power=2.0)
    save2('hut_in_clean', Cn, variants=('night', 'lit'), gain=0.72, keep=0.26)


# ═════════════════════════ 殿上 ═════════════════════════
if 'hall' in which:
    S = Canvas(W, H, bg=hexc('#7a746c'))
    lm = LightMap(W, H)
    rwash(S, 0, 0, W, 840, A['wood_dk'] * 1.1, op=1.0, wob=1.0, seed=901, tex_k=0.14, rim=0.0)
    wash(S, rect(0, 0, W, 840), hexc('#6b6e78'), op=0.30, wob=1, seed=902, smooth=0, rim=0.0)
    roof_underside(S, -10, W + 10, 0, 96, seed=903)                         # 梁枋 / 藻井的暗影
    dougong(S, -10, W + 10, 96, 130, pitch=96, seed=904)
    # 高窗：冷白的光
    for k, x_ in enumerate((560, 880, 1520, 1840)):
        lattice_panel(S, x_ - 70, 190, x_ + 70, 420, nx=3, ny=5, seed=910 + k, lm=lm, light=0.9)
    # 宝座后的大屏风（灰蓝，沿边一圈灰金）：x 760~1640，y 200~700
    rwash(S, 756, 196, 1644, 706, A['blue_dk'], op=1.0, wob=0.8, seed=920, tex_k=0.2, rim=0.2)
    boxline(S, 756, 196, 1644, 706, w=3.4, op=0.8, seed=921)
    for (yy, sd) in ((214, 922), (688, 923)):
        rwash(S, 756, yy - 7, 1644, yy + 7, A['gold'], op=0.85, wob=0.5, seed=sd, tex_k=0.1, rim=0.0)
    for k in range(6):          # 屏风上淡淡的水纹云纹
        cy_ = 300 + k * 66
        brush(S, [(800 + k * 30, cy_), (900 + k * 60, cy_ - 22), (1040 + k * 40, cy_ + 8), (1200 + k * 20, cy_ - 16), (1380 - k * 20, cy_ + 10), (1580 - k * 30, cy_ - 8)], w0=3, color=A['blue_lt'], op=0.35, seed=925 + k, wob=2, taper=0.3, dry=0.3)
    # 两侧的帷幔（灰蓝 / 灰金）
    for (x_, c_, sd) in ((140, A['cloth'], 930), (2260, A['gold'], 931)):
        wash(S, [(x_ - 70, 140), (x_ + 70, 140), (x_ + 60, 480), (x_ + 20, 560), (x_ - 40, 470), (x_ - 62, 560)], c_, op=0.88, wob=1.5, seed=sd, smooth=1, tex_k=0.2, rim=0.2)
    save2('hall_king_far', S, variants=('night', 'lit'), gain=0.62, keep=0.2, lights=[(lm, WINDOW_LIGHT)])

    Nn = Canvas(W, H)
    lm2 = LightMap(W, H)
    floor_surface(Nn, 0, 800, W, H, A['brick'] * 0.98, vp=(1200, 380), tile_px=130, tile_h_px=50, seed=941, var=0.08)
    # 三级台阶的高台：台面 y≈640，向前三级落到 y≈832；宝座在台上（座面 y≈640）
    cx = 1200
    steps = [(640, 706, 330, 360), (706, 772, 360, 410), (772, 832, 410, 470)]
    for k, (yt, yb, hwt, hwb) in enumerate(steps):
        solid(Nn, [(cx - hwb, yb), (cx - hwt, yt), (cx + hwt, yt), (cx + hwb, yb)], A['slab'] if k % 2 == 0 else A['slab_lt'], seed=950 + k, w=2.6)
        wash(Nn, [(cx - hwt, yt), (cx + hwt, yt), (cx + hwt + 4, yt + 8), (cx - hwt - 4, yt + 8)], hexc('#ffffff'), op=0.25, wob=0.5, seed=955 + k, smooth=0, rim=0.0)
    # 宝座：高背椅（灰金 / 土黄），座面 y≈640；国王精灵（含袍摆，底边 y=640）坐在它前面
    back = [(cx - 190, 640), (cx - 200, 250), (cx - 160, 190), (cx + 160, 190), (cx + 200, 250), (cx + 190, 640)]
    solid(Nn, back, A['gold_dk'], seed=960, w=3.4)
    wash(Nn, [(cx - 168, 640), (cx - 176, 262), (cx - 142, 214), (cx + 142, 214), (cx + 176, 262), (cx + 168, 640)], A['gold'], op=0.8, wob=1.0, seed=961, smooth=0, rim=0.2)
    for k in range(2):      # 靠背上的回纹框和卷云
        boxline(Nn, cx - 150 + k * 18, 250 + k * 18, cx + 150 - k * 18, 600 - k * 18, w=2.2, op=0.5, seed=966 + k)
    for sx_ in (-1, 1):
        brush(Nn, [(cx + sx_ * 120, 320), (cx + sx_ * 60, 300), (cx + sx_ * 40, 350), (cx + sx_ * 84, 372), (cx + sx_ * 92, 336)], w0=3, color=A['gold_dk'], op=0.8, seed=970 + sx_, wob=0.8, taper=0.2)
    solid(Nn, ell(cx, 228, 64, 22, 18), A['gold_lt'], seed=972, w=2.2)
    for (ax_, sd) in ((-1, 962), (1, 963)):     # 扶手
        solid(Nn, [(cx + ax_ * 190, 520), (cx + ax_ * 236, 520), (cx + ax_ * 236, 646), (cx + ax_ * 190, 646)], A['gold_dk'], seed=sd, w=2.6)
    brush(Nn, [(cx - 120, 230), (cx - 40, 214), (cx + 40, 214), (cx + 120, 230)], w0=3, color=A['gold_lt'], op=0.7, seed=964, wob=1, taper=0.2)
    wash(Nn, [(cx - 212, 640), (cx + 212, 640), (cx + 222, 672), (cx - 222, 672)], A['gold_dk'], op=0.98, wob=0.8, seed=965, smooth=0, tex_k=0.22, rim=0.2)    # 座面前沿
    # 两侧立柱（x≈330、x≈2070）：土红灰，带柱础
    for k, x_ in enumerate((330, 2070)):
        column(Nn, x_, 120, GY + 14, 116, seed=970 + k, base=True, base_h=44, grain_n=80)
    # 立柱上的宫灯（纸白冷光）
    for k, x_ in enumerate((470, 1930)):
        lantern(Nn, x_, 300, 24, seed=980 + k, lm=lm2, cord=150)
    save2('hall_king_near', Nn, variants=('night', 'lit'), gain=0.6, keep=0.2, lights=[(lm2, WINDOW_LIGHT)])
