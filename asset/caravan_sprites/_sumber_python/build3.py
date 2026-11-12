import os, shutil, pickle
from PIL import Image
from horse3 import *
from poses3 import *
from harness3 import *
OUT='/mnt/user-data/outputs/caravan_sprites'
KD=f'{OUT}/kuda'
if os.path.exists(KD): shutil.rmtree(KD)
os.makedirs(KD)
names={'bay':'kuda_1_bay','putih':'kuda_2_putih_abu','hitam':'kuda_3_hitam_BONUS','kastanye':'kuda_4_kastanye_kaus_putih_BONUS'}
POSES={a:poses_for(a) for a in ACTIONS}
SPEC={a:(STD if ACTIONS[a][2]=='std' else BIG) for a in ACTIONS}
cacheH={}; cacheR={}
for key,fn in PALS.items():
    pal=fn()
    for a,(n,_,_) in ACTIONS.items():
        d=f'{KD}/{names[key]}/{a}_{n}f'; os.makedirs(f'{d}/layer',exist_ok=True)
        fr=[render_frame(SPEC[a],p,pal) for p in POSES[a]]
        cacheH[(key,a)]=[f['_merged'] for f in fr]
        sheet(cacheH[(key,a)]).save(f'{d}/{names[key]}_{a}_{n}f.png')
        for ln,_ in ORDER: sheet([f[ln] for f in fr]).save(f'{d}/layer/{ln}_{a}_{n}f.png')
for hn,hc in HARN.items():
    for a,(n,_,_) in ACTIONS.items():
        d=f'{KD}/harness_{hn}/{a}_{n}f'; os.makedirs(f'{d}/layer',exist_ok=True)
        anch = a in ('diam','jalan')
        fr=[render_harness_frame(SPEC[a],p,hc,anch) for p in POSES[a]]
        merged=[comp(*[f[k] for k in ('h1_kerah','h2_badan','h3_kepala','h4_tali')]) for f in fr]
        cacheR[(hn,a)]=merged
        sheet(merged).save(f'{d}/harness_{hn}_{a}_{n}f.png')
        for k in ('h1_kerah','h2_badan','h3_kepala','h4_tali'): sheet([f[k] for f in fr]).save(f'{d}/layer/{k}_{a}_{n}f.png')
pickle.dump({'H':{(k,a):v for (k,a),v in cacheH.items() if a=='jalan'},'R':{(k,a):v for (k,a),v in cacheR.items() if a=='jalan'},
             'HA':cacheH,'RA':cacheR},open('/tmp/horse_cache.pkl','wb'))
print('export ok')
