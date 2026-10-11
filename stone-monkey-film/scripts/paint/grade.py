"""调色：把“中性淡彩”的画布变成 夜色（靛蓝 + 纸白 + 墨）/ 光里的柔彩 / 晨光。
夜色用“亮度 → 色带”的渐变映射，保证画面只落在设定的色板里：深夜 #121A2E、靛蓝 #1E2A44、灰蓝 #5A6B86、纸白 #EFE8D8、墨 #2A2622。"""
import numpy as np
from pt import hexc, F

NIGHT_STOPS = [(0.00, '#080c18'), (0.14, '#121A2E'), (0.34, '#1E2A44'), (0.58, '#46587a'), (0.74, '#5A6B86'), (0.90, '#aeb7c4'), (1.00, '#EFE8D8')]
DAWN_STOPS = [(0.00, '#2A2622'), (0.25, '#5b5a62'), (0.55, '#a39a9a'), (0.80, '#e6d2c0'), (1.00, '#faf1df')]


def ramp(lum, stops):
    xs = np.array([s[0] for s in stops], F)
    cs = np.stack([hexc(s[1]) for s in stops]).astype(F)
    out = np.empty(lum.shape + (3,), F)
    for c in range(3):
        out[..., c] = np.interp(lum, xs, cs[:, c])
    return out


def lum_of(rgb):
    return rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114


def night(rgb, keep=0.22, gamma=1.0, gain=1.0, lift=0.0):
    """夜色：保留一点原色的色相差（keep），其余按亮度落进靛蓝色带。gain<1 整体更暗。"""
    l = np.clip(lum_of(rgb) ** gamma * gain + lift, 0, 1)
    base = ramp(l, NIGHT_STOPS)
    chroma = rgb - lum_of(rgb)[..., None]
    return np.clip(base + chroma * keep * (0.35 + 0.65 * l[..., None]), 0, 1).astype(F)


def lit(rgb, sat=0.78, gain=1.04, tint=(1.0, 0.985, 0.96)):
    """被光照到的地方：柔和、降了饱和度的自然色（灰绿、土黄、石灰），不抢光源。"""
    l = lum_of(rgb)[..., None]
    out = l + (rgb - l) * sat
    return np.clip(out * np.asarray(tint, F) * gain, 0, 1).astype(F)


def dawn(rgb, glow=None, sat=0.85):
    """晨光：偏暖的柔彩。"""
    l = lum_of(rgb)[..., None]
    out = l + (rgb - l) * sat
    out = out * np.array([1.04, 1.0, 0.95], F)
    return np.clip(out, 0, 1).astype(F)


def apply(L, fn, **kw):
    """对画布的 RGB 原地调色（不动 alpha）。返回一个新画布。"""
    from pt import Canvas
    out = Canvas(L.w, L.h)
    out.rgb = fn(L.rgb, **kw)
    out.a = L.a.copy()
    return out
