#!/usr/bin/env python3
"""字幕会不会超出画面：用真实字体（Andika）量每条字幕每一行的宽度，加上左右内边距，必须在 1920 宽的画面内留出 ≥ 120 px 边距；
行数 ≤ 2；底部不越界。和 Subtitle.tsx 的字号 / 字距 / 内边距保持一致。"""
import json, pathlib, sys, re
from fontTools.ttLib import TTFont
from PIL import ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
tmp = pathlib.Path('/tmp/andika-400.ttf')
if not tmp.exists():
    f = TTFont(ROOT / 'public/fonts/andika-latin-400-normal.woff2'); f.flavor = None; f.save(tmp)
tl = json.loads((ROOT / 'src/timeline.json').read_text())

def wrap(text, mx=36):
    parts = text.split('\n')
    if len(parts) > 1: return parts
    if len(text) <= mx: return [text]
    best, bs = -1, 1e9
    for i in range(4, len(text) - 3):
        if text[i] != ' ': continue
        sc = abs(i - len(text) / 2) - (6 if re.match(r'[,.:;!?]', text[i - 1]) else 0)
        if sc < bs: bs, best = sc, i
    return [text] if best < 0 else [text[:best], text[best + 1:]]

worst = (0, '')
bad = 0
for sc in tl['scenes']:
    for c in sc['cues']:
        lines = wrap(c['text'])
        size = 60 if len(lines) > 1 else 68
        font = ImageFont.truetype(str(tmp), size)
        w = max(font.getlength(l) + 0.6 * len(l) for l in lines) + 92
        h = len(lines) * size * 1.28 + 32
        bottom = 44 if len(lines) > 1 else 64
        if w > worst[0]: worst = (w, c['text'])
        if w > 1920 - 240 or len(lines) > 2 or bottom + h > 1080:
            bad += 1; print('✗', sc['id'], round(w), len(lines), c['text'])
print(f'最宽的字幕框 {worst[0]:.0f}px（画面 1920px，左右各留 {(1920 - worst[0]) / 2:.0f}px）: 「{worst[1]}」')
print('全部在画面内 ✓' if not bad else f'{bad} 条有问题')
sys.exit(1 if bad else 0)
