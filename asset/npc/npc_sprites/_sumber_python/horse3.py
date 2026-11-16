"""Kuda v3 – anatomi mengikuti referensi (3 lingkaran, kepala baji, lutut kotak, fetlock tebal, teracak segitiga).
Rig: badan (pitch/dx/dy) -> leher (rot) -> kepala (rot di poll); kaki IK 2-tulang + sendi; semua dirender 4x lalu
di-sampling tengah => sub-pixel halus. Tiap bagian = 1 layer terpisah.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageChops
from pxlib import H, comp, new, sheet, up, mix, darker

SS = 4
GY = 63.0
PIV = (54.0, 24.0)
POLL = (75.5, 8.0)
CEN = (40.0, 33.0)
STD = (96, 64, 0, 0)
BIG = (128, 96, 16, 28)

# ---------------------------------------------------------------- palet
def pal_bay():
    return dict(base=H('a95b33'), light=H('c77c45'), high=H('e09d5f'), shade=H('7d3f27'), deep=H('55291d'),
                low=H('3e2219'), hoof=H('6e6878'), hoof_hi=H('958fa3'),
                mane=H('2d3f47'), mane_hi=H('4f6a74'), mane_d=H('1b272d'),
                muzzle=H('4b2d25'), muzzle_hi=H('87594b'), ear_in=H('8a4a38'), eye=H('120d0e'), sock=False)

def pal_white():
    return dict(base=H('dde1e7'), light=H('f1f3f6'), high=H('ffffff'), shade=H('b2bac5'), deep=H('8a93a1'),
                low=H('b9c0ca'), hoof=H('787385'), hoof_hi=H('9b97aa'),
                mane=H('2d3f47'), mane_hi=H('506b75'), mane_d=H('1b272d'),
                muzzle=H('9b929e'), muzzle_hi=H('c9c0c6'), ear_in=H('d9aeae'), eye=H('120d0e'), sock=False)

def pal_black():
    return dict(base=H('3d3941'), light=H('55505c'), high=H('6e6876'), shade=H('2b282f'), deep=H('1a181e'),
                low=H('27242b'), hoof=H('6e6878'), hoof_hi=H('938da0'),
                mane=H('232f35'), mane_hi=H('3e535c'), mane_d=H('141c20'),
                muzzle=H('2a262b'), muzzle_hi=H('5b525b'), ear_in=H('5a4650'), eye=H('c9c2cc'), sock=False)

def pal_chestnut():
    return dict(base=H('b9693b'), light=H('d48c52'), high=H('eaa96c'), shade=H('8f4c2d'), deep=H('6c3624'),
                low=H('f1ebdf'), hoof=H('6e6878'), hoof_hi=H('938da0'),
                mane=H('e2bd78'), mane_hi=H('f3dc9c'), mane_d=H('b98f4f'),
                muzzle=H('d9a285'), muzzle_hi=H('efc7ae'), ear_in=H('a45a3c'), eye=H('120d0e'), sock=True)

PALS = {'bay': pal_bay, 'putih': pal_white, 'hitam': pal_black, 'kastanye': pal_chestnut}


def far_pal(p):
    q = dict(p)
    for k in ('base', 'light', 'high', 'shade', 'low', 'hoof', 'hoof_hi'):
        q[k] = mix(p[k], p['deep'], 0.45)
    q['deep'] = mix(p['deep'], (10, 6, 10), 0.3)
    return q

# ---------------------------------------------------------------- geometry
def chaikin(pts, it=2, closed=True):
    for _ in range(it):
        out = [] if closed else [pts[0]]
        rng = range(len(pts)) if closed else range(len(pts) - 1)
        for i in rng:
            a, b = pts[i], pts[(i + 1) % len(pts)]
            out.append((a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25))
            out.append((a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75))
        if not closed:
            out.append(pts[-1])
        pts = out
    return pts


def rot(p, piv, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    x, y = p[0] - piv[0], p[1] - piv[1]
    return (piv[0] + x * c - y * s, piv[1] + x * s + y * c)


def ellp(cx, cy, rx, ry, deg=0, n=26):
    return [rot((cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)), (cx, cy), deg) for i in range(n)]


def capp(p0, p1, w0, w1):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1e-6
    nx, ny = -dy / L, dx / L
    return [(p0[0] + nx * w0 / 2, p0[1] + ny * w0 / 2), (p1[0] + nx * w1 / 2, p1[1] + ny * w1 / 2),
            (p1[0] - nx * w1 / 2, p1[1] - ny * w1 / 2), (p0[0] - nx * w0 / 2, p0[1] - ny * w0 / 2)]


def smooth(s):
    s = max(0.0, min(1.0, s))
    return s * s * (3 - 2 * s)


class Rig:
    def __init__(self, p):
        self.p = p

    def B(self, pt):
        x, y = rot(pt, CEN, self.p['pitch'])
        return (x + self.p['dx'], y + self.p['dy'])

    def Bs(self, pts):
        return [self.B(q) for q in pts]

    def N(self, pt):
        return self.B(rot(pt, PIV, self.p['neck']))

    def Ns(self, pts):
        return [self.N(q) for q in pts]

    def Hd(self, pt):
        return self.B(rot(rot(pt, POLL, self.p['head']), PIV, self.p['neck']))

    def Hs(self, pts):
        return [self.Hd(q) for q in pts]


class Cv:
    def __init__(self, spec):
        self.W, self.Hh, self.ox, self.oy = spec
        self.im = Image.new('RGBA', (self.W * SS, self.Hh * SS), (0, 0, 0, 0))
        self.mask = Image.new('L', (self.W * SS, self.Hh * SS), 0)
        self.d = ImageDraw.Draw(self.im)
        self.dm = ImageDraw.Draw(self.mask)

    def S(self, pts):
        return [((x + self.ox) * SS, (y + self.oy) * SS) for x, y in pts]

    def poly(self, pts, col):
        s = self.S(pts)
        self.d.polygon(s, fill=col)
        self.dm.polygon(s, fill=255)

    def cpoly(self, pts, col):
        s = self.S(pts)
        xs = [p[0] for p in s]; ys = [p[1] for p in s]
        x0, y0 = max(int(min(xs)) - 1, 0), max(int(min(ys)) - 1, 0)
        x1, y1 = min(int(max(xs)) + 2, self.im.width), min(int(max(ys)) + 2, self.im.height)
        if x1 <= x0 or y1 <= y0:
            return
        t = Image.new('L', (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(t).polygon([(x - x0, y - y0) for x, y in s], fill=255)
        a = ImageChops.multiply(t, self.mask.crop((x0, y0, x1, y1)))
        self.im.paste(col, (x0, y0), a)

    def cap(self, p0, p1, w0, w1, col, rnd=True):
        self.poly(capp(p0, p1, w0, w1), col)
        if rnd:
            self.poly(ellp(p0[0], p0[1], w0 / 2, w0 / 2, 0, 14), col)
            self.poly(ellp(p1[0], p1[1], w1 / 2, w1 / 2, 0, 14), col)

    def ccap(self, p0, p1, w0, w1, col, rnd=True):
        self.cpoly(capp(p0, p1, w0, w1), col)
        if rnd:
            self.cpoly(ellp(p0[0], p0[1], w0 / 2, w0 / 2, 0, 12), col)
            self.cpoly(ellp(p1[0], p1[1], w1 / 2, w1 / 2, 0, 12), col)

    def out(self):
        return self.im.resize((self.W, self.Hh), Image.NEAREST)


def put(img, spec, x, y, c):
    x, y = int(math.floor(x + spec[2])), int(math.floor(y + spec[3]))
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), c)

# ---------------------------------------------------------------- BODY  (3 lingkaran + otot)
TORSO = [(53, 20.6), (44, 22.8), (35, 22.4), (27, 20.8), (20.4, 21.6), (17.0, 25.6), (16.0, 30.8), (16.4, 35.0),
         (19.0, 38.4), (26, 39.4), (33, 39.8), (42, 40.8), (50, 41.2), (56, 40.6), (61.8, 38.0), (64.8, 33.4),
         (65.2, 28.4), (63.0, 23.8), (58.5, 21.2)]


def stripe(a, b, w):
    return capp(a, b, w, w)


def limb_poly(p0, p1, stations):
    """stasiun (t, lebar, geser) sepanjang p0->p1; geser + = ke sisi normal (-uy,ux)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1e-6
    nx, ny = -dy / L, dx / L
    left, right = [], []
    for t, w, sh in stations:
        cx, cy = p0[0] + dx * t + nx * sh, p0[1] + dy * t + ny * sh
        left.append((cx + nx * w / 2, cy + ny * w / 2)); right.append((cx - nx * w / 2, cy - ny * w / 2))
    return chaikin(left + right[::-1], 2)


def pt_on(p0, p1, t, sh=0.0):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1e-6
    return (p0[0] + dx * t - dy / L * sh, p0[1] + dy * t + dx / L * sh)


def dither(img, a, b, vertical=True):
    """transisi a->b berpola catur (a di atas b)."""
    arr = np.array(img)
    A = np.array(a[:3]); B = np.array(b[:3])
    isA = (arr[..., :3] == A).all(-1) & (arr[..., 3] > 0)
    isB = (arr[..., :3] == B).all(-1) & (arr[..., 3] > 0)
    h, w = isA.shape
    yy, xx = np.mgrid[0:h, 0:w]
    chk = ((xx + yy) % 2 == 0)
    up_ = np.zeros_like(isA); up_[1:] = isA[:-1]
    dn_ = np.zeros_like(isA); dn_[:-1] = isB[1:]
    toA = isB & up_ & chk
    toB = isA & dn_ & ~chk
    arr[toA, :3] = A
    arr[toB, :3] = B
    return Image.fromarray(arr, 'RGBA')


def layer_body(spec, p, pal):
    R = Rig(p); c = Cv(spec)
    tor = chaikin(TORSO, 2)
    c.poly(R.Bs(tor), pal['base'])
    # --- bayangan besar (3 tingkat) + cahaya pantul perut
    c.cpoly(R.Bs([(10, 32.4), (20, 33.8), (30, 35.0), (40, 36.0), (50, 35.6), (58, 34.4), (70, 31), (72, 52), (10, 52)]), pal['shade'])
    c.cpoly(R.Bs([(10, 37.6), (24, 38.0), (36, 38.6), (48, 38.9), (58, 38.1), (70, 36.0), (72, 52), (10, 52)]), pal['deep'])
    # --- cahaya atas (rim) mengikuti garis punggung & kroup
    top = [(52, 21.2), (44, 23.4), (35, 23.0), (27, 21.5), (21, 22.2), (18.3, 25.2)]
    for i in range(len(top) - 1):
        c.ccap(R.B(top[i]), R.B(top[i + 1]), 2.6, 2.6, pal['light'], False)
    for i in range(len(top) - 1):
        c.ccap(R.B((top[i][0], top[i][1] - 0.5)), R.B((top[i + 1][0], top[i + 1][1] - 0.5)), 1.1, 1.1, pal['high'], False)
    # --- bokong: otot gluteal (kroup bulat), biseps femoris (paha), tuber coxae (tulang pinggul)
    c.cpoly(R.Bs(ellp(22.0, 27.0, 6.4, 6.4)), pal['light'])
    c.cpoly(R.Bs(ellp(21.0, 25.0, 3.8, 3.0, -25)), pal['high'])
    c.cpoly(R.Bs(ellp(31.6, 30.2, 7.0, 6.2, 10)), pal['light'])
    c.cpoly(R.Bs(ellp(30.6, 27.9, 4.2, 2.8, -12)), pal['high'])
    c.cpoly(R.Bs(ellp(27.2, 23.2, 2.1, 1.7)), pal['high'])                       # tulang pinggul
    c.cpoly(R.Bs(stripe((25.2, 24.6), (26.0, 36.0), 1.0)), pal['shade'])         # celah gluteal/paha
    c.cpoly(R.Bs(stripe((27.8, 24.8), (19.0, 28.0), 0.9)), pal['shade'])         # garis kroup -> pangkal ekor
    c.cpoly(R.Bs(ellp(18.6, 33.2, 2.4, 5.0, 10)), pal['shade'])                  # sisi belakang paha (bayangan)
    c.cpoly(R.Bs(ellp(24.0, 37.0, 4.6, 1.6)), pal['light'])                      # cahaya pantul bawah paha
    # --- rusuk (perut) : garis samar miring
    rib = mix(pal['base'], pal['shade'], 0.55)
    for i in range(5):
        x0 = 36.0 + 3.2 * i
        c.cpoly(R.Bs(stripe((x0, 27.0), (x0 - 3.2, 36.8), 0.8)), rib)
    c.cpoly(R.Bs(ellp(36.5, 27.6, 7.0, 2.0)), pal['light'])                      # cahaya punggung tengah
    # --- lipatan flank & otot perut
    c.cpoly(R.Bs(ellp(29.5, 36.0, 7.5, 2.0)), pal['shade'])
    c.cpoly(R.Bs(stripe((30, 36.4), (45, 37.6), 0.8)), pal['deep'])
    # --- bahu: skapula, triceps, pektoral
    c.cpoly(R.Bs(ellp(55.2, 29.2, 5.8, 7.0, 8)), pal['light'])
    c.cpoly(R.Bs(ellp(54.4, 25.8, 3.0, 3.2, 8)), pal['high'])
    c.cpoly(R.Bs(stripe((51.6, 22.4), (56.8, 37.0), 0.9)), pal['shade'])         # tepi skapula
    c.cpoly(R.Bs(ellp(51.6, 33.6, 3.2, 3.8, -8)), pal['shade'])                  # triceps (di belakang siku)
    c.cpoly(R.Bs(ellp(61.4, 32.0, 3.4, 5.0, 12)), pal['light'])                  # dada / pektoral
    c.cpoly(R.Bs(ellp(60.8, 29.4, 1.8, 2.4, 12)), pal['high'])
    c.cpoly(R.Bs(ellp(58.4, 37.4, 3.0, 2.2)), pal['shade'])                      # siku
    out = c.out()
    out = dither(out, pal['base'], pal['shade'])
    out = dither(out, pal['shade'], pal['deep'])
    return out

# ---------------------------------------------------------------- NECK + HEAD
NECK = [(50, 22.4), (55.5, 17.6), (61.5, 12.8), (67.5, 9.0), (73, 6.8), (77.2, 7.6), (76.4, 12.6), (74.5, 18.6),
        (71.8, 25), (69.0, 32.0), (66.4, 38.6), (60, 41.5), (54, 36), (51.5, 29)]
HEAD = [(74.6, 7.2), (79.4, 8.2), (83.6, 11.6), (87.4, 15.6), (90.2, 19.6), (91.8, 22.2), (91.4, 24.2), (89.8, 25.2),
        (88.4, 26.7), (86.2, 26.2), (84.0, 24.2), (80.4, 22.0), (77.6, 19.4), (76.0, 15.6), (74.4, 10.8)]
EAR_N = [(75.2, 8.2), (74.6, 4.4), (75.8, 0.8), (77.8, 4.6), (78.2, 7.8)]
EAR_F = [(73.4, 8.2), (72.8, 5.0), (73.8, 2.0), (75.6, 5.0), (75.8, 7.8)]
EYE = (80.0, 12.8)
EAR_BASE = (76.4, 8.2)


def ear_pts(pts, p):
    return [rot(q, EAR_BASE, p['ear']) for q in pts]


def layer_head(spec, p, pal):
    R = Rig(p); c = Cv(spec)
    c.poly(R.Hs(chaikin(ear_pts(EAR_F, p), 1)), mix(pal['base'], pal['deep'], 0.5))
    c.poly(R.Ns(chaikin(NECK, 2)), pal['base'])
    c.poly(R.Hs(chaikin(HEAD, 2)), pal['base'])
    c.poly(R.Hs(chaikin(ear_pts(EAR_N, p), 1)), pal['base'])
    c.cpoly(R.Hs(chaikin([(75.9, 7.4), (75.4, 4.6), (75.9, 2.4), (77.1, 4.8), (77.2, 7.2)], 1)), pal['ear_in'])
    # leher: bayangan bawah, lekuk vena jugularis, otot (brakiosefalikus), cahaya jengger
    c.cpoly(R.Ns([(76.6, 12), (74.5, 18.6), (71.8, 25), (69.0, 32.0), (66.4, 38.6), (60, 42), (63, 34), (67, 27.5), (70.6, 21), (73.4, 15.5)]), pal['shade'])
    c.cpoly(R.Ns(stripe((74.4, 19.8), (65.6, 36.4), 1.0)), pal['deep'])
    c.cpoly(R.Ns(stripe((57.0, 26.0), (69.0, 15.0), 5.0)), pal['light'])
    c.cpoly(R.Ns(stripe((58.5, 24.6), (68.0, 15.8), 1.4)), pal['high'])
    c.cpoly(R.Ns(stripe((56.0, 29.0), (66.0, 22.0), 0.9)), pal['shade'])         # garis otot leher
    # kepala: pipi (masseter), batang hidung, rahang, vena rahang, benjolan dagu
    c.cpoly(R.Hs(ellp(78.8, 16.6, 3.6, 4.6, 30)), pal['light'])
    c.cpoly(R.Hs(ellp(78.2, 15.0, 1.8, 2.4, 30)), pal['high'])
    c.cpoly(R.Hs(stripe((79.6, 9.4), (90.0, 20.4), 1.3)), pal['light'])          # batang hidung
    c.cpoly(R.Hs([(77.6, 19.4), (80.4, 22.0), (84.0, 24.2), (86.2, 26.2), (88.4, 26.7), (89.8, 25.2), (86.0, 23.2), (82.4, 20.6), (79.2, 17.8)]), pal['shade'])
    c.cpoly(R.Hs(stripe((78.8, 17.2), (82.8, 22.6), 0.9)), pal['deep'])          # vena rahang
    c.cpoly(R.Hs(ellp(89.4, 22.6, 2.8, 3.4, 30)), pal['muzzle'])
    c.cpoly(R.Hs(ellp(89.8, 21.2, 1.3, 1.7, 30)), pal['muzzle_hi'])
    c.cpoly(R.Hs(ellp(87.8, 26.0, 1.5, 1.0)), pal['light'])                      # dagu
    c.cpoly(R.Hs(ellp(79.6, 12.6, 2.9, 2.5)), mix(pal['base'], pal['shade'], 0.55))   # rongga mata
    c.cpoly(R.Hs(stripe((76.4, 9.6), (82.0, 10.6), 1.1)), pal['light'])          # tulang alis
    out = c.out()
    ex, ey = R.Hd(EYE)
    ex, ey = int(round(ex)), int(round(ey))
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        put(out, spec, ex + dx, ey + dy, pal['eye'])
    put(out, spec, ex + 1, ey, H('ffffff') if pal['eye'][0] < 100 else H('202020'))
    dk = mix(pal['base'], pal['deep'], 0.7)
    for dx, dy in ((-1, 0), (-1, -1), (0, -1), (1, -1), (2, -1)):
        put(out, spec, ex + dx, ey + dy, dk)                                      # kelopak
    nx, ny = R.Hd((90.4, 21.4)); put(out, spec, round(nx), round(ny), pal['deep']); put(out, spec, round(nx) + 1, round(ny) + 1, pal['deep'])
    put(out, spec, round(nx) - 1, round(ny) - 1, pal['muzzle_hi'])
    mx, my = R.Hd((89.0, 24.8)); put(out, spec, round(mx), round(my), pal['deep'])
    mx2, my2 = R.Hd((87.6, 25.0)); put(out, spec, round(mx2), round(my2), pal['shade'])
    return out

# ---------------------------------------------------------------- MANE
CREST = [(51.8, 21.4), (55.4, 18.2), (59.0, 15.2), (62.6, 12.6), (66.2, 10.4), (69.8, 8.7), (73.4, 7.4)]


def layer_mane(spec, p, pal):
    R = Rig(p); c = Cv(spec)
    n = len(CREST); outer, inner = [], []
    wind = p.get('wind', 0.0)
    for i, (x, y) in enumerate(CREST):
        a = CREST[max(i - 1, 0)]; b = CREST[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L
        k = i / float(n - 1)
        w = 7.0 - 3.2 * k + (0.9 if i % 2 else -0.4)
        sway = math.sin(p['mane'] - i * 0.8) * (0.35 + 0.65 * k) * (0.9 + 0.8 * abs(wind))
        outer.append((x - nx * 1.0, y - ny * 1.0))
        inner.append((x + nx * w + sway * 0.8 - wind * (0.4 + 1.6 * k) * 1.0, y + ny * w + sway * 0.6 - abs(wind) * 0.3 * k))
    poly = outer + inner[::-1]
    c.poly(R.Ns(chaikin(poly, 1)), pal['mane'])
    for i in range(n - 1):
        c.ccap(R.N(outer[i]), R.N(inner[i + 1]), 1.0, 1.0, pal['mane_hi'], False)
    for i in range(1, n):
        o = (outer[i][0] * 0.4 + inner[i][0] * 0.6, outer[i][1] * 0.4 + inner[i][1] * 0.6)
        c.ccap(R.N(outer[i]), R.N(o), 0.9, 0.9, pal['mane_d'], False)
    sw = math.sin(p['mane'] - 2.2) * 0.4 - wind * 0.8
    fl = [(75.4, 6.6), (78.4, 7.4), (79.2 + sw, 10.6), (77.6 + sw, 10.0), (76.4, 8.8)]
    c.poly(R.Hs(fl), pal['mane'])
    c.ccap(R.Hd((76.2, 7.6)), R.Hd((77.9 + sw, 9.8)), 0.9, 0.9, pal['mane_hi'], False)
    return c.out()

# ---------------------------------------------------------------- TAIL
def layer_tail(spec, p, pal):
    R = Rig(p); c = Cv(spec)
    root = R.B((18.0, 24.5))
    sway = p.get('tailsway', 0.0)
    base = p.get('tailbase', 12.0)
    curve = p.get('tailcurve', 2.2)
    Ls = [5.0, 5.4, 5.4, 5.0, 4.4, 3.6]
    wd = [6.0, 7.0, 7.0, 6.4, 5.2, 3.6, 1.6]
    a = base + p['pitch'] * -1.0 + 3 * sway
    pts = [root]; cur = root
    for i, l in enumerate(Ls):
        a += curve + sway * (1.2 + i * 0.55)
        cur = (cur[0] - math.sin(math.radians(a)) * l, cur[1] + math.cos(math.radians(a)) * l)
        pts.append(cur)
    for i in range(len(pts) - 1):
        c.cap(pts[i], pts[i + 1], wd[i], wd[i + 1], pal['mane'])
    for i in range(len(pts) - 1):
        c.ccap((pts[i][0] + 1.0, pts[i][1] + 0.2), (pts[i + 1][0] + 0.9, pts[i + 1][1] + 0.2), 1.0, 1.0, pal['mane_hi'])
    for i in range(1, len(pts) - 1):
        c.ccap((pts[i][0] - 1.4, pts[i][1]), (pts[i + 1][0] - 1.3, pts[i + 1][1]), 0.9, 0.9, pal['mane_d'])
    return c.out()

# ---------------------------------------------------------------- LEGS
def solve_ik(h, f, l1, l2, bend):
    dx, dy = f[0] - h[0], f[1] - h[1]
    dist = math.hypot(dx, dy) or 1e-6
    d = max(min(dist, l1 + l2 - 0.02), abs(l1 - l2) + 0.02)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    hh = math.sqrt(max(l1 * l1 - a * a, 0))
    ux, uy = dx / dist, dy / dist
    mx, my = h[0] + ux * a, h[1] + uy * a
    k1 = (mx - uy * hh, my + ux * hh); k2 = (mx + uy * hh, my - ux * hh)
    if bend > 0:
        return k1 if k1[0] > k2[0] else k2
    return k1 if k1[0] < k2[0] else k2


LEG = {
    'HN': dict(front=False, hip=(28.0, 33.0), far=False, L1=15.9, L2=10.5),
    'HF': dict(front=False, hip=(28.0, 33.0), far=True, L1=15.9, L2=10.5),
    'FN': dict(front=True, hip=(56.5, 34.6), far=False, L1=12.0, L2=11.9),
    'FF': dict(front=True, hip=(56.5, 34.6), far=True, L1=12.0, L2=11.9),
}


def norm(v):
    l = math.hypot(*v) or 1e-6
    return (v[0] / l, v[1] / l)


def leg_geom(p, key):
    R = Rig(p); g = LEG[key]
    hip = R.B(g['hip'])
    Fx, Fy, th = p['legs'][key]
    F = (Fx, Fy)
    K = solve_ik(hip, F, g['L1'], g['L2'], +1 if g['front'] else -1)
    return hip, K, F, th


def layer_leg(spec, p, pal0, key):
    g = LEG[key]; pal = far_pal(pal0) if g['far'] else pal0
    front = g['front']; far = g['far']
    hip, K, F, th = leg_geom(p, key)
    c = Cv(spec)
    coat, sh, li, hi, lowc = pal['base'], pal['shade'], pal['light'], pal['high'], pal['low']
    # ---- lengan atas: otot besar (lengan bawah depan / paha-betis belakang)
    if front:
        st = [(0.0, 9.0, 0.0), (0.2, 9.0, -0.5), (0.5, 7.0, -0.2), (0.85, 5.4, 0.0), (1.0, 5.2, 0.0)]
    else:
        st = [(0.0, 11.0, 0.0), (0.2, 10.6, 0.7), (0.5, 8.0, 1.0), (0.8, 5.8, 0.4), (1.0, 5.2, 0.0)]
    c.poly(limb_poly(hip, K, st), sh)
    c.poly(limb_poly(hip, K, [(t, w * 0.80, s_ - 0.5) for t, w, s_ in st]), coat)
    if not far:
        c.cpoly(limb_poly(hip, K, [(0.06, 2.6, st[0][2] - 1.9), (0.3, 3.4, st[1][2] - 1.7), (0.62, 2.2, st[2][2] - 1.2)]), li)
        c.cpoly(limb_poly(hip, K, [(0.12, 1.2, st[0][2] - 2.2), (0.34, 1.6, st[1][2] - 2.0)]), hi)
    # garis otot / tendon di sisi belakang
    a_ = pt_on(hip, K, 0.38, (st[1][2] + 3.6) if not front else (st[1][2] + 3.0))
    c.ccap(a_, pt_on(hip, K, 1.0, 2.0), 0.9, 0.9, mix(sh, pal['deep'], 0.5), False)
    # ---- sendi
    u = norm((hip[0] - K[0], hip[1] - K[1])); v = norm((F[0] - K[0], F[1] - K[1]))
    bs = (u[0] + v[0], u[1] + v[1])
    bis = norm(bs) if math.hypot(*bs) > 0.2 else (-1, 0)
    kc = lowc if pal0['sock'] else coat
    if front:
        c.poly(ellp(K[0], K[1], 2.9, 2.9, 22, 8), kc)
        c.poly([(K[0] - bis[0] * 2.8 - 1.2, K[1] - bis[1] * 2.8 - 1.2), (K[0] - bis[0] * 2.8 + 1.2, K[1] - bis[1] * 2.8 + 1.2), (K[0], K[1])], kc)
        if not far:
            c.cpoly(ellp(K[0] + 0.6, K[1] - 0.6, 1.2, 1.2), li)
    else:
        c.poly(ellp(K[0], K[1], 2.8, 2.9, 0, 12), coat)
        tip = (K[0] - bis[0] * 4.6, K[1] - bis[1] * 4.6)
        pp = (-bis[1], bis[0])
        c.poly([(K[0] + pp[0] * 2.1, K[1] + pp[1] * 2.1), tip, (K[0] - pp[0] * 2.1, K[1] - pp[1] * 2.1)], coat)
        if not far:
            c.cpoly(ellp(tip[0] + bis[0] * 1.6, tip[1] + bis[1] * 1.6, 1.0, 1.0), li)
    # ---- tulang kering (tendon tebal) + garis tendon
    c.poly(limb_poly(K, F, [(0.0, 4.8, 0), (0.5, 3.9, 0), (1.0, 4.5, 0)]), lowc)
    if not far:
        fr = mix(lowc, (255, 255, 255, 255), 0.18) if not pal0['sock'] else mix(lowc, pal['shade'], 0.1)
        c.ccap(pt_on(K, F, 0.1, -1.4), pt_on(K, F, 0.9, -1.4), 0.9, 0.9, fr, False)
    c.ccap(pt_on(K, F, 0.15, 1.6), pt_on(K, F, 0.92, 1.6), 0.8, 0.8, mix(lowc, pal['deep'], 0.45), False)
    # ---- fetlock + bulu kaki + pastern + teracak
    def Lp(px, py):
        return rot((F[0] + px, F[1] + py), F, th)
    feather = mix(lowc, pal['deep'], 0.25)
    c.poly([Lp(-1.2, -0.6), Lp(-3.6, 2.2), Lp(-3.0, 5.0), Lp(-1.4, 4.0), Lp(-0.4, 1.6)], feather)
    c.cpoly([Lp(-1.8, 0.8), Lp(-3.0, 2.6), Lp(-2.6, 4.2), Lp(-1.8, 2.6)], mix(lowc, (255, 255, 255, 255), 0.1))
    c.poly(ellp(F[0], F[1], 2.8, 2.8, 0, 12), lowc)
    c.cap(Lp(0, 0.2), Lp(1.1, 3.0), 4.0, 3.7, lowc)
    c.poly([Lp(-2.0, 2.4), Lp(2.0, 2.4), Lp(4.1, 5.2), Lp(-2.9, 5.2)], pal['hoof'])
    c.cpoly([Lp(-2.0, 2.4), Lp(2.0, 2.4), Lp(2.3, 3.2), Lp(-2.1, 3.2)], pal['hoof_hi'])
    c.cpoly([Lp(-2.9, 4.6), Lp(4.1, 4.6), Lp(4.1, 5.2), Lp(-2.9, 5.2)], mix(pal['hoof'], (20, 12, 22, 255), 0.45))
    return c.out()

# ---------------------------------------------------------------- outline (numpy)
def outline_under(img, under, mode, hip_px=None, R=10.0):
    a = np.array(img); al = a[..., 3] > 0
    u = np.array(under)[..., 3] > 0
    h, w = al.shape
    pad = np.pad(al, 1)
    nb = [pad[1:-1, 2:], pad[1:-1, :-2], pad[2:, 1:-1], pad[:-2, 1:-1]]
    edge = (nb[0] | nb[1] | nb[2] | nb[3]) & ~al
    if mode == 'outer':
        edge &= ~u
    elif mode == 'legs' and hip_px is not None:
        yy, xx = np.mgrid[0:h, 0:w]
        near = (xx - hip_px[0]) ** 2 + (yy - hip_px[1]) ** 2 < R * R
        edge &= ~(u & near)
    padc = np.pad(a, ((1, 1), (1, 1), (0, 0)))
    cols = [padc[1:-1, 2:], padc[1:-1, :-2], padc[2:, 1:-1], padc[:-2, 1:-1]]
    col = np.zeros_like(a)
    done = np.zeros(al.shape, bool)
    for nbm, cc in zip(nb, cols):
        sel = nbm & ~done & edge
        col[sel] = cc[sel]
        done |= nbm
    dark = np.array((28, 14, 24), float)
    outc = (col[..., :3].astype(float) * (1 - 0.62) + dark * 0.62).astype(np.uint8)
    res = a.copy()
    res[edge, :3] = outc[edge]
    res[edge, 3] = 255
    return Image.fromarray(res, 'RGBA')


ORDER = [('01_kaki_belakang_jauh', 'HF'), ('02_kaki_depan_jauh', 'FF'), ('03_ekor', 'tail'), ('04_badan', 'body'),
         ('05_leher_kepala', 'head'), ('06_surai', 'mane'), ('07_kaki_belakang_dekat', 'HN'), ('08_kaki_depan_dekat', 'FN')]
MODES = {'HF': 'all', 'FF': 'all', 'tail': 'all', 'body': 'all', 'head': 'outer', 'mane': 'outer', 'HN': 'legs', 'FN': 'legs'}


def render_frame(spec, p, pal):
    raw = {'HF': layer_leg(spec, p, pal, 'HF'), 'FF': layer_leg(spec, p, pal, 'FF'), 'tail': layer_tail(spec, p, pal),
           'body': layer_body(spec, p, pal), 'head': layer_head(spec, p, pal), 'mane': layer_mane(spec, p, pal),
           'HN': layer_leg(spec, p, pal, 'HN'), 'FN': layer_leg(spec, p, pal, 'FN')}
    under = new(spec[0], spec[1]); res = {}
    for name, key in ORDER:
        hp = None
        if MODES[key] == 'legs':
            hp = leg_geom(p, key)[0]
            hp = (hp[0] + spec[2], hp[1] + spec[3])
        o = outline_under(raw[key], under, MODES[key], hp)
        res[name] = o
        under = comp(under, o)
    res['_merged'] = under
    return res
