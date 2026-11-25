"""NPC humanoid rig – gaya sama dengan kusir (24x34, outline berwarna, shading 3 tingkat), tapi berdiri & bergerak.
Menghadap KANAN. Frame 48x48, tanah di y=45, pusat x=24.  Render 4x (center-sampling) => gerak sub-pixel halus.
"""
import math
import numpy as np
from PIL import Image
from horse3 import Cv, ellp, capp, rot, chaikin, smooth
from pxlib import H, mix, darker, outline, comp, new, sheet

FW = FH = 56
GY = 52.0
CX = 28.0
SPEC = (FW, FH, 0, 0)


def shade(c, n=1):
    return mix(c, (30, 18, 36), 0.22 * n)


def light(c, n=1):
    return mix(c, (255, 250, 235), 0.20 * n)


def put1(img, x, y, c):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), c)


DEFAULT = dict(
    hf=1.0, wf=1.0, hs=1.0, skin=H('f0b98d'), hair='short', hair_c=H('6a4528'), beard=None, stache=False,
    top='tunic', top_c=H('5b86c7'), trim_c=None, sleeve_c=None, sleeve='full', belt_c=H('4a3020'),
    apron_c=None, pants_c=H('7b6349'), boots_c=H('4b2f20'), hat=None, hat_c=H('8f5d36'), cape_c=None,
    glasses=False, blush=False, armor=False, tabard_c=None, emblem_c=None, bare_feet=False, sack=False,
    pouch=False, quiver=False, scarf_c=None, slim_legs=True, bulk=0.0,
)


class Npc:
    def __init__(self, name, **kw):
        self.name = name
        self.__dict__.update(DEFAULT)
        self.__dict__.update(kw)
        if self.sleeve_c is None:
            self.sleeve_c = self.top_c
        # proporsi
        self.thigh = 7.0 * self.hf
        self.shin = 7.2 * self.hf
        self.torso = 10.6 * (0.5 + 0.5 * self.hf)
        self.upper = 5.2 * (0.55 + 0.45 * self.hf)
        self.fore = 5.2 * (0.55 + 0.45 * self.hf)
        self.headr = 4.9 * self.hs
        self.ankle_h = 1.8
        self.hip_h = self.ankle_h + 0.985 * (self.thigh + self.shin)
        self.tw = 3.9 * self.wf + self.bulk * 0.5        # setengah tebal torso depan-belakang (sisi hadap)


# ----------------------------------------------------------------------------- IK
def ik2(p0, p1, l1, l2, bend_pref):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    dist = math.hypot(dx, dy) or 1e-6
    d = max(min(dist, l1 + l2 - 0.02), abs(l1 - l2) + 0.02)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(l1 * l1 - a * a, 0))
    ux, uy = dx / dist, dy / dist
    mx, my = p0[0] + ux * a, p0[1] + uy * a
    k1 = (mx - uy * h, my + ux * h); k2 = (mx + uy * h, my - ux * h)
    s1 = bend_pref[0] * k1[0] + bend_pref[1] * k1[1]
    s2 = bend_pref[0] * k2[0] + bend_pref[1] * k2[1]
    return k1 if s1 > s2 else k2


def unit(v):
    l = math.hypot(*v) or 1e-6
    return (v[0] / l, v[1] / l)


class Skel:
    """Hitung semua sendi dari pose."""
    def __init__(self, n, p):
        self.n, self.p = n, p
        lean = math.radians(p.get('lean', 0.0))
        self.H = (CX + p.get('dx', 0.0), GY - n.hip_h + p.get('dy', 0.0))
        self.u = (math.sin(lean), -math.cos(lean))              # arah torso (ke atas)
        self.f = (math.cos(lean), math.sin(lean))               # arah depan (tegak lurus)
        self.S = (self.H[0] + self.u[0] * n.torso, self.H[1] + self.u[1] * n.torso)
        self.N = (self.S[0] + self.u[0] * 1.2, self.S[1] + self.u[1] * 1.2)
        tilt = p.get('head', 0.0)
        hu = rot((self.u[0], self.u[1]), (0, 0), tilt)
        self.hu = hu
        self.C = (self.N[0] + hu[0] * (n.headr * 0.85), self.N[1] + hu[1] * (n.headr * 0.85))
        self.tilt = tilt
        # kaki
        self.leg = {}
        for key in ('N', 'F'):
            fx, fy, fa = p['f' + key]
            A = (CX + fx, GY - n.ankle_h - fy)
            hip = (self.H[0] + (0.6 if key == 'N' else -0.6) * self.f[0], self.H[1] + (0.6 if key == 'N' else -0.6) * self.f[1])
            K = ik2(hip, A, n.thigh, n.shin, (1.0, 0.1))
            self.leg[key] = (hip, K, A, fa)
        # lengan
        self.arm = {}
        sh = {'N': (self.S[0] - self.u[0] * 0.8 + self.f[0] * 0.3, self.S[1] - self.u[1] * 0.8 + self.f[1] * 0.3),
              'F': (self.S[0] - self.u[0] * 0.8 - self.f[0] * 0.3, self.S[1] - self.u[1] * 0.8 - self.f[1] * 0.3)}
        tool = p.get('tool')
        self.tool_tf = None
        self.tool_hand = 'N'
        targets = {'N': None, 'F': None}
        if tool:
            nm, gx, gy, phi, two = tool[:5]
            hand = tool[5] if len(tool) > 5 else 'N'
            other = 'F' if hand == 'N' else 'N'
            self.tool_hand = hand
            G = (sh[hand][0] + gx, sh[hand][1] + gy)
            targets[hand] = G
            ph = math.radians(phi)
            self.tool_tf = (G, phi)
            if two:
                targets[other] = (G[0] + two * math.cos(ph), G[1] + two * math.sin(ph))
        for key in ('N', 'F'):
            if p.get('h' + key) is not None:
                hx, hy = p['h' + key]
                targets[key] = (sh[key][0] + hx, sh[key][1] + hy)
        for key in ('N', 'F'):
            s = sh[key]
            if targets[key] is not None:
                W_ = targets[key]
                E = ik2(s, W_, n.upper, n.fore, (-0.35, 1.0))
            else:
                a1, e1 = p.get('arm' + key, (4.0, 8.0))
                a1r = math.radians(a1); a2r = math.radians(a1 + e1)
                E = (s[0] + math.sin(a1r) * n.upper, s[1] + math.cos(a1r) * n.upper)
                W_ = (E[0] + math.sin(a2r) * n.fore, E[1] + math.cos(a2r) * n.fore)
            self.arm[key] = (s, E, W_)


# ----------------------------------------------------------------------------- partes
def draw_leg(c, n, key, sk, far):
    hip, K, A, fa = sk.leg[key]
    pc = shade(n.pants_c, 1.2) if far else n.pants_c
    bc = shade(n.boots_c, 1.2) if far else n.boots_c
    wf = n.wf
    c.cap(hip, K, 4.4 * wf, 3.6 * wf, pc)
    c.cap(K, A, 3.6 * wf, 3.0 * wf, pc)
    if not far:
        c.ccap((hip[0] + 0.7, hip[1] + 0.4), (K[0] + 0.5, K[1]), 1.0, 1.0, light(pc, 0.8))
    # sepatu / boots
    sd = unit((A[0] - K[0], A[1] - K[1]))
    top = (A[0] - sd[0] * 1.6, A[1] - sd[1] * 1.6)
    if n.bare_feet:
        bc = shade(n.skin, 1.0) if far else n.skin
    c.cap(top, A, 3.4 * wf, 3.0 * wf, bc)
    pts = [(-1.9, -1.2), (1.6, -1.3), (4.4, 0.4), (4.5, 1.9), (-2.0, 1.9)]
    pts = [rot((A[0] + x, A[1] + y), A, fa) for x, y in pts]
    c.poly(pts, bc)
    if not n.bare_feet:
        c.cpoly([rot((A[0] - 2.0, A[1] + 1.2), A, fa), rot((A[0] + 4.5, A[1] + 1.2), A, fa), rot((A[0] + 4.5, A[1] + 1.9), A, fa), rot((A[0] - 2.0, A[1] + 1.9), A, fa)], shade(bc, 1.2))


def draw_arm(c, n, key, sk, far):
    s, E, Wr = sk.arm[key]
    sc = shade(n.sleeve_c, 1.2) if far else n.sleeve_c
    skin = shade(n.skin, 1.0) if far else n.skin
    wf = n.wf
    c.cap(s, E, 3.4 * wf, 3.0 * wf, sc)
    fc = sc if n.sleeve == 'full' else skin
    c.cap(E, Wr, 3.0 * wf, 2.5 * wf, fc)
    if n.sleeve == 'full' and n.trim_c and not far:
        d = unit((Wr[0] - E[0], Wr[1] - E[1]))
        c.cap((Wr[0] - d[0] * 1.2, Wr[1] - d[1] * 1.2), Wr, 2.9 * wf, 2.9 * wf, n.trim_c, rnd=False)
    d = unit((Wr[0] - E[0], Wr[1] - E[1]))
    hc = (Wr[0] + d[0] * 1.0, Wr[1] + d[1] * 1.0)
    c.poly(ellp(hc[0], hc[1], 1.55, 1.55, 0, 10), skin)
    if not far:
        c.cpoly(ellp(hc[0] - 0.3, hc[1] - 0.3, 0.7, 0.7, 0, 8), light(skin, 0.8))
    return hc


def torso_pts(n, sk):
    u, f, Hh, S = sk.u, sk.f, sk.H, sk.S
    tw = n.tw
    P = lambda base, a, b: (base[0] + f[0] * a + u[0] * b, base[1] + f[1] * a + u[1] * b)
    return {
        'sb': P(S, -tw * 0.95, 0.3), 'sf': P(S, tw * 1.05, 0.3),
        'cf': P(S, tw * 1.25 + n.bulk * 0.4, -2.6), 'wf': P(Hh, tw * 1.1 + n.bulk * 0.8, 3.2),
        'hf': P(Hh, tw * 1.1 + n.bulk * 0.8, -0.2), 'hb': P(Hh, -tw * 1.0 - n.bulk * 0.3, -0.2), 'wb': P(Hh, -tw * 0.95, 3.2),
        'cb': P(S, -tw * 1.05, -2.6),
    }


def draw_body(c, n, sk, p):
    T = torso_pts(n, sk)
    f, u, Hh, S = sk.f, sk.u, sk.H, sk.S
    tc = n.top_c
    sway = p.get('sway', 0.0)
    kind = n.top
    # ----- rok / bagian bawah tunik / jubah
    if kind in ('tunic', 'longtunic', 'dress', 'robe', 'armor'):
        hem = {'tunic': 2.6, 'armor': 3.8, 'longtunic': 5.6}.get(kind, None)
        if kind in ('dress', 'robe'):
            hem_y = GY - (3.2 if kind == 'dress' else 2.4) + p.get('dy', 0.0) * 0.3
            fw = 4.0 + 2.2 * (1 if kind == 'robe' else 0.7)
            fb = fw * 0.85
            sk_pts = [T['hb'], T['hf'], (Hh[0] + fw + sway, hem_y), (Hh[0] - fb + sway * 0.6, hem_y)]
        else:
            fw = n.tw * 1.2 + (1.2 if kind == 'longtunic' else 0.6) + n.bulk * 0.8
            sk_pts = [T['hb'], T['hf'], (Hh[0] + fw + sway * 0.4, Hh[1] + hem), (Hh[0] - fw * 0.8 + sway * 0.2, Hh[1] + hem)]
        sk_pts = [(x, y) for x, y in sk_pts]
        c.poly(sk_pts, shade(tc, 0.4))
        c.cpoly([sk_pts[3], sk_pts[2], (sk_pts[2][0], sk_pts[2][1] - 0.9), (sk_pts[3][0], sk_pts[3][1] - 0.9)], shade(tc, 1.4))
        if n.trim_c:
            c.cpoly([(sk_pts[3][0], sk_pts[3][1] - 1.4), (sk_pts[2][0], sk_pts[2][1] - 1.4), (sk_pts[2][0], sk_pts[2][1] - 0.4), (sk_pts[3][0], sk_pts[3][1] - 0.4)], n.trim_c)
    # ----- torso
    order = ['sb', 'sf', 'cf', 'wf', 'hf', 'hb', 'wb', 'cb']
    pts = chaikin([T[k] for k in order], 1)
    base = n.top_c if kind != 'armor' else H('8d93a3')
    c.poly(pts, base)
    # bayangan bawah/belakang dan sorotan atas depan
    c.cpoly([T['wb'], T['wf'], T['hf'], T['hb']], shade(base, 0.7))
    c.cpoly([T['cb'], T['sb'], (T['sb'][0] + f[0] * 1.3, T['sb'][1] + f[1] * 1.3), (T['cb'][0] + f[0] * 1.3, T['cb'][1] + f[1] * 1.3)], shade(base, 0.9))
    hi = [T['sf'], T['cf'], (T['cf'][0] - u[0] * 3.0, T['cf'][1] - u[1] * 3.0), (T['sf'][0] - f[0] * 1.2, T['sf'][1] - f[1] * 1.2)]
    c.cpoly(hi, light(base, 0.9))
    if kind == 'armor':
        # tabard
        if n.tabard_c:
            tb = [(T['sf'][0] - f[0] * 0.2, T['sf'][1]), (T['sb'][0] + f[0] * 1.2, T['sb'][1]),
                  (Hh[0] - f[0] * 2.4 + sway * 0.2, Hh[1] + 6.6), (Hh[0] + f[0] * 3.7 + sway * 0.4, Hh[1] + 6.6)]
            c.poly(tb, n.tabard_c)
            c.cpoly([tb[0], tb[1], (tb[1][0], tb[1][1] + 2), (tb[0][0], tb[0][1] + 2)], light(n.tabard_c, 0.8))
            if n.emblem_c:
                mid = ((tb[0][0] + tb[1][0]) / 2 + 0.2, (tb[0][1] + tb[3][1]) / 2 - 0.5)
                c.poly(ellp(mid[0], mid[1], 1.5, 1.8, 0, 8), n.emblem_c)
    # apron
    if n.apron_c:
        ap = [(T['sf'][0] - f[0] * 0.4, T['sf'][1] + 1.0), (T['sf'][0] + f[0] * 1.0, T['sf'][1] + 1.4), (Hh[0] + f[0] * (n.tw * 1.3 + 1.0), Hh[1] + 5.8),
              (Hh[0] - f[0] * 0.8, Hh[1] + 5.8)]
        if kind in ('dress', 'robe'):
            ap = [(T['sf'][0] - f[0] * 0.4, T['sf'][1] + 1.0), (T['sf'][0] + f[0] * 1.0, T['sf'][1] + 1.4), (Hh[0] + f[0] * 5.0 + sway, GY - 5.5),
                  (Hh[0] - f[0] * 0.8 + sway * 0.6, GY - 5.5)]
        c.poly(ap, n.apron_c)
        c.cpoly([ap[0], ap[1], (ap[1][0], ap[1][1] + 1.2), (ap[0][0], ap[0][1] + 1.2)], light(n.apron_c, 0.7))
        c.cpoly([ap[3], ap[2], (ap[2][0], ap[2][1] - 0.9), (ap[3][0], ap[3][1] - 0.9)], shade(n.apron_c, 0.9))
    # sabuk
    if n.belt_c and kind != 'robe_nobelt':
        b0 = (T['wb'][0] - u[0] * 0.2, T['wb'][1] - u[1] * 0.2)
        b1 = (T['wf'][0] + f[0] * 0.3 - u[0] * 0.2, T['wf'][1] + f[1] * 0.3 - u[1] * 0.2)
        c.cap(b0, b1, 1.5, 1.5, n.belt_c, rnd=False)
    # leher + kerah
    if n.trim_c:
        cl = [T['sb'], T['sf'], (T['sf'][0] - u[0] * 1.1 + f[0] * 0.2, T['sf'][1] - u[1] * 1.1), (T['sb'][0] - u[0] * 1.0, T['sb'][1] - u[1] * 1.0)]
        c.poly(cl, n.trim_c)
    c.cap(sk.S, (sk.N[0] + sk.hu[0] * 1.0, sk.N[1] + sk.hu[1] * 1.0), 3.0, 2.8, shade(n.skin, 0.8))


def HPt(sk, x, y):
    return rot((sk.C[0] + x, sk.C[1] + y), sk.C, sk.tilt)


def HPs(sk, pts):
    return [HPt(sk, x, y) for x, y in pts]


def draw_hair_back(c, n, sk):
    hc = n.hair_c
    r = n.headr / 4.9
    if n.hair in ('long', 'braid', 'bunlong'):
        L = 8.5 if n.hair != 'braid' else 9.5
        pts = HPs(sk, [(-4.2 * r, -3.0 * r), (-4.6 * r, 1.0 * r), (-4.8 * r, L * r), (-1.8 * r, L * r), (-1.0 * r, 2.0 * r)])
        if n.hair == 'braid':
            pts = HPs(sk, [(-4.2 * r, -3.0 * r), (-4.6 * r, 1.0 * r), (-5.4 * r, 4.0 * r), (-3.0 * r, 4.0 * r), (-1.0 * r, 2.0 * r)])
        c.poly(pts, hc)
        c.cpoly(HPs(sk, [(-4.4 * r, 0), (-4.8 * r, L * r * 0.9), (-3.8 * r, L * r * 0.9), (-3.4 * r, 0)]), shade(hc, 1.2))
        if n.hair == 'braid':
            p0 = HPt(sk, -4.6 * r, 3.4 * r); p1 = (p0[0] - 1.0, p0[1] + 4.5); p2 = (p1[0] + 0.8, p1[1] + 4.5)
            c.cap(p0, p1, 2.4, 2.2, hc); c.cap(p1, p2, 2.2, 1.6, shade(hc, 0.6))
            c.poly(ellp(p2[0], p2[1] + 0.8, 1.0, 1.0, 0, 8), n.trim_c or H('c8433a'))
    if n.hat in ('hood', 'monkhood'):
        pts = HPs(sk, [(-5.2 * r, -4.2 * r), (-6.2 * r, 3.0 * r), (-4.0 * r, 7.0 * r), (-0.5 * r, 5.5 * r), (0, -2 * r)])
        c.poly(pts, n.hat_c)
        c.cpoly(HPs(sk, [(-5.6 * r, 3 * r), (-4.0 * r, 7.0 * r), (-2.0 * r, 6.5 * r), (-3.5 * r, 2 * r)]), shade(n.hat_c, 1.2))


def draw_cape(c, n, sk, p):
    if not n.cape_c:
        return
    sw = p.get('sway', 0.0)
    T = torso_pts(n, sk)
    L = 15
    pts = [(T['sb'][0] + 0.8, T['sb'][1] - 0.6), (T['sf'][0] - 1.0, T['sf'][1] - 0.2),
           (T['hb'][0] - 2.2 + sw * 1.4, T['hb'][1] + L), (T['hb'][0] - 5.0 + sw * 2.0, T['hb'][1] + L - 0.5)]
    c.poly(chaikin(pts, 1), n.cape_c)
    c.cpoly([pts[3], pts[2], (pts[2][0], pts[2][1] - 1.1), (pts[3][0], pts[3][1] - 1.1)], shade(n.cape_c, 1.2))
    c.cpoly([pts[0], (pts[0][0] - 3.2, pts[0][1] + 8), (pts[3][0] + 1.5, pts[3][1] - 6), pts[3]], shade(n.cape_c, 0.9))


def draw_head(c, n, sk, p):
    r = n.headr / 4.9
    skin = n.skin
    C = sk.C
    # kepala
    c.poly(HPs(sk, ellp(0, 0, 4.2 * r, 4.5 * r, 0, 22)), skin)
    c.poly(HPs(sk, [(-1, 2.0 * r), (3.6 * r, 2.6 * r), (3.0 * r, 4.4 * r), (-0.8, 4.6 * r)]), skin)
    c.cpoly(HPs(sk, [(-4.4 * r, 0.6 * r), (-1.2 * r, 0.6 * r), (-0.5 * r, 4.8 * r), (-4.4 * r, 4.8 * r)]), shade(skin, 0.7))   # bayangan belakang
    c.cpoly(HPs(sk, ellp(1.6 * r, 1.5 * r, 1.4 * r, 1.0 * r)), light(skin, 0.7))
    c.poly(HPs(sk, ellp(4.2 * r, 0.9 * r, 0.9 * r, 0.8 * r, 0, 8)), skin)        # hidung
    # jenggot
    if n.beard:
        bc = n.hair_c
        if n.beard == 'long':
            pts = HPs(sk, [(0.6 * r, 1.6 * r), (3.9 * r, 2.3 * r), (3.5 * r, 5.2 * r), (1.6 * r, 8.6 * r), (-1.0 * r, 6.0 * r), (-2.0 * r, 2.4 * r)])
        else:
            pts = HPs(sk, [(0.4 * r, 2.0 * r), (3.8 * r, 2.6 * r), (3.4 * r, 4.6 * r), (1.4 * r, 5.6 * r), (-1.2 * r, 4.8 * r), (-2.0 * r, 2.4 * r)])
        c.poly(pts, bc)
        c.cpoly(HPs(sk, [(0.4 * r, 2.0 * r), (3.8 * r, 2.6 * r), (3.2 * r, 3.2 * r), (0.4 * r, 3.0 * r)]), light(bc, 0.8))
        c.cpoly(HPs(sk, [(-1.0 * r, 5 * r), (2.0 * r, 5.2 * r), (1.0 * r, 7.0 * r), (-1.0 * r, 6.0 * r)]), shade(bc, 0.8))
    if n.stache:
        c.poly(HPs(sk, [(1.2 * r, 1.9 * r), (4.6 * r, 2.0 * r), (4.2 * r, 3.2 * r), (1.6 * r, 3.1 * r)]), n.hair_c)
    # rambut depan
    hc = n.hair_c
    st = n.hair
    cap = HPs(sk, [(-4.6 * r, 0.8 * r), (-4.5 * r, -2.6 * r), (-2.8 * r, -4.7 * r), (0.6 * r, -5.0 * r), (3.2 * r, -4.0 * r), (4.0 * r, -2.2 * r),
                   (2.8 * r, -2.6 * r), (1.0 * r, -2.2 * r), (-0.8 * r, -1.2 * r), (-1.6 * r, 0.8 * r)])
    if st in ('short', 'long', 'braid', 'bun', 'bunlong', 'curly'):
        c.poly(cap, hc)
        c.cpoly(HPs(sk, [(-3.0 * r, -4.6 * r), (0.4 * r, -4.9 * r), (2.5 * r, -4.0 * r), (0.0, -3.4 * r), (-2.4 * r, -3.2 * r)]), light(hc, 1.2))
        if st in ('bun', 'bunlong'):
            c.poly(HPs(sk, ellp(-3.8 * r, -4.2 * r, 2.0 * r, 1.9 * r, 0, 10)), hc)
            c.cpoly(HPs(sk, ellp(-4.1 * r, -4.6 * r, 0.9 * r, 0.7 * r, 0, 8)), light(hc, 1.2))
        if st == 'curly':
            for (hx, hy) in [(-3.5, -3.5), (-1.0, -5.0), (1.8, -4.6), (3.6, -3.0)]:
                c.poly(HPs(sk, ellp(hx * r, hy * r, 1.5 * r, 1.4 * r, 0, 8)), hc)
    elif st == 'tonsure':
        c.poly(HPs(sk, [(-4.6 * r, 1.4 * r), (-4.4 * r, -1.6 * r), (-2.2 * r, -1.2 * r), (-1.0 * r, 0.4 * r), (-2.0 * r, 2.4 * r)]), hc)
    elif st == 'bald':
        pass
    elif st == 'sidebald':
        c.poly(HPs(sk, [(-4.6 * r, 1.6 * r), (-4.5 * r, -1.0 * r), (-2.8 * r, -0.4 * r), (-1.6 * r, 1.4 * r)]), hc)
    # topi / penutup kepala
    ht = n.hat
    hcn = n.hat_c
    if ht == 'straw':
        c.poly(HPs(sk, ellp(0.3 * r, -3.6 * r, 7.4 * r, 1.5 * r, -4, 18)), hcn)
        c.poly(HPs(sk, chaikin([(-3.6 * r, -3.4 * r), (-2.6 * r, -6.8 * r), (2.0 * r, -6.8 * r), (3.2 * r, -3.4 * r)], 1)), hcn)
        c.cpoly(HPs(sk, ellp(0.3 * r, -3.0 * r, 7.0 * r, 0.9 * r, -4, 16)), shade(hcn, 1.1))
        c.cpoly(HPs(sk, [(-3.4 * r, -4.4 * r), (3.0 * r, -4.4 * r), (3.2 * r, -3.4 * r), (-3.6 * r, -3.4 * r)]), n.trim_c or H('c8433a'))
        c.cpoly(HPs(sk, [(-2.4 * r, -6.6 * r), (1.6 * r, -6.6 * r), (1.2 * r, -5.2 * r), (-2.8 * r, -5.2 * r)]), light(hcn, 1.0))
    elif ht == 'cap':
        c.poly(HPs(sk, chaikin([(-4.7 * r, -0.6 * r), (-4.4 * r, -3.6 * r), (-1.8 * r, -5.6 * r), (2.4 * r, -5.2 * r), (4.4 * r, -3.0 * r), (3.0 * r, -2.4 * r), (-1.0 * r, -2.2 * r)], 1)), hcn)
        c.cpoly(HPs(sk, [(-1.0 * r, -5.4 * r), (2.4 * r, -5.0 * r), (3.6 * r, -3.2 * r), (0, -3.4 * r)]), light(hcn, 1.0))
        c.cpoly(HPs(sk, [(-4.7 * r, -2.2 * r), (4.4 * r, -2.6 * r), (4.4 * r, -2.0 * r), (-4.7 * r, -1.4 * r)]), shade(hcn, 1.2))
    elif ht == 'coif':
        c.poly(HPs(sk, chaikin([(-4.8 * r, 2.4 * r), (-5.0 * r, -2.6 * r), (-2.4 * r, -5.2 * r), (1.6 * r, -5.0 * r), (3.4 * r, -3.2 * r), (1.2 * r, -1.6 * r), (-1.2 * r, 0.8 * r), (-1.4 * r, 3.6 * r)], 1)), hcn)
        c.cpoly(HPs(sk, [(-1.4 * r, -5.0 * r), (1.6 * r, -4.8 * r), (2.8 * r, -3.4 * r), (-0.4 * r, -3.2 * r)]), light(hcn, 0.8))
    elif ht == 'headscarf':
        c.poly(HPs(sk, chaikin([(-4.8 * r, 1.4 * r), (-4.9 * r, -2.8 * r), (-2.4 * r, -5.3 * r), (1.8 * r, -5.2 * r), (4.0 * r, -3.2 * r), (4.4 * r, -1.8 * r), (0.8 * r, -2.0 * r), (-1.4 * r, 0.6 * r)], 1)), hcn)
        c.poly(HPs(sk, [(-4.6 * r, -0.4 * r), (-7.4 * r, 3.0 * r), (-6.6 * r, 5.4 * r), (-4.0 * r, 2.6 * r)]), shade(hcn, 0.7))
        c.cpoly(HPs(sk, [(-2.4 * r, -5.1 * r), (1.8 * r, -5.0 * r), (3.0 * r, -3.8 * r), (-1.0 * r, -3.8 * r)]), light(hcn, 1.0))
    elif ht in ('hood', 'monkhood'):
        c.poly(HPs(sk, chaikin([(-5.2 * r, 2.0 * r), (-5.2 * r, -3.2 * r), (-2.6 * r, -5.8 * r), (1.8 * r, -5.6 * r), (4.2 * r, -3.4 * r), (4.6 * r, -1.2 * r), (1.0 * r, -1.6 * r), (-1.0 * r, 0.8 * r), (-1.2 * r, 3.6 * r)], 1)), hcn)
        c.cpoly(HPs(sk, [(1.2 * r, -5.4 * r), (4.2 * r, -3.2 * r), (4.6 * r, -1.2 * r), (2.4 * r, -1.6 * r)]), shade(hcn, 1.2))
        c.cpoly(HPs(sk, [(-2.4 * r, -5.7 * r), (1.0 * r, -5.5 * r), (2.0 * r, -4.2 * r), (-1.6 * r, -4.4 * r)]), light(hcn, 1.0))
    elif ht == 'helmet':
        iron = H('9aa0b0')
        c.poly(HPs(sk, chaikin([(-5.0 * r, 1.8 * r), (-5.2 * r, -3.4 * r), (-2.4 * r, -6.0 * r), (2.4 * r, -5.8 * r), (4.8 * r, -3.0 * r), (4.6 * r, -1.2 * r), (-0.6 * r, -1.2 * r), (-1.0 * r, 1.4 * r)], 1)), iron)
        c.poly(HPs(sk, [(3.6 * r, -2.6 * r), (4.6 * r, 0.6 * r), (4.0 * r, 2.2 * r), (3.2 * r, 1.0 * r)]), shade(iron, 0.8))    # pelindung hidung
        c.cpoly(HPs(sk, [(-2.4 * r, -5.8 * r), (1.8 * r, -5.6 * r), (3.2 * r, -4.2 * r), (-1.0 * r, -4.0 * r)]), light(iron, 1.2))
        c.cpoly(HPs(sk, [(-5.2 * r, -1.8 * r), (4.8 * r, -2.2 * r), (4.7 * r, -1.2 * r), (-5.2 * r, -0.8 * r)]), shade(iron, 1.1))
        c.poly(HPs(sk, [(-5.0 * r, 1.0 * r), (-1.4 * r, 1.2 * r), (-1.2 * r, 4.4 * r), (-4.6 * r, 5.4 * r)]), H('7d8494'))   # coif kerah mail
    elif ht == 'chef':
        c.poly(HPs(sk, ellp(0, -6.8 * r, 3.8 * r, 3.0 * r, 0, 14)), hcn)
        c.poly(HPs(sk, [(-3.8 * r, -3.2 * r), (3.8 * r, -3.4 * r), (3.6 * r, -5.8 * r), (-3.6 * r, -5.6 * r)]), hcn)
        c.cpoly(HPs(sk, [(-3.8 * r, -4.0 * r), (3.8 * r, -4.2 * r), (3.8 * r, -3.2 * r), (-3.8 * r, -3.0 * r)]), shade(hcn, 0.8))
        c.cpoly(HPs(sk, ellp(-1.0 * r, -7.6 * r, 1.4 * r, 1.0 * r)), light(hcn, 0.6))
    elif ht == 'feather':
        c.poly(HPs(sk, chaikin([(-4.8 * r, -1.0 * r), (-4.4 * r, -4.2 * r), (-1.0 * r, -5.4 * r), (3.0 * r, -4.6 * r), (5.6 * r, -2.4 * r), (3.6 * r, -2.0 * r), (-1.0 * r, -2.2 * r)], 1)), hcn)
        c.cpoly(HPs(sk, [(-4.8 * r, -2.6 * r), (4.8 * r, -2.6 * r), (5.6 * r, -2.4 * r), (-4.8 * r, -1.6 * r)]), shade(hcn, 1.2))
        fe = n.trim_c or H('e8d8a0')
        c.poly(HPs(sk, chaikin([(-3.4 * r, -4.0 * r), (-7.6 * r, -8.0 * r), (-5.6 * r, -9.4 * r), (-1.6 * r, -5.0 * r)], 1)), fe)
    elif ht == 'crown':
        gold = H('f0c455')
        c.poly(HPs(sk, [(-3.6 * r, -3.6 * r), (-3.2 * r, -6.8 * r), (-1.6 * r, -5.0 * r), (0, -7.4 * r), (1.6 * r, -5.0 * r), (3.2 * r, -6.8 * r), (3.6 * r, -3.6 * r)]), gold)
        c.cpoly(HPs(sk, [(-3.6 * r, -4.4 * r), (3.6 * r, -4.4 * r), (3.6 * r, -3.6 * r), (-3.6 * r, -3.6 * r)]), shade(gold, 1.2))
        c.poly(HPs(sk, ellp(0, -4.9 * r, 0.8 * r, 0.8 * r, 0, 6)), H('d9453d'))
    elif ht == 'scholar':
        c.poly(HPs(sk, chaikin([(-4.6 * r, -1.2 * r), (-4.3 * r, -4.2 * r), (0, -5.6 * r), (4.4 * r, -4.0 * r), (4.8 * r, -2.4 * r), (-1.0 * r, -2.0 * r)], 1)), hcn)
        c.cpoly(HPs(sk, [(-1.4 * r, -5.4 * r), (3.2 * r, -4.2 * r), (0, -3.6 * r)]), light(hcn, 1.0))
    elif ht == 'bandana':
        c.poly(HPs(sk, chaikin([(-4.8 * r, -0.2 * r), (-4.7 * r, -3.4 * r), (-2.0 * r, -5.4 * r), (2.4 * r, -5.2 * r), (4.4 * r, -3.0 * r), (4.4 * r, -1.8 * r), (-4.0 * r, -1.0 * r)], 1)), hcn)
    out = None
    return out


def face_details(img, n, sk, p, spec_ox=0, spec_oy=0):
    r = n.headr / 4.9
    blink = p.get('blink', 0)
    eye_c = H('15101a')
    ex, ey = HPt(sk, 2.1 * r, -0.4 * r)
    if blink:
        put1(img, ex, ey + 0.8, eye_c); put1(img, ex + 1, ey + 0.8, shade(n.skin, 2.0))
    else:
        put1(img, ex, ey, eye_c); put1(img, ex, ey + 1, eye_c)
        bx, by = HPt(sk, 1.9 * r, -1.8 * r)
        put1(img, bx, by, shade(n.hair_c if n.hair_c else n.skin, 0.8) if n.hair not in ('bald', 'tonsure') else shade(n.skin, 1.6))
    if n.glasses:
        fc = H('b8a890')
        for dx, dy in ((-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 2), (-1, 2), (1, 2), (-1, 0)):
            put1(img, ex + dx, ey + dy, fc)
        put1(img, ex, ey, eye_c); put1(img, ex, ey + 1, eye_c)
    mx, my = HPt(sk, 3.0 * r, 2.5 * r)
    if p.get('mouth', 0) == 1:
        put1(img, mx, my, H('7a2a2a')); put1(img, mx, my + 1, H('7a2a2a'))
    elif not (n.beard or n.stache):
        put1(img, mx, my, shade(n.skin, 2.2))
    if n.blush:
        kx, ky = HPt(sk, 1.6 * r, 1.8 * r)
        put1(img, kx, ky, H('e48a80'))
    ox, oy = HPt(sk, -1.2 * r, 0.8 * r)
    put1(img, ox, oy, shade(n.skin, 1.4))


# ----------------------------------------------------------------------------- tools
IRON = H('9aa0b0'); IRON_D = H('646a7a'); WOOD = H('9a6a3a'); WOOD_L = H('c18c50'); WOOD_D = H('6a4526')


def tool_shapes(name):
    """grip di (0,0); sumbu +x. return list (pts, color)."""
    if name == 'hoe':
        return [([(-6, -0.7), (17, -0.7), (17, 0.7), (-6, 0.7)], WOOD), ([(16, -1.2), (18.4, -1.0), (21.6, 4.6), (18.4, 4.8), (16.4, 1.6)], IRON)]
    if name == 'shovel':
        return [([(-5, -0.7), (16, -0.7), (16, 0.7), (-5, 0.7)], WOOD), ([(15, -2.0), (21, -2.6), (22, 2.6), (15, 2.0)], IRON)]
    if name == 'sickle':
        return [([(-1, -0.7), (6, -0.7), (6, 0.7), (-1, 0.7)], WOOD), ([(6, -0.8), (10, -2.2), (13.5, -0.4), (14, 2.8), (12.6, 2.2), (11, 0.2), (8.5, -0.6), (6, 0.6)], IRON)]
    if name == 'scythe':
        return [([(-6, -0.7), (20, -0.7), (20, 0.7), (-6, 0.7)], WOOD), ([(19, -0.6), (25, 1.2), (31, 5.0), (30.6, 6.8), (24, 3.6), (19, 1.4)], IRON)]
    if name == 'spear':
        return [([(-20, -0.7), (24, -0.7), (24, 0.7), (-20, 0.7)], WOOD), ([(23, -1.8), (29, 0), (23, 1.8)], IRON), ([(21.5, -1.0), (23.5, -1.0), (23.5, 1.0), (21.5, 1.0)], H('c8433a'))]
    if name == 'sword':
        return [([(-1.5, -0.8), (1.5, -0.8), (1.5, 0.8), (-1.5, 0.8)], WOOD_D), ([(1.5, -2.6), (3.0, -2.6), (3.0, 2.6), (1.5, 2.6)], H('c9a74a')), ([(3, -0.9), (14, -0.9), (16, 0), (14, 0.9), (3, 0.9)], H('c6ccd8'))]
    if name == 'hammer':
        return [([(-2, -0.7), (9, -0.7), (9, 0.7), (-2, 0.7)], WOOD), ([(8, -2.8), (12.2, -2.8), (12.2, 2.6), (8, 2.6)], IRON_D), ([(8, -2.8), (12.2, -2.8), (12.2, -1.8), (8, -1.8)], IRON)]
    if name == 'axe':
        return [([(-3, -0.7), (14, -0.7), (14, 0.7), (-3, 0.7)], WOOD), ([(12, -1.0), (15, -3.0), (16.5, -3.4), (17.4, 3.4), (15, 3.0), (12, 1.0)], IRON)]
    if name == 'broom':
        return [([(-6, -0.6), (15, -0.6), (15, 0.6), (-6, 0.6)], WOOD), ([(14, -2.2), (22, -3.6), (22, 3.6), (14, 2.2)], H('c9a74a')), ([(14, -2.2), (22, -3.6), (22, -2.4), (14, -1.2)], H('e2c470'))]
    if name == 'staff':
        return [([(-12, -0.7), (14, -0.7), (14, 0.7), (-12, 0.7)], WOOD), ([(13.5, -1.8), (16.5, -1.8), (16.5, 1.8), (13.5, 1.8)], H('f0c455'))]
    if name == 'bow':
        return [(chaikin([(0.6, -9.5), (3.0, -6.0), (4.4, 0), (3.0, 6.0), (0.6, 9.5), (1.4, 6.0), (2.6, 0), (1.4, -6.0)], 2), WOOD), ([(0.6, -1.4), (3.4, -1.4), (3.4, 1.4), (0.6, 1.4)], WOOD_D)]
    if name == 'book':
        return [([(-1, -2.6), (4.6, -2.6), (4.6, 2.6), (-1, 2.6)], H('7a3a2a')), ([(-0.4, -2.0), (4.0, -2.0), (4.0, 2.0), (-0.4, 2.0)], H('efe4c4')), ([(-1, 2.0), (4.6, 2.0), (4.6, 2.6), (-1, 2.6)], H('5a2a1e'))]
    if name == 'basket':
        return [([(0, -1.6), (7, -1.6), (7.6, 4.6), (-0.6, 4.6)], H('b98a4a')), ([(0, -1.6), (7, -1.6), (7, -0.6), (0, -0.6)], H('e2c470')), ([(0.4, 1.6), (7, 1.6), (7, 2.4), (0.4, 2.4)], H('8a6030')),
                ([(1, -3.6), (3, -3.0), (5, -3.8), (6.4, -2.0), (1.4, -1.6)], H('d9453d'))]
    if name == 'bucket':
        return [([(0, 0), (6, 0), (5.2, 5.6), (0.8, 5.6)], WOOD), ([(0, 1.2), (6, 1.2), (5.9, 2.0), (0.1, 2.0)], IRON_D), ([(0.4, 0), (5.6, 0), (5.6, 0.9), (0.4, 0.9)], H('3a6a8a'))]
    if name == 'sack':
        return [([(0, -3.4), (8, -3.4), (9.4, 3.4), (8, 5.6), (0, 5.6), (-1.2, 3.4)], H('c9a468')), ([(0, -3.4), (8, -3.4), (7.4, -2.4), (0.6, -2.4)], H('9c7a45')), ([(2, -4.4), (6, -4.4), (6, -3.4), (2, -3.4)], H('9c7a45'))]
    if name == 'log':
        return [([(-6, -2.2), (7, -2.2), (7, 2.2), (-6, 2.2)], H('8a5a30')), ([(6, -2.2), (8.2, -1.6), (8.2, 1.6), (6, 2.2)], H('e2c490')), ([(-6, -0.8), (7, -0.8), (7, -0.2), (-6, -0.2)], H('6a4526'))]
    if name == 'tray':
        return [([(-3, 0), (9, 0), (9, 1.0), (-3, 1.0)], WOOD_L), ([(-1, -2.6), (2.6, -2.6), (3, 0), (-1.4, 0)], H('d9a050')), ([(3.2, -2.2), (6.6, -2.4), (7, 0), (3.4, 0)], H('c8893a'))]
    if name == 'coins':
        return [([(-1.2, -1.0), (1.8, -1.0), (1.8, 1.0), (-1.2, 1.0)], H('f0c455'))]
    if name == 'arrow':
        return [([(-6, -0.4), (6, -0.4), (6, 0.4), (-6, 0.4)], H('e8e0c8')), ([(6, -1.2), (8.6, 0), (6, 1.2)], IRON), ([(-6, -1.4), (-3.5, -0.4), (-6, 0)], H('d9453d'))]
    if name == 'seedbag':
        return [([(0, 0), (3.6, 0), (4.2, 4.4), (-0.6, 4.4)], H('c9a468'))]
    return []


def draw_tool(c, name, G, phi, flip=False):
    for pts, col in tool_shapes(name):
        P = [rot((G[0] + x, G[1] + y), G, phi) for x, y in pts]
        c.poly(P, col)


# ----------------------------------------------------------------------------- aksesoris
def draw_back_items(c, n, sk, p):
    T = torso_pts(n, sk)
    f, u = sk.f, sk.u
    if n.sack:
        b = (T['hb'][0] - 3.0, T['hb'][1] - 4.0)
        c.poly(chaikin([(b[0], b[1] - 2.0), (b[0] + 4.0, b[1] - 1.0), (b[0] + 4.6, b[1] + 5.0), (b[0] - 0.6, b[1] + 6.0), (b[0] - 3.2, b[1] + 2.0)], 1), H('c9a468'))
        c.cpoly([(b[0] - 3.2, b[1] + 2.0), (b[0] - 0.6, b[1] + 6.0), (b[0] + 4.6, b[1] + 5.0), (b[0] + 1, b[1] + 1)], H('9c7a45'))
    if n.quiver:
        q0 = (T['sb'][0] - 1.0, T['sb'][1] - 1.0); q1 = (T['hb'][0] - 3.0, T['hb'][1] + 3.0)
        c.cap(q0, q1, 3.0, 3.0, H('7a4a2a'))
        c.cap((q0[0] - 0.8, q0[1] - 0.4), (q0[0] - 2.4, q0[1] - 3.6), 1.0, 1.0, H('e8e0c8'))
        c.cap((q0[0] + 0.6, q0[1] - 0.4), (q0[0] + 0.0, q0[1] - 4.0), 1.0, 1.0, H('e8e0c8'))
        c.poly(ellp(q0[0] - 2.4, q0[1] - 3.8, 0.9, 0.9, 0, 6), H('d9453d')); c.poly(ellp(q0[0], q0[1] - 4.2, 0.9, 0.9, 0, 6), H('d9453d'))


def draw_front_items(c, n, sk, p):
    T = torso_pts(n, sk)
    f, u = sk.f, sk.u
    if n.pouch:
        pc = (T['wf'][0] + f[0] * 0.6, T['wf'][1] + 2.4)
        c.poly(ellp(pc[0], pc[1], 2.0, 2.2, 0, 8), H('7a4a2a'))
        c.cpoly(ellp(pc[0] - 0.4, pc[1] - 0.7, 1.0, 0.8, 0, 6), H('a8743f'))
    if p.get('scabbard'):
        a = (T['wb'][0] - 0.8, T['wb'][1] + 1.2); b = (a[0] - 7.5, a[1] + 4.6)
        c.cap(a, b, 1.8, 1.4, H('5a3a22'))


# ----------------------------------------------------------------------------- render
def render(n, p):
    sk = Skel(n, p)
    groups = []

    def grp(fn, strength=0.6):
        c = Cv(SPEC)
        fn(c)
        im = c.out()
        groups.append((im, strength))
        return im

    # 1 kaki jauh
    grp(lambda c: draw_leg(c, n, 'F', sk, True))
    # 2 barang belakang (jubah, rambut panjang, tudung, karung, tabung panah)
    def back(c):
        draw_cape(c, n, sk, p)
        draw_back_items(c, n, sk, p)
        draw_hair_back(c, n, sk)
        if p.get('tool') and sk.tool_tf and p.get('tool_z') == 'back':
            draw_tool(c, p['tool'][0], sk.tool_tf[0], sk.tool_tf[1])
    grp(back)
    # 3 lengan jauh
    grp(lambda c: draw_arm(c, n, 'F', sk, True))
    # 4 kaki dekat
    grp(lambda c: draw_leg(c, n, 'N', sk, False))
    # 5 badan + kepala
    def body(c):
        draw_body(c, n, sk, p)
        draw_head(c, n, sk, p)
    bi = grp(body)
    face_details(bi, n, sk, p)
    # 6 barang depan (kantong, sarung pedang) + alat
    def front(c):
        draw_front_items(c, n, sk, p)
        if p.get('tool') and sk.tool_tf and p.get('tool_z', 'front') == 'front':
            nm = p['tool'][0]
            G, phi = sk.tool_tf
            draw_tool(c, nm, G, phi)
            hs, he, hw = sk.arm['N']
            d = unit((hw[0] - he[0], hw[1] - he[1]))
            hp = (hw[0] + d[0] * 1.0, hw[1] + d[1] * 1.0)
            if nm == 'bow':
                top = rot((G[0] + 1.4, G[1] - 9.0), G, phi); bot = rot((G[0] + 1.4, G[1] + 9.0), G, phi)
                mid = hp if p.get('draw', 0) > 0.05 else rot((G[0] + 1.6, G[1]), G, phi)
                sc_ = H('efe6cc')
                c.cap(top, mid, 0.9, 0.9, sc_, rnd=False); c.cap(mid, bot, 0.9, 0.9, sc_, rnd=False)
                if p.get('arrow') == 'nocked':
                    tipx = (G[0] + 5.0 * math.cos(math.radians(phi)) + 3, G[1] + 5.0 * math.sin(math.radians(phi)))
                    ang = math.degrees(math.atan2(tipx[1] - hp[1], tipx[0] - hp[0]))
                    ln = math.hypot(tipx[0] - hp[0], tipx[1] - hp[1])
                    draw_tool(c, 'arrow', (hp[0] + ln / 2 - 0.5, hp[1] + (tipx[1] - hp[1]) / 2), ang)
                elif isinstance(p.get('arrow'), tuple):
                    draw_tool(c, 'arrow', (p['arrow'][1], p['arrow'][2]), phi)
    grp(front, 0.55)
    # 7 lengan dekat
    grp(lambda c: draw_arm(c, n, 'N', sk, False))
    # ekstra: alat di belakang tangan dekat tapi di depan badan (mis. tombak)
    out = new(FW, FH)
    for im, st in groups:
        o = outline(im, st)
        out.alpha_composite(o)
        out.alpha_composite(im)
    for fx in p.get('fx', []) or []:
        if fx[0] == 'dot':
            put1(out, fx[1], fx[2], fx[3])
        elif fx[0] == 'rel':
            hs_, he_, hw_ = sk.arm[fx[1]]
            d_ = unit((hw_[0] - he_[0], hw_[1] - he_[1]))
            put1(out, hw_[0] + d_[0] + fx[2], hw_[1] + d_[1] + fx[3], fx[4])
    return out


STAND = dict(fN=(2.0, 0.0, 0.0), fF=(-2.5, 0.0, 0.0), armN=(8.0, 10.0), armF=(-6.0, 8.0))

if __name__ == '__main__':
    farmer = Npc('petani', hf=0.95, skin=H('e9b08a'), hair='short', hair_c=H('6a4528'), top='tunic', top_c=H('a9835a'), trim_c=H('e8d8a0'),
                 pants_c=H('6b5a48'), boots_c=H('4b2f20'), hat='straw', hat_c=H('e2c470'), belt_c=H('4a3020'), stache=True, pouch=True)
    smith = Npc('pandai_besi', hf=0.9, wf=1.25, bulk=1.2, skin=H('d99a74'), hair='bald', hair_c=H('3a2a20'), beard='long', top='tunic', top_c=H('7a7f8e'),
                apron_c=H('5a3a22'), pants_c=H('4a4552'), boots_c=H('2f1c14'), sleeve='rolled')
    guard = Npc('penjaga', hf=1.1, wf=1.1, skin=H('f0b98d'), hair='short', top='armor', top_c=H('8d93a3'), tabard_c=H('3f6fb0'), emblem_c=H('f0c455'),
                hat='helmet', pants_c=H('4a4552'), boots_c=H('3a2a20'), belt_c=H('4a3020'))
    lib = Npc('pustakawan', hf=1.0, skin=H('f0c8a0'), hair='bun', hair_c=H('d8d0c8'), top='robe', top_c=H('3f5f9a'), trim_c=H('f0c455'), glasses=True,
              hat=None, belt_c=H('f0c455'), boots_c=H('3a2a20'), blush=True)
    child = Npc('anak', hf=0.62, hs=1.05, wf=0.85, skin=H('f2c09a'), hair='short', hair_c=H('c9803a'), top='tunic', top_c=H('d9584c'), pants_c=H('6b5a48'), blush=True)
    ims = []
    for nn in (farmer, smith, guard, lib, child):
        ims.append(render(nn, dict(STAND)))
    s = sheet(ims)
    bg = Image.new('RGBA', s.size, (120, 160, 120, 255)); bg.alpha_composite(s)
    bg.resize((bg.width * 8, bg.height * 8), Image.NEAREST).save('/home/claude/work/npc_t1.png')
    print('ok')
