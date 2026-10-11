"""杂项：灭了的灯盘……"""
from ccommon import *
L = Canvas(440, 440)
lamp_disc(L, 220, 220, 190, seed=4, col=hexc('#c7c9ca'))
save_plate('lamp_dead', L, variants=('night',), gain=0.66, keep=0.12, ext='png')
