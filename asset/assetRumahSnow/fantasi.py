from bio import *

def noise_fill(img, poly_fn, rng, pal, x0, x1, y0, y1):
    for y in range(y0, y1):
        for x in range(x0, x1):
            if poly_fn(x, y):
                put(img, x, y, pal[0] if rng.random() < 0.15 else pal[1] if rng.random() < 0.7 else pal[2])

def tier(img, cx, top, base, hw, dark, light, snow=True, rng=None):
    for y in range(top, base):
        t = (y - top) / max(1, base - top)
        w = int(2 + (hw - 2) * t)
        for x in range(cx - w, cx + w + 1):
            c = light if x < cx else dark
            if snow:
                dep = int((base - top) * 0.55 + 3 * math.sin(x * 0.5))
                if y - top < dep:
                    e = dep - (y - top)
                    c = S.SN2 if e <= 1 else S.SN1 if e <= 3 else S.SN0
            put(img, x, y, c)

# ---------- pohon elf ----------
def elf_snow():
    B = SNOW
    W, H = 168, 224
    img = canvas(W, H)
    rng = random.Random(5)
    d = ImageDraw.Draw(img)
    tx0, tx1 = 62, 106
    for y in range(110, H):
        fl = max(0, y - (H - 16)) // 2
        for x in range(tx0 - fl, tx1 + fl):
            c = S.W1
            if (x - tx0) % 7 == 0 or rng.random() < 0.05:
                c = S.W2
            if x < tx0 + 3 - fl:
                c = S.W0
            if x > tx1 - 4 + fl:
                c = S.W3
            put(img, x, y, c)
    dark, light = H_('2e6a4a'), H_('3f8a5e')
    for top, base, hw in ((6, 50, 26), (30, 80, 40), (56, 112, 54), (84, 140, 66)):
        tier(img, 84, top, base, hw, dark, light)
    for lx, ly in ((60, 100), (108, 96), (84, 62), (50, 128), (118, 126), (84, 22)):
        put(img, lx, ly, S.GL0); put(img, lx + 1, ly, S.GL1); put(img, lx, ly + 1, S.GL1)
    d.ellipse([75, 146, 93, 164], fill=S.W3)
    d.ellipse([77, 148, 91, 162], fill=S.GL1)
    d.ellipse([79, 150, 89, 160], fill=S.GL0)
    rect(d, 77, 155, 91, 156, S.W3)
    rect(d, 83, 148, 85, 162, S.W3)
    rect(d, 52, 178, 116, 182, S.W1)
    rect(d, 52, 178, 116, 179, S.W0)
    for px in range(54, 116, 10):
        rect(d, px, 168, px + 2, 178, S.W2)
    rect(d, 52, 167, 116, 169, S.W2)
    B.cap(img, 52, 116, 167)
    di = S.door(img, 71, H)
    S.drift(img, 40, 128, rng, skip=(69, 99))
    finish(B, 'rumah_pohon_elf', img, di, note='Pohon cemara raksasa dengan rumah elf di batang, balkon dan jendela bulat.')

def elf_desert():
    B = DESERT
    W, H = 176, 220
    img = canvas(W, H)
    rng = random.Random(6)
    d = ImageDraw.Draw(img)
    cx = 88
    for y in range(84, H):
        t = (y - 84) / (H - 84)
        hw = int(26 + 12 * math.sin(math.pi * min(1, t * 1.0) * 0.8) + (8 if y > H - 14 else 0))
        for x in range(cx - hw, cx + hw):
            c = H_('b98f66')
            if (x - cx) % 8 == 0 or rng.random() < 0.05:
                c = H_('8f6a48')
            if x < cx - hw + 3:
                c = H_('d4ab80')
            if x > cx + hw - 5:
                c = H_('6e4e32')
            put(img, x, y, c)
    # rumah di atas pohon (sarang)
    rect(d, 44, 98, 132, 108, G.WD1)
    rect(d, 44, 98, 132, 99, G.WD0)
    for px in range(48, 132, 10):
        rect(d, px, 86, px + 2, 98, G.WD2)
    rect(d, 44, 85, 132, 87, G.WD2)
    G.mud_wall(img, 58, 50, 118, 84, rng)
    G.parapet(img, 58, 118, 44, rng, vigas=False)
    G.arch_window(img, 82, 58, 10, 14)
    G.tile_band(img, 58, 118, 74, 3)
    # kanopi daun
    for (ex, ey, rw, rh) in ((30, 40, 34, 14), (146, 40, 34, 14), (60, 22, 30, 12), (116, 22, 30, 12), (88, 12, 34, 12), (20, 60, 18, 8), (156, 60, 18, 8)):
        d.ellipse([ex - rw, ey - rh, ex + rw, ey + rh], fill=G.GRN1)
        d.ellipse([ex - rw + 4, ey - rh, ex + rw - 4, ey + rh - 5], fill=G.GRN0)
    for lx, ly in ((60, 60), (118, 62), (30, 52), (146, 52)):
        put(img, lx, ly, S.GL0); put(img, lx + 1, ly + 1, S.GL1)
    # tali tangga
    d.line([(60, 108), (60, 150)], fill=G.WD2)
    d.line([(68, 108), (68, 150)], fill=G.WD2)
    for yy in range(112, 150, 8):
        rect(d, 60, yy, 69, yy + 2, G.WD1)
    di = G.arch_door(img, 75, H)
    for (wx, wy_) in ((58, 150), (118, 150)):
        d.ellipse([wx, wy_, wx + 12, wy_ + 12], fill=G.C3)
        d.ellipse([wx + 2, wy_ + 2, wx + 10, wy_ + 10], fill=S.GL1)
        d.ellipse([wx + 3, wy_ + 3, wx + 8, wy_ + 8], fill=S.GL0)
    G.sand(img, 30, 150, rng, skip=(72, 104))
    finish(B, 'rumah_pohon_elf', img, di, note='Pohon baobab raksasa dengan sarang rumah di kanopi dan pintu di batang.')

# ---------- menara penyihir ----------
def star(img, x, y, c=G.GO0):
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        put(img, x + dx, y + dy, c)

def wizard_snow():
    B = SNOW
    W, H = 116, 240
    img = canvas(W, H)
    rng = random.Random(7)
    d = ImageDraw.Draw(img)
    stone_body(img, 28, 98, 88, H - 6, rng, (S.ST0, S.ST1, S.ST2))
    S.stone_base(img, 26, 90, H - 6, H, rng)
    rect(d, 22, 150, 94, 156, S.ST0)
    rect(d, 22, 156, 94, 158, S.ST2)
    S.snow_roof(img, 24, 92, 104, 28, 26, 6, rng, frac=0.5)
    for (wx, wy_) in ((50, 116), (50, 170)):
        fill = lambda a, b: H_('7a4ad0') if b < wy_ + 8 else H_('b07af0')
        G.fill_arch(img, wx, wy_, wy_ + 16, 10, lambda a, b: S.W3, pad=2)
        G.fill_arch(img, wx, wy_, wy_ + 16, 10, fill)
    rect(d, 56, 6, 58, 30, S.W2)
    star(img, 57, 6, G.GO0)
    star(img, 40, 70, G.GO0); star(img, 76, 58, S.IC0); star(img, 62, 84, G.GO0)
    d.ellipse([70, 66, 82, 78], fill=G.GO0)
    d.ellipse([74, 64, 86, 76], fill=S.R1)
    di = S.door(img, 45, H)
    S.torch(img, 34, 200); S.torch(img, 78, 200)
    S.drift(img, 20, 98, rng, skip=(43, 73))
    finish(B, 'menara_penyihir', img, di, note='Menara batu atap kerucut bersalju, jendela ungu, bintang dan bulan.')

def wizard_desert():
    B = DESERT
    W, H = 116, 240
    img = canvas(W, H)
    rng = random.Random(8)
    d = ImageDraw.Draw(img)
    G.dome(img, 58, 84, 36, 44, G.TURQ, bw=10, bh=6)
    d.polygon([(54, 42), (62, 42), (58, 16)], fill=G.T1)
    rect(d, 57, 8, 59, 20, G.GO1)
    d.arc([52, 4, 64, 16], 40, 320, fill=G.GO0)
    G.mud_wall(img, 28, 84, 88, 150, rng)
    G.parapet(img, 28, 88, 80, rng, vigas=False)
    G.tile_band(img, 28, 88, 96, 3)
    G.mud_wall(img, 22, 150, 94, H, rng)
    G.parapet(img, 22, 94, 142, rng)
    G.tile_band(img, 22, 94, 160, 3)
    for (wx, wy_) in ((47, 110), (47, 176)):
        G.fill_arch(img, wx, wy_, wy_ + 16, 10, lambda a, b: G.C3, pad=2)
        G.fill_arch(img, wx, wy_, wy_ + 16, 10, lambda a, b: H_('7a4ad0') if b < wy_ + 8 else H_('b07af0'))
    star(img, 36, 124, G.T1); star(img, 80, 130, G.T1)
    di = G.arch_door(img, 45, H)
    G.jar(img, 82, H, 10, 14)
    G.sand(img, 16, 100, rng, skip=(42, 74))
    finish(B, 'menara_penyihir', img, di, note='Menara batu pasir dengan kubah bawang pirus dan bulan sabit emas.')

# ---------- kuil peramal ----------
def seer_snow():
    B = SNOW
    W, H = 144, 150
    img = canvas(W, H)
    rng = random.Random(9)
    d = ImageDraw.Draw(img)
    S.ice_dome(img, 72, 84, 52, 52, seed=2)
    d.ellipse([62, 20, 82, 40], fill=S.IC2)
    d.ellipse([64, 22, 80, 38], fill=S.IC1)
    d.ellipse([66, 24, 72, 30], fill=S.SN0)
    rect(d, 66, 38, 78, 44, S.ST1)
    for sx, sy in ((50, 48), (96, 52), (74, 12), (36, 70), (110, 74)):
        star(img, sx, sy, S.IC0)
    stone_body(img, 18, 84, 126, H - 6, rng, (S.ST0, S.ST1, S.ST2))
    S.stone_base(img, 16, 128, H - 6, H, rng)
    rect(d, 16, 80, 128, 86, S.ST0)
    rect(d, 16, 76, 128, 80, S.SN0)
    rect(d, 16, 80, 128, 81, S.SN2)
    di = S.door(img, 59, H)
    for wx in (30, 98):
        G.fill_arch(img, wx, 104, 120, 14, lambda a, b: S.W3, pad=2)
        G.fill_arch(img, wx, 104, 120, 14, lambda a, b: H_('6ab0f0') if b < 114 else H_('a8d8ff'))
    S.torch(img, 48, 104); S.torch(img, 98, 104)
    S.drift(img, 10, 134, rng, skip=(57, 87))
    finish(B, 'kuil_peramal', img, di, note='Kuil kubah es dengan bola kristal besar di puncak.')

def seer_desert():
    B = DESERT
    W, H = 148, 156
    img = canvas(W, H)
    rng = random.Random(10)
    d = ImageDraw.Draw(img)
    G.dome(img, 74, 88, 54, 52, G.TURQ, bw=12, bh=7)
    d.ellipse([68, 28, 80, 40], fill=G.GO1)
    rect(d, 73, 18, 75, 30, G.GO1)
    G.mud_wall(img, 18, 88, 130, H, rng)
    G.parapet(img, 18, 130, 82, rng, vigas=False)
    G.tile_band(img, 18, 130, 98, 4)
    # mata besar
    d.ellipse([60, 104, 88, 122], fill=G.CR)
    d.ellipse([68, 105, 80, 121], fill=G.T1)
    d.ellipse([71, 108, 77, 118], fill=G.DK)
    d.arc([56, 100, 92, 126], 200, 340, fill=G.GO1)
    di = G.arch_door(img, 61, H, frame=G.T0)
    for wx in (32, 104):
        G.arch_window(img, wx, 118, 10, 14)
    for sx, sy in ((30, 70), (116, 66), (74, 12)):
        star(img, sx, sy, G.GO0)
    G.sand(img, 10, 138, rng, skip=(58, 90))
    finish(B, 'kuil_peramal', img, di, note='Kuil kubah pirus dengan mata peramal di atas pintu.')

# ---------- tambang kurcaci ----------
def mine(B, sandstone):
    W, H = 184, 136
    img = canvas(W, H)
    rng = random.Random(11 if not sandstone else 12)
    d = ImageDraw.Draw(img)
    pal = (G.C1, G.C2, G.C3) if sandstone else (S.ST0, S.ST1, S.ST2)
    hi = G.C0 if sandstone else S.ST0
    cx = 88
    def inside(x, y):
        u = (x + 0.5 - cx) / 82
        v = (H - y - 0.5) / 108
        return u * u + v * v <= 1
    for y in range(20, H):
        for x in range(4, 172):
            if inside(x, y):
                r = rng.random()
                c = pal[1]
                if r < 0.18:
                    c = pal[2]
                elif r < 0.3:
                    c = pal[0]
                if (y // 10) % 2 == 0 and r < 0.5 and sandstone:
                    c = pal[2] if r < 0.12 else c
                if x < cx - 40 and r < 0.4:
                    c = pal[0]
                if x > cx + 40 and r < 0.5:
                    c = pal[2]
                put(img, x, y, c)
    if not sandstone:
        for x in range(4, 172):
            for y in range(20, 70):
                if inside(x, y):
                    dep = 30 + 6 * math.sin(x * 0.2) + 3 * math.sin(x * 0.7)
                    if y - 20 < dep - (abs(x - cx) * 0.25):
                        put(img, x, y, S.SN0 if (y - 20) < dep - (abs(x - cx) * 0.25) - 2 else S.SN2)
    # pintu tambang
    ox, ow, oh = 75, 26, 44
    rect(d, ox - 8, H - oh - 10, ox + ow + 8, H, G.WD3)
    rect(d, ox, H - oh, ox + ow, H, G.DK)
    rect(d, ox + 6, H - 12, ox + 20, H - 4, H_('3a2e38'))
    rect(d, ox - 8, H - oh - 10, ox + ow + 8, H - oh - 4, G.WD1)
    rect(d, ox - 8, H - oh - 10, ox + ow + 8, H - oh - 9, G.WD0)
    for px in (ox - 8, ox + ow + 3):
        rect(d, px, H - oh - 4, px + 5, H, G.WD1)
        rect(d, px, H - oh - 4, px + 1, H, G.WD0)
    rect(d, ox - 12, H - oh - 14, ox + ow + 12, H - oh - 10, G.WD2)
    if not sandstone:
        B.cap(img, ox - 12, ox + ow + 12, H - oh - 14)
    S.torch(img, ox - 16, H - 40)
    # gerobak
    cxx = 130
    rect(d, cxx, H - 22, cxx + 28, H - 8, G.WD1)
    rect(d, cxx, H - 22, cxx + 28, H - 20, G.WD0)
    rect(d, cxx + 2, H - 20, cxx + 26, H - 10, S.IRON)
    for gx, gy in ((cxx + 4, H - 26), (cxx + 10, H - 28), (cxx + 17, H - 27), (cxx + 22, H - 25), (cxx + 7, H - 24)):
        rect(d, gx, gy, gx + 4, gy + 4, G.GO0 if (gx % 2) else H_('7fd0e8'))
    for wx in (cxx + 4, cxx + 20):
        d.ellipse([wx, H - 10, wx + 8, H - 2], fill=S.ST2)
        put(img, wx + 4, H - 6, S.ST0)
    rect(d, 8, H - 3, 176, H - 1, G.WD2)
    for rx_ in range(10, 176, 10):
        rect(d, rx_, H - 3, rx_ + 4, H, G.WD1)
    if sandstone:
        G.sand(img, 2, 182, rng, skip=(ox, ox + ow))
    else:
        S.drift(img, 2, 182, rng, skip=(ox, ox + ow))
    di = dict(x=ox, y=H - oh, w=ow, h=oh, cx=ox + ow // 2)
    finish(B, 'tambang_kurcaci', img, di, note='Gunung batu dengan pintu tambang berbingkai kayu, rel dan gerobak bijih.')

# ---------- pondok orc ----------
def orc(B):
    W, H = 152, 138
    img = canvas(W, H)
    rng = random.Random(13)
    d = ImageDraw.Draw(img)
    cx = 76
    hide = (H_('8a6a50'), H_('6c5040'), H_('4c3828'))
    for y in range(16, H):
        t = (y - 16) / (H - 16)
        hw = int(3 + 60 * t)
        for x in range(cx - hw, cx + hw + 1):
            k = (x - cx) // 7
            c = hide[1]
            if (x - cx) % 7 == 0:
                c = hide[2]
            elif x < cx - hw + 3:
                c = hide[0]
            elif x > cx + hw - 4:
                c = hide[2]
            elif (y // 9 + k) % 5 == 0 and rng.random() < 0.6:
                c = hide[0]
            put(img, x, y, c)
    rect(d, 16, H - 8, 136, H - 6, H_('3a2a20'))
    # tengkorak dan duri
    for sx in (24, 124):
        for k in range(3):
            d.polygon([(sx + k * 6 - 3, H - 8), (sx + k * 6 + 3, H - 8), (sx + k * 6, H - 28 - k * 3)], fill=H_('d8cdb0'))
    d.polygon([(cx - 3, 18), (cx + 3, 18), (cx, 4)], fill=H_('d8cdb0'))
    d.ellipse([cx - 7, 14, cx + 7, 28], fill=H_('ece4cc'))
    rect(d, cx - 4, 19, cx - 1, 23, G.DK); rect(d, cx + 1, 19, cx + 4, 23, G.DK)
    rect(d, cx - 4, 26, cx + 4, 28, H_('ece4cc'))
    # corat-coret cat
    for (px_, py_) in ((50, 80), (102, 84)):
        d.line([(px_, py_), (px_ + 10, py_ + 12)], fill=G.RD0, width=2)
        d.line([(px_ + 10, py_), (px_, py_ + 12)], fill=G.RD0, width=2)
    # pintu
    ox = cx - 13
    rect(d, ox - 3, H - 47, ox + 29, H, G.WD3)
    rect(d, ox, H - 44, ox + 26, H, G.DK)
    rect(d, ox + 8, H - 14, ox + 18, H - 6, H_('3a2e38'))
    d.polygon([(ox - 3, H - 47), (ox + 29, H - 47), (ox + 22, H - 54), (ox + 4, H - 54)], fill=hide[2])
    # api unggun kecil
    fx = 120
    rect(d, fx, H - 4, fx + 14, H - 1, G.WD2)
    d.polygon([(fx + 3, H - 4), (fx + 11, H - 4), (fx + 7, H - 16)], fill=S.GL1)
    d.polygon([(fx + 5, H - 4), (fx + 9, H - 4), (fx + 7, H - 11)], fill=S.GL0)
    B.cap(img, cx - 14, cx + 14, 36) if B is SNOW else None
    if B is SNOW:
        for y in range(16, 66):
            t = (y - 16) / (H - 16)
            hw = int(3 + 60 * t)
            for x in range(cx - hw, cx + hw + 1):
                dep = 34 + 5 * math.sin(x * 0.4)
                if y - 16 < dep * (0.55 + 0.2 * (x - cx) / 60 if False else 1) - abs(x - cx) * 0.3:
                    put(img, x, y, S.SN2 if (y - 16) > dep - abs(x - cx) * 0.3 - 3 else S.SN0)
        S.drift(img, 6, 146, rng, skip=(ox - 2, ox + 28))
    else:
        G.sand(img, 6, 146, rng, skip=(ox - 2, ox + 28))
    di = dict(x=ox, y=H - 44, w=26, h=44, cx=cx)
    finish(B, 'pondok_orc', img, di, note='Pondok kerucut kulit dan tulang, tengkorak di puncak, duri pagar, api unggun.')

# ---------- menara alkemis ----------
def alchemist(B):
    snow = B is SNOW
    W, H = 128, 200
    img = canvas(W, H)
    rng = random.Random(14 if snow else 15)
    d = ImageDraw.Draw(img)
    # cerobong tembaga
    cop = (H_('e6a05a'), H_('c97a3a'), H_('9a5a2a'))
    for px in (30, 92):
        rect(d, px, 20, px + 10, 80, cop[1])
        rect(d, px, 20, px + 2, 80, cop[0])
        rect(d, px + 8, 20, px + 10, 80, cop[2])
        rect(d, px - 2, 16, px + 12, 22, cop[2])
        for (ox_, oy_, r_) in ((px + 5, 8, 4), (px + 8, 0, 3)):
            d.ellipse([ox_ - r_, oy_ - r_, ox_ + r_, oy_ + r_], fill=PURPLE[1])
    body0, body1 = 24, 104
    if snow:
        stone_body(img, body0, 96, body1, H - 6, rng, (S.ST0, S.ST1, S.ST2))
        S.stone_base(img, body0 - 2, body1 + 2, H - 6, H, rng)
        rect(d, body0 - 4, 92, body1 + 4, 98, S.ST0)
        B.cap(img, body0 - 4, body1 + 4, 92)
    else:
        G.mud_wall(img, body0, 96, body1, H, rng)
        G.parapet(img, body0, body1, 90, rng, vigas=False)
        G.tile_band(img, body0, body1, 106, 3)
    pal = (H_('dff6ff'), H_('b7e0f0'), H_('8cc3dc'), H_('6aa0bd')) if snow else (cop[0], cop[1], cop[2], H_('6e3d1f'))
    G.dome(img, 64, 90, 34, 34, pal, bw=12, bh=8)
    for (bx, by, br) in ((54, 74, 4), (70, 68, 3), (62, 80, 5), (74, 78, 3)):
        d.ellipse([bx - br, by - br, bx + br, by + br], fill=PURPLE[1] if snow else GREEN[1])
        put(img, bx - 1, by - 1, PURPLE[0] if snow else GREEN[0])
    rect(d, 63, 52, 65, 58, cop[2])
    d.ellipse([60, 48, 68, 54], fill=cop[1])
    di = S.door(img, 51, H) if snow else G.arch_door(img, 51, H)
    for wx in (34, 84):
        if snow:
            S.window(img, wx, 118, 10, 14)
        else:
            G.arch_window(img, wx, 118, 10, 14)
        d.rectangle([wx, 120, wx + 9, 131], outline=None, fill=None)
    # pipa dan tong
    rect(d, 104, 130, 112, 134, cop[1])
    rect(d, 110, 130, 114, 170, cop[1])
    for bx in (6, 112):
        if snow:
            S.barrel(img, bx, H - 20, 14, 20)
        else:
            G.jar(img, bx, H, 12, 18)
        rect(d, bx + 3, H - 20, bx + 9, H - 17, GREEN[1])
    (S.drift if snow else G.sand)(img, 2, 126, rng, (49, 79))
    finish(B, 'menara_alkemis', img, di, smoke=[dict(x=35, y=-4), dict(x=97, y=-4)],
           note='Menara alkemis: kubah kaca berisi cairan ungu, dua cerobong tembaga, tong ramuan.')

def tabib(B):
    props = [('herbs', -22), ('jar', -50)] if B is DESERT else [('herbs', -22), ('barrel', -52)]
    if B is DESERT:
        props.append(('cactus', 46))
    house(B, 'pondok_tabib', 108, 68, 44, 'gable', wins=(-34,), icon_name='leaf', props=props, dcx=12, seed=33)

def build_all(B):
    if B is SNOW:
        elf_snow(); wizard_snow(); seer_snow()
    else:
        elf_desert(); wizard_desert(); seer_desert()
    mine(B, B is DESERT)
    orc(B)
    alchemist(B)
    tabib(B)

if __name__ == '__main__':
    build_all(SNOW)
    build_all(DESERT)
    print('ok')
