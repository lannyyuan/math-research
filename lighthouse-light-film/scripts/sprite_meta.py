#!/usr/bin/env python3
"""给 public/sprites/ 里所有 PNG 写 sprites.json：尺寸 + 脚底锚点。派生出来的层（帽子、棒球帽、熄灯的 Bolts……）沿用原精灵的锚点。"""
import json, pathlib
from PIL import Image
SP = pathlib.Path(__file__).resolve().parent.parent / 'public/sprites'
meta = json.loads((SP / 'sprites.json').read_text())
BASE = {'bud_front_bare': 'bud_front', 'bud_side_bare': 'bud_side', 'bud_hat_front': 'bud_front', 'bud_hat_side': 'bud_side', 'bud_cap_front': 'bud_front', 'bud_cap_side': 'bud_side',
        'bolts_front_off': 'bolts_front', 'bolts_side_off': 'bolts_side', 'pebbles_front_top': 'pebbles_front'}
for p in sorted(SP.glob('*.png')):
    n = p.stem
    w, h = Image.open(p).size
    b = meta.get(BASE.get(n, n))
    meta[n] = {'w': w, 'h': h, 'ax': b['ax'], 'ay': b['ay']}
(SP / 'sprites.json').write_text(json.dumps(meta, indent=1))
print(len(meta), 'sprites')
