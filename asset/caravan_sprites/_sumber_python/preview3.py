import pickle, math
from PIL import Image, ImageDraw
from pxlib import *
from horse3 import STD, BIG, GY
from poses3 import ACTIONS
OUT='/mnt/user-data/outputs/caravan_sprites/preview'
C=pickle.load(open('/tmp/horse_cache.pkl','rb')); HA=C['HA']; RA=C['RA']
def bgf(w,h,scroll):
    im=Image.new('RGBA',(w,h),H('9fd3e8')); d=ImageDraw.Draw(im)
    for y in range(h-12):
        t=y/(h-12); d.line([(0,y),(w,y)],fill=tuple(int(a*(1-t)+b*t) for a,b in zip(H('86c3e6')[:3],H('d9efe0')[:3]))+(255,))
    d.rectangle([0,h-12,w,h],fill=H('c89a62')); d.rectangle([0,h-12,w,h-11],fill=H('8fbf62'))
    for i in range(0,w+60,19):
        x=(i-int(scroll))%(w+20); d.point((x,h-6+(i%4)),fill=H('9a6c3c')); d.point((x+1,h-6+(i%4)),fill=H('e0b988'))
    return im
speed={'diam':0,'jalan':1.8,'lari':6.5,'lompat':4.5,'berhenti':3.0}
tiles=[]
for a,(n,_,cv) in ACTIONS.items():
    spec=STD if cv=='std' else BIG
    fw,fh=spec[0],spec[1]
    frames=[]
    for k in range(n*3 if a!='lari' else n*4):
        f=k%n if a in('diam','jalan','lari') else min(k//2,n-1)
        sc=bgf(fw+40,fh+8,k*speed[a]); gy=fh+8-12
        # ground line: horse ground row GY+oy must sit on grass top (h-12)
        spr=HA[('bay',a)][f].copy(); spr.alpha_composite(RA[('coklat',a)][f])
        y=(fh+8-12)-int(GY+spec[3])
        sc.alpha_composite(spr,(20,y))
        frames.append(up(sc,5).convert('RGB'))
    dur=100 if a!='lari' else 70
    frames[0].save(f'{OUT}/preview_aksi_{a}.gif',save_all=True,append_images=frames[1:],duration=dur,loop=0)
# contact sheet of every frame, bay, with harness
rows=[]
W=128*3
sheetim=Image.new('RGBA',(14*128,5*96),(196,164,70,255))
for r,(a,(n,_,cv)) in enumerate(ACTIONS.items()):
    spec=STD if cv=='std' else BIG
    for f in range(n):
        spr=HA[('bay',a)][f].copy(); spr.alpha_composite(RA[('coklat',a)][f])
        sheetim.alpha_composite(spr,(f*128,r*96+(96-spec[1])))
up(sheetim,2).convert('RGB').save(f'{OUT}/preview_semua_aksi.png')
print('ok')
