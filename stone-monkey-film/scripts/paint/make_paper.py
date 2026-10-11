"""宣纸纹理：中性灰底 + 纤维 + 斑驳，soft-light 叠在整片画面上。"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from cn import *
import cv2

W, H = 1920, 1080
r = np.random.default_rng(5)
base = 0.5 + (fbm(H, W, 3, 260, 4, 0.55) - 0.5) * 0.10 + (fbm(H, W, 8, 40, 3, 0.5) - 0.5) * 0.07 + grain(H, W, 9, 0.7) * 0.05
L = Canvas(W, H, bg=0.0)
L.rgb[:] = base[..., None]
# 纤维：很多细长的弯曲浅线 / 深线
fib = np.zeros((H, W), np.float32)
for _ in range(2600):
    x, y = r.uniform(0, W), r.uniform(0, H)
    ang = r.uniform(0, math.pi)
    ln = r.uniform(14, 70)
    pts = []
    a = ang
    for k in range(5):
        a += r.normal(0, 0.35)
        x += math.cos(a) * ln / 5; y += math.sin(a) * ln / 5
        pts.append((int(x), int(y)))
    v = r.choice([-1, 1]) * r.uniform(0.05, 0.16)
    tmp = np.zeros((H, W), np.uint8)
    for i in range(len(pts) - 1):
        cv2.line(tmp, pts[i], pts[i + 1], 255, 1, cv2.LINE_AA)
    fib += (tmp.astype(np.float32) / 255.0) * v if False else 0
    if len(pts) > 1:
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x0, x1, y0, y1 = max(min(xs) - 2, 0), min(max(xs) + 3, W), max(min(ys) - 2, 0), min(max(ys) + 3, H)
        if x1 > x0 and y1 > y0:
            sub = np.zeros((y1 - y0, x1 - x0), np.uint8)
            for i in range(len(pts) - 1):
                cv2.line(sub, (pts[i][0] - x0, pts[i][1] - y0), (pts[i + 1][0] - x0, pts[i + 1][1] - y0), 255, 1, cv2.LINE_AA)
            fib[y0:y1, x0:x1] += sub.astype(np.float32) / 255.0 * v
fib = cv2.GaussianBlur(fib, (0, 0), 0.6)
img = np.clip(base + fib, 0, 1)
out = np.stack([img] * 3, -1)
cv2.imwrite(str(pathlib.Path(__file__).resolve().parents[2] / 'public/bg/paper.jpg'), cv2.cvtColor((out * 255).astype(np.uint8), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
print('paper ok')
