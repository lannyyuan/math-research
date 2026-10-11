"""把精灵摆到靛蓝底上并排看（和石娃/奶奶比大小）。
python3 prev_people.py out.png name1 name2 ...  [--night] [--zoom=1.0] [--ref] [--bg=#1E2A44]
--ref：在最左边加上石娃和奶奶（front）。"""
import sys, json, pathlib
import numpy as np, cv2
ROOT = pathlib.Path(__file__).resolve().parents[2]
SP = ROOT / 'public/sprites'
SCR = pathlib.Path('/tmp/claude-0/-home-user-math-research/747091a3-a05e-575b-b1ac-cb27e1adeb12/scratchpad/prev')


def load(n, night=False):
    f = SP / (f'{n}_night.png' if night and (SP / f'{n}_night.png').exists() else f'{n}.png')
    im = cv2.imread(str(f), cv2.IMREAD_UNCHANGED)
    return cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA).astype(np.float32) / 255


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    opts = [a for a in sys.argv[1:] if a.startswith('--')]
    out = args[0]
    names = args[1:]
    night = '--night' in opts
    zoom = 1.0
    bgc = '#1E2A44'
    if night:
        bgc = '#1E2A44'
    for o in opts:
        if o.startswith('--zoom='):
            zoom = float(o.split('=')[1])
        if o.startswith('--bg='):
            bgc = o.split('=')[1]
    if '--ref' in opts:
        names = ['shiwa_front', 'nainai_front'] + names
    meta = json.loads((SP / 'sprites.json').read_text())
    items = []
    for n in names:
        im = load(n, night)
        m = meta.get(n)
        ax, ay = (m['ax'], m['ay']) if m else (im.shape[1] / 2, im.shape[0] - 4)
        items.append((n, im, ax, ay))
    gap = 40
    Hmax = max(it[1].shape[0] for it in items)
    W = int(sum(it[1].shape[1] for it in items) + gap * (len(items) + 1))
    Hc = Hmax + 60
    bg = np.array([int(bgc[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
    canvas = np.ones((Hc, W, 3), np.float32) * bg
    # 地面线
    gy = Hc - 30
    canvas[gy:gy + 1] = canvas[gy:gy + 1] * 0.6 + 0.4 * np.array([0.35, 0.42, 0.55], np.float32)
    x = gap
    for n, im, ax, ay in items:
        h, w = im.shape[:2]
        x0, y0 = int(x), int(gy - ay)
        a = im[..., 3:4]
        ys, xs = max(y0, 0), x0
        canvas[ys:y0 + h, x0:x0 + w] = im[ys - y0:, :, :3] * a[ys - y0:] + canvas[ys:y0 + h, x0:x0 + w] * (1 - a[ys - y0:])
        x += w + gap
    o = (np.clip(canvas, 0, 1) * 255).astype(np.uint8)
    if zoom != 1.0:
        o = cv2.resize(o, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_CUBIC if zoom > 1 else cv2.INTER_AREA)
    cv2.imwrite(str(SCR / out) if not out.startswith('/') else out, cv2.cvtColor(o, cv2.COLOR_RGB2BGR))
    print('->', out, o.shape)


main()
