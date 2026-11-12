import pickle, math
from pxlib import *
from wagon import *
from acc import *
from driver import *
OUT='/mnt/user-data/outputs/caravan_sprites'
C=pickle.load(open('/tmp/horse_cache.pkl','rb'))
HW=C['H']; RW=C['R']
wheels={s:wheel_sheet(s) for s in ('kayu','merah')}
drv={'a':render_driver(D1),'b':render_driver(D2)}
A_body=body_layer('A'); B_body=body_layer('B')
canA=canopy_png(H('efe4c4')); cabB=cabin_png(H('3f8f93'),H('f2e3b8'),H('a63a3a'),H('d85a50'))
flag=[a_flag(f) for f in range(8)]; smoke=[b_smoke(f) for f in range(8)]
accA=[a_barrel(),a_ropes(),a_tools(),a_lantern(),a_pots(),a_roofcargo(),a_brake()]
accB=[b_awning(),b_sign(),b_steps(),b_chimney(),a_lantern(),a_pots()]
BOUNCE=[0,0,-1,-1,0,0,-1,-1]
def bg(w,h,scroll):
    im=Image.new('RGBA',(w,h)); d=ImageDraw.Draw(im)
    for y in range(h-22):
        t=y/(h-22); d.line([(0,y),(w,y)],fill=tuple(int(a*(1-t)+b*t) for a,b in zip(H('86c3e6')[:3],H('d9efe0')[:3]))+(255,))
    for x in range(w):
        yy=h-30-int(6*math.sin((x+scroll*0.25)/22.0)+3*math.sin((x+scroll*0.25)/9.0)); d.line([(x,yy),(x,h-22)],fill=H('9bc58a'))
    for x in range(w):
        yy=h-25-int(3*math.sin((x+scroll*0.6)/14.0)); d.line([(x,yy),(x,h-22)],fill=H('78ae6b'))
    d.rectangle([0,h-22,w,h],fill=H('c89a62')); d.rectangle([0,h-22,w,h-21],fill=H('8fbf62')); d.rectangle([0,h-20,w,h-20],fill=H('a97945'))
    for i in range(0,w+60,17):
        x=(i-int(scroll))%(w+20); d.point((x,h-12+(i%5)),fill=H('9a6c3c')); d.point((x+1,h-12+(i%5)),fill=H('e0b988'))
    return im
def scene(kind,hk,hn,dk,wheel,k):
    f12=(k//2)%12; f8=k%8; f8s=(k//3)%8
    sc=new(216,WH+4); by=BOUNCE[f8s]
    layers=[A_body,canA]+accA+[flag[f8s]] if kind=='A' else [B_body,cabB]+accB[:4]+[smoke[f8s],flag[f8s]]+accB[4:]
    wag=new(WW,WH)
    for l in layers: wag.alpha_composite(l)
    sc.alpha_composite(wag,(0,2+by))
    for cx in (REAR_WHEEL_X,FRONT_WHEEL_X): sc.alpha_composite(wheels[wheel][f8],(cx-15,2+Y0+WHEEL_CY-15))
    sc.alpha_composite(drv[dk][f8s],(96,2+32+by))
    sc.alpha_composite(HW[(hk,'jalan')][f12],(120,2+33)); sc.alpha_composite(RW[(hn,'jalan')][f12],(120,2+33))
    return sc
for name,args in (('preview_A_covered_wagon.gif',('A','bay','coklat','a','kayu')),('preview_B_karavan_dagang.gif',('B','putih','hitam','b','merah'))):
    fr=[]
    for k in range(24):
        b=bg(250,118,k*0.9); s=scene(*args,k); b.alpha_composite(s,(14,118-s.height-2)); fr.append(up(b,4).convert('RGB'))
    fr[0].save(f'{OUT}/preview/{name}',save_all=True,append_images=fr[1:],duration=40,loop=0)
    fr[6].save(f'{OUT}/preview/{name.replace(".gif","_frame.png")}')
# horse-only walk strip preview (3 horses)
rows=[]
for hk,hn in (('bay','coklat'),('putih','hitam'),('hitam','merah'),('kastanye','coklat')):
    rows.append(sheet([comp(HW[(hk,'jalan')][i],RW[(hn,'jalan')][i]) for i in range(12)]))
im=Image.new('RGBA',(96*12,64*4),(196,164,70,255))
for i,r in enumerate(rows): im.alpha_composite(r,(0,64*i))
up(im,2).convert('RGB').save(f'{OUT}/preview/preview_kuda_jalan_semua.png')
# horse gif
fr=[]
for k in range(24):
    b=Image.new('RGBA',(96*2+8,64*2+4),(196,164,70,255))
    for i,(hk,hn) in enumerate((('bay','coklat'),('putih','hitam'))):
        b.alpha_composite(comp(HW[(hk,'jalan')][(k//2)%12],RW[(hn,'jalan')][(k//2)%12]),(i*100,2))
    fr.append(up(b,5).convert('RGB'))
fr[0].save(f'{OUT}/preview/preview_kuda_jalan.gif',save_all=True,append_images=fr[1:],duration=80,loop=0)
print('ok')
