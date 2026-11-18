import json, pickle, math, sys, os
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/home/claude/work')
from pxlib import H, up, sheet
OUT = '/mnt/user-data/outputs/bangunan_kota'; NPC = '/mnt/user-data/outputs/npc_sprites'; CV = '/mnt/user-data/outputs/caravan_sprites'
imgs = pickle.load(open('/tmp/bld_cache.pkl', 'rb')); meta = json.load(open(f'{OUT}/data_bangunan.json'))
try: FNT = ImageFont.load_default(size=11)
except Exception: FNT = ImageFont.load_default()
def catalog(names, fn, title, width=1500):
    rows = []; cur = []; cw = 0
    for n in names:
        im = imgs[n]
        if cw + im.width + 14 > width and cur: rows.append(cur); cur = []; cw = 0
        cur.append(n); cw += im.width + 14
    rows.append(cur)
    H_ = sum(max(imgs[n].height for n in r) + 26 for r in rows) + 30
    cat = Image.new('RGBA', (width, H_), (96, 128, 150, 255)); d = ImageDraw.Draw(cat); d.text((8, 6), title, fill=(255, 255, 255, 255), font=FNT)
    y = 24
    for r in rows:
        x = 8; rh = max(imgs[n].height for n in r)
        for n in r:
            im = imgs[n]; cat.alpha_composite(im, (x, y + rh - im.height)); d.text((x, y + rh + 4), n, fill=(255, 255, 255, 255), font=FNT); x += im.width + 14
        y += rh + 26
    cat.convert('RGB').save(f'{OUT}/preview/{fn}')
hum = [n for n, m in meta.items() if m['folder'] == 'rumah_manusia']
fan = [n for n, m in meta.items() if m['folder'] == 'rumah_fantasi']
dep = [n for n, m in meta.items() if m['folder'] in ('depot_karavan', 'gerbang_pagar_tembok')]
catalog(hum, 'katalog_rumah_manusia.png', 'RUMAH MANUSIA (menghadap layar)')
catalog(fan, 'katalog_rumah_fantasi.png', 'RUMAH FANTASI (menghadap layar)')
catalog(dep, 'katalog_depot_gerbang_pagar.png', 'DEPOT KARAVAN, GERBANG, PAGAR, TEMBOK')
# ---------------- karavan (frame diam)
from wagon import *
from acc import *
def caravan():
    A = body_layer('A'); canA = canopy_png(H('efe4c4'))
    wag = new(WW, WH)
    for l in [A, canA, a_barrel(), a_ropes(), a_tools(), a_lantern(), a_pots(), a_roofcargo(), a_brake(), a_flag(0)]: wag.alpha_composite(l)
    wh = wheel_sheet('kayu')
    sc = new(216, WH)
    sc.alpha_composite(wag, (0, 0))
    for cx in (REAR_WHEEL_X, FRONT_WHEEL_X): sc.alpha_composite(wh[0], (cx - 15, Y0 + WHEEL_CY - 15))
    from driver import render_driver, D1
    sc.alpha_composite(render_driver(D1)[0], (96, 32))
    hs = Image.open(f'{CV}/kuda/kuda_1_bay/diam_36f/kuda_1_bay_diam_36f.png').crop((0, 0, 96, 64))
    hr = Image.open(f'{CV}/kuda/harness_coklat/diam_36f/harness_coklat_diam_36f.png').crop((0, 0, 96, 64))
    sc.alpha_composite(hs, (120, 33)); sc.alpha_composite(hr, (120, 33))
    return sc
car = caravan()
def npc(name, anim, n, fi=0):
    s = Image.open(f'{NPC}/{name}/{name}_{anim}_{n}f.png'); return s.crop((fi * 56, 0, fi * 56 + 56, 56))
# ---------------- peta kota
GY = 300; W = 2900; HH = 340
sc = Image.new('RGBA', (W, HH))
d = ImageDraw.Draw(sc)
for y in range(GY):
    t = y / GY; d.line([(0, y), (W, y)], fill=tuple(int(a * (1 - t) + b * t) for a, b in zip(H('86c3e6')[:3], H('dff0e8')[:3])) + (255,))
d.rectangle([0, GY, W, HH], fill=H('b09878'))
for x in range(0, W, 9):
    for y in range(GY + 2, HH, 6):
        off = (x // 9 + y // 6) % 2 * 4
        d.rectangle([x + off, y, x + off + 6, y + 3], fill=H('c2aa8a') if (x * y) % 5 else H('a08868'))
d.rectangle([0, GY, W, GY + 1], fill=H('7a6248'))
def put(name, x, front=None):
    im = imgs[name]; sc.alpha_composite(im, (x, GY + 1 - im.height)); return x + im.width
x = 0
x = put('gerbang_kota', x) - 20
for i in range(2): sc.alpha_composite(imgs['pagar_kayu'], (x + i * 32, GY + 1 - imgs['pagar_kayu'].height))
x += 70
places = {}
for nm in ('rumah_petani', 'rumah_warga_kayu', 'bengkel_pandai_besi', 'perpustakaan', 'toko_pedagang', 'gereja_kapel', 'toko_roti', 'kedai_penginapan'):
    places[nm] = x; x = put(nm, x) + 6
gx = x + 10
x = put('depot_gudang', gx)
dock_x = gx + 36
sc.alpha_composite(imgs['depot_dermaga_muat'], (dock_x, GY + 1 - imgs['depot_dermaga_muat'].height))
cx0 = dock_x + imgs['depot_dermaga_muat'].width - 4
sc.alpha_composite(car, (cx0, GY + 1 - 96))
kx = cx0 + 216 + 90
x = put('depot_kantor_tukar', kx)
sc.alpha_composite(imgs['depot_tumpukan_a'], (gx + 150, GY + 1 - 58)) if False else None
sc.alpha_composite(imgs['depot_papan_harga'], (kx - 82, GY + 1 - 70)); sc.alpha_composite(imgs['depot_timbangan'], (kx - 24, GY + 1 - 50)); sc.alpha_composite(imgs['depot_tanda_arah'], (cx0 + 216 + 18, GY + 1 - 74))
sc.alpha_composite(imgs['depot_tumpukan_b'], (dock_x + 6, GY + 1 - 44 - 58)) if False else None
sc.alpha_composite(imgs['depot_tumpukan_a'], (dock_x + 16, GY + 1 - 38 - 58 + 6))
x = put('pagar_kayu_gerbang', x + 10)
# NPC di depan pintu masing-masing
def door_x(nm):
    ds = meta[nm]['doors']; return places[nm] + (ds[0][0] if ds else imgs[nm].width // 2)
for nm, (npcn, an, n, fi, dxo) in {'rumah_petani': ('petani_pria', 'diam', 60, 4, 40), 'bengkel_pandai_besi': ('pandai_besi', 'diam', 60, 4, 70), 'perpustakaan': ('pustakawan', 'diam', 60, 4, 0),
                                 'toko_pedagang': ('pedagang', 'menawarkan', 60, 12, 36), 'gereja_kapel': ('pendeta', 'berdoa', 60, 20, 0),
                                 'toko_roti': ('tukang_roti', 'diam', 60, 4, 34), 'kedai_penginapan': ('kucing_bard', 'diam', 60, 4, 50), 'rumah_warga_kayu': ('warga_pria', 'diam', 60, 4, 30)}.items():
    f = npc(npcn, an, n, fi); sc.alpha_composite(f, (int(door_x(nm) + dxo) - 28, GY + 1 - 52))
sc.alpha_composite(npc('penjaga_gerbang', 'diam', 60, 4), (150, GY + 1 - 52))
sc.alpha_composite(npc('anak', 'melambai', 36, 6), (gx + 120, GY + 1 - 52))
sc.convert('RGB').save(f'{OUT}/preview/peta_kota_skala.png')
sc.crop((gx - 40, 0, min(W, kx + 300), HH)).convert('RGB').save(f'{OUT}/preview/area_depot_dengan_karavan.png')
print('ok', sc.size, 'caravan x', cx0, 'dock', dock_x)
