import os, math, json
from PIL import Image, ImageDraw, ImageFont
from pxlib import H, new, outline, up, sheet
from npc_roster import R
from npc_anims import ALL
OUT='/mnt/user-data/outputs/npc_sprites'
P=f'{OUT}/props'; PV=f'{OUT}/preview'
os.makedirs(P,exist_ok=True); os.makedirs(PV,exist_ok=True)
def fin(im): 
    o=outline(im,0.55); o.alpha_composite(im); return o
def rect(d,x0,y0,x1,y1,c): d.rectangle([x0,y0,x1,y1],fill=c)
WOOD=H('9a6a3a'); WL=H('c18c50'); WD=H('6a4526'); IR=H('8a90a0'); IRL=H('b8bece'); IRD=H('555b6b')
# landasan 16x10 (+1 pad)
im=new(18,12); d=ImageDraw.Draw(im)
rect(d,5,6,12,10,WOOD); rect(d,5,6,12,6,WL); rect(d,12,6,12,10,WD)
rect(d,3,2,14,4,IR); rect(d,3,2,14,2,IRL); rect(d,1,3,3,3,IR); rect(d,0,3,1,3,IRD); rect(d,6,5,11,5,IRD); rect(d,3,4,14,4,IRD)
fin(im).save(f'{P}/prop_landasan.png')
# meja adonan 20x15
im=new(22,17); d=ImageDraw.Draw(im)
rect(d,1,5,20,6,WL); rect(d,1,7,20,7,WD); rect(d,3,8,5,16,WOOD); rect(d,16,8,18,16,WOOD); rect(d,5,12,16,12,WD)
d.ellipse([7,1,15,6],fill=H('f3e6c8')); d.ellipse([8,1,12,3],fill=H('fff8e8')); d.rectangle([16,3,18,4],fill=H('d8c9a0'))
fin(im).save(f'{P}/prop_meja_adonan.png')
# balok kayu 18x6
im=new(20,8); d=ImageDraw.Draw(im)
rect(d,1,1,16,6,H('8a5a30')); rect(d,1,1,16,2,H('a8743f')); rect(d,1,5,16,6,H('6a4526'))
d.ellipse([14,1,18,6],fill=H('e2c490')); d.ellipse([15,2,17,5],outline=H('c0a070'))
for x in (4,8,12): d.point((x,3),fill=H('6a4526'))
fin(im).save(f'{P}/prop_balok_kayu.png')
# tanah olahan 24x5
im=new(26,7); d=ImageDraw.Draw(im)
rect(d,1,2,24,5,H('6a4526')); rect(d,1,2,24,2,H('8a5a30'))
for x in range(3,24,4): rect(d,x,1,x+2,2,H('8a5a30')); d.point((x+1,3),fill=H('4a2e1a'))
for x in (5,13,21): d.point((x,0),fill=H('5fa04a')); d.point((x,1),fill=H('78c058'))
fin(im).save(f'{P}/prop_tanah_olahan.png')
# rak buku 18x44
im=new(20,46); d=ImageDraw.Draw(im)
rect(d,1,1,18,44,WD); rect(d,2,2,17,43,H('4a2e1a'))
cols=[H('c8433a'),H('3f6fb0'),H('5fa04a'),H('f0c455'),H('8a2f5a'),H('efe4c4'),H('5a4a8a')]
for r in range(5):
    y=3+r*8
    rect(d,2,y+6,17,y+7,WL)
    x=3
    for i in range(6):
        w=2+((i+r)%2); h=5-((i*r)%2)
        rect(d,x,y+6-h,x+w-1,y+5,cols[(i*2+r)%7]); x+=w+1
fin(im).save(f'{P}/prop_rak_buku.png')
anch={'prop_landasan':(33,42),'prop_meja_adonan':(32,36),'prop_balok_kayu':(37,45),'prop_tanah_olahan':(33,49),'prop_rak_buku':(40,7)}
json.dump(anch,open(f'{P}/posisi_prop.json','w'),indent=1)
# ---------- frames loader
def frames(k,a):
    n=ALL[a][0]; s=Image.open(f'{OUT}/{k}/{k}_{a}_{n}f.png')
    return [s.crop((i*56,0,i*56+56,56)) for i in range(n)]
def bg(w,h,gh=14):
    im=Image.new('RGBA',(w,h)); d=ImageDraw.Draw(im)
    for y in range(h-gh):
        t=y/(h-gh); d.line([(0,y),(w,y)],fill=tuple(int(a*(1-t)+b*t) for a,b in zip(H('86c3e6')[:3],H('d9efe0')[:3]))+(255,))
    d.rectangle([0,h-gh,w,h],fill=H('c89a62')); d.rectangle([0,h-gh,w,h-gh+1],fill=H('8fbf62')); d.rectangle([0,h-gh+2,w,h-gh+2],fill=H('a97945'))
    for x in range(3,w,13): d.point((x,h-gh+7+(x%4)),fill=H('9a6c3c'))
    return im
# ---------- GIF peragaan per NPC
Z=3
for k,v in R.items():
    seq=[]
    for a in ['diam','jalan','lari','ngobrol']+v['jobs']:
        fr=frames(k,a); loops=1 if len(fr)>=36 else 2
        seq+=[(a,f) for _ in range(loops) for f in fr]
    out=[]
    for a,f in seq:
        b=bg(76,64,12); b.alpha_composite(f,(10,64-12-52+0-0))
        out.append(up(b,Z).convert('RGB'))
    out[0].save(f'{PV}/peragaan_{k}.gif',save_all=True,append_images=out[1:],duration=33,loop=0)
print('gifs ok',flush=True)
# ---------- roster sheet
try: FNT=ImageFont.load_default(size=11)
except Exception: FNT=ImageFont.load_default()
cols=7; cw=56*3+10; rows=2; ch=56*3+34
sh=Image.new('RGBA',(cols*cw,rows*ch),(96,140,100,255)); d=ImageDraw.Draw(sh)
for i,(k,v) in enumerate(R.items()):
    f=frames(k,'diam')[10]; r,c=divmod(i,cols)
    sh.alpha_composite(up(f,3),(c*cw+5,r*ch+4))
    d.text((c*cw+8,r*ch+56*3+8),v['label'],fill=(255,255,255,255),font=FNT)
sh.convert('RGB').save(f'{PV}/roster_semua_npc.png')
# ---------- adegan desa
stations=[('petani_pria','cangkul',None),('tukang_roti','menguleni','prop_meja_adonan'),('pandai_besi','menempa','prop_landasan'),
          ('penebang_kayu','menebang','prop_balok_kayu'),('pustakawan','menata_buku','prop_rak_buku'),('penjaga_gerbang','jaga',None),
          ('warga_wanita','menyapu',None),('pedagang','menawarkan',None),('pendeta','berdoa',None),('anak','melompat',None),('pemanah','memanah',None)]
step=50; W=step*len(stations)+30; Hh=70
cache={s[0]+s[1]:frames(s[0],s[1]) for s in stations}
props={n:Image.open(f'{P}/{n}.png') for n in anch}
out=[]
for k in range(120):
    b=bg(W,Hh,14)
    for i,(npc,an,pr) in enumerate(stations):
        ox=8+i*step; oy=Hh-14-52
        fr=cache[npc+an]; f=fr[k%len(fr)]
        if pr:
            ax,ay=anch[pr]; b.alpha_composite(props[pr],(ox+ax,oy+ay))
        if npc=='petani_pria':
            b.alpha_composite(props['prop_tanah_olahan'],(ox+anch['prop_tanah_olahan'][0]+2,oy+anch['prop_tanah_olahan'][1]))
        b.alpha_composite(f,(ox,oy))
    out.append(up(b,3).convert('RGB'))
out[0].save(f'{PV}/adegan_desa_medieval.gif',save_all=True,append_images=out[1:],duration=33,loop=0)
out[40].save(f'{PV}/adegan_desa_frame.png')
print('scene ok',flush=True)
