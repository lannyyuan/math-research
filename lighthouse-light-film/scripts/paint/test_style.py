import sys, time, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from world import *
from PIL import Image
W, H = 1920, 1080
t0 = time.time()
L = Canvas(W, H, bg=(0, 0, 0))
L.rgb[:] = sky(W, H, 'night', seed=4, horizon=0.55)
flakes(L, 220, 5, region=(0, 0, W, 520), op=0.85, sparkle=0.05)
# 远山 + 海
hills(L, ridge_pts(0, 1400, 560, 60, 3, 30), 640, hexc('#31466f'), snow=True, seed=2, op=0.95)
sea(L, 560, 760, seed=3, lit_x=1500, lit_op=0.0)
# 近处雪坡
top = np.array([[0, 700], [300, 690], [700, 740], [1100, 800], [1500, 850], [1920, 900]], F)
snow_ground(L, catmull(top, 10), 1100, seed=5)
for i, x in enumerate([60, 260, 430]): post(L, x, 800 + i * 5, 110 + i * 10, 34, seed=i)
bush(L, 140, 860, 170, 1.0, 8, seed=11)
bush(L, 1650, 940, 150, 1.0, 7, seed=12)
rocks(L, 380, 1000, 260, 90, seed=3)
rocks(L, 1780, 1010, 240, 90, seed=4)
print('paint', round(time.time() - t0, 1), 's')
img = Image.fromarray((np.clip(L.flat(), 0, 1) * 255).astype(np.uint8))
meta = json.load(open(pathlib.Path(__file__).parents[2] / 'public/sprites/sprites.json'))
sp = pathlib.Path(__file__).parents[2] / 'public/sprites'
def put(name, x, y, h):
    im = Image.open(sp / f'{name}.png'); m = meta[name]
    s = h / m['ay']; im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    img.paste(im, (int(x - m['ax'] * s), int(y - m['ay'] * s)), im)
put('hazel_side', 900, 960, 360); put('bud_side', 1060, 970, 360); put('bolts_side', 1180, 975, 150); put('comet_side', 1330, 985, 260)
img.save('/tmp/claude-0/-home-user-math-research/747091a3-a05e-575b-b1ac-cb27e1adeb12/scratchpad/ref/test_style.png')
