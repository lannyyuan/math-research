"""暖色审计：在抽样帧里找出“暖色”像素（色相 0~70° 或 335~360°，饱和度≥0.30，亮度≥0.30），
列出每帧的暖色像素占比和连通区域，并生成高亮图（暖色像素标成洋红）供人工核对：
全片暖色只允许出现在 灯 / 火堆 / 小石头的红围巾 三处。
用法： python3 -I scripts/audit_warm.py out/audit  frame1.png frame2.png ..."""
import sys, os
import numpy as np
from PIL import Image

outdir = sys.argv[1]
os.makedirs(outdir, exist_ok=True)

def hsv(a):
    r, g, b = a[..., 0] / 255.0, a[..., 1] / 255.0, a[..., 2] / 255.0
    mx, mn = np.max(a / 255.0, axis=-1), np.min(a / 255.0, axis=-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rr = m & (mx == r)
    gg = m & (mx == g) & ~rr
    bb = m & ~rr & ~gg
    h[rr] = (60 * ((g - b)[rr] / d[rr])) % 360
    h[gg] = 60 * ((b - r)[gg] / d[gg]) + 120
    h[bb] = 60 * ((r - g)[bb] / d[bb]) + 240
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx

print(f"{'frame':36s} {'warm%':>7s}  warm bounding boxes (x0,y0,x1,y1 in 1920x1080)")
for f in sys.argv[2:]:
    im = Image.open(f).convert("RGB")
    sc = 1920 / im.width
    a = np.asarray(im).astype(np.float32)
    h, s, v = hsv(a)
    warm = (((h <= 70) | (h >= 335)) & (s >= 0.30) & (v >= 0.30))
    pct = 100.0 * warm.mean()
    # 粗略连通：把图分成 24px 方格，合并相邻有暖色的方格
    cell = 24
    H, W = warm.shape
    gh, gw = (H + cell - 1) // cell, (W + cell - 1) // cell
    grid = np.zeros((gh, gw), bool)
    for y in range(gh):
        for x in range(gw):
            grid[y, x] = warm[y * cell:(y + 1) * cell, x * cell:(x + 1) * cell].sum() >= 4
    seen = np.zeros_like(grid)
    boxes = []
    for y in range(gh):
        for x in range(gw):
            if grid[y, x] and not seen[y, x]:
                st = [(y, x)]; seen[y, x] = True; xs = []; ys = []
                while st:
                    cy, cx = st.pop(); xs.append(cx); ys.append(cy)
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < gh and 0 <= nx < gw and grid[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True; st.append((ny, nx))
                boxes.append((int(min(xs) * cell * sc), int(min(ys) * cell * sc), int((max(xs) + 1) * cell * sc), int((max(ys) + 1) * cell * sc)))
    name = os.path.basename(f)
    print(f"{name:36s} {pct:6.2f}%  {boxes[:8]}")
    out = a.copy()
    out[warm] = [255, 0, 255]
    both = np.concatenate([a, out], axis=1).astype(np.uint8)
    Image.fromarray(both).resize((both.shape[1] // 2, both.shape[0] // 2)).save(os.path.join(outdir, name))
