import sys, pathlib, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from cn import *
import grade
W, H = 2900, 1080
t0 = time.time()
S = sky(W, H, hexc("#a3b2bd"), hexc("#cfd6d6"), hexc("#efe8d8"), seed=3, horizon=0.82, cloud=0.5)
print('sky', time.time() - t0)
r1 = ridge_y(W, 640, 330, 11, rough=0.5, scale=620)
mountain(S, r1, 700, N['far2'], N['far1'], seed=1, tex=0.5, tex_op=0.22, snow=N['snow'], snow_from=0.22, haze=0.35)
mist(S, 0, W, 640, 70, seed=2, op=0.65)
r2 = ridge_y(W, 720, 230, 21, rough=0.55, scale=420)
mountain(S, r2, 800, N['mid2'], N['mid1'], seed=2, tex=0.8, tex_op=0.3, haze=0.2)
mist(S, 0, W, 740, 80, seed=5, op=0.6)
r3 = ridge_y(W, 800, 150, 31, rough=0.5, scale=300)
mountain(S, r3, 880, N['near1'], N['near2'], seed=3, tex=1.0, tex_op=0.34)
for i in range(18):
    pine(S, 200 + i * 150 + (i * 37) % 90, 800 + (i % 3) * 14, 90 + (i * 53) % 70, seed=i)
print('painted', time.time() - t0)
S.save('/tmp/test_day.png')
G = grade.apply(S, grade.night)
G.save('/tmp/test_night.png')
import cv2
for n in ('day', 'night'):
    im = cv2.imread(f'/tmp/test_{n}.png'); cv2.imwrite(f'/tmp/test_{n}_s.jpg', cv2.resize(im, (1450, 540), interpolation=cv2.INTER_AREA))
