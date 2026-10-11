"""《小石猴点灯》补充精灵（接手后补的）：道具 + 动物 + 坐着的老婆婆 + 凤凰 + 鸟。
用法：python3 chars_extra.py [名字 ...]（不带参数 = 全部）；每个函数画一个精灵并登记进 public/sprites/sprites.json，
画完再 python3 -I scripts/make_night.py 生成夜色版。
锚点约定：站立的东西 = 脚底 / 底边中点；会飞、会被“拿着”的小东西（鳞片、木板、鸟、凤凰）= 中心。
PLATES.md §4 的尺寸基准；暖色只有红布包（#B8382E）是允许的红。"""
import sys
from chars_new import *     # noqa  (带出 cn_people 的全部名字 + leg / sleeve / hair_cap_side …)
from chars_new import REG as _REG

REG = {}


def sprite(fn):
    REG[fn.__name__] = fn
    return fn


GREY_HAIR_ = hexc('#d9d6d1')


def blob(cx, cy, rx, ry, n=16, jit=0.06, seed=0):
    return ellipse_pts(cx, cy, rx, ry, n, jit=jit, seed=seed)


# ═════════════════════════ 小道具 ═════════════════════════
@sprite
def bundle_red():
    """奶奶包银针的红布包：红布（#B8382E，允许的红）一角露出银针的尖。≈140×120，锚点 = 底边中点。"""
    L = new_canvas(260, 220)
    cx, foot = 130, 190
    body = [(cx - 62, foot), (cx - 70, foot - 38), (cx - 50, foot - 80), (cx - 14, foot - 98), (cx + 24, foot - 96), (cx + 58, foot - 76), (cx + 74, foot - 38), (cx + 64, foot)]
    garment(L, body, K['red'], 301, shade=0.38, stain=0.3, flick=0.3, ink_w=2.2, wob=0.8, smooth=2, rough=0.6, folds=[[(cx - 40, foot - 70), (cx - 12, foot - 40), (cx - 30, foot - 6)], [(cx + 44, foot - 66), (cx + 14, foot - 34), (cx + 36, foot - 4)], [(cx - 6, foot - 92), (cx, foot - 50), (cx + 8, foot - 8)]], fold_op=0.5)
    knot = blob(cx + 4, foot - 100, 18, 12, 12, seed=302)
    garment(L, knot, K['red'] * 0.9, 303, shade=0.4, stain=0.2, flick=0.2, ink_w=2.0, wob=0.6, rough=0.5)
    for s_, (dx, dy) in ((-1, (-34, -26)), (1, (36, -22))):          # 打结后露出的两个布角
        tail = [(cx + 4, foot - 100), (cx + 4 + dx * 0.6, foot - 100 + dy * 0.2), (cx + 4 + dx, foot - 100 + dy), (cx + 4 + dx * 0.7, foot - 100 + dy + 14)]
        garment(L, tail, K['red'], 304 + s_, shade=0.3, stain=0.2, flick=0.2, ink_w=1.8, wob=0.5, rough=0.4)
    line(L, [(cx + 52, foot - 70), (cx + 82, foot - 108), (cx + 96, foot - 124)], 3.2, hexc('#d9dcdd'), 0.97, 308, 0.2, 0.0, 0.3, w1=1.0)    # 银针的尖
    line(L, [(cx + 52, foot - 70), (cx + 82, foot - 108), (cx + 96, foot - 124)], 1.1, INK, 0.6, 309, 0.2, 0.0, 0.2)
    sheet_save(L, 'bundle_red', (cx, foot), 301)


@sprite
def bowl():
    """一只粗陶碗，冷灰，冒着冷白的热气。≈70×40（连热气 ≈ 70×80）。锚点 = 碗底中点。"""
    L = new_canvas(160, 170)
    bx, by = 80, 150
    pts = [(bx - 36, by - 40), (bx + 36, by - 40), (bx + 28, by - 10), (bx + 16, by), (bx - 16, by), (bx - 28, by - 10)]
    garment(L, pts, hexc('#a7a9aa'), 311, shade=0.38, stain=0.25, flick=0.3, ink_w=2.0, wob=0.6, smooth=2, rough=0.4)
    wash(L, [(bx - 36, by - 41), (bx + 36, by - 41), (bx + 33, by - 34), (bx - 33, by - 34)], hexc('#e4e6e4'), op=0.95, wob=0.5, seed=312, smooth=1)
    for k, (dx, ph) in enumerate([(-14, 0), (0, 1.5), (14, 3.0)]):
        pts_ = [(bx + dx + math.sin(t * 0.9 + ph) * 6, by - 46 - t * 8) for t in range(10)]
        line(L, pts_, 4.0, hexc('#f1efe8'), 0.8, 320 + k, 0.4, 0.2, 0.8, w1=1.2)
    sheet_save(L, 'bowl', (bx, by), 311)


@sprite
def scale():
    """大鱼的一片鱼鳞：银蓝灰色的水滴形，边缘有一圈淡光。≈120×100，锚点 = 中心。"""
    L = new_canvas(220, 190)
    cx, cy = 110, 95
    drop = [(cx - 54, cy), (cx - 40, cy - 38), (cx - 6, cy - 54), (cx + 34, cy - 40), (cx + 58, cy - 6), (cx + 46, cy + 30), (cx + 8, cy + 52), (cx - 32, cy + 34)]
    garment(L, drop, hexc('#a3b6c4'), 321, shade=0.35, stain=0.25, flick=0.2, ink_w=2.4, wob=0.7, smooth=2, rough=0.5, tex_k=0.1)
    for k, rr in enumerate((38, 26, 14)):          # 鳞片的生长环
        pts = [(cx + 2 + rr * math.cos(a) * 1.15, cy + 2 + rr * math.sin(a)) for a in np.linspace(math.pi * 0.15, math.pi * 1.9, 14)]
        line(L, pts, 1.8, hexc('#6f8392'), 0.65, 330 + k, 0.4, 0.1, 0.4)
    for k in range(7):                              # 放射的细纹
        a = math.pi * (0.3 + k * 0.22)
        line(L, [(cx + 8, cy + 6), (cx + 8 + 44 * math.cos(a), cy + 6 + 44 * math.sin(a))], 1.2, hexc('#7f93a1'), 0.45, 340 + k, 0.5, 0.2, 0.3)
    glow(L, cx, cy, 80, hexc('#e9f0f5'), op=0.25, power=2.0)
    sheet_save(L, 'scale', (cx, cy), 321)


@sprite
def plank():
    """一块木板：≈300×26，土黄灰，锚点 = 中心。"""
    L = new_canvas(380, 90)
    cx, cy = 190, 45
    pts = [(cx - 150, cy - 12), (cx + 150, cy - 13), (cx + 154, cy + 12), (cx - 148, cy + 13)]
    garment(L, pts, hexc('#a99872'), 351, shade=0.4, stain=0.3, flick=0.9, fdir=2, ink_w=2.2, wob=0.6, smooth=0, rough=0.9, tex_k=0.16)
    for k in range(5):
        y = cy - 8 + k * 4.2
        line(L, [(cx - 140 + k * 9, y), (cx - 40, y + 0.8), (cx + 120 - k * 6, y - 0.6)], 1.1, hexc('#6c5d44'), 0.4, 352 + k, 0.4, 0.3, 0.6)
    for x_ in (-118, 110):
        dots(L, [(cx + x_, cy, 2.6)], hexc('#4f4538'), op=0.9)
    sheet_save(L, 'plank', (cx, cy), 351)


def _firewood_draw(tied):
    L = new_canvas(420, 340)
    cx, foot = 210, 310
    r = np.random.default_rng(361)
    spread = 0.52 if tied else 1.0
    sticks = []
    for i in range(22):
        ang = math.radians(r.uniform(-34, 34) * (0.45 if tied else 1.0) + 90)       # 大致竖着，上端散开
        ln = r.uniform(190, 250) * (1.0 if tied else r.uniform(0.82, 1.0))
        bx = cx + r.normal(0, 22 * spread)
        by = foot - r.uniform(0, 12)
        ex, ey = bx + math.cos(ang) * ln * 0.6 * (spread * 0.6 + 0.4), by - math.sin(ang) * ln
        sticks.append((bx, by, ex, ey, r.uniform(8, 15)))
    sticks.sort(key=lambda s: -s[4] * 0.0 + s[3])            # 后排（梢更高）先画
    for k, (bx, by, ex, ey, w) in enumerate(sticks):
        col = mix(K['wood'], K['wood_dk'], r.uniform(0, 0.6))
        brush(L, [(bx, by), ((bx + ex) / 2 + r.normal(0, 4), (by + ey) / 2), (ex, ey)], w0=w, w1=w * 0.55, color=col, op=0.97, seed=362 + k, wob=1.0, taper=0.12, dry=0.12)
        brush(L, [(bx + w * 0.2, by - 4), ((bx + ex) / 2 + w * 0.2, (by + ey) / 2), (ex + 1, ey + 4)], w0=w * 0.3, w1=0.8, color=K['wood_lt'], op=0.4, seed=400 + k, wob=0.6, taper=0.3)
        brush(L, [(bx - w * 0.5, by), ((bx + ex) / 2 - w * 0.5, (by + ey) / 2), (ex - w * 0.3, ey)], w0=1.6, color=INK, op=0.55, seed=430 + k, wob=0.8, taper=0.2, dry=0.4)
        if r.random() < 0.5:         # 小枝杈
            t = r.uniform(0.35, 0.8)
            px, py = bx + (ex - bx) * t, by + (ey - by) * t
            brush(L, [(px, py), (px + r.uniform(-34, 34), py - r.uniform(14, 36))], w0=4, w1=1.4, color=col, op=0.9, seed=460 + k, wob=0.6, taper=0.3)
    if tied:
        for k, yb in enumerate((foot - 96, foot - 150)):
            pts = [(cx - 40 + 4 * k, yb + 6), (cx - 6, yb + 14 - k * 2), (cx + 36 - 4 * k, yb + 6)]
            for t in (0, 5):
                brush(L, [(p[0], p[1] + t) for p in pts], w0=9, color=K['rope'], op=0.97, seed=470 + k * 3 + t, wob=0.6, taper=0.08)
                brush(L, [(p[0], p[1] + t + 3) for p in pts], w0=2.0, color=K['rope_dk'], op=0.7, seed=480 + k * 3 + t, wob=0.6, taper=0.1, dry=0.3)
        dots(L, [(cx + 8, foot - 140, 9)], K['rope'], op=0.98)                            # 绳结
        brush(L, [(cx + 8, foot - 140), (cx + 22, foot - 122), (cx + 20, foot - 100)], w0=7, w1=3, color=K['rope'], op=0.97, seed=490, taper=0.2)
    else:
        brush(L, [(cx + 30, foot - 30), (cx + 52, foot - 6), (cx + 76, foot + 2)], w0=8, w1=4, color=K['rope'], op=0.95, seed=495, taper=0.25, wob=1.2)     # 断了的绳头垂在地上
        brush(L, [(cx - 36, foot - 24), (cx - 62, foot - 2), (cx - 88, foot + 4)], w0=8, w1=4, color=K['rope'], op=0.95, seed=496, taper=0.25, wob=1.2)
    ground_shadow(L, cx, foot + 6, 120, 10, 0.28, 361)
    return L, (cx, foot)


@sprite
def firewood():
    L, anc = _firewood_draw(False)
    sheet_save(L, 'firewood', anc, 361)


@sprite
def firewood_tied():
    L, anc = _firewood_draw(True)
    sheet_save(L, 'firewood_tied', anc, 362)


@sprite
def boulder():
    """压着泉眼的青石：比石娃还高，高≈400 宽≈520，青灰色，水草苔痕，底边平。锚点 = 底边中点。"""
    L = new_canvas(640, 480)
    cx, by = 320, 450
    rock(L, cx, by, 520, 400, seed=371, col=hexc('#7f949b'), dark=hexc('#4d6068'), light=hexc('#aebfc4'), moss=0.7)
    r = np.random.default_rng(372)
    for i in range(26):          # 皴擦
        x = cx + r.uniform(-230, 230)
        y = by - r.uniform(30, 360)
        line(L, [(x, y), (x + r.uniform(-30, 30), y + r.uniform(30, 90))], r.uniform(1.4, 3.0), INK, r.uniform(0.15, 0.4), 380 + i, 0.4, 0.5, 0.8)
    for i in range(7):           # 水草的丝
        x = cx - 200 + i * 62
        line(L, [(x, by - 6), (x + r.normal(0, 14), by - 60), (x + r.normal(0, 22), by - 110)], 3.0, hexc('#5f7a62'), 0.7, 410 + i, 0.5, 0.2, 1.0)
    wash(L, [(cx - 250, by), (cx + 250, by), (cx + 236, by - 16), (cx - 236, by - 16)], hexc('#37454a'), op=0.5, wob=2, seed=420, smooth=1, rim=0.0)
    sheet_save(L, 'boulder', (cx, by), 371)


@sprite
def lever():
    """长木棍：竖直，高 700 宽 36，一头略粗。锚点 = 底端中点。"""
    L = new_canvas(120, 760)
    cx, foot = 60, 735
    pts = [(cx - 19, foot), (cx - 16, foot - 300), (cx - 14, foot - 690), (cx + 12, foot - 692), (cx + 15, foot - 300), (cx + 19, foot)]
    garment(L, pts, K['wood'], 441, shade=0.4, stain=0.4, flick=1.2, fdir=88, ink_w=2.4, wob=0.8, smooth=1, rough=1.0, tex_k=0.2)
    for k in range(10):
        y = foot - 40 - k * 66
        line(L, [(cx - 15, y), (cx + 1, y + 5), (cx + 16, y - 1)], 1.6, INK, 0.35, 442 + k, 0.5, 0.3, 0.5)
    wash(L, [(cx - 8, foot - 692), (cx + 8, foot - 692), (cx + 3, foot - 684)], K['wood_lt'], op=0.9, wob=0.5, seed=460, smooth=0, rim=0.0)
    sheet_save(L, 'lever', (cx, foot), 441)


@sprite
def flat_stone():
    """扁石：宽 160 高 50。锚点 = 底边中点。"""
    L = new_canvas(230, 100)
    rock(L, 115, 82, 160, 50, seed=451, col=hexc('#8b9496'), dark=hexc('#555e61'), light=hexc('#b9c0bf'), moss=0.15)
    sheet_save(L, 'flat_stone', (115, 82), 451)


@sprite
def wick_fixed():
    """接好的完整灯芯：一根棉芯，长 ≈210，中间一圈银针缠的接口。锚点 = 底端中点。"""
    L = new_canvas(90, 270)
    cx, foot = 45, 250
    pts = [(cx, foot), (cx + 5, foot - 70), (cx - 4, foot - 140), (cx + 2, foot - 208)]
    brush(L, pts, w0=15, w1=10, color=hexc('#e6e0cf'), op=0.99, seed=501, wob=0.8, taper=0.08, dry=0.1)
    for k in range(13):          # 拧着的棉线纹
        y = foot - 6 - k * 15.5
        brush(L, [(cx - 7 + math.sin(y * 0.05) * 4, y + 4), (cx + 7 + math.sin(y * 0.05) * 4, y - 4)], w0=1.5, color=hexc('#a89f88'), op=0.6, seed=510 + k, taper=0.4, wob=0.3)
    brush(L, pts, w0=2.0, color=INK, op=0.35, seed=502, wob=0.8, taper=0.2, dry=0.5)
    for k in range(6):           # 银针缠出来的接口
        y = foot - 96 - k * 4.4
        brush(L, [(cx - 11 + 2, y + 2), (cx + 11, y - 2)], w0=2.8, color=hexc('#cfd4d8'), op=0.98, seed=530 + k, taper=0.2, wob=0.3)
    line(L, [(cx + 2, foot - 94), (cx + 14, foot - 128)], 2.0, hexc('#eef1f2'), 0.95, 540, 0.3, 0.0, 0.2, w1=0.8)
    brush(L, [(cx - 3, foot - 206), (cx + 2, foot - 214), (cx + 6, foot - 208)], w0=3, color=hexc('#8f877a'), op=0.8, seed=545, wob=0.5, taper=0.3)      # 灯芯头
    sheet_save(L, 'wick_fixed', (cx, foot), 501)


# ═════════════════════════ 动物 ═════════════════════════
@sprite
def horse_side():
    """朴素的草原马（侧面，朝右，≈430 高 × 560 宽），灰褐，鬃毛，带一副简单的鞍子。锚点 = 蹄底中点。"""
    L = new_canvas(720, 580)
    cx, gy = 330, 540
    hc, hd, hl = K['horse'], K['horse_dk'], K['horse_lt']
    ground_shadow(L, cx + 10, gy + 4, 230, 14, 0.3, 601)
    # 远侧的两条腿（深一点）
    leg(L, [(262, 350), (280, 430), (268, 488), (272, gy - 8)], 52, 24, hd * 0.9, 602, shade=0.3, stain=0.3, ink_w=2.0, rough=0.8)
    leg(L, [(420, 350), (430, 440), (428, gy - 8)], 42, 22, hd * 0.9, 603, shade=0.3, stain=0.3, ink_w=2.0, rough=0.8)
    # 尾
    for k in range(7):
        brush(L, [(200 + k, 318 + k * 2), (150 + k * 4, 380 + k * 6), (120 + k * 7, 470 + k * 8)], w0=14 - k, w1=2, color=mix(hd, INK, 0.2 + 0.05 * k), op=0.95, seed=610 + k, wob=2.0, taper=0.25, dry=0.3)
    # 躯干
    body = [(196, 300), (220, 262), (290, 250), (370, 256), (440, 268), (490, 296), (500, 346), (466, 392), (390, 404), (300, 404), (228, 396), (192, 352)]
    garment(L, body, hc, 620, shade=0.4, stain=0.4, flick=0.9, fdir=10, ink_w=2.6, wob=1.0, smooth=2, rough=0.9, tex_k=0.14)
    # 脖子 + 头
    neck_ = [(440, 276), (466, 196), (508, 128), (548, 98), (586, 134), (560, 224), (520, 310)]
    garment(L, neck_, hc, 621, shade=0.35, stain=0.3, flick=0.8, fdir=60, ink_w=2.4, wob=1.0, smooth=2, rough=0.8)
    head = [(524, 94), (564, 84), (598, 120), (626, 166), (634, 194), (612, 214), (584, 198), (548, 164), (520, 128)]
    garment(L, head, hc, 622, shade=0.4, stain=0.3, flick=0.5, fdir=40, ink_w=2.4, wob=0.7, smooth=2, rough=0.6)
    garment(L, [(538, 90), (546, 56), (562, 88)], hd, 623, shade=0.2, stain=0.1, flick=0.1, ink_w=1.8, wob=0.4, smooth=0)
    eye_dot(L, 566, 126, 4.4, 3.8, seed=624)
    dots(L, [(622, 196, 2.6)], INK, op=0.8)
    # 鬃毛
    for k in range(10):
        t = k / 9
        bx, by = 534 - t * 70 + 4, 96 + t * 190
        brush(L, [(bx, by), (bx - 26 - 4 * k % 3, by + 14 + 3), (bx - 38, by + 34)], w0=8, w1=2, color=hd * 0.85, op=0.95, seed=630 + k, wob=1.2, taper=0.3, dry=0.25)
    # 鞍：灰蓝的鞍褥 + 土色的鞍子 + 肚带
    garment(L, [(318, 252), (418, 256), (426, 330), (322, 328)], hexc('#6d7f96'), 640, shade=0.35, stain=0.3, flick=0.3, ink_w=2.0, wob=0.7, smooth=1, rough=0.6)
    garment(L, [(334, 240), (396, 242), (404, 290), (340, 290)], K['gb'], 641, shade=0.35, stain=0.3, flick=0.3, ink_w=2.0, wob=0.6, smooth=1, rough=0.6)
    line(L, [(364, 330), (368, 380), (362, 404)], 6, K['gb_dk'], 0.9, 642, 0.2, 0.1, 0.5)
    # 近侧的两条腿
    leg(L, [(226, 330), (262, 420), (246, 478), (250, gy - 2)], 66, 30, hc, 650, shade=0.4, stain=0.4, ink_w=2.4, rough=1.0)
    leg(L, [(446, 346), (452, 430), (450, gy - 2)], 48, 26, hc, 651, shade=0.4, stain=0.4, ink_w=2.4, rough=1.0)
    for x_, sd in ((244, 660), (448, 661)):          # 蹄
        garment(L, [(x_ - 16, gy - 20), (x_ + 14, gy - 20), (x_ + 18, gy + 2), (x_ - 18, gy + 2)], K['dark2'], sd, shade=0.2, stain=0.2, flick=0.1, ink_w=1.8, wob=0.4, smooth=1)
    sheet_save(L, 'horse_side', (369, gy), 601)      # 锚点 = 鞍子正下方的地面（骑手的髋对着它）


@sprite
def sheep():
    """一只羊（侧面，朝右，≈90 高）。锚点 = 蹄底中点。"""
    L = new_canvas(220, 170)
    cx, gy = 100, 150
    ground_shadow(L, cx, gy + 2, 62, 6, 0.28, 701)
    for x_, sd in ((-26, 702), (-10, 703), (14, 704), (30, 705)):
        leg(L, [(cx + x_, gy - 38), (cx + x_ + 1, gy - 18), (cx + x_, gy - 3)], 10, 8, K['dark2'] * 1.2, sd, shade=0.2, stain=0.2, ink_w=1.6, rough=0.4)
    r = np.random.default_rng(706)
    puff = []
    for a in np.linspace(0, 2 * math.pi, 22, endpoint=False):
        rr = 1 + r.uniform(-0.1, 0.12)
        puff.append((cx - 2 + 54 * math.cos(a) * rr, gy - 62 + 34 * math.sin(a) * rr))
    garment(L, puff, hexc('#d7d3c8'), 707, shade=0.4, stain=0.3, flick=0.8, fdir=40, ink_w=2.2, wob=1.6, smooth=1, rough=1.4, tex_k=0.18)
    for k in range(8):       # 毛团的卷纹
        a = r.uniform(0, 6.28)
        px, py = cx - 2 + 34 * math.cos(a) * r.uniform(0.2, 1), gy - 62 + 20 * math.sin(a) * r.uniform(0.2, 1)
        line(L, [(px - 6, py), (px, py - 5), (px + 6, py)], 1.4, hexc('#8f8b80'), 0.5, 710 + k, 0.4, 0.3, 0.3)
    head = [(cx + 46, gy - 80), (cx + 62, gy - 84), (cx + 78, gy - 70), (cx + 82, gy - 52), (cx + 66, gy - 46), (cx + 50, gy - 56)]
    garment(L, head, K['dark2'] * 1.4, 720, shade=0.3, stain=0.3, flick=0.2, ink_w=1.8, wob=0.5, smooth=2, rough=0.4)
    garment(L, [(cx + 46, gy - 80), (cx + 36, gy - 72), (cx + 44, gy - 62)], K['dark2'] * 1.4, 721, shade=0.2, stain=0.1, flick=0.1, ink_w=1.4, wob=0.3, smooth=1)
    dots(L, [(cx + 66, gy - 70, 1.8)], hexc('#efe8d8'), op=0.9)
    sheet_save(L, 'sheep', (cx, gy), 701)


# ═════════════════════════ 凤凰、鸟 ═════════════════════════
def _feather(L, bx, by, ang, ln, w, col, seed, dry=0.3, curve=0.0):
    """一根羽毛：从 (bx,by) 沿 ang 方向长出，末端微弯。"""
    ex, ey = bx + math.cos(ang) * ln, by + math.sin(ang) * ln
    mx, my = (bx + ex) / 2 - math.sin(ang) * ln * curve, (by + ey) / 2 + math.cos(ang) * ln * curve
    brush(L, [(bx, by), (mx, my), (ex, ey)], w0=w, w1=w * 0.2, color=col, op=0.97, seed=seed, wob=0.7, taper=0.3, dry=dry)
    brush(L, [(bx, by), (mx, my), (ex, ey)], w0=1.2, color=INK, op=0.35, seed=seed + 1, wob=0.5, taper=0.4, dry=0.5)


def _phoenix(up, seed0):
    L = new_canvas(620, 460)
    cx, cy = 300, 230
    gold, gold_lt, blue, blue_dk, white = hexc('#c9bd96'), hexc('#e2d9b8'), hexc('#8d9db0'), hexc('#5f7088'), hexc('#ece8dc')
    r = np.random.default_rng(seed0)
    # 尾羽：三根长长的拖在身后（朝左）
    for k, (da, ln, col) in enumerate(((0.22, 280, gold), (0.0, 310, blue), (-0.2, 260, white))):
        pts = [(cx - 50, cy + 14 + k * 4), (cx - 150, cy + 34 + da * 120), (cx - 250, cy + 70 + da * 260 + 30), (cx - 280, cy + 130 + da * 300)]
        brush(L, pts, w0=20, w1=3, color=col, op=0.97, seed=seed0 + 10 + k, wob=1.2, taper=0.25, dry=0.25)
        brush(L, pts, w0=1.6, color=INK, op=0.35, seed=seed0 + 20 + k, wob=0.8, taper=0.4, dry=0.5)
        for j in range(5):       # 羽枝
            t = 0.25 + j * 0.16
            px, py = (cx - 50) + (pts[-1][0] - (cx - 50)) * t * 0.95, (cy + 14) + (pts[-1][1] - (cy + 14)) * t ** 1.3
            brush(L, [(px, py), (px - 14, py + 8 + j * 2)], w0=5, w1=1, color=col, op=0.8, seed=seed0 + 30 + k * 7 + j, wob=0.4, taper=0.3)
    # 远侧的翅（深一点）、身体、近侧的翅
    def wing(base, col_main, col_alt, op, sd):
        sx, sy = base
        n = 11
        for i in range(n):
            t = i / (n - 1)
            if up:
                ang = math.radians(-100 + t * 70)        # 向上
                ln = 120 + 150 * math.sin(math.pi * (0.2 + 0.7 * t))
            else:
                ang = math.radians(100 - t * 60)         # 向下
                ln = 120 + 140 * math.sin(math.pi * (0.2 + 0.7 * t))
            _feather(L, sx, sy, ang, ln, 24 - t * 8, mix(col_main, col_alt, (i % 3) / 3.0), sd + i, curve=0.06 * (1 if up else -1))
    wing((cx + 10, cy - 8), blue_dk, blue, 0.9, seed0 + 100)
    body = blob(cx, cy, 78, 34, 18, jit=0.03, seed=seed0 + 2)
    garment(L, body, white, seed0 + 3, shade=0.4, stain=0.2, flick=0.5, fdir=170, ink_w=2.2, wob=0.7, smooth=2, rough=0.6, tex_k=0.1)
    # 颈与头（朝右）
    neck_ = [(cx + 50, cy - 8), (cx + 86, cy - 44), (cx + 108, cy - 66), (cx + 124, cy - 56), (cx + 100, cy - 22), (cx + 70, cy + 18)]
    garment(L, neck_, white, seed0 + 4, shade=0.35, stain=0.2, flick=0.3, ink_w=2.0, wob=0.6, smooth=2, rough=0.5)
    head = blob(cx + 120, cy - 72, 20, 16, 14, seed=seed0 + 5)
    garment(L, head, white, seed0 + 6, shade=0.3, stain=0.15, flick=0.1, ink_w=1.8, wob=0.4, smooth=2)
    garment(L, [(cx + 136, cy - 80), (cx + 164, cy - 70), (cx + 138, cy - 62)], gold, seed0 + 7, shade=0.2, stain=0.1, flick=0.1, ink_w=1.6, wob=0.3, smooth=0)      # 喙
    dots(L, [(cx + 125, cy - 76, 2.4)], INK, op=0.95)
    for k in range(3):       # 头冠
        brush(L, [(cx + 108, cy - 86), (cx + 98 - k * 8, cy - 112 - k * 6), (cx + 90 - k * 10, cy - 124 - k * 6)], w0=5, w1=1, color=[gold, blue, gold_lt][k], op=0.95, seed=seed0 + 40 + k, wob=0.5, taper=0.3)
    wing((cx + 4, cy - 2), blue, gold, 1.0, seed0 + 200)
    # 腿爪（收在身下）
    for dx in (-8, 14):
        line(L, [(cx + dx, cy + 30), (cx + dx + 14, cy + 52), (cx + dx + 28, cy + 56)], 3.0, hexc('#8b8366'), 0.9, seed0 + 60 + dx, 0.3, 0.1, 0.4)
    return L, (cx, cy)


@sprite
def phoenix_a():
    L, anc = _phoenix(True, 800)
    sheet_save(L, 'phoenix_a', anc, 801)


@sprite
def phoenix_b():
    L, anc = _phoenix(False, 900)
    sheet_save(L, 'phoenix_b', anc, 901)


def _bird(name, up, swallow, seed0):
    L = new_canvas(180, 130)
    cx, cy = 90, 66
    ink_c = hexc('#3b4350')
    body = [(cx - 26, cy + 2), (cx - 12, cy - 8), (cx + 14, cy - 8), (cx + 30, cy - 2), (cx + 18, cy + 8), (cx - 6, cy + 10)]
    garment(L, body, ink_c if swallow else hexc('#5b6676'), seed0, shade=0.3, stain=0.1, flick=0.2, ink_w=1.6, wob=0.4, smooth=2, rough=0.3)
    garment(L, [(cx + 22, cy - 12), (cx + 38, cy - 10), (cx + 42, cy - 2), (cx + 28, cy)], ink_c, seed0 + 1, shade=0.2, stain=0.1, flick=0.1, ink_w=1.4, wob=0.3, smooth=2)
    garment(L, [(cx + 40, cy - 8), (cx + 52, cy - 5), (cx + 40, cy - 2)], hexc('#8b8366'), seed0 + 2, shade=0.1, stain=0.0, flick=0.0, ink_w=1.0, wob=0.2, smooth=0)
    if swallow:        # 分叉的尾
        for s_ in (-1, 1):
            brush(L, [(cx - 22, cy + 4), (cx - 46, cy + 8 + s_ * 8), (cx - 62, cy + 6 + s_ * 18)], w0=7, w1=1.4, color=ink_c, op=0.97, seed=seed0 + 3 + s_, taper=0.2, wob=0.3)
    else:
        brush(L, [(cx - 24, cy + 2), (cx - 46, cy + 8), (cx - 58, cy + 12)], w0=9, w1=3, color=hexc('#5b6676'), op=0.97, seed=seed0 + 3, taper=0.2, wob=0.3)
    sgn = -1 if up else 1
    for k, (dx, ln, ang) in enumerate(((0, 56, 0.0), (10, 50, 0.22), (-8, 48, -0.18))):
        a = math.radians((-90 if up else 90) + (-18 + k * 18) * (1 if up else -1)) + ang * 0
        ex, ey = cx + dx + math.cos(a) * ln * 0.5 + 8, cy - 4 + math.sin(a) * ln
        brush(L, [(cx + dx - 2, cy - 4), ((cx + dx + ex) / 2 - 4, (cy - 4 + ey) / 2), (ex, ey)], w0=12 - k * 2, w1=2, color=ink_c, op=0.95, seed=seed0 + 10 + k, wob=0.5, taper=0.3, dry=0.15)
    sheet_save(L, name, (cx, cy), seed0)


@sprite
def bird_up():
    _bird('bird_up', True, False, 1000)


@sprite
def bird_down():
    _bird('bird_down', False, False, 1010)


@sprite
def swallow_up():
    _bird('swallow_up', True, True, 1020)


@sprite
def swallow_down():
    _bird('swallow_down', False, True, 1030)


# ═════════════════════════ 坐着的老婆婆 ═════════════════════════
@sprite
def oldwoman_sit_side():
    """崖下的老婆婆：朝右坐在路边，手扶着膝上，≈300 高。头发灰白、背微驼、深灰蓝粗布衣，没有红头绳。锚点 = 坐地处中点。"""
    L = new_canvas(520, 420)
    cx, foot = 220, 390
    seed = 1100
    cy, a, b = foot - 262, 30, 36
    hx = cx + 40
    ground_shadow(L, cx + 20, foot + 2, 150, 12, 0.28, seed)
    robe_c = hexc('#4c566d')
    dark_c = hexc('#5a5249')
    # 腿：大腿向前平放，小腿落地（朝右）
    leg(L, [(cx - 10, foot - 52), (cx + 56, foot - 76), (cx + 108, foot - 70)], 52, 40, robe_c * 0.92, seed + 1, shade=0.4, stain=0.5, flick=0.6, ink_w=2.2, rough=1.0)
    leg(L, [(cx + 106, foot - 78), (cx + 118, foot - 40), (cx + 120, foot - 14)], 38, 28, dark_c, seed + 2, shade=0.4, stain=0.5, flick=0.5, ink_w=2.0, rough=1.0)
    shoe_side(L, cx + 126, foot, 54, 24, K['dark'], seed + 3, toe=1)
    # 身体：微驼的背，上身略向前倾
    torso = [(cx - 40, foot - 36), (cx - 52, foot - 96), (cx - 40, foot - 160), (cx - 6, foot - 200), (cx + 30, foot - 200), (cx + 44, foot - 168), (cx + 40, foot - 118), (cx + 46, foot - 56), (cx + 30, foot - 30)]
    rp, rm = garment(L, torso, robe_c, seed + 10, shade=0.42, stain=0.5, worn=0.15, flick=0.8, fdir=80, streak=0.6, ink_w=2.4, smooth=1, edge_dk=0.22, rough=1.3,
                     folds=[[(cx - 16, foot - 120), (cx - 20, foot - 80), (cx - 14, foot - 44)], [(cx + 16, foot - 110), (cx + 24, foot - 70), (cx + 24, foot - 38)]])
    garment(L, [(cx - 42, foot - 92), (cx + 46, foot - 90), (cx + 48, foot - 76), (cx - 44, foot - 78)], K['gb_lt'], seed + 11, shade=0.3, stain=0.4, flick=0.3, fdir=5, ink_w=1.8, smooth=1, rough=0.6)    # 腰带
    patch(L, cx - 22, foot - 56, 20, 18, K['gb'], seed + 12, ang=0.1, clipmask=rm)
    # 脖子 + 脸 + 白发
    neck(L, hx - 10, cy + b - 8, foot - 196, 26, seed + 20, skin=K['skin_old'])
    face_side(L, hx, cy, a, b, seed + 30, skin=K['skin_old'], mood='calm', blush=0.2, nose=1.3, eye_y=0.02, chin=0.85, age=0.9, browr=1.0)
    hair_cap_side(L, hx, cy, a, b, seed + 40, col=GREY_HAIR_, fringe=0.3, nape=0.35, puff=1.0, back=0.9)
    garment(L, blob(hx - a * 0.95, cy - b * 0.35, 15, 13, 12, seed=seed + 41), GREY_HAIR_, seed + 42, shade=0.35, stain=0.1, flick=0.3, ink_w=1.6, wob=0.4, smooth=2)      # 脑后的发髻
    garment(L, [(hx - a * 0.9, cy - b * 0.75), (hx + a * 0.15, cy - b * 1.0), (hx + a * 0.55, cy - b * 0.55), (hx + a * 0.1, cy - b * 0.45), (hx - a * 0.7, cy - b * 0.1)], hexc('#66738f'), seed + 43, shade=0.35, stain=0.3, flick=0.3, ink_w=1.8, wob=0.5, smooth=1, rough=0.5)   # 头巾
    # 手臂：近侧的手扶着膝头
    sh, el, wr = (cx + 20, foot - 180), (cx + 52, foot - 122), (cx + 94, foot - 100)
    ap = tube([sh, el, wr], 30, 26, cap0=0.9, cap1=0.1)
    shadow_on(L, rm, ap, -4, 3, op=0.4)
    sleeve(L, [sh, el, wr], 30, 26, robe_c, seed + 50, cuff=8, cuff_col=K['gb_lt'], shade=0.42, stain=0.5, worn=0.1, flick=0.7, streak=0.4, edge_dk=0.2, rough=1.0)
    hand(L, wr[0], wr[1] + 2, math.pi / 2 - 0.5, 22, skin=K['skin_old'], seed=seed + 60, kind='open', side=1)
    sheet_save(L, 'oldwoman_sit_side', (cx + 20, foot), seed)


if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        REG[n]()
