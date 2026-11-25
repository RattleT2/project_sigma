from bio import *

def gudang(B):
    house(B, 'depot_gudang', 212, 86, 46, 'wide', wins=(-92, -4), icon_name='box',
          props=[('bigdoor', 22), ('crate2', -102), ('barrel', 100)], dcx=-52, seed=41, sign_dx=-16)

def kantor(B):
    house(B, 'depot_kantor_pertukaran', 150, 76, 46, 'gable', wins=(), icon_name='coin',
          props=[('counter', 6), ('chimney', -44), ('flag2', 52), ('sack', -70)], dcx=-34, seed=43, sign_dx=62)

def dermaga(B):
    W, H = 190, 50
    deck = H - 32
    img = canvas(W, H)
    rng = random.Random(45)
    d = ImageDraw.Draw(img)
    px0 = 44
    if B is SNOW:
        stone_body(img, px0, deck + 6, W - 2, H, rng, (S.ST0, S.ST1, S.ST2))
    else:
        G.mud_wall(img, px0, deck + 6, W - 2, H, rng)
    rect(d, px0 - 2, deck, W, deck + 6, B.W[1])
    rect(d, px0 - 2, deck, W, deck + 1, B.W[0])
    rect(d, px0 - 2, deck + 4, W, deck + 6, B.W[2])
    for x in range(px0 + 8, W, 14):
        rect(d, x, deck + 1, x + 1, deck + 5, B.W[3])
    for x in range(px0 + 6, W - 4, 40):
        rect(d, x, deck + 6, x + 6, H, B.W[1])
        rect(d, x, deck + 6, x + 1, H, B.W[0])
    for i in range(4):
        top = H - 8 * (i + 1)
        x0 = 4 + 10 * i
        rect(d, x0, top, x0 + 10, H, B.W[1])
        rect(d, x0, top, x0 + 10, top + 2, B.W[0])
        rect(d, x0, top + 6, x0 + 10, H, B.W[2]) if False else None
        rect(d, x0 + 9, top, x0 + 10, H, B.W[3])
        B.cap(img, x0, x0 + 10, top)
    for bx in (px0 + 22, W - 34):
        rect(d, bx, deck - 9, bx + 6, deck, B.W[2])
        rect(d, bx - 1, deck - 11, bx + 7, deck - 8, B.W[1])
        rect(d, bx - 1, deck - 11, bx + 7, deck - 10, B.W[0])
        rect(d, bx - 2, deck - 6, bx + 8, deck - 4, G.C0 if B is DESERT else S.SN1)
        B.cap(img, bx - 1, bx + 7, deck - 11)
    lantern(B, img, W - 12, deck - 22)
    rect(d, W - 11, deck - 14, W - 9, deck, B.W[2])
    finish(B, 'depot_dermaga_muat', img, None,
           note='Dermaga muat setinggi 32 px dari tanah (deck_y). Parkirkan gerobak dengan bagian belakang di ujung kanan.')
    META[B.key]['depot_dermaga_muat_%s' % B.key].update(deck_y=deck, tinggi_dari_tanah=32, tangga_x=[4, 44])

def crane_img(B, dx):
    W, H = 160, 164
    img = canvas(W, H)
    d = ImageDraw.Draw(img)
    rng = random.Random(47)
    if B is SNOW:
        stone_body(img, 8, H - 14, 52, H, rng, (S.ST0, S.ST1, S.ST2))
    else:
        G.mud_wall(img, 8, H - 14, 52, H, rng)
    rect(d, 20, 26, 34, H - 14, B.W[1])
    rect(d, 20, 26, 22, H - 14, B.W[0])
    rect(d, 32, 26, 34, H - 14, B.W[3])
    for yy in range(40, H - 14, 24):
        d.line([(20, yy), (34, yy + 12)], fill=B.W[3])
    rect(d, 14, 20, 142, 28, B.W[1])
    rect(d, 14, 20, 142, 21, B.W[0])
    rect(d, 14, 26, 142, 28, B.W[2])
    d.line([(34, 74), (110, 28)], fill=B.W[2], width=3)
    d.line([(34, 64), (80, 28)], fill=B.W[3], width=2)
    rect(d, 4, 22, 22, 36, S.ST1)
    rect(d, 4, 22, 22, 24, S.ST0)
    B.cap(img, 14, 142, 20)
    rect(d, 130, 28, 136, 36, S.IRON)
    d.ellipse([129, 34, 137, 42], fill=S.IRON)
    rx = 133 + dx * 0.4
    hx = 133 + dx
    d.line([(133, 38), (int(hx), 90)], fill=G.C3 if B is DESERT else S.W2, width=1)
    cx_ = int(hx)
    rect(d, cx_ - 2, 88, cx_ + 2, 94, S.IRON)
    crate(B, img, cx_ - 13, 118, 26, 24, cap=True)
    d.line([(cx_ - 8, 94), (cx_ - 13, 96)], fill=S.IRON)
    d.line([(cx_ + 8, 94), (cx_ + 13, 96)], fill=S.IRON)
    return img

def derek(B):
    img = crane_img(B, 0)
    finish(B, 'depot_derek', img, None, note='Derek muat; lihat sheet animasi untuk gerakan berayun (30 fps).')
    frames = 24
    fw, fh = img.width, img.height
    sheet = canvas(fw * frames, fh)
    for f in range(frames):
        fr = outline(crane_img(B, 8 * math.sin(2 * math.pi * f / frames)), B.OL)
        sheet.paste(fr, (f * fw, 0))
    od = os.path.join('/home/claude', 'kota_' + B.key)
    name = f'depot_derek_{B.key}_sheet'
    sheet.save(os.path.join(od, name + '.png'))
    META[B.key][name] = dict(file=name + '.png', frame_w=fw, frame_h=fh, frames=frames, fps=30,
                             note='Animasi derek berayun, loop.')

def stacks(B):
    # 1: kotak
    img = canvas(64, 54)
    for x in (2, 38):
        crate(B, img, x, 54, 18, 16, cap=True)
    crate(B, img, 20, 54, 18, 16)
    for x in (11, 29):
        crate(B, img, x, 38, 18, 16)
    crate(B, img, 20, 22, 18, 16, cap=True)
    finish(B, 'depot_tumpukan_kotak', img, note='Tumpukan kotak piramida.')
    # 2: tong / guci + karung
    img = canvas(80, 52)
    for x in (4, 22, 40):
        B.barrel(img, x, 52, 16, 20)
    B.barrel(img, 13, 32, 16, 20)
    B.barrel(img, 31, 32, 16, 20)
    sack(img, 58, 52, 16, 15)
    sack(img, 62, 38, 14, 14)
    finish(B, 'depot_tumpukan_tong', img, note='Tumpukan tong (salju) atau guci (gurun) dengan karung.')
    # 3: karung dan gulungan
    img = canvas(84, 46)
    d = ImageDraw.Draw(img)
    for x in (2, 20, 38):
        sack(img, x, 46, 17, 16)
    sack(img, 11, 30, 16, 15)
    sack(img, 29, 30, 16, 15)
    col = (H_('e8e2d6'), H_('b8b0a0')) if B is SNOW else (G.RD0, G.RD1)
    col2 = (H_('9a7a60'), H_('6e5238')) if B is SNOW else (G.T1, G.T2)
    for k, cc in enumerate((col, col2)):
        yy = 46 - 11 * (k + 1)
        rect(d, 58, yy, 82, yy + 10, cc[0])
        rect(d, 58, yy + 7, 82, yy + 10, cc[1])
        d.ellipse([54, yy, 62, yy + 10], fill=cc[1])
        d.ellipse([57, yy + 3, 61, yy + 7], fill=cc[0])
    B.cap(img, 58, 82, 24)
    finish(B, 'depot_tumpukan_karung', img, note='Tumpukan karung dan gulungan kain/kulit.')

def timbangan(B):
    img = canvas(48, 58)
    d = ImageDraw.Draw(img)
    H = 58
    rect(d, 14, H - 8, 34, H, S.ST1)
    rect(d, 14, H - 8, 34, H - 6, S.ST0)
    rect(d, 22, 12, 26, H - 8, B.W[2])
    rect(d, 22, 12, 23, H - 8, B.W[0])
    d.polygon([(3, 18), (3, 15), (24, 11), (45, 15), (45, 18), (24, 14)], fill=B.W[1])
    rect(d, 22, 8, 26, 14, S.IRON)
    put(img, 24, 8, G.GO0)
    d.line([(5, 18), (5, 34)], fill=S.IRON); d.line([(5, 34), (13, 34)], fill=S.IRON)
    d.line([(43, 18), (43, 26)], fill=S.IRON)
    rect(d, 0, 34, 18, 37, S.IRON)
    rect(d, 36, 26, 48, 29, S.IRON)
    for gx in (3, 8, 12):
        rect(d, gx, 30, gx + 3, 34, G.GO0)
    rect(d, 39, 21, 44, 26, S.ST1)
    B.cap(img, 3, 45, 15)
    finish(B, 'depot_timbangan', img, note='Timbangan dagang dua piring.')

def papan(B):
    W, H = 64, 74
    img = canvas(W, H)
    d = ImageDraw.Draw(img)
    for px in (8, 50):
        rect(d, px, 24, px + 5, H, B.W[1])
        rect(d, px, 24, px + 1, H, B.W[0])
    rect(d, 2, 8, 62, 52, B.W[3])
    rect(d, 4, 10, 60, 50, NAVY)
    d.polygon([(0, 10), (64, 10), (60, 2), (4, 2)], fill=B.W[2])
    rect(d, 0, 8, 64, 10, B.W[1])
    B.cap(img, 4, 60, 2)
    for i, yy in enumerate((13, 25, 37)):
        icon(img, 8, yy, 'coin', G.GO0, G.GO1)
        for k in range(3 + i):
            rect(d, 22 + k * 7, yy + 1, 25 + k * 7, yy + 7, G.CR)
        rect(d, 22, yy + 9, 56, yy + 10, S.ST2) if False else None
    S.drift(img, 2, 62, random.Random(2)) if B is SNOW else G.sand(img, 2, 62, random.Random(2))
    finish(B, 'depot_papan_harga', img, note='Papan harga (ikon koin dan tanda hitung, tanpa teks).')

def tiang(B):
    W, H = 52, 84
    img = canvas(W, H)
    d = ImageDraw.Draw(img)
    rect(d, 24, 8, 29, H, B.W[1])
    rect(d, 24, 8, 25, H, B.W[0])
    rect(d, 28, 8, 29, H, B.W[3])
    d.polygon([(22, 8), (31, 8), (26, 2)], fill=B.W[2])
    B.cap(img, 23, 30, 8)
    for (x0, x1, y, rt) in ((26, 48, 14, True), (4, 26, 30, False), (26, 50, 46, True)):
        if rt:
            pts = [(x0, y), (x1 - 6, y), (x1, y + 5), (x1 - 6, y + 10), (x0, y + 10)]
        else:
            pts = [(x1, y), (x0 + 6, y), (x0, y + 5), (x0 + 6, y + 10), (x1, y + 10)]
        d.polygon(pts, fill=B.W[1])
        rect(d, min(x0, x1) + 2, y, max(x0, x1) - 2, y + 1, B.W[0])
        rect(d, min(x0, x1) + 2, y + 9, max(x0, x1) - 2, y + 10, B.W[3])
        put(img, 27 if rt else 23, y + 5, G.GO0)
    (S.drift if B is SNOW else G.sand)(img, 12, 40, random.Random(3))
    finish(B, 'depot_tiang_arah', img, note='Tiang penunjuk arah tiga papan.')

# ---------- gerbang masuk samping (dua lapis) ----------
def gate_side(B):
    mx = 14
    W, H = 328, 206
    clear = 118
    yc = H - clear
    back = canvas(W, H)
    front = canvas(W, H)
    rng = random.Random(51)
    d = ImageDraw.Draw(back)
    xa, xb = mx, W - mx
    p = 26
    # interior lorong
    rect(d, xa + p, yc, xb - p, H, B.W[3])
    if B is SNOW:
        for x in range(xa + p, xb - p, 7):
            rect(d, x, yc, x + 1, H, B.W[2])
        for x in range(xa + p, xb - p, 48):
            rect(d, x, yc, x + 7, H, B.W[1])
            rect(d, x, yc, x + 1, H, B.W[0])
    else:
        rect(d, xa + p, yc, xb - p, H, H_('5a4030'))
        for _ in range(500):
            put(back, rng.randint(xa + p, xb - p - 1), rng.randint(yc, H - 1), H_('6e5038') if rng.random() < 0.5 else H_('48321f'))
        G.tile_band(back, xa + p, xb - p, yc + 40, 3)
        for x in range(xa + p, xb - p, 56):
            rect(d, x, yc, x + 8, H, G.C3)
            rect(d, x, yc, x + 1, H, G.C2)
    rect(d, xa + p, yc, xb - p, yc + 14, B.W[2])
    rect(d, xa + p, yc, xb - p, yc + 2, B.W[0])
    for x in range(xa + p + 20, xb - p, 36):
        rect(d, x, yc + 14, x + 8, yc + 20, B.W[1])
    rect(d, xa + p, H - 8, xb - p, H, B.W[3] if B is SNOW else H_('8c6a44'))
    rect(d, xa + p, H - 8, xb - p, H - 7, B.W[2] if B is SNOW else H_('a8844e'))
    for tx in (xa + p + 50, xb - p - 56):
        S.torch(back, tx, H - 96)
    G.banner(back, (W // 2) - 8, yc + 18, 16, 32)
    lantern(B, back, W // 2 + 40, yc + 14)
    lantern(B, back, W // 2 - 46, yc + 14)
    sack(back, xa + p + 8, H - 8, 14, 13)
    B.barrel(back, xb - p - 24, H - 8, 14, 18) if B is SNOW else G.jar(back, xb - p - 24, H - 8, 12, 16)
    # ruang atas dan atap
    if B is SNOW:
        S.log_wall(back, xa, 40, xb, yc, rng)
        rect(d, xa, yc - 4, xb, yc, S.W3)
        for wx in (70, 130, 198, 258):
            S.window(back, wx, 54, 12, 14)
        S.snow_roof(back, xa, xb, 44, 2, 40, 10, rng, frac=0.55)
    else:
        G.mud_wall(back, xa, 40, xb, yc, rng)
        G.merlons(back, xa, xb, 22, 8, 16, 10, 3)
        G.parapet(back, xa, xb, 30, rng, vigas=False)
        G.tile_band(back, xa, xb, 40, 4)
        G.tile_band(back, xa, xb, yc - 8, 4)
        for wx in (74, 134, 194, 254):
            G.arch_window(back, wx, 56, 10, 14)
    # pilar
    for (px0, px1) in ((xa, xa + p), (xb - p, xb)):
        for img_ in (back, front):
            dd = ImageDraw.Draw(img_)
            if B is SNOW:
                k = px0
                while k < px1:
                    w_ = min(9, px1 - k)
                    rect(dd, k, yc - 4, k + w_, H, S.W1)
                    rect(dd, k, yc - 4, k + 1, H, S.W0)
                    rect(dd, k + w_ - 2, yc - 4, k + w_, H, S.W2)
                    k += w_
                for yy in range(yc + 8, H, 22):
                    rect(dd, px0, yy, px1, yy + 2, S.W3)
                rect(dd, px0 - 3, yc - 8, px1 + 3, yc - 4, S.W2)
                B.cap(img_, px0 - 3, px1 + 3, yc - 8)
            else:
                G.mud_wall(img_, px0, yc - 4, px1, H, rng)
                G.tile_band(img_, px0, px1, yc + 6, 3)
                G.tile_band(img_, px0, px1, yc + 64, 3)
                rect(dd, px0 - 2, yc - 8, px1 + 2, yc - 4, G.C0)
    # jeruji gerbang (portcullis terangkat) di lapis depan
    fd = ImageDraw.Draw(front)
    for (bx0, bx1) in ((xa + p, xa + p + 10), (xb - p - 10, xb - p)):
        rect(fd, bx0, yc + 14, bx1, yc + 18, S.IRON)
        for bx in range(bx0 + 1, bx1, 4):
            rect(fd, bx, yc + 18, bx + 2, yc + 34, S.IRON)
            fd.polygon([(bx, yc + 34), (bx + 2, yc + 34), (bx + 1, yc + 40)], fill=S.ST0)
    # simpan
    od = os.path.join('/home/claude', 'kota_' + B.key)
    for nm, im in (('belakang', back), ('depan', front)):
        o = outline(im, B.OL)
        # hilangkan outline di area lorong (bagian tengah) agar bersih
        o.save(os.path.join(od, f'depot_gerbang_samping_{nm}_{B.key}.png'))
        META[B.key][f'depot_gerbang_samping_{nm}_{B.key}'] = dict(
            file=f'depot_gerbang_samping_{nm}_{B.key}.png', w=W, h=H, pivot=[W // 2, H],
            lorong=dict(x=xa + p, y=yc, w=(xb - xa - 2 * p), h=clear), tinggi_lorong=clear,
            lapis='belakang (gambar di bawah NPC/karavan)' if nm == 'belakang' else 'depan (gambar di atas NPC/karavan)',
            note='Gerbang depot dilalui menyamping (kiri-kanan). Gambar lapis belakang, lalu NPC/karavan, lalu lapis depan.')
    comb = Image.alpha_composite(outline(back, B.OL), outline(front, B.OL))
    comb.save(os.path.join(od, f'depot_gerbang_samping_{B.key}.png'))
    META[B.key][f'depot_gerbang_samping_{B.key}'] = dict(file=f'depot_gerbang_samping_{B.key}.png', w=W, h=H,
        pivot=[W // 2, H], lorong=dict(x=xa + p, y=yc, w=(xb - xa - 2 * p), h=clear),
        note='Gabungan belakang+depan (untuk dipakai statis tanpa lapisan).')

def build(B):
    gudang(B); kantor(B); dermaga(B); derek(B); stacks(B); timbangan(B); papan(B); tiang(B); gate_side(B)

if __name__ == '__main__':
    build(SNOW)
    build(DESERT)
    print('ok')
