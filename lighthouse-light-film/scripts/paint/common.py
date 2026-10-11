"""各场景背景共用的小工具：调色（夜里的雪是蓝灰的）、预览、木板/石墙等。"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from objects import *   # noqa
from world import *     # noqa
import cv2

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'public/bg'
OUT.mkdir(parents=True, exist_ok=True)
REF = pathlib.Path('/tmp/claude-0/-home-user-math-research/747091a3-a05e-575b-b1ac-cb27e1adeb12/scratchpad/ref')
REF.mkdir(parents=True, exist_ok=True)
W, H = 2900, 1080

# 调色：把一层画布的颜色整体压向夜里的蓝灰（只动 RGB，不动透明度）
GRADES = {
    'dusk': ((0.86, 0.90, 0.99), (0.0, 0.0, 0.01)),
    'night': ((0.66, 0.74, 0.95), (0.0, 0.004, 0.03)),
    'storm': ((0.58, 0.66, 0.90), (0.0, 0.004, 0.03)),
    'deep': ((0.46, 0.54, 0.80), (0.0, 0.004, 0.035)),
}


def grade(L, kind):
    mul, add = GRADES[kind]
    L.rgb = np.clip(L.rgb * np.asarray(mul, F) + np.asarray(add, F), 0, 1)
    return L


def save_pair(name, far, near, w=None, h=None, jpg_far=True):
    w = w or (far or near).w
    h = h or (far or near).h
    if far is not None:
        far.save(OUT / f'{name}_far.jpg', jpg=True, q=92)
    if near is not None:
        near.save(OUT / f'{name}_near.png')
    comp = Canvas(w, h)
    for L in (far, near):
        if L is not None:
            comp.over(0, h, 0, w, L.rgb, L.a)
    img = (np.clip(comp.flat(), 0, 1) * 255).astype(np.uint8)
    cv2.imwrite(str(REF / f'{name}.png'), cv2.cvtColor(cv2.resize(img, (w // 2, h // 2), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2BGR))


def planks(L, x0, y0, x1, y1, seed=0, col='#5c6a8a', gap=46, hor=True):
    """木板（地板 / 工作台面 / 墙板）：一排排窄色块 + 木纹。"""
    r = np.random.default_rng(seed)
    if hor:
        n = int((y1 - y0) / gap) + 1
        for i in range(n):
            ya, yb = y0 + i * gap, min(y0 + (i + 1) * gap, y1)
            c = rgbmix(hexc(col), hexc(col) * 0.82, r.random())
            wash(L, rect(x0, ya, x1, yb), c, op=1.0, wob=0.8, seed=int(r.integers(1e6)), smooth=0, tex_k=0.06, rim=0.08, rim_w=1.5)
            ink(L, [(x0, ya + 1), ((x0 + x1) / 2, ya + r.normal(0, 0.7)), (x1, ya + 1)], w0=1.2, color=INK, op=0.45, seed=int(r.integers(1e6)), wob=0.4, taper=0.1)
            for _ in range(int((x1 - x0) / 160)):
                gx = r.uniform(x0, x1)
                ink(L, [(gx, ya + gap * 0.3), (gx + r.uniform(40, 120), ya + gap * 0.3 + r.normal(0, 1.2))], w0=0.9, color=INK, op=0.16, seed=int(r.integers(1e6)), wob=0.3, taper=0.5)
    else:
        n = int((x1 - x0) / gap) + 1
        for i in range(n):
            xa, xb = x0 + i * gap, min(x0 + (i + 1) * gap, x1)
            c = rgbmix(hexc(col), hexc(col) * 0.82, r.random())
            wash(L, rect(xa, y0, xb, y1), c, op=1.0, wob=0.8, seed=int(r.integers(1e6)), smooth=0, tex_k=0.06, rim=0.08, rim_w=1.5)
            ink(L, [(xa + 1, y0), (xa + r.normal(0, 0.7), (y0 + y1) / 2), (xa + 1, y1)], w0=1.2, color=INK, op=0.45, seed=int(r.integers(1e6)), wob=0.4, taper=0.1)


def stones(L, x0, y0, x1, y1, seed=0, col='#6b7893', row=54, bw=120):
    """石头墙：错缝的方石块，每块一点点不同的蓝灰。"""
    r = np.random.default_rng(seed)
    n = int((y1 - y0) / row) + 1
    for i in range(n):
        ya, yb = y0 + i * row, min(y0 + (i + 1) * row, y1)
        x = x0 - (bw * 0.5 if i % 2 else 0) + r.uniform(0, 20)
        while x < x1:
            w = bw * r.uniform(0.8, 1.25)
            xa, xb = max(x, x0), min(x + w, x1)
            if xb - xa > 6:
                c = rgbmix(hexc(col), hexc(col) * 0.8, r.random() * 0.8)
                pts = rect(xa + 2, ya + 2, xb - 2, yb - 2)
                wash(L, pts, c, op=1.0, wob=1.2, seed=int(r.integers(1e6)), smooth=1, tex_k=0.2, rim=0.16, rim_w=2.0)
                ink(L, [(xa + 4, yb - 3), ((xa + xb) / 2, yb - 3 + r.normal(0, .6)), (xb - 4, yb - 3)], w0=1.2, color=INK, op=0.4, seed=int(r.integers(1e6)), wob=0.4, taper=0.2)
            x += w


def field(L, y0, y1, seed=0, top='#c3d0e6', bot='#eef2f9', x0=0, x1=None):
    """远处的一整片雪原（地平线以下、近景雪坡以上）：淡蓝 → 近白的渐变 + 几道浅浅的雪垄；上沿是缓缓起伏、虚化的。"""
    x1 = x1 or L.w
    h = y1 - y0
    ys = np.linspace(0, 1, h, dtype=F)[:, None, None]
    img = rgbmix(hexc(top), hexc(bot), ys ** 0.8) * np.ones((1, x1 - x0, 1), F)
    n = fbm(h, x1 - x0, seed, 220, 4, 0.55, warp=40)[..., None]
    img = img * (0.96 + 0.08 * n) + grain(h, x1 - x0, seed + 1, 0.8)[..., None] * 0.012
    xs = np.arange(x1 - x0, dtype=F)
    edge = 14 * np.sin(xs / 310 + seed) + 9 * np.sin(xs / 97 + seed * 2) + 30
    yy = np.arange(h, dtype=F)[:, None]
    a = np.clip((yy - edge[None, :]) / 26.0, 0, 1)
    a = a * a * (3 - 2 * a)
    L.over(y0, y1, x0, x1, np.clip(img, 0, 1).astype(F), a.astype(F))
    r = np.random.default_rng(seed + 7)
    for i in range(int((x1 - x0) / 140)):
        y = y0 + 40 + (r.random() ** 1.2) * (h - 40)
        x = r.uniform(x0, x1)
        ln = r.uniform(60, 240) * (0.5 + (y - y0) / max(h, 1))
        ink(L, [(x, y), (x + ln / 2, y + r.normal(0, 1.5)), (x + ln, y + r.normal(0, 2))], w0=1.6, color=P['snow_sh2'], op=0.25, seed=int(r.integers(1e6)), wob=1.0, taper=0.5)


def land(L, x0, x1, ytop, ybot, seed=0, snow='#dfe7f4', rock='#3b4a6e'):
    """水边的一小块陆地（房子脚下）：上面是雪，水线处一圈深色的岩石。"""
    r = np.random.default_rng(seed)
    n = max(int((x1 - x0) / 90), 4)
    xs = np.linspace(x0, x1, n)
    top = [(x, ytop + r.normal(0, 4)) for x in xs]
    bot = [(x, ybot + r.normal(0, 3)) for x in xs[::-1]]
    wash(L, np.array(top + bot, F), hexc(rock), op=1.0, wob=2.0, seed=seed, smooth=1, tex_k=0.2)
    sn = [(x, y) for x, y in top] + [(x, y + (ybot - ytop) * 0.7 + r.normal(0, 3)) for x, y in top[::-1]]
    wash(L, np.array(sn, F), hexc(snow), op=1.0, wob=2.0, seed=seed + 1, smooth=2, tex_k=0.07)
    ink(L, np.array(top, F), w0=1.6, color=INK, op=0.45, seed=seed + 2, wob=1.0, taper=0.2)
