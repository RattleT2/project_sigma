from bld_core import *

def townhouse(w=116, floor_h=(54, 46), roof_h=46, roof_c=H('c8573d'), roof_kind='tile', ground='stone', gwall=H('b8aa94'), plaster=H('eadfc0'),
              beam=H('5a3a22'), shutter=H('4f80c0'), sign=None, awn=None, chim='r', door_c=H('7a4a2a'), flower=H('e86a7a'), seed=1,
              upper_over=4, door_x=None, props=(), bays=4, stories=2, brace='x', attic=True, chim_c=H('a87a64'), door_w=26, shop=None, pad_r=0, lit=False):
    M = 12; fw = w - 2 * M
    Htot = 7 + sum(floor_h[:stories]) + roof_h + 16
    p = Pen(w + pad_r, Htot)
    y = Htot - 1
    foundation(p, M - 1, M + fw, y - 6, y, seed=seed + 20)
    # ---- lantai dasar
    g1 = y - 7; g0 = g1 - floor_h[0] + 1
    if ground == 'stone': stone_rect(p, M, g0, M + fw - 1, g1, gwall, seed=seed)
    elif ground == 'brick': brick_rect(p, M, g0, M + fw - 1, g1, gwall, seed=seed)
    else:
        plaster_rect(p, M, g0, M + fw - 1, g1, plaster, seed=seed); timber_frame(p, M, g0, M + fw - 1, g1, beam, bays=bays, brace=brace)
    dx = door_x if door_x is not None else (fw - door_w) // 2
    door(p, M + dx, g1 - 44, door_w, 44, wood=door_c)
    if door_w > 30: p.vline(M + dx + door_w // 2, g1 - 40, g1 - 1, H('3a2412'))
    steps(p, M + dx - 3, M + dx + door_w + 2, g1 + 6, n=2)
    # jendela dasar
    wins = []
    for cx in ((M + dx) // 2 + 4, M + dx + 26 + (M + fw - (M + dx + 26)) // 2 - 4):
        if cx - 9 > M and cx + 9 < M + fw: wins.append(cx)
    for cx in wins:
        if shop:
            window(p, cx - 9, g1 - 38, 18, 20, shutter=shutter, glass=H('ffe39a') if lit else H('b8d8e8'), sill=False)
            p.rect(cx - 10, g1 - 17, cx + 9, g1 - 15, H('c18c50')); p.hline(cx - 10, cx + 9, g1 - 17, H('e2b070'))
            for gi, gx_ in enumerate(range(cx - 8, cx + 8, 4)):
                gc = shop[gi % len(shop)]
                p.rect(gx_, g1 - 22, gx_ + 2, g1 - 18, gc); p.pt(gx_, g1 - 22, light(gc, 0.4))
        else:
            window(p, cx - 6, g1 - 36, 12, 16, shutter=shutter, flower=flower, glass=H('ffe39a') if lit else H('9bc4e0'))
    # ---- lantai atas (menjorok)
    cur0 = g0
    for s in range(1, stories):
        u1 = cur0 - 1; u0 = u1 - floor_h[s] + 1
        xo = M - upper_over; xe = M + fw - 1 + upper_over
        p.rect(xo, u1 + 1, xe, u1 + 4, shade(beam, 0.0)); p.hline(xo, xe, u1 + 1, light(beam, 0.2)); p.hline(xo, xe, u1 + 4, shade(beam, 0.4))
        plaster_rect(p, xo, u0, xe, u1, plaster, seed=seed + s); timber_frame(p, xo, u0, xe, u1, beam, bays=bays, brace=brace)
        nwin = bays
        xs = [xo + int(round(i * (xe - xo - 2) / bays)) + 3 for i in range(bays + 1)]
        for i in range(bays):
            cx = (xs[i] + xs[i + 1]) // 2
            window(p, cx - 5, u0 + 12, 10, 14, shutter=shutter, flower=flower)
        cur0 = u0
    # ---- atap
    cx = M + fw // 2
    half = fw // 2 + upper_over
    ytop = roof_gable(p, cx, cur0 - 1, half, roof_h, roof_c, kind=roof_kind, over=3)
    if attic:
        ay = cur0 - 1 - roof_h // 3
        p.rect(cx - 7, ay - 3, cx + 6, ay + 9, beam); plank_rect(p, cx - 6, ay - 2, cx + 5, ay + 8, H('c9a468'), pw=3)
        window(p, cx - 4, ay, 8, 6, sill=False, shutter=None)
    # cerobong
    if chim:
        sx = cx + (int(half * 0.5) if chim == 'r' else -int(half * 0.5))
        slope_y = ytop + int(abs(sx - cx) / (half + 3) * roof_h)
        chimney(p, sx - 4, ytop - 6, slope_y + 4, w=9, base=chim_c, seed=seed + 3)
    if sign:
        hang_sign(p, M + fw, g0 + 8, sign, side='r')
    if awn:
        awning(p, M + 2, M + fw - 3, g0 + 3, depth=8, c1=awn[0], c2=awn[1])
    for kind, px_ in props:
        if kind == 'barrel': barrel(p, px_, g1 - 11)
        elif kind == 'crate': crate(p, px_, g1 - 10)
        elif kind == 'sack': sack(p, px_, g1 - 10)
        elif kind == 'lantern': lantern(p, px_, g0 + 10)
    return finish(p)

def test1():
    A = townhouse(seed=1, sign=None, props=[('barrel', 6), ('crate', 2)])
    B = townhouse(w=124, ground='plaster', plaster=H('f0e8d0'), roof_c=H('5a6a8a'), roof_kind='slate', shutter=H('5fa04a'), seed=4, chim='l', bays=5, floor_h=(54, 44), roof_h=44)
    C = townhouse(w=96, ground='brick', gwall=H('b0553a'), roof_c=H('c9843a'), roof_kind='shingle', shutter=H('8a2f5a'), seed=7, stories=2, bays=3, floor_h=(54, 46), roof_h=40, sign='koin')
    W = A.width + B.width + C.width + 20; Hh = max(A.height, B.height, C.height)
    bg = Image.new('RGBA', (W, Hh), (150, 200, 230, 255)); x = 5
    for im in (A, B, C):
        bg.alpha_composite(im, (x, Hh - im.height)); x += im.width + 5
    up(bg, 4).save('/home/claude/work/bt1.png'); print(bg.size, A.size, B.size, C.size)


def test2():
    A = cottage(seed=2, sign='gandum', extras=[('hay', 2), ('fork', 8), ('barrel', M_ := 100)], pad_r=14)
    B = cottage(wall='logs', roof_c=H('7a5a3a'), roof_kind='shingle', seed=5, extras=[('woodpile', 98, 3, 3), ('crate', 2)], sign='kapak', pad_r=14)
    C = cottage(wall='logs', roof_c=H('6a8a5a'), roof_kind='shingle', seed=8, antler=True, extras=[('pelt', 70), ('target', 100)], sign='busur', pad_r=14)
    D = guardhouse(seed=4)
    ims = [A, B, C, D]
    W = sum(i.width for i in ims) + 5 * len(ims); Hh = max(i.height for i in ims)
    bg = Image.new('RGBA', (W, Hh), (150, 200, 230, 255)); x = 5
    for im in ims:
        bg.alpha_composite(im, (x, Hh - im.height)); x += im.width + 5
    up(bg, 3).save('/home/claude/work/bt2.png'); print(bg.size)



def anvil_small(p, x, y):
    c = H('9aa0b0')
    p.rect(x, y, x + 12, y + 2, light(c, 0.25)); p.rect(x + 3, y + 3, x + 9, y + 4, c); p.rect(x + 2, y + 5, x + 10, y + 6, shade(c, 0.2))
    p.rect(x - 3, y, x - 1, y + 1, c); p.rect(x + 4, y + 7, x + 8, y + 11, H('7a4a2a'))


def smithy(w=136, seed=6, pad_r=14):
    M = 14; fw = w - 2 * M
    Ht = 7 + 56 + 40 + 40
    p = Pen(w + pad_r, Ht); y = Ht - 1
    foundation(p, M - 1, M + fw, y - 6, y, seed=seed)
    g1 = y - 7; g0 = g1 - 55
    stone_rect(p, M, g0, M + fw - 1, g1, H('a89c8c'), seed=seed)
    # bukaan tungku (kiri)
    ax, ay, aw, ah = M + 8, g1 - 52, 48, 52
    arch_stone(p, ax, ay, aw, ah, interior=H('241418'), frame=H('b8aa94'), t=4)
    # isi: tungku + landasan + perkakas
    p.rect(ax + 26, g1 - 30, ax + 44, g1, H('6a6458')); stone_rect(p, ax + 26, g1 - 30, ax + 44, g1, H('7a7468'), seed=3, rh=(4, 5), bw=(5, 8))
    p.rect(ax + 29, g1 - 20, ax + 41, g1 - 6, H('1a0e10'))
    p.ell(ax + 29, g1 - 20, ax + 41, g1 - 4, H('e8742a')); p.ell(ax + 31, g1 - 16, ax + 39, g1 - 6, H('ffb040')); p.ell(ax + 33, g1 - 13, ax + 37, g1 - 8, H('fff0a0'))
    anvil_small(p, ax + 8, g1 - 14)
    for i, tx in enumerate((ax + 6, ax + 12, ax + 18)):
        p.vline(tx, ay + 14, ay + 24 + i * 2, H('9aa0b0')); p.rect(tx - 1, ay + 24 + i * 2, tx + 1, ay + 26 + i * 2, H('7a4a2a'))
    # pintu (kanan)
    dx = M + fw - 46
    door(p, dx, g1 - 44, 26, 44)
    steps(p, dx - 3, dx + 28, g1 + 6, n=1)
    window(p, dx - 24, g1 - 34, 12, 14, shutter=H('555b6b'), bars=True, sill=True)
    # atap
    cx = M + fw // 2
    ytop = roof_gable(p, cx, g0 - 1, fw // 2 + 4, 40, H('6a5a52'), kind='slate', over=4)
    # cerobong batu besar di atas tungku
    chx = ax + 24
    stone_rect(p, chx, ytop - 20, chx + 15, ytop + 30, H('9a9486'), seed=9, rh=(4, 6), bw=(6, 9))
    p.rect(chx - 2, ytop - 24, chx + 17, ytop - 20, H('8a847a')); p.hline(chx - 2, chx + 17, ytop - 24, light(H('8a847a'), 0.25)); p.rect(chx + 4, ytop - 25, chx + 11, ytop - 25, H('1a1218'))
    hang_sign(p, M + fw, g0 + 6, 'landasan', 'r')
    # perlengkapan luar
    barrel(p, M + fw - 60, g1 - 11, w=10, h=12)
    return finish(p), (chx + 8, ytop - 26), (ax, ay, aw, ah, g1)


def forge_overlays(size, glow_box, chim_pt, n=30):
    """anim: nyala api tungku + asap cerobong (sejajar dengan sprite bengkel)"""
    ax, g1 = glow_box
    glow, smoke = [], []
    for f in range(n):
        t = f / n
        q = Pen(size[0], size[1])
        fl = 0.5 + 0.5 * math.sin(2 * math.pi * t * 2) * 0.6 + 0.3 * math.sin(2 * math.pi * t * 5 + 1)
        r = int(3 + 2 * fl)
        q.ell(ax + 35 - r - 2, g1 - 12 - r, ax + 35 + r + 2, g1 - 7 + r, (255, 160, 60, 150))
        q.ell(ax + 35 - r, g1 - 11 - r + 2, ax + 35 + r, g1 - 8 + r, (255, 220, 120, 190))
        for i in range(3):
            q.pt(ax + 31 + i * 4, g1 - 22 - int(2 * fl) - i % 2, (255, 200, 90, 220))
        glow.append(q.get())
        s = Pen(size[0], size[1])
        for k in range(4):
            ph = (t + k / 4) % 1.0
            x = chim_pt[0] + math.sin((ph + k) * 5) * 2.5 + ph * 5
            yy = chim_pt[1] - 4 - ph * 26
            rr = 2 + 3 * ph
            a = int(210 * (1 - ph) ** 0.8)
            tmp = Image.new('RGBA', size, (0, 0, 0, 0)); ImageDraw.Draw(tmp).ellipse([x - rr, yy - rr, x + rr, yy + rr], fill=(226, 226, 236, a))
            s.im.alpha_composite(tmp)
        smoke.append(s.get())
    return glow, smoke


def library(w=164, seed=12):
    M = 8
    Ht = 7 + 56 + 46 + 38 + 30
    p = Pen(w, Ht); y = Ht - 1
    stone = H('c4b8a0'); slate = H('4a5a84')
    foundation(p, M, w - M - 1, y - 6, y, base=H('9a9486'), seed=seed)
    g1 = y - 7
    cw = 70; cx = w // 2; cx0 = cx - cw // 2; cx1 = cx + cw // 2 - 1
    # sayap kiri-kanan (2 lantai)
    for (x0, x1) in ((M + 2, cx0 - 1), (cx1 + 1, w - M - 3)):
        stone_rect(p, x0, g1 - 99, x1, g1, stone, seed=seed + x0)
        p.hline(x0, x1, g1 - 55, shade(stone, 0.35)); p.hline(x0, x1, g1 - 54, light(stone, 0.2))
        for wx in range((x0 + x1) // 2 - 6, (x0 + x1) // 2 + 1, 12):
            pass
        mid = (x0 + x1) // 2
        window(p, mid - 6, g1 - 40, 12, 22, arched=True, frame=H('5a4a3a'), glass=H('7aa4d0'))
        window(p, mid - 6, g1 - 88, 12, 22, arched=True, frame=H('5a4a3a'), glass=H('7aa4d0'))
        roof_gable(p, mid, g1 - 100, (x1 - x0) // 2 + 2, 30, slate, kind='slate', over=3)
    # blok tengah
    stone_rect(p, cx0, g1 - 99, cx1, g1, shade(stone, 0.0), seed=seed + 1, rh=(6, 8), bw=(10, 16))
    # kolom (tampak depan serambi)
    cols = [cx0 + 4, cx0 + 21, cx1 - 26, cx1 - 9]
    for i, x in enumerate(cols):
        p.rect(x, g1 - 94, x + 6, g1 - 1, light(stone, 0.22)); p.vline(x, g1 - 94, g1 - 1, WHITE + (255,)); p.vline(x + 6, g1 - 94, g1 - 1, shade(stone, 0.25))
        p.rect(x - 1, g1 - 96, x + 7, g1 - 94, shade(stone, 0.05)); p.rect(x - 1, g1 - 2, x + 7, g1 - 1, shade(stone, 0.1))
    p.rect(cx0 - 2, g1 - 100, cx1 + 2, g1 - 96, light(stone, 0.1)); p.hline(cx0 - 2, cx1 + 2, g1 - 96, shade(stone, 0.3))
    # pintu ganda
    door(p, cx - 15, g1 - 46, 30, 46, wood=H('7a4a2a'), arch=True, glass=True)
    p.vline(cx, g1 - 40, g1 - 1, H('3a2412'))
    window(p, cx - 24 + 0, g1 - 78, 0, 0, sill=False) if False else None
    window(p, cx - 7, g1 - 82, 14, 22, arched=True, frame=H('5a4a3a'), glass=H('7aa4d0'))
    # pedimen segitiga + ikon buku
    ytop = roof_gable(p, cx, g1 - 100, cw // 2 + 2, 36, slate, kind='slate', over=3)
    p.ell(cx - 9, g1 - 134 + 14, cx + 9, g1 - 134 + 32, H('efe4c4')); p.ell(cx - 8, g1 - 134 + 15, cx + 8, g1 - 134 + 31, H('3a5a8a'))
    icon(p, 'buku', cx - 5, g1 - 134 + 19)
    steps(p, cx - 26, cx + 26, g1 + 6, n=3, base=H('b8aa94'))
    # banner
    for bx in (M + 4, w - M - 14): banner(p, bx, g1 - 94, h=26, w=9, c=H('3f5f9a'), emblem=H('f3ead8'))
    return finish(p)


def chapel(w=140, seed=21):
    M = 10
    Ht = 7 + 56 + 44 + 34 + 44 + 24
    p = Pen(w, Ht); y = Ht - 1
    stone = H('b8b0a4'); cx = w // 2
    foundation(p, M, w - M - 1, y - 6, y, base=H('8a8478'), seed=seed)
    g1 = y - 7
    tw = 48
    t0, t1 = cx - tw // 2, cx + tw // 2 - 1
    # lorong samping
    for (x0, x1, flip) in ((M + 2, t0 - 1, 0), (t1 + 1, w - M - 3, 1)):
        stone_rect(p, x0, g1 - 56, x1, g1, stone, seed=seed + x0)
        mid = (x0 + x1) // 2
        window(p, mid - 4, g1 - 44, 8, 22, arched=True, frame=H('5a4a3a'), glass=H('d9453d') if flip else H('3f6fb0'))
        # atap miring (shed) menempel ke menara
        pts = [(x0 - 3, g1 - 56), (x1 + 1, g1 - 76), (x1 + 1, g1 - 70), (x0 - 3, g1 - 52)] if not flip else [(x1 + 3, g1 - 56), (x0 - 1, g1 - 76), (x0 - 1, g1 - 70), (x1 + 3, g1 - 52)]
        m = p.mask(pts); fn = roof_pattern('slate', H('5a6a8a'))
        p.paint(m, lambda x, y_: fn(x, y_, g1 - 76)); p.line(*(pts[0] + pts[1]), shade(H('5a6a8a'), 0.5), 2)
    # menara
    stone_rect(p, t0, g1 - 134, t1, g1, stone, seed=seed + 3, rh=(6, 8), bw=(10, 15))
    p.hline(t0, t1, g1 - 56, shade(stone, 0.35)); p.hline(t0, t1, g1 - 100, shade(stone, 0.35)); p.hline(t0, t1, g1 - 99, light(stone, 0.2))
    for s in (t0 - 3, t1 - 1): p.rect(s, g1 - 134, s + 4, g1, light(stone, 0.05)); p.vline(s, g1 - 134, g1, light(stone, 0.25)); p.vline(s + 4, g1 - 134, g1, shade(stone, 0.25))
    door(p, cx - 14, g1 - 46, 28, 46, wood=H('6a3a22'), arch=True, studs=True)
    steps(p, cx - 22, cx + 22, g1 + 6, n=2, base=H('b8aa94'))
    # jendela mawar
    rcy = g1 - 78
    p.ell(cx - 11, rcy - 11, cx + 11, rcy + 11, H('8a8478')); p.ell(cx - 9, rcy - 9, cx + 9, rcy + 9, H('3f6fb0'))
    for k in range(8):
        a = k * math.pi / 4; p.line(cx, rcy, cx + 9 * math.cos(a), rcy + 9 * math.sin(a), H('8a8478'))
    p.ell(cx - 3, rcy - 3, cx + 3, rcy + 3, H('f0c455'))
    for (a, c) in ((0, H('d9453d')), (2, H('f0c455')), (4, H('5fa04a')), (6, H('d9453d'))): p.pt(cx + int(6 * math.cos(a * math.pi / 4)), rcy + int(6 * math.sin(a * math.pi / 4)), c)
    # lonceng
    bay = g1 - 128
    arch_stone(p, cx - 9, bay, 18, 22, interior=H('2a1c26'), frame=H('a8a090'), t=3)
    p.poly([(cx - 5, bay + 8), (cx + 4, bay + 8), (cx + 6, bay + 18), (cx - 7, bay + 18)], H('e0b040')); p.rect(cx - 1, bay + 19, cx + 1, bay + 21, H('8a6020'))
    # atap meruncing
    ytop = roof_cone(p, cx, g1 - 134, tw // 2 + 4, 44, H('5a6a8a'), kind='slate')
    p.vline(cx, ytop - 10, ytop - 1, H('f0c455')); p.hline(cx - 3, cx + 3, ytop - 7, H('f0c455'))
    return finish(p)


def manor(w=214, seed=31):
    M = 8
    Ht = 7 + 56 + 44 + 44 + 40 + 34
    p = Pen(w, Ht); y = Ht - 1
    stone = H('b8b0a0'); plaster = H('efe6cc'); beam = H('4a3220'); cx = w // 2
    foundation(p, M, w - M - 1, y - 6, y, base=H('8a8478'), seed=seed)
    g1 = y - 7
    # menara samping
    tw = 40
    for tx0 in (M + 4, w - M - 4 - tw):
        tx1 = tx0 + tw - 1
        stone_rect(p, tx0, g1 - 160, tx1, g1, stone, seed=seed + tx0, rh=(6, 8), bw=(10, 15))
        for yy in (g1 - 56, g1 - 100): p.hline(tx0, tx1, yy, shade(stone, 0.35)); p.hline(tx0, tx1, yy + 1, light(stone, 0.2))
        mid = (tx0 + tx1) // 2
        window(p, mid - 5, g1 - 40, 10, 18, arched=True, frame=H('5a4a3a'), glass=H('7aa4d0'))
        window(p, mid - 5, g1 - 90, 10, 18, arched=True, frame=H('5a4a3a'), glass=H('7aa4d0'))
        window(p, mid - 5, g1 - 136, 10, 18, arched=True, frame=H('5a4a3a'), glass=H('ffe39a'))
        battlements(p, tx0 - 2, tx1 + 2, g1 - 160, shade(stone, 0.05), mw=7, mh=6, gap=3)
        roof_cone(p, mid, g1 - 166, tw // 2 + 5, 46, H('3a7a8a'), kind='tile')
        banner(p, mid - 4, g1 - 218 + 28, h=22, w=9, c=H('8a2f5a'), emblem=H('f0c455'))
    # aula tengah
    hx0, hx1 = M + 46, w - M - 47
    stone_rect(p, hx0, g1 - 56, hx1, g1, stone, seed=seed + 3, rh=(6, 8), bw=(10, 16))
    for fl in (1, 2):
        u1 = g1 - 56 - (fl - 1) * 44 - 1; u0 = u1 - 43
        plaster_rect(p, hx0, u0, hx1, u1, plaster, seed=seed + fl); timber_frame(p, hx0, u0, hx1, u1, beam, bays=4, brace='x')
        xs = [hx0 + int(round(i * (hx1 - hx0 - 2) / 4)) + 3 for i in range(5)]
        for i in range(4):
            cxx = (xs[i] + xs[i + 1]) // 2
            if fl == 1 and i in (1, 2): continue
            window(p, cxx - 5, u0 + 12, 10, 16, shutter=H('8a2f5a'), flower=H('e86a7a'))
    # balkon + pintu besar
    door(p, cx - 18, g1 - 50, 36, 50, wood=H('6a3a22'), arch=True)
    p.vline(cx, g1 - 44, g1 - 1, H('3a2412'))
    by = g1 - 56 - 1
    p.rect(cx - 28, by - 2, cx + 27, by + 2, light(stone, 0.1)); p.hline(cx - 28, cx + 27, by + 3, shade(stone, 0.4))
    for x in range(cx - 27, cx + 27, 5): p.vline(x, by - 11, by - 3, H('3a3a44'))
    p.hline(cx - 28, cx + 27, by - 12, H('3a3a44'))
    p.ell(cx - 7, g1 - 74, cx + 7, g1 - 60, H('efe4c4')); p.ell(cx - 5, g1 - 72, cx + 5, g1 - 62, H('8a2f5a')); icon(p, 'tameng', cx - 4, g1 - 71)
    ytop = roof_gable(p, (hx0 + hx1) // 2, g1 - 144, (hx1 - hx0) // 2 + 2, 40, H('4a5a84'), kind='slate', over=4)
    steps(p, cx - 34, cx + 34, g1 + 6, n=3, base=H('b8aa94'))
    for lx in (cx - 40, cx + 40): lantern(p, lx, g1 - 38)
    return finish(p)

def test3():
    s, chp, box = smithy()
    ims = [s, library(), chapel(), manor()]
    W = sum(i.width for i in ims) + 5 * len(ims); Hh = max(i.height for i in ims)
    bg = Image.new('RGBA', (W, Hh), (150, 200, 230, 255)); x = 5
    for im in ims:
        bg.alpha_composite(im, (x, Hh - im.height)); x += im.width + 5
    up(bg, 2).save('/home/claude/work/bt3.png'); print(bg.size, [i.size for i in ims])

