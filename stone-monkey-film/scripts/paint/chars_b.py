"""新人物与小道具（续）。"""
from chars_new import *

# ───────────────────────── 长枪 ─────────────────────────
def spear_draw(L, x, y_bot, y_tip, shaft_w=8.0, head_len=64, seed=0, tassel=True, ink=1.0):
    """竖直的长枪：木杆 + 枪头（柳叶形）+ 枪头下的灰缨。枪尖朝上。"""
    shaft = tube([(x, y_bot), (x + 1.5, (y_bot + y_tip) / 2), (x, y_tip + head_len * 0.8)], shaft_w, shaft_w * 0.85, cap=0.0)
    garment(L, shaft, K['wood'], seed, shade=0.45, shade_dir=1, stain=0.4, flick=1.2, fdir=90, ink_w=1.8 * ink, smooth=1, rough=0.5, wob=0.5, tex_k=0.1, edge_dk=0.2,
            folds=[[(x - shaft_w * 0.2, y_bot - 20), (x - shaft_w * 0.2, y_tip + head_len + 60)]], fold_op=0.3)
    # 枪头
    hx0 = x
    ty = y_tip
    blade = [(hx0, ty), (hx0 + shaft_w * 0.9, ty + head_len * 0.35), (hx0 + shaft_w * 0.7, ty + head_len * 0.78), (hx0 + shaft_w * 0.4, ty + head_len), (hx0 - shaft_w * 0.4, ty + head_len),
             (hx0 - shaft_w * 0.7, ty + head_len * 0.78), (hx0 - shaft_w * 0.9, ty + head_len * 0.35)]
    bp, bm = garment(L, blade, hexc('#a9b0b8'), seed + 3, shade=0.4, shade_dir=1, stain=0.25, flick=0.0, ink_w=1.7 * ink, smooth=1, rough=0.2, wob=0.3, speck=0.0, dark=hexc('#59626d'), light=hexc('#e4e8ea'), worn=0.3)
    line(L, [(hx0, ty + 3), (hx0 + 0.5, ty + head_len * 0.5), (hx0, ty + head_len * 0.95)], 1.2, hexc('#59626d'), 0.6, seed + 4, 0.3, 0, 0.2)
    # 銎（枪头和杆连接的套）
    garment(L, [(hx0 - shaft_w * 0.7, ty + head_len), (hx0 + shaft_w * 0.7, ty + head_len), (hx0 + shaft_w * 0.6, ty + head_len + 14), (hx0 - shaft_w * 0.6, ty + head_len + 14)], hexc('#7c838c'), seed + 5, smooth=0, wob=0.3, ink_w=1.5 * ink, shade=0.4, stain=0.2, flick=0, rough=0.3, speck=0)
    if tassel:   # 灰缨：垂在枪头下面
        r = np.random.default_rng(seed + 9)
        for k in range(16):
            sx = hx0 + r.normal(0, 2)
            sy = ty + head_len + 8
            dx = r.normal(0, 8) + (k - 8) * 1.4
            ln_ = r.uniform(28, 46)
            brush(L, [(sx, sy), (sx + dx * 0.5, sy + ln_ * 0.5), (sx + dx, sy + ln_)], w0=3.0, w1=1.0, color=mix(hexc('#a7a9ad'), hexc('#d8d6d0'), r.uniform(0, 0.6)) * r.uniform(0.7, 1.0), op=0.9, seed=int(r.integers(1e6)), taper=0.3, wob=0.6)
        wash(L, ellipse_pts(hx0, ty + head_len + 10, 6, 5, 8), hexc('#8d9096'), op=1.0, wob=0.3, seed=seed + 8, smooth=1)


STEEL = hexc('#727d8b')
STEEL_DK = hexc('#3e4753')
LEATHER = hexc('#6a5a49')


def helmet_front(L, cx, yh, a, seed=0, col=None):
    """铁盔（正面）：圆顶 + 额前的护沿 + 两侧护颊 + 顶上的盔缨座和灰缨。yh = 额头顶。"""
    col = STEEL if col is None else np.asarray(col, F)
    # 护颊（先画，在脸两侧）
    for s_ in (-1, 1):
        cheek = [(cx + s_ * a * 0.92, yh + 6), (cx + s_ * a * 1.12, yh + 20), (cx + s_ * a * 1.1, yh + 70), (cx + s_ * a * 0.92, yh + 84), (cx + s_ * a * 0.8, yh + 56)]
        garment(L, cheek, mix(col, INK, 0.2), seed + 3 + s_, shade=0.35, stain=0.35, flick=0.3, ink_w=2.0, smooth=1, rough=0.6)
    dome = [(cx - a * 1.1, yh + 16), (cx - a * 1.08, yh - 8), (cx - a * 0.86, yh - 34), (cx - a * 0.45, yh - 52), (cx, yh - 58), (cx + a * 0.45, yh - 52), (cx + a * 0.86, yh - 34), (cx + a * 1.08, yh - 8), (cx + a * 1.1, yh + 16), (cx, yh + 20)]
    dp, dm = garment(L, dome, col, seed, shade=0.42, shade_dir=1, stain=0.4, worn=0.25, flick=0.5, fdir=70, ink_w=2.4, smooth=1, rough=0.6, edge_dk=0.2, dark=STEEL_DK, light=hexc('#c4ccd4'),
                     folds=[[(cx, yh - 56), (cx, yh + 14)], [(cx - a * 0.55, yh - 40), (cx - a * 0.7, yh + 6)], [(cx + a * 0.55, yh - 40), (cx + a * 0.7, yh + 6)]], fold_op=0.5)
    # 额前护沿
    brim = [(cx - a * 1.12, yh + 12), (cx - a * 0.5, yh + 22), (cx, yh + 24), (cx + a * 0.5, yh + 22), (cx + a * 1.12, yh + 12), (cx + a * 1.1, yh + 20), (cx, yh + 32), (cx - a * 1.1, yh + 20)]
    garment(L, brim, mix(col, STEEL_DK, 0.35), seed + 6, shade=0.3, stain=0.3, flick=0.2, ink_w=2.0, smooth=1, rough=0.5)
    # 铆钉
    dots(L, [(cx + (k - 3) * a * 0.28, yh + 18 + 2 * abs(k - 3) * 0.6, 1.6) for k in range(7)], hexc('#d8dde0'), op=0.7)
    # 盔缨座 + 灰缨
    garment(L, [(cx - 6, yh - 56), (cx + 6, yh - 56), (cx + 5, yh - 68), (cx, yh - 76), (cx - 5, yh - 68)], STEEL_DK * 1.2, seed + 7, smooth=0, wob=0.3, ink_w=1.6, shade=0.3, stain=0.2, flick=0, rough=0.2, speck=0)
    r = np.random.default_rng(seed + 11)
    for k in range(22):
        t = (k - 11) / 11
        sx, sy = cx + t * 3, yh - 66
        brush(L, [(sx, sy), (sx + t * 36 + r.normal(0, 3), sy + 14 + abs(t) * 6 + r.normal(0, 2)), (sx + t * 52 + r.normal(0, 5), sy + 34 + abs(t) * 18 + r.normal(0, 4))], w0=3.2, w1=1.0,
              color=mix(hexc('#a3a5aa'), hexc('#dcdad4'), r.uniform(0, 0.7)) * r.uniform(0.75, 1.0), op=0.92, seed=int(r.integers(1e6)), taper=0.3, wob=0.6)


def guard_front_draw(cx=320, foot=760, H=540, seed=700, hold=True):
    L = new_canvas(660, 820)
    T = foot - H
    cy, a, b = T + 96, 40, 42
    ground_shadow(L, cx, foot + 2, 200, 16, 0.28, seed)
    cloth = mix(K['gb'], K['blue_dk'], 0.35)
    # 长枪（在手后面）
    sx = cx - 92
    spear_draw(L, sx, foot - 6, T - 96, 9, 66, seed + 1)
    # 靴 + 绑腿 + 裤
    for s_ in (-1, 1):
        leg(L, [(cx + s_ * 30, T + 330), (cx + s_ * 32, T + 400), (cx + s_ * 33, T + 468)], 52, 42, cloth, seed + 10 + s_, shade=0.4, stain=0.5, flick=0.7, fdir=88, ink_w=2.2, rough=1.0, edge_dk=0.2)
        leg(L, [(cx + s_ * 33, T + 440), (cx + s_ * 33, T + 482)], 46, 44, K['linen'], seed + 12 + s_, shade=0.3, stain=0.4, flick=0.6, fdir=0, ink_w=1.8, rough=0.8)
        boot_front(L, cx + s_ * 34, foot, 52, 64, K['dark2'], seed + 14 + s_)
    # 甲裙：一片片垂下的甲片
    belt_y = T + 272
    for k in range(7):
        t = (k - 3) / 3
        x = cx + t * 62
        w_ = 30
        plate = [(x - w_ / 2, belt_y), (x + w_ / 2, belt_y), (x + w_ / 2 + t * 3, belt_y + 86), (x, belt_y + 94), (x - w_ / 2 + t * 3, belt_y + 86)]
        pp, pm = garment(L, plate, mix(STEEL, LEATHER, 0.35 + 0.1 * (k % 2)), seed + 20 + k, shade=0.4, stain=0.4, worn=0.2, flick=0.3, ink_w=2.0, smooth=1, rough=0.6, dark=STEEL_DK, light=hexc('#aeb6bd'))
        bb = bbox_of(L, pp)
        scale_pattern(L, pm * 0.55, bb, STEEL, seed + 30 + k, dx=10, dy=9, op=0.8)
        line(L, [(x - w_ / 2 + 3, belt_y + 74), (x, belt_y + 80), (x + w_ / 2 - 3, belt_y + 74)], 1.2, STEEL_DK, 0.5, seed + 40 + k, 0.3, 0, 0.3)
    # 胸甲（札甲）
    rows = [(T + 144, 24, 24), (T + 152, 56, 56), (T + 166, 70, 70), (T + 196, 72, 72), (T + 236, 64, 64), (T + 270, 60, 60)]
    cp, cm = garment(L, lathe(cx, rows), STEEL, seed + 50, shade=0.4, shade_dir=1, stain=0.3, worn=0.2, flick=0.0, ink_w=2.5, smooth=1, rough=0.8, edge_dk=0.2, dark=STEEL_DK, light=hexc('#bcc4cc'), speck=0.3)
    scale_pattern(L, cm, bbox_of(L, cp), STEEL, seed + 51, dx=17, dy=13, op=0.9)
    side_glaze_mask = None
    # 胸前一道皮带 + 护心镜
    wash(L, ellipse_pts(cx, T + 196, 20, 20, 16, jit=0.03, seed=seed + 52), hexc('#aab2ba'), op=1.0, wob=0.6, seed=seed + 52, smooth=1, tex_k=0.12, rim=0.3)
    ink_outline(L, ellipse_pts(cx, T + 196, 20, 20, 16), seed + 53, w=2.0, op=0.8, gaps=0.15, closed=True)
    line(L, [(cx - 12, T + 190), (cx - 4, T + 186)], 2.0, hexc('#eef0f0'), 0.7, seed + 54, 0.4, 0, 0.1)
    for s_ in (-1, 1):
        line(L, [(cx + s_ * 24, T + 156), (cx + s_ * 18, T + 186), (cx + s_ * 6, T + 200)], 3.2, LEATHER, 0.9, seed + 55 + s_, 0.2, 0.1, 0.5)
    # 腰带
    belt = [(cx - 64, belt_y - 6), (cx + 64, belt_y - 6), (cx + 66, belt_y + 14), (cx - 66, belt_y + 14)]
    garment(L, belt, LEATHER, seed + 60, shade=0.35, stain=0.4, flick=0.5, fdir=0, ink_w=2.2, smooth=1, rough=0.6)
    wash(L, rot_rect(cx, belt_y + 4, 22, 22, 0.0), hexc('#a99f86'), op=1.0, wob=0.4, seed=seed + 61, smooth=1, tex_k=0.1, rim=0.3)
    ink_outline(L, rot_rect(cx, belt_y + 4, 22, 22, 0.0), seed + 62, w=1.8, op=0.8, gaps=0.1)
    neck(L, cx, cy + b - 8, T + 152, 34, seed + 63, skin=TAN)
    # 脖子上的衣领（灰蓝布）
    garment(L, [(cx - 30, T + 140), (cx + 30, T + 140), (cx + 38, T + 158), (cx, T + 170), (cx - 38, T + 158)], cloth, seed + 64, shade=0.35, stain=0.4, flick=0.5, ink_w=2.0, smooth=1, rough=0.6)
    # 肩甲
    for s_ in (-1, 1):
        for k, (dy_, rx_, ry_) in enumerate([(2, 46, 24), (18, 42, 20)]):
            pts = ellipse_pts(cx + s_ * 74, T + 166 + dy_, rx_, ry_, 16, rot=s_ * 0.35, jit=0.03, seed=seed + 70 + k + s_)
            pp, pm = garment(L, pts, mix(STEEL, STEEL_DK, 0.25 * k), seed + 70 + k + s_ * 3, shade=0.4, shade_dir=1, stain=0.3, worn=0.2, flick=0.0, ink_w=2.3, smooth=0, rough=0.7, dark=STEEL_DK, light=hexc('#bcc4cc'))
            scale_pattern(L, pm * 0.6, bbox_of(L, pp), STEEL, seed + 75 + k, dx=11, dy=9, op=0.8)
    # 手臂：右手（画面左）握枪，左手叉在腰间
    for i, s_ in enumerate((-1, 1)):
        if s_ == -1:
            sh, el, wr = (cx - 80, T + 182), (cx - 100, T + 238), (sx + 2, T + 300)
        else:
            sh, el, wr = (cx + 80, T + 182), (cx + 98, T + 240), (cx + 80, T + 292)
        ap = tube([sh, el, wr], 34, 29, cap0=0.9, cap1=0.0)
        shadow_on(L, cm, ap, -s_ * 5, 4, op=0.4)
        sleeve(L, [sh, el, wr], 34, 29, cloth, seed + 80 + i, shade=0.42, stain=0.5, worn=0.1, flick=0.7, fdir=82, streak=0.4, ink_w=2.4, edge_dk=0.2, rough=1.0,
               folds=[[(el[0] - s_ * 8, el[1] - 10), (el[0] - s_ * 2, el[1] + 3), (el[0] - s_ * 9, el[1] + 12)]])
        # 护臂
        gp = tube([(wr[0] + s_ * -2, wr[1] - 34), wr], 32, 30, cap=0.0)
        garment(L, gp, mix(STEEL, LEATHER, 0.5), seed + 90 + i, shade=0.4, stain=0.4, flick=0.3, ink_w=2.0, smooth=1, rough=0.6)
        for k in range(3):
            line(L, [(wr[0] - 15, wr[1] - 26 + k * 10), (wr[0] + 15, wr[1] - 26 + k * 10)], 1.4, STEEL_DK, 0.5, seed + 95 + k, 0.3, 0, 0.3, smooth=False)
        hand(L, wr[0], wr[1] + 2, math.pi / 2 + s_ * 0.0, 26, skin=TAN, seed=seed + 100 + i, kind='fist', side=-s_)
    # 脸 + 头盔
    face_front(L, cx, cy, a, b, seed + 110, skin=TAN, mood='stern', blush=0.2, eye_y=0.04, eye_sep=0.45, eye_r=0.085, brow='stern', mouth_w=0.2, age=0.15)
    # 小胡子
    for s_ in (-1, 1):
        brush(L, [(cx + s_ * 2, cy + b * 0.5), (cx + s_ * a * 0.22, cy + b * 0.52), (cx + s_ * a * 0.4, cy + b * 0.62)], w0=a * 0.14, w1=1.5, color=INK, op=0.9, seed=seed + 120 + s_, taper=0.3, wob=0.3)
    helmet_front(L, cx, cy - b + 6, a, seed + 130)
    return L, (cx, foot)


@sprite
def guard():
    L, anc = guard_front_draw()
    sheet_save(L, 'guard_front', anc, 41)


# ───────────────────────── 官员 ─────────────────────────
BLACK = hexc('#2f2d30')
OFFC = hexc('#5a6781')       # 灰蓝官袍


def wuSha_hat(L, cx, yh, a, seed=0, side=False, wing=60):
    """乌纱帽：圆顶 + 一圈帽檐 + 两侧平伸的展角（侧面看是一小截）。yh = 额头顶。"""
    crown = [(cx - a * 1.02, yh + 14), (cx - a * 1.0, yh - 12), (cx - a * 0.8, yh - 34), (cx - a * 0.35, yh - 46), (cx, yh - 48), (cx + a * 0.35, yh - 46), (cx + a * 0.8, yh - 34), (cx + a * 1.0, yh - 12), (cx + a * 1.02, yh + 14), (cx, yh + 18)]
    if not side:
        for s_ in (-1, 1):
            w_ = [(cx + s_ * a * 0.9, yh - 6), (cx + s_ * (a * 0.9 + wing), yh - 10), (cx + s_ * (a * 0.9 + wing + 6), yh - 2), (cx + s_ * (a * 0.9 + wing), yh + 4), (cx + s_ * a * 0.9, yh + 4)]
            garment(L, w_, BLACK * 1.1, seed + 3 + s_, shade=0.3, stain=0.25, flick=0.3, fdir=0, ink_w=2.0, smooth=1, rough=0.4, light=hexc('#8a8d99'), worn=0.2, speck=0.1)
    cp, cm = garment(L, crown, BLACK, seed, shade=0.4, stain=0.25, worn=0.35, flick=0.4, fdir=80, ink_w=2.2, smooth=1, rough=0.5, edge_dk=0.15, light=hexc('#7a7d8a'), dark=hexc('#17171a'), speck=0.1,
                     folds=[[(cx - a * 0.4, yh - 40), (cx - a * 0.5, yh + 8)], [(cx + a * 0.3, yh - 42), (cx + a * 0.4, yh + 8)]], fold_op=0.5)
    band = [(cx - a * 1.04, yh + 8), (cx + a * 1.04, yh + 8), (cx + a * 1.05, yh + 20), (cx - a * 1.05, yh + 20)]
    garment(L, band, mix(BLACK, hexc('#6b5d4a'), 0.5), seed + 7, shade=0.3, stain=0.3, flick=0.3, fdir=0, ink_w=2.0, smooth=1, rough=0.4)


def official_front_draw(cx=300, foot=670, H=520, seed=800):
    L = new_canvas(600, 720)
    T = foot - H
    cy, a, b = T + 80, 38, 42
    ground_shadow(L, cx, foot + 2, 190, 16, 0.28, seed)
    # 朝靴（黑靴白底）
    for s_ in (-1, 1):
        boot_front(L, cx + s_ * 32, foot, 50, 40, K['dark2'] * 0.9, seed + s_)
    # 袍
    rows = [(T + 134, 24, 24), (T + 142, 52, 52), (T + 156, 64, 64), (T + 190, 64, 64), (T + 240, 56, 56), (T + 262, 58, 58), (T + 330, 66, 66), (T + 420, 78, 78), (T + 480, 86, 86), (T + 496, 87, 87)]
    cp, cm = garment(L, lathe(cx, rows), OFFC, seed + 5, shade=0.42, shade_dir=1, stain=0.45, worn=0.12, flick=0.8, fdir=86, streak=0.6, ink_w=2.5, hem_dirt=0.3, smooth=1, edge_dk=0.22, rough=1.0, scale=30,
                     folds=[[(cx - 20, T + 300), (cx - 26, T + 390), (cx - 34, T + 490)], [(cx + 18, T + 300), (cx + 24, T + 390), (cx + 34, T + 490)], [(cx - 52, T + 330), (cx - 62, T + 410), (cx - 70, T + 490)], [(cx + 50, T + 330), (cx + 60, T + 410), (cx + 70, T + 490)]], fold_op=0.5)
    # 下摆的深色滚边
    garment(L, [(cx - 87, T + 468), (cx + 87, T + 468), (cx + 89, T + 498), (cx - 89, T + 498)], mix(OFFC, INK, 0.45), seed + 6, shade=0.3, stain=0.4, flick=0.4, fdir=0, ink_w=2.0, smooth=1, rough=1.0)
    neck(L, cx, cy + b - 8, T + 148, 30, seed + 7, skin=K['skin'])
    # 圆领
    ring = ellipse_pts(cx, T + 148, 36, 18, 18)
    garment(L, ring, mix(OFFC, K['white'], 0.35), seed + 8, shade=0.3, stain=0.3, flick=0.3, fdir=0, ink_w=2.0, smooth=1, rough=0.4)
    wash(L, ellipse_pts(cx, T + 150, 22, 9, 14), K['skin_sh'], op=1.0, wob=0.3, seed=seed + 9, smooth=1, tex_k=0.05, rim=0.1)
    # 补子（胸前方块）
    bx, by_ = cx, T + 205
    bp = rot_rect(bx, by_, 52, 50, 0.0)
    wash(L, bp, mix(OFFC, K['white'], 0.6), op=1.0, wob=0.8, seed=seed + 10, smooth=0, tex_k=0.15, rim=0.3)
    ink_outline(L, bp, seed + 11, w=1.5, op=0.6, gaps=0.2)
    brush(L, [(bx - 12, by_ + 14), (bx - 4, by_ - 2), (bx + 2, by_ - 12), (bx + 10, by_ - 14)], w0=2.2, color=INK, op=0.6, seed=seed + 12, taper=0.3, wob=0.5)   # 鹤（几笔）
    brush(L, [(bx - 4, by_ - 2), (bx + 14, by_ + 6), (bx + 24, by_ + 2)], w0=3.0, color=INK, op=0.45, seed=seed + 13, taper=0.3, wob=0.5)
    brush(L, [(bx - 20, by_ + 18), (bx + 20, by_ + 18)], w0=1.2, color=INK, op=0.4, seed=seed + 14, taper=0.4, wob=0.5)
    # 腰带（深色）+ 玉板
    belt_y = T + 262
    belt = [(cx - 60, belt_y - 12), (cx + 60, belt_y - 12), (cx + 62, belt_y + 14), (cx - 62, belt_y + 14)]
    garment(L, belt, hexc('#42413f'), seed + 15, shade=0.3, stain=0.3, flick=0.4, fdir=0, ink_w=2.2, smooth=1, rough=0.5)
    for k in range(5):
        wash(L, rot_rect(cx - 48 + k * 24, belt_y + 1, 16, 18, 0), K['jade'], op=1.0, wob=0.4, seed=seed + 20 + k, smooth=0, tex_k=0.1, rim=0.3)
        ink_outline(L, rot_rect(cx - 48 + k * 24, belt_y + 1, 16, 18, 0), seed + 30 + k, w=1.2, op=0.6, gaps=0.2, minseg=10, maxseg=30)
    # 拢袖：两条大袖从肩垂到腹前交叠
    for i, s_ in enumerate((-1, 1)):
        pth = [(cx + s_ * 58, T + 160), (cx + s_ * 80, T + 214), (cx + s_ * 56, T + 270), (cx + s_ * 8 * (1 if i else 1), T + 292)]
        ap = tube(pth, 48, 56, cap0=0.9, cap1=0.6)
        shadow_on(L, cm, ap, -s_ * 5, 5, op=0.4)
        sleeve(L, pth, 48, 56, mix(OFFC, K['blue_lt'], 0.12), seed + 40 + i, shade=0.44, stain=0.45, worn=0.1, flick=0.7, fdir=60, streak=0.5, ink_w=2.5, edge_dk=0.25, rough=0.9,
               folds=[[(cx + s_ * 74, T + 190), (cx + s_ * 82, T + 224), (cx + s_ * 66, T + 254)], [(cx + s_ * 40, T + 270), (cx + s_ * 28, T + 284)]])
    # 袖口白边（交叠处）
    garment(L, [(cx - 44, T + 276), (cx + 44, T + 276), (cx + 40, T + 300), (cx - 40, T + 300)], mix(OFFC, K['white'], 0.5), seed + 50, shade=0.35, stain=0.35, flick=0.3, fdir=0, ink_w=2.0, smooth=1, rough=0.6)
    line(L, [(cx - 6, T + 276), (cx - 2, T + 300)], 1.8, INKB, 0.7, seed + 51, 0.3, 0, 0.3)
    # 脸
    face_front(L, cx, cy, a, b, seed + 60, skin=K['skin'], mood='calm', blush=0.3, eye_y=0.08, eye_sep=0.44, eye_r=0.085, brow='plain', mouth_w=0.2, age=0.25)
    # 髭 + 山羊须
    for s_ in (-1, 1):
        brush(L, [(cx + s_ * 3, cy + b * 0.5), (cx + s_ * a * 0.25, cy + b * 0.55), (cx + s_ * a * 0.48, cy + b * 0.72), (cx + s_ * a * 0.5, cy + b * 0.92)], w0=a * 0.12, w1=1.2, color=INK, op=0.9, seed=seed + 70 + s_, taper=0.3, wob=0.4)
    gp = [(cx - a * 0.2, cy + b * 0.82), (cx + a * 0.2, cy + b * 0.82), (cx + a * 0.14, cy + b * 1.3), (cx, cy + b * 1.7), (cx - a * 0.14, cy + b * 1.3)]
    beard(L, gp, hexc('#4a4642'), seed + 72, strands=14)
    wuSha_hat(L, cx, cy - b + 6, a, seed + 80)
    return L, (cx, foot)


@sprite
def official():
    L, anc = official_front_draw()
    sheet_save(L, 'official_front', anc, 51)


def official_side_draw(cx=300, foot=670, H=520, seed=900):
    L = new_canvas(600, 720)
    T = foot - H
    cy, a, b = T + 80, 38, 42
    hx = cx + 8
    ground_shadow(L, cx + 6, foot + 2, 170, 16, 0.28, seed)
    boot_side(L, cx - 8, foot, 64, 40, K['dark2'] * 0.85, seed + 1)
    boot_side(L, cx + 16, foot, 64, 40, K['dark2'], seed + 2)
    rows = [(T + 134, 22, 24), (T + 142, 38, 40), (T + 156, 46, 50), (T + 190, 46, 52), (T + 240, 42, 50), (T + 262, 44, 52), (T + 330, 52, 58), (T + 420, 62, 66), (T + 480, 70, 72), (T + 496, 71, 73)]
    cp, cm = garment(L, lathe(cx, rows), OFFC, seed + 5, shade=0.42, shade_dir=1, stain=0.45, worn=0.12, flick=0.8, fdir=86, streak=0.6, ink_w=2.5, hem_dirt=0.3, smooth=1, edge_dk=0.22, rough=1.0, scale=30,
                     folds=[[(cx - 14, T + 300), (cx - 20, T + 390), (cx - 28, T + 490)], [(cx + 22, T + 300), (cx + 28, T + 390), (cx + 36, T + 490)]], fold_op=0.5)
    garment(L, [(cx - 71, T + 468), (cx + 73, T + 468), (cx + 75, T + 498), (cx - 73, T + 498)], mix(OFFC, INK, 0.45), seed + 6, shade=0.3, stain=0.4, flick=0.4, fdir=0, ink_w=2.0, smooth=1, rough=1.0)
    neck(L, hx - 4, cy + b - 8, T + 148, 30, seed + 7, skin=K['skin'])
    garment(L, ellipse_pts(cx + 2, T + 148, 26, 14, 18), mix(OFFC, K['white'], 0.35), seed + 8, shade=0.3, stain=0.3, flick=0.3, fdir=0, ink_w=2.0, smooth=1, rough=0.4)
    belt_y = T + 262
    garment(L, [(cx - 46, belt_y - 12), (cx + 54, belt_y - 12), (cx + 56, belt_y + 14), (cx - 48, belt_y + 14)], hexc('#42413f'), seed + 15, shade=0.3, stain=0.3, flick=0.4, fdir=0, ink_w=2.2, smooth=1, rough=0.5)
    for k in range(4):
        wash(L, rot_rect(cx - 26 + k * 20, belt_y + 1, 14, 18, 0), K['jade'], op=1.0, wob=0.4, seed=seed + 20 + k, smooth=0, tex_k=0.1, rim=0.3)
    # 拢袖：袖子垂到腹前向前伸出一截
    pth = [(cx - 2, T + 160), (cx + 12, T + 214), (cx + 30, T + 262), (cx + 52, T + 284)]
    ap = tube(pth, 50, 56, cap0=0.9, cap1=0.6)
    shadow_on(L, cm, ap, -5, 5, op=0.4)
    sleeve(L, pth, 50, 56, mix(OFFC, K['blue_lt'], 0.12), seed + 40, shade=0.44, stain=0.45, worn=0.1, flick=0.7, fdir=60, streak=0.5, ink_w=2.5, edge_dk=0.25, rough=0.9,
           folds=[[(cx + 18, T + 200), (cx + 24, T + 240)], [(cx + 38, T + 264), (cx + 48, T + 282)]])
    garment(L, [(cx + 44, T + 262), (cx + 64, T + 266), (cx + 66, T + 304), (cx + 46, T + 300)], mix(OFFC, K['white'], 0.5), seed + 50, shade=0.35, stain=0.35, flick=0.3, fdir=0, ink_w=2.0, smooth=1, rough=0.6)
    face_side(L, hx, cy, a, b, seed + 60, skin=K['skin'], mood='calm', blush=0.3, nose=1.6, eye_y=0.08, chin=0.95, age=0.25, browr=1.04)
    # 髭 + 须
    brush(L, [(hx + a * 0.95, cy + b * 0.5), (hx + a * 0.75, cy + b * 0.52), (hx + a * 0.55, cy + b * 0.64), (hx + a * 0.5, cy + b * 0.8)], w0=a * 0.12, w1=1.2, color=INK, op=0.9, seed=seed + 70, taper=0.3, wob=0.4)
    gp = [(hx + a * 0.4, cy + b * 0.82), (hx + a * 0.78, cy + b * 0.82), (hx + a * 0.72, cy + b * 1.3), (hx + a * 0.58, cy + b * 1.7), (hx + a * 0.42, cy + b * 1.3)]
    beard(L, gp, hexc('#4a4642'), seed + 72, strands=14)
    # 后脑的头发（帽下露出一点）
    hair_mass(L, [(hx - a * 0.6, cy - b * 0.6), (hx - a * 1.02, cy - b * 0.2), (hx - a * 1.02, cy + b * 0.4), (hx - a * 0.7, cy + b * 0.7), (hx - a * 0.3, cy + b * 0.4), (hx - a * 0.2, cy - b * 0.2)], None, seed + 75, strands=8, direction=100)
    wuSha_hat(L, hx - 4, cy - b + 6, a, seed + 80, side=True)
    # 帽后的一小截展角
    garment(L, [(hx - a * 0.9, cy - b - 6), (hx - a * 0.9 - 30, cy - b - 10), (hx - a * 0.9 - 34, cy - b - 2), (hx - a * 0.9, cy - b + 2)], BLACK * 1.1, seed + 81, shade=0.3, stain=0.25, flick=0.3, fdir=0, ink_w=2.0, smooth=1, rough=0.4, speck=0.1)
    return L, (cx + 6, foot)


@sprite
def official_side():
    L, anc = official_side_draw()
    sheet_save(L, 'official_side', anc, 52)


# ───────────────────────── 国王（坐像）─────────────────────────
GOLD = hexc('#c2b690')       # 灰金（降饱和，接近 #cfc29a）
GOLD_DK = hexc('#867b5d')
GOLD_LT = hexc('#e4dab8')


def roundel(L, x, y, r, col, seed=0, op=0.55):
    """衣服上的团花：一个圈 + 四瓣 + 中心点（淡淡的织纹）。"""
    brush(L, [(x + math.cos(a) * r, y + math.sin(a) * r) for a in np.linspace(0, 2 * math.pi * 0.98, 16)], w0=2.2, color=col, op=op, seed=seed, taper=0.1, wob=0.5, dry=0.2)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        brush(L, [(x + math.cos(a) * r * 0.25, y + math.sin(a) * r * 0.25), (x + math.cos(a + 0.35) * r * 0.62, y + math.sin(a + 0.35) * r * 0.62), (x + math.cos(a) * r * 0.82, y + math.sin(a) * r * 0.82)], w0=2.0, color=col, op=op * 0.9, seed=seed + k, taper=0.35, wob=0.4)
    dots(L, [(x, y, 2.2)], col, op=op)


def king_seated_draw(cx=350, base=640, H=520, seed=1000):
    L = new_canvas(700, 700)
    T = base - H
    cy, a, b = T + 92, 40, 44
    ground_shadow(L, cx, base + 2, 340, 16, 0.22, seed)
    robe = GOLD
    # 下摆：盘坐的衣摆，一大片，像一个缓坡
    rows = [(T + 268, 70, 70), (T + 300, 88, 88), (T + 350, 114, 114), (T + 410, 142, 144), (T + 470, 164, 166), (T + 508, 174, 176), (T + 524, 176, 178)]
    lp, lm = garment(L, lathe(cx, rows), robe, seed + 1, shade=0.4, shade_dir=1, stain=0.45, worn=0.15, flick=0.7, fdir=75, streak=0.6, ink_w=2.5, hem_dirt=0.3, smooth=1, edge_dk=0.22, rough=1.0, scale=34, dark=GOLD_DK, light=GOLD_LT,
                     folds=[[(cx - 30, T + 330), (cx - 56, T + 420), (cx - 80, T + 515)], [(cx + 26, T + 330), (cx + 52, T + 420), (cx + 80, T + 515)], [(cx - 96, T + 360), (cx - 120, T + 440), (cx - 148, T + 515)], [(cx + 94, T + 360), (cx + 120, T + 440), (cx + 148, T + 515)], [(cx, T + 330), (cx + 4, T + 420), (cx + 2, T + 515)]], fold_op=0.5)
    # 下摆的滚边
    garment(L, [(cx - 176, T + 498), (cx + 176, T + 498), (cx + 180, T + 526), (cx - 180, T + 526)], mix(GOLD, GOLD_DK, 0.55), seed + 2, shade=0.3, stain=0.4, flick=0.5, fdir=0, ink_w=2.0, smooth=1, rough=1.0)
    for x in (-110, -50, 50, 110):
        roundel(L, cx + x, T + 450, 18, GOLD_LT * 0.95, seed + 3 + int(x), 0.5)
    # 袍身
    rows = [(T + 144, 24, 24), (T + 152, 58, 58), (T + 166, 76, 76), (T + 200, 80, 80), (T + 250, 72, 72), (T + 285, 70, 70)]
    tp, tm = garment(L, lathe(cx, rows), robe, seed + 10, shade=0.4, shade_dir=1, stain=0.45, worn=0.12, flick=0.6, fdir=86, streak=0.5, ink_w=2.5, smooth=1, edge_dk=0.22, rough=0.9, dark=GOLD_DK, light=GOLD_LT,
                     folds=[[(cx - 40, T + 190), (cx - 46, T + 240), (cx - 40, T + 280)], [(cx + 40, T + 190), (cx + 46, T + 240), (cx + 40, T + 280)]], fold_op=0.45)
    roundel(L, cx, T + 215, 24, GOLD_LT, seed + 11, 0.55)
    # 衣襟（交领，白色里衣）
    neck(L, cx, cy + b - 8, T + 152, 32, seed + 12)
    wash(L, [(cx - 26, T + 142), (cx + 26, T + 142), (cx + 4, T + 186), (cx - 4, T + 186)], K['white'], op=1.0, wob=0.5, seed=seed + 13, smooth=1, tex_k=0.1, rim=0.2)
    line(L, [(cx - 34, T + 144), (cx - 6, T + 190), (cx + 26, T + 270)], 2.6, GOLD_DK, 0.85, seed + 14, 0.2, 0.1, 0.4)
    line(L, [(cx + 34, T + 144), (cx + 8, T + 190), (cx + 26, T + 270)], 2.4, GOLD_DK, 0.8, seed + 15, 0.2, 0.1, 0.4)
    # 腰带 + 玉佩
    by_ = T + 276
    garment(L, [(cx - 82, by_ - 12), (cx + 82, by_ - 12), (cx + 84, by_ + 14), (cx - 84, by_ + 14)], mix(GOLD_DK, INK, 0.3), seed + 16, shade=0.3, stain=0.3, flick=0.4, fdir=0, ink_w=2.2, smooth=1, rough=0.5)
    for k in range(7):
        wash(L, rot_rect(cx - 66 + k * 22, by_ + 1, 14, 17, 0), K['jade'], op=1.0, wob=0.4, seed=seed + 20 + k, smooth=0, tex_k=0.1, rim=0.3)
    brush(L, [(cx, by_ + 14), (cx + 2, by_ + 50), (cx - 1, by_ + 90)], w0=5, color=K['jade_dk'], op=0.9, seed=seed + 30, taper=0.15, wob=0.6)
    wash(L, ellipse_pts(cx - 1, by_ + 96, 9, 12, 12), K['jade'], op=1.0, wob=0.4, seed=seed + 31, smooth=1, tex_k=0.1, rim=0.3)
    # 宽袖：垂到膝上
    for i, s_ in enumerate((-1, 1)):
        pth = [(cx + s_ * 70, T + 172), (cx + s_ * 104, T + 240), (cx + s_ * 108, T + 312), (cx + s_ * 96, T + 352)]
        ap = tube(pth, 48, 64, cap0=0.9, cap1=0.2)
        shadow_on(L, tm, ap, -s_ * 6, 5, op=0.4)
        sleeve(L, pth, 48, 64, mix(robe, K['white'], 0.06), seed + 40 + i, shade=0.44, stain=0.45, worn=0.12, flick=0.7, fdir=60, streak=0.5, ink_w=2.5, edge_dk=0.25, rough=0.9, dark=GOLD_DK, light=GOLD_LT,
               folds=[[(cx + s_ * 92, T + 200), (cx + s_ * 100, T + 250), (cx + s_ * 96, T + 310)], [(cx + s_ * 70, T + 260), (cx + s_ * 82, T + 320)]])
        # 袖口镶边
        garment(L, [(cx + s_ * 70, T + 340), (cx + s_ * 146, T + 340), (cx + s_ * 144, T + 366), (cx + s_ * 72, T + 366)] if False else tube([(cx + s_ * 104, T + 344), (cx + s_ * 90, T + 356)], 70, 66, cap=0.0), mix(GOLD_DK, INK, 0.2), seed + 44 + i, shade=0.3, stain=0.3, flick=0.3, ink_w=2.0, smooth=1, rough=0.6)
        hand(L, cx + s_ * 74, T + 360, math.pi / 2 + s_ * 0.9, 28, skin=K['skin'], seed=seed + 50 + i, kind='open', side=-s_)
    # 脸 + 胡须 + 冕
    face_front(L, cx, cy, a, b, seed + 60, skin=K['skin'], mood='calm', blush=0.3, eye_y=0.06, eye_sep=0.44, eye_r=0.085, brow='soft', mouth_w=0.2, age=0.2)
    for s_ in (-1, 1):
        hair_mass(L, [(cx + s_ * a * 0.82, cy - b * 1.0), (cx + s_ * a * 1.06, cy - b * 0.7), (cx + s_ * a * 1.08, cy + b * 0.25), (cx + s_ * a * 0.92, cy + b * 0.1), (cx + s_ * a * 0.84, cy - b * 0.4)], hexc('#4a4743'), seed + 65 + s_, strands=6, direction=95, wob=0.6)
    beard_front(L, cx, cy, a, b, hexc('#8a857d'), seed + 70, length=2.0, w=0.95, strands=60)
    # 冕：帽圈 + 冕板 + 玉旒
    garment(L, [(cx - 50, T + 22), (cx + 50, T + 22), (cx + 54, T + 48), (cx - 54, T + 48)], hexc('#4b4d59'), seed + 80, shade=0.3, stain=0.2, flick=0.3, fdir=0, ink_w=2.2, smooth=1, rough=0.5, speck=0.1, light=hexc('#8a8c98'), worn=0.2)
    line(L, [(cx - 52, T + 40), (cx + 52, T + 40)], 3.0, GOLD, 0.8, seed + 81, 0.1, 0.1, 0.3)
    garment(L, [(cx - 66, T + 2), (cx + 66, T + 2), (cx + 70, T + 20), (cx - 70, T + 20)], hexc('#3c3e48'), seed + 82, shade=0.3, stain=0.2, flick=0.3, fdir=0, ink_w=2.4, smooth=1, rough=0.6, speck=0.1, light=hexc('#8a8c98'), worn=0.2)
    line(L, [(cx - 68, T + 18), (cx + 68, T + 18)], 2.4, GOLD, 0.8, seed + 83, 0.1, 0.1, 0.3)
    r = np.random.default_rng(seed + 90)
    for k in range(11):
        x = cx - 60 + k * 12
        ln_ = 44 + r.uniform(-4, 6)
        line(L, [(x, T + 20), (x + r.normal(0, 0.6), T + 20 + ln_ * 0.5), (x, T + 20 + ln_)], 1.2, GOLD_DK, 0.75, seed + 91 + k, 0.1, 0, 0.2)
        for j in range(1, 5):
            dots(L, [(x, T + 20 + ln_ * j / 4.2, 2.2)], mix(GOLD_LT, K['jade'], 0.3 * (j % 2)), op=0.9, soft=0.5)
    return L, (cx, base)


@sprite
def king_seated():
    L, anc = king_seated_draw()
    sheet_save(L, 'king_seated', anc, 61)


# ───────────────────────── 天门神 ─────────────────────────
WHITE = hexc('#e6e2d6')
WHITE_SH = hexc('#9ea9bb')


def ribbon(L, pts, w0, w1, col, seed=0, op=0.95):
    """飘带：沿曲线的一条细长带子，带一道折线和淡淡的边。"""
    p = tube(pts, w0, w1, cap0=0.3, cap1=0.3)
    garment(L, p, col, seed, shade=0.35, shade_dir=1, stain=0.25, flick=0.0, ink_w=1.6, ink_op=0.6, smooth=1, rough=0.5, wob=0.8, speck=0.0, dark=WHITE_SH, light=hexc('#f2f0ea'), tex_k=0.08, op=op, edge_dk=0.12, gaps=0.3)


def god_draw(cx=350, foot=730, H=600, seed=1100):
    L = new_canvas(700, 780)
    T = foot - H
    cy, a, b = T + 74, 40, 44
    # 背景里的光环（淡灰金）
    hx, hy, hr = cx, cy - 4, 86
    glow(L, hx, hy, hr * 1.4, hexc('#f4efdc'), op=0.22, power=2.2)
    ring = [(hx + math.cos(t) * hr, hy + math.sin(t) * hr) for t in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
    wash(L, ring, hexc('#f4efdc'), op=0.12, wob=1.5, seed=seed + 1, smooth=2, tex_k=0.05, rim=0.0)
    for k, (rr, w_, op_) in enumerate([(hr, 4.0, 0.8), (hr - 8, 1.6, 0.5), (hr + 6, 1.4, 0.35)]):
        brush(L, [(hx + math.cos(t) * rr, hy + math.sin(t) * rr) for t in np.linspace(0.1 + k * 0.4, 2 * math.pi * 0.995 + 0.1 + k * 0.4, 36)], w0=w_, color=hexc('#cfc29a') * (0.92 if k == 0 else 1.0), op=op_, seed=seed + 2 + k, wob=0.7, taper=0.04, dry=0.15 if k == 0 else 0.3)
    for k in range(24):    # 光环上的细刻度
        t = k * math.pi / 12
        brush(L, [(hx + math.cos(t) * (hr - 4), hy + math.sin(t) * (hr - 4)), (hx + math.cos(t) * (hr + 4), hy + math.sin(t) * (hr + 4))], w0=1.1, color=hexc('#b3a77f'), op=0.5, seed=seed + 10 + k, smooth=False, taper=0.2)
    ground_shadow(L, cx, foot + 2, 220, 14, 0.15, seed, col=hexc('#9ba3b3'))
    # 云（脚下的淡云）
    r = np.random.default_rng(seed + 5)
    for k in range(9):
        x = cx + (k - 4) * 34 + r.normal(0, 6)
        pts = ellipse_pts(x, foot - 6 + r.normal(0, 4), 44 + r.uniform(-8, 12), 20 + r.uniform(-4, 6), 14, jit=0.1, seed=seed + 20 + k)
        wash(L, pts, mix(hexc('#cfd6e0'), hexc('#f2f0ea'), r.uniform(0.2, 0.8)), op=0.75, wob=2.0, seed=seed + 20 + k, smooth=2, tex_k=0.1, rim=0.2)
    # 背后的长发
    for s_ in (-1, 1):
        hp = [(cx + s_ * 38, cy - 26), (cx + s_ * 60, cy + 20), (cx + s_ * 72, T + 190), (cx + s_ * 80, T + 270), (cx + s_ * 56, T + 300), (cx + s_ * 46, T + 230), (cx + s_ * 36, cy + 50)]
        hair_mass(L, hp, hexc('#d4d1ca'), seed + 30 + s_, strands=24, direction=90, wob=1.5, sheen=0.3, hi=False)
    # 飘带（披帛）：从肩上扬起，在风里起伏着飘开
    def wave(x0, y0, sx, n=6, amp=20, dx=34, dy=-14, ph=0.0):
        return [(x0 + sx * (k * dx), y0 + k * dy + math.sin(k * 1.25 + ph) * amp) for k in range(n)]
    for s_, ph in ((-1, 0.0), (1, 1.2)):
        ribbon(L, wave(cx + s_ * 60, T + 176, s_, 7, 22, 34, -12, ph), 22, 4, hexc('#cdd4df'), seed + 40 + int(s_ + 1))
        ribbon(L, wave(cx + s_ * 74, T + 300, s_, 6, 18, 36, 12, ph + 0.8), 18, 4, hexc('#d6dce5'), seed + 43 + int(s_ + 1))
    # 长衣（素白，带蓝灰的影），下摆随风翻出波浪
    rows = [(T + 134, 24, 24), (T + 142, 56, 56), (T + 158, 72, 72), (T + 200, 76, 76), (T + 262, 68, 68), (T + 330, 84, 84), (T + 420, 100, 100), (T + 510, 116, 116), (T + 576, 126, 126), (T + 596, 130, 130)]
    rp, rm = garment(L, lathe(cx, rows), WHITE, seed + 50, shade=0.5, shade_dir=1, shade_start=0.55, stain=0.14, worn=0.0, flick=0.3, speck=0.1, fdir=86, streak=0.0, ink_w=2.3, ink_op=0.7, hem_dirt=0.15, smooth=1, edge_dk=0.15, rough=1.0, scale=34, dark=WHITE_SH * 0.9, light=hexc('#faf8f2'),
                     folds=[[(cx - 20, T + 300), (cx - 30, T + 420), (cx - 44, T + 585)], [(cx + 22, T + 300), (cx + 34, T + 420), (cx + 50, T + 585)], [(cx - 58, T + 340), (cx - 76, T + 440), (cx - 96, T + 580)], [(cx + 58, T + 340), (cx + 78, T + 440), (cx + 98, T + 580)]], fold_op=0.45)
    # 波浪形的下摆
    hem = [(cx - 128, T + 566)] + [(cx - 128 + k * 32, T + 568 + (10 if k % 2 else -4)) for k in range(1, 8)] + [(cx + 128, T + 566), (cx + 130, T + 600)] + [(cx + 128 - k * 32, T + 604 + (6 if k % 2 else -2)) for k in range(0, 9)] + [(cx - 130, T + 600)]
    garment(L, hem, mix(WHITE, WHITE_SH, 0.3), seed + 51, shade=0.3, stain=0.2, flick=0.3, fdir=0, ink_w=1.8, ink_op=0.6, smooth=1, rough=1.2, dark=WHITE_SH * 0.8, light=hexc('#faf8f2'), speck=0.1)
    neck(L, cx, cy + b - 8, T + 150, 30, seed + 52)
    # 交领（蓝灰的领缘）
    wash(L, [(cx - 24, T + 142), (cx + 24, T + 142), (cx + 3, T + 190), (cx - 3, T + 190)], K['skin'] * 0.96, op=1.0, wob=0.5, seed=seed + 53, smooth=1, tex_k=0.05, rim=0.2)
    line(L, [(cx - 34, T + 146), (cx - 6, T + 192), (cx + 24, T + 270)], 3.4, WHITE_SH, 0.9, seed + 54, 0.2, 0.1, 0.4)
    line(L, [(cx + 34, T + 146), (cx + 6, T + 192), (cx + 24, T + 270)], 3.0, WHITE_SH, 0.9, seed + 55, 0.2, 0.1, 0.4)
    line(L, [(cx - 36, T + 146), (cx - 8, T + 192), (cx + 24, T + 272)], 1.4, INKB, 0.55, seed + 56, 0.2, 0.1, 0.4)
    # 腰带 + 垂带
    by_ = T + 268
    garment(L, [(cx - 68, by_ - 10), (cx + 68, by_ - 10), (cx + 70, by_ + 12), (cx - 70, by_ + 12)], hexc('#aab6c8'), seed + 57, shade=0.35, stain=0.25, flick=0.3, fdir=0, ink_w=1.9, ink_op=0.7, smooth=1, rough=0.5, speck=0.0)
    for k, dx in enumerate((-14, 14)):
        ribbon(L, [(cx + dx * 0.3, by_ + 10), (cx + dx, by_ + 70), (cx + dx * 1.8, by_ + 150)], 16, 8, hexc('#c1cad8'), seed + 58 + k)
    # 玉尺
    rx = cx - 112
    ruler = [(rx - 8, T + 170), (rx + 8, T + 170), (rx + 8, T + 500), (rx - 8, T + 500)]
    rp_, rm_ = garment(L, ruler, K['jade'], seed + 60, shade=0.4, shade_dir=1, stain=0.15, flick=0.0, ink_w=1.8, ink_op=0.65, smooth=0, rough=0.4, wob=0.5, speck=0.0, dark=K['jade_dk'], light=hexc('#eef6f2'), worn=0.3, tex_k=0.1, op=1.0)
    for k in range(0, 24):
        yy = T + 180 + k * 13.5
        line(L, [(rx - 8, yy), (rx - (3 if k % 2 else 0), yy)], 1.0, K['jade_dk'] * 0.7, 0.7, seed + 70 + k, 0.2, 0, 0.1, smooth=False)
    # 袖子：右手（画面左）握玉尺，左手（画面右）抬起，掌心向外
    for i, s_ in enumerate((-1, 1)):
        if s_ == -1:
            pth = [(cx - 68, T + 160), (cx - 100, T + 230), (cx - 108, T + 300)]
            wr = pth[-1]
        else:
            pth = [(cx + 68, T + 160), (cx + 112, T + 220), (cx + 138, T + 270)]
            wr = pth[-1]
        ap = tube(pth, 46, 62, cap0=0.9, cap1=0.2)
        shadow_on(L, rm, ap, -s_ * 5, 4, op=0.35)
        sleeve(L, pth, 46, 62, mix(WHITE, WHITE_SH, 0.1), seed + 80 + i, shade=0.5, shade_dir=1, shade_start=0.55, stain=0.3, flick=0.4, fdir=70, streak=0.0, ink_w=2.2, ink_op=0.7, edge_dk=0.15, rough=0.8, dark=WHITE_SH * 0.9, light=hexc('#faf8f2'),
               folds=[[(pth[1][0] - s_ * 6, pth[1][1] - 18), (pth[1][0] + s_ * 2, pth[1][1] + 10)]], fold_op=0.4)
        garment(L, tube([(wr[0] - s_ * 6, wr[1] - 20), wr], 62, 60, cap=0.0), mix(WHITE_SH, WHITE, 0.4), seed + 84 + i, shade=0.3, stain=0.2, flick=0.2, ink_w=1.8, ink_op=0.6, smooth=1, rough=0.6, speck=0.0)
    hand(L, cx - 110, T + 326, math.pi / 2, 28, skin=K['skin'], seed=seed + 90, kind='fist', side=1)
    hand(L, cx + 144, T + 262, -math.pi / 2 + 0.5, 28, skin=K['skin'], seed=seed + 91, kind='open', side=1)
    # 脸 + 须发
    face_front(L, cx, cy, a, b, seed + 100, skin=K['skin'], mood='smile', blush=0.35, eye_y=0.08, eye_sep=0.44, eye_r=0.085, brow='white', mouth_w=0.2, age=0.25)
    beard_front(L, cx, cy, a, b, hexc('#e4e2dc'), seed + 101, length=2.2, w=1.0, strands=60)
    # 额前白发 + 发髻
    for s_ in (-1, 1):
        hair_mass(L, [(cx + s_ * 2, cy - b * 0.9), (cx + s_ * a * 0.6, cy - b * 0.86), (cx + s_ * a * 1.0, cy - b * 0.3), (cx + s_ * a * 1.06, cy + b * 0.3), (cx + s_ * a * 0.9, cy + b * 0.1), (cx + s_ * a * 0.82, cy - b * 0.2), (cx + s_ * a * 0.4, cy - b * 0.6)], hexc('#dcd9d2'), seed + 110 + s_, strands=10, direction=90, wob=0.8, hi=False)
    hair_mass(L, [(cx - a * 0.9, cy - b * 0.7), (cx - a * 0.5, cy - b * 1.1), (cx, cy - b * 1.2), (cx + a * 0.5, cy - b * 1.1), (cx + a * 0.9, cy - b * 0.7), (cx + a * 0.5, cy - b * 0.82), (cx, cy - b * 0.86), (cx - a * 0.5, cy - b * 0.82)], hexc('#dcd9d2'), seed + 112, strands=14, direction=0, wob=0.8, hi=False)
    # 发髻（束在头顶，用玉簪）
    hair_mass(L, ellipse_pts(cx, cy - b * 1.34, 24, 18, 14, jit=0.04, seed=seed + 113), hexc('#d9d6cf'), seed + 114, strands=12, direction=90, wob=0.8, hi=False)
    line(L, [(cx - 34, cy - b * 1.3), (cx + 34, cy - b * 1.36)], 3.2, K['jade'], 0.95, seed + 115, 0.15, 0, 0.3)
    return L, (cx, foot)


@sprite
def god():
    L, anc = god_draw()
    sheet_save(L, 'god', anc, 71)
