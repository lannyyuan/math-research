#!/usr/bin/env python3
"""把角色与道具设定表（ref/character-sheet.png）抠成带透明通道的 PNG（public/sprites/）。

设定表是“宣纸色底上的透明水彩”。做法（沿用 ink-storybook-film 技能）：
  1. 纸色 = 四角的中位数；算每个像素和纸色在 Lab 空间的距离 ΔE；
  2. ΔE 超过阈值 → “颜料”→ 二值蒙版；闭运算 + 填洞（白发、鱼肚、眼白都是“洞”，要补成不透明）；
  3. 边缘按 ΔE 做柔和 alpha（保留水彩软边），颜色和纸色“解混”（去白边）；
  4. 去碎片，只留主体（和离主体很近的小碎片：胡须、龙须、水花）。
输出 <name>.png + sprites.json（脚底中心锚点 + 尺寸）。
"""
import json, pathlib, sys
import numpy as np, cv2
from scipy import ndimage as ndi
from skimage import color as skc

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHEET = ROOT / 'ref/character-sheet.png'
OUT = ROOT / 'public/sprites'
OUT.mkdir(parents=True, exist_ok=True)

# name: (x0, y0, x1, y1, ground_y or None, near_px)  坐标是设定表像素
BOXES = {
    'shiwa_front': (8, 128, 162, 512, 507, 4),
    'shiwa_side': (162, 128, 292, 512, 507, 4),
    'houzi_front': (282, 350, 398, 512, 507, 4),
    'houzi_side': (399, 350, 502, 512, 507, 4),
    'nainai_front': (500, 112, 646, 512, 507, 4),
    'nainai_side': (646, 112, 780, 512, 507, 4),
    'fish_front': (766, 98, 928, 506, None, 12),
    'fish_side': (922, 98, 1048, 506, None, 12),
    'turtle_front': (1049, 225, 1258, 512, 507, 4),
    'turtle_side': (1236, 245, 1398, 512, 507, 4),
    'dragon_front': (1312, 28, 1496, 512, None, 30),
    'dragon_side': (1486, 28, 1668, 512, None, 30),
    'bell': (380, 566, 690, 858, None, 8),
    'fire': (704, 548, 952, 858, None, 8),
    'drum': (974, 580, 1346, 872, None, 10),
    'needle': (1356, 570, 1655, 858, None, 8),
    'pearl_stone': (26, 556, 372, 858, None, 8),
}


# 外框里混进来的邻居碎片（设定表坐标），抠之前涂成纸色
EXCLUDE = {
    'turtle_side': [(1352, 245, 1400, 350), (1368, 340, 1400, 445), (1236, 340, 1262, 512)],
    'turtle_front': [(1049, 225, 1053, 512)],
    'dragon_side': [(1486, 300, 1514, 512)],
}


# 先抠出来的精灵所占的像素也涂成纸色（邻居挨得很近：老龟的背和老龙的须）
EXCL_BY = {'dragon_front': ['turtle_side'], 'dragon_side': ['dragon_front']}
FULL = {}
FADE = {'dragon_front': [('right', 18)], 'dragon_side': [('left', 10)]}


def extract(img, name, box, ground, near_px):
    x0, y0, x1, y1 = box
    crop = img[y0:y1, x0:x1].astype(np.float32) / 255.0
    h, w = crop.shape[:2]
    paper = np.array([249, 247, 242], np.float32) / 255.0
    for (ex0, ey0, ex1, ey1) in EXCLUDE.get(name, []):
        crop[max(ey0 - y0, 0):max(ey1 - y0, 0), max(ex0 - x0, 0):max(ex1 - x0, 0)] = paper
    for other in EXCL_BY.get(name, []):
        om = cv2.dilate((FULL[other][y0:y1, x0:x1] > 0.02).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
        crop[om] = paper
    lab = skc.rgb2lab(crop)
    lab_p = skc.rgb2lab(paper.reshape(1, 1, 3))[0, 0]
    dE = np.sqrt(((lab - lab_p) ** 2).sum(-1))
    dEs = cv2.GaussianBlur(dE, (0, 0), 0.8)
    mask = dEs > 8.0
    if ground:
        mask[ground - y0:] = False
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)).astype(bool)
    holes = ndi.binary_fill_holes(mask) & ~mask
    hl, hn = ndi.label(holes)
    for i in range(1, hn + 1):
        reg = hl == i
        if reg.sum() < 500 or dEs[reg].mean() > 2.5:
            mask |= reg
    lab_cc, n = ndi.label(mask)
    if n:
        sizes = ndi.sum(mask, lab_cc, range(1, n + 1))
        main = int(np.argmax(sizes)) + 1
        dist = ndi.distance_transform_edt(lab_cc != main)
        keep = [main] + [i + 1 for i in range(n) if i + 1 != main and sizes[i] >= 6 and dist[lab_cc == i + 1].min() <= near_px]
        mask = np.isin(lab_cc, keep)
    core = cv2.erode(mask.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=1).astype(bool)
    near = cv2.dilate(mask.astype(np.uint8), np.ones((5, 5), np.uint8), iterations=1).astype(bool)
    soft = np.clip((dEs - 5.0) / 12.0, 0, 1)
    alpha = np.where(core, 1.0, soft * near)
    alpha = np.clip((alpha - 0.10) / 0.90, 0, 1)
    alpha = cv2.GaussianBlur(alpha.astype(np.float32), (0, 0), 0.6)
    if ground:
        alpha[ground - y0:] = 0
    for side, px in FADE.get(name, []):   # 被相邻精灵切掉的那一边：用渐隐代替硬边
        ramp = np.clip(np.arange(px, dtype=np.float32) / px, 0, 1)
        if side == 'right': alpha[:, w - px:] *= ramp[::-1][None, :]
        if side == 'left': alpha[:, :px] *= ramp[None, :]
    a3 = alpha[..., None]
    C = np.where(a3 > 0.04, (crop - (1 - a3) * paper) / np.maximum(a3, 0.04), crop)
    C = np.clip(C, 0, 1)
    inner = alpha > 0.9
    idx = ndi.distance_transform_edt(~inner, return_distances=False, return_indices=True)
    Cn = C[idx[0], idx[1]]
    edge = (alpha < 0.9) & (alpha > 0.0)
    C = np.where(edge[..., None], 0.25 * C + 0.75 * Cn, C)
    ys, xs = np.where(alpha > 0.02)
    ya, yb, xa, xb = max(ys.min() - 3, 0), min(ys.max() + 4, h), max(xs.min() - 3, 0), min(xs.max() + 4, w)
    full = np.zeros(img.shape[:2], np.float32)
    full[y0:y1, x0:x1] = alpha
    FULL[name] = full
    rgba = np.dstack([C, alpha])[ya:yb, xa:xb]
    out = (rgba * 255 + 0.5).astype(np.uint8)
    cv2.imwrite(str(OUT / f'{name}.png'), cv2.cvtColor(out, cv2.COLOR_RGBA2BGRA))
    bottom = np.where(alpha[ya:yb].max(axis=1) > 0.3)[0].max()
    cols = np.where(alpha[ya:yb, xa:xb][max(bottom - 8, 0):bottom + 1].max(axis=0) > 0.3)[0]
    ax = float((cols.min() + cols.max()) / 2) if len(cols) else (xb - xa) / 2
    return {'w': int(xb - xa), 'h': int(yb - ya), 'ax': round(ax, 1), 'ay': int(bottom)}


def main():
    img = cv2.cvtColor(cv2.imread(str(SHEET)), cv2.COLOR_BGR2RGB)
    meta = {}
    only = sys.argv[1:]
    for name, (x0, y0, x1, y1, g, npx) in BOXES.items():
        if only and name not in only and not any(name in EXCL_BY.get(o, []) for o in only):
            continue
        meta[name] = extract(img, name, (x0, y0, x1, y1), g, npx)
        if name in ('drum', 'bell', 'fire', 'needle', 'pearl_stone'):   # 道具：锚点 = 外框底边中点
            meta[name]['ax'] = round(meta[name]['w'] / 2, 1)
        print(name, meta[name])
    mp = OUT / 'sprites.json'
    old = json.loads(mp.read_text()) if mp.exists() else {}
    old.update(meta)
    mp.write_text(json.dumps(old, indent=1))


if __name__ == '__main__':
    main()
