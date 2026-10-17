import json, numpy as np
from PIL import Image
S=8
d=json.load(open('free.json'))
for name,v in d.items():
    a=np.asarray(Image.open(f'img/{name}.png').convert('RGB')).astype(int); H,W,_=a.shape
    free=(np.abs(a-np.array(v['card'])).sum(2)<14)
    h,w=H//S,W//S
    f=free[:h*S,:w*S].reshape(h,S,w,S).all(axis=(1,3))
    sat=np.zeros((h+1,w+1),int); sat[1:,1:]=(~f).cumsum(0).cumsum(1)
    pad=int(40/S)
    x0,y0,rw,rh=[t//S for t in v['rect']]
    ww=int(min(rw*0.9, 4.0*192/S)); hh=int(round(ww*9/16))
    HH,WW=hh+2*pad,ww+2*pad
    # valid top-left positions in the pocket around the max rect (same connected area)
    ok=np.zeros((h-HH+1,w-WW+1),bool)
    ys,xs=np.mgrid[0:h-HH+1,0:w-WW+1]
    ok=(sat[ys+HH,xs+WW]-sat[ys,xs+WW]-sat[ys+HH,xs]+sat[ys,xs])==0
    # flood from the max-rect position
    from collections import deque
    sy,sx=y0-pad,x0-pad; sy=max(0,min(sy,ok.shape[0]-1)); sx=max(0,min(sx,ok.shape[1]-1))
    if not ok[sy,sx]:
        cand=np.argwhere(ok); k=np.abs(cand-[sy,sx]).sum(1).argmin(); sy,sx=cand[k]
    seen=np.zeros_like(ok); q=deque([(sy,sx)]); seen[sy,sx]=True; pts=[]
    while q:
        y,x=q.popleft(); pts.append((y,x))
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            Y,X=y+dy,x+dx
            if 0<=Y<ok.shape[0] and 0<=X<ok.shape[1] and ok[Y,X] and not seen[Y,X]:
                seen[Y,X]=True; q.append((Y,X))
    pts=np.array(pts); cy=(pts[:,0].min()+pts[:,0].max())/2; cx=(pts[:,1].min()+pts[:,1].max())/2
    k=((pts-[cy,cx])**2).sum(1).argmin(); y,x=pts[k]
    v['place']=[int((x+pad)*S),int((y+pad)*S),ww*S,hh*S]
    print(name,[round(t/192,2) for t in v['place']])
json.dump(d,open('free.json','w'))
