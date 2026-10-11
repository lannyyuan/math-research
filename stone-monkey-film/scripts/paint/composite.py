"""把一组分层的画板（far/mid/near）叠起来，按变体存一张预览：python3 composite.py village night,day [scale=0.4]"""
import sys, json, pathlib
import numpy as np, cv2
ROOT = pathlib.Path(__file__).resolve().parents[2]
BG = ROOT / 'public/bg'
PREV = pathlib.Path('/tmp/claude-0/-home-user-math-research/747091a3-a05e-575b-b1ac-cb27e1adeb12/scratchpad/prev')
name = sys.argv[1]; variants = sys.argv[2].split(','); scale = float(sys.argv[3]) if len(sys.argv) > 3 else 0.4
mf = json.loads((BG / 'manifest.json').read_text())
layers = [k for k in (f'{name}_far', f'{name}_mid', f'{name}_near', f'{name}_fg') if k in mf]
rows = []
for v in variants:
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
    out = (comp[..., :3] * 255).astype(np.uint8)
    out = cv2.resize(out, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    rows.append(out)
cv2.imwrite(str(PREV / f'{name}_comp.jpg'), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 90])
print('->', PREV / f'{name}_comp.jpg', np.vstack(rows).shape)
