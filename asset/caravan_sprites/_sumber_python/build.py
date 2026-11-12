import os, shutil, math
from PIL import ImageFont
from pxlib import *
from wagon import *
from acc import *
from horse import *
from driver import *

OUT = '/mnt/user-data/outputs/caravan_sprites'
if os.path.exists(OUT):
    shutil.rmtree(OUT)
for d in ('kuda', 'pengemudi', 'gerobak_A_covered_wagon', 'gerobak_B_karavan_dagang', 'roda', 'aksesoris', 'preview'):
    os.makedirs(f'{OUT}/{d}')


def save(img, path):
    img.save(f'{OUT}/{path}')


# ---------------------------------------------------------------- HORSES
horses = {
    'kuda_1_kastanye': PAL1,
    'kuda_2_abu': PAL2,
}
harns = {'coklat': HARN_BROWN, 'hitam': HARN_BLACK, 'merah': HARN_RED}
walk_h, idle_h = {}, {}
for name, pal in horses.items():
    w = render_horse(pal, 'walk', 8)
    i = render_horse(pal, 'idle', 4)
    walk_h[name], idle_h[name] = w, i
    save(sheet(w), f'kuda/{name}_jalan_8f.png')
    save(sheet(i), f'kuda/{name}_diam_4f.png')
harn_walk = {}
for hn, hc in harns.items():
    hw = render_harness(hc, 'walk', 8)
    hi = render_harness(hc, 'idle', 4)
    harn_walk[hn] = hw
    save(sheet(hw), f'kuda/harness_{hn}_jalan_8f.png')
    save(sheet(hi), f'kuda/harness_{hn}_diam_4f.png')

# ---------------------------------------------------------------- DRIVERS
drivers = {'pengemudi_1_pionir': D1, 'pengemudi_2_pedagang': D2}
drv_frames = {}
for n, c in drivers.items():
    fr = render_driver(c)
    drv_frames[n] = fr
    save(sheet(fr), f'pengemudi/{n}_duduk_8f.png')

# ---------------------------------------------------------------- WHEELS
wheel_frames = {}
for st in ('kayu', 'merah'):
    fr = wheel_sheet(st)
    wheel_frames[st] = fr
    save(sheet(fr), f'roda/roda_{st}_8f.png')

# ---------------------------------------------------------------- WAGON A
A_body = body_layer('A')
save(A_body, 'gerobak_A_covered_wagon/A_badan.png')
save(hoops_png(), 'gerobak_A_covered_wagon/A_rangka_kanopi.png')
canopies = {
    'krem': (H('efe4c4'), None, False),
    'krem_tambal': (H('efe4c4'), None, True),
    'belang_merah': (H('f1e6c8'), H('d9584c'), False),
    'hijau': (H('8fae6a'), None, False),
    'biru': (H('86a3d2'), None, False),
}
canopy_imgs = {}
for n, (b, s_, pt) in canopies.items():
    im = canopy_png(b, s_, pt)
    canopy_imgs[n] = im
    save(im, f'gerobak_A_covered_wagon/A_kanopi_{n}.png')

# ---------------------------------------------------------------- WAGON B
B_body = body_layer('B')
save(B_body, 'gerobak_B_karavan_dagang/B_badan.png')
cabins = {
    'toska': (H('3f8f93'), H('f2e3b8'), H('a63a3a'), H('d85a50')),
    'kuning': (H('e0aa3e'), H('fbf1d2'), H('3f7a56'), H('c84f45')),
    'ungu': (H('7a5aa8'), H('f6e8c8'), H('8a4a2a'), H('f0b84a')),
}
cabin_imgs = {}
for n, c in cabins.items():
    im = cabin_png(*c)
    cabin_imgs[n] = im
    save(im, f'gerobak_B_karavan_dagang/B_kabin_{n}.png')
chim = b_chimney()
save(chim, 'gerobak_B_karavan_dagang/B_cerobong.png')
smoke = [b_smoke(f) for f in range(8)]
save(sheet(smoke), 'gerobak_B_karavan_dagang/B_asap_8f.png')
awn = b_awning(); sign = b_sign(); steps = b_steps()
save(awn, 'gerobak_B_karavan_dagang/B_awning_belang.png')
save(sign, 'gerobak_B_karavan_dagang/B_papan_dagang.png')
save(steps, 'gerobak_B_karavan_dagang/B_tangga_belakang.png')

# ---------------------------------------------------------------- ACCESSORIES (shared)
acc = {
    'tong_air': a_barrel(), 'tali_gulung': a_ropes(), 'sekop_beliung': a_tools(), 'lentera': a_lantern(),
    'panci_ember': a_pots(), 'roda_cadangan': a_spare_wheel('kayu'), 'karung_atap': a_roofcargo(),
    'tuas_rem': a_brake(), 'peti_ayam': a_crate_under(),
}
for n, im in acc.items():
    save(im, f'aksesoris/akses_{n}.png')
flag = [a_flag(f) for f in range(8)]
save(sheet(flag), 'aksesoris/akses_bendera_8f.png')

# ---------------------------------------------------------------- PREVIEW SCENES
BOUNCE = [0, 0, -1, -1, 0, 0, -1, -1]
HX, HY = 120, 33
DX, DY = 96, 32


def make_scene(kind, hname, harn, dname, layers, wheel, f, bounce=True):
    W_ = 216
    sc = new(W_, WH + 4)
    by = BOUNCE[f] if bounce else 0
    wag = new(WW, WH)
    for l in layers:
        wag.alpha_composite(l)
    sc.alpha_composite(wag, (0, 2 + by))
    whs = wheel_frames[wheel]
    for cx in (REAR_WHEEL_X, FRONT_WHEEL_X):
        sc.alpha_composite(whs[f], (cx - 15, 2 + Y0 + WHEEL_CY - 15))
    sc.alpha_composite(drv_frames[dname][f], (DX, 2 + DY + by))
    sc.alpha_composite(walk_h[hname][f], (HX, 2 + HY))
    sc.alpha_composite(harn_walk[harn][f], (HX, 2 + HY))
    return sc


def bg_frame(w, h, f, scroll):
    im = Image.new('RGBA', (w, h), H('9fd3e8'))
    d = ImageDraw.Draw(im)
    for y in range(0, h - 22):
        t = y / (h - 22)
        d.line([(0, y), (w, y)], fill=tuple(int(a * (1 - t) + b * t) for a, b in zip(H('86c3e6')[:3], H('d9efe0')[:3])) + (255,))
    # far hills (scroll slow)
    for x in range(w):
        yy = h - 30 - int(6 * math.sin((x + scroll * 0.25) / 22.0) + 3 * math.sin((x + scroll * 0.25) / 9.0))
        d.line([(x, yy), (x, h - 22)], fill=H('9bc58a'))
    for x in range(w):
        yy = h - 25 - int(3 * math.sin((x + scroll * 0.6) / 14.0))
        d.line([(x, yy), (x, h - 22)], fill=H('78ae6b'))
    # ground
    d.rectangle([0, h - 22, w, h], fill=H('c89a62'))
    d.rectangle([0, h - 22, w, h - 21], fill=H('8fbf62'))
    d.rectangle([0, h - 20, w, h - 20], fill=H('a97945'))
    for i in range(0, w + 40, 17):
        x = (i - int(scroll)) % (w + 20)
        d.point((x, h - 12 + (i % 5)), fill=H('9a6c3c'))
        d.point((x + 1, h - 12 + (i % 5)), fill=H('e0b988'))
    return im


def gif(name, layers, kind, hname, harn, dname, wheel, scale=4):
    W_, H_ = 250, 118
    frames = []
    for f in range(8):
        bg = bg_frame(W_, H_, f, f * 3)
        sc = make_scene(kind, hname, harn, dname, layers, wheel, f)
        bg.alpha_composite(sc, (14, H_ - sc.height - 2 + 0))
        frames.append(up(bg, scale).convert('RGB'))
    frames[0].save(f'{OUT}/preview/{name}', save_all=True, append_images=frames[1:], duration=130, loop=0, optimize=False)
    return frames


layersA = [A_body, hoops_png() if False else Image.new('RGBA', (WW, WH)), canopy_imgs['krem'], acc['tong_air'], acc['tali_gulung'],
           acc['sekop_beliung'], acc['lentera'], acc['panci_ember'], acc['karung_atap'], acc['tuas_rem'], flag[0]]
# flag animation requires per-frame layer: handle by wrapping
def layers_with_flag(base, fl=None, extra=None):
    return base


framesA = []
W_, H_ = 250, 118
for f in range(8):
    L = [A_body, canopy_imgs['krem'], acc['tong_air'], acc['tali_gulung'], acc['sekop_beliung'], acc['lentera'],
         acc['panci_ember'], acc['karung_atap'], acc['tuas_rem'], flag[f]]
    bg = bg_frame(W_, H_, f, f * 3)
    sc = make_scene('A', 'kuda_1_kastanye', 'coklat', 'pengemudi_1_pionir', L, 'kayu', f)
    bg.alpha_composite(sc, (14, H_ - sc.height - 2))
    framesA.append(up(bg, 4).convert('RGB'))
framesA[0].save(f'{OUT}/preview/preview_A_covered_wagon.gif', save_all=True, append_images=framesA[1:], duration=130, loop=0)

framesB = []
for f in range(8):
    L = [B_body, cabin_imgs['toska'], acc['tong_air'] if False else Image.new('RGBA', (WW, WH)), awn, sign, steps, chim, smoke[f],
         acc['lentera'], acc['panci_ember'], flag[f]]
    bg = bg_frame(W_, H_, f, f * 3)
    sc = make_scene('B', 'kuda_2_abu', 'hitam', 'pengemudi_2_pedagang', L, 'merah', f)
    bg.alpha_composite(sc, (14, H_ - sc.height - 2))
    framesB.append(up(bg, 4).convert('RGB'))
framesB[0].save(f'{OUT}/preview/preview_B_karavan_dagang.gif', save_all=True, append_images=framesB[1:], duration=130, loop=0)
framesA[0].save(f'{OUT}/preview/preview_A_frame.png')
framesB[0].save(f'{OUT}/preview/preview_B_frame.png')

# ---------------------------------------------------------------- CATALOG (variants)
try:
    FONT = ImageFont.load_default(size=11)
    FONT_B = ImageFont.load_default(size=14)
except Exception:
    FONT = FONT_B = ImageFont.load_default()

K = 3
cells = []


def label(img, text, w=None):
    return (img, text)


def put(canvas, img, x, y, k=K):
    canvas.alpha_composite(up(img, k), (x, y))


def crop_content(img, pad=2):
    bb = img.getbbox()
    if not bb:
        return img
    x0, y0, x1, y1 = bb
    return img.crop((max(x0 - pad, 0), max(y0 - pad, 0), min(x1 + pad, img.width), min(y1 + pad, img.height)))


cat_w = 1600
rows = []


def block(title, items, ncols, cellw, cellh, k=K):
    n = len(items)
    nrows = (n + ncols - 1) // ncols
    hh = 34 + nrows * (cellh + 24)
    im = Image.new('RGBA', (cat_w, hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((12, 6), title, fill=(255, 255, 255, 255), font=FONT_B)
    for i, (img, text) in enumerate(items):
        r, c = divmod(i, ncols)
        x, y = 12 + c * cellw, 34 + r * (cellh + 24)
        im.alpha_composite(up(img, k), (x, y))
        d.text((x, y + cellh + 4), text, fill=(235, 240, 255, 255), font=FONT)
    return im


def comp_wagon(layers, wheel, f=0):
    sc = new(WW, WH)
    for l in layers:
        sc.alpha_composite(l)
    for cx in (REAR_WHEEL_X, FRONT_WHEEL_X):
        sc.alpha_composite(wheel_frames[wheel][f], (cx - 15, Y0 + WHEEL_CY - 15))
    return sc


blocks = []
# canopies
items = [(comp_wagon([A_body, canopy_imgs[n]], 'kayu'), f'kanopi_{n}') for n in canopies]
items.append((comp_wagon([A_body, hoops_png()], 'kayu'), 'rangka_kanopi (tanpa kain)'))
blocks.append(block('GEROBAK A - varian kanopi', items, 3, 128 * 4 + 8, 96 * 4, 4))
items = [(comp_wagon([B_body, cabin_imgs[n], b_chimney()], 'merah'), f'kabin_{n}') for n in cabins]
items.append((comp_wagon([B_body, cabin_imgs['toska'], awn, sign, steps, chim, smoke[2]], 'merah'), 'toska + awning + papan + tangga + cerobong'))
blocks.append(block('GEROBAK B - varian kabin & modifikasi', items, 3, 128 * 4 + 8, 96 * 4, 4))
# accessories
items = [(crop_content(im), n) for n, im in acc.items()]
items.append((crop_content(flag[0]), 'bendera (8f)'))
items.append((crop_content(chim), 'cerobong'))
items.append((crop_content(awn), 'awning'))
items.append((crop_content(sign), 'papan_dagang'))
items.append((crop_content(steps), 'tangga'))
blocks.append(block('AKSESORIS (overlay 128x96, posisi sudah pas)', items, 4, 380, 170, 4))
H_total = sum(b.height for b in blocks) + 20
cat = Image.new('RGBA', (cat_w, H_total), H('3a4256'))
y = 10
for b in blocks:
    cat.alpha_composite(b, (0, y)); y += b.height
cat.convert('RGB').save(f'{OUT}/preview/katalog_modifikasi.png')

# horses + drivers sheet preview
ims = []
for n in ('kuda_1_kastanye', 'kuda_2_abu'):
    h = 'coklat' if n == 'kuda_1_kastanye' else 'hitam'
    ims.append(sheet([comp(walk_h[n][i], harn_walk[h][i]) for i in range(8)]))
hs = Image.new('RGBA', (768, 64 * 2 + 4 + 2 * 36 + 8), H('3a4256'))
hs.alpha_composite(ims[0], (0, 0)); hs.alpha_composite(ims[1], (0, 66))
hs.alpha_composite(sheet(drv_frames['pengemudi_1_pionir']), (0, 134))
hs.alpha_composite(sheet(drv_frames['pengemudi_2_pedagang']), (192 + 40, 134))
up(hs, 2).convert('RGB').save(f'{OUT}/preview/preview_kuda_pengemudi.png')

print('done')
