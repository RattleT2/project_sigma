"""Toolkit bangunan pixel-art kota medieval (tampak depan / menghadap layar). Gaya sama dengan gerobak:
outline berwarna, 3 tingkat shading, cahaya dari kiri-atas."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from pxlib import H, mix, outline, up, comp, new, sheet

WHITE = (255, 248, 232); DARK = (40, 24, 40)


def light(c, t=0.2): return mix(c, WHITE, t)
def shade(c, t=0.2): return mix(c, DARK, t)


REC = {'chim': [], 'door': []}


class Pen:
    def __init__(self, w, h):
        self.im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.w, self.h = w, h

    def rect(self, x0, y0, x1, y1, c):
        if x1 < x0 or y1 < y0: return
        self.d.rectangle([int(x0), int(y0), int(x1), int(y1)], fill=c)

    def pt(self, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h: self.im.putpixel((x, y), c)

    def hline(self, x0, x1, y, c): self.rect(x0, y, x1, y, c)
    def vline(self, x, y0, y1, c): self.rect(x, y0, x, y1, c)

    def poly(self, pts, c):
        self.d.polygon([(int(round(x)), int(round(y))) for x, y in pts], fill=c)

    def line(self, x0, y0, x1, y1, c, w=1):
        self.d.line([(int(x0), int(y0)), (int(x1), int(y1))], fill=c, width=w)

    def ell(self, x0, y0, x1, y1, c):
        if x1 < x0: x0, x1 = x1, x0
        if y1 < y0: y0, y1 = y1, y0
        self.d.ellipse([int(x0), int(y0), int(x1), int(y1)], fill=c)

    def mask(self, pts):
        m = Image.new('L', (self.w, self.h), 0)
        ImageDraw.Draw(m).polygon([(int(round(x)), int(round(y))) for x, y in pts], fill=255)
        return np.array(m) > 0

    def paint(self, mask, fn):
        ys, xs = np.where(mask)
        px = self.im.load()
        for y, x in zip(ys, xs):
            px[int(x), int(y)] = fn(int(x), int(y))

    def get(self):
        return self.im


# ------------------------------------------------------------------ tekstur dinding
def stone_rect(p, x0, y0, x1, y1, base, seed=1, rh=(5, 7), bw=(8, 14)):
    rng = random.Random(seed)
    p.rect(x0, y0, x1, y1, shade(base, 0.3))
    y = y0
    while y <= y1:
        h = rng.randint(*rh); ye = min(y + h - 2, y1)
        x = x0 - rng.randint(0, bw[1] - 1)
        while x <= x1:
            w = rng.randint(*bw)
            xs, xe = max(x, x0), min(x + w - 2, x1)
            if xe >= xs and ye >= y:
                c = mix(base, WHITE if rng.random() < 0.5 else (70, 56, 60), rng.random() * 0.14)
                p.rect(xs, y, xe, ye, c)
                p.hline(xs, xe, y, light(c, 0.2)); p.hline(xs, xe, ye, shade(c, 0.14))
                p.pt(xs, y + 1 if ye > y else y, light(c, 0.1))
            x += w
        y += h


def brick_rect(p, x0, y0, x1, y1, base, seed=2):
    rng = random.Random(seed)
    p.rect(x0, y0, x1, y1, shade(base, 0.34))
    row = 0; y = y0
    while y <= y1:
        x = x0 - (4 if row % 2 else 0)
        while x <= x1:
            xs, xe = max(x, x0), min(x + 6, x1)
            if xe >= xs:
                c = mix(base, WHITE if rng.random() < .5 else (60, 40, 44), rng.random() * 0.12)
                p.rect(xs, y, xe, min(y + 2, y1), c)
                p.hline(xs, xe, y, light(c, 0.16))
            x += 8
        y += 4; row += 1


def plaster_rect(p, x0, y0, x1, y1, base, seed=3):
    rng = random.Random(seed)
    p.rect(x0, y0, x1, y1, base)
    for _ in range(int((x1 - x0) * (y1 - y0) / 18)):
        x, y = rng.randint(x0, x1), rng.randint(y0, y1)
        p.pt(x, y, shade(base, 0.07) if rng.random() < 0.6 else light(base, 0.1))
    p.vline(x0, y0, y1, light(base, 0.14)); p.vline(x1, y0, y1, shade(base, 0.12))


def timber_frame(p, x0, y0, x1, y1, beam, bays=3, brace='x', bw=3):
    """kerangka kayu (di atas plester) : tiang, balok, dan palang silang."""
    lb, db = light(beam, 0.18), shade(beam, 0.25)
    def vb(x, ya, yb):
        p.rect(x, ya, x + bw - 1, yb, beam); p.vline(x, ya, yb, lb); p.vline(x + bw - 1, ya, yb, db)
    def hb(y, xa, xb):
        p.rect(xa, y, xb, y + bw - 1, beam); p.hline(xa, xb, y, lb); p.hline(xa, xb, y + bw - 1, db)
    hb(y0, x0, x1); hb(y1 - bw + 1, x0, x1)
    xs = [x0 + int(round(i * (x1 - x0 - bw + 1) / bays)) for i in range(bays + 1)]
    for x in xs: vb(x, y0, y1)
    for i in range(bays):
        xa, xb = xs[i] + bw, xs[i + 1] - 1
        if brace in ('x', 'v') and xb - xa > 8:
            ya, yb = y0 + bw, y1 - bw
            p.line(xa, ya, xb, yb, beam, 2)
            if brace == 'x': p.line(xb, ya, xa, yb, beam, 2)
    return xs


def log_rect(p, x0, y0, x1, y1, base, seed=4):
    rng = random.Random(seed)
    y = y0
    while y <= y1:
        h = 6; ye = min(y + h - 1, y1)
        c = mix(base, WHITE if rng.random() < .5 else (60, 36, 24), rng.random() * 0.1)
        p.rect(x0, y, x1, ye, c)
        p.hline(x0, x1, y, light(c, 0.22)); p.hline(x0, x1, ye, shade(c, 0.3))
        for _ in range(3):
            xx = rng.randint(x0 + 2, max(x0 + 3, x1 - 6)); p.hline(xx, xx + rng.randint(2, 5), y + 2, shade(c, 0.12))
        # ujung kayu menonjol di sudut
        p.ell(x0 - 2, y, x0 + 3, ye, light(c, 0.1)); p.ell(x1 - 3, y, x1 + 2, ye, light(c, 0.1))
        p.pt(x0, y + 2, shade(c, 0.35)); p.pt(x1, y + 2, shade(c, 0.35))
        y += h


def plank_rect(p, x0, y0, x1, y1, base, seed=5, pw=4, horiz=False):
    rng = random.Random(seed)
    if horiz:
        y = y0
        while y <= y1:
            c = mix(base, WHITE if rng.random() < .5 else (60, 36, 24), rng.random() * 0.1)
            p.rect(x0, y, x1, min(y + pw - 1, y1), c); p.hline(x0, x1, y, light(c, 0.18)); p.hline(x0, x1, min(y + pw - 1, y1), shade(c, 0.3)); y += pw
    else:
        x = x0
        while x <= x1:
            c = mix(base, WHITE if rng.random() < .5 else (60, 36, 24), rng.random() * 0.1)
            p.rect(x, y0, min(x + pw - 1, x1), y1, c); p.vline(x, y0, y1, light(c, 0.16)); p.vline(min(x + pw - 1, x1), y0, y1, shade(c, 0.3))
            for _ in range(2):
                yy = rng.randint(y0, y1); p.pt(min(x + 1, x1), yy, shade(c, 0.2))
            x += pw


# ------------------------------------------------------------------ atap
def roof_pattern(kind, base):
    L1, D1, D2 = light(base, 0.22), shade(base, 0.2), shade(base, 0.38)
    def fn(x, y, y0):
        yy = y - y0
        if kind in ('tile', 'slate', 'copper'):
            rh = 6 if kind == 'tile' else 5
            row = yy // rh; ty = yy % rh
            tw = 8 if kind == 'tile' else 7
            tx = (x + (row % 2) * (tw // 2)) % tw
            c = base
            if ty == 0: c = L1
            if ty == rh - 1: c = D1
            if ty == rh - 2 and (tx in (0, tw - 1) or tx == tw // 2 - 1) : c = D1
            if tx == 0 and 0 < ty < rh - 1: c = D1
            if (x * 7 + y * 3) % 17 == 0: c = L1
            if row % 3 == 1 and kind == 'tile': c = mix(base, (255, 200, 150), 0.07)
            return c
        if kind == 'thatch':
            c = base
            s = (x * 3 + y * 5) % 9
            if s == 0: c = D1
            elif s == 4: c = L1
            if (x + y * 2) % 13 == 0: c = D2
            if yy % 6 == 5: c = D1
            return c
        if kind == 'shingle':
            row = yy // 4; ty = yy % 4; tx = (x + (row % 2) * 3) % 6
            c = base
            if ty == 0: c = L1
            if ty == 3: c = D1
            if tx == 0: c = D1
            return c
        return base
    return fn


def roof_gable(p, cx, y_base, half_w, h, base, kind='tile', over=4, trim=None, y_cut=None):
    """atap pelana menghadap depan (segitiga)."""
    ytop = y_base - h
    pts = [(cx - half_w - over, y_base), (cx, ytop), (cx + half_w + over, y_base)]
    m = p.mask(pts)
    fn = roof_pattern(kind, base)
    p.paint(m, lambda x, y: fn(x, y, ytop))
    # papan tepi (fascia) mengikuti lereng
    tr = trim or shade(base, 0.45)
    p.line(cx - half_w - over, y_base, cx, ytop, tr, 2); p.line(cx + half_w + over, y_base, cx, ytop, tr, 2)
    p.line(cx - half_w - over + 1, y_base - 1, cx - 1, ytop + 1, light(tr, 0.3), 1)
    # tepi bawah (bayangan di bawah atap)
    p.hline(cx - half_w - over, cx + half_w + over, y_base, shade(base, 0.5))
    p.hline(cx - half_w - over + 1, cx + half_w + over - 1, y_base + 1, shade(base, 0.62))
    p.pt(cx, ytop - 1, light(base, 0.3))
    return ytop


def roof_slab(p, x0, x1, y_top, y_base, base, kind='tile', over=4, inset=10):
    """atap tampak samping panjang (trapesium)."""
    pts = [(x0 + inset, y_top), (x1 - inset, y_top), (x1 + over, y_base), (x0 - over, y_base)]
    m = p.mask(pts)
    fn = roof_pattern(kind, base)
    p.paint(m, lambda x, y: fn(x, y, y_top))
    tr = shade(base, 0.45)
    p.line(x0 + inset, y_top, x0 - over, y_base, tr, 2); p.line(x1 - inset, y_top, x1 + over, y_base, tr, 2)
    p.hline(x0 + inset, x1 - inset, y_top, light(base, 0.35)); p.hline(x0 + inset, x1 - inset, y_top - 1, shade(base, 0.5))
    p.hline(x0 - over, x1 + over, y_base, shade(base, 0.5)); p.hline(x0 - over + 1, x1 + over - 1, y_base + 1, shade(base, 0.62))


def roof_cone(p, cx, y_base, r, h, base, kind='tile'):
    ytop = y_base - h
    pts = [(cx - r, y_base), (cx, ytop), (cx + r, y_base)]
    m = p.mask(pts); fn = roof_pattern(kind, base)
    p.paint(m, lambda x, y: fn(x, y, ytop))
    p.line(cx - r, y_base, cx, ytop, shade(base, 0.45), 2); p.line(cx + r, y_base, cx, ytop, shade(base, 0.45), 2)
    p.hline(cx - r, cx + r, y_base, shade(base, 0.5))
    p.line(cx, ytop - 4, cx, ytop, H('4a3a2a'))
    return ytop


# ------------------------------------------------------------------ komponen
def window(p, x, y, w, h, shutter=None, glass=H('9bc4e0'), frame=H('5a3a22'), sill=True, arched=False, flower=None, lit=False, bars=False):
    fr = frame
    if shutter:
        sw = max(3, w // 3)
        for sx in (x - sw - 1, x + w + 1):
            p.rect(sx, y, sx + sw - 1, y + h - 1, shutter)
            p.vline(sx, y, y + h - 1, light(shutter, 0.25)); p.vline(sx + sw - 1, y, y + h - 1, shade(shutter, 0.3))
            for yy in range(y + 2, y + h - 1, 3): p.hline(sx + 1, sx + sw - 2, yy, shade(shutter, 0.28))
    p.rect(x - 1, y - 1, x + w, y + h, fr)
    gl = H('ffe39a') if lit else glass
    p.rect(x, y, x + w - 1, y + h - 1, gl)
    # gradien & kilau kaca
    for yy in range(y, y + h): 
        if (yy - y) > h * 0.55: p.hline(x, x + w - 1, yy, shade(gl, 0.1))
    p.pt(x + 1, y + 1, light(gl, 0.6)); p.pt(x + 2, y + 1, light(gl, 0.45)); p.pt(x + 1, y + 2, light(gl, 0.45))
    if arched:
        p.rect(x - 1, y - 1, x + w, y, fr)
        p.pt(x - 1, y - 1, (0, 0, 0, 0)); p.pt(x + w, y - 1, (0, 0, 0, 0))
    # kisi
    p.vline(x + w // 2, y, y + h - 1, fr)
    if h >= 10: p.hline(x, x + w - 1, y + h // 2 - 1, fr)
    if bars:
        for xx in range(x + 1, x + w - 1, 3): p.vline(xx, y, y + h - 1, H('555b6b'))
    if sill:
        p.rect(x - 2, y + h, x + w + 1, y + h + 1, light(H('b8aa94'), 0.1)); p.hline(x - 2, x + w + 1, y + h + 2, shade(H('b8aa94'), 0.3))
    if flower:
        p.rect(x - 2, y + h + 2, x + w + 1, y + h + 5, H('7a4a2a')); p.hline(x - 2, x + w + 1, y + h + 2, H('a8743f'))
        for i, xx in enumerate(range(x - 1, x + w + 1, 2)):
            p.pt(xx, y + h + 1, H('4fa05a')); p.pt(xx, y + h, flower if i % 2 else light(flower, 0.3))


def door(p, x, y, w, h, wood=H('7a4a2a'), arch=True, studs=True, frame=None, knob=True, glass=False):
    REC['door'].append((x + w // 2, y, w, h))
    fr = frame or H('8a7a66')
    p.rect(x - 2, y - 2, x + w + 1, y + h, fr)
    p.vline(x - 2, y - 2, y + h, light(fr, 0.2)); p.vline(x + w + 1, y - 2, y + h, shade(fr, 0.25))
    plank_rect(p, x, y, x + w - 1, y + h - 1, wood, seed=x + y, pw=4)
    if arch:
        r = w // 2
        for i in range(r):
            dx = r - int(math.sqrt(max(r * r - (r - i) ** 2, 0)))
            p.hline(x, x + dx - 1, y + i, fr); p.hline(x + w - dx, x + w - 1, y + i, fr)
    if studs:
        for yy in (y + h // 4, y + 3 * h // 4):
            p.hline(x, x + w - 1, yy, H('3a3a44')); p.hline(x + 1, x + 3, yy + 1, H('555b6b')); p.hline(x + w - 4, x + w - 2, yy + 1, H('555b6b'))
    if glass:
        p.rect(x + w // 2 - 2, y + 4, x + w // 2 + 1, y + 9, H('9bc4e0')); p.rect(x + w // 2 - 2, y + 4, x + w // 2 + 1, y + 4, H('5a3a22'))
    if knob: p.rect(x + w - 5, y + h // 2, x + w - 4, y + h // 2 + 1, H('f0c455'))
    p.vline(x + w // 2, y + 3, y + h - 1, shade(wood, 0.45))


def steps(p, x0, x1, y, n=2, base=H('a8a090')):
    for i in range(n):
        p.rect(x0 + i * 2, y - (n - i - 1) * 3 - 2, x1 - i * 2, y - (n - i - 1) * 3 + 0, base)
        p.hline(x0 + i * 2, x1 - i * 2, y - (n - i - 1) * 3 - 2, light(base, 0.25)); p.hline(x0 + i * 2, x1 - i * 2, y - (n - i - 1) * 3, shade(base, 0.25))


def chimney(p, x, y_top, y_base, w=9, base=H('a87a64'), stone=False, seed=7):
    REC['chim'].append((x + w // 2, y_top - 3))
    if stone: stone_rect(p, x, y_top, x + w - 1, y_base, base, seed=seed, rh=(4, 5), bw=(5, 8))
    else: brick_rect(p, x, y_top, x + w - 1, y_base, base, seed=seed)
    p.rect(x - 1, y_top - 2, x + w, y_top, shade(base, 0.2)); p.hline(x - 1, x + w, y_top - 2, light(base, 0.2))
    p.rect(x + 2, y_top - 3, x + w - 3, y_top - 3, DARK + (255,) if False else H('2a1c22'))


def awning(p, x0, x1, y, depth=9, c1=H('d9453d'), c2=H('f6eedc')):
    n = 0
    for x in range(x0, x1 + 1):
        c = c1 if ((x - x0) // 5) % 2 == 0 else c2
        for yy in range(y, y + depth):
            t = (yy - y) / depth
            p.pt(x, yy, shade(c, 0.12) if t > 0.7 else (light(c, 0.1) if t < 0.2 else c))
        sc = y + depth + (1 if ((x - x0) % 5) in (1, 2, 3) else 0)
        p.pt(x, y + depth, shade(c, 0.2)); p.pt(x, sc, shade(c, 0.3))
    p.hline(x0, x1, y - 1, shade(c1, 0.4))


def barrel(p, x, y, w=10, h=12, band=H('555b6b'), wood=H('9a6a3a')):
    p.rect(x + 1, y + 2, x + w - 2, y + h - 2, wood); p.rect(x, y + 4, x + w - 1, y + h - 4, wood)
    p.ell(x + 1, y, x + w - 2, y + 4, light(wood, 0.25)); p.ell(x + 2, y + 1, x + w - 3, y + 3, shade(wood, 0.15))
    for yy in (y + 4, y + h - 5): p.hline(x, x + w - 1, yy, band)
    for xx in range(x + 2, x + w - 1, 3): p.vline(xx, y + 5, y + h - 6, shade(wood, 0.25))
    p.vline(x + 1, y + 4, y + h - 3, light(wood, 0.2))


def crate(p, x, y, w=12, h=11, wood=H('b98a4a')):
    p.rect(x, y, x + w - 1, y + h - 1, wood)
    p.hline(x, x + w - 1, y, light(wood, 0.28)); p.hline(x, x + w - 1, y + h - 1, shade(wood, 0.35))
    p.vline(x, y, y + h - 1, light(wood, 0.15)); p.vline(x + w - 1, y, y + h - 1, shade(wood, 0.28))
    p.line(x + 1, y + 1, x + w - 2, y + h - 2, shade(wood, 0.3)); p.line(x + w - 2, y + 1, x + 1, y + h - 2, shade(wood, 0.3))
    p.rect(x + 1, y + 1, x + w - 2, y + 1, light(wood, 0.1))


def sack(p, x, y, w=10, h=11, base=H('c9a468')):
    p.ell(x, y + 2, x + w - 1, y + h - 1, base)
    p.rect(x + 2, y, x + w - 3, y + 3, base); p.hline(x + 2, x + w - 3, y + 3, shade(base, 0.35)); p.pt(x + 3, y, light(base, 0.3))
    p.line(x + 2, y + 4, x + 2, y + h - 3, light(base, 0.25)); p.line(x + w - 3, y + 4, x + w - 3, y + h - 3, shade(base, 0.25))


def lantern(p, x, y, glow=True):
    p.line(x, y - 4, x, y, H('3a3a44')); p.rect(x - 2, y, x + 2, y + 1, H('3a3a44'))
    p.rect(x - 2, y + 2, x + 2, y + 6, H('ffd45e')); p.vline(x, y + 2, y + 6, H('fff2b0')); p.rect(x - 2, y + 7, x + 2, y + 8, H('3a3a44'))


def banner(p, x, y, h=22, w=10, c=H('3f6fb0'), emblem=H('f0c455')):
    p.rect(x, y, x + w - 1, y + 1, H('5a3a22'))
    p.poly([(x + 1, y + 2), (x + w - 2, y + 2), (x + w - 2, y + h - 4), (x + (w - 1) / 2, y + h), (x + 1, y + h - 4)], c)
    p.vline(x + 1, y + 2, y + h - 4, light(c, 0.2)); p.vline(x + w - 2, y + 2, y + h - 4, shade(c, 0.25))
    p.ell(x + w // 2 - 2, y + 6, x + w // 2 + 1, y + 9, emblem)


# ------------------------------------------------------------------ ikon papan nama (9x9 piksel)
ICON = {
 'landasan': ["..........", ".hhhhhhh..", "hhhhhhhhh.", "..hhhhh...", "...hhh....", "..hhhhh...", ".hhhhhhh..", ".........."],
 'roti': ["..........", "...oooo...", "..oOOOOo..", ".oOkOOkOo.", ".oOOOOOOo.", "..oooooo..", ".........."],
 'buku': [".........", ".rrrr.rrr.", ".rwwr.wwr.", ".rwwr.wwr.", ".rwwrrwwr.", ".rrrrrrrr.", "........."],
 'koin': ["...yyy...", "..yYYYy..", ".yYyyyYy.", ".yYyyyYy.", ".yYyyyYy.", "..yYYYy..", "...yyy..."],
 'salib': ["....w....", "....w....", "..wwwww..", "....w....", "....w....", "....w....", "....w...."],
 'cangkir': [".........", ".wwwwww..", ".wBBBBw.w", ".wBBBBw.w", ".wBBBBww.", "..wwwww..", "........."],
 'ramuan': ["...kk....", "...kk....", "...ww....", "..wGGw...", ".wGGGGw..", ".wGGGGw..", "..wwww..."],
 'busur': ["..bb.....", ".b..b....", "b....b...", "b.wwwwb..", "b....b...", ".b..b....", "..bb....."],
 'kapak': ["...gg....", "..gggb...", "..ggb....", "...b.....", "...b.....", "...b.....", "...b....."],
 'beliung': [".gggggg..", "g..b...g.", "...b.....", "...b.....", "...b.....", "...b.....", "...b....."],
 'gandum': ["...y.....", "..yyy....", "...y.....", "..yyy....", "...y.....", "...g.....", "...g....."],
 'kristal': ["...pp....", "..pPPp...", ".pPwPPp..", ".pPPPPp..", "..pPPp...", "...pp....", "........."],
 'peti': ["wwwwwww..", "wbbbbbw..", "wbwwwbw..", "wbwwwbw..", "wbbbbbw..", "wwwwwww.."],
 'tukar': ["..yy..bb.", ".yyyy.bb.", "yyyyyybbbb", ".yyyy.bb..", "..yy..bb..", "bb..yy....", "bbbbyyyy.."],
 'tameng': [".wwwwwww.", ".wBBwRRw.", ".wBBwRRw.", ".wwwwwww.", "..wRRRw..", "...wRw...", "....w...."],
 'tangan': ["..ff.f...", ".ffffff..", ".ffffff..", ".ffffff..", "..ffff...", "..fff...."],
 'tanduk': ["w.....w..", "ww...ww..", ".w.w.w...", "..www....", "..www....", "...w....."],
 'gergaji': ["ggggggggg", "g.g.g.g.g", ".........", ".bbbb....", ".b.......", ".b......."],
}
ICOLORS = dict(h=H('9aa0b0'), w=H('f3ead8'), r=H('a8433a'), o=H('c9843a'), O=H('e0a860'), k=H('8a5a28'), y=H('f0c455'), Y=H('b8892c'),
               B=H('c9843a'), G=H('b060e0'), b=H('7a4a2a'), g=H('b8bece'), p=H('9a70e0'), P=H('c8a8ff'), f=H('e8a070'))


def icon(p, name, x, y, scale=1):
    rows = ICON[name]
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != '.':
                c = ICOLORS.get(ch, H('888888'))
                for sy in range(scale):
                    for sx in range(scale): p.pt(x + i * scale + sx, y + j * scale + sy, c)


def hang_sign(p, x, y, name, side='r', board=H('c18c50'), w=15, h=13):
    """papan nama gantung dengan lengan besi dari dinding di x."""
    dx = 1 if side == 'r' else -1
    x1 = x + dx * (w + 4)
    p.hline(min(x, x1), max(x, x1), y, H('3a3a44')); p.vline(x + dx * 1, y, y + 3, H('3a3a44'))
    bx0 = min(x + dx * 3, x + dx * (3 + w)) if True else x
    bx0 = x + 3 if side == 'r' else x - 3 - w + 1
    for cx in (bx0 + 2, bx0 + w - 3): p.vline(cx, y + 1, y + 4, H('3a3a44'))
    p.rect(bx0, y + 4, bx0 + w - 1, y + 4 + h - 1, board); p.hline(bx0, bx0 + w - 1, y + 4, light(board, 0.3)); p.hline(bx0, bx0 + w - 1, y + 3 + h, shade(board, 0.35))
    p.vline(bx0, y + 4, y + 3 + h, light(board, 0.15)); p.vline(bx0 + w - 1, y + 4, y + 3 + h, shade(board, 0.3))
    ic = ICON[name]; iw = max(len(r) for r in ic); ih = len(ic)
    icon(p, name, bx0 + (w - iw) // 2, y + 4 + (h - ih) // 2)


def foundation(p, x0, x1, y0, y1, base=H('9a9486'), seed=11):
    stone_rect(p, x0, y0, x1, y1, base, seed=seed, rh=(4, 5), bw=(6, 10))


def finish(p, strength=0.55):
    im = p.get()
    o = outline(im, strength)
    o.alpha_composite(im)
    return o


# ------------------------------------------------------------------ komponen tambahan
def battlements(p, x0, x1, y, base, mw=6, mh=5, gap=4):
    x = x0
    while x + mw - 1 <= x1:
        p.rect(x, y - mh, x + mw - 1, y, base); p.hline(x, x + mw - 1, y - mh, light(base, 0.25)); p.vline(x, y - mh, y, light(base, 0.12)); p.vline(x + mw - 1, y - mh, y, shade(base, 0.2))
        x += mw + gap


def arch_stone(p, x, y, w, h, interior=H('2a1c26'), frame=H('a8a090'), t=4):
    """bukaan melengkung berbingkai batu; (x,y) sudut kiri-atas, h total termasuk lengkung."""
    r = w // 2
    p.rect(x - t, y - t, x + w + t - 1, y + h - 1, frame)
    for i in range(t + 1):
        pass
    p.rect(x, y + r, x + w - 1, y + h - 1, interior)
    for yy in range(y, y + r):
        dx = int(math.sqrt(max(r * r - (r - (yy - y)) ** 2, 0)))
        p.hline(x + r - dx, x + r + dx - 1, yy, interior)
    # sudut atas dipotong jadi lengkung luar
    for yy in range(y - t, y + r):
        dxo = int(math.sqrt(max((r + t) ** 2 - (r - (yy - y)) ** 2, 0))) if (r - (yy - y)) < (r + t) else 0
        for xx in range(x - t, x + w + t):
            if abs(xx - (x + r - 0.5)) > dxo: p.pt(xx, yy, (0, 0, 0, 0))
    p.vline(x - t, y + r, y + h - 1, light(frame, 0.2)); p.vline(x + w + t - 1, y + r, y + h - 1, shade(frame, 0.25))


def haybale(p, x, y, w=14, h=11):
    c = H('e0c060')
    p.rect(x, y, x + w - 1, y + h - 1, c)
    for yy in range(y + 1, y + h - 1, 2): p.hline(x + 1, x + w - 2, yy, shade(c, 0.12))
    for xx in range(x + 2, x + w - 2, 3): p.pt(xx, y + 2, light(c, 0.3)); p.pt(xx + 1, y + h - 3, shade(c, 0.25))
    p.hline(x, x + w - 1, y, light(c, 0.25)); p.hline(x, x + w - 1, y + h - 1, shade(c, 0.3))
    p.vline(x + 3, y, y + h - 1, H('8a6030')); p.vline(x + w - 4, y, y + h - 1, H('8a6030'))


def pitchfork(p, x, y, h=30):
    p.vline(x, y, y + h, H('9a6a3a')); p.vline(x + 1, y, y + h, light(H('9a6a3a'), 0.2))
    for dx in (-2, 0, 2): p.vline(x + dx + (1 if dx == 0 else 0), y - 6, y, H('9aa0b0'))
    p.hline(x - 2, x + 3, y, H('9aa0b0'))


def woodpile(p, x, y, cols=5, rows=3, r=5):
    for j in range(rows):
        for i in range(cols):
            cx = x + i * (r * 2 - 1) + (r if j % 2 else 0); cy = y - j * (r * 2 - 2)
            p.ell(cx, cy - r * 2 + 2, cx + r * 2 - 1, cy + 1, H('8a5a30'))
            p.ell(cx + 1, cy - r * 2 + 3, cx + r * 2 - 2, cy, H('e2c490'))
            p.ell(cx + 3, cy - r * 2 + 5, cx + r * 2 - 4, cy - 2, H('c8a470')); p.pt(cx + r, cy - r + 1, H('8a5a30'))


def antlers(p, cx, y):
    c = H('e8dcc0')
    for s in (-1, 1):
        p.line(cx, y, cx + s * 5, y - 3, c, 1); p.line(cx + s * 5, y - 3, cx + s * 7, y - 9, c, 1)
        p.line(cx + s * 4, y - 3, cx + s * 4, y - 8, c, 1); p.line(cx + s * 6, y - 6, cx + s * 9, y - 7, c, 1)
    p.rect(cx - 3, y, cx + 3, y + 3, H('c8a470')); p.ell(cx - 3, y - 1, cx + 3, y + 5, H('9a6a3a'))


def pelt(p, x, y, c=H('a8743f')):
    p.poly([(x, y), (x + 9, y), (x + 11, y + 5), (x + 8, y + 11), (x + 5, y + 14), (x + 2, y + 11), (x - 1, y + 5)], c)
    p.hline(x, x + 9, y, light(c, 0.2)); p.vline(x + 3, y + 2, y + 9, shade(c, 0.2))


def target_board(p, cx, cy, r=10):
    p.rect(cx - 1, cy + r, cx + 1, cy + r + 12, H('7a4a2a'))
    cols = [H('f3ead8'), H('c8433a'), H('f3ead8'), H('3f6fb0'), H('f0c455')]
    for i, c in enumerate(cols):
        rr = r - i * 2
        if rr > 0: p.ell(cx - rr, cy - rr, cx + rr, cy + rr, c)


def herbs(p, x, y):
    p.hline(x, x + 10, y, H('7a4a2a'))
    for i, xx in enumerate((x + 1, x + 4, x + 7, x + 10)):
        c = [H('5fa04a'), H('8a60c8'), H('d9a050'), H('5fa04a')][i]
        p.vline(xx, y + 1, y + 3, H('7a4a2a')); p.rect(xx - 1, y + 4, xx + 1, y + 8, c); p.pt(xx, y + 9, shade(c, 0.2))


def thatch_fray(p, x0, x1, y):
    rng = random.Random(x0 + y)
    for x in range(x0, x1 + 1):
        n = rng.randint(1, 3)
        for k in range(n): p.pt(x, y + 1 + k, shade(H('c9a85a'), 0.2 + 0.1 * k))


# ------------------------------------------------------------------ jenis bangunan
def cottage(w=108, wall='plaster', roof_c=H('c9a85a'), roof_kind='thatch', plaster=H('eadfc0'), beam=H('5a3a22'), shutter=H('5fa04a'),
            sign=None, extras=(), seed=3, door_c=H('7a4a2a'), chim_c=H('9a9486'), pad_r=0, herbs_=False, antler=False):
    M = 14; fw = w - 2 * M
    Ht = 7 + 56 + 44 + 14
    p = Pen(w + pad_r, Ht); y = Ht - 1
    foundation(p, M - 1, M + fw, y - 6, y, seed=seed)
    g1 = y - 7; g0 = g1 - 55
    if wall == 'plaster':
        plaster_rect(p, M, g0, M + fw - 1, g1, plaster, seed=seed); timber_frame(p, M, g0, M + fw - 1, g1, beam, bays=3, brace='v')
    elif wall == 'logs':
        log_rect(p, M, g0, M + fw - 1, g1, H('9a6a3a'), seed=seed)
    else:
        stone_rect(p, M, g0, M + fw - 1, g1, H('b8aa94'), seed=seed)
    door(p, M + 8, g1 - 44, 26, 44, wood=door_c)
    steps(p, M + 5, M + 37, g1 + 6, n=1)
    window(p, M + fw - 26, g1 - 36, 14, 16, shutter=shutter, flower=H('e86a7a'))
    cx = M + fw // 2; half = fw // 2 + 6
    ytop = roof_gable(p, cx, g0 - 1, half, 42, roof_c, kind=roof_kind, over=5)
    if roof_kind == 'thatch': thatch_fray(p, cx - half - 5, cx + half + 5, g0 + 1)
    p.ell(cx - 5, g0 - 17, cx + 5, g0 - 6, beam); p.ell(cx - 4, g0 - 16, cx + 4, g0 - 7, H('9bc4e0')); p.vline(cx, g0 - 16, g0 - 7, beam)
    sx = cx - int(half * 0.45)
    chimney(p, sx - 4, ytop + 2, ytop + 24, w=9, base=chim_c, stone=True, seed=seed)
    if herbs_:
        for i, xx in enumerate((M + 40, M + 52, M + 64)): herbs(p, xx, g0 + 4)
    if antler: antlers(p, M + 21, g0 + 6)
    for e in extras:
        k = e[0]
        if k == 'hay': haybale(p, e[1], g1 - 10)
        elif k == 'fork': pitchfork(p, e[1], g1 - 28)
        elif k == 'barrel': barrel(p, e[1], g1 - 11)
        elif k == 'crate': crate(p, e[1], g1 - 10)
        elif k == 'sack': sack(p, e[1], g1 - 10)
        elif k == 'pelt': pelt(p, e[1], g0 + 8, e[2] if len(e) > 2 else H('a8743f'))
        elif k == 'target': target_board(p, e[1], g1 - 22)
        elif k == 'woodpile': woodpile(p, e[1], g1, e[2], e[3])
    if sign: hang_sign(p, M + fw, g0 + 6, sign, 'r')
    return finish(p)


def guardhouse(w=100, stone=H('a8a2b0'), banner_c=H('3f6fb0'), emblem=H('f0c455'), seed=5, floors=2, wide=False, pad=0):
    M = 16; fw = w - 2 * M
    Ht = 7 + 56 + (floors - 1) * 44 + 22 + 30
    p = Pen(w, Ht); y = Ht - 1
    foundation(p, M - 2, M + fw + 1, y - 6, y, base=shade(stone, 0.1), seed=seed)
    top = y - 7 - 56 - (floors - 1) * 44
    stone_rect(p, M, top, M + fw - 1, y - 7, stone, seed=seed, rh=(5, 7), bw=(9, 15))
    # gerbang kayu + palang besi
    dx = (fw - 28) // 2
    arch_stone(p, M + dx, y - 7 - 46, 28, 46, interior=H('4a2e1c'), frame=light(stone, 0.12))
    plank_rect(p, M + dx, y - 7 - 32, M + dx + 27, y - 8, H('7a4a2a'), seed=seed, pw=4)
    for yy in (y - 7 - 26, y - 7 - 12): p.hline(M + dx, M + dx + 27, yy, H('3a3a44'))
    steps(p, M + dx - 4, M + dx + 31, y - 1, n=2, base=light(stone, 0.05))
    for f in range(1, floors):
        fy = top + 4 + (f - 1) * 0
    # celah panah / jendela kecil
    for fl in range(floors):
        wy = top + 10 + fl * 44 if fl > 0 else top + 8
    # lantai atas dengan jendela
    for i, cx in enumerate((M + 10, M + fw - 14)):
        p.rect(cx, top + 14, cx + 3, top + 28, H('1a1218')); p.rect(cx - 2, top + 20, cx + 5, top + 22, H('1a1218'))
    if floors > 1:
        p.hline(M, M + fw - 1, top + 44, shade(stone, 0.3)); p.hline(M, M + fw - 1, top + 45, light(stone, 0.2))
        window(p, M + fw // 2 - 6, top + 8, 12, 18, arched=True, sill=True, bars=False, frame=H('4a4452'))
    battlements(p, M - 3, M + fw + 2, top, shade(stone, 0.05), mw=8, mh=7, gap=5)
    p.rect(M - 3, top, M + fw + 2, top + 4, light(stone, 0.12)); p.hline(M - 3, M + fw + 2, top + 5, shade(stone, 0.4))
    # tiang bendera + banner
    for bx in (M - 8, M + fw + 4):
        p.vline(bx + 3, top - 22, y - 8, H('5a3a22')); banner(p, bx - 1, top - 20 + 8, h=26, w=9, c=banner_c, emblem=emblem)
    lantern(p, M + dx - 8, top + 36)
    return finish(p)


# ------------------------------------------------------------------ bangunan fantasi & lain
def leaf_cluster(p, cx, cy, r, cols, seed=1):
    rng = random.Random(seed)
    for _ in range(int(r * 2.2)):
        a = rng.random() * 6.283; d = rng.random() * r
        x, y = cx + math.cos(a) * d * 1.3, cy + math.sin(a) * d * 0.8
        c = cols[rng.randint(0, len(cols) - 1)]
        rr = rng.randint(3, 6)
        p.ell(x - rr, y - rr, x + rr, y + rr, c)
        p.ell(x - rr + 1, y - rr + 1, x, y, light(c, 0.15))


def bark(p, x0, y0, x1, y1, base=H('7a5a3a'), seed=2):
    rng = random.Random(seed)
    p.rect(x0, y0, x1, y1, base)
    for x in range(x0, x1 + 1):
        c = shade(base, 0.18) if (x * 5 + seed) % 7 in (0, 3) else (light(base, 0.12) if (x + seed) % 6 == 1 else base)
        p.vline(x, y0, y1, c)
    for _ in range((x1 - x0) * (y1 - y0) // 50):
        x, y = rng.randint(x0, x1), rng.randint(y0, y1); p.vline(x, y, y + rng.randint(2, 5), shade(base, 0.3))
    p.vline(x0, y0, y1, light(base, 0.2)); p.vline(x1, y0, y1, shade(base, 0.3))


def fox_statue(p, x, y, flip=False):
    s = -1 if flip else 1
    c = H('c8c0b4')
    p.rect(x - 4, y - 2, x + 4, y, shade(c, 0.1))
    p.ell(x - 4, y - 14, x + 4, y - 2, c); p.ell(x - 3, y - 20, x + 3, y - 13, c)
    p.poly([(x - 3, y - 19), (x - 4, y - 25), (x, y - 20)], c); p.poly([(x + 1, y - 20), (x + 4, y - 25), (x + 4, y - 19)], c)
    p.rect(x + s * 3, y - 18, x + s * 6, y - 16, c); p.pt(x + s * 6, y - 17, H('2a2a34'))
    p.ell(x - s * 8, y - 10, x - s * 2, y, shade(c, 0.1)); p.rect(x - 3, y - 12, x - 2, y - 8, light(c, 0.3))
    p.rect(x - 2, y - 11, x + 2, y - 10, H('d9453d'))


def treehouse(w=156, seed=41):
    Ht = 256
    p = Pen(w, Ht); cx = w // 2; y = Ht - 1
    # akar & batang
    for s in (-1, 1):
        p.poly([(cx + s * 14, y - 40), (cx + s * 30, y - 6), (cx + s * 36, y), (cx + s * 16, y), (cx + s * 8, y - 30)], H('6a4a2a'))
    bark(p, cx - 24, y - 190, cx + 23, y - 6, seed=seed)
    p.poly([(cx - 24, y - 12), (cx - 34, y), (cx + 34, y), (cx + 23, y - 12)], H('7a5a3a'))
    for k in range(6): p.vline(cx - 30 + k * 12, y - 6, y, shade(H('7a5a3a'), 0.3))
    # kanopi
    cols = [H('3f8a4a'), H('5fa858'), H('7fc868')]
    leaf_cluster(p, cx, y - 200, 62, cols, seed)
    leaf_cluster(p, cx - 40, y - 178, 26, cols, seed + 1); leaf_cluster(p, cx + 42, y - 176, 26, cols, seed + 2)
    # rumah di dahan
    py = y - 118
    plank_rect(p, cx - 50, py, cx + 49, py + 6, H('b98a4a'), pw=5, horiz=False)
    p.hline(cx - 50, cx + 49, py, light(H('b98a4a'), 0.3)); p.hline(cx - 50, cx + 49, py + 7, shade(H('b98a4a'), 0.4))
    for x in range(cx - 48, cx + 49, 12): p.rect(x, py - 10, x + 1, py, H('7a5a3a'))
    p.hline(cx - 50, cx + 49, py - 11, H('7a5a3a'))
    hx0, hx1 = cx - 38, cx + 37
    plank_rect(p, hx0, py - 46, hx1, py - 1, H('c9a468'), pw=4)
    window(p, hx0 + 6, py - 34, 12, 14, shutter=H('5fa058'), flower=H('e86a7a'))
    window(p, hx1 - 18, py - 34, 12, 14, shutter=H('5fa058'), flower=H('f0c455'))
    door(p, cx - 10, py - 38, 20, 37, wood=H('7a5a3a'), arch=True, studs=False)
    # atap daun
    for i, (rx, ry, rr) in enumerate([(cx, py - 52, 40), (cx - 22, py - 46, 24), (cx + 22, py - 46, 24)]):
        leaf_cluster(p, rx, ry - 8, rr, [H('2f7a4a'), H('4f9a58'), H('6fb868')], seed + 10 + i)
    p.rect(cx - 36, py - 50, cx + 35, py - 46, H('4f9a58'))
    lantern(p, hx0 - 6, py - 30); lantern(p, hx1 + 6, py - 30)
    # tangga tali
    lx = cx + 30
    p.vline(lx, py + 7, y - 2, H('b8a070')); p.vline(lx + 8, py + 7, y - 2, H('b8a070'))
    for yy in range(py + 12, y - 2, 6): p.hline(lx, lx + 8, yy, H('9a6a3a'))
    # pintu di pangkal batang (setinggi NPC)
    door(p, cx - 13, y - 48, 26, 46, wood=H('6a4a2a'), arch=True, frame=H('5a7a3a'), studs=False)
    for i in range(6): p.pt(cx - 14 + i * 5, y - 50 + (i % 2), H('5fa858')); p.pt(cx - 13 + i * 5, y - 49, H('7fc868'))
    lantern(p, cx - 24, y - 40); lantern(p, cx + 24, y - 40)
    return finish(p)


def shrine(w=150, seed=43):
    Ht = 150
    p = Pen(w, Ht); cx = w // 2; y = Ht - 1
    stone = H('c4bcb0'); red = H('c8433a')
    foundation(p, cx - 56, cx + 56, y - 8, y, base=H('9a9486'), seed=seed)
    steps(p, cx - 30, cx + 30, y - 1, n=3, base=H('b8b0a4'))
    plank_rect(p, cx - 50, y - 70, cx + 49, y - 9, H('d8c8a0'), pw=5)
    for x in (cx - 50, cx - 30, cx + 28, cx + 47):
        p.rect(x, y - 76, x + 4, y - 9, red); p.vline(x, y - 76, y - 9, light(red, 0.25)); p.vline(x + 4, y - 76, y - 9, shade(red, 0.3))
    p.rect(cx - 52, y - 78, cx + 51, y - 72, H('3a2a30')); p.hline(cx - 52, cx + 51, y - 78, light(H('3a2a30'), 0.2))
    door(p, cx - 13, y - 50, 26, 42, wood=H('4a2a3a'), arch=False, studs=False, frame=red)
    p.rect(cx - 12, y - 49, cx + 11, y - 36, H('8a2f5a')); p.vline(cx, y - 49, y - 36, H('6a1f4a'))
    p.ell(cx - 4, y - 46, cx + 3, y - 38, H('f0c455'));
    # atap melengkung
    for lvl, (y0, hw, c) in enumerate([(y - 78, 62, H('8a2f3a')), (y - 98, 46, H('a8433a'))]):
        pts = [(cx - hw - 8, y0 + 2), (cx - hw, y0 - 4), (cx - hw * 0.4, y0 - 14), (cx, y0 - 18), (cx + hw * 0.4, y0 - 14), (cx + hw, y0 - 4), (cx + hw + 8, y0 + 2), (cx + hw, y0 + 8), (cx - hw, y0 + 8)]
        m = p.mask(pts); fn = roof_pattern('tile', c); p.paint(m, lambda x, y_, y0=y0: fn(x, y_, y0 - 18))
        p.line(cx - hw - 8, y0 + 2, cx - hw, y0 - 4, shade(c, 0.5), 2); p.line(cx + hw + 8, y0 + 2, cx + hw, y0 - 4, shade(c, 0.5), 2)
        p.hline(cx - hw, cx + hw, y0 + 8, shade(c, 0.55))
    p.rect(cx - 30, y - 98 + 8, cx + 29, y - 80, H('d8c8a0')); p.rect(cx - 30, y - 98 + 8, cx + 29, y - 98 + 9, red)
    p.ell(cx - 7, y - 96, cx + 7, y - 82, H('efe4c4')); p.ell(cx - 5, y - 94, cx + 5, y - 84, H('b03a8a')); icon(p, 'kristal', cx - 5, y - 93)
    p.vline(cx, y - 130, y - 116, H('3a2a30')); p.ell(cx - 3, y - 134, cx + 3, y - 128, H('f0c455'))
    for lx in (cx - 40, cx + 38): 
        p.vline(lx, y - 72, y - 66, H('3a2a30')); p.ell(lx - 4, y - 66, lx + 4, y - 54, red); p.hline(lx - 3, lx + 3, y - 60, H('f0c455')); p.ell(lx - 2, y - 64, lx + 2, y - 58, H('ffd890'))
    fox_statue(p, cx - 44, y - 1); fox_statue(p, cx + 44, y - 1, flip=True)
    return finish(p)


def mine(w=170, seed=45):
    Ht = 172
    p = Pen(w, Ht); cx = w // 2; y = Ht - 1
    pts = [(4, y), (6, y - 60), (22, y - 112), (44, y - 138), (78, y - 152), (118, y - 140), (146, y - 116), (162, y - 70), (166, y)]
    m = p.mask(pts)
    ys, xs = np.where(m)
    rng = random.Random(seed)
    px = p.im.load()
    for yy, xx in zip(ys, xs):
        n = ((xx * 7 + yy * 3) % 11) / 11.0
        base = H('7a7f8e'); c = mix(base, WHITE, 0.12 * n) if (xx // 6 + yy // 5) % 3 else shade(base, 0.12 * (1 - n))
        px[int(xx), int(yy)] = c
    for _ in range(40):
        x, yv = rng.randint(10, w - 10), rng.randint(y - 140, y - 4)
        if m[min(yv, Ht - 1), min(x, w - 1)]: p.hline(x, x + rng.randint(3, 8), yv, shade(H('7a7f8e'), 0.28))
    # rumput atas
    for x in range(20, w - 20):
        top = next((yy for yy in range(Ht) if m[yy, x]), None)
        if top is not None:
            for k in range(3 + (x * 3) % 3): p.pt(x, top + k, H('5fa04a') if k else H('7fc868'))
    # kristal
    for (kx, ky) in ((30, y - 50), (136, y - 76), (118, y - 30)):
        p.poly([(kx, ky), (kx + 3, ky - 12), (kx + 7, ky)], H('7fe0ff')); p.poly([(kx + 5, ky), (kx + 8, ky - 8), (kx + 11, ky)], H('b8f0ff'))
    # pintu tambang (kerangka kayu)
    dw, dh = 54, 60
    x0 = cx - dw // 2
    p.rect(x0, y - dh, x0 + dw - 1, y - 6, H('120c10'))
    p.rect(x0 + 10, y - dh + 18, x0 + dw - 11, y - 6, H('0a0608'))
    for xx, c in ((x0 - 4, 5), (x0 + dw - 2, 5)):
        p.rect(xx, y - dh - 6, xx + 5, y - 2, H('8a5a30')); p.vline(xx, y - dh - 6, y - 2, light(H('8a5a30'), 0.2)); p.vline(xx + 5, y - dh - 6, y - 2, shade(H('8a5a30'), 0.3))
    p.rect(x0 - 8, y - dh - 8, x0 + dw + 6, y - dh - 1, H('9a6a3a')); p.hline(x0 - 8, x0 + dw + 6, y - dh - 8, light(H('9a6a3a'), 0.25)); p.hline(x0 - 8, x0 + dw + 6, y - dh - 1, shade(H('9a6a3a'), 0.35))
    p.line(x0 - 3, y - dh + 12, x0 + 12, y - dh - 1, H('7a4a2a'), 3); p.line(x0 + dw + 1, y - dh + 12, x0 + dw - 14, y - dh - 1, H('7a4a2a'), 3)
    hang_sign(p, x0 + dw + 6, y - dh + 6, 'beliung', 'r', w=13, h=12) if False else None
    p.rect(cx - 12, y - dh - 22, cx + 12, y - dh - 10, H('c18c50')); p.hline(cx - 12, cx + 12, y - dh - 22, light(H('c18c50'), 0.3)); icon(p, 'beliung', cx - 4, y - dh - 21)
    lantern(p, x0 - 10, y - 38)
    # rel & gerobak tambang
    p.rect(x0 + 12, y - 4, w - 16, y - 2, H('4a4a58')); 
    for xx in range(x0 + 14, w - 16, 7): p.rect(xx, y - 2, xx + 2, y, H('7a4a2a'))
    cart = (w - 58, y - 20)
    p.rect(cart[0], cart[1], cart[0] + 22, cart[1] + 12, H('7a4a2a')); p.hline(cart[0], cart[0] + 22, cart[1], light(H('7a4a2a'), 0.25)); p.hline(cart[0], cart[0] + 22, cart[1] + 12, shade(H('7a4a2a'), 0.4))
    p.rect(cart[0] + 2, cart[1] - 3, cart[0] + 20, cart[1], H('555b6b'))
    for k in range(5): p.pt(cart[0] + 4 + k * 4, cart[1] - 3 - (k % 2), H('7fe0ff') if k % 2 else H('b8f0ff'))
    for wx in (cart[0] + 3, cart[0] + 17): p.ell(wx, cart[1] + 9, wx + 5, cart[1] + 14, H('2a2a34')); p.pt(wx + 2, cart[1] + 11, H('8a90a0'))
    return finish(p)


def orc_hut(w=190, seed=47):
    Ht = 150
    p = Pen(w, Ht); cx = w // 2; y = Ht - 1
    hide = H('7a5240'); 
    # tenda kulit besar di tengah
    pts = [(cx - 46, y - 10), (cx - 30, y - 70), (cx, y - 118), (cx + 30, y - 70), (cx + 46, y - 10)]
    m = p.mask(pts); ys, xs = np.where(m); px = p.im.load()
    for yy, xx in zip(ys, xs):
        panel = (xx - (cx - 50)) // 18
        c = mix(hide, H('9a6a4a'), 0.35 if panel % 2 else 0.0)
        if (yy % 12) == 0: c = shade(c, 0.35)
        px[int(xx), int(yy)] = c
    for k in range(-2, 3):
        p.line(cx, y - 118, cx + k * 16, y - 12, shade(hide, 0.42))
        for yy in range(y - 100, y - 14, 6): p.pt(cx + int(k * 16 * (yy - (y - 118)) / 106), yy, H('e8dcc0'))
    p.line(cx - 46, y - 10, cx, y - 118, shade(hide, 0.55), 2); p.line(cx + 46, y - 10, cx, y - 118, shade(hide, 0.55), 2)
    # pintu kulit (flap) setinggi NPC
    p.rect(cx - 14, y - 52, cx + 13, y - 2, H('2a1612'))
    p.poly([(cx - 15, y - 54), (cx - 1, y - 54), (cx - 5, y - 14), (cx - 15, y - 4)], H('6a4232')); p.poly([(cx + 14, y - 54), (cx + 1, y - 54), (cx + 5, y - 14), (cx + 14, y - 4)], H('7a5240'))
    for (tx, d) in ((cx - 16, -1), (cx + 15, 1)):
        p.poly([(tx, y - 50), (tx + d * 5, y - 56), (tx + d * 2, y - 44)], H('f3ead8'))
    # tengkorak di puncak
    p.ell(cx - 5, y - 134, cx + 5, y - 122, H('efe4c4')); p.rect(cx - 3, y - 124, cx + 3, y - 120, H('efe4c4')); p.rect(cx - 3, y - 131, cx - 2, y - 129, H('2a1c22')); p.rect(cx + 2, y - 131, cx + 3, y - 129, H('2a1c22'))
    p.line(cx - 12, y - 128, cx + 12, y - 120, H('e8dcc0'), 2)
    # pagar kayu runcing kiri-kanan
    rng = random.Random(seed)
    for side in (-1, 1):
        for i in range(8):
            px0 = cx + side * (52 + i * 9) - (0 if side > 0 else 8)
            h = rng.randint(52, 80)
            c = H('7a5a3a')
            p.rect(px0, y - h, px0 + 7, y, c); p.vline(px0, y - h, y, light(c, 0.2)); p.vline(px0 + 7, y - h, y, shade(c, 0.3))
            p.poly([(px0, y - h), (px0 + 3.5, y - h - 8), (px0 + 7, y - h)], c)
            p.hline(px0, px0 + 7, y - 22, shade(c, 0.35)); p.hline(px0, px0 + 7, y - h + 12, shade(c, 0.3))
    # panji merah
    for bx in (cx - 62, cx + 56):
        p.vline(bx + 4, y - 120, y - 4, H('5a3a22')); p.poly([(bx, y - 116), (bx + 9, y - 114), (bx + 9, y - 90), (bx + 5, y - 96), (bx, y - 90)], H('b03a3a')); icon(p, 'tangan', bx - 1, y - 112) if False else None
        p.ell(bx + 2, y - 108, bx + 7, y - 100, H('f3ead8'))
    p.rect(cx - 8, y - 1, cx + 8, y, H('3a2a20'))
    return finish(p)


def tower(w=84, floors=3, base=H('b8aa94'), plaster=H('d8c8f0'), roof_c=H('6a4a9a'), accent=H('f0c455'), kind='alch', seed=49):
    Ht = 7 + 56 + (floors - 1) * 44 + 64 + 18
    p = Pen(w, Ht); cx = w // 2; y = Ht - 1
    tw = w - 28; x0 = cx - tw // 2; x1 = x0 + tw - 1
    foundation(p, x0 - 2, x1 + 2, y - 6, y, seed=seed)
    g1 = y - 7
    stone_rect(p, x0, g1 - 55, x1, g1, base, seed=seed)
    door(p, cx - 13, g1 - 44, 26, 44, wood=H('5a3a5a') if kind != 'alch' else H('4a5a3a'), arch=True)
    steps(p, cx - 17, cx + 17, g1 + 6, n=2)
    cur = g1 - 56
    for f in range(1, floors):
        u1 = cur; u0 = u1 - 43
        if kind == 'alch':
            plaster_rect(p, x0 - 3, u0, x1 + 3, u1, plaster, seed=seed + f); timber_frame(p, x0 - 3, u0, x1 + 3, u1, H('4a3a5a'), bays=2, brace='v')
            p.ell(cx - 7, u0 + 12, cx + 7, u0 + 28, H('3a2a5a')); p.ell(cx - 5, u0 + 14, cx + 5, u0 + 26, H('7fe880')); p.vline(cx, u0 + 14, u0 + 26, H('3a2a5a')); p.hline(cx - 5, cx + 5, u0 + 20, H('3a2a5a'))
        else:
            stone_rect(p, x0, u0, x1, u1, base, seed=seed + f)
            window(p, cx - 5, u0 + 10, 10, 20, arched=True, glass=H('9ad0ff'), frame=H('5a6a8a'))
        p.hline(x0 - 3, x1 + 3, u1 + 1, H('3a2a3a')); cur = u0 - 1
    # bukit atas
    if kind == 'alch':
        p.rect(x0 - 6, cur - 2, x1 + 6, cur + 3, H('8a6a4a')); p.hline(x0 - 6, x1 + 6, cur - 2, light(H('8a6a4a'), 0.3))
        for xx in range(x0 - 5, x1 + 6, 5): p.vline(xx, cur - 10, cur - 3, H('3a2a3a'))
        p.hline(x0 - 6, x1 + 6, cur - 11, H('3a2a3a'))
        p.ell(x0 - 2, cur - 20, x0 + 12, cur - 4, H('2a2a34')); p.ell(x0, cur - 18, x0 + 10, cur - 12, H('7fe880'))
    ytop = roof_cone(p, cx, cur - 1, tw // 2 + 9, 62, roof_c, kind='tile' if kind == 'alch' else 'slate')
    # bintang bulan di atap
    if kind == 'alch':
        icon(p, 'ramuan', cx - 4, cur - 40)
        chimney(p, cx + tw // 2 - 6, ytop + 8, ytop + 34, w=8, base=H('8a7a8a'), stone=True, seed=3)
    else:
        for (sx_, sy_) in ((cx - 8, cur - 40), (cx + 6, cur - 26), (cx - 2, cur - 14)): p.poly([(sx_, sy_ - 3), (sx_ + 1, sy_ - 1), (sx_ + 3, sy_), (sx_ + 1, sy_ + 1), (sx_, sy_ + 3), (sx_ - 1, sy_ + 1), (sx_ - 3, sy_), (sx_ - 1, sy_ - 1)], accent)
        p.ell(cx - 4, ytop - 16, cx + 4, ytop - 8, H('7fe0ff')); p.ell(cx - 2, ytop - 14, cx + 1, ytop - 11, H('e8ffff'))
    return finish(p)

def test4():
    ims = [treehouse(), shrine(), mine(), orc_hut(), tower(kind='alch'), tower(kind='mage', base=H('9aa8c8'), roof_c=H('3a5a9a'), w=84)]
    W = sum(i.width for i in ims) + 5 * len(ims); Hh = max(i.height for i in ims)
    bg = Image.new('RGBA', (W, Hh), (150, 200, 230, 255)); x = 5
    for im in ims:
        bg.alpha_composite(im, (x, Hh - im.height)); x += im.width + 5
    up(bg, 2).save('/home/claude/work/bt4.png'); print(bg.size, [i.size for i in ims])
