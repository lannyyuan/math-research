"""场景 8：灯塔里面——灯室（大透镜 + 一圈窗，外面是暴风雪的夜）和 发电机房（石墙 + 老发电机）。全是冷色，没有一盏暖色的灯。
 暖色的光（灯亮了以后）由 Remotion 叠上去。"""
from common import *
from bg_workshop import cog

WW = 2400
LENS = (1200, 700)   # 透镜的底座中心（世界坐标）


def lamp_far():
    L = Canvas(WW, H)
    # 一圈大窗：外面是暴风雪的夜空和黑海
    L.rgb[:] = hexc('#3d4a6c')
    L.a[:] = 1
    wy0, wy1 = 80, 700
    sk = sky(WW, wy1 - wy0, 'storm', seed=9, horizon=0.78, blotch=0.4)
    L.over(wy0, wy1, 0, WW, sk, np.ones((wy1 - wy0, WW), F))
    sea(L, 430, wy1, seed=14, tone='night', strokes=220)
    L.a[:] = 1
    # 窗框：竖向的铁条 + 上下的横梁
    for i in range(9):
        x = i * 300
        wash(L, rect(x - 9, wy0 - 30, x + 9, 790), hexc('#2a3552'), op=1.0, wob=0.6, seed=i, smooth=0, tex_k=0.12)
        ink(L, [(x - 9, wy0), (x - 9, 790)], w0=1.4, color=INK, op=0.7, seed=i + 20, wob=0.3)
    wash(L, rect(0, wy0 - 40, WW, wy0 + 10), hexc('#2a3552'), op=1.0, wob=0.8, seed=30, smooth=0, tex_k=0.12)
    wash(L, rect(0, 700, WW, 790), hexc('#37456b'), op=1.0, wob=0.8, seed=31, smooth=0, tex_k=0.12)
    ink(L, [(0, 700), (WW, 700)], w0=3, color=INK, op=0.8, seed=32, wob=0.8)
    # 窗外的雪（斜着飘）由 Remotion 的 Snow 负责。窗台雪
    wash(L, rect(0, 686, WW, 704), P['snow'], op=0.9, wob=2.0, seed=33, smooth=1, tex_k=0.08)
    # 地板：深色的石板（圆形平台的感觉：一块宽宽的石盘）
    planks(L, 0, 790, WW, H, seed=34, col='#46526f', gap=64, hor=True)
    ink(L, [(0, 790), (WW, 790)], w0=3, color=INK, op=0.8, seed=35, wob=0.8)
    grade(L, 'dusk')
    return L


def lamp_near():
    L = Canvas(WW, H)
    cx, by = LENS
    # 透镜的铁底座
    wash(L, np.array([[cx - 230, by + 90], [cx + 230, by + 90], [cx + 200, by + 20], [cx - 200, by + 20]], F), hexc('#3a4668'), op=1.0, wob=0.8, seed=40, smooth=0, tex_k=0.14)
    outline(L, np.array([[cx - 230, by + 90], [cx + 230, by + 90], [cx + 200, by + 20], [cx - 200, by + 20]], F), 1.8, 0.85, 41)
    # 大透镜：蜂窝状的玻璃罩（一圈圈棱镜），淡蓝的玻璃，灯泡的位置在中心
    body = [(cx - 190, by + 22), (cx - 205, by - 120), (cx - 180, by - 330), (cx - 110, by - 480), (cx, by - 520), (cx + 110, by - 480), (cx + 180, by - 330), (cx + 205, by - 120), (cx + 190, by + 22)]
    wash(L, np.array(body, F), hexc('#a9c0e0'), op=0.62, wob=1.0, seed=42, smooth=2, tex_k=0.08, rim=0.2, rim_w=5)
    wash(L, np.array(body, F) * [0.78, 1] + [cx * 0.22, 0], hexc('#d3e1f4'), op=0.35, wob=1.0, seed=43, smooth=2, tex_k=0.08)
    # 一圈圈的棱镜带
    for k in range(9):
        y = by - 20 - k * 52
        half = 200 * (1 - (k / 10) ** 2.2)
        ink(L, [(cx - half, y), (cx - half * 0.5, y + 10), (cx, y + 14), (cx + half * 0.5, y + 10), (cx + half, y)], w0=2.4, color=hexc('#5972a4'), op=0.7, seed=50 + k, wob=0.6, taper=0.2)
        for j in range(-4, 5):
            x = cx + j * half / 4.2
            ink(L, [(x, y), (x + j * 1.5, y - 40)], w0=1.2, color=hexc('#7b92bf'), op=0.5, seed=70 + k * 10 + j, wob=0.4, taper=0.3)
    ink(L, np.vstack([body, body[:1]]), w0=2.6, color=INK, op=0.85, seed=90, wob=1.0, taper=0.05, smooth=True)
    # 中心的灯座（灯泡的位置：空的插口）
    wash(L, rect(cx - 26, by - 170, cx + 26, by - 100), hexc('#2e3a5c'), op=1.0, wob=0.6, seed=91, smooth=0, tex_k=0.1)
    outline(L, rect(cx - 26, by - 170, cx + 26, by - 100), 1.4, 0.85, 92)
    wash(L, rect(cx - 12, by - 182, cx + 12, by - 170), hexc('#8d9bbd'), op=1.0, wob=0.4, seed=93, smooth=0)
    dots(L, [(cx, by - 285, 20)], hexc('#cfdcf0'), 0.0)
    # 铁栏杆（前景一圈）
    for i in range(12):
        x = 60 + i * 200
        ink(L, [(x, 1000), (x, 905)], w0=4, color=hexc('#2a3552'), op=0.9, seed=100 + i, wob=0.4)
    ink(L, [(0, 905), (WW, 905)], w0=4, color=hexc('#2a3552'), op=0.9, seed=120, wob=0.8)
    grade(L, 'dusk')
    return L


# 发电机房
GEN = (1200, 860)


def gen_far():
    L = Canvas(WW, H)
    wash(L, rect(0, 0, WW, 800), hexc('#566785'), op=1.0, wob=0.5, seed=1, smooth=0, tex_k=0.05)
    stones(L, 0, 0, WW, 800, seed=1, col='#788aab', row=62, bw=150)
    glow(L, 400, 330, 420, hexc('#dbe6f6'), 0.20, 1.8)
    planks(L, 0, 800, WW, H, seed=2, col='#505d7c', gap=60, hor=True)
    ink(L, [(0, 800), (WW, 800)], w0=3, color=INK, op=0.8, seed=3, wob=1.0)
    # 小窗：暴风雪的夜（窄）
    wx0, wy0, wx1, wy1 = 250, 220, 380, 420
    sk = sky(wx1 - wx0, wy1 - wy0, 'storm', seed=5, horizon=0.9, blotch=0.2)
    L.over(wy0, wy1, wx0, wx1, sk, np.ones((wy1 - wy0, wx1 - wx0), F))
    flakes(L, 14, 9, 1.5, 3, region=(wx0, wy0, wx1, wy1), color=(0.95, 0.97, 1), op=0.95, sparkle=0)
    outline(L, rect(wx0, wy0, wx1, wy1), 6, 0.95, 6, col=hexc('#2a3552'))
    ink(L, [((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], w0=4, color=hexc('#2a3552'), op=0.9, seed=7, wob=0.3)
    # 墙上的管子 + 一根粗电缆通向天花板（通向灯室）
    for k, (px, py) in enumerate([(560, 360), (560, 420)]):
        ink(L, [(px, py), (px + 800, py + 2)], w0=18, color=hexc('#4a5778'), op=0.95, seed=10 + k, wob=0.8, taper=0.02)
        ink(L, [(px, py - 5), (px + 800, py - 3)], w0=4, color=hexc('#9bacca'), op=0.5, seed=12 + k, wob=0.8, taper=0.02)
    ink(L, [(1360, 360), (1460, 360), (1500, 330), (1500, 0)], w0=22, color=hexc('#4a5778'), op=0.95, seed=14, wob=0.8, taper=0.02)
    for x in range(600, 1400, 160):
        ink(L, [(x, 340), (x, 440)], w0=6, color=hexc('#2f3b5b'), op=0.9, seed=x, wob=0.4)
    cog(L, 1760, 400, 80, 20, col='#6e7ea4', teeth=14)
    cog(L, 1870, 330, 46, 22, col='#8190b3', teeth=10)
    # 悬着的灯泡（灭的，冷色）
    ink(L, [(1000, 0), (1000, 190)], w0=3, color=INK, op=0.8, seed=30, wob=0.3)
    wash(L, np.array([[1000 + math.cos(a) * 26, 220 + math.sin(a) * 30] for a in np.linspace(0, 6.28, 12, endpoint=False)], F), hexc('#cfdcf0'), op=0.85, wob=0.5, seed=31, smooth=2)
    outline(L, np.array([[1000 + math.cos(a) * 26, 220 + math.sin(a) * 30] for a in np.linspace(0, 6.28, 12, endpoint=False)], F), 1.2, 0.7, 32)
    grade(L, 'dusk')
    return L


def gen_near():
    L = Canvas(WW, H)
    gx, gy = GEN
    # 发电机：深绿灰的大铁箱 + 圆筒油箱 + 飞轮 + 排气管 + 小表盘；电池仓在前面（打开着，是空的）
    body = rect(gx - 300, gy - 330, gx + 300, gy)
    wash(L, body, hexc('#58708f'), op=1.0, wob=1.4, seed=200, smooth=0, tex_k=0.14, rim=0.16)
    outline(L, body, 2.4, 0.85, 201)
    wash(L, rect(gx - 300, gy - 330, gx - 250, gy), hexc('#46586f'), op=0.7, wob=1.0, seed=202, smooth=0, tex_k=0.1)
    hatch(L, body, 78, 11, 24, hexc('#2c3a58'), op=0.22, w=1.0, seed=203)
    for rx in (gx - 270, gx + 270):
        for ry in (gy - 300, gy - 30):
            dots(L, [(rx, ry, 6)], hexc('#aab9d4'), 0.9)
    # 顶上的圆筒（油箱）
    tank = np.array([[gx - 170, gy - 330], [gx - 170, gy - 430], [gx + 100, gy - 430], [gx + 100, gy - 330]], F)
    wash(L, tank, hexc('#6f86a8'), op=1.0, wob=1.0, seed=204, smooth=2, tex_k=0.14)
    outline(L, tank, 2.0, 0.85, 205)
    ink(L, [(gx - 160, gy - 400), (gx + 90, gy - 400)], w0=3, color=hexc('#aab9d4'), op=0.5, seed=206, wob=0.6)
    # 排气管
    ink(L, [(gx + 200, gy - 330), (gx + 200, gy - 470), (gx + 260, gy - 520)], w0=22, color=hexc('#3a4a68'), op=0.95, seed=207, wob=0.8, taper=0.02)
    # 飞轮（右侧的大圆）+ 拉绳手柄
    fx, fy = gx + 420, gy - 170
    wash(L, np.array([[fx + math.cos(a) * 130, fy + math.sin(a) * 130] for a in np.linspace(0, 6.28, 28, endpoint=False)], F), hexc('#3a4a68'), op=1.0, wob=0.8, seed=208, smooth=2, tex_k=0.12)
    wash(L, np.array([[fx + math.cos(a) * 95, fy + math.sin(a) * 95] for a in np.linspace(0, 6.28, 24, endpoint=False)], F), hexc('#5d6f93'), op=1.0, wob=0.8, seed=209, smooth=2, tex_k=0.12)
    for k in range(6):
        a = k * math.pi / 3
        ink(L, [(fx, fy), (fx + math.cos(a) * 92, fy + math.sin(a) * 92)], w0=12, color=hexc('#2a3552'), op=0.9, seed=210 + k, wob=0.4)
    dots(L, [(fx, fy, 22)], hexc('#aab9d4'), 1.0)
    outline(L, np.array([[fx + math.cos(a) * 130, fy + math.sin(a) * 130] for a in np.linspace(0, 6.28, 28, endpoint=False)], F), 2.0, 0.85, 220)
    ink(L, [(fx + 120, fy - 20), (fx + 190, fy + 20), (fx + 210, fy + 140)], w0=3, color=hexc('#2a3552'), op=0.9, seed=221, wob=0.6)
    wash(L, rect(fx + 196, fy + 136, fx + 226, fy + 160), hexc('#aab9d4'), op=1.0, wob=0.4, seed=222, smooth=0)
    # 小表盘
    dots(L, [(gx - 160, gy - 230, 44)], hexc('#d8e3f4'), 1.0)
    dots(L, [(gx - 160, gy - 230, 44)], hexc('#2a3552'), 0.0)
    for a in np.linspace(math.pi * 0.8, math.pi * 2.2, 9):
        ink(L, [(gx - 160 + math.cos(a) * 34, gy - 230 + math.sin(a) * 34), (gx - 160 + math.cos(a) * 40, gy - 230 + math.sin(a) * 40)], w0=1.4, color=INK, op=0.8, seed=int(a * 100), wob=0.1)
    ink(L, [(gx - 160, gy - 230), (gx - 140, gy - 252)], w0=2.6, color=INK, op=0.9, seed=230, wob=0.2)
    ink(L, np.array([[gx - 160 + math.cos(a) * 44, gy - 230 + math.sin(a) * 44] for a in np.linspace(0, 6.4, 24)], F), w0=3, color=INK, op=0.85, seed=231, wob=0.4)
    # 电池仓：前面一个敞开的方框，里面是黑的（Bolts 要把电池装进来）
    bay = rect(gx + 20, gy - 200, gx + 200, gy - 70)
    wash(L, bay, hexc('#15203c'), op=1.0, wob=0.8, seed=232, smooth=0, tex_k=0.1)
    outline(L, bay, 3.2, 0.9, 233)
    wash(L, rect(gx + 200, gy - 205, gx + 296, gy - 66), hexc('#46586f'), op=1.0, wob=0.8, seed=234, smooth=0, tex_k=0.1)   # 打开的仓门
    outline(L, rect(gx + 200, gy - 205, gx + 296, gy - 66), 2.0, 0.85, 235)
    for i in range(3):
        ink(L, [(gx + 30, gy - 180 + i * 38), (gx + 190, gy - 180 + i * 38)], w0=2.2, color=hexc('#3a4a68'), op=0.7, seed=236 + i, wob=0.4)
    # 脚：粗粗的底座 + 地上的电缆
    wash(L, rect(gx - 330, gy, gx + 330, gy + 36), hexc('#2f3b5b'), op=1.0, wob=1.0, seed=240, smooth=0, tex_k=0.12)
    outline(L, rect(gx - 330, gy, gx + 330, gy + 36), 2.0, 0.85, 241)
    ink(L, [(gx - 330, gy + 20), (gx - 600, gy + 60), (gx - 900, gy + 40), (gx - 1180, gy + 80)], w0=12, color=hexc('#2a3552'), op=0.9, seed=242, wob=2.0)
    ink(L, [(gx - 330, gy + 17), (gx - 600, gy + 57), (gx - 900, gy + 37)], w0=2.4, color=hexc('#8493b5'), op=0.4, seed=243, wob=2.0)
    # 煤桶 / 工具箱
    wash(L, np.array([[1960, 820], [2100, 820], [2085, 960], [1975, 960]], F), hexc('#44526f'), op=1.0, wob=1.0, seed=250, smooth=1, tex_k=0.14)
    outline(L, np.array([[1960, 820], [2100, 820], [2085, 960], [1975, 960]], F), 1.8, 0.85, 251)
    grade(L, 'dusk')
    return L


if __name__ == '__main__':
    save_pair('lamp', lamp_far(), lamp_near())
    save_pair('gen', gen_far(), gen_near())
    print('ok')
