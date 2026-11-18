from bld_core import *

def clear_arch(p, cx, base_y, half, rect_h):
    """lubangi (transparan) lengkungan: persegi tinggi rect_h + setengah lingkaran jari-jari half."""
    for yy in range(base_y - rect_h - half, base_y + 1):
        if yy > base_y - rect_h: dx = half
        else: dx = int(math.sqrt(max(half * half - (base_y - rect_h - yy) ** 2, 0)))
        for xx in range(cx - dx, cx + dx):
            p.pt(xx, yy, (0, 0, 0, 0))


def gerbang_kota(w=250, seed=61):
    Ht = 214
    p = Pen(w, Ht); cx = w // 2; y = Ht - 1
    stone = H('a8a0b0')
    tw = 62
    # blok penuh dulu
    foundation(p, 6, w - 7, y - 6, y, base=H('8a8498'), seed=seed)
    stone_rect(p, 8, y - 170, w - 9, y - 7, stone, seed=seed, rh=(6, 8), bw=(10, 16))
    # menara kiri-kanan lebih tinggi
    for (x0, x1) in ((8, 8 + tw - 1), (w - 9 - tw + 1, w - 9)):
        stone_rect(p, x0, y - 196, x1, y - 170, stone, seed=seed + x0, rh=(6, 8), bw=(10, 16))
        battlements(p, x0 - 3, x1 + 3, y - 196, shade(stone, 0.05), mw=8, mh=7, gap=5)
        p.rect(x0 - 3, y - 196, x1 + 3, y - 191, light(stone, 0.1)); p.hline(x0 - 3, x1 + 3, y - 190, shade(stone, 0.4))
        mid = (x0 + x1) // 2
        p.rect(mid - 2, y - 150, mid + 1, y - 128, H('1a1218')); p.rect(mid - 5, y - 142, mid + 4, y - 140, H('1a1218'))
        window(p, mid - 6, y - 110, 12, 20, arched=True, frame=H('4a4452'), glass=H('7aa4d0'))
        for yy in (y - 170, y - 90): p.hline(x0, x1, yy, shade(stone, 0.35)); p.hline(x0, x1, yy + 1, light(stone, 0.2))
        banner(p, mid - 5, y - 188, h=30, w=11, c=H('3f6fb0'), emblem=H('f0c455'))
    # ruang jaga di atas lengkungan
    p.rect(tw + 8, y - 176, w - tw - 9, y - 170, light(stone, 0.12)); p.hline(tw + 8, w - tw - 9, y - 176, shade(stone, 0.35))
    battlements(p, tw + 6, w - tw - 7, y - 176, shade(stone, 0.05), mw=8, mh=6, gap=5)
    # lubangi gerbang: lebar 90, tinggi 118 (karavan tinggi ~96)
    half = 45; rect_h = 70
    clear_arch(p, cx, y - 7, half, rect_h)
    # lengkung batu (voussoir) & jeruji gerbang terangkat
    top_y = y - 7 - rect_h - half
    for k in range(-half - 3, half + 3):
        yy = y - 7 - rect_h - int(math.sqrt(max((half + 3) ** 2 - k * k, 0)))
        for t in range(4): p.pt(cx + k, yy - t, light(stone, 0.16) if t == 0 else (shade(stone, 0.12 * t) if (k // 6) % 2 else stone))
    for k in range(-half - 3, half + 3):
        yy = y - 7 - rect_h - int(math.sqrt(max((half) ** 2 - k * k, 0))) if abs(k) <= half else None
        if yy is not None:
            p.pt(cx + k, yy, shade(stone, 0.5)); p.pt(cx + k, yy + 1, shade(stone, 0.3))
    # jeruji besi (portcullis terangkat sebagian) di bagian atas lubang
    gy0 = top_y + 2
    for xx in range(cx - half + 5, cx + half - 4, 6):
        ext = int(math.sqrt(max(half * half - (xx - cx) ** 2, 0)))
        h_ = min(20, ext - 2)
        p.rect(xx, y - 7 - rect_h - ext + 2, xx + 1, y - 7 - rect_h - ext + 2 + h_, H('3a3a44')); p.pt(xx, y - 7 - rect_h - ext + 2 + h_ + 1, H('7a7a8a'))
    for yy in (top_y + 8, top_y + 16): p.hline(cx - 38, cx + 38, yy, H('3a3a44')) if yy < y - 7 - rect_h else None
    lantern(p, cx - half - 8, y - 7 - 50); lantern(p, cx + half + 8, y - 7 - 50)
    return finish(p)


def pagar_kayu(w=32, h=34):
    p = Pen(w + 4, h + 4)
    c = H('b98a4a'); base = h + 2
    p.rect(1, base - 4, w + 2, base - 1, shade(c, 0.1)) if False else None
    for x in range(2, w + 2, 8):
        p.rect(x, base - h + 6, x + 5, base, c); p.vline(x, base - h + 6, base, light(c, 0.25)); p.vline(x + 5, base - h + 6, base, shade(c, 0.3))
        p.poly([(x, base - h + 6), (x + 2.5, base - h + 1), (x + 5, base - h + 6)], light(c, 0.1))
    for yy in (base - 22, base - 10):
        p.rect(0, yy, w + 3, yy + 3, H('8a5a30')); p.hline(0, w + 3, yy, light(H('8a5a30'), 0.3)); p.hline(0, w + 3, yy + 3, shade(H('8a5a30'), 0.4))
    return finish(p)


def pagar_batu(w=32, h=26):
    p = Pen(w + 4, h + 4)
    stone_rect(p, 2, 6, w + 1, h + 1, H('a8a090'), seed=3, rh=(5, 7), bw=(8, 12))
    p.rect(0, 3, w + 3, 7, light(H('b8b0a0'), 0.1)); p.hline(0, w + 3, 3, WHITE + (255,)); p.hline(0, w + 3, 8, shade(H('b8b0a0'), 0.35))
    return finish(p)


def pagar_besi(w=32, h=42):
    p = Pen(w + 4, h + 4); iron = H('3a3a48')
    p.rect(0, h - 8, w + 3, h - 6, iron); p.rect(0, 12, w + 3, 13, iron)
    for x in range(2, w + 2, 5):
        p.rect(x, 8, x + 1, h + 1, iron); p.vline(x, 8, h + 1, H('6a6a7a')); p.poly([(x - 1, 8), (x + 0.5, 1), (x + 2, 8)], H('6a6a7a'))
    for x in (1, w + 1): p.rect(x - 1, 4, x + 3, h + 1, H('4a4a58')); p.rect(x, 1, x + 2, 4, H('f0c455'))
    stone_rect(p, 0, h - 4, w + 3, h + 1, H('8a8478'), seed=4, rh=(3, 4), bw=(6, 9))
    return finish(p)


def pagar_kayu_gerbang(w=44, h=38):
    p = Pen(w + 6, h + 6); c = H('b98a4a')
    for x in (2, w): p.rect(x, 4, x + 4, h + 4, H('8a5a30')); p.vline(x, 4, h + 4, light(H('8a5a30'), 0.25)); p.rect(x - 1, 1, x + 5, 4, light(H('8a5a30'), 0.1))
    for x in range(9, w - 4, 7):
        p.rect(x, 10, x + 4, h + 4, c); p.vline(x, 10, h + 4, light(c, 0.25)); p.vline(x + 4, 10, h + 4, shade(c, 0.3)); p.poly([(x, 10), (x + 2, 5), (x + 4, 10)], light(c, 0.1))
    for yy in (14, h - 4): p.rect(7, yy, w - 3, yy + 3, H('8a5a30')); p.hline(7, w - 3, yy, light(H('8a5a30'), 0.3))
    p.line(8, h - 3, w - 4, 15, H('8a5a30'), 3)
    p.rect(w - 9, 24, w - 7, 26, H('f0c455'))
    return finish(p)


def tembok_kota(w=64, h=120, seed=63):
    p = Pen(w + 4, h + 4)
    stone = H('a8a0b0')
    stone_rect(p, 2, 14, w + 1, h + 3, stone, seed=seed, rh=(6, 8), bw=(10, 16))
    p.rect(0, 10, w + 3, 16, light(stone, 0.12)); p.hline(0, w + 3, 17, shade(stone, 0.4)); battlements(p, 0, w + 3, 10, shade(stone, 0.05), mw=8, mh=7, gap=4)
    p.rect(w // 2 - 1, 38, w // 2 + 2, 58, H('1a1218')); p.rect(w // 2 - 4, 46, w // 2 + 5, 48, H('1a1218'))
    for k in range(2): p.hline(2, w + 1, 70 + k * 30, shade(stone, 0.3))
    return finish(p)


def timbang(w=52, h=50):
    p = Pen(w, h); cx = w // 2; y = h - 1
    p.rect(cx - 14, y - 8, cx + 14, y, H('7a4a2a')); p.hline(cx - 14, cx + 14, y - 8, light(H('7a4a2a'), 0.3)); p.hline(cx - 14, cx + 14, y, shade(H('7a4a2a'), 0.4))
    p.rect(cx - 2, y - 34, cx + 1, y - 8, H('555b6b')); p.vline(cx - 2, y - 34, y - 8, H('8a90a0'))
    p.rect(cx - 20, y - 36, cx + 19, y - 34, H('555b6b')); p.hline(cx - 20, cx + 19, y - 36, H('9aa0b0')); p.ell(cx - 3, y - 39, cx + 2, y - 33, H('f0c455'))
    for sx in (cx - 18, cx + 17):
        p.line(sx, y - 34, sx - 5, y - 20, H('3a3a44')); p.line(sx, y - 34, sx + 5, y - 20, H('3a3a44'))
        p.rect(sx - 8, y - 20, sx + 8, y - 18, H('c9a74a')); p.hline(sx - 8, sx + 8, y - 20, light(H('c9a74a'), 0.3))
    crate(p, cx - 24, y - 30 - 0, 9, 9) if False else None
    sack(p, cx - 22, y - 30, 9, 10); p.rect(cx + 13, y - 28, cx + 20, y - 21, H('555b6b')); p.hline(cx + 13, cx + 20, y - 28, H('9aa0b0'))
    return finish(p)


def papan_harga(w=70, h=70):
    p = Pen(w, h); cx = w // 2; y = h - 1
    for x in (cx - 24, cx + 20): p.rect(x, y - 30, x + 3, y, H('7a4a2a')); p.vline(x, y - 30, y, light(H('7a4a2a'), 0.25))
    p.rect(cx - 30, y - 62, cx + 29, y - 28, H('8a5a30')); plank_rect(p, cx - 28, y - 60, cx + 27, y - 30, H('b98a4a'), pw=4)
    p.rect(cx - 30, y - 62, cx + 29, y - 61, light(H('8a5a30'), 0.3))
    for i, (ic, col) in enumerate((('gandum', H('f3ead8')), ('peti', H('f3ead8')), ('beliung', H('f3ead8')), ('buku', H('f3ead8')))):
        x = cx - 26 + (i % 2) * 26; yy = y - 58 + (i // 2) * 15
        p.rect(x, yy, x + 22, yy + 12, col); p.hline(x, x + 22, yy, light(col, 0.3)); p.hline(x, x + 22, yy + 12, shade(col, 0.2))
        icon(p, ic, x + 1, yy + 2) 
        for k in range(3): p.rect(x + 13 + k * 3, yy + 5, x + 14 + k * 3, yy + 9, H('3a2a20') if k < 2 else H('d9453d'))
    return finish(p)


def tanda_depot(w=48, h=74):
    p = Pen(w, h); cx = w // 2; y = h - 1
    p.rect(cx - 2, y - 66, cx + 2, y, H('7a4a2a')); p.vline(cx - 2, y - 66, y, light(H('7a4a2a'), 0.25))
    for (yy, dirn, ic) in ((y - 60, 1, 'peti'), (y - 40, -1, 'tukar')):
        x0 = cx - 20 if dirn < 0 else cx - 14
        pts = [(x0, yy), (x0 + 30, yy), (x0 + 30 + (6 if dirn > 0 else 0), yy + 7), (x0 + 30, yy + 14), (x0, yy + 14)] if dirn > 0 else [(x0 + 6, yy + 7), (x0 + 6, yy), (x0 + 36, yy), (x0 + 36, yy + 14), (x0 + 6, yy + 14)]
        p.poly(pts, H('c18c50')); p.hline(x0 + 6 if dirn < 0 else x0, x0 + 30, yy, light(H('c18c50'), 0.3)); p.hline(x0 + 6 if dirn < 0 else x0, x0 + 30, yy + 14, shade(H('c18c50'), 0.4))
        icon(p, ic, (x0 + 12) if dirn > 0 else (x0 + 16), yy + 3)
    p.rect(cx - 6, y - 4, cx + 6, y, H('8a8478'))
    return finish(p)


def tumpukan(kind='a', w=76, h=58, seed=1):
    p = Pen(w, h); y = h - 1
    if kind == 'a':
        for i in range(3): crate(p, 6 + i * 13, y - 11)
        for i in range(2): crate(p, 12 + i * 13, y - 22)
        crate(p, 19, y - 33)
        barrel(p, 48, y - 15, 11, 15); barrel(p, 60, y - 15, 11, 15); barrel(p, 54, y - 29, 11, 15)
    elif kind == 'b':
        for i in range(3): sack(p, 6 + i * 11, y - 11)
        for i in range(2): sack(p, 11 + i * 11, y - 21)
        sack(p, 17, y - 31)
        barrel(p, 44, y - 15, 11, 15); crate(p, 57, y - 11, 14, 11); crate(p, 59, y - 22, 12, 11)
    else:
        crate(p, 4, y - 11, 16, 11); crate(p, 22, y - 11, 14, 11); barrel(p, 40, y - 15, 11, 15); sack(p, 54, y - 11); sack(p, 60, y - 21)
        crate(p, 8, y - 22, 13, 11)
        p.poly([(2, y - 24), (38, y - 24), (42, y - 8), (-1, y - 8)], H('7a8a6a')) if False else None
    return finish(p)


def dermaga(w=116, h=44):
    p = Pen(w, h); y = h - 1
    top = 12
    plank_rect(p, 2, top, w - 3, y - 1, H('a8743f'), pw=6, horiz=True)
    p.rect(0, top - 4, w - 1, top, H('c18c50')); p.hline(0, w - 1, top - 4, light(H('c18c50'), 0.3)); p.hline(0, w - 1, top, shade(H('c18c50'), 0.35))
    for x in range(8, w - 4, 36):
        p.rect(x, top, x + 5, y, H('7a4a2a')); p.vline(x, top, y, light(H('7a4a2a'), 0.25)); p.vline(x + 5, top, y, shade(H('7a4a2a'), 0.3))
        p.line(x + 6, top + 4, x + 22, y - 2, H('6a3a22'), 2)
    for bx in (w // 2 - 20, w // 2 + 40):
        p.rect(bx, top - 12, bx + 5, top - 4, H('3a3a44')); p.ell(bx - 1, top - 14, bx + 6, top - 9, H('555b6b')); p.hline(bx, bx + 5, top - 12, H('7a7a8a'))
    p.line(30, top - 6, 36, top - 2, H('d8c08a'), 1)
    return finish(p)


def derek(frames=30, w=96, h=156):
    out = []
    for f in range(frames):
        p = Pen(w, h); y = h - 1; sw = math.sin(2 * math.pi * f / frames)
        wood = H('8a5a30')
        p.rect(8, y - 6, 28, y, H('8a8478'))
        p.rect(14, y - 120, 21, y - 6, wood); p.vline(14, y - 120, y - 6, light(wood, 0.25)); p.vline(21, y - 120, y - 6, shade(wood, 0.3))
        p.line(18, y - 40, 52, y - 118, wood, 4); p.line(18, y - 120, 70, y - 120, wood, 6)
        p.line(21, y - 86, 40, y - 120, shade(wood, 0.2), 3)
        p.hline(18, 72, y - 123, light(wood, 0.3))
        p.ell(66, y - 130, 76, y - 118, H('555b6b')); p.ell(69, y - 127, 73, y - 121, H('9aa0b0'))
        rx = 71 + int(round(sw * 2)); ry = y - 118
        hook_y = y - 60
        p.line(rx, ry, rx + int(round(sw * 3)), hook_y, H('d8c08a'))
        hx = rx + int(round(sw * 3))
        p.rect(hx - 1, hook_y, hx + 1, hook_y + 4, H('3a3a44')); p.hline(hx - 3, hx + 3, hook_y + 4, H('555b6b'))
        crate(p, hx - 9, hook_y + 6, 18, 16, H('b98a4a'))
        p.line(hx - 8, hook_y + 6, hx, hook_y + 3, H('d8c08a')); p.line(hx + 8, hook_y + 6, hx, hook_y + 3, H('d8c08a'))
        out.append(finish(p))
    return out


def gudang(w=196, seed=71):
    M = 10; fw = w - 2 * M
    Ht = 7 + 56 + 46 + 52 + 18
    p = Pen(w + 30, Ht); y = Ht - 1; cx = M + fw // 2
    foundation(p, M - 1, M + fw, y - 6, y, seed=seed)
    g1 = y - 7; g0 = g1 - 55
    stone_rect(p, M, g0, M + fw - 1, g1, H('b0a490'), seed=seed)
    u1 = g0 - 1; u0 = u1 - 45
    plaster_rect(p, M - 3, u0, M + fw + 2, u1, H('e8dcb8'), seed=seed + 1); timber_frame(p, M - 3, u0, M + fw + 2, u1, H('5a3a22'), bays=6, brace='x')
    p.rect(M - 3, g0, M + fw + 2, g0 + 2, H('5a3a22'))
    # pintu muat lebar (lengkung) dengan daun pintu terbuka dan peti di dalam
    bw = 62
    ax = cx - bw // 2
    arch_stone(p, ax, g1 - 58, bw, 58, interior=H('2a1c20'), frame=H('b8aa94'), t=4)
    for i in range(4): crate(p, ax + 4 + i * 14, g1 - 11)
    for i in range(3): crate(p, ax + 10 + i * 14, g1 - 22)
    barrel(p, ax + 44, g1 - 36 if False else g1 - 33, 11, 11)
    for sx in (ax - 14, ax + bw + 2):
        plank_rect(p, sx, g1 - 50, sx + 11, g1 - 1, H('7a4a2a'), pw=4)
        p.hline(sx, sx + 11, g1 - 40, H('3a3a44')); p.hline(sx, sx + 11, g1 - 12, H('3a3a44'))
    # pintu kecil + jendela
    door(p, M + fw - 44, g1 - 44, 24, 44)
    window(p, M + 18, g1 - 36, 14, 18, shutter=H('555b6b'), bars=True)
    # jendela atas & pintu loteng
    for xx in (M + 20, M + fw - 34): window(p, xx, u0 + 14, 12, 16, shutter=H('8a6a3a'))
    window(p, cx - 9, u0 + 8, 18, 28, shutter=None, glass=H('2a1c20'), frame=H('5a3a22'))
    plank_rect(p, cx - 8, u0 + 9, cx + 7, u0 + 34, H('9a6a3a'), pw=4)
    ytop = roof_gable(p, cx, u0 - 1, fw // 2 + 3, 52, H('b0553a'), kind='tile', over=5)
    # balok katrol
    bx0 = cx + 2
    p.rect(bx0, u0 - 22, bx0 + 40, u0 - 18, H('8a5a30')); p.hline(bx0, bx0 + 40, u0 - 22, light(H('8a5a30'), 0.3))
    p.line(bx0 + 4, u0 - 6, bx0 + 30, u0 - 20, H('7a4a2a'), 3)
    p.ell(bx0 + 36, u0 - 26, bx0 + 44, u0 - 18, H('555b6b')); p.ell(bx0 + 38, u0 - 24, bx0 + 42, u0 - 20, H('9aa0b0'))
    p.line(bx0 + 40, u0 - 18, bx0 + 40, u0 + 8, H('d8c08a')); p.rect(bx0 + 38, u0 + 8, bx0 + 42, u0 + 12, H('3a3a44'))
    # spanduk
    p.rect(M + 6, g0 - 24, M + 31, g0 - 6, H('efe4c4')) if False else None
    banner(p, M + 6, u0 + 6, h=30, w=12, c=H('b03a3a'), emblem=H('f3ead8')); icon(p, 'peti', M + 7, u0 + 14)
    hang_sign(p, M + fw, g0 + 6, 'peti', 'r')
    return finish(p)


def kantor_tukar(w=128, seed=73):
    M = 12; fw = w - 2 * M
    Ht = 7 + 56 + 44 + 44 + 16
    p = Pen(w + 14, Ht); y = Ht - 1; cx = M + fw // 2
    foundation(p, M - 1, M + fw, y - 6, y, seed=seed)
    g1 = y - 7; g0 = g1 - 55
    stone_rect(p, M, g0, M + fw - 1, g1, H('b8aa94'), seed=seed)
    # loket penukaran (jendela besar berjeruji + meja)
    wx = M + 8
    p.rect(wx - 2, g1 - 40, wx + 41, g1 - 14, H('5a3a22')); p.rect(wx, g1 - 38, wx + 39, g1 - 16, H('ffe39a'))
    p.rect(wx + 15, g1 - 38, wx + 24, g1 - 16, H('c9a468')) if False else None
    for xx in range(wx + 2, wx + 38, 5): p.vline(xx, g1 - 38, g1 - 16, H('555b6b'))
    p.rect(wx - 3, g1 - 14, wx + 42, g1 - 11, H('c18c50')); p.hline(wx - 3, wx + 42, g1 - 14, light(H('c18c50'), 0.3))
    for k in range(4): p.ell(wx + 4 + k * 8, g1 - 18, wx + 9 + k * 8, g1 - 15, H('f0c455') if k % 2 else H('c9a74a'))
    awning(p, wx - 4, wx + 43, g1 - 46, depth=7, c1=H('3f6fb0'), c2=H('f0c455'))
    door(p, M + fw - 38, g1 - 44, 26, 44, wood=H('5a3a22'))
    steps(p, M + fw - 41, M + fw - 9, g1 + 6, n=2)
    u1 = g0 - 1; u0 = u1 - 43
    plaster_rect(p, M - 3, u0, M + fw + 2, u1, H('efe6cc'), seed=seed + 1); timber_frame(p, M - 3, u0, M + fw + 2, u1, H('4a3220'), bays=3, brace='x')
    for xx in (M + 14, M + fw // 2 + 4): window(p, xx, u0 + 12, 14, 16, shutter=H('3f6fb0'), flower=H('f0c455'))
    window(p, M + fw - 26, u0 + 12, 12, 16, shutter=H('3f6fb0'), flower=H('f0c455'))
    cx2 = M + fw // 2
    ytop = roof_gable(p, cx2, u0 - 1, fw // 2 + 3, 44, H('4a6aa0'), kind='tile', over=4)
    p.ell(cx2 - 9, u0 - 30, cx2 + 9, u0 - 12, H('efe4c4')); p.ell(cx2 - 7, u0 - 28, cx2 + 7, u0 - 14, H('3a5a9a')); icon(p, 'tukar', cx2 - 5, u0 - 26)
    chimney(p, cx2 + 28, ytop + 4, ytop + 28, w=9, base=H('a87a64'), seed=2)
    hang_sign(p, M + fw, g0 + 6, 'koin', 'r')
    return finish(p)


def depot_test():
    ims = [gerbang_kota(), gudang(), kantor_tukar(), dermaga(), tumpukan('a'), tumpukan('b'), tumpukan('c'), timbang(), papan_harga(), tanda_depot(), derek(30)[8], pagar_kayu(), pagar_batu(), pagar_besi(), pagar_kayu_gerbang(), tembok_kota()]
    W = sum(i.width for i in ims) + 4 * len(ims); Hh = max(i.height for i in ims)
    bg = Image.new('RGBA', (W, Hh), (150, 200, 230, 255)); x = 4
    for im in ims:
        bg.alpha_composite(im, (x, Hh - im.height)); x += im.width + 4
    up(bg, 1).save('/home/claude/work/bt5.png'); print(bg.size, [i.size for i in ims])

if __name__ == '__main__':
    depot_test()
