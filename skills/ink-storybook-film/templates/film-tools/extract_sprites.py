#!/usr/bin/env python3
"""把角色设定图（ref/character-sheet.png）里的 10 个造型抠成带透明通道的 PNG（public/sprites/）。

设定图是“白纸上的透明水彩”：纸色 ≈ 米白，角色边缘是水彩晕开的。做法：
  1. 估计纸色（空白区域的中位数），算每个像素和纸色在 Lab 空间里的距离 ΔE；
  2. ΔE 超过阈值的是“颜料”→ 二值蒙版；闭运算 + 填洞（脸上的高光、外套上的雪点、眼白都是“洞”，必须补成不透明）；
  3. 边缘按 ΔE 做柔和的 alpha（保留水彩的软边），再把颜色和纸色“解混”（去掉白边）；
  4. 去掉脚底的地面短线和别的角色的碎片，只留主体。
输出：<name>.png（RGBA，裁到主体外框 + 4px），同时写 sprites.json：每个精灵的脚底锚点（anchor）和尺寸。
"""
import json, pathlib, sys
import numpy as np, cv2
from scipy import ndimage as ndi
from skimage import color as skc

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHEET = ROOT / 'ref/character-sheet.png'
OUT = ROOT / 'public/sprites'
OUT.mkdir(parents=True, exist_ok=True)

# 每个造型在设定图里的外框 (x0, y0, x1, y1)，脚底线 y≈722
BOXES = {
    'hazel_front': (20, 205, 209, 735),
    'hazel_side': (209, 215, 392, 735),
    'bud_front': (390, 205, 587, 735),
    'bud_side': (587, 210, 750, 735),
    'bolts_front': (716, 455, 893, 735),
    'bolts_side': (897, 462, 995, 735),
    'comet_front': (984, 275, 1133, 735),
    'comet_side': (1133, 275, 1395, 735),
    'pebbles_front': (1338, 575, 1485, 735),
    'pebbles_side': (1492, 575, 1668, 735),
}
# 外框里混进来的邻居碎片（设定图坐标），抠之前先涂成纸色
EXCLUDE = {
    'bud_side': [(715, 560, 750, 735)],
    'bolts_front': [(716, 455, 736, 570)],
}
GROUND_Y = 724   # 地面线：脚底以下的全部丢掉


def extract(img, box, name):
    x0, y0, x1, y1 = box
    crop = img[y0:y1, x0:x1].astype(np.float32) / 255.0
    h, w = crop.shape[:2]
    for (ex0, ey0, ex1, ey1) in EXCLUDE.get(name, []):
        # 先用四周的纸色填平邻居的碎片
        crop[max(ey0 - y0, 0):ey1 - y0, max(ex0 - x0, 0):ex1 - x0] = np.median(np.concatenate([crop[:6].reshape(-1, 3), crop[:, :6].reshape(-1, 3)]), axis=0)
    # 纸色：外框四周 6px 的中位数（不含角色）
    border = np.concatenate([crop[:6].reshape(-1, 3), crop[:, :6].reshape(-1, 3), crop[:, -6:].reshape(-1, 3)])
    paper = np.median(border, axis=0)
    lab = skc.rgb2lab(crop)
    lab_p = skc.rgb2lab(paper.reshape(1, 1, 3))[0, 0]
    dE = np.sqrt(((lab - lab_p) ** 2).sum(-1))
    dEs = cv2.GaussianBlur(dE, (0, 0), 0.8)
    mask = dEs > 9.0
    # 地面线以下全部丢掉（地面短线、脚下的雪痕）
    gy = GROUND_Y - y0
    mask[gy:] = False
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)).astype(bool)
    # 填洞：脸上的高光、眼白、外套上的雪点是“洞”，要补成不透明；但腿之间、手臂和身体之间的空隙是真空，不能补。
    # 规则：小洞（<400px）一律填；大洞里平均 ΔE 明显高于纸（>3.0）说明里面有颜色（比如毛领的白毛），也填；纯纸色的大洞留空。
    holes = ndi.binary_fill_holes(mask) & ~mask
    hl, hn = ndi.label(holes)
    for i in range(1, hn + 1):
        reg = hl == i
        if reg.sum() < 400 or dEs[reg].mean() > 3.0:
            mask |= reg
    # 去碎片：只保留面积 ≥ 最大块 3% 的连通块（脚边的小雪点、别的角色的边角会被去掉）
    lab_cc, n = ndi.label(mask)
    if n:
        sizes = ndi.sum(mask, lab_cc, range(1, n + 1))
        main = int(np.argmax(sizes)) + 1
        # 只留最大的主体，以及离主体 14px 以内的小碎块（散开的卷发、天线、鹿角尖……）；别的角色的边角会被去掉
        dist = ndi.distance_transform_edt(lab_cc != main)
        keep = [main] + [i + 1 for i in range(n) if i + 1 != main and sizes[i] >= 6 and dist[lab_cc == i + 1].min() <= 4]
        mask = np.isin(lab_cc, keep)
    # 软边：核心（腐蚀 2px）完全不透明，边缘按 ΔE 渐变
    core = cv2.erode(mask.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=1).astype(bool)
    near = cv2.dilate(mask.astype(np.uint8), np.ones((5, 5), np.uint8), iterations=1).astype(bool)
    soft = np.clip((dEs - 6.0) / 12.0, 0, 1)
    alpha = np.where(core, 1.0, soft * near)
    alpha = np.clip((alpha - 0.12) / 0.88, 0, 1)
    alpha = cv2.GaussianBlur(alpha.astype(np.float32), (0, 0), 0.6)
    alpha[gy:] = 0
    # 解混：pixel = a*C + (1-a)*paper → C = (pixel - (1-a)*paper)/a
    a3 = alpha[..., None]
    C = np.where(a3 > 0.04, (crop - (1 - a3) * paper) / np.maximum(a3, 0.04), crop)
    C = np.clip(C, 0, 1)
    # 半透明边缘处颜色向最近的实心像素取色，避免白边
    inner = alpha > 0.9
    idx = ndi.distance_transform_edt(~inner, return_distances=False, return_indices=True)
    Cn = C[idx[0], idx[1]]
    edge = (alpha < 0.9) & (alpha > 0.0)
    C = np.where(edge[..., None], 0.25 * C + 0.75 * Cn, C)
    # 裁到外框
    ys, xs = np.where(alpha > 0.02)
    ya, yb, xa, xb = max(ys.min() - 4, 0), min(ys.max() + 5, h), max(xs.min() - 4, 0), min(xs.max() + 5, w)
    rgba = np.dstack([C, alpha])[ya:yb, xa:xb]
    out = (rgba * 255 + 0.5).astype(np.uint8)
    cv2.imwrite(str(OUT / f'{name}.png'), cv2.cvtColor(out, cv2.COLOR_RGBA2BGRA))
    # 锚点：脚底中心（以裁后图像为坐标）。脚底 = 最下面的不透明行
    bottom = np.where(alpha[ya:yb].max(axis=1) > 0.3)[0].max()
    cols = np.where(alpha[ya:yb][max(bottom - 8, 0):bottom + 1].max(axis=0)[xa:xb] > 0.3)[0] if False else np.where(alpha[ya:yb, xa:xb][max(bottom - 8, 0):bottom + 1].max(axis=0) > 0.3)[0]
    ax = float((cols.min() + cols.max()) / 2) if len(cols) else (xb - xa) / 2
    return {'w': int(xb - xa), 'h': int(yb - ya), 'ax': round(ax, 1), 'ay': int(bottom), 'src': [x0 + int(xa), y0 + int(ya)]}


def main():
    img = cv2.cvtColor(cv2.imread(str(SHEET)), cv2.COLOR_BGR2RGB)
    meta = {}
    for name, box in BOXES.items():
        meta[name] = extract(img, box, name)
        print(name, meta[name])
    (OUT / 'sprites.json').write_text(json.dumps(meta, indent=1))


if __name__ == '__main__':
    main()
