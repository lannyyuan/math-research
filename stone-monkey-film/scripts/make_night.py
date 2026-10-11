#!/usr/bin/env python3
"""给 public/sprites/ 里的每个精灵生成夜色版 <name>_night.png（靛蓝色带），并把 night 标记写进 sprites.json。
可以重复运行（只处理缺夜色版或原图更新过的精灵）；新画的角色/道具放进 public/sprites/ 并在 sprites.json 里登记 w/h/ax/ay 后运行它即可。
  python3 -I scripts/make_night.py [--all]
"""
import json, pathlib, sys
import numpy as np, cv2
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts/paint'))
import grade
SP = ROOT / 'public/sprites'
meta = json.loads((SP / 'sprites.json').read_text())
force = '--all' in sys.argv


def load(n):
    im = cv2.cvtColor(cv2.imread(str(SP / f'{n}.png'), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA).astype(np.float32) / 255.0
    return im[..., :3], im[..., 3]


KG = {  # name: (keep, gain)；默认角色 (0.5, 0.8)
    'fire': None, 'pearl': None, 'needle': (0.9, 0.82), 'bell': (0.45, 0.72),
}
for n, m in list(meta.items()):
    if m.get('night') is False or n.endswith('_night'):
        continue
    dst = SP / f'{n}_night.png'
    if dst.exists() and not force and dst.stat().st_mtime >= (SP / f'{n}.png').stat().st_mtime:
        continue
    kg = KG.get(n, (0.5, 0.8))
    if kg is None:
        m['night'] = False
        continue
    rgb, a = load(n)
    out = grade.night(rgb, keep=kg[0], gain=kg[1])
    # 夜里的人和物：压暗但保留细节
    o = (np.clip(np.dstack([out, a]), 0, 1) * 255 + 0.5).astype(np.uint8)
    cv2.imwrite(str(SP / f'{n}_night.png'), cv2.cvtColor(o, cv2.COLOR_RGBA2BGRA))
    m['night'] = True
(SP / 'sprites.json').write_text(json.dumps(meta, indent=1))
print(len(meta), 'sprites')
