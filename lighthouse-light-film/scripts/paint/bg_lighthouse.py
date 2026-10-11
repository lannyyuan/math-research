"""灯塔外景：岬角上一座又高又白的灯塔，脚下是守塔人的小屋和一道结冰的石阶。
 lh_day：圣诞前夜的早晨（阴天）；lh_night：暴风雪的夜里。灯室是黑的，亮不亮由 Remotion 里叠的光决定。"""
from common import *

LX, LY, LH = 1560, 900, 660   # 灯塔：塔底中点、塔高


def far(kind):
    L = Canvas(W, H)
    hz = 520
    L.rgb[:] = sky(W, H, 'day' if kind == 'day' else 'storm', seed=4 if kind == 'day' else 6, horizon=hz / H, blotch=0.3)
    L.a[:] = 1
    tone = 'grey' if kind == 'day' else 'night'
    hills(L, ridge_pts(0, W, hz + 4, 34, 21, 60), hz + 30, hexc('#9aabc6') if kind == 'day' else hexc('#34476f'), snow=True, seed=21, op=0.9)
    sea(L, hz + 14, H, seed=7, tone=tone, strokes=620)
    # 海面上几道白浪
    r = np.random.default_rng(3)
    for i in range(34):
        y = hz + 60 + r.random() ** 1.4 * 420
        x = r.uniform(0, W)
        ln = r.uniform(60, 220) * (0.6 + (y - hz) / 400)
        ink(L, [(x, y), (x + ln / 2, y - 2), (x + ln, y + 1)], w0=1.5 + (y - hz) / 150, color=hexc('#dbe5f6'), op=0.35 if kind == 'day' else 0.28, seed=i + 300, wob=0.8, taper=0.5)
    if kind == 'day':
        grade(L, 'dusk') if False else None
    return L


def near(kind):
    L = Canvas(W, H)
    # 岬角：岩石的断面 + 顶上一块平平的雪地
    plateau = np.array([[-60, 905], [300, 900], [700, 906], [1100, 902], [1560, 904], [2000, 906], [2150, 914], [2250, 938]], F)
    # 悬崖的岩壁（右边伸向大海的那一面）
    rock_face = np.array([[2100, 910], [2250, 936], [2330, 990], [2400, 1090], [2480, 1180], [1900, 1180], [1950, 990]], F)
    wash(L, rock_face, P['rock'], op=1.0, wob=2.5, seed=11, smooth=1, tex_k=0.22, rim=0.2)
    hatch(L, rock_face, 72, 9, 22, P['rock_dk'], op=0.5, w=1.2, seed=12)
    hatch(L, rock_face, 20, 14, 26, P['rock_lt'], op=0.2, w=1.0, seed=13)
    rock_base(L, 1250, 985, 2100, 230, seed=17, snow=True)
    snow_ground(L, catmull(plateau, 8), 1300, seed=15)
    # 岩壁边缘的雪檐
    lip = np.array([[2080, 906], [2160, 912], [2250, 934], [2290, 958], [2240, 958], [2150, 936], [2070, 928]], F)
    wash(L, lip, P['snow'], op=1.0, wob=1.5, seed=16, smooth=2, tex_k=0.07)
    # 灯塔 + 脚下的小屋
    lighthouse(L, LX, LY, LH, lit=False, seed=31, cottage=False)
    house(L, LX - 560, 912, 380, 210, 0.55, seed=41, windows=2, door=True, chimney=True, wall='#eef2f8', roof_col='#566480')
    smoke(L, LX - 500, 640, n=5, seed=42, s=0.9, op=0.4)
    # 通向塔门的结冰石阶：三级，蓝灰的侧面，白的踏面，旁边一道铁扶手
    for k in range(3):
        x0, x1 = LX - 110 - (2 - k) * 28, LX + 110 + (2 - k) * 28
        y1 = LY + 36 - k * 12 + 2
        top = rect(x0, y1 - 14, x1, y1)
        wash(L, top, P['snow'], op=1.0, wob=1.0, seed=50 + k, smooth=1, tex_k=0.07)
        side = rect(x0 + 4, y1, x1 - 4, y1 + 22)
        wash(L, side, P['snow_sh2'], op=0.85, wob=1.0, seed=60 + k, smooth=0, tex_k=0.16)
        outline(L, side, 1.2, 0.5, 70 + k)
    ink(L, [(LX - 150, LY + 30), (LX - 150, LY - 80), (LX - 100, LY - 80)], w0=2.4, color=INK, op=0.85, seed=80, wob=0.5)
    ink(L, [(LX + 150, LY + 30), (LX + 150, LY - 80), (LX + 100, LY - 80)], w0=2.4, color=INK, op=0.85, seed=81, wob=0.5)
    # 篱笆桩 + 绳子，沿小路
    for i in range(5):
        px = 160 + i * 150
        post(L, px, 972 + i * 3, 96, 32, seed=300 + i)
        if i:
            wire(L, (px - 150 + 6, 972 + (i - 1) * 3 - 92), (px - 6, 972 + i * 3 - 92), sag=10, seed=330 + i)
    for i, (bx, by) in enumerate([(240, 1060), (1250, 1040), (2250, 1010)]):
        bush(L, bx, by, 150, 1.0, 8, seed=400 + i)
    rocks(L, 820, 1050, 260, 90, seed=500)
    rocks(L, 1880, 1040, 240, 80, seed=501)
    if kind == 'night':
        grade(L, 'storm')
    else:
        grade(L, 'dusk')
    return L


if __name__ == '__main__':
    for k in ('day', 'night'):
        f = far(k)
        n = near(k)
        save_pair(f'lh_{k}', f, n)
    print('ok')
