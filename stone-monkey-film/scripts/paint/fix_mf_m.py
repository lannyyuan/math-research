"""Agent M 的画板在 manifest.json 里丢了条目时补回来（根据 public/bg 里实际存在的文件）。python3 fix_mf_m.py"""
import json, os, tempfile, pathlib
import cv2
ROOT = pathlib.Path(__file__).resolve().parents[2]
BG = ROOT / 'public/bg'
NAMES = ['hill_far', 'hill_mid', 'hill_near', 'frost_forest_far', 'frost_forest_mid', 'frost_forest_near',
         'snow_hut_far', 'snow_hut_mid', 'snow_hut_near', 'snow_hut_near_clear', 'hut_in_far', 'hut_in_near', 'hut_in_clean',
         'grassland_far', 'grassland_mid', 'grassland_near', 'kitchen_far', 'kitchen_near']
mf = json.loads((BG / 'manifest.json').read_text())
changed = False
for n in NAMES:
    vs = [v for v in ('night', 'lit', 'day', 'dawn') if (BG / f'{n}_{v}.png').exists() or (BG / f'{n}_{v}.jpg').exists()]
    if not vs:
        continue
    ext = 'jpg' if (BG / f'{n}_{vs[0]}.jpg').exists() else 'png'
    im = cv2.imread(str(BG / f'{n}_{vs[0]}.{ext}'), cv2.IMREAD_UNCHANGED)
    h, w = im.shape[:2]
    ent = {'variants': vs, 'ext': ext, 'w': w, 'h': h}
    if mf.get(n) != ent:
        mf[n] = ent
        changed = True
        print('fixed', n, ent)
if changed:
    fd, tmp = tempfile.mkstemp(dir=str(BG), suffix='.json')
    with os.fdopen(fd, 'w') as f:
        f.write(json.dumps(mf, indent=1))
    os.replace(tmp, BG / 'manifest.json')
print('ok', [n for n in NAMES if n in mf])
