"""设定图里没有、但剧情里要出现的“东西”和配角，用同一套画笔画成带透明通道的小精灵：
雪人（和棒球帽）、Mrs Mallet、背光的爸爸、梯子、电池、灯泡和纸盒、落叶堆。
输出到 public/props/，同时写 props.json（尺寸 + 脚底/底边锚点）。
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from objects import *  # noqa
from world import *  # noqa
import cv2

OUT = pathlib.Path(__file__).resolve().parents[2] / 'public/props'
OUT.mkdir(parents=True, exist_ok=True)
META = {}


def finish(L, name, anchor='bottom'):
    a = L.a
    ys, xs = np.where(a > 0.02)
    y0, y1, x0, x1 = max(ys.min() - 3, 0), min(ys.max() + 4, L.h), max(xs.min() - 3, 0), min(xs.max() + 4, L.w)
    sub = Canvas(x1 - x0, y1 - y0)
    sub.rgb = L.rgb[y0:y1, x0:x1].copy(); sub.a = L.a[y0:y1, x0:x1].copy()
    sub.save(OUT / f'{name}.png')
    META[name] = {'w': int(x1 - x0), 'h': int(y1 - y0), 'ax': float((x1 - x0) / 2), 'ay': float(y1 - y0 - 2)}
    return sub


def ball(L, cx, cy, r, seed, shade=True):
    n = 18
    pts = np.array([[cx + math.cos(a) * r * (1 + 0.025 * math.sin(a * 3 + seed)), cy + math.sin(a) * r * (1 + 0.02 * math.cos(a * 2 + seed))] for a in np.linspace(0, 2 * math.pi, n, endpoint=False)], F)
    wash(L, pts, P['snow_lit'], op=1.0, wob=1.2, seed=seed, smooth=2, tex_k=0.07, rim=0.12, rim_w=3)
    if shade:
        sh = np.array([[cx + math.cos(a) * r * 0.98, cy + math.sin(a) * r * 0.98] for a in np.linspace(-0.2, 2.2, 14)] + [[cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.62 + r * 0.15] for a in np.linspace(2.2, -0.2, 8)], F)
        wash(L, sh, P['snow_sh2'], op=0.5, wob=1.5, seed=seed + 1, smooth=2, tex_k=0.16)
        wash(L, sh * 0.9 + np.array([cx, cy]) * 0.1, P['snow_sh1'], op=0.35, wob=1.5, seed=seed + 2, smooth=2)
        hatch(L, sh, 62, 8, 16, P['snow_sh3'], op=0.25, w=1.0, seed=seed + 3, jitter=0.3)
    ink(L, np.vstack([pts, pts[:1]]), w0=1.4, color=hexc('#6f84ad'), op=0.55, seed=seed + 4, wob=1.0, taper=0.1)


def stick(L, x0, y0, x1, y1, seed, w=5):
    ink(L, [(x0, y0), ((x0 + x1) / 2 + 4, (y0 + y1) / 2 - 3), (x1, y1)], w0=w, w1=w * 0.5, color=hexc('#5b524e'), op=0.95, seed=seed, wob=0.8, taper=0.1)


def snowman():
    L = Canvas(380, 620)
    ball(L, 190, 470, 118, 1)
    ball(L, 190, 318, 84, 2)
    ball(L, 190, 205, 60, 3)
    # 眼睛（黑石子）、鼻子（胡萝卜：颜色画得淡淡的，不用橙色）、嘴
    for ex in (168, 212):
        dots(L, [(ex, 195, 6)], hexc('#262b3a'), 1.0, soft=1.0)
    nose = np.array([[184, 208], [236, 220], [186, 224]], F)
    wash(L, nose, hexc('#e1c8b4'), op=1.0, wob=0.5, seed=7, smooth=0, tex_k=0.1)
    ink(L, np.vstack([nose, nose[:1]]), w0=1.2, color=hexc('#6a5c57'), op=0.8, seed=8, wob=0.3, taper=0.1, smooth=False)
    for k, ang in enumerate(np.linspace(0.3, math.pi - 0.3, 6)):
        dots(L, [(190 + math.cos(ang) * 30, 222 + math.sin(ang) * 14, 3.0)], hexc('#262b3a'), 0.95, soft=0.8)
    for by in (300, 335, 370):
        dots(L, [(190, by, 5.5)], hexc('#262b3a'), 0.95, soft=1.0)
    # 树枝做的手臂
    stick(L, 118, 304, 40, 236, 11); stick(L, 70, 262, 52, 232, 12, 3.5); stick(L, 78, 268, 34, 262, 13, 3.5)
    stick(L, 262, 308, 346, 246, 14); stick(L, 316, 262, 336, 236, 15, 3.5); stick(L, 322, 268, 360, 262, 16, 3.5)
    snowman_body = finish(L, 'snowman')
    # 棒球帽：单独一层（Bud 把帽子给了雪人）
    C = Canvas(380, 620)
    navy, dk = hexc('#2f4172'), hexc('#1f2c52')
    dome = [(138, 168), (136, 148), (146, 126), (166, 112), (190, 108), (214, 112), (236, 126), (244, 148), (242, 168), (214, 162), (188, 160), (160, 162)]
    wash(C, dome, navy, op=1.0, wob=0.8, seed=21, smooth=2, tex_k=0.2, rim=0.2, rim_w=2.0)
    wash(C, [(190, 110), (214, 114), (236, 128), (242, 148), (222, 134), (200, 126)], hexc('#4b5f95'), op=0.45, wob=0.6, seed=22, smooth=2)
    for k, x in enumerate((160, 190, 216)):
        ink(C, [(190, 108), (190 + (x - 190) * 0.6, 134), (x, 164)], w0=1.0, color=dk, op=0.55, seed=23 + k, wob=0.3)
    dots(C, [(190, 108, 4.2)], hexc('#4b5f95'), 1.0)
    brim = [(134, 158), (190, 166), (246, 158), (254, 166), (238, 174), (190, 178), (140, 174), (128, 166)]
    wash(C, brim, dk, op=1.0, wob=0.7, seed=24, smooth=2, tex_k=0.2, rim=0.2, rim_w=2.0)
    ink(C, np.vstack([brim, brim[:1]]), w0=1.3, color=hexc('#141b36'), op=0.8, seed=25, wob=0.5, taper=0.1, smooth=False)
    # 帽子层和雪人同一块画布裁法：用雪人的外框偏移，保证叠上去位置对
    ys, xs = np.where(L.a > 0.02)
    y0, x0 = max(ys.min() - 3, 0), max(xs.min() - 3, 0)
    sub = Canvas(snowman_body.w, snowman_body.h)
    sub.rgb = C.rgb[y0:y0 + snowman_body.h, x0:x0 + snowman_body.w].copy(); sub.a = C.a[y0:y0 + snowman_body.h, x0:x0 + snowman_body.w].copy()
    sub.save(OUT / 'snowman_cap.png')
    META['snowman_cap'] = dict(META['snowman'])


def soft(L, pts, w=1.4, op=0.65, seed=0, n=2):
    p = chaikin(np.asarray(pts, F), n, True)
    ink(L, np.vstack([p, p[:1]]), w0=w, color=INK, op=op, seed=seed, wob=0.6, taper=0.1, smooth=False)


def sw(L, pts, col, seed, n=2, **kw):
    p = chaikin(np.asarray(pts, F), n, True)
    wash(L, p, col, op=1.0, wob=kw.pop('wob', 1.0), seed=seed, smooth=0, tex_k=kw.pop('tex_k', 0.14), rim=kw.pop('rim', 0.16), **kw)
    return p


def mallet():
    L = Canvas(340, 560)
    # 鞋、裙子、围裙、开襟毛衣、手臂、头、白发（轮廓全部圆角化，不要棱角）
    for sx in (140, 190):
        sw(L, [[sx - 22, 522], [sx + 24, 522], [sx + 30, 540], [sx - 28, 540]], hexc('#2b3350'), sx, wob=0.8)
    skirt = [[112, 330], [218, 330], [236, 516], [94, 516]]
    p = sw(L, skirt, hexc('#5d6f93'), 31, wob=1.2)
    hatch(L, p, 80, 9, 40, hexc('#2b3556'), op=0.25, w=1.0, seed=32)
    soft(L, skirt, 1.5, 0.7, 33)
    apron = [[128, 300], [202, 300], [212, 330], [220, 498], [110, 498], [118, 330]]
    sw(L, apron, hexc('#eef1f6'), 34, tex_k=0.1, rim=0.14)
    for px in (134, 176):
        pk = rect(px, 400, px + 32, 434)
        sw(L, pk, hexc('#dbe2ee'), px, n=1, wob=0.5, tex_k=0.1)
        soft(L, pk, 1.1, 0.6, px, 1)
    body = [[110, 216], [220, 216], [230, 336], [100, 336]]
    sw(L, body, hexc('#7d8cab'), 37, wob=1.2)
    sw(L, [[134, 228], [196, 228], [202, 304], [128, 304]], hexc('#eef1f6'), 38, wob=0.8, tex_k=0.08, rim=0.1)
    soft(L, body, 1.5, 0.7, 39)
    # 手臂：向前托着东西
    for sgn, (sx, sy, ex, ey) in enumerate([(108, 234, 76, 326), (222, 234, 256, 316)]):
        arm = [[sx - 14, sy], [sx + 14, sy], [ex + 11, ey], [ex - 11, ey]]
        sw(L, arm, hexc('#7d8cab'), 40 + sgn)
        soft(L, arm, 1.2, 0.6, 42 + sgn)
        dots(L, [(ex, ey + 10, 11)], hexc('#efdccf'), 1.0, soft=1.2)
    # 头
    wash(L, np.array([[165 + math.cos(a) * 42, 162 + math.sin(a) * 48] for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)], F), hexc('#f0ddd0'), op=1.0, wob=0.8, seed=45, smooth=2, tex_k=0.1, rim=0.12)
    for ex in (150, 182):
        dots(L, [(ex, 160, 3.0)], hexc('#2c3140'), 1.0, soft=0.8)
        ink(L, [(ex - 12, 158), (ex, 152), (ex + 12, 158), (ex, 168), (ex - 12, 158)], w0=1.3, color=INK, op=0.85, seed=46 + int(ex), wob=0.2, taper=0.1)
    ink(L, [(163, 162), (166, 176), (172, 178)], w0=1.2, color=hexc('#a77a68'), op=0.8, seed=47, wob=0.3)
    ink(L, [(150, 190), (166, 197), (182, 189)], w0=1.4, color=hexc('#b06a64'), op=0.85, seed=48, wob=0.3)
    dots(L, [(140, 180, 8), (192, 180, 8)], hexc('#ecb5ad'), 0.45, soft=3)
    # 白发 + 发髻
    hair = np.array([[120, 150], [124, 120], [142, 104], [166, 98], [190, 106], [206, 124], [210, 152], [196, 132], [168, 122], [140, 130]], F)
    wash(L, hair, hexc('#f1f3f8'), op=1.0, wob=1.0, seed=50, smooth=2, tex_k=0.1, rim=0.16)
    wash(L, np.array([[165 + math.cos(a) * 24, 96 + math.sin(a) * 22] for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)], F), hexc('#e6e9f1'), op=1.0, wob=0.8, seed=51, smooth=2, tex_k=0.1, rim=0.16)
    for i in range(14):
        a = -math.pi * (0.1 + 0.8 * i / 13)
        ink(L, [(165 + math.cos(a) * 12, 120 + math.sin(a) * 8), (165 + math.cos(a) * 40, 120 + math.sin(a) * 30), (165 + math.cos(a) * 46, 128 + math.sin(a) * 28)], w0=0.9, color=hexc('#9aa6bd'), op=0.6, seed=52 + i, wob=0.3)
    ink(L, np.vstack([hair, hair[:1]]), w0=1.2, color=hexc('#6c7794'), op=0.6, seed=53, wob=0.5, taper=0.1)
    finish(L, 'mallet')


def dad():
    """背光的爸爸：深靛蓝的剪影，被灯塔的光勾出一圈暖色的边。"""
    L = Canvas(300, 620)
    sil = hexc('#151b38')
    legs = np.array([[118, 330], [186, 330], [192, 560], [160, 566], [152, 420], [140, 566], [108, 560], [112, 420]], F)
    wash(L, legs, sil, op=1.0, wob=1.0, seed=61, smooth=1, tex_k=0.1)
    coat = np.array([[96, 160], [210, 160], [232, 330], [226, 440], [82, 440], [76, 330]], F)
    wash(L, coat, sil, op=1.0, wob=1.2, seed=62, smooth=1, tex_k=0.12)
    # 手臂：张开向前，要把孩子抱起来
    for sgn, (sx, sy, ex, ey) in enumerate([(98, 176, 20, 300), (208, 176, 286, 296)]):
        arm = np.array([[sx - 20, sy], [sx + 20, sy], [ex + 14, ey], [ex - 14, ey]], F)
        wash(L, arm, sil, op=1.0, wob=1.0, seed=63 + sgn, smooth=1, tex_k=0.1)
    wash(L, np.array([[153 + math.cos(a) * 34, 118 + math.sin(a) * 40] for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)], F), sil, op=1.0, wob=0.8, seed=65, smooth=2, tex_k=0.1)
    cap = np.array([[112, 104], [118, 76], [152, 62], [190, 78], [196, 104], [220, 112], [114, 114]], F)
    wash(L, cap, sil, op=1.0, wob=0.8, seed=66, smooth=2, tex_k=0.1)
    # 暖色的轮廓光（光从右边来）
    rim = hexc('#ffd978')
    ink(L, [(196, 100), (190, 76), (170, 64)], w0=2.0, color=rim, op=0.8, seed=67, wob=0.3)
    ink(L, [(184, 120), (190, 150), (210, 176), (230, 330), (226, 440)], w0=2.2, color=rim, op=0.7, seed=68, wob=0.4)
    ink(L, [(230, 190), (286, 290)], w0=2.0, color=rim, op=0.65, seed=69, wob=0.3)
    ink(L, [(188, 340), (192, 560)], w0=1.8, color=rim, op=0.5, seed=70, wob=0.3)
    finish(L, 'dad')


def ladder():
    L = Canvas(560, 120)
    wood = hexc('#76727a')
    for y, seed in ((24, 1), (86, 2)):
        wash(L, np.array([[10, y - 7], [550, y - 9], [550, y + 7], [10, y + 8]], F), wood, op=1.0, wob=0.8, seed=seed, smooth=1, tex_k=0.2)
        ink(L, [(10, y), (280, y - 1), (550, y)], w0=1.2, color=hexc('#3b3a44'), op=0.55, seed=seed + 5, wob=0.5)
    for i in range(9):
        x = 40 + i * 58
        wash(L, np.array([[x - 5, 24], [x + 5, 24], [x + 7, 86], [x - 5, 86]], F), rgbmix(wood, hexc('#8a8590'), 0.3), op=1.0, wob=0.5, seed=10 + i, smooth=0, tex_k=0.2)
        ink(L, [(x, 24), (x + 1, 86)], w0=1.0, color=hexc('#3b3a44'), op=0.5, seed=20 + i, wob=0.3)
    finish(L, 'ladder')


def battery():
    L = Canvas(120, 200)
    body = np.array([[22, 40], [98, 40], [98, 172], [22, 172]], F)
    wash(L, body, hexc('#aab6c8'), op=1.0, wob=0.6, seed=71, smooth=1, tex_k=0.14, rim=0.2)
    wash(L, np.array([[22, 76], [98, 76], [98, 118], [22, 118]], F), hexc('#4a5f8f'), op=1.0, wob=0.5, seed=72, smooth=0, tex_k=0.1)
    wash(L, np.array([[44, 22], [76, 22], [76, 40], [44, 40]], F), hexc('#8d98ad'), op=1.0, wob=0.4, seed=73, smooth=0)
    wash(L, np.array([[28, 44], [40, 44], [40, 168], [28, 168]], F), hexc('#e8eef8'), op=0.5, wob=0.3, seed=74, smooth=0)
    outline(L, body, 1.5, 0.8, 75)
    ink(L, [(46, 98), (74, 98)], w0=2.0, color=hexc('#e8eef8'), op=0.9, seed=76, wob=0.2)
    ink(L, [(60, 84), (60, 112)], w0=2.0, color=hexc('#e8eef8'), op=0.9, seed=77, wob=0.2)
    finish(L, 'battery')


def bulb_box():
    L = Canvas(420, 360)
    box = np.array([[30, 180], [390, 180], [380, 340], [40, 340]], F)
    wash(L, box, hexc('#9aa0b2'), op=1.0, wob=1.0, seed=81, smooth=0, tex_k=0.18, rim=0.18)
    wash(L, np.array([[30, 180], [390, 180], [380, 210], [40, 210]], F), hexc('#7e86a0'), op=0.8, wob=0.8, seed=82, smooth=0, tex_k=0.14)
    outline(L, box, 1.6, 0.75, 83)
    # 纸和棉花
    cot = np.array([[60, 190], [120, 150], [200, 140], [290, 146], [360, 176], [380, 196], [40, 196]], F)
    wash(L, cot, hexc('#f1f3f8'), op=1.0, wob=2.0, seed=84, smooth=2, tex_k=0.1, rim=0.12)
    # 大灯泡：像甜瓜一样大，像冰一样透明
    cx, cy, r = 210, 96, 84
    glass = np.array([[cx + math.cos(a) * r, cy + math.sin(a) * r * 1.05] for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)], F)
    wash(L, glass, hexc('#dfeaf8'), op=0.55, wob=0.8, seed=85, smooth=2, tex_k=0.06, rim=0.25, rim_w=4)
    wash(L, np.array([[cx - r * 0.7, cy - r * 0.2], [cx - r * 0.45, cy - r * 0.7], [cx - r * 0.2, cy - r * 0.75], [cx - r * 0.5, cy - r * 0.2]], F), hexc('#ffffff'), op=0.8, wob=0.6, seed=86, smooth=2)
    ink(L, np.vstack([glass, glass[:1]]), w0=1.6, color=hexc('#6f84ad'), op=0.8, seed=87, wob=0.8, taper=0.1)
    nk = np.array([[cx - 30, cy + r * 0.92], [cx + 30, cy + r * 0.92], [cx + 34, 190], [cx - 34, 190]], F)
    wash(L, nk, hexc('#8d98ad'), op=1.0, wob=0.5, seed=88, smooth=0, tex_k=0.14)
    for k in range(4):
        ink(L, [(cx - 32, 172 + k * 5), (cx + 32, 170 + k * 5)], w0=1.2, color=hexc('#4a556e'), op=0.7, seed=89 + k, wob=0.2)
    outline(L, nk, 1.4, 0.8, 94)
    ink(L, [(cx - 22, cy + 30), (cx - 10, cy - 4), (cx, cy + 20), (cx + 10, cy - 4), (cx + 22, cy + 30)], w0=1.1, color=hexc('#6f7a96'), op=0.6, seed=95, wob=0.3)
    finish(L, 'bulb_box')


def leaf_pile():
    L = Canvas(520, 200)
    r = np.random.default_rng(5)
    mound = np.array([[10, 190], [60, 120], [140, 70], [260, 52], [380, 76], [460, 124], [510, 190]], F)
    wash(L, mound, hexc('#59584f'), op=1.0, wob=3.0, seed=91, smooth=2, tex_k=0.2, rim=0.2)
    cols = ['#6b6a60', '#5c6558', '#7a776c', '#4e5249', '#837f73', '#686456']
    for i in range(190):
        t = r.random()
        x = 20 + r.random() * 480
        top = np.interp(x, mound[:, 0], mound[:, 1])
        y = top + 6 + r.random() * (188 - top - 10)
        ang = r.uniform(0, math.pi)
        a, b = r.uniform(12, 26), r.uniform(5, 10)
        pts = np.array([[x + math.cos(ang) * a * math.cos(u) - math.sin(ang) * b * math.sin(u), y + math.sin(ang) * a * math.cos(u) + math.cos(ang) * b * math.sin(u)] for u in np.linspace(0, 2 * math.pi, 8, endpoint=False)], F)
        wash(L, pts, hexc(cols[int(r.integers(0, len(cols)))]), op=0.95, wob=0.4, seed=int(r.integers(1e6)), smooth=1, tex_k=0.2, rim=0.2, rim_w=1.5)
    for i in range(8):
        cx = 60 + r.random() * 400
        cy = np.interp(cx, mound[:, 0], mound[:, 1]) + 4
        cap = np.array([[cx - 40, cy + 14], [cx - 18, cy - 10], [cx + 14, cy - 12], [cx + 42, cy + 12], [cx, cy + 20]], F)
        wash(L, cap, P['snow'], op=0.95, wob=2, seed=int(r.integers(1e6)), smooth=2, tex_k=0.08)
    finish(L, 'leaf_pile')


if __name__ == '__main__':
    snowman(); mallet(); dad(); ladder(); battery(); bulb_box(); leaf_pile()
    (OUT / 'props.json').write_text(json.dumps(META, indent=1))
    print(META)
    from PIL import Image
    names = list(META)
    ims = [Image.open(OUT / f'{n}.png') for n in names]
    W_ = sum(i.width for i in ims) + 20 * len(ims); H_ = max(i.height for i in ims) + 20
    sheet = Image.new('RGB', (W_, H_), (150, 175, 215)); x = 10
    for i in ims:
        sheet.paste(i, (x, H_ - i.height - 10), i); x += i.width + 20
    sheet.save('/tmp/claude-0/-home-user-math-research/747091a3-a05e-575b-b1ac-cb27e1adeb12/scratchpad/ref/props.png')
