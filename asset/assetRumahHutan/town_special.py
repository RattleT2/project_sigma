from town_build import *

def forge_extra(img, sk, c):
    d = ImageDraw.Draw(img)
    x0, Hh = c['x0'], c['Hh']
    ax, aw, atop = x0 + 8, 52, c['Hh'] - 56
    fill_arch(img, ax, atop, Hh, aw, lambda a, b: sk.stone[2], pad=4)
    fill_arch(img, ax, atop, Hh, aw, lambda a, b: sk.stone[0], pad=3)
    fill_arch(img, ax, atop, Hh, aw, lambda a, b: H('2b2024') if b < Hh - 20 else H('3a2a2c'))
    rect(d, ax + 34, Hh - 26, ax + 50, Hh, sk.stone[1])
    rect(d, ax + 34, Hh - 26, ax + 50, Hh - 24, sk.stone[0])
    rect(d, ax + 37, Hh - 20, ax + 47, Hh - 6, H('1a1214'))
    rect(d, ax + 38, Hh - 15, ax + 46, Hh - 6, GLOW[2])
    rect(d, ax + 40, Hh - 19, ax + 44, Hh - 11, GLOW[1])
    rect(d, ax + 41, Hh - 17, ax + 43, Hh - 13, GLOW[0])
    rect(d, ax + 10, Hh - 8, ax + 20, Hh, H('5a4a3a'))
    rect(d, ax + 6, Hh - 14, ax + 24, Hh - 8, H('4a4e5a'))
    rect(d, ax + 6, Hh - 14, ax + 24, Hh - 13, H('8a90a0'))
    rect(d, ax + 3, Hh - 12, ax + 7, Hh - 10, H('4a4e5a'))
    for tx in (ax + 12, ax + 18, ax + 24):
        rect(d, tx, atop + 12, tx + 1, atop + 26, H('9aa0b0'))
        rect(d, tx - 1, atop + 26, tx + 2, atop + 29, H('5a5e6a'))
    rect(d, ax - 5, Hh - 2, ax + aw + 5, Hh, sk.stone[0])

def warehouse_extra(img, sk, c):
    d = ImageDraw.Draw(img)
    cx, Hh, uy0 = c['cx'], c['Hh'], c['uy0']
    ax, aw, atop = cx - 10, 62, Hh - 50
    fill_arch(img, ax, atop, Hh, aw, lambda a, b: sk.stone[2], pad=4)
    fill_arch(img, ax, atop, Hh, aw, lambda a, b: sk.stone[0], pad=3)
    fill_arch(img, ax, atop, Hh, aw, lambda a, b: H('2b2024'))
    crate(img, sk, ax + 6, Hh, 18, 16); crate(img, sk, ax + 24, Hh, 18, 16); crate(img, sk, ax + 15, Hh - 16, 18, 16)
    barrel(img, sk, ax + 44, Hh, 13, 17)
    rect(d, ax - 5, Hh - 2, ax + aw + 5, Hh, sk.stone[0])
    wood = mix(sk.timber[1], H('c89a64'), 0.3)
    rect(d, cx - 9, uy0 + 9, cx + 9, uy0 + 33, sk.timber[2])
    rect(d, cx - 7, uy0 + 11, cx + 7, uy0 + 33, wood)
    rect(d, cx - 1, uy0 + 11, cx + 1, uy0 + 33, sk.timber[2])
    rect(d, cx - 7, uy0 + 20, cx + 7, uy0 + 21, H('3a3438'))
    bx = cx + 9
    rect(d, bx, uy0 + 5, bx + 40, uy0 + 9, sk.timber[1])
    rect(d, bx, uy0 + 5, bx + 40, uy0 + 6, sk.timber[0])
    d.line([(bx + 6, uy0 + 20), (bx + 30, uy0 + 9)], fill=sk.timber[2], width=2)
    d.ellipse([bx + 36, uy0 + 9, bx + 43, uy0 + 16], fill=H('4a4e5a'))
    rect(d, bx + 39, uy0 + 16, bx + 40, uy0 + 34, H('c8b890'))
    rect(d, bx + 37, uy0 + 34, bx + 43, uy0 + 36, H('4a4e5a'))

def herbs_extra(img, sk, c):
    d = ImageDraw.Draw(img)
    cx, Hh = c['cx'], c['Hh']
    x = cx + 8
    y = Hh - 62
    rect(d, x, y, x + 38, y + 2, sk.timber[2])
    for i in range(5):
        px = x + 3 + i * 7
        rect(d, px, y + 2, px + 1, y + 6, sk.timber[2])
        d.polygon([(px - 2, y + 6), (px + 3, y + 6), (px + 1, y + 17)], fill=GRN[(i % 2)])
        put(img, px, y + 10, H('b6f07a'))

def office(sk):
    townhouse(sk, 'depot_kantor_pertukaran', W=104, floors=2, roof='blue', ground='stone', door_dx=26,
              gwins=((-24, 'shop'),), awn=(H('3f6fa8'), H('f0c840')), icon='coin',
              props=(('crate', -62), ('sack', 58)), seed=31)

def gudang(sk):
    townhouse(sk, 'depot_gudang', W=152, floors=2, roof='red', ground='stone', door_dx=-46, gwins=(), icon='box',
              chim=0.34, props=(('crate2', -102),), seed=33, rh_extra=6, extra=warehouse_extra, nb=5)

def smithy(sk):
    townhouse(sk, 'rumah_pandai_besi', W=112, floors=1, roof='slate', ground='stone', door_dx=36, gwins=(),
              chim=-0.22, chim_kind='stone', chim_up=34, icon='anvil', dorm=False,
              props=(('barrel', 64), ('wood', -72)), seed=21, extra=forge_extra)

def tabib(sk):
    townhouse(sk, 'rumah_tabib', W=100, floors=1, roof='green', ground='plaster', door_dx=-16,
              gwins=((26, 'plain'),), chim=0.28, chim_kind='stone', icon='leaf', dorm=False,
              props=(('jar', -62), ('planter', 52)), seed=23, shut=2, extra=herbs_extra)

def wing_roof(img, sk, x_a, y_a, x_b, y_b, pal, thick, rng):
    # bidang atap miring dari (x_a,y_a) ke (x_b,y_b); isi genteng
    lo, hi = min(x_a, x_b), max(x_a, x_b)
    for x in range(lo, hi + 1):
        t = (x - x_a) / (x_b - x_a) if x_b != x_a else 0
        yt = int(round(y_a + (y_b - y_a) * t))
        for k in range(thick):
            y = yt + k
            ri = k // 5
            yy = k % 5
            off = (ri % 2) * 3
            col = (x + off) // 6
            xx = (x + off) % 6
            hs = (col * 31 + ri * 17) % 5
            base = pal[1]
            if hs == 0: base = mix(pal[1], pal[0], 0.35)
            elif hs == 1: base = mix(pal[1], pal[2], 0.25)
            c = pal[2] if (yy == 4 or k == thick - 1) else mix(base, pal[0], 0.5) if yy == 0 else mix(base, pal[2], 0.5) if xx == 5 else base
            put(img, x, y, c)
        if sk.cover:
            put(img, x, yt - 1, sk.cover); put(img, x, yt - 2, sk.cover)
    return

def church(sk):
    rng = random.Random(77)
    W = 124
    mxl, mxr = 24, 34
    Hh = 178
    Wc = W + mxl + mxr
    img = canvas(Wc, Hh)
    d = ImageDraw.Draw(img)
    x0 = mxl
    x1 = x0 + W
    cx = (x0 + x1) // 2
    tw = 23
    wall_h = 72
    pal = sk.roofs['blue']
    stone_wall(img, x0, Hh - wall_h, x1, Hh, sk.stone, rng, sk)
    ty0 = Hh - 134
    stone_wall(img, cx - tw, ty0, cx + tw, Hh, sk.stone, rng, sk)
    rect(d, cx - tw - 2, ty0 + 70, cx + tw + 2, ty0 + 73, sk.stone[0])
    rect(d, cx - tw - 2, ty0 + 73, cx + tw + 2, ty0 + 75, sk.stone[2])
    fill_arch(img, cx - 10, ty0 + 8, ty0 + 34, 20, lambda a, b: sk.stone[2], pad=2)
    fill_arch(img, cx - 10, ty0 + 8, ty0 + 34, 20, lambda a, b: H('2b2024'))
    d.ellipse([cx - 6, ty0 + 18, cx + 6, ty0 + 31], fill=GOLD[0])
    rect(d, cx - 6, ty0 + 28, cx + 6, ty0 + 31, GOLD[1])
    rect(d, cx - 1, ty0 + 14, cx + 1, ty0 + 19, GOLD[1])
    d.ellipse([cx - 11, ty0 + 40, cx + 11, ty0 + 62], fill=sk.stone[0])
    d.ellipse([cx - 9, ty0 + 42, cx + 9, ty0 + 60], fill=GOLD[1])
    d.ellipse([cx - 7, ty0 + 44, cx + 7, ty0 + 58], fill=H('3f6fa8'))
    d.line([(cx - 6, ty0 + 51), (cx + 6, ty0 + 51)], fill=GOLD[0])
    d.line([(cx, ty0 + 45), (cx, ty0 + 57)], fill=GOLD[0])
    for sgn in (-1, 1):
        if sgn < 0:
            wing_roof(img, sk, x0 - 8, Hh - wall_h + 4, cx - tw, Hh - wall_h - 24, pal, 16, rng)
        else:
            wing_roof(img, sk, cx + tw, Hh - wall_h - 24, x1 + 8, Hh - wall_h + 4, pal, 16, rng)
    rows = draw_roof(img, sk, pal, cx - tw - 3, cx + tw + 3, ty0 + 3, ty0 - 48, over=2, ridge=0, kind='tile', rng=rng)
    sk.roof_decor(img, rows, ty0 - 48, ty0 + 3, rng, pal)
    rect(d, cx - 1, ty0 - 62, cx + 1, ty0 - 46, GOLD[1])
    rect(d, cx - 4, ty0 - 58, cx + 4, ty0 - 56, GOLD[1])
    window(img, sk, x0 + 22, Hh - 56, 10, 20, shut=False, box=False, glass=(H('7ab0f0'), H('4a78c0')))
    window(img, sk, x1 - 22, Hh - 56, 10, 20, shut=False, box=False, glass=(H('f08a7a'), H('c04a4a')))
    di = door(img, sk, cx - 13, Hh)
    l, r = rows[ty0 + 2]
    sk.eave_decor(img, l, r, ty0 + 3, rng)
    hang_sign(img, sk, x1 + 1, Hh - 56, 'sun')
    sk.ground_fx(img, x0 - 14, x1 + 22, rng, skip=(cx - 17, cx + 17))
    finish(sk, 'rumah_pendeta', img, di, note='Gereja: menara lonceng berpucuk, sayap atap miring, jendela kaca patri.')

def manor(sk):
    rng = random.Random(88)
    W = 172
    gh, uh, rh, topp = 64, 54, 60, 24
    mxl, mxr = 26, 34
    Hh = topp + rh + uh + gh
    Wc = W + mxl + mxr
    img = canvas(Wc, Hh)
    d = ImageDraw.Draw(img)
    x0 = mxl
    x1 = x0 + W
    cx = (x0 + x1) // 2
    gy0 = Hh - gh
    uy0 = gy0 - uh
    eave = uy0 + 3
    pal = sk.roofs['blue']
    stone_wall(img, x0, uy0, x1, Hh, sk.stone, rng, sk)
    rect(d, x0 - 2, gy0 - 2, x1 + 2, gy0 + 1, sk.stone[0])
    rect(d, x0 - 2, gy0 + 1, x1 + 2, gy0 + 3, sk.stone[2])
    layer = canvas(Wc, Hh)
    ww = 66
    rows_c = draw_roof(img, sk, sk.roofs['slate'], cx - 34, cx + 34, eave, eave - 30, over=2, ridge=14, kind='tile', rng=rng)
    rows_l = draw_roof(img, sk, pal, x0, x0 + ww, eave, eave - rh, over=5, ridge=0, kind='tile', rng=rng)
    rows_r = draw_roof(img, sk, pal, x1 - ww, x1, eave, eave - rh, over=5, ridge=0, kind='tile', rng=rng)
    sk.roof_decor(img, rows_l, eave - rh, eave, rng, pal)
    sk.roof_decor(img, rows_r, eave - rh, eave, rng, pal)
    sk.roof_decor(img, rows_c, eave - 30, eave, rng, sk.roofs['slate'])
    for rows_ in (rows_l, rows_r):
        l, r = rows_[eave - 1]
        sk.eave_decor(img, l, r, eave, rng)
    for xc in (x0 + ww // 2, x1 - ww // 2):
        d.ellipse([xc - 8, eave - rh + 26, xc + 8, eave - rh + 42], fill=sk.stone[0])
        d.ellipse([xc - 6, eave - rh + 28, xc + 6, eave - rh + 40], fill=H('2b3a6a'))
        d.ellipse([xc - 3, eave - rh + 31, xc + 3, eave - rh + 37], fill=GOLD[0])
    for xc in (x0 + ww // 2, x1 - ww // 2, cx):
        window(img, sk, xc, uy0 + 10, 12, 20, shut=sk.shutters[0], box=False)
    for xc in (x0 + ww // 2, x1 - ww // 2):
        window(img, sk, xc, Hh - 46, 12, 18, shut=sk.shutters[0], box=True, rng=rng)
    for sx in (cx - 28, cx + 22):
        rect(d, sx, gy0 + 4, sx + 6, Hh, sk.stone[0])
        rect(d, sx + 4, gy0 + 4, sx + 6, Hh, sk.stone[2])
        rect(d, sx - 1, gy0 + 2, sx + 7, gy0 + 5, sk.stone[0])
    rect(d, cx - 30, gy0 - 1, cx + 30, gy0 + 3, sk.stone[0])
    di = door(img, sk, cx - 13, Hh)
    banner(img, x0 + 4, uy0 + 14, 14, 28, RED, sk) if False else None
    banner(img, x0 + 8, gy0 + 6, 14, 26, H('3f6fa8'), sk)
    banner(img, x1 - 22, gy0 + 6, 14, 26, H('3f6fa8'), sk)
    hang_sign(img, sk, x1 + 1, Hh - 56, 'crown')
    sk.ground_fx(img, x0 - 14, x1 + 22, rng, skip=(cx - 17, cx + 17))
    finish(sk, 'rumah_bangsawan', img, di, note='Rumah bangsawan batu: dua sayap beratap runcing, pilaster dan pintu tengah.')

def barak(sk):
    townhouse(sk, 'barak', W=156, floors=2, roof='red', ground='stone', upper='stone', door_dx=0,
              gwins=((-48, 'plain'), (-26, 'plain'), (26, 'plain'), (48, 'plain')), icon='shield',
              chim=0.34, chim_kind='stone', props=(('banner', -86), ('banner2', 74), ('lamp', 30)), seed=17, rh_extra=-4)

def build_all(sk):
    build_jobs(sk)
    smithy(sk); tabib(sk); office(sk); gudang(sk); church(sk); manor(sk); barak(sk)

if __name__ == '__main__':
    for sk in (SNOW, DESERT, FOREST):
        build_all(sk)
    print('ok')
