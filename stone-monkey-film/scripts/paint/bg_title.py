"""片头：灰色的灯盘 + 远山。夜色。"""
from ccommon import *
W, H = 1920, 1080
S = sky(W, H, hexc('#6b7a8c'), hexc('#8d9aa6'), hexc('#bcc3c6'), seed=21, horizon=0.9, cloud=0.55, scale=380)
lamp_disc(S, 960, 300, 262, seed=4)
mist(S, 0, W, 640, 70, seed=2, op=0.5)
r1 = ridge_y(W, 905, 190, 5, rough=0.5, scale=520)
mountain(S, r1, 960, N['far3'], N['far2'], seed=1, tex=0.5, tex_op=0.25, snow=N['snow'], snow_from=0.14, haze=0.25)
mist(S, 0, W, 925, 50, seed=3, op=0.6)
r2 = ridge_y(W, 985, 110, 15, rough=0.5, scale=380)
mountain(S, r2, 1080, N['mid3'], N['mid2'], seed=2, tex=0.8, tex_op=0.3)
save_plate('title_sky', S, variants=('night',), gain=0.62, keep=0.12)
