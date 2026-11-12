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

# ---------------------------------------------------------------- BODY  (3 lingkaran: dada - badan - bokong)
TORSO = [(53, 21), (44, 23.0), (35, 22.6), (27, 21.2), (20.8, 22.2), (17.6, 26.4), (16.8, 31.2), (17.2, 34.6),
         (19.6, 37.8), (26, 39.0), (33, 39.6), (42, 40.7), (50, 41.1), (56, 40.4), (61.4, 37.6), (64.0, 33.2),
         (64.4, 28.4), (62.4, 24.2), (58.5, 21.6)]


def stripe(a, b, w):
    return capp(a, b, w, w)


def layer_body(spec, p, pal):
    R = Rig(p); c = Cv(spec)
    c.poly(R.Bs(chaikin(TORSO, 2)), pal['base'])
    c.cpoly(R.Bs([(10, 33.2), (20, 34.4), (30, 35.6), (40, 36.6), (50, 36.2), (58, 35), (70, 31.5), (72, 52), (10, 52)]), pal['shade'])
    c.cpoly(R.Bs([(10, 38.4), (24, 38.9), (36, 39.5), (48, 39.8), (58, 38.9), (70, 36.6), (72, 52), (10, 52)]), pal['deep'])
    c.cpoly(R.Bs(ellp(39, 26.4, 12.5, 3.0)), pal['light'])                       # sorotan punggung
    c.cpoly(R.Bs(ellp(22.2, 27.4, 5.7, 5.9)), pal['light'])                     # lingkaran bokong
    c.cpoly(R.Bs(ellp(21.3, 25.6, 3.4, 2.8, -20)), pal['high'])
    c.cpoly(R.Bs(ellp(30.6, 30.2, 6.4, 5.4)), pal['light'])                     # paha
    c.cpoly(R.Bs(ellp(29.6, 28.2, 3.9, 2.6, -10)), pal['high'])
    c.cpoly(R.Bs(stripe((25.4, 24.2), (26.2, 35.2), 0.9)), pal['shade'])          # lekuk antar otot
    c.cpoly(R.Bs(ellp(55.3, 30.0, 5.6, 6.8, 8)), pal['light'])                  # bahu
    c.cpoly(R.Bs(ellp(54.4, 26.8, 2.9, 3.1, 8)), pal['high'])
    c.cpoly(R.Bs(stripe((49.8, 25.6), (50.6, 35.6), 0.9)), pal['shade'])
    c.cpoly(R.Bs(ellp(58.2, 37.8, 3.2, 2.3)), pal['shade'])                     # siku
    c.cpoly(R.Bs(ellp(30, 36.0, 8.5, 1.4)), pal['shade'])
    return c.out()

# ---------------------------------------------------------------- NECK + HEAD
NECK = [(50, 22.5), (55.5, 18), (61.5, 13.2), (67.5, 9.4), (73, 7.2), (77.2, 7.8), (76.4, 12.6), (74.5, 18.6),
        (71.8, 25), (68.6, 31.6), (65.5, 37.6), (60, 41.5), (54, 36), (51.5, 29)]
HEAD = [(74.6, 7.4), (79.5, 8.4), (83.8, 12.2), (87.6, 16.4), (90.4, 20.6), (91.4, 23.2), (90.8, 25.0), (88.6, 26.4),
        (86.4, 25.6), (83.2, 23.6), (79.6, 21.3), (77.2, 18.6), (75.8, 14.8), (74.4, 10.6)]
EAR_N = [(75.2, 8.2), (74.9, 4.6), (76.3, 1.5), (78.0, 4.8), (78.1, 7.8)]
EAR_F = [(73.4, 8.2), (73.0, 5.0), (74.0, 2.4), (75.7, 5.2), (75.8, 7.8)]
EYE = (80.2, 13.0)
EAR_BASE = (76.4, 8.2)


def ear_pts(pts, p):
    return [rot(q, EAR_BASE, p['ear']) for q in pts]


def layer_head(spec, p, pal):
    R = Rig(p); c = Cv(spec)
    c.poly(R.Hs(chaikin(ear_pts(EAR_F, p), 1)), mix(pal['base'], pal['deep'], 0.5))
    c.poly(R.Ns(chaikin(NECK, 2)), pal['base'])
    c.poly(R.Hs(chaikin(HEAD, 2)), pal['base'])
    c.poly(R.Hs(chaikin(ear_pts(EAR_N, p), 1)), pal['base'])
    c.cpoly(R.Hs(chaikin([(75.9, 7.4), (75.7, 4.8), (76.5, 3.0), (77.2, 5.0), (77.2, 7.2)], 1)), pal['ear_in'])
    # leher: lekuk vena jugularis + bayangan bawah
    c.cpoly(R.Ns([(76.6, 12), (74.5, 18.6), (71.8, 25), (68.6, 31.6), (65.5, 37.6), (60, 42), (63, 34), (67, 27.5), (70.6, 21), (73.4, 15.5)]), pal['shade'])
    c.cpoly(R.Ns(stripe((74.2, 19.6), (65.0, 36.0), 0.9)), pal['deep'])
    c.cpoly(R.Ns(stripe((57.5, 24.5), (69.5, 13.8), 4.2)), pal['light'])        # otot leher
    # kepala: pipi (masseter), garis wajah, rahang
    c.cpoly(R.Hs(ellp(79.0, 16.8, 3.3, 4.4, 30)), pal['light'])
    c.cpoly(R.Hs(stripe((79.8, 9.6), (89.8, 21.2), 1.3)), pal['light'])
    c.cpoly(R.Hs([(77.2, 18.6), (79.6, 21.3), (83.2, 23.6), (86.4, 25.6), (88.6, 26.4), (89.6, 25.0), (86, 23), (82.5, 20.6), (79.5, 18)]), pal['shade'])
    c.cpoly(R.Hs(ellp(89.0, 22.8, 2.6, 3.2, 30)), pal['muzzle'])
    c.cpoly(R.Hs(ellp(89.4, 21.5, 1.2, 1.5, 30)), pal['muzzle_hi'])
    c.cpoly(R.Hs(stripe((76.4, 9.4), (80.8, 11.2), 1.1)), pal['shade'])         # alis
    out = c.out()
    ex, ey = R.Hd(EYE)
    ex, ey = int(round(ex)), int(round(ey))
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        put(out, spec, ex + dx, ey + dy, pal['eye'])
    put(out, spec, ex + 1, ey, H('ffffff') if pal['eye'][0] < 100 else H('202020'))
    dk = mix(pal['base'], pal['deep'], 0.6)
    put(out, spec, ex - 1, ey, dk); put(out, spec, ex - 1, ey - 1, dk); put(out, spec, ex, ey - 1, dk)
    nx, ny = R.Hd((90.0, 21.2)); put(out, spec, round(nx), round(ny), pal['deep'])
    mx, my = R.Hd((88.4, 25.0)); put(out, spec, round(mx), round(my), pal['deep'])
    mx2, my2 = R.Hd((87.4, 25.0)); put(out, spec, round(mx2), round(my2), pal['shade'])
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
    wd = [5.2, 6.0, 6.0, 5.4, 4.4, 3.0, 1.4]
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
    front = g['front']
    hip, K, F, th = leg_geom(p, key)
    c = Cv(spec)
    coat, sh, li, lowc = pal['base'], pal['shade'], pal['light'], pal['low']
    if front:
        w0, w1, wc0, wc1 = 5.6, 3.9, 3.0, 3.3
    else:
        w0, w1, wc0, wc1 = 6.6, 4.2, 3.0, 3.4
    # lengan atas / gaskin
    c.cap(hip, K, w0, w1, sh)
    c.cap((hip[0] - 0.5, hip[1]), (K[0] - 0.4, K[1]), w0 * 0.78, w1 * 0.8, coat)
    if not g['far']:
        c.ccap((hip[0] + 1.2, hip[1]), (K[0] + 0.9, K[1]), w0 * 0.30, w1 * 0.36, sh)
    # sendi: lutut kotak (depan) / hock runcing (belakang)
    u = norm((hip[0] - K[0], hip[1] - K[1])); v = norm((F[0] - K[0], F[1] - K[1]))
    bis = norm((u[0] + v[0], u[1] + v[1])) if math.hypot(u[0] + v[0], u[1] + v[1]) > 0.2 else (-1, 0)
    if front:
        kc = lowc if pal0['sock'] else coat
        c.poly(ellp(K[0], K[1], 2.5, 2.5, 22, 8), kc)
        c.poly([(K[0] - bis[0] * 2.4 - 1.0, K[1] - bis[1] * 2.4 - 1.0), (K[0] - bis[0] * 2.4 + 1.0, K[1] - bis[1] * 2.4 + 1.0),
                (K[0], K[1])], kc)
    else:
        c.poly(ellp(K[0], K[1], 2.5, 2.6, 0, 12), coat)
        tip = (K[0] - bis[0] * 3.7, K[1] - bis[1] * 3.7)
        pp = (-bis[1], bis[0])
        c.poly([(K[0] + pp[0] * 1.7, K[1] + pp[1] * 1.7), tip, (K[0] - pp[0] * 1.7, K[1] - pp[1] * 1.7)], coat)
    # tulang kering
    c.cap(K, F, wc0, wc1, lowc)
    if not g['far'] and not pal0['sock']:
        c.ccap((K[0] - 0.6, K[1] + 0.5), (F[0] - 0.5, F[1] - 0.5), 1.0, 1.0, mix(lowc, (255, 255, 255, 255), 0.12))
    # fetlock (lebih tebal dari tulang), pastern, teracak segitiga
    def Lp(px, py):
        return rot((F[0] + px, F[1] + py), F, th)
    c.poly(ellp(F[0], F[1], 2.3, 2.3, 0, 12), lowc)
    c.cap(Lp(0, 0.2), Lp(1.0, 2.7), 3.3, 3.0, lowc)
    c.poly([Lp(-1.5, 2.2), Lp(1.5, 2.2), Lp(3.4, 5.0), Lp(-2.3, 5.0)], pal['hoof'])
    c.cpoly([Lp(-1.5, 2.2), Lp(1.5, 2.2), Lp(1.8, 3.1), Lp(-1.6, 3.1)], pal['hoof_hi'])
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
