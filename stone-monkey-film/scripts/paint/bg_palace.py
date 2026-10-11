"""海底宫殿外景（S3）：2900×1080。far（水体渐变 + 斜射的光柱 + 远处的珊瑚岩 + 悬浮的细粒）/ mid（宫殿正面：贝壳和彩石搭的中式宫门 + 珊瑚海草）/ near（海底沙地 + 光斑 + 前景海草）。
宫殿中心 x≈1900，宽≈900（x1450~2350），顶 y≈268；门洞 x 1790~2010、y 482~812（宽 220 高 330），门板是珍珠白的贝壳片镶嵌；门前 x 1400~1750 是空地。
颜色：全部是降了饱和度的珠光灰（珍珠白、灰粉、土黄、石板蓝），窗里的光是纸白。
用法：python3 bg_palace.py [far mid near]"""
from ccommon import *
from cn_water import *
import sys

W, H = 2900, 1080
which = sys.argv[1:] or ['far', 'mid', 'near']
CX = 1900
GY = 832


def arch_y(x, cx, hw, spring, rise):
    u = np.clip((np.asarray(x, F) - cx) / hw, -1, 1)
    return spring - rise * np.sqrt(1 - u ** 2)


def eave_curve(cx, y, w, up, n=26):
    xs = np.linspace(-1, 1, n)
    return [(cx + x * w / 2, y - up * abs(x) ** 3.0) for x in xs]


def outline(L, pts, w=2.2, op=0.6, seed=0, dry=0.3, smooth=False):
    brush(L, pts, w0=w, color=INK, op=op, seed=seed, wob=0.7, taper=0.1, dry=dry, smooth=smooth)


def shell_roof(L, cx, y_eave, w, rise, up=26, seed=0, size=16, cols=None, ridge_w=0.6, fascia=14):
    """中式屋顶（正面）：贝壳瓦（石板蓝、灰粉为主，珠光白点缀）+ 檐口一圈瓦当 + 脊 + 脊端的珊瑚饰。"""
    cols = [NW['slate'], NW['slate_lt'], NW['pearl_sh'], NW['pink_dk'], NW['slate_dk']] if cols is None else cols
    low = eave_curve(cx, y_eave, w, up)
    tipL, tipR = low[0], low[-1]
    rl, rr = cx - w * ridge_w / 2, cx + w * ridge_w / 2
    yr = y_eave - rise
    sl = [(tipL[0] + (rl - tipL[0]) * t, tipL[1] + (yr - tipL[1]) * t ** 1.7) for t in np.linspace(0, 1, 10)]
    sr = [(tipR[0] + (rr - tipR[0]) * t, tipR[1] + (yr - tipR[1]) * t ** 1.7) for t in np.linspace(0, 1, 10)]
    poly = low + sr[::-1][:] + sl[1:]
    poly = low + sr[::-1] + [(rl, yr)] + sl[::-1][:-1][::-1][1:][::-1] if False else low + sr[::-1] + sl[1:][::1][::-1][::-1]
    # 上面一行有点绕：外轮廓 = 檐口曲线（左→右）→ 右坡（右檐角→脊右端）→ 脊（右→左）→ 左坡（脊左端→左檐角）
    poly = low + sr[1:] + [(rl, yr)] + sl[1:][::-1][:-1]
    shell_scales(L, poly, size=size, cols=cols, seed=seed, op=1.0, line=0.55)
    # 屋面受光的一道亮
    wash(L, [(rl + 20, yr + 4), (rr - 20, yr + 4), (rr - 50, yr + rise * 0.35), (rl + 50, yr + rise * 0.35)], NW['pearl'], op=0.22, wob=2, seed=seed + 1, smooth=2, tex_k=0.1, rim=0.0)
    # 檐口：一条深色的封檐板 + 一圈瓦当
    fas = [(x, y) for x, y in low] + [(x, y + fascia) for x, y in low[::-1]]
    wash(L, fas, NW['slate_dk'] * 0.95, op=0.97, wob=0.6, seed=seed + 2, smooth=0, tex_k=0.2, rim=0.2, rim_w=2)
    dots(L, [(x, y + fascia * 0.62, 3.6) for x, y in low[1:-1:1]], NW['pearl'], op=0.85)
    outline(L, low, w=2.6, op=0.75, seed=seed + 3)
    outline(L, [(x, y + fascia) for x, y in low], w=2.0, op=0.6, seed=seed + 4)
    outline(L, sl, w=2.4, op=0.7, seed=seed + 5)
    outline(L, sr, w=2.4, op=0.7, seed=seed + 6)
    # 脊：珠光的一条 + 脊端的珊瑚饰
    wash(L, [(rl - 16, yr - 10), (rr + 16, yr - 10), (rr + 10, yr + 6), (rl - 10, yr + 6)], NW['pearl'], op=0.97, wob=0.8, seed=seed + 7, smooth=1, tex_k=0.15, rim=0.25, rim_w=2)
    outline(L, [(rl - 16, yr - 10), (rr + 16, yr - 10)], w=2.0, op=0.6, seed=seed + 8)
    outline(L, [(rl - 10, yr + 6), (rr + 10, yr + 6)], w=1.8, op=0.5, seed=seed + 9)
    for s_ in (-1, 1):
        ex = (rl - 16) if s_ < 0 else (rr + 16)
        coral_antler(L, ex, yr - 8, 38, seed=seed + 20 + s_, col=NW['pearl'], dk=NW['pearl_dk'], depth=3, w=5, spread=0.7)
    return low, (rl, rr, yr)


def brackets(L, cx, y, w, n, seed=0):
    """檐下的斗拱（简化成一排阶梯状的小块）。"""
    r = np.random.default_rng(seed)
    for i in range(n):
        x = cx - w / 2 + (i + 0.5) * w / n
        wash(L, [(x - 9, y), (x + 9, y), (x + 9, y + 7), (x - 9, y + 7)], NW['pearl_dk'], op=0.97, wob=0.4, seed=int(r.integers(1e6)), smooth=0, rim=0.25)
        wash(L, [(x - 6, y + 7), (x + 6, y + 7), (x + 6, y + 15), (x - 6, y + 15)], NW['slate'], op=0.97, wob=0.4, seed=int(r.integers(1e6)), smooth=0, rim=0.25)
        outline(L, [(x - 9, y), (x + 9, y), (x + 9, y + 7), (x + 6, y + 7), (x + 6, y + 15), (x - 6, y + 15), (x - 6, y + 7), (x - 9, y + 7), (x - 9, y)], w=1.3, op=0.5, seed=int(r.integers(1e6)))


def pillar(L, x, y0, y1, w=22, seed=0, col=None):
    """柱：珍珠白的圆柱（左亮右暗），柱头一块石板蓝的墩，柱脚一块础石。"""
    col = NW['pearl'] if col is None else col
    wash(L, [(x - w / 2, y0), (x + w / 2, y0), (x + w / 2, y1), (x - w / 2, y1)], col, op=0.97, wob=0.6, seed=seed, smooth=0, tex_k=0.18, rim=0.2, rim_w=2)
    wash(L, [(x + w * 0.1, y0), (x + w / 2, y0), (x + w / 2, y1), (x + w * 0.1, y1)], NW['pearl_sh'], op=0.55, wob=0.5, seed=seed + 1, smooth=0, tex_k=0.1)
    brush(L, [(x - w * 0.3, y0 + 6), (x - w * 0.3, y1 - 6)], w0=3, color=NW['pearl'] * 1.04, op=0.7, seed=seed + 2, taper=0.2, dry=0.3)
    outline(L, [(x - w / 2, y0), (x - w / 2, y1)], w=2.0, op=0.55, seed=seed + 3)
    outline(L, [(x + w / 2, y0), (x + w / 2, y1)], w=2.0, op=0.6, seed=seed + 4)
    wash(L, [(x - w * 0.75, y0), (x + w * 0.75, y0), (x + w * 0.65, y0 + 14), (x - w * 0.65, y0 + 14)], NW['slate'], op=0.97, wob=0.5, seed=seed + 5, smooth=0, rim=0.25)
    outline(L, [(x - w * 0.75, y0), (x + w * 0.75, y0), (x + w * 0.65, y0 + 14), (x - w * 0.65, y0 + 14), (x - w * 0.75, y0)], w=1.5, op=0.55, seed=seed + 6)
    wash(L, [(x - w * 0.8, y1 - 14), (x + w * 0.8, y1 - 14), (x + w * 0.95, y1), (x - w * 0.95, y1)], NW['pearl_dk'], op=0.97, wob=0.5, seed=seed + 7, smooth=0, rim=0.25)
    outline(L, [(x - w * 0.8, y1 - 14), (x + w * 0.8, y1 - 14)], w=1.5, op=0.5, seed=seed + 8)


def round_window(L, x, y, r_, seed=0, glow_k=1.0):
    """圆窗：纸白的光 + 细细的窗棂（米字）+ 一圈石板蓝的框。"""
    pts = [(x + math.cos(a) * r_, y + math.sin(a) * r_) for a in np.linspace(0, 2 * math.pi, 28, endpoint=False)]
    glow(L, x, y, r_ * 3.2, NW['pearl'], op=0.22 * glow_k, power=2.0)
    wash(L, pts, hexc('#f2f1ea'), op=0.98, wob=0.4, seed=seed, smooth=2, tex_k=0.08, rim=0.0)
    wash(L, [(x + math.cos(a) * r_ * 0.8, y + math.sin(a) * r_ * 0.8) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)], hexc('#ffffff'), op=0.55, wob=0.4, seed=seed + 1, smooth=2, rim=0.0)
    for k in range(4):
        a = k * math.pi / 4
        brush(L, [(x - math.cos(a) * r_, y - math.sin(a) * r_), (x + math.cos(a) * r_, y + math.sin(a) * r_)], w0=1.8, color=NW['slate_dk'], op=0.75, seed=seed + 5 + k, taper=0.05, smooth=False)
    brush(L, pts + [pts[0]], w0=4.2, color=NW['slate'], op=0.97, seed=seed + 9, wob=0.3, taper=0.02)
    brush(L, pts + [pts[0]], w0=1.6, color=INK, op=0.6, seed=seed + 10, wob=0.3, taper=0.02)


def shell_string(L, x, y, n, seed=0, gap=14, op=0.9):
    """檐角挂着的一串贝壳风铃：一根细线，下面几枚小贝壳 / 珠子。"""
    r = np.random.default_rng(seed)
    ln = n * gap
    brush(L, [(x, y), (x + r.normal(0, 1.5), y + ln)], w0=1.2, color=NW['pearl_dk'], op=0.7 * op, seed=seed, taper=0.05)
    for i in range(n):
        yy = y + (i + 0.5) * gap + 4
        if i == n - 1:
            scallop(L, x, yy - 4, 7, seed=seed + 3 + i, col=NW['pearl'], tilt=math.pi, ribs=5, op=op)
        else:
            dots(L, [(x, yy, r.uniform(2.2, 3.4))], NW['pearl'], op=op)


# ═════════════════════════ far ═════════════════════════
if 'far' in which:
    S = Canvas(W, H, bg=0.0)
    fill_region(S, 0, 0, W, H, hexc('#8dacaf'), hexc('#2b4352'), seed=201, mott=0.2, gamma=0.85, scale=320)
    # 斜射下来的光柱
    light_shafts(S, [(260, 130, 560, 320, 0, 900, 0.8), (880, 180, 1250, 400, 0, 900, 1.0), (1480, 110, 1700, 280, 0, 900, 0.55), (2020, 200, 2400, 440, 0, 900, 0.95), (2600, 130, 2880, 320, 0, 900, 0.7)], seed=1, op=0.26)
    # 远处的珊瑚岩（一层又一层，越远越淡）
    base = 790
    r1 = ridge_y(W, base, 330, 211, rough=0.55, scale=380)
    mountain(S, r1, 880, NW['uw_hi'] * 0.95, NW['uw'] * 0.9, seed=31, tex=0.5, tex_op=0.22, haze=0.5, haze_col=NW['uw_hi'], glaze=0.35, lit_dir=1, rim_op=0.3)
    mist(S, 0, W, 760, 90, seed=32, op=0.55, color=NW['uw_hi'], scale=300)
    base = 830
    r2 = ridge_y(W, base, 230, 212, rough=0.55, scale=300)
    mountain(S, r2, 900, NW['uw'], NW['uw_dk'], seed=33, tex=0.7, tex_op=0.28, haze=0.3, haze_col=NW['uw_hi'], glaze=0.45, lit_dir=1, rim_op=0.4)
    mist(S, 0, W, 800, 80, seed=34, op=0.5, color=NW['uw_hi'], scale=280)
    # 远处几丛摇曳的海草（淡淡的）
    for i, x in enumerate([180, 620, 1060, 1320, 2540, 2760]):
        seaweed(S, x, 830 + (i % 3) * 8, 180 + (i * 37) % 90, seed=40 + i, n=4, col=NW['uw'] * 0.95, dk=NW['uw_dk'], sway=0.35, op=0.55)
    floaters(S, 0, 40, W, 800, 330, seed=7, op=0.5)
    save_plate('palace_far', S, variants=('night', 'lit'), gain=0.62, keep=0.18)

# ═════════════════════════ mid ═════════════════════════
if 'mid' in which:
    M = Canvas(W, H)
    # 宫殿后面的一团光（让它从深水里浮出来）
    glow(M, CX, 560, 640, NW['pearl'], op=0.28, power=2.0)
    # 背后的珊瑚树
    coral_antler(M, 1330, 836, 300, seed=301, depth=4)
    coral_antler(M, 2470, 836, 340, seed=302, depth=4, col=NW['pearl_dk'], dk=NW['pink_dk'])
    coral_fan(M, 1240, 836, 220, seed=303)
    coral_fan(M, 2590, 836, 260, seed=304, col=NW['pink'])
    # ── 左右两翼：矮墙 + 一道檐
    for (cx_, sd, sgn) in ((1565, 410, -1), (2235, 420, 1)):
        wall = [(cx_ - 115, 650), (cx_ + 115, 650), (cx_ + 115, 840), (cx_ - 115, 840)]
        shell_scales(M, wall, size=19, cols=[NW['pearl'], NW['pearl_dk'], NW['pink'], NW['ochre'], NW['slate_lt']], seed=sd, line=0.5)
        outline(M, [(cx_ - 115, 650), (cx_ - 115, 832)], w=2.2, op=0.6, seed=sd + 1)
        outline(M, [(cx_ + 115, 650), (cx_ + 115, 832)], w=2.2, op=0.6, seed=sd + 2)
        low, rg = shell_roof(M, cx_, 650, 300, 50, up=24, seed=sd + 3, size=15, ridge_w=0.62, fascia=12)
        brackets(M, cx_, 664, 190, 8, seed=sd + 4)
        round_window(M, cx_, 748, 32, seed=sd + 5)
        pillar(M, cx_ - 112, 664, 832, w=17, seed=sd + 6)
        pillar(M, cx_ + 112, 664, 832, w=17, seed=sd + 7)
        shell_string(M, low[0][0] + 4 * (-sgn), low[0][1] + 12, 5, seed=sd + 8)
        shell_string(M, low[-1][0] - 4 * (-sgn), low[-1][1] + 12, 5, seed=sd + 9)
    # ── 主体：下层墙（有门洞）
    wall = [(1680, 470), (2120, 470), (2120, 846), (1680, 846)]
    shell_scales(M, wall, size=21, cols=[NW['pearl'], NW['pearl_dk'], NW['pink'], NW['ochre'], NW['slate_lt']], seed=430, line=0.5)
    # 门洞：拱
    GCX, HW, SPR, RISE, BOT = 1900, 110, 528, 46, 812
    xs = np.linspace(GCX - HW, GCX + HW, 30)
    ay = arch_y(xs, GCX, HW, SPR, RISE)
    # 先挖一个黑一点的门洞（门板后的暗）
    opening = [(x, y) for x, y in zip(xs, ay)] + [(GCX + HW, BOT), (GCX - HW, BOT)]
    wash(M, opening, NW['uw_deep'], op=0.0, seed=1)
    # 拱圈：石板蓝的一圈，带券石的放射线
    outer = [(x, y - 16 * (1 - 0.3 * abs(x - GCX) / HW)) for x, y in zip(xs, ay)]
    ring = outer + [(x, y) for x, y in zip(xs[::-1], ay[::-1])]
    wash(M, ring + [], NW['slate'], op=0.97, wob=0.6, seed=431, smooth=0, tex_k=0.2, rim=0.25, rim_w=2)
    for k in range(1, 13):
        i = int(k / 13 * (len(xs) - 1))
        brush(M, [(xs[i], ay[i]), (outer[i][0], outer[i][1])], w0=1.5, color=NW['slate_dk'], op=0.7, seed=440 + k, taper=0.2, smooth=False)
    outline(M, outer, w=2.4, op=0.65, seed=432)
    # 两扇门：珍珠白的贝壳片镶嵌
    for (xa, xb, sd) in ((GCX - HW, GCX - 2, 450), (GCX + 2, GCX + HW, 460)):
        yt = arch_y(np.array([xa, (xa + xb) / 2, xb], F), GCX, HW, SPR, RISE)
        pts = []
        for x in np.linspace(xa, xb, 12):
            pts.append((x, float(arch_y(np.array([x], F), GCX, HW, SPR, RISE)[0])))
        leaf = pts + [(xb, BOT), (xa, BOT)]
        shell_scales(M, leaf, size=13, cols=[NW['pearl'], hexc('#f4f1e8'), NW['pearl'], NW['pearl_dk'], NW['pink']], seed=sd, line=0.4, shade=NW['pearl_sh'])
        wash(M, leaf, hexc('#ffffff'), op=0.18, wob=1, seed=sd + 1, smooth=0, rim=0.0)
        # 门边框、横档
        outline(M, [(xa + 5, pts[0][1] + 18), (xa + 5, BOT)], w=3.0, op=0.55, seed=sd + 2, dry=0.2)
        outline(M, [(xb - 5, pts[-1][1] + 18), (xb - 5, BOT)], w=3.0, op=0.55, seed=sd + 3, dry=0.2)
        for yy in (600, 700):
            brush(M, [(xa + 5, yy), (xb - 5, yy)], w0=5, color=NW['slate'], op=0.9, seed=sd + 4 + yy, taper=0.05, wob=0.6)
            outline(M, [(xa + 5, yy - 2.5), (xb - 5, yy - 2.5)], w=1.3, op=0.5, seed=sd + 8 + yy)
        # 门钉（珠）
        for rx in range(3):
            for ry in range(2):
                x_ = xa + 22 + rx * (xb - xa - 44) / 2
                y_ = 628 + ry * 72 + 30
                dots(M, [(x_, y_, 4.0)], hexc('#fbfaf5'), op=0.95)
                dots(M, [(x_ + 1, y_ + 1.5, 4.6)], NW['pearl_sh'], op=0.35)
    # 门缝 + 门环（圆的珠光铜环，不是金）
    brush(M, [(GCX, 520), (GCX, BOT)], w0=3.2, color=INK, op=0.7, seed=470, taper=0.05, dry=0.2)
    for sx in (-1, 1):
        cx_, cy_ = GCX + sx * 18, 700
        wash(M, [(cx_ + math.cos(a) * 13, cy_ + math.sin(a) * 13) for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)], NW['pearl_dk'], op=0.97, wob=0.3, seed=480 + sx, smooth=2, rim=0.3)
        brush(M, [(cx_ + math.cos(a) * 8, cy_ + 12 + math.sin(a) * 9) for a in np.linspace(-0.3, math.pi + 0.3, 12)], w0=3.2, color=NW['slate_dk'], op=0.85, seed=490 + sx, wob=0.3, taper=0.1)
    # 门前的石阶：两级
    for (xa, xb, y0, y1, sd) in ((1740, 2060, 822, 840, 500), (1768, 2032, 808, 824, 510)):
        wash(M, [(xa, y0), (xb, y0), (xb + 6, y1), (xa - 6, y1)], NW['pearl_dk'], op=0.97, wob=0.8, seed=sd, smooth=0, tex_k=0.2, rim=0.2)
        wash(M, [(xa, y0), (xb, y0), (xb, y0 + 4), (xa, y0 + 4)], NW['pearl'], op=0.8, wob=0.4, seed=sd + 1, smooth=0, rim=0.0)
        outline(M, [(xa, y0), (xb, y0)], w=2.0, op=0.6, seed=sd + 2)
    # 中柱、边柱
    for (x_, sd) in ((1700, 520), (1792, 521), (2008, 522), (2100, 523)):
        pillar(M, x_, 482, 832, w=24 if x_ in (1700, 2100) else 20, seed=sd)
    # 门额：一块匾（空白的珠光板，边框是石板蓝）
    wash(M, [(1840, 484), (1960, 484), (1960, 506), (1840, 506)], NW['pearl'], op=0.97, wob=0.5, seed=530, smooth=0, rim=0.25)
    outline(M, [(1840, 484), (1960, 484), (1960, 506), (1840, 506), (1840, 484)], w=2.0, op=0.6, seed=531)
    for k in range(4):
        brush(M, [(1856 + k * 28, 490), (1860 + k * 28, 500), (1868 + k * 28, 492)], w0=1.4, color=NW['slate_dk'], op=0.5, seed=532 + k, taper=0.3)
    # ── 下层屋檐
    low1, rg1 = shell_roof(M, CX, 464, 640, 74, up=30, seed=540, size=17, ridge_w=0.56, fascia=16)
    brackets(M, CX, 480, 440, 17, seed=541)
    # ── 上层：窗 + 窄一圈的墙 + 上层屋檐
    wall2 = [(1744, 330), (2056, 330), (2056, 396), (1744, 396)]
    shell_scales(M, wall2, size=17, cols=[NW['pearl'], NW['pearl_dk'], NW['pink'], NW['slate_lt']], seed=550, line=0.5)
    outline(M, [(1744, 336), (1744, 398)], w=2.0, op=0.6, seed=551)
    outline(M, [(2056, 336), (2056, 398)], w=2.0, op=0.6, seed=552)
    for x_ in (1818, 1900, 1982):
        round_window(M, x_, 366, 20, seed=560 + int(x_))
    for x_ in (1744, 2056):
        pillar(M, x_, 336, 398, w=15, seed=570 + int(x_))
    low2, rg2 = shell_roof(M, CX, 338, 470, 72, up=26, seed=580, size=15, ridge_w=0.58, fascia=13)
    brackets(M, CX, 352, 320, 11, seed=581)
    # 宝顶：脊中央一颗珠（纸白）+ 小小的珊瑚尖
    px, py = CX, rg2[2] - 18
    glow(M, px, py, 54, hexc('#ffffff'), op=0.4, power=2.0)
    wash(M, [(px + math.cos(a) * 11, py + math.sin(a) * 12) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)], hexc('#f6f5ee'), op=0.98, wob=0.3, seed=590, smooth=2, rim=0.15)
    wash(M, [(px - 6, py + 11), (px + 6, py + 11), (px + 8, py + 20), (px - 8, py + 20)], NW['pearl_dk'], op=0.97, wob=0.3, seed=591, smooth=0)
    # 檐角的贝壳风铃
    for (lw, sd) in ((low1, 600), (low2, 610)):
        shell_string(M, lw[0][0] + 6, lw[0][1] + 18, 4, seed=sd)
        shell_string(M, lw[-1][0] - 6, lw[-1][1] + 18, 4, seed=sd + 1)
    # 柱脚、台基：一条宽宽的珠光石基，把整座宫殿托在海底
    base = [(1420, 826), (2380, 826), (2392, 846), (1408, 846)]
    wash(M, base, NW['pearl_dk'], op=0.97, wob=0.9, seed=620, smooth=0, tex_k=0.2, rim=0.22)
    wash(M, [(1420, 826), (2380, 826), (2380, 832), (1420, 832)], NW['pearl'], op=0.8, wob=0.5, seed=621, smooth=0, rim=0.0)
    outline(M, [(1420, 826), (1900, 827), (2380, 826)], w=2.2, op=0.6, seed=622)
    # 前景两侧的珊瑚、海草
    coral_antler(M, 1380, 848, 150, seed=701, depth=3, col=NW['pink'], dk=NW['pink_dk'])
    coral_mound(M, 2440, 846, 110, 52, seed=702)
    coral_antler(M, 2680, 846, 210, seed=703, depth=4)
    coral_fan(M, 2790, 846, 170, seed=704, col=NW['pearl_dk'])
    coral_mound(M, 1120, 846, 130, 60, seed=705, col=NW['pink'])
    coral_fan(M, 1010, 846, 200, seed=706)
    seaweed(M, 1180, 846, 300, seed=710, n=6, sway=0.4)
    seaweed(M, 2540, 846, 260, seed=711, n=5, sway=0.4)
    seaweed(M, 2860, 846, 330, seed=712, n=6, sway=0.4)
    seaweed(M, 760, 846, 260, seed=713, n=5, sway=0.4)
    coral_antler(M, 520, 846, 190, seed=714, depth=4, col=NW['pearl_dk'], dk=NW['pink_dk'])
    seaweed(M, 330, 846, 240, seed=715, n=5, sway=0.4)
    floaters(M, 1500, 250, 2300, 800, 70, seed=9, op=0.8)
    save_plate('palace_mid', M, variants=('night', 'lit'), gain=0.82, keep=0.2)

# ═════════════════════════ near ═════════════════════════
if 'near' in which:
    Nn = Canvas(W, H)
    xs = np.arange(W, dtype=F)
    gy = GY + 6 * np.sin(xs / 260.0) + 3.5 * np.sin(xs / 71.0 + 1)
    # 海底的沙：灰绿的、带潮纹
    ground_strip(Nn, gy, 1080, hexc('#9fb0a4'), hexc('#566f70'), seed=211, tex=0.8, tex_col=NW['uw_deep'])
    # 光斑：透过水面的光落在沙上
    caustics(Nn, 0, 850, W, 1060, 212, n=170, col=NW['pearl'], op=0.3)
    r = np.random.default_rng(213)
    for _ in range(40):   # 沙纹
        x, y = r.uniform(0, W), r.uniform(850, 1070)
        ln = r.uniform(80, 260)
        brush(Nn, [(x, y), (x + ln * 0.5, y + r.normal(0, 3)), (x + ln, y + r.normal(0, 2))], w0=r.uniform(2, 4.5), color=NW['uw_dk'], op=0.28, seed=int(r.integers(1e6)), wob=1.5, taper=0.4, dry=0.3)
    pebbles(Nn, 0, W, (850, 1060), 90, seed=214, col=NW['uw'] * 0.9, dk=NW['uw_deep'], rmin=3, rmax=10, op=0.9)
    # 贝壳
    for i in range(14):
        x, y = r.uniform(80, W - 80), r.uniform(870, 1050)
        if 1380 < x < 1780 and y < 900:
            continue
        if r.random() < 0.65:
            scallop(Nn, x, y, r.uniform(9, 17), seed=220 + i, col=NW['pearl'], tilt=r.normal(0, 0.5))
        else:
            spiral_shell(Nn, x, y, r.uniform(5, 8), seed=240 + i, col=NW['pearl_dk'])
    # 前景海草（稀的）：左右两边
    seaweed(Nn, 70, 960, 420, seed=250, n=6, sway=0.45, col=NW['uw'] * 0.75, dk=NW['uw_deep'])
    seaweed(Nn, 150, 990, 300, seed=251, n=4, sway=0.45, col=NW['uw'] * 0.75, dk=NW['uw_deep'])
    seaweed(Nn, 2840, 975, 430, seed=252, n=6, sway=0.45, col=NW['uw'] * 0.75, dk=NW['uw_deep'])
    seaweed(Nn, 2750, 1010, 280, seed=253, n=4, sway=0.45, col=NW['uw'] * 0.75, dk=NW['uw_deep'])
    seaweed(Nn, 1040, 1040, 200, seed=254, n=4, sway=0.4, col=NW['uw'] * 0.75, dk=NW['uw_deep'])
    coral_mound(Nn, 2400, 1030, 150, 60, seed=255, col=NW['pink'])
    floaters(Nn, 0, 300, W, 1000, 60, seed=11, op=0.7)
    save_plate('palace_near', Nn, variants=('night', 'lit'), gain=0.62, keep=0.2)
