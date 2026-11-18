import os, json, shutil, math, sys
from PIL import Image, ImageDraw, ImageFont
from bld_core import *
import bld_core
from bld_town import *
from bld_depot import *

OUT = '/mnt/user-data/outputs/bangunan_kota'
if os.path.exists(OUT): shutil.rmtree(OUT)
for d in ('rumah_manusia', 'rumah_fantasi', 'depot_karavan', 'gerbang_pagar_tembok', 'animasi', 'preview'):
    os.makedirs(f'{OUT}/{d}')

SHOP = [H('d9453d'), H('f0c455'), H('3f6fb0'), H('5fa04a')]
BREAD = [H('c8893a'), H('e0a860'), H('f3ead8'), H('c8893a')]
CAT = {}      # nama -> (folder, image, npc, deskripsi, chim_color)

def reg(name, folder, fn, npc, desc, smoke=None):
    bld_core.REC['chim'].clear(); bld_core.REC['door'].clear()
    r = fn()
    im = r[0] if isinstance(r, tuple) else r
    extra = None
    meta = dict(folder=folder, npc=npc, desc=desc, size=list(im.size), doors=[list(d) for d in bld_core.REC['door']],
                chimneys=[list(c) for c in bld_core.REC['chim']], ground_y=im.height - 1)
    im.save(f'{OUT}/{folder}/{name}.png')
    CAT[name] = dict(meta=meta, img=im, smoke=smoke, extra=extra)

# ---------------- rumah manusia (sesuai pekerjaan NPC)
RM = 'rumah_manusia'
reg('rumah_petani', RM, lambda: cottage(seed=2, sign='gandum', extras=[('hay', 2), ('fork', 8), ('barrel', 100)], pad_r=20), 'petani_pria, petani_wanita', 'pondok beratap jerami, tumpukan jerami, garpu', (210, 210, 220))
reg('rumah_warga_kayu', RM, lambda: townhouse(seed=1, props=[('barrel', 6), ('crate', 2)], pad_r=4), 'warga_pria', 'rumah kayu 2 lantai atap genteng merah', (210, 210, 220))
reg('rumah_warga_plester', RM, lambda: townhouse(w=124, ground='plaster', plaster=H('f0e8d0'), roof_c=H('5a6a8a'), roof_kind='slate', shutter=H('5fa04a'), seed=4, chim='l', bays=5, floor_h=(54, 44), roof_h=44, pad_r=4), 'warga_wanita', 'rumah plester + kayu, atap batu tulis biru', (210, 210, 220))
reg('rumah_warga_bata', RM, lambda: townhouse(w=100, ground='brick', gwall=H('b0553a'), roof_c=H('c9843a'), roof_kind='shingle', shutter=H('8a2f5a'), seed=7, bays=3, floor_h=(54, 46), roof_h=40, sign='koin', pad_r=22), 'warga (umum)', 'rumah bata, atap sirap', (210, 210, 220))
reg('pos_penjaga', RM, lambda: guardhouse(seed=4), 'penjaga_gerbang', 'pos jaga batu dengan benteng dan panji', None)
reg('bengkel_pandai_besi', RM, lambda: smithy(), 'pandai_besi, beruang_pandai_besi', 'bengkel tempa dengan tungku, landasan, cerobong besar', None)
reg('perpustakaan', RM, lambda: library(), 'pustakawan', 'perpustakaan batu bertiang dengan pedimen buku', None)
reg('toko_pedagang', RM, lambda: townhouse(w=124, ground='plaster', plaster=H('f0e4c4'), roof_c=H('8a4a3a'), shutter=H('3f6fb0'), seed=9, shop=SHOP, awn=(H('d9453d'), H('f6eedc')), sign='koin', bays=4, lit=True, chim='r', pad_r=22, props=[('crate', 4), ('barrel', 108)]), 'pedagang', 'toko dengan etalase, kanopi belang, peti dagangan', (210, 210, 220))
reg('gereja_kapel', RM, lambda: chapel(), 'pendeta', 'kapel batu dengan menara lonceng dan jendela mawar', None)
reg('toko_roti', RM, lambda: townhouse(w=112, ground='plaster', plaster=H('f6e8c8'), roof_c=H('c9843a'), roof_kind='tile', shutter=H('c9843a'), seed=12, shop=BREAD, awn=(H('e0903a'), H('f6eedc')), sign='roti', bays=3, lit=True, chim='r', pad_r=22, chim_c=H('b0553a'), props=[('sack', 4), ('sack', 100)]), 'tukang_roti', 'toko roti dengan oven bata dan kanopi', (240, 240, 245))
reg('penggergajian_kayu', RM, lambda: cottage(wall='logs', roof_c=H('7a5a3a'), roof_kind='shingle', seed=5, extras=[('woodpile', 98, 3, 3), ('crate', 2)], sign='kapak', pad_r=44), 'penebang_kayu', 'pondok kayu gelondongan dengan tumpukan kayu', (210, 210, 220))
reg('pondok_pemburu', RM, lambda: cottage(wall='logs', roof_c=H('6a8a5a'), roof_kind='shingle', seed=8, antler=True, extras=[('pelt', 70), ('target', 104)], sign='busur', pad_r=34), 'pemanah, elf_pemanah', 'pondok pemburu dengan tanduk, kulit, sasaran panah', (210, 210, 220))
reg('rumah_bangsawan', RM, lambda: manor(), 'bangsawan', 'rumah besar dengan dua menara, balkon, dan lambang', None)
reg('kedai_penginapan', RM, lambda: townhouse(w=156, ground='plaster', plaster=H('f0dcb0'), roof_c=H('8a4a3a'), shutter=H('8a2f5a'), seed=15, door_w=34, bays=5, sign='cangkir', lit=True, chim='l', floor_h=(54, 46), roof_h=44, pad_r=22, props=[('barrel', 6), ('barrel', 18), ('lantern', 50)]), 'kucing_bard, kelinci_pelayan', 'kedai dan penginapan, pintu ganda lebar, papan cangkir', (230, 230, 235))
reg('barak_serigala', RM, lambda: guardhouse(w=170, banner_c=H('5a3a7a'), emblem=H('d8dce6'), seed=14), 'serigala_penjaga', 'barak penjaga besar, panji ungu', None)
reg('rumah_pencuri', RM, lambda: townhouse(w=100, ground='stone', gwall=H('7a7a8a'), plaster=H('8a8aa0'), beam=H('2a1c3a'), roof_c=H('4a3a6a'), shutter=H('2a1c3a'), flower=H('7a5ac8'), seed=17, bays=3, lit=True, floor_h=(54, 44), roof_h=40, pad_r=4), 'rubah_pencuri', 'rumah sempit gelap tempat persembunyian', (200, 200, 215))
RF = 'rumah_fantasi'
reg('rumah_pohon_elf', RF, lambda: treehouse(), 'elf_pemanah, elf_tabib', 'rumah pohon raksasa dengan tangga tali', None)
reg('pondok_tabib', RF, lambda: cottage(roof_c=H('7a9a5a'), roof_kind='thatch', wall='plaster', plaster=H('e8e0c0'), shutter=H('8a60c8'), herbs_=True, sign='ramuan', seed=19, extras=[('barrel', 100)], pad_r=20), 'elf_tabib', 'pondok herbal dengan tanaman obat digantung', (190, 235, 190))
reg('menara_penyihir', RF, lambda: tower(kind='mage', base=H('9aa8c8'), roof_c=H('3a5a9a'), w=84, seed=51), 'elf_penyihir', 'menara batu biru bertabur bintang dan bola cahaya', None)
reg('kuil_peramal', RF, lambda: shrine(), 'rubah_peramal', 'kuil merah dengan patung rubah dan bola kristal', None)
reg('tambang_kurcaci', RF, lambda: mine(), 'kurcaci_penambang', 'pintu tambang di bukit batu, rel dan gerobak', None)
reg('pondok_orc', RF, lambda: orc_hut(), 'orc_prajurit', 'tenda kulit dengan pagar kayu runcing dan panji', None)
reg('menara_alkemis', RF, lambda: tower(kind='alch'), 'kadal_alkemis', 'menara alkemis dengan balkon kuali dan atap ungu', (140, 255, 150))
# ---------------- depot (khusus kota) + gerbang
DP = 'depot_karavan'
reg('depot_gudang', DP, lambda: gudang(), 'MC karavan (muat/bongkar barang)', 'gudang besar dengan pintu muat, katrol, panji peti', (210, 210, 220))
reg('depot_kantor_tukar', DP, lambda: kantor_tukar(), 'MC karavan (pertukaran barang/koin)', 'kantor pertukaran dengan loket berjeruji dan papan tukar', (210, 210, 220))
reg('depot_dermaga_muat', DP, lambda: dermaga(), 'MC karavan', 'dermaga muat setinggi dasar gerobak (32 px)', None)
reg('depot_tumpukan_a', DP, lambda: tumpukan('a'), '-', 'tumpukan peti dan tong', None)
reg('depot_tumpukan_b', DP, lambda: tumpukan('b'), '-', 'tumpukan karung dan peti', None)
reg('depot_tumpukan_c', DP, lambda: tumpukan('c'), '-', 'campuran peti, tong, karung', None)
reg('depot_timbangan', DP, lambda: timbang(), '-', 'timbangan dagang', None)
reg('depot_papan_harga', DP, lambda: papan_harga(), '-', 'papan harga barang', None)
reg('depot_tanda_arah', DP, lambda: tanda_depot(), '-', 'tiang penunjuk arah ke depot dan pertukaran', None)
GP = 'gerbang_pagar_tembok'
reg('gerbang_kota', GP, lambda: gerbang_kota(), '-', 'gerbang kota, lubang 90x118 px (karavan bisa lewat)', None)
reg('pagar_kayu', GP, lambda: pagar_kayu(), '-', 'pagar kayu 32 px (ubin sambung ke kanan)', None)
reg('pagar_kayu_gerbang', GP, lambda: pagar_kayu_gerbang(), '-', 'pintu pagar kayu', None)
reg('pagar_batu', GP, lambda: pagar_batu(), '-', 'pagar batu rendah 32 px', None)
reg('pagar_besi', GP, lambda: pagar_besi(), '-', 'pagar besi 32 px', None)
reg('tembok_kota', GP, lambda: tembok_kota(), '-', 'segmen tembok kota 64 px', None)
d = derek(30)
sheet(d).save(f'{OUT}/animasi/depot_derek_30f.png'); d[0].save(f'{OUT}/{DP}/depot_derek_frame0.png')
CAT['depot_derek'] = dict(meta=dict(folder=DP, npc='-', desc='derek kayu dengan peti berayun (30 frame)', size=list(d[0].size), doors=[], chimneys=[], ground_y=d[0].height - 1), img=d[0], smoke=None, extra=None)

# ---------------- animasi asap cerobong
PAD = 44
def smoke_frames(size, pts, col, n=30):
    frames = []
    for f in range(n):
        t = f / n
        im = Image.new('RGBA', (size[0], size[1] + PAD), (0, 0, 0, 0))
        for (cx, cy) in pts:
            for k in range(4):
                ph = (t + k / 4.0) % 1.0
                x = cx + math.sin((ph + k * 0.7) * 5) * 2.5 + ph * 6
                yy = cy + PAD - 3 - ph * 34
                rr = 2 + 3.2 * ph
                a = int(215 * (1 - ph) ** 0.9)
                tmp = Image.new('RGBA', im.size, (0, 0, 0, 0))
                ImageDraw.Draw(tmp).ellipse([x - rr, yy - rr, x + rr, yy + rr], fill=col + (a,))
                im.alpha_composite(tmp)
        frames.append(im)
    return frames
for name, c in CAT.items():
    if c['smoke'] and c['meta']['chimneys']:
        fr = smoke_frames(tuple(c['meta']['size']), c['meta']['chimneys'][:1], c['smoke'])
        sheet(fr).save(f'{OUT}/animasi/{name}_asap_30f.png')
        c['meta']['asap'] = f'animasi/{name}_asap_30f.png (kanvas {fr[0].size[0]}x{fr[0].size[1]}, taruh di (0,-{PAD}))'
# bengkel: api tungku + asap abu
sm_im, chp, box = smithy()
bld_core.REC['chim'].clear()
glow, smk = forge_overlays(sm_im.size, (box[0], box[4]), chp)
sheet(glow).save(f'{OUT}/animasi/bengkel_pandai_besi_api_30f.png')
fr = smoke_frames(tuple(sm_im.size), [(chp[0], chp[1] + 3)], (200, 200, 210))
sheet(fr).save(f'{OUT}/animasi/bengkel_pandai_besi_asap_30f.png')
CAT['bengkel_pandai_besi']['meta']['asap'] = f'animasi/bengkel_pandai_besi_asap_30f.png (kanvas {fr[0].size[0]}x{fr[0].size[1]}, taruh di (0,-{PAD}))'
CAT['bengkel_pandai_besi']['meta']['api'] = 'animasi/bengkel_pandai_besi_api_30f.png (ukuran sama dengan sprite, taruh di (0,0))'
fr = smoke_frames(CAT['menara_alkemis']['meta']['size'] and tuple(CAT['menara_alkemis']['meta']['size']), CAT['menara_alkemis']['meta']['chimneys'][:1], (140, 255, 150))
sheet(fr).save(f'{OUT}/animasi/menara_alkemis_asap_30f.png')
json.dump({k: v['meta'] for k, v in CAT.items()}, open(f'{OUT}/data_bangunan.json', 'w'), indent=1, ensure_ascii=False)
print('exported', len(CAT), flush=True)
import pickle
pickle.dump({k: v['img'] for k, v in CAT.items()}, open('/tmp/bld_cache.pkl', 'wb'))
