import sys, json, numpy as np
from PIL import Image
out={}
S=8  # downsample factor (px)
for name in sys.argv[1:]:
    im=Image.open(f'img/{name}.png').convert('RGB')
    a=np.asarray(im).astype(int); H,W,_=a.shape
    # card colour = most common colour in the central band of the card
    q=(a[150:1350:4,150:2400:4]//4).reshape(-1,3)
    vals,cnt=np.unique(q,axis=0,return_counts=True); card=vals[cnt.argmax()]*4+2
    free=(np.abs(a-card).sum(2)<14)
    # downsample: a cell is free only if all its pixels are free
    h,w=H//S,W//S
    f=free[:h*S,:w*S].reshape(h,S,w,S).all(axis=(1,3))
    # summed-area table for fast all-free rectangle test
    sat=np.zeros((h+1,w+1),int); sat[1:,1:]=(~f).cumsum(0).cumsum(1)
    def ok(y,x,hh,ww): return sat[y+hh,x+ww]-sat[y,x+ww]-sat[y+hh,x]+sat[y,x]==0
    pad=int(40/S)  # keep 40px clear of artwork
    best=None
    for ww in range(w,0,-2):
        hh=int(round(ww*9/16))
        HH,WW=hh+2*pad,ww+2*pad
        if HH>h or WW>w: continue
        found=None
        for y in range(0,h-HH+1,2):
            for x in range(0,w-WW+1,2):
                if ok(y,x,HH,WW): found=(x+pad,y+pad); break
            if found: break
        if found: best=(found[0]*S,found[1]*S,ww*S,hh*S); break
    out[name]=dict(card=[int(c) for c in card],rect=best)
    print(name,card,best, 'inches', [round(v/192,2) for v in best])
json.dump(out,open('free.json','w'))
