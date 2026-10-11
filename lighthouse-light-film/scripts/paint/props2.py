"""第二批配角和道具：Grandad（摔伤坐在石阶上 / 圣诞早上坐在扶手椅里）、农场的大婶、门口的 Mum（剪影）、船。"""
import json
from props import *   # noqa (soft, sw, finish, META, OUT, ball ...)
import props as P_


def face(L, cx, cy, rx, ry, seed, smile=True, brow=True):
    wash(L, np.array([[cx + math.cos(a) * rx, cy + math.sin(a) * ry] for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)], F), hexc('#efdccf'), op=1.0, wob=0.8, seed=seed, smooth=2, tex_k=0.1, rim=0.12)
    for ex in (cx - rx * 0.36, cx + rx * 0.36):
        dots(L, [(ex, cy - ry * 0.08, 2.8)], hexc('#2c3140'), 1.0, soft=0.8)
        if brow:
            ink(L, [(ex - 8, cy - ry * 0.3), (ex, cy - ry * 0.36), (ex + 8, cy - ry * 0.3)], w0=1.4, color=hexc('#5b5870'), op=0.8, seed=seed + int(ex), wob=0.2)
    ink(L, [(cx - 2, cy), (cx + 1, cy + ry * 0.2), (cx + 6, cy + ry * 0.24)], w0=1.2, color=hexc('#a77a68'), op=0.8, seed=seed + 2, wob=0.3)
    if smile:
        ink(L, [(cx - rx * 0.32, cy + ry * 0.5), (cx, cy + ry * 0.62), (cx + rx * 0.32, cy + ry * 0.5)], w0=1.4, color=hexc('#b06a64'), op=0.85, seed=seed + 3, wob=0.3)
    dots(L, [(cx - rx * 0.55, cy + ry * 0.3, 7), (cx + rx * 0.55, cy + ry * 0.3, 7)], hexc('#ecb5ad'), 0.4, soft=3)


def beard(L, cx, cy, rx, ry, seed, col='#f4f6fb'):
    pts = [(cx - rx, cy - ry * 0.1), (cx - rx * 0.95, cy + ry * 0.5), (cx - rx * 0.5, cy + ry * 1.1), (cx, cy + ry * 1.35), (cx + rx * 0.5, cy + ry * 1.1), (cx + rx * 0.95, cy + ry * 0.5), (cx + rx, cy - ry * 0.1), (cx + rx * 0.5, cy + ry * 0.2), (cx, cy + ry * 0.1), (cx - rx * 0.5, cy + ry * 0.2)]
    wash(L, np.array(pts, F), hexc(col), op=1.0, wob=1.0, seed=seed, smooth=2, tex_k=0.1, rim=0.16)
    for i in range(9):
        x = cx + (i - 4) * rx * 0.2
        ink(L, [(x, cy + ry * 0.3), (x + (i - 4) * 1.5, cy + ry * 0.9)], w0=0.9, color=hexc('#9aa6bd'), op=0.5, seed=seed + 10 + i, wob=0.3, taper=0.5)
    ink(L, np.vstack([np.array(pts, F), np.array(pts[:1], F)]), w0=1.1, color=hexc('#7d89a6'), op=0.55, seed=seed + 30, wob=0.5, taper=0.1)


def grandad_hurt():
    """坐在结冰的石阶上，一只手按着摔疼的脚踝，一条腿伸直；光头、大白胡子、深蓝大衣。"""
    L = Canvas(420, 360)
    coat, coat_dk = hexc('#3f4f7a'), hexc('#2e3b60')
    # 伸直的腿 + 靴子
    sw(L, [[170, 270], [330, 262], [350, 290], [180, 304]], hexc('#3a4770'), 1, wob=1.0)
    sw(L, [[320, 256], [372, 250], [384, 296], [332, 306]], hexc('#222a45'), 2, wob=0.8)
    # 身体（坐姿，微微前倾）
    body = [[110, 120], [210, 112], [250, 196], [236, 296], [90, 300], [70, 196]]
    sw(L, body, coat, 3, wob=1.2)
    hatch(L, chaikin(np.array(body, F), 2, True), 78, 9, 24, coat_dk, op=0.25, w=1.0, seed=4)
    soft(L, body, 1.5, 0.7, 5)
    # 围巾（冷色，淡蓝，不是红）
    sw(L, [[112, 118], [210, 112], [214, 140], [150, 154], [108, 144]], hexc('#a9bde6'), 6, wob=0.8)
    # 弯着的腿：膝盖朝前，手按在脚踝上
    sw(L, [[150, 270], [240, 250], [262, 306], [160, 312]], hexc('#3a4770'), 7, wob=1.0)
    ink(L, [(190, 300), (220, 262), (236, 232)], w0=18, color=coat, op=1.0, seed=8, wob=0.5)
    dots(L, [(240, 226, 14)], hexc('#efdccf'), 1.0, soft=1.2)
    # 头：光头 + 大白胡子，眉毛皱着一点，不吓人
    face(L, 160, 70, 40, 44, 20, smile=False)
    ink(L, [(134, 52), (150, 46), (164, 52)], w0=3.0, color=hexc('#f4f6fb'), op=1.0, seed=24, wob=0.3)
    ink(L, [(160, 52), (174, 46), (188, 52)], w0=3.0, color=hexc('#f4f6fb'), op=1.0, seed=25, wob=0.3)
    beard(L, 160, 84, 38, 24, 30)
    dots(L, [(120, 62, 8)], hexc('#efdccf'), 1.0, soft=1.0)   # 耳朵
    # 手杖倒在一边
    ink(L, [(300, 200), (390, 330)], w0=7, color=hexc('#5a4f4a'), op=1.0, seed=40, wob=0.8)
    ink(L, [(300, 200), (292, 184), (310, 176)], w0=7, color=hexc('#5a4f4a'), op=1.0, seed=41, wob=0.6)
    finish(L, 'grandad_hurt')


def grandad_chair():
    """圣诞早上：Grandad 坐在扶手椅里，腿上盖着小毯子，伤腿打着白石膏架在小凳上，旁边靠着拐杖；光头、大白胡子。"""
    L = Canvas(620, 560)
    chair, chair_dk = hexc('#6f84b5'), hexc('#566b9e')
    # 椅子：高靠背 + 扶手
    sw(L, [[130, 80], [440, 80], [470, 420], [100, 420]], chair, 1, wob=1.5, rim=0.2)
    soft(L, [[130, 80], [440, 80], [470, 420], [100, 420]], 1.8, 0.7, 2)
    sw(L, [[60, 250], [160, 240], [170, 470], [50, 480]], chair_dk, 3, wob=1.2)
    sw(L, [[410, 240], [510, 250], [520, 480], [400, 470]], chair_dk, 4, wob=1.2)
    soft(L, [[60, 250], [160, 240], [170, 470], [50, 480]], 1.5, 0.7, 5)
    soft(L, [[410, 240], [510, 250], [520, 480], [400, 470]], 1.5, 0.7, 6)
    sw(L, [[90, 400], [480, 400], [500, 470], [70, 470]], chair, 7, wob=1.2)
    soft(L, [[90, 400], [480, 400], [500, 470], [70, 470]], 1.5, 0.7, 8)
    for x in (90, 470):
        ink(L, [(x, 470), (x + (8 if x > 300 else -8), 540)], w0=12, color=hexc('#3a4668'), op=1.0, seed=int(x), wob=0.5)
    # Grandad：开衫 + 毯子
    cardi = hexc('#4d6a8a')
    body = [[200, 160], [370, 160], [392, 330], [180, 330]]
    sw(L, body, cardi, 10, wob=1.2)
    soft(L, body, 1.4, 0.7, 11)
    sw(L, [[200, 160], [290, 150], [340, 190], [290, 330], [180, 330]], hexc('#dfe8f6'), 12, wob=1.0, tex_k=0.1)  # 衬衫
    blanket = [[170, 330], [400, 326], [420, 420], [160, 424]]
    sw(L, blanket, hexc('#9fb3dd'), 13, wob=1.4, tex_k=0.12)
    for i in range(6):
        ink(L, [(180 + i * 40, 330), (176 + i * 42, 420)], w0=1.4, color=hexc('#6f84b5'), op=0.5, seed=14 + i, wob=0.5)
    soft(L, blanket, 1.4, 0.7, 20)
    # 石膏腿：伸出来，架在小凳上
    sw(L, [[380, 380], [560, 390], [566, 430], [384, 424]], hexc('#f4f7fc'), 21, wob=1.0, tex_k=0.08)
    soft(L, [[380, 380], [560, 390], [566, 430], [384, 424]], 1.4, 0.7, 22)
    for x in (430, 480, 530):
        ink(L, [(x, 386), (x + 2, 428)], w0=1.2, color=hexc('#9aa6bd'), op=0.5, seed=int(x), wob=0.4)
    sw(L, [[550, 386], [592, 400], [596, 440], [552, 436]], hexc('#2a3358'), 23, wob=0.8)   # 拖鞋/袜子
    sw(L, [[400, 430], [572, 436], [584, 470], [396, 470]], hexc('#566b9e'), 24, wob=1.0)   # 小凳
    # 手 + 头
    dots(L, [(236, 326, 15), (330, 324, 15)], hexc('#efdccf'), 1.0, soft=1.2)
    face(L, 290, 96, 44, 48, 30, smile=True, brow=False)
    ink(L, [(262, 80), (278, 74), (292, 80)], w0=3.2, color=hexc('#f4f6fb'), op=1.0, seed=34, wob=0.3)
    ink(L, [(290, 80), (306, 74), (320, 80)], w0=3.2, color=hexc('#f4f6fb'), op=1.0, seed=35, wob=0.3)
    beard(L, 290, 112, 42, 26, 36)
    dots(L, [(244, 94, 8), (336, 94, 8)], hexc('#efdccf'), 1.0, soft=1.0)
    # 拐杖：靠在椅子旁
    for k, x in enumerate((26, 44)):
        ink(L, [(x, 280), (x + 4, 540)], w0=7, color=hexc('#5a4f4a'), op=1.0, seed=50 + k, wob=0.6)
        ink(L, [(x - 8, 276), (x + 14, 272)], w0=7, color=hexc('#5a4f4a'), op=1.0, seed=52 + k, wob=0.4)
    finish(L, 'grandad_chair')


def farmer():
    """农场的大婶：绿色的厚外套、淡蓝的头巾、粗手套；笑着，手里递一顶毛线帽（帽子在 Bud 的精灵里，这里不画）。"""
    L = Canvas(340, 600)
    coat = hexc('#587a72')
    for sx in (140, 196):
        sw(L, [[sx - 22, 560], [sx + 24, 560], [sx + 32, 586], [sx - 28, 586]], hexc('#3a3b4c'), sx, wob=0.8)
    skirt = [[104, 330], [236, 330], [262, 566], [78, 566]]
    sw(L, skirt, coat, 31, wob=1.4)
    hatch(L, chaikin(np.array(skirt, F), 2, True), 78, 9, 26, hexc('#2f4a46'), op=0.28, w=1.0, seed=32)
    soft(L, skirt, 1.6, 0.7, 33)
    body = [[100, 200], [240, 200], [252, 346], [88, 346]]
    sw(L, body, hexc('#668a82'), 34, wob=1.2)
    soft(L, body, 1.6, 0.7, 35)
    ink(L, [(170, 202), (170, 344)], w0=2.0, color=hexc('#2f4a46'), op=0.7, seed=36, wob=0.4)
    for y in (240, 280, 320):
        dots(L, [(160, y, 3.4), (180, y, 3.4)], hexc('#b9ccd2'), 0.9)
    # 手臂：一只向前伸（递东西），一只垂着
    for sgn, (sx, sy, ex, ey) in enumerate([(108, 214, 60, 340), (236, 214, 300, 300)]):
        arm = [[sx - 17, sy], [sx + 17, sy], [ex + 13, ey], [ex - 13, ey]]
        sw(L, arm, coat, 40 + sgn)
        soft(L, arm, 1.3, 0.65, 42 + sgn)
        dots(L, [(ex, ey + 8, 15)], hexc('#8a98b4'), 1.0, soft=1.2)   # 手套
    face(L, 172, 132, 44, 50, 45, smile=True, brow=False)
    # 头巾（淡蓝）+ 几缕灰发
    kerch = [[116, 138], [120, 96], [146, 70], [180, 64], [214, 78], [230, 114], [232, 150], [214, 112], [180, 96], [146, 106], [128, 150]]
    sw(L, kerch, hexc('#a9bde6'), 46, wob=1.0)
    ink(L, np.vstack([np.array(kerch, F), np.array(kerch[:1], F)]), w0=1.3, color=hexc('#6c7794'), op=0.6, seed=47, wob=0.5, taper=0.1)
    for i in range(5):
        ink(L, [(130 + i * 6, 120), (126 + i * 5, 146 + i * 2)], w0=1.2, color=hexc('#aab4c6'), op=0.7, seed=60 + i, wob=0.3)
    for ex in (140, 204):
        ink(L, [(ex - 6, 112), (ex, 108), (ex + 6, 112)], w0=1.1, color=hexc('#aab4c6'), op=0.0, seed=70, wob=0.1)
    finish(L, 'farmer')


def mum():
    """门口的 Mum：逆着走廊的冷白光，只看见一个深蓝的剪影（长发，长外套），身后一圈淡淡的亮边。"""
    L = Canvas(300, 620)
    sil = hexc('#1a2244')
    wash(L, np.array([[120, 340], [186, 340], [190, 590], [158, 596], [152, 480], [140, 596], [112, 590]], F), sil, op=1.0, wob=1.0, seed=3, smooth=1, tex_k=0.1)
    wash(L, np.array([[100, 180], [200, 180], [240, 360], [226, 470], [92, 470], [66, 360]], F), sil, op=1.0, wob=1.2, seed=4, smooth=2, tex_k=0.1)
    wash(L, np.array([[100, 196], [70, 330], [58, 360], [86, 354], [108, 230]], F), sil, op=1.0, wob=1.0, seed=5, smooth=1, tex_k=0.1)
    wash(L, np.array([[198, 196], [230, 330], [240, 360], [214, 354], [190, 230]], F), sil, op=1.0, wob=1.0, seed=6, smooth=1, tex_k=0.1)
    wash(L, np.array([[150 + math.cos(a) * 34, 142 + math.sin(a) * 40] for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)], F), sil, op=1.0, wob=0.8, seed=7, smooth=2, tex_k=0.1)
    # 长发
    wash(L, np.array([[112, 130], [118, 96], [150, 82], [184, 96], [190, 130], [204, 230], [192, 260], [170, 200], [130, 200], [108, 260], [96, 230]], F), sil, op=1.0, wob=1.0, seed=8, smooth=2, tex_k=0.1)
    rim = hexc('#eaf1fc')
    ink(L, [(112, 120), (120, 96), (150, 82)], w0=2.0, color=rim, op=0.7, seed=9, wob=0.3)
    ink(L, [(96, 232), (108, 260)], w0=1.8, color=rim, op=0.6, seed=10, wob=0.3)
    ink(L, [(100, 196), (68, 330), (58, 360)], w0=1.8, color=rim, op=0.55, seed=11, wob=0.3)
    finish(L, 'mum')


def boats():
    """两种船：小渔船（回港的船队）和 Dad 的船（深蓝船身 + 白色条纹，船舱亮着暖光）。画得够大，Remotion 里按 1:1 或缩小用，不放大。"""
    L = Canvas(520, 420)
    boat(L, 260, 340, 1.9, lit=True, seed=11, hull='#4c6399', flag=True, stripe='#d6e0f4')
    finish(L, 'boat_s')
    L = Canvas(900, 700)
    boat(L, 450, 560, 3.3, lit=True, seed=12, hull='#3a5a96', stripe='#e8eef8')
    wash(L, rect(450 + 1 * 3.3, 560 - 44 * 3.3, 450 + 15 * 3.3, 560 - 28 * 3.3), hexc('#ffe9a0'), op=0.95, wob=0.4, seed=5, smooth=0)
    outline(L, rect(450 + 1 * 3.3, 560 - 44 * 3.3, 450 + 15 * 3.3, 560 - 28 * 3.3), 2.0, 0.8, 6)
    finish(L, 'boat_dad')


if __name__ == '__main__':
    old = json.loads((OUT / 'props.json').read_text())
    META.clear(); META.update(old)
    for nm in ('ice_hole_back', 'ice_hole_front'):   # 由 bg_wild.py 生成的冰窟窿图，补上锚点（中心）
        META[nm] = {'w': 380, 'h': 120, 'ax': 190.0, 'ay': 60.0}
    grandad_hurt(); grandad_chair(); farmer(); mum(); boats()
    (OUT / 'props.json').write_text(json.dumps(META, indent=1))
    from PIL import Image
    names = ['grandad_hurt', 'grandad_chair', 'farmer', 'mum', 'boat_s', 'boat_dad']
    ims = [Image.open(OUT / f'{n}.png') for n in names]
    W_ = sum(i.width for i in ims) + 20 * len(ims); H_ = max(i.height for i in ims) + 20
    sheet = Image.new('RGB', (W_, H_), (150, 175, 215)); x = 10
    for i in ims:
        sheet.paste(i, (x, H_ - i.height - 10), i); x += i.width + 20
    sheet.save('/tmp/claude-0/-home-user-math-research/747091a3-a05e-575b-b1ac-cb27e1adeb12/scratchpad/ref/props2.png')
    print({k: META[k] for k in names})
