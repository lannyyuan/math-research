"""海底两块补板（S3）：hall_sea（老龙的殿内，2400×1080，far + near）、spring（压着泉眼的青石，2900×1080，far + near + spring_clear）。
锚点见 PLATES.md：地面线 y=832；hall_sea 的圆形珊瑚台在 x≈1500（台面 y≈832，直径 520），左右珊瑚柱 x≈130 / x≈2270；
spring 的青石在 x≈1500（板上只画湿暗的泥），断木在 x≈1760~1800，小孔在 x≈1830；spring_clear 是 x 1380~2000 的一汪清水。
用法：python3 bg_sea_extra.py [hall_far] [hall_near] [spring_far] [spring_near] [spring_clear]"""
from ccommon import *
from cn_water import *
import sys

which = sys.argv[1:] or ['hall_far', 'hall_near', 'spring_far', 'spring_near', 'spring_clear']
GY = 832


def ell(cx, cy, rx, ry, n=22, a0=0.0, a1=2 * math.pi):
    return [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in np.linspace(a0, a1, n, endpoint=False if a1 - a0 >= 6.28 else True)]


def outline(L, pts, w=2.2, op=0.6, seed=0, dry=0.3):
    brush(L, pts, w0=w, color=INK, op=op, seed=seed, wob=0.7, taper=0.1, dry=dry, smooth=False)


# ═════════════════════════ hall_sea ═════════════════════════
if 'hall_far' in which:
    W, H = 2400, 1080
    S = Canvas(W, H, bg=0.0)
    fill_region(S, 0, 0, W, H, hexc('#a9c0c0'), hexc('#4a6a76'), seed=301, mott=0.16, gamma=0.8, scale=300)
    # 后墙：整面贝壳瓦的高墙，中间一座高大的拱门（门里是更亮的珠白光）
    wall = [(120, 150), (2280, 150), (2280, 840), (120, 840)]
    shell_scales(S, wall, size=26, cols=[NW['pearl'], NW['pearl_dk'], NW['pink'], NW['slate_lt'], NW['ochre']], seed=310, line=0.45, op=0.9)
    wash(S, wall, NW['uw'], op=0.28, wob=1, seed=311, smooth=0, rim=0.0)          # 蒙一层水色，让墙退到后面
    cx, hw = 1200, 360
    arch = [(cx - hw, 840)] + [(cx - hw * math.cos(a), 400 - 250 * math.sin(a)) for a in np.linspace(0, math.pi, 28)][::1] + [(cx + hw, 840)]
    arch = [(cx - hw, 840)] + [(cx + hw * math.cos(a), 410 - 260 * math.sin(a)) for a in np.linspace(math.pi, 0, 28)] + [(cx + hw, 840)]
    wash(S, arch, hexc('#f1f0e6'), op=0.96, wob=1, seed=312, smooth=0, tex_k=0.08, rim=0.1)
    glow(S, cx, 520, 520, hexc('#ffffff'), op=0.55, power=2.0)
    outline(S, [(cx - hw, 840), (cx - hw, 410)] + [(cx + hw * math.cos(a), 410 - 260 * math.sin(a)) for a in np.linspace(math.pi, 0, 28)] + [(cx + hw, 840)], w=4.0, op=0.65, seed=313)
    # 拱圈的券石
    for k in range(1, 15):
        a = math.pi * k / 15
        x0_, y0_ = cx + (hw + 4) * math.cos(a + math.pi), 410 - 264 * math.sin(a)
        x1_, y1_ = cx + (hw + 52) * math.cos(a + math.pi), 410 - 312 * math.sin(a)
        brush(S, [(x0_, y0_), (x1_, y1_)], w0=2.0, color=NW['slate_dk'], op=0.55, seed=320 + k, taper=0.2, smooth=False)
    # 半透明的珊瑚屏风：两扇，前面的珊瑚扇淡淡的透出后面的墙
    for (x_, sd) in ((560, 340), (1840, 350)):
        wash(S, [(x_ - 130, 840), (x_ - 130, 330), (x_ + 130, 330), (x_ + 130, 840)], NW['uw_hi'], op=0.22, wob=1.5, seed=sd, smooth=0, rim=0.2)
        outline(S, [(x_ - 130, 840), (x_ - 130, 330), (x_ + 130, 330), (x_ + 130, 840)], w=2.6, op=0.4, seed=sd + 1, dry=0.4)
        coral_fan(S, x_, 836, 400, seed=sd + 2, col=NW['pink'], op=0.7)
    # 从上面透下来的珠白的光
    light_shafts(S, [(500, 220, 760, 360, 0, 860, 1.0), (1200, 300, 1200, 480, 0, 860, 1.1), (1900, 220, 1640, 360, 0, 860, 0.95)], seed=5, op=0.30)
    floaters(S, 0, 40, W, 820, 260, seed=9, op=0.55)
    save_plate('hall_sea_far', S, variants=('night', 'lit'), gain=0.8, keep=0.22)

if 'hall_near' in which:
    W, H = 2400, 1080
    Nn = Canvas(W, H)
    xs = np.arange(W, dtype=F)
    gy = GY + 2.5 * np.sin(xs / 190.0)
    # 地板：珍珠母贝镶嵌（浅珠光 → 前景略深），隐约的倒影纹
    ground_strip(Nn, gy, 1080, hexc('#d8d6cc'), hexc('#7e9697'), seed=331, tex=0.5, tex_col=NW['uw_deep'])
    r = np.random.default_rng(332)
    for row in range(5):          # 地板的大方砖缝（透视：越近越宽）
        yy = 856 + row * row * 12 + row * 22
        brush(Nn, [(0, yy), (W / 2, yy + 2), (W, yy)], w0=2.0 + row * 0.5, color=NW['uw_dk'], op=0.35, seed=340 + row, taper=0.02, wob=0.8, dry=0.3)
    for x0_ in np.linspace(-200, 2600, 15):
        brush(Nn, [(1200 + (x0_ - 1200) * 0.55, 848), (x0_, 1080)], w0=2.2, color=NW['uw_dk'], op=0.30, seed=int(x0_) % 777 + 10, taper=0.02, wob=0.8, dry=0.3, smooth=False)
    caustics(Nn, 0, 860, W, 1070, 333, n=110, col=hexc('#ffffff'), op=0.30)
    for i in range(10):   # 嵌在地上的贝壳
        scallop(Nn, r.uniform(120, W - 120), r.uniform(880, 1050), r.uniform(10, 18), seed=350 + i, col=NW['pearl'], tilt=r.normal(0, 0.5))
    # 中间偏右的圆形珊瑚台：台面 y≈832，直径 520，厚 ≈ 64；台后要留出高高的空墙（精灵盘在上面）
    cx, cy = 1500, GY
    side = ell(cx, cy + 10, 262, 38, 40)
    body = [(cx - 262, cy + 10)] + [(cx + 262 * math.cos(a), cy + 70 + 40 * math.sin(a)) for a in np.linspace(math.pi, 0, 30)] + [(cx + 262, cy + 10)]
    wash(Nn, body, NW['pink_dk'], op=0.98, wob=1.2, seed=360, smooth=0, tex_k=0.2, rim=0.22)
    shell_scales(Nn, body, size=14, cols=[NW['pearl_dk'], NW['pink'], NW['pearl']], seed=361, line=0.4, op=0.85)
    wash(Nn, ell(cx, cy, 262, 38, 40), NW['pearl'], op=0.98, wob=1.0, seed=362, smooth=0, tex_k=0.12, rim=0.3)      # 台面
    outline(Nn, ell(cx, cy, 262, 38, 40) + [ell(cx, cy, 262, 38, 40)[0]], w=2.8, op=0.65, seed=363)
    outline(Nn, [(cx - 262, cy + 6)] + [(cx + 262 * math.cos(a), cy + 66 + 40 * math.sin(a)) for a in np.linspace(math.pi, 0, 24)] + [(cx + 262, cy + 6)], w=2.4, op=0.55, seed=364)
    coral_antler(Nn, cx - 300, GY + 70, 110, seed=365, depth=3, col=NW['pink'], dk=NW['pink_dk'])
    coral_mound(Nn, cx + 330, GY + 78, 110, 46, seed=366)
    # 左右两根高大的珊瑚柱（框住画面）
    for (x_, sd, sgn) in ((130, 370, 1), (2270, 380, -1)):
        col_ = [(x_ - 54, GY + 20), (x_ - 38, 40), (x_ + 38, 40), (x_ + 54, GY + 20)]
        wash(Nn, col_, NW['pearl_dk'], op=0.98, wob=1.5, seed=sd, smooth=0, tex_k=0.22, rim=0.25)
        shell_scales(Nn, col_, size=16, cols=[NW['pearl_dk'], NW['pink'], NW['pearl'], NW['slate_lt']], seed=sd + 1, line=0.4, op=0.85)
        wash(Nn, [(x_ - 54, GY + 20), (x_ - 38, 40), (x_ - 14, 40), (x_ - 20, GY + 20)], hexc('#ffffff'), op=0.22, wob=1.0, seed=sd + 2, smooth=0, rim=0.0)
        outline(Nn, [(x_ - 38, 40), (x_ - 54, GY + 20)], w=3.0, op=0.6, seed=sd + 3)
        outline(Nn, [(x_ + 38, 40), (x_ + 54, GY + 20)], w=3.0, op=0.6, seed=sd + 4)
        for yb in (260, 520):     # 柱身的箍
            brush(Nn, [(x_ - 46 + (yb - 260) * 0.012, yb), (x_ + 46 - (yb - 260) * 0.012, yb)], w0=7, color=NW['slate'], op=0.8, seed=sd + 5 + yb, taper=0.05, wob=0.6)
        coral_antler(Nn, x_ + sgn * 80, GY + 40, 190, seed=sd + 6, depth=3, col=NW['pink'], dk=NW['pink_dk'])
        coral_fan(Nn, x_ + sgn * 170, GY + 44, 150, seed=sd + 7, col=NW['pearl_dk'])
        seaweed(Nn, x_ + sgn * 20, 1040, 300, seed=sd + 8, n=5, sway=0.4, col=NW['uw'] * 0.75, dk=NW['uw_deep'])
    floaters(Nn, 0, 100, W, 1000, 50, seed=11, op=0.7)
    save_plate('hall_sea_near', Nn, variants=('night', 'lit'), gain=0.78, keep=0.24)

# ═════════════════════════ spring ═════════════════════════
if 'spring_far' in which:
    W, H = 2900, 1080
    S = Canvas(W, H, bg=0.0)
    fill_region(S, 0, 0, W, H, hexc('#7f9590'), hexc('#2a3b40'), seed=401, mott=0.2, gamma=0.8, scale=330)
    r1 = ridge_y(W, 800, 260, 411, rough=0.55, scale=340)
    mountain(S, r1, 880, NW['uw'] * 0.8, NW['uw_deep'] * 1.1, seed=41, tex=0.6, tex_op=0.25, haze=0.45, haze_col=NW['uw'], glaze=0.4, lit_dir=1, rim_op=0.3)
    mist(S, 0, W, 770, 90, seed=42, op=0.5, color=NW['uw'], scale=300)
    r2 = ridge_y(W, 835, 170, 412, rough=0.55, scale=260)
    mountain(S, r2, 900, NW['uw_dk'], NW['uw_deep'], seed=43, tex=0.8, tex_op=0.3, haze=0.2, haze_col=NW['uw'], glaze=0.45, lit_dir=1, rim_op=0.35)
    for i, x in enumerate([200, 640, 1080, 1960, 2400, 2760]):    # 灰暗海底的枯草（病恹恹的）
        seaweed(S, x, 836 + (i % 3) * 6, 150 + (i * 37) % 70, seed=420 + i, n=3, col=NW['weed_dry'], dk=NW['weed_dk'], sway=0.25, op=0.5, dry=0.5)
    floaters(S, 0, 60, W, 820, 160, seed=7, op=0.35)
    save_plate('spring_far', S, variants=('night', 'lit'), gain=0.72, keep=0.2)

if 'spring_near' in which:
    W, H = 2900, 1080
    Nn = Canvas(W, H)
    xs = np.arange(W, dtype=F)
    gy = GY + 5 * np.sin(xs / 260.0) + 3 * np.sin(xs / 83.0 + 1)
    ground_strip(Nn, gy, 1080, hexc('#9a9c90'), hexc('#4f5a56'), seed=431, tex=0.9, tex_col=NW['uw_deep'])
    r = np.random.default_rng(432)
    for _ in range(36):    # 沙纹
        x, y = r.uniform(0, W), r.uniform(850, 1070)
        ln = r.uniform(80, 240)
        brush(Nn, [(x, y), (x + ln * 0.5, y + r.normal(0, 3)), (x + ln, y + r.normal(0, 2))], w0=r.uniform(2, 4), color=NW['uw_deep'], op=0.28, seed=int(r.integers(1e6)), wob=1.5, taper=0.4, dry=0.3)
    pebbles(Nn, 0, W, (850, 1060), 80, seed=433, col=NW['mud'], dk=NW['mud_dk'], rmin=3, rmax=11, op=0.9)
    # 青石的位置（x≈1500）：地面上一圈湿暗的泥（石头自己是精灵）
    wash(Nn, ell(1500, GY + 14, 330, 46, 36), NW['mud_dk'], op=0.75, wob=3, seed=434, smooth=2, tex_k=0.25, rim=0.2)
    wash(Nn, ell(1500, GY + 18, 240, 30, 30), NW['basalt_dk'], op=0.5, wob=3, seed=435, smooth=2, rim=0.1)
    # 断木的断头（x≈1760~1800，斜插，长 ≈ 90）与旁边的小孔（x≈1830，黑色，直径 ≈ 40）
    stump = [(1752, GY + 18), (1768, GY - 60), (1812, GY - 70), (1826, GY + 16)]
    wash(Nn, stump, N['wood'], op=0.98, wob=1.2, seed=436, smooth=0, tex_k=0.3, rim=0.25)
    wash(Nn, [(1768, GY - 60), (1812, GY - 70), (1812, GY - 56), (1768, GY - 47)], N['earth_lt'], op=0.9, wob=0.8, seed=437, smooth=0, rim=0.2)    # 断口
    wash(Nn, ell(1790, GY - 62, 22, 7, 14), N['earth'], op=0.95, wob=0.6, seed=438, smooth=2, rim=0.2)
    outline(Nn, [(1752, GY + 18), (1768, GY - 60), (1812, GY - 70), (1826, GY + 16)], w=2.8, op=0.7, seed=439)
    for k in range(5):
        brush(Nn, [(1760 + k * 12, GY - 45 + k), (1764 + k * 12, GY + 6)], w0=1.4, color=INK, op=0.4, seed=440 + k, taper=0.3, dry=0.4)
    wash(Nn, ell(1858, GY + 22, 24, 9, 16), hexc('#171c1f'), op=0.97, wob=0.5, seed=445, smooth=2, rim=0.0)          # 小孔
    outline(Nn, ell(1858, GY + 22, 24, 9, 16) + [ell(1858, GY + 22, 24, 9, 16)[0]], w=2.0, op=0.6, seed=446)
    # 枯干的海草、病恹恹的小鱼（侧躺，很小）、碎石
    for i, (x, h) in enumerate([(120, 330), (260, 210), (700, 250), (1050, 170), (2150, 190), (2520, 260), (2780, 340)]):
        seaweed(Nn, x, 1000 - (i % 3) * 30, h, seed=450 + i, n=4, col=NW['weed_dry'], dk=NW['weed_dk'], sway=0.3, op=0.9, dry=0.55)
    for i, (x, y, ln) in enumerate([(930, 905, 52), (1220, 960, 44), (2040, 925, 50), (2330, 980, 40)]):
        small_fish(Nn, x, y, ln, seed=460 + i, col=NW['uw'] * 0.85, side=1 if i % 2 else -1)
        brush(Nn, [(x - ln * 0.2, y + 10), (x + ln * 0.3, y + 12)], w0=3, color=NW['uw_deep'], op=0.3, seed=470 + i, taper=0.4)
    for i in range(6):
        rock(Nn, r.uniform(80, 2800), r.uniform(900, 1040), r.uniform(50, 120), r.uniform(26, 52), seed=480 + i, col=NW['mud'], dark=NW['mud_dk'])
    save_plate('spring_near', Nn, variants=('night', 'lit'), gain=0.72, keep=0.22)

if 'spring_clear' in which:
    W, H = 2900, 1080
    C_ = Canvas(W, H)
    # 撬开石头后涌出的清水：x 1380~2000 的一汪，镜子一样（浅蓝灰绿），带涟漪和反光
    pool = ell(1690, GY + 20, 320, 52, 40)
    wash(C_, pool, hexc('#b8d2d6'), op=0.92, wob=2.5, seed=501, smooth=2, tex_k=0.06, rim=0.35, rim_w=4)
    wash(C_, ell(1690, GY + 14, 250, 30, 32), hexc('#e4eef0'), op=0.55, wob=2, seed=502, smooth=2, tex_k=0.05, rim=0.0)    # 镜面的亮
    ripple_rings(C_, 1500, GY + 6, 200, 28, n=5, seed=503, col=hexc('#f2f6f4'), op=0.8)
    ripple_rings(C_, 1500, GY + 6, 330, 46, n=2, seed=504, col=hexc('#dfeaea'), op=0.5)
    for i in range(7):    # 反光的亮线
        x = 1420 + i * 82
        brush(C_, [(x, GY + 4 + (i % 3) * 9), (x + 54, GY + 6 + (i % 3) * 9)], w0=2.4, color=hexc('#ffffff'), op=0.75, seed=510 + i, taper=0.5, dry=0.3)
    save_plate('spring_clear', C_, variants=('night', 'lit'), gain=0.95, keep=0.45)
