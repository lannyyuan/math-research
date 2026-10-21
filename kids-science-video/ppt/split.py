import json, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
names=['car1','car2','car3','car4','car5','car6','car7','ev1','ev2','ev3','ev7']
out={}
X0,Y0,X1,Y1=120,105,2440,1340   # inside the card border
for n in names:
    a=np.asarray(Image.open(f'img/{n}.png').convert('RGB')).astype(int)
    gas=n.startswith('car')
    card=np.array([253,251,244] if gas else [251,251,255]); bub=np.array([242,231,219] if gas else [241,237,235])
    sub=a[Y0:Y1,X0:X1]
    non=(np.abs(sub-card).sum(2)>24)
    isb=(np.abs(sub-bub).sum(2)<10)
    # bubble = largest connected bubble-coloured blob
    lab,k=ndimage.label(isb); sizes=ndimage.sum(isb,lab,range(1,k+1)); bl=np.argmax(sizes)+1
    ys,xs=np.where(lab==bl); bubble=[int(xs.min()+X0),int(ys.min()+Y0),int(xs.max()+X0),int(ys.max()+Y0)]
    # illustration = largest connected non-card blob after removing the bubble box and the title band
    m=non.copy(); m[ys.min():ys.max()+1, xs.min():xs.max()+1]=False; m[:180-Y0+105,:]=False
    m=ndimage.binary_closing(m,iterations=6)
    lab,k=ndimage.label(m); sizes=ndimage.sum(m,lab,range(1,k+1)); il=np.argmax(sizes)+1
    ys,xs=np.where(lab==il); ill=[int(xs.min()+X0),int(ys.min()+Y0),int(xs.max()+X0),int(ys.max()+Y0)]
    # title = non-card pixels in the top band
    t=non[:200,:1100]; ys,xs=np.where(t); title=[int(xs.min()+X0),int(ys.min()+Y0),int(xs.max()+X0),int(ys.max()+Y0)]
    out[n]=dict(title=title,ill=ill,bubble=bubble,side='L' if ill[0]<1280 else 'R')
    print(n,out[n])
json.dump(out,open('split.json','w'),indent=1)
ims=[]
for n in names:
    im=Image.open(f'img/{n}.png').convert('RGB'); d=ImageDraw.Draw(im); o=out[n]
    for k,c in (('title',(255,0,0)),('ill',(0,0,255)),('bubble',(0,160,0))): d.rectangle(o[k],outline=c,width=8)
    ims.append(im.resize((640,360)))
g=Image.new('RGB',(640*4,360*3),'white')
for i,im in enumerate(ims): g.paste(im,((i%4)*640,(i//4)*360))
g.save('qa/split.jpg')
