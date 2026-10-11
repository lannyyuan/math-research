"""看图工具：python3 crop.py <name> <variant> x0 y0 [w h] [scale]   把各层叠起来，裁一块 1:1（或缩放）存到预览目录。"""
import sys, json, pathlib
import numpy as np, cv2
ROOT = pathlib.Path(__file__).resolve().parents[2]
BG = ROOT / 'public/bg'
PREV = pathlib.Path('/tmp/claude-0/-home-user-math-research/747091a3-a05e-575b-b1ac-cb27e1adeb12/scratchpad/prev')
name, v = sys.argv[1], sys.argv[2]
x0, y0 = int(sys.argv[3]), int(sys.argv[4])
w = int(sys.argv[5]) if len(sys.argv) > 5 else 1000
h = int(sys.argv[6]) if len(sys.argv) > 6 else 600
sc = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
extra = sys.argv[8].split(',') if len(sys.argv) > 8 else []
mf = json.loads((BG / 'manifest.json').read_text())
layers = [k for k in (f'{name}_far', f'{name}_mid', f'{name}_near', f'{name}_fg') if k in mf]
layers += [k for k in extra if k in mf]
import os
if os.environ.get('NEAR'):
    layers = [os.environ['NEAR'] if k == f'{name}_near' else k for k in layers]
if extra and extra[0].startswith('-'):   # 例如 -near：把 near 换成别的
    pass
comp = None
for k in layers:
    info = mf[k]
    vv = v if v in info['variants'] else 'night'
    im = cv2.imread(str(BG / f'{k}_{vv}.{info["ext"]}'), cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    if im.shape[2] == 3:
        im = np.dstack([im, np.ones(im.shape[:2], np.float32)])
    if comp is None:
        comp = im.copy()
    else:
        a = im[..., 3:4]
        comp[..., :3] = im[..., :3] * a + comp[..., :3] * (1 - a)
        comp[..., 3:4] = a + comp[..., 3:4] * (1 - a)
out = (comp[..., :3] * 255).astype(np.uint8)[y0:y0 + h, x0:x0 + w]
if sc != 1.0:
    out = cv2.resize(out, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
p = PREV / f'{name}{os.environ.get("TAG", "")}_{v}_{x0}_{y0}.png'
cv2.imwrite(str(p), out)
print(p)
