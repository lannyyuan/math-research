#!/usr/bin/env python3
"""从设定图抠出来的精灵再派生几个状态：
   · bolts_front_off / bolts_side_off：Bolts 眼睛熄灭（拆了电池以后，一直到圣诞节早上）
   · pebbles_front_top：只有刺猬露出来的上半身（第一次从落叶堆里探出头时，还没有毛线帽）
"""
import pathlib
import numpy as np, cv2

ROOT = pathlib.Path(__file__).resolve().parent.parent
SP = ROOT / 'public/sprites'


def load(n):
    return cv2.cvtColor(cv2.imread(str(SP / f'{n}.png'), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA).astype(np.float32) / 255


def save(n, a):
    cv2.imwrite(str(SP / f'{n}.png'), cv2.cvtColor((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), cv2.COLOR_RGBA2BGRA))


def eyes_off(name, box):
    im = load(name)
    R, G, B, A = im[..., 0], im[..., 1], im[..., 2], im[..., 3]
    m = ((A > 0.3) & (R > 0.72) & (G > 0.52) & (B < 0.55) & (R - B > 0.28)).astype(np.uint8)
    x0, y0, x1, y1 = box
    box_m = np.zeros_like(m); box_m[y0:y1, x0:x1] = 1
    m = cv2.dilate(m * box_m, np.ones((5, 5), np.uint8)).astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 1.0)
    lum = (R + G + B) / 3
    dark = np.stack([0.30 + 0.35 * lum, 0.32 + 0.35 * lum, 0.37 + 0.33 * lum], -1) * 0.8
    out = im.copy()
    out[..., :3] = im[..., :3] * (1 - m[..., None]) + dark * m[..., None]
    save(name + '_off', out)
    return int(m.sum())


def pebbles_top():
    im = load('pebbles_front')
    h = im.shape[0]
    y = np.arange(h, dtype=np.float32)[:, None]
    fade = np.clip((86 - y) / 8.0, 0, 1)   # y>=86 全透明，84~86 渐隐
    out = im.copy()
    out[..., 3] *= fade
    save('pebbles_front_top', out)


if __name__ == '__main__':
    print('bolts front eye px', eyes_off('bolts_front', (52, 50, 128, 90)), 'side', eyes_off('bolts_side', (0, 48, 40, 86)))
    pebbles_top()
