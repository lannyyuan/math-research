"""设定表上的几处修图（在抠精灵之前，直接改设定表的像素）：
 · 老龙：设定表上眼神凶、眉头紧——任务书要求“慈眉，眼皮半垂，像刚睡醒，不能凶”：把眼睛盖上半垂的眼皮，抹平眉间的怒纹，重画弯弯垂向外侧的慈眉，嘴角微微上扬；
 · 龟甲：胸前添一道细裂纹（石头变的）。
"""
import math
import numpy as np, cv2

def _ring_color(img, cx, cy, r0, r1):
    yy, xx = np.mgrid[0:img.shape[0], 0:img.shape[1]]
    d = np.hypot(xx - cx, yy - cy)
    m = (d >= r0) & (d <= r1)
    px = img[m].astype(np.float32)
    lum = px @ np.array([0.299, 0.587, 0.114], np.float32)
    keep = (lum > np.percentile(lum, 35)) & (lum < np.percentile(lum, 90))   # 去掉最暗的墨线和最亮的高光
    return np.median(px[keep], axis=0)

def _blend_poly(img, poly, color, alpha=1.0, ss=4, blur=0.6):
    h, w = img.shape[:2]
    x0 = int(max(poly[:, 0].min() - 3, 0)); x1 = int(min(poly[:, 0].max() + 4, w))
    y0 = int(max(poly[:, 1].min() - 3, 0)); y1 = int(min(poly[:, 1].max() + 4, h))
    big = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.uint8)
    cv2.fillPoly(big, [np.round((poly - [x0, y0]) * ss).astype(np.int32)], 255, lineType=cv2.LINE_AA)
    m = cv2.resize(big, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    if blur: m = cv2.GaussianBlur(m, (0, 0), blur)
    m = (m * alpha)[..., None]
    img[y0:y1, x0:x1] = (img[y0:y1, x0:x1] * (1 - m) + np.asarray(color, np.float32) * m)

def _stroke(img, pts, w, color, alpha=0.9, taper=True):
    """一笔：两头收尖的弯线"""
    pts = np.asarray(pts, np.float32)
    n = len(pts)
    for i in range(n - 1):
        t = (i + 0.5) / (n - 1)
        k = math.sin(math.pi * t) ** 0.6 if taper else 1.0
        poly = np.array([pts[i], pts[i + 1]], np.float32)
        d = poly[1] - poly[0]; L = np.hypot(*d) + 1e-6; nrm = np.array([-d[1], d[0]]) / L
        hw = max(w * k, 0.35) / 2
        quad = np.array([poly[0] + nrm * hw, poly[1] + nrm * hw, poly[1] - nrm * hw, poly[0] - nrm * hw], np.float32)
        _blend_poly(img, quad, color, alpha, ss=6, blur=0.35)

def _arc(cx, cy, rx, ry, a0, a1, n=14):
    return [(cx + math.cos(a) * rx, cy + math.sin(a) * ry) for a in np.linspace(a0, a1, n)]

def gentle_eye(img, cx, cy, rx=7.0, ry=4.5, droop=0.0, seed=0):
    """半垂的眼皮：用周围的皮肤色（带一点纹理）盖住眼睛的上 60%，眼皮边缘一条深褐色的线（外侧略下垂），下面只露一线眼珠"""
    skin = _ring_color(img, cx, cy, rx * 1.3, rx * 2.3)
    rng = np.random.default_rng(seed)
    y_lid = cy - ry * 0.05
    # 盖住眼睛上部：多边形的下沿就是眼皮线
    lid = [(cx - rx * 1.2, y_lid + droop * 0.9), (cx - rx * 0.5, y_lid + ry * 0.12 + droop * 0.4), (cx + rx * 0.5, y_lid + ry * 0.12 - droop * 0.4), (cx + rx * 1.2, y_lid - droop * 0.9)]
    cover = np.array([(cx - rx * 1.6, cy - ry * 2.6), (cx + rx * 1.6, cy - ry * 2.6)] + lid[::-1], np.float32)
    h0, h1 = int(cy - ry * 3), int(cy + ry * 3); w0, w1 = int(cx - rx * 2), int(cx + rx * 2)
    patch = np.empty_like(img[h0:h1, w0:w1], dtype=np.float32)
    patch[:] = skin
    noise = cv2.GaussianBlur(rng.standard_normal(patch.shape[:2]).astype(np.float32), (0, 0), 0.9)[..., None] * 9
    patch += noise
    tmp = img.copy().astype(np.float32)
    tmp[h0:h1, w0:w1] = patch
    m = np.zeros(img.shape[:2], np.float32)
    cv2.fillPoly(m, [np.round(cover * 4).astype(np.int32) // 4], 1.0, lineType=cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 0.8)[..., None]
    img[:] = (img * (1 - m) + tmp * m).astype(img.dtype)
    ink = np.array([62, 50, 40], np.float32)
    lid_pts = [(cx - rx * 1.35, y_lid + droop * 1.1 - 0.3), (cx - rx * 0.6, y_lid + ry * 0.2 + droop * 0.4), (cx + rx * 0.2, y_lid + ry * 0.26), (cx + rx * 1.35, y_lid - droop * 1.1 + 0.2)]
    _stroke(img, lid_pts, 2.7, ink, 0.92)
    _stroke(img, [(p[0], p[1] - ry * 0.85) for p in lid_pts], 1.3, ink, 0.42)    # 双眼皮的褶
    _stroke(img, [(cx - rx * 0.8, cy + ry * 1.5), (cx, cy + ry * 1.9), (cx + rx * 0.8, cy + ry * 1.5)], 1.0, ink, 0.3)  # 眼袋


def kind_brow(img, cx, cy, sign, length=15.0, rise=2.6):
    """慈眉：从眉心向外侧微微下垂的弯线（sign=-1 左眉，+1 右眉）。先把原来凶相的眉毛抹平。"""
    reg = img[int(cy - 9):int(cy + 3), int(cx - length * 0.7):int(cx + length * 0.7)]
    sm = cv2.medianBlur(reg, 7)
    sm = cv2.GaussianBlur(sm, (0, 0), 1.2)
    m = np.zeros(reg.shape[:2], np.float32); cv2.ellipse(m, (reg.shape[1] // 2, reg.shape[0] // 2), (reg.shape[1] // 2 - 1, reg.shape[0] // 2 - 1), 0, 0, 360, 1, -1); m = cv2.GaussianBlur(m, (0, 0), 2.0)[..., None]
    reg[:] = (reg * (1 - m * 0.9) + sm * (m * 0.9)).astype(reg.dtype)
    col = np.array([66, 58, 50], np.float32)
    x0 = cx - sign * length * 0.15
    pts = [(x0 + sign * length * t, cy - rise * math.sin(math.pi * min(t * 1.1, 1.0)) + 2.0 * t * t) for t in np.linspace(0, 1, 9)]
    _stroke(img, pts, 3.4, col, 0.92)
    _stroke(img, [(p[0], p[1] + 1.8) for p in pts], 1.3, col, 0.5)

def smile(img, x0, x1, y, lift=2.2):
    ink = np.array([60, 52, 46], np.float32)
    pts = [(x0 + (x1 - x0) * t, y + lift * (1 - (2 * t - 1) ** 2) * -0.0 + (2 * t - 1) ** 2 * -lift) for t in np.linspace(0, 1, 9)]
    # 嘴线：两端上翘（y 小 = 高）
    pts = [(x0 + (x1 - x0) * t, y - lift * (2 * t - 1) ** 2 + lift) for t in np.linspace(0, 1, 9)]
    _stroke(img, pts, 1.3, ink, 0.55)

def crack(img, x, y, length=26.0, seed=0):
    """龟甲胸前的一道细裂纹：折线 + 一个小岔，旁边一线浅色高光"""
    rng = np.random.default_rng(seed)
    pts = [(x, y)]
    for k in range(5):
        pts.append((pts[-1][0] + rng.normal(0, 1.6), pts[-1][1] + length / 5))
    _stroke(img, [(p[0] + 0.9, p[1]) for p in pts], 1.0, np.array([225, 225, 220], np.float32), 0.35, taper=True)
    _stroke(img, pts, 1.3, np.array([48, 46, 48], np.float32), 0.85, taper=True)
    b = pts[2]
    _stroke(img, [b, (b[0] + 6, b[1] + 3), (b[0] + 10, b[1] + 8)], 0.9, np.array([48, 46, 48], np.float32), 0.7)

def retouch(img):
    img = img.copy()
    # 老龙（正面）：两只眼 (1395,181)、(1437,182)
    gentle_eye(img, 1395.0, 181.5, 7.5, 4.4, droop=-1.0, seed=1)
    gentle_eye(img, 1437.0, 182.0, 7.5, 4.4, droop=1.0, seed=2)
    kind_brow(img, 1393.0, 171.0, -1, 17, 2.4)
    kind_brow(img, 1440.0, 171.5, +1, 17, 2.4)
    smile(img, 1396, 1438, 228.5, 2.6)
    # 老龙（侧面）：眼 (1537.5,183)
    gentle_eye(img, 1537.5, 183.0, 7.0, 4.4, droop=0.8, seed=3)
    kind_brow(img, 1535.0, 173.0, +1, 16, 2.2)
    # 龟甲：胸前裂纹（正面 / 侧面）
    crack(img, 339.0, 437.0, 26, 1)
    crack(img, 452.0, 437.0, 24, 2)
    return img
