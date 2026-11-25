import os, shutil, json
from PIL import Image
from npc_rig import *
from npc_roster import R
from npc_anims import ALL

OUT='/mnt/user-data/outputs/npc_sprites'
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
for k,v in R.items():
    n=v['npc']; d=f'{OUT}/{k}'; os.makedirs(d)
    anims=['diam','jalan','lari','ngobrol']+v['jobs']
    for a in anims:
        fr,fn=ALL[a]
        frames=[render(n,fn(n,i/fr)) for i in range(fr)]
        sheet(frames).save(f'{d}/{k}_{a}_{fr}f.png')
    print('ok',k,flush=True)
print('export done',flush=True)
