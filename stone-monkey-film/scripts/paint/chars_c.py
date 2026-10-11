"""新人物与小道具（续）。"""
from chars_new import *

# ───────────────────────── 头发 / 头饰（正面）─────────────────────────
def hair_messy(L, cx, cy, a, b, seed=0, tuft=8, fringe=0.42):
    return hair_cap_front(L, cx, cy, a, b, seed, fringe=fringe, side=0.25, puff=1.04, tuft=tuft, spiky=1.0)


def hair_bun_woman(L, cx, cy, a, b, seed=0, col=None, pin=True):
    hair_cap_front(L, cx, cy, a, b, seed, fringe=0.3, side=0.5, puff=1.05, col=col)
    # 中分线
    line(L, [(cx, cy - b * 1.1), (cx + 1, cy - b * 0.7), (cx - 1, cy - b * 0.42)], 1.2, hexc('#8d8a90'), 0.7, seed + 1, 0.3, 0, 0.2)
    bun = ellipse_pts(cx, cy - b * 1.28, a * 0.5, a * 0.42, 14, jit=0.04, seed=seed + 2)
    hair_mass(L, bun, col, seed + 3, strands=10, direction=0)
    if pin:
        line(L, [(cx - a * 0.7, cy - b * 1.26), (cx + a * 0.75, cy - b * 1.34)], 2.6, K['wood_lt'], 0.95, seed + 4, 0.2, 0, 0.3)


def hair_topknot(L, cx, cy, a, b, seed=0, col=None, knot=True):
    hair_cap_front(L, cx, cy, a, b, seed, fringe=0.18, side=0.15, puff=1.02, col=col)
    if knot:
        hair_mass(L, ellipse_pts(cx, cy - b * 1.28, a * 0.3, a * 0.34, 12, jit=0.05, seed=seed + 2), col, seed + 3, strands=5, direction=90)
        line(L, [(cx - a * 0.3, cy - b * 1.12), (cx + a * 0.3, cy - b * 1.12)], 2.6, K['stone'], 0.9, seed + 4, 0.2, 0, 0.3)


def hair_old_white(L, cx, cy, a, b, seed=0):
    """老人：头顶稀疏，两侧和脑后的白发。"""
    for s_ in (-1, 1):
        hp = [(cx + s_ * a * 0.74, cy - b * 0.7), (cx + s_ * a * 1.04, cy - b * 0.3), (cx + s_ * a * 1.08, cy + b * 0.3), (cx + s_ * a * 0.92, cy + b * 0.05), (cx + s_ * a * 0.84, cy - b * 0.3)]
        hair_mass(L, hp, hexc('#dcd9d2'), seed + s_, strands=8, direction=90, wob=0.8, hi=False)
    # 头顶薄薄的几缕
    for k in range(6):
        x = cx + (k - 2.5) * a * 0.3
        line(L, [(x, cy - b * 0.98), (x + (k - 2.5) * 2, cy - b * 0.82), (x + (k - 2.5) * 3, cy - b * 0.72)], 1.3, hexc('#cfccc6'), 0.8, seed + 10 + k, 0.4, 0, 0.3)


def head_cloth(L, cx, cy, a, b, seed=0, col=None, knot_side=1):
    """男子的包头布：绕额头一圈 + 头顶一块，侧面打结，两个布角。"""
    col = K['stone'] if col is None else np.asarray(col, F)
    pts = [(cx - a * 1.08, cy - b * 0.05), (cx - a * 1.04, cy - b * 0.7), (cx - a * 0.6, cy - b * 1.12), (cx, cy - b * 1.22), (cx + a * 0.6, cy - b * 1.12), (cx + a * 1.04, cy - b * 0.7), (cx + a * 1.08, cy - b * 0.05),
           (cx + a * 0.9, cy - b * 0.3), (cx + a * 0.5, cy - b * 0.5), (cx, cy - b * 0.54), (cx - a * 0.5, cy - b * 0.5), (cx - a * 0.9, cy - b * 0.3)]
    garment(L, pts, col, seed, shade=0.4, stain=0.4, worn=0.1, flick=0.8, fdir=10, ink_w=2.0, smooth=1, edge_dk=0.2, rough=0.8,
            folds=[[(cx - a * 0.8, cy - b * 0.4), (cx, cy - b * 0.7), (cx + a * 0.8, cy - b * 0.4)], [(cx - a * 0.5, cy - b * 0.9), (cx + a * 0.3, cy - b * 1.0)]])
    kx, ky = cx + knot_side * a * 1.0, cy - b * 0.5
    wash(L, ellipse_pts(kx, ky, 9, 8, 10, jit=0.1, seed=seed), mix(col, K['blue_dk'], 0.3), op=1.0, wob=0.5, seed=seed + 1, smooth=1)
    for k, (dx, dy) in enumerate([(16, 4), (12, 20)]):
        brush(L, [(kx, ky), (kx + knot_side * dx * 0.6, ky + dy * 0.4), (kx + knot_side * dx, ky + dy)], w0=8, w1=3, color=col, op=0.95, seed=seed + 5 + k, taper=0.2, wob=0.5)
        line(L, [(kx, ky + 1), (kx + knot_side * dx * 0.6, ky + dy * 0.4 + 1), (kx + knot_side * dx, ky + dy + 1)], 1.5, INKB, 0.6, seed + 8 + k, 0.4, 0, 0.3)


def hair_braids(L, cx, cy, a, b, seed=0, ribbon_col=None, length=1.9):
    ribbon_col = K['stone'] if ribbon_col is None else np.asarray(ribbon_col, F)
    for s_ in (-1, 1):
        pts = [(cx + s_ * a * 1.0, cy + b * 0.25), (cx + s_ * a * 1.15, cy + b * 0.8), (cx + s_ * a * 1.0, cy + b * 1.3), (cx + s_ * a * 1.12, cy + b * length)]
        p = tube(pts, a * 0.3, a * 0.22, cap0=0.4, cap1=0.9)
        hp = hair_mass(L, p, None, seed + 20 + s_, strands=6, direction=90, wob=0.6, smooth=1)
        for k in range(1, 5):   # 辫子的节
            t = k / 5
            yy = cy + b * (0.25 + (length - 0.25) * t)
            xx = cx + s_ * a * (1.05 + 0.05 * math.sin(t * 5))
            line(L, [(xx - a * 0.16, yy - 2), (xx + a * 0.16, yy + 2)], 1.3, hexc('#6a6870'), 0.6, seed + 30 + k + s_, 0.3, 0, 0.2, smooth=False)
        ex, ey = pts[-1]
        wash(L, ellipse_pts(ex, ey - 2, 8, 6, 10), ribbon_col, op=1.0, wob=0.4, seed=seed + 40 + s_, smooth=1)
    hair_cap_front(L, cx, cy, a, b, seed, fringe=0.3, side=0.3, puff=1.06)


def mustache_front(L, cx, cy, a, b, seed=0, col=None, w=0.12, drop=0.8):
    col = INK if col is None else col
    for s_ in (-1, 1):
        brush(L, [(cx + s_ * 3, cy + b * 0.5), (cx + s_ * a * 0.25, cy + b * 0.55), (cx + s_ * a * 0.44, cy + b * (0.5 + drop * 0.3))], w0=a * w, w1=1.3, color=col, op=0.9, seed=seed + s_, taper=0.3, wob=0.3)


# ───────────────────────── 通用的正面站姿人物 ─────────────────────────
def human_front(cx=300, foot=700, H=500, kind='adult', seed=0, canvas=(600, 760), top_col=None, bot_col=None, skin=None,
                bot='trousers', top_style='tunic', top_len=0.30, a=None, b=None, face=None, hair=None, hat=None, beard=None,
                arms=None, belt=None, patches=(), shoe_col=None, hand_kind=('open', 'open'), wrap=True, sleeve_w=None, dx_head=0, stoop=0.0,
                skirt_len=0.06, extra_back=None, extra_front=None, cuff=True, shade_dir=1, leg_gap=None, hand_skin=None, snow=0.0, bot_hem=None, lean=None, legs_fn=None, bw=1.0, deco_bot=None, skirt_hw=None, deco_top=None, face_fn=None):
    """一个站着的人：脚 → 下装 → 上衣 → 袖/手 → 头。kind: kid / adult / old。尺寸都按 H 缩放。
    arms: {'L': (el_dx, el_dy, wr_dx, wr_dy), 'R': ...}（相对肩点的偏移，单位 H）。"""
    L = new_canvas(*canvas)
    T = foot - H
    top_col = K['blue'] if top_col is None else np.asarray(top_col, F)
    bot_col = K['gb'] if bot_col is None else np.asarray(bot_col, F)
    skin = K['skin'] if skin is None else np.asarray(skin, F)
    hand_skin = skin if hand_skin is None else hand_skin
    kd = {'kid': (0.108, 0.138, 0.185, 0.345), 'adult': (0.077, 0.081, 0.155, 0.265), 'old': (0.086, 0.100, 0.16, 0.265)}[kind]
    a = H * kd[0] if a is None else a
    b = H * kd[1] if b is None else b
    cy = T + H * kd[2]
    jy = cy + b + (8 if kind != 'kid' else 8)
    hw_s = H * 0.125 * bw
    hw_w = hw_s * (0.86 if top_style != 'robe' else 0.9)
    hip_y = jy + H * (0.25 if kind != 'kid' else 0.27)
    ankle = foot - H * 0.05
    ground_shadow(L, cx, foot + 2, H * 0.34, H * 0.03, 0.28, seed)
    if extra_back:
        extra_back(L, cx, T, jy)
    # ── 下装
    if legs_fn is not None:
        legs_fn(L, cx, foot, hip_y, ankle)
        cover_y = hip_y
    elif bot == 'trousers':
        gap = H * 0.055 if leg_gap is None else leg_gap
        for s_ in (-1, 1):
            top_w, bot_w = H * 0.105, H * 0.075
            leg(L, [(cx + s_ * gap * 0.9, hip_y), (cx + s_ * gap, (hip_y + ankle) / 2), (cx + s_ * gap * 1.05, ankle)], top_w, bot_w, bot_col, seed + s_, shade=0.4, stain=0.5, flick=0.6, fdir=86, ink_w=2.0, edge_dk=0.18, rough=1.0, shade_dir=shade_dir,
                folds=[[(cx + s_ * gap * 0.6, hip_y + H * 0.1), (cx + s_ * gap * 0.7, hip_y + H * 0.25)]])
            if wrap:
                leg(L, [(cx + s_ * gap * 1.05, ankle - H * 0.08), (cx + s_ * gap * 1.05, ankle)], bot_w * 1.05, bot_w * 1.0, K['linen_lt'], seed + 5 + s_, shade=0.25, stain=0.35, flick=0.3, fdir=0, ink_w=1.6, rough=0.6)
            shoe_front(L, cx + s_ * gap * 1.15, foot, H * 0.1, H * 0.052, shoe_col if shoe_col is not None else K['dark'], seed + 10 + s_, snow=snow)
        cover_y = hip_y
    else:   # 长裙/长袍
        hem_y = foot - H * skirt_len
        waist_y = jy + H * 0.22
        hem_hw = H * (0.15 if bot == 'skirt' else 0.13) * bw if skirt_hw is None else skirt_hw
        rows = [(waist_y - 10, hw_w, hw_w), (waist_y + 20, hw_w * 1.12, hw_w * 1.12), ((waist_y + hem_y) / 2, (hw_w + hem_hw) / 2, (hw_w + hem_hw) / 2), (hem_y, hem_hw, hem_hw), (hem_y + 5, hem_hw * 1.01, hem_hw * 1.01)]
        for s_ in (-1, 1):
            shoe_front(L, cx + s_ * H * 0.06, foot, H * 0.1, H * 0.05, shoe_col if shoe_col is not None else K['dark'], seed + 10 + s_)
        bh = bot_hem if bot_hem is not None else mix(bot_col, INK, 0.3)
        sp_, sm_ = garment(L, lathe(cx, rows), bot_col, seed + 20, shade=0.42, shade_dir=shade_dir, stain=0.5, worn=0.1, flick=0.7, fdir=86, streak=0.4, ink_w=2.3, hem_dirt=0.3, smooth=1, edge_dk=0.2, rough=1.1,
                           folds=[[(cx - H * 0.04, waist_y + 20), (cx - H * 0.055, (waist_y + hem_y) / 2), (cx - H * 0.07, hem_y - 6)], [(cx + H * 0.04, waist_y + 20), (cx + H * 0.06, (waist_y + hem_y) / 2), (cx + H * 0.08, hem_y - 6)]])
        cover_y = waist_y
        if deco_bot:
            deco_bot(L, sm_, bbox_of(L, sp_), waist_y, hem_y)
    # ── 上衣（可以整体前倾：先画在临时画布上再旋转）
    Lu = new_canvas(*canvas) if lean else L
    th = H * top_len + (H * 0.04 if top_style == 'robe' else 0)
    rows = [(jy - 6, a * 0.35, a * 0.35), (jy - 1, a * 0.7, a * 0.7), (jy + 8, hw_s * 0.86, hw_s * 0.86), (jy + H * 0.03, hw_s, hw_s), (jy + th * 0.55, hw_w, hw_w), (jy + th * 0.9, hw_w * 1.08, hw_w * 1.08), (jy + th, hw_w * 1.12, hw_w * 1.12)]
    tp, tm = garment(Lu, lathe(cx, rows), top_col, seed + 30, shade=0.42, shade_dir=shade_dir, stain=0.5, worn=0.12, flick=0.7, fdir=84, streak=0.4, ink_w=2.4, hem_dirt=0.18, smooth=1, edge_dk=0.22, rough=1.0,
                     folds=[[(cx - hw_w * 0.3, jy + th * 0.4), (cx - hw_w * 0.4, jy + th * 0.75), (cx - hw_w * 0.35, jy + th * 0.95)], [(cx + hw_w * 0.35, jy + th * 0.35), (cx + hw_w * 0.4, jy + th * 0.7), (cx + hw_w * 0.5, jy + th * 0.95)]])
    if deco_top:
        deco_top(Lu, tm, bbox_of(Lu, tp), jy, th)
    neck(Lu, cx + dx_head * 0.5, cy + b - 10, jy + 4, a * 0.46, seed + 40, skin=skin)
    collar(Lu, cx, jy - 2, a * 0.64, a * 0.5, K['white'], seed + 41)
    if belt:
        by_ = jy + th * belt.get('t', 0.62)
        if belt.get('kind') == 'rope':
            brush(Lu, [(cx - hw_w, by_ - 1), (cx, by_ + 3), (cx + hw_w, by_ - 1)], w0=5, color=K['rope'], op=0.95, seed=seed + 50, taper=0.15, wob=0.6)
            for k in range(8):
                x = cx - hw_w * 0.8 + k * hw_w * 0.23
                line(Lu, [(x, by_ - 3), (x + 4, by_ + 4)], 1.1, K['rope_dk'], 0.7, seed + 51 + k, 0.3, 0, 0.1, smooth=False)
            brush(Lu, [(cx + 12, by_ + 3), (cx + 18, by_ + 18), (cx + 14, by_ + 30)], w0=3.0, color=K['rope'], op=0.9, seed=seed + 60, taper=0.3, wob=0.6)
        else:
            c_ = belt.get('col', K['gb_dk'])
            garment(Lu, [(cx - hw_w, by_ - 6), (cx + hw_w, by_ - 6), (cx + hw_w + 2, by_ + 8), (cx - hw_w - 2, by_ + 8)], c_, seed + 50, shade=0.3, stain=0.35, flick=0.3, fdir=0, ink_w=1.9, smooth=1, rough=0.6)
    for (px, py, pw, ph, pc, pa) in patches:
        patch(Lu, cx + px * H, jy + py * H, pw * H, ph * H, pc, seed + 70 + int(px * 100), ang=pa, clipmask=tm)
    # ── 手臂
    arms = arms or {}
    sw = (H * 0.07 if kind != 'kid' else H * 0.075) * bw if sleeve_w is None else sleeve_w
    wrists = {}
    for i, s_ in enumerate((-1, 1)):
        key = 'L' if s_ == -1 else 'R'
        sh = (cx + s_ * (hw_s - sw * 0.35), jy + H * 0.03)
        if key in arms:
            e_dx, e_dy, w_dx, w_dy = arms[key][:4]
        else:
            e_dx, e_dy, w_dx, w_dy = s_ * H * 0.035, H * 0.105, s_ * H * 0.045, H * 0.21
        el = (sh[0] + e_dx, sh[1] + e_dy)
        wr = (sh[0] + w_dx, sh[1] + w_dy)
        wrists[key] = wr
        path = [sh, el, wr]
        ap = tube(path, sw, sw * 0.85, cap0=0.9, cap1=0.0)
        shadow_on(Lu, tm, ap, -s_ * 4, 3, op=0.4)
        sleeve(Lu, path, sw, sw * 0.85, top_col, seed + 80 + i, cuff=(sw * 0.4 if cuff else 0), shade=0.42, stain=0.5, worn=0.1, flick=0.6, fdir=80, streak=0.3, shade_dir=shade_dir, edge_dk=0.2, rough=0.9, ink_w=2.3,
               folds=[[(el[0] - s_ * sw * 0.25, el[1] - sw * 0.35), (el[0] + s_ * sw * 0.0, el[1] + 2), (el[0] - s_ * sw * 0.25, el[1] + sw * 0.4)]])
    # ── 头
    face = dict(face or {})
    face.setdefault('mood', 'smile')
    hx = cx + dx_head
    (face_fn or face_front)(Lu, hx, cy, a, b, seed + 100, skin=skin, **face)
    if beard:
        beard(Lu, hx, cy, a, b, seed + 110)
    if hair:
        hair(Lu, hx, cy, a, b, seed + 120)
    if hat:
        hat(Lu, hx, cy, a, b, seed + 130)
    # ── 手（盖在袖子上）
    for i, s_ in enumerate((-1, 1)):
        key = 'L' if s_ == -1 else 'R'
        wr = wrists[key]
        arm = arms.get(key)
        ang = math.pi / 2 + s_ * 0.1
        if arm and len(arm) >= 5:
            ang = arm[4]
        hand(Lu, wr[0], wr[1] + 1, ang, H * 0.06 if kind != 'kid' else H * 0.05, skin=hand_skin, seed=seed + 140 + i, kind=hand_kind[i], side=-s_)
    if extra_front:
        extra_front(Lu, cx, T, jy, wrists)
    if lean:
        paste_layer(L, Lu, (cx, hip_y), lean[0], lean[1] if len(lean) > 1 else 0, lean[2] if len(lean) > 2 else 0)
    return L, (cx, foot)


# ───────────────────────── 围观的人 ─────────────────────────
def staff(L, x, y_bot, y_top, seed=0, w=7):
    p = tube([(x, y_bot), (x + 3, (y_bot + y_top) / 2), (x + 1, y_top)], w, w * 0.8, cap=0.5)
    garment(L, p, K['wood'], seed, shade=0.45, stain=0.4, flick=1.0, fdir=90, ink_w=1.8, smooth=1, rough=0.6, wob=0.6, edge_dk=0.2)


@sprite
def villager1():
    """男子，包头布，惊讶地仰着头，一手托腮。"""
    def beard_fn(L, cx, cy, a, b, seed):
        # 下巴上的一圈胡茬
        pts = [(cx - a * 0.7, cy + b * 0.55), (cx - a * 0.5, cy + b * 0.95), (cx, cy + b * 1.1), (cx + a * 0.5, cy + b * 0.95), (cx + a * 0.7, cy + b * 0.55), (cx + a * 0.4, cy + b * 0.7), (cx, cy + b * 0.74), (cx - a * 0.4, cy + b * 0.7)]
        beard(L, pts, hexc('#6a6358'), seed, strands=26, direction=90)
        mustache_front(L, cx, cy, a, b, seed + 5, col=hexc('#4a443c'), w=0.1, drop=0.5)
    L, anc = human_front(cx=300, foot=700, H=500, kind='adult', seed=1200, top_col=hexc('#5d6a82'), bot_col=hexc('#6b6054'), skin=hexc('#d9ad88'),
                         bot='trousers', top_len=0.29, face=dict(mood='open', brow='soft', eye_y=0.02, blush=0.25, age=0.2, eye_r=0.09),
                         hair=lambda L, cx, cy, a, b, s: head_cloth(L, cx, cy, a, b, s, hexc('#7d8a9b'), 1), beard=lambda L, cx, cy, a, b, s: beard_fn(L, cx, cy, a, b, s),
                         belt=dict(kind='rope', t=0.7), patches=[(-0.05, 0.2, 0.06, 0.05, K['linen'], 0.1)],
                         arms={'L': (-0.04 * 500, 0.1 * 500, -0.02 * 500, 0.21 * 500), 'R': (12, 45, -30, -12, -2.2)}, hand_kind=('open', 'fist'))
    sheet_save(L, 'villager1', anc, 81)


@sprite
def villager2():
    """妇人，灰褐的衫、深色长裙，挽髻，捂着嘴惊讶。"""
    L, anc = human_front(cx=300, foot=700, H=500, kind='adult', seed=1300, top_col=hexc('#7a6c5e'), bot_col=hexc('#4f5566'), skin=hexc('#e0b794'),
                         bot='skirt', top_len=0.27, face=dict(mood='open', brow='soft', eye_y=0.05, blush=0.4, eye_r=0.09),
                         hair=lambda L, cx, cy, a, b, s: hair_bun_woman(L, cx, cy, a, b, s),
                         belt=dict(kind='cloth', t=0.95, col=hexc('#aeb2b8')), patches=[(0.06, 0.15, 0.05, 0.045, K['gb_lt'], -0.1)],
                         arms={'L': (-0.045 * 500, 0.1 * 500, -0.01 * 500, 0.2 * 500), 'R': (14, 44, -16, 4, -2.4)}, hand_kind=('open', 'fist'), skirt_len=0.05)
    sheet_save(L, 'villager2', anc, 82)


@sprite
def villager3():
    """驼背老人，白须，拄杖，仰头看。≈380。"""
    def beard_fn(L, cx, cy, a, b, seed):
        beard_front(L, cx, cy, a, b, hexc('#e2e0da'), seed, length=1.5, w=0.8, strands=36)
    stk = {}

    def front(L, cx, T, jy, wr):
        x, y = wr['R']
        staff(L, x + 2, 700 - 4, jy - 20, 1405, 8)
        hand(L, x, y + 1, math.pi / 2, 26, skin=hexc('#d6a987'), seed=1406, kind='fist', side=-1)
    L, anc = human_front(cx=300, foot=700, H=380, kind='old', seed=1400, top_col=hexc('#7c7060'), bot_col=hexc('#52504c'), skin=hexc('#d6a987'),
                         bot='trousers', top_style='robe', top_len=0.5, face=dict(mood='calm', brow='soft', eye_y=0.04, blush=0.2, age=0.8, eye_r=0.09),
                         hair=lambda L, cx, cy, a, b, s: hair_old_white(L, cx, cy, a, b, s), beard=lambda L, cx, cy, a, b, s: beard_fn(L, cx, cy, a, b, s),
                         belt=dict(kind='rope', t=0.5), patches=[(-0.07, 0.3, 0.07, 0.06, K['linen'], 0.1)],
                         arms={'L': (-0.04 * 380, 0.1 * 380, -0.02 * 380, 0.2 * 380), 'R': (0.06 * 380, 0.1 * 380, 0.085 * 380, 0.19 * 380)}, extra_front=front)
    sheet_save(L, 'villager3', anc, 83)


@sprite
def villager4():
    """小男孩，束发，仰头指着天。≈380。"""
    L, anc = human_front(cx=300, foot=700, H=380, kind='kid', seed=1500, top_col=hexc('#6b8191'), bot_col=hexc('#5a5148'), skin=hexc('#e2b48f'),
                         bot='trousers', top_len=0.3, face=dict(mood='open', brow='soft', eye_y=0.12, blush=0.5, eye_r=0.105),
                         hair=lambda L, cx, cy, a, b, s: hair_topknot(L, cx, cy, a, b, s),
                         belt=dict(kind='rope', t=0.8), patches=[(0.06, 0.12, 0.06, 0.05, K['linen'], 0.1)],
                         arms={'L': (-0.04 * 380, 0.1 * 380, -0.02 * 380, 0.2 * 380), 'R': (0.07 * 380, -0.05 * 380, 0.1 * 380, -0.2 * 380, -math.pi / 2 + 0.2)}, hand_kind=('open', 'point'))
    sheet_save(L, 'villager4', anc, 84)


# ───────────────────────── 孩子们 ─────────────────────────
def flowers(L, mask, bb, cols, seed=0, n=60, r=(5, 8), hole=None):
    """在 mask 里撒小花（五瓣）：灰粉、淡灰蓝。"""
    rr = np.random.default_rng(seed)
    y0, y1, x0, x1 = bb
    for _ in range(n):
        x, y = rr.uniform(x0, x1), rr.uniform(y0, y1)
        if mask[int(min(max(y, 0), L.h - 1)), int(min(max(x, 0), L.w - 1))] < 0.95:
            continue
        rad = rr.uniform(*r)
        col = cols[int(rr.integers(len(cols)))]
        ph = rr.uniform(0, 6.28)
        for k in range(5):
            ang = ph + k * 2 * math.pi / 5
            wash(L, ellipse_pts(x + math.cos(ang) * rad * 0.55, y + math.sin(ang) * rad * 0.55, rad * 0.5, rad * 0.34, 8, rot=ang), col, op=0.92, wob=0.2, seed=int(rr.integers(1e6)), smooth=1, tex_k=0.05, rim=0.25, rim_w=1.5)
        dots(L, [(x, y, rad * 0.22)], hexc('#cdbf92'), op=0.95, soft=0.4)
        for k in range(2):
            line(L, [(x, y + rad * 0.5), (x + rr.normal(0, 3), y + rad * 1.6)], 0.9, K['pine_dk'] if False else hexc('#6f7a6a'), 0.4, int(rr.integers(1e6)), 0.4, 0, 0.2)


@sprite
def kid1():
    """男孩，笑着在跑：上身前倾，一腿抬起，一手握拳摆在胸前。"""
    bot_col = hexc('#5f574d')
    skin = hexc('#e2b48f')

    def run_legs(L, cx, foot, hip_y, ankle):
        # 后腿（蹬地）：短裤 + 光小腿
        for pts, col_s, shoe_xy, lift in [([(cx - 16, hip_y), (cx - 34, hip_y + 46), (cx - 46, foot - 16)], 0, (cx - 48, foot), 0),
                                         ([(cx + 16, hip_y), (cx + 40, hip_y + 40), (cx + 36, foot - 54)], 1, (cx + 38, foot - 44), 1)]:
            hip, knee, ank = pts
            leg(L, [knee, ank], 20, 15, skin, 1600 + col_s, shade=0.35, stain=0.15, flick=0.0, ink_w=1.8, rough=0.5, speck=0.0, tex_k=0.07)
            leg(L, [(ank[0], ank[1] - 18), ank], 20, 19, K['linen_lt'], 1602 + col_s, shade=0.2, stain=0.3, flick=0.2, ink_w=1.4)
            shoe_front(L, shoe_xy[0], shoe_xy[1], 38, 18, K['dark'], 1610 + col_s)
            leg(L, [hip, ((hip[0] + knee[0]) / 2, (hip[1] + knee[1]) / 2 + 4), (knee[0], knee[1] + 6)], 40, 32, bot_col, 1620 + col_s, shade=0.4, stain=0.5, flick=0.6, fdir=80, ink_w=2.1, rough=1.0, edge_dk=0.2)
    L, anc = human_front(cx=210, foot=400, H=350, kind='kid', seed=1600, canvas=(420, 440), top_col=hexc('#6d8594'), bot_col=bot_col, skin=skin,
                         legs_fn=run_legs, top_len=0.3, face=dict(mood='grin', brow='plain', eye_y=0.14, blush=0.6, eye_r=0.11),
                         hair=lambda L, cx, cy, a, b, s: hair_messy(L, cx, cy, a, b, s, tuft=10, fringe=0.4),
                         belt=dict(kind='rope', t=0.8), patches=[(-0.08, 0.15, 0.06, 0.05, K['linen'], 0.1)],
                         arms={'L': (-0.085 * 350, 0.085 * 350, -0.125 * 350, 0.16 * 350, math.pi / 2 - 0.5), 'R': (31, 40, 20, -2, -math.pi / 2 + 0.3)}, hand_kind=('open', 'fist'), lean=(9, 0, 0))
    sheet_save(L, 'kid1', anc, 91)


@sprite
def kid2():
    """男孩蹲着，低头看地上的蚂蚁，双手扶膝。"""
    bot_col = hexc('#4e4a48')

    def squat_legs(L, cx, foot, hip_y, ankle):
        # 两膝之间的裤裆（大腿朝着镜头，只看到一团）
        garment(L, [(cx - 66, hip_y - 20), (cx - 28, hip_y - 10), (cx + 28, hip_y - 10), (cx + 66, hip_y - 20), (cx + 56, foot - 36), (cx, foot - 26), (cx - 56, foot - 36)], bot_col, 1700, shade=0.4, stain=0.5, flick=0.6, fdir=80, ink_w=2.2, smooth=1, rough=1.0, edge_dk=0.2)
        for s_ in (-1, 1):
            leg(L, [(cx + s_ * 62, hip_y - 14), (cx + s_ * 60, hip_y + 34), (cx + s_ * 56, foot - 16)], 40, 28, bot_col, 1701 + s_, shade=0.4, stain=0.5, flick=0.6, fdir=88, ink_w=2.1, rough=1.0, edge_dk=0.2,
                folds=[[(cx + s_ * 56, hip_y - 4), (cx + s_ * 58, hip_y + 20)]])
            leg(L, [(cx + s_ * 56, foot - 38), (cx + s_ * 56, foot - 14)], 29, 28, K['linen_lt'], 1703 + s_, shade=0.2, stain=0.3, flick=0.2, ink_w=1.4)
            shoe_front(L, cx + s_ * 58, foot, 42, 20, K['dark'], 1705 + s_)
    L, anc = human_front(cx=210, foot=400, H=250, kind='kid', seed=1700, canvas=(420, 440), a=36, b=46, bw=1.4, top_col=hexc('#7a6c5e'), bot_col=bot_col, skin=hexc('#dcae88'),
                         legs_fn=squat_legs, top_len=0.28, face=dict(mood='calm', brow='soft', eye_y=0.3, blush=0.45, eye_r=0.1, look=(0, 2.2)),
                         hair=lambda L, cx, cy, a, b, s: hair_messy(L, cx, cy, a, b, s, tuft=4, fringe=0.14),
                         belt=dict(kind='rope', t=0.85), patches=[(0.1, 0.1, 0.07, 0.06, K['linen'], 0.1)],
                         arms={'L': (-0.15 * 250, 0.07 * 250, -0.11 * 250, 0.15 * 250, math.pi / 2 - 0.3), 'R': (0.15 * 250, 0.07 * 250, 0.11 * 250, 0.15 * 250, math.pi / 2 + 0.3)}, hand_kind=('open', 'open'), lean=(0, 0, 0))
    sheet_save(L, 'kid2', anc, 92)


@sprite
def kid3():
    """小女孩，一手举到额前遮着光、仰头看。"""
    L, anc = human_front(cx=210, foot=400, H=345, kind='kid', seed=1800, canvas=(420, 440), top_col=hexc('#6f7f78'), bot_col=hexc('#4f4f56'), skin=hexc('#e4b892'),
                         top_len=0.31, face=dict(mood='open', brow='soft', eye_y=0.1, blush=0.5, eye_r=0.11),
                         hair=lambda L, cx, cy, a, b, s: hair_braids(L, cx, cy, a, b, s),
                         belt=dict(kind='cloth', t=0.82, col=hexc('#a7a89f')), patches=[(0.07, 0.17, 0.06, 0.05, K['gb_lt'], 0.1)],
                         arms={'L': (-0.045 * 345, 0.1 * 345, -0.02 * 345, 0.2 * 345), 'R': (30, -28, -8, -75, math.pi + 0.15)}, hand_kind=('open', 'open'), shoe_col=hexc('#3a3a3c'))
    sheet_save(L, 'kid3', anc, 93)


@sprite
def girl_flower():
    """跳舞的女孩：花裙子（淡灰蓝带灰粉的小花）张开，双臂展开。≈350。"""
    base = hexc('#8aa0b0')
    rose = [hexc('#cfa9a4'), hexc('#d8b8b0'), hexc('#c4a2a6')]
    cream = hexc('#e6e0d0')

    def deco(L, mask, bb, wy, hy):
        flowers(L, mask, bb, rose + [cream], 1901, n=70, r=(5, 8))
    L, anc = human_front(cx=210, foot=400, H=350, kind='kid', seed=1900, canvas=(460, 440), top_col=hexc('#b9bec2'), bot_col=base, skin=hexc('#e4b892'),
                         bot='skirt', skirt_len=0.08, skirt_hw=0.27 * 350, top_len=0.24, face=dict(mood='grin', brow='soft', eye_y=0.14, blush=0.6, eye_r=0.11),
                         hair=lambda L, cx, cy, a, b, s: hair_buns_flower(L, cx, cy, a, b, s, rose),
                         belt=dict(kind='cloth', t=0.92, col=hexc('#8d9aa4')), deco_bot=deco,
                         arms={'L': (-0.12 * 350, -0.02 * 350, -0.2 * 350, -0.1 * 350, math.pi + 0.5), 'R': (0.12 * 350, -0.02 * 350, 0.2 * 350, -0.1 * 350, -0.5)}, hand_kind=('open', 'open'),
                         lean=(-5, 0, 0), dx_head=0)
    sheet_save(L, 'girl_flower', anc, 94)


def hair_buns_flower(L, cx, cy, a, b, seed, rose):
    for s_ in (-1, 1):
        bun = ellipse_pts(cx + s_ * a * 0.86, cy - b * 0.98, 15, 14, 14, jit=0.05, seed=seed + s_)
        hair_mass(L, bun, None, seed + 10 + s_, strands=8, direction=90)
        # 发髻上的小花
        for k in range(5):
            ang = k * 2 * math.pi / 5
            wash(L, ellipse_pts(cx + s_ * a * 0.86 + math.cos(ang) * 6, cy - b * 0.98 - 12 + math.sin(ang) * 6, 5, 3.4, 8, rot=ang), rose[0], op=0.95, wob=0.2, seed=seed + 20 + k, smooth=1, tex_k=0.05, rim=0.2)
        dots(L, [(cx + s_ * a * 0.86, cy - b * 0.98 - 12, 2.4)], hexc('#cdbf92'), op=0.95)
    hair_cap_front(L, cx, cy, a, b, seed, fringe=0.3, side=0.3, puff=1.06, tuft=2)
