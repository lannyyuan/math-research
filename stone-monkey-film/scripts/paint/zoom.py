import sys, cv2, numpy as np, pathlib
SP = pathlib.Path('/home/user/math-research/stone-monkey-film/public/sprites')
OUT = '/tmp/claude-0/-home-user-math-research/747091a3-a05e-575b-b1ac-cb27e1adeb12/scratchpad/prev/'
n = sys.argv[1]; z = float(sys.argv[2]); y0, y1, x0, x1 = [int(v) for v in sys.argv[3:7]] if len(sys.argv) > 6 else (0, 9999, 0, 9999)
im = cv2.imread(str(SP / f'{n}.png'), cv2.IMREAD_UNCHANGED)
bg = np.full(im.shape[:2] + (3,), (68, 42, 30), np.uint8)
a = im[..., 3:4] / 255.
o = (im[..., :3] * a + bg * (1 - a)).astype(np.uint8)[y0:y1, x0:x1]
o = cv2.resize(o, None, fx=z, fy=z, interpolation=cv2.INTER_CUBIC)
cv2.imwrite(OUT + f'z_{n}.png', o)
print(OUT + f'z_{n}.png', o.shape)
