import math
from npc_rig import STAND, smooth

TAU = 2 * math.pi


def sm(x):
    return smooth(x)


def base(**kw):
    p = dict(lean=0.0, dx=0.0, dy=0.0, head=0.0, fN=(2.0, 0.0, 0.0), fF=(-2.5, 0.0, 0.0), armN=(8.0, 10.0), armF=(-6.0, 8.0),
             sway=0.0, blink=0, mouth=0)
    p.update(kw)
    return p


def blink_at(t, centers=(0.62,), w=0.035):
    return 1 if any(abs(((t - c + 0.5) % 1.0) - 0.5) < w for c in centers) else 0


# ------------------------------------------------------------------ interpolasi keyframe periodik
def lerp(a, b, u):
    if a is None or b is None:
        return a if u < 0.5 else b
    if isinstance(a, (int, float)):
        return a + (b - a) * u
    if isinstance(a, tuple):
        if len(a) != len(b):
            return a
        return tuple(lerp(x, y, u) if isinstance(x, (int, float)) and isinstance(y, (int, float)) else x for x, y in zip(a, b))
    return a


def blend(pa, pb, u):
    out = {}
    for k in set(pa) | set(pb):
        a, b = pa.get(k), pb.get(k)
        if k in ('tool',) and (a is None or b is None):
            out[k] = a if (a is not None and u < 0.5) or b is None else b
        else:
            out[k] = lerp(a, b, u) if (a is not None and b is not None) else (a if a is not None else b)
    return out


def kf(t, keys, ease=True):
    """keys: [(t, pose)], t menaik dari 0 ke 1; pose terakhir harus = pose pertama agar loop mulus."""
    t = t % 1.0
    for i in range(len(keys) - 1):
        t0, p0 = keys[i]; t1, p1 = keys[i + 1]
        if t0 <= t <= t1:
            u = (t - t0) / max(t1 - t0, 1e-6)
            return blend(p0, p1, sm(u) if ease else u)
    return dict(keys[-1][1])


# ------------------------------------------------------------------ jalan / lari
def gait_leg(t, off, S, lift, st, nat):
    q = (t - off) % 1.0
    if q < st:
        u = q / st
        x = S - 2 * S * u; y = 0.0
        ang = -10 * sm((u - 0.75) / 0.25)
    else:
        s = (q - st) / (1 - st)
        x = -S + 2 * S * sm(s)
        y = lift * (math.sin(math.pi * s) ** 0.9)
        ang = 30 * math.sin(math.pi * s) - 10 * (1 - sm(min(1, s * 3)))
    return (nat + x, y, ang), x


def walk(n, t, speed=1.0, arms=True, lean=3.0, stride=1.0):
    S = 5.4 * stride
    a, xa = gait_leg(t, 0.0, S, 3.6, 0.6, 1.0)
    b, xb = gait_leg(t, 0.5, S, 3.6, 0.6, -1.0)
    p = base(fN=a, fF=b, lean=lean, dy=-0.55 * math.cos(2 * TAU * (t - 0.3)) + 0.2, head=-lean * 0.7 + 1.2 * math.sin(TAU * t + 1),
             sway=0.55 * math.sin(TAU * t), blink=blink_at(t))
    if arms:
        sw = 34 * stride
        p['armN'] = ((xb / S) * sw * 0.9, 8 + 12 * max(0, xb / S))
        p['armF'] = ((xa / S) * sw * 0.9, 8 + 12 * max(0, xa / S))
    return p


def run(n, t, lean=14.0):
    S = 8.6
    a, xa = gait_leg(t, 0.0, S, 8.5, 0.36, 1.0)
    b, xb = gait_leg(t, 0.5, S, 8.5, 0.36, -1.0)
    dy = -1.6 * max(0.0, math.cos(2 * TAU * (t - 0.18))) + 0.6
    p = base(fN=a, fF=b, lean=lean, dy=dy, head=-lean * 0.7, sway=1.4 * math.sin(TAU * t), blink=0, mouth=0)
    p['armN'] = ((xb / S) * 52, 88 + 6 * (xb / S))
    p['armF'] = ((xa / S) * 52, 88 + 6 * (xa / S))
    return p


def idle(n, t):
    st = getattr(n, 'idle_style', 'normal')
    p = base(dy=0.35 * math.sin(TAU * t), head=1.4 * math.sin(TAU * t + 0.4), lean=0.6 * math.sin(TAU * t + 0.4),
             fN=(2.0 + 0.5 * math.sin(TAU * t), 0.0, 0.0), blink=blink_at(t, (0.62,)), sway=0.3 * math.sin(TAU * t))
    p['armN'] = (8.0 + 2 * math.sin(TAU * t + 0.8), 10.0)
    p['armF'] = (-6.0 - 1.5 * math.sin(TAU * t + 0.8), 8.0)
    if st == 'hunch':
        p['lean'] += 8; p['head'] += -6
    return p


def talk(n, t):
    p = idle(n, t)
    g1 = sm(max(0, math.sin(TAU * (t * 2 - 0.05))))
    p['hN'] = (6.5 + 2.5 * g1, 2.0 - 7.0 * g1 + 1.2 * math.sin(TAU * t * 6) * g1)
    p['head'] = 3.0 * math.sin(TAU * t * 2) + 1.0
    p['mouth'] = 1 if (math.sin(TAU * t * 9) > 0.1 and (t % 0.5) < 0.38) else 0
    p['dy'] += -0.5 * g1
    p['hF'] = None
    return p


# ------------------------------------------------------------------ pekerjaan
def hold_arms(p, hn=None, hf=None):
    if hn is not None: p['hN'] = hn
    if hf is not None: p['hF'] = hf
    return p


def cangkul(n, t):
    K = lambda lean, G, phi, dy: base(lean=lean, tool=('hoe', G[0], G[1], phi, 7.0), fN=(5.0, 0, 0), fF=(-4.0, 0, 0), dy=dy, head=-lean * 0.5)
    keys = [(0.0, K(22, (8, 4.5), 74, 1.2)), (0.38, K(-5, (-2, -7), -122, -0.2)), (0.5, K(-7, (-3, -8), -128, -0.3)),
            (0.60, K(24, (8, 4.5), 62, 1.4)), (0.80, K(22, (6, 5), 80, 1.2)), (1.0, K(22, (8, 4.5), 74, 1.2))]
    return kf(t, keys)


def tanam(n, t):
    def K(dy, lean, hn, head, hf=(6, 4)):
        return base(dy=dy, lean=lean, fN=(5.0, 0, 0), fF=(-3.0, 0, 0), hN=hn, hF=hf, head=head)
    keys = [(0.0, K(0, 4, (6, 6), 2, (-3, 8))), (0.22, K(6, 40, (8, 11), 12, (3, 8))), (0.38, K(7, 44, (11, 14.6), 14, (3, 9))),
            (0.52, K(7, 42, (10, 13.6), 12, (3, 9))), (0.62, K(7, 44, (11, 14.6), 14, (3, 9))), (0.82, K(2, 18, (8, 8), 4, (-2, 8))), (1.0, K(0, 4, (6, 6), 2, (-3, 8)))]
    p = kf(t, keys)
    p['blink'] = blink_at(t, (0.9,))
    return p


def menabur(n, t):
    p = walk(n, t, stride=0.5, lean=6)
    ph = (t * 2) % 1.0
    ang = -25 + 110 * sm(min(1.0, ph / 0.55)) if ph < 0.55 else 85 - 110 * sm((ph - 0.55) / 0.45)
    p['armN'] = (ang, 22 - 14 * (1 if ph < 0.55 else 0))
    p['armF'] = (-8, 40)
    p['fx'] = []
    if 0.5 < ph < 0.8:
        k = (ph - 0.5) / 0.3
        for i in range(4):
            p['fx'].append(('rel', 'N', 2 + 9 * k + i * 1.6, -1 + 6 * k * (1 + 0.3 * i) - 3 * i * (1 - k), (232, 200, 100, 255)))
    return p


def memanen(n, t):
    def K(lean, hn, hf, phi, dx):
        return base(lean=lean, dx=dx, tool=('sickle', hn[0], hn[1], phi, 0), hF=hf, fN=(4.0, 0, 0), fF=(-4.0, 0, 0), head=-lean * 0.3, dy=1.0)
    keys = [(0.0, K(24, (11, 12), (7, 8), 20, 0)), (0.3, K(22, (7, 14), (6, 7), 90, 0.5)), (0.5, K(18, (1, 11), (4, 6), 150, 1.0)),
            (0.72, K(14, (-1, 6), (3, 4), 170, 0.6)), (0.9, K(20, (7, 11), (6, 7), 60, 0.2)), (1.0, K(24, (11, 12), (7, 8), 20, 0))]
    return kf(t, keys)


def walk_carry(tool, gx, gy, phi, hn=None, hf=None, lean=3.0, stride=1.0, two=0):
    def f(n, t):
        p = walk(n, t, lean=lean, stride=stride)
        p['tool'] = (tool, gx, gy + 0.5 * math.cos(2 * TAU * (t - 0.3)), phi + 1.5 * math.sin(TAU * t), two)
        if hf is not None:
            p['hF'] = hf
        else:
            p['armF'] = (-10 * math.sin(TAU * t), 14)
        p.pop('armN', None)
        if tool in ('sack', 'log'):
            p['tool_z'] = 'back'
        return p
    return f


def menyapu(n, t):
    s = math.sin(TAU * t)
    G = (4.5 + 3.0 * s, 6.0)
    phi = 62 + 14 * s
    p = base(lean=12 + 2 * s, tool=('broom', G[0], G[1], phi, 7.0), fN=(3.0 + 1.5 * s, 0, 0), fF=(-3.0, 0, 0), dy=0.3 * abs(s),
             head=5 - 3 * s, blink=blink_at(t))
    return p


def jaga(n, t):
    p = idle(n, t)
    p['tool'] = ('spear', 8.6, 4.5 + 0.2 * math.sin(TAU * t), -92 + 0.6 * math.sin(TAU * t), 0)
    p['armF'] = (-4.0, 10.0)
    p['fN'] = (3.0, 0.0, 0.0)
    shift = max(0.0, math.sin(TAU * (t - 0.4)) ) ** 4
    p['dx'] = 0.4 * shift
    p['head'] += 1.0 * shift
    return p


def tusuk(n, t):
    def K(G, phi, lean, fx, dy=0.0):
        return base(tool=('spear', G[0], G[1], phi, 8.0), lean=lean, fN=(fx, 0, 0), fF=(-5.0, 0, 0), dy=dy, head=-lean * 0.5, mouth=0)
    keys = [(0.0, K((5, 2), -22, 4, 4)), (0.3, K((0, 3), -10, 0, 3, 0.4)), (0.42, K((12.5, 2), -4, 18, 8, 0.6)), (0.55, K((12.5, 2), -4, 18, 8, 0.6)),
            (0.8, K((6, 2), -16, 6, 5)), (1.0, K((5, 2), -22, 4, 4))]
    p = kf(t, keys)
    p['mouth'] = 1 if 0.38 < t < 0.55 else 0
    return p


def menempa(n, t):
    def K(G, phi, lean, dy, hf):
        return base(tool=('hammer', G[0], G[1], phi, 0), lean=lean, hF=hf, fN=(4.0, 0, 0), fF=(-4.0, 0, 0), dy=dy, head=lean * 0.4)
    anvil = (11, 13)
    keys = [(0.0, K((8, 12), 58, 18, 1.0, anvil)), (0.10, K((6, 5), 10, 12, 0.6, anvil)), (0.32, K((1, -8), -112, 4, -0.4, (11, 12))),
            (0.42, K((0, -9), -116, 3, -0.6, (11, 12))), (0.52, K((8, 12), 58, 18, 1.0, anvil)), (0.58, K((7, 10), 40, 16, 0.8, anvil)),
            (1.0, K((8, 12), 58, 18, 1.0, anvil))]
    p = kf(t, keys)
    p['fx'] = []
    if 0.5 <= t < 0.66:
        k = (t - 0.5) / 0.16
        for i, (dx, dy) in enumerate([(2, -2), (4, -4), (3, -6), (0, -5), (5, -1)]):
            p['fx'].append(('rel', 'F', 1 + dx * k * 1.5, -2 + dy * k * 1.4 + 3 * k * k, (255, 230 - i * 20, 120, 255)))
    return p


def berkacak(n, t):
    p = idle(n, t)
    p['hN'] = (3.5, 7.0); p['hF'] = (-1.0, 7.5)
    p['head'] += 2 * math.sin(TAU * t * 1 + 1)
    p['lean'] = -1.0 + 0.6 * math.sin(TAU * t)
    return p


def membaca(n, t):
    pg = sm(max(0, min(1, (t - 0.52) / 0.12))) * (1 - sm(max(0, min(1, (t - 0.66) / 0.12))))
    p = base(dy=0.3 * math.sin(TAU * t), lean=2, head=13 + 1.2 * math.sin(TAU * t), tool=('book', 5.8, 5.2, -38, 0), fN=(2.0, 0, 0), fF=(-3.0, 0, 0))
    p['hF'] = (7.0 + 3.5 * pg, 8.0 - 6.0 * pg)
    p['blink'] = blink_at(t, (0.25, 0.85))
    return p


def menata_buku(n, t):
    def K(hn, head, lean, hf=(5, 6), book=True):
        p = base(hN=hn, head=head, lean=lean, hF=hf, fN=(3.0, 0, 0), fF=(-3.0, 0, 0))
        p['tool'] = ('book', hn[0] + 0.6, hn[1] - 0.2, -50 if hn[1] > -2 else -88, 0)
        return p
    keys = [(0.0, K((6, 6), 4, 0)), (0.28, K((8.5, -2), -6, -2)), (0.45, K((11, -10), -12, -3)), (0.58, K((12.5, -10), -12, -3)),
            (0.72, K((9, -4), -4, -1)), (1.0, K((6, 6), 4, 0))]
    p = kf(t, keys)
    if 0.5 <= t <= 0.62:
        p['tool'] = None
        p.pop('tool')
    p['blink'] = blink_at(t, (0.9,))
    return p


def menawarkan(n, t):
    p = talk(n, t)
    g = sm(max(0, math.sin(TAU * (t * 2 + 0.1))))
    p['hN'] = (7.0 + 3.5 * g, 1.0 - 9.0 * g)
    p['hF'] = (-1.0 + 6.5 * (1 - g), 7.0 - 1.5 * g)
    p['dy'] = -0.9 * abs(math.sin(TAU * t * 2))
    p['head'] = 4 * math.sin(TAU * t * 2 + 0.4) - 2
    return p


def hitung_koin(n, t):
    pick = sm(max(0, math.sin(TAU * t * 3)))
    p = base(lean=5, head=12, dy=0.25 * math.sin(TAU * t), fN=(2.0, 0, 0), fF=(-3.0, 0, 0))
    p['hF'] = (6.5, 7.5)
    p['hN'] = (6.5 + 1.2 * pick, 3.0 + 4.0 * (1 - pick))
    p['fx'] = [('rel', 'F', 0.5, -2.2, (240, 196, 85, 255)), ('rel', 'F', 1.6, -2.6, (240, 196, 85, 255)), ('rel', 'F', 0.9, -3.3, (200, 150, 60, 255))]
    p['blink'] = blink_at(t, (0.4,))
    return p


def berdoa(n, t):
    p = base(lean=2, head=15 + 1.5 * math.sin(TAU * t), dy=0.3 * math.sin(TAU * t), fN=(2.0, 0, 0), fF=(-2.5, 0, 0))
    p['hN'] = (5.0, 3.5 + 0.4 * math.sin(TAU * t)); p['hF'] = (5.5, 4.0 + 0.4 * math.sin(TAU * t))
    p['blink'] = 1 if 0.2 < t < 0.8 else 0
    return p


def memberkati(n, t):
    a = TAU * t
    p = base(lean=0, head=-2, fN=(2.0, 0, 0), fF=(-2.5, 0, 0))
    cx = 10 + 0.0
    vert = sm(max(0, min(1, (t - 0.15) / 0.2))) * (1 - sm(max(0, min(1, (t - 0.5) / 0.15))))
    hor = sm(max(0, min(1, (t - 0.38) / 0.18))) * (1 - sm(max(0, min(1, (t - 0.6) / 0.15))))
    raise_ = sm(max(0, min(1, t / 0.18))) * (1 - sm(max(0, min(1, (t - 0.85) / 0.15))))
    p['hN'] = (6 + 4 * raise_ + 1.5 * hor, 6 - 14 * raise_ + 6 * vert + 0.0 * hor)
    p['hF'] = (-2.0, 8.0)
    p['mouth'] = 1 if 0.1 < t < 0.55 and (t * 24) % 2 < 1 else 0
    p['dy'] = 0.3 * math.sin(a)
    return p


def menguleni(n, t):
    a = math.sin(TAU * t * 2)
    p = base(lean=14 + 2 * a, head=8, dy=0.5 * abs(a), fN=(4.0, 0, 0), fF=(-3.0, 0, 0))
    p['hN'] = (9.5 + 2.0 * a, 9.0 + 1.2 * abs(a)); p['hF'] = (8.5 - 2.0 * a, 9.5 + 1.0 * abs(a))
    p['blink'] = blink_at(t, (0.7,))
    return p


def menebang(n, t):
    def K(G, phi, lean, dy, fx):
        return base(tool=('axe', G[0], G[1], phi, 7.0), lean=lean, fN=(fx, 0, 0), fF=(-4.0, 0, 0), dy=dy, head=-lean * 0.4)
    keys = [(0.0, K((8, 8), 64, 20, 1.0, 5)), (0.40, K((0, -7), -120, 2, -0.5, 4)), (0.52, K((-1, -8), -126, 0, -0.6, 4)),
            (0.62, K((9, 8), 70, 22, 1.2, 6)), (0.78, K((9, 8), 66, 20, 1.0, 5)), (1.0, K((8, 8), 64, 20, 1.0, 5))]
    return kf(t, keys)


def memanah(n, t):
    def K(hb, hs, lean=2, phi=-4, draw=0.0, rel=0):
        p = base(lean=lean, fN=(3.0, 0, 0), fF=(-5.0, 0, 0), head=-1, tool=('bow', hb[0], hb[1], phi, 0, 'F'), hN=hs)
        p['draw'] = draw
        return p
    keys = [(0.0, K((12.5, 0.5), (-1, 3), 0, -4, 0)), (0.12, K((12.5, 0.5), (1, 3), 0, -4, 0.2)), (0.5, K((13, -0.5), (-5, -1), -2, -2, 1.0)),
            (0.72, K((13, -0.5), (-5.4, -1), -2, -2, 1.0)), (0.76, K((13.4, -0.4), (-8, 0.6), -2, -2, 0.0)), (0.9, K((12.5, 0.5), (-3, 3), 0, -4, 0.0)),
            (1.0, K((12.5, 0.5), (-1, 3), 0, -4, 0))]
    p = kf(t, keys)
    p['arrow'] = None
    if t < 0.76:
        p['arrow'] = 'nocked'
    elif t < 0.95:
        p['arrow'] = ('fly', 36 + (t - 0.76) * 150, 25)
    return p


def mengintai(n, t):
    p = idle(n, t)
    sway = math.sin(TAU * t)
    p['hN'] = (6.5, -11.5 + 0.5 * sway)
    p['head'] = -4 + 5 * sway
    p['lean'] = 2 + 1.0 * sway
    p['armF'] = (-5, 14)
    return p


def melompat(n, t):
    h = math.sin(math.pi * ((t * 2) % 1.0))
    air = max(0.0, h)
    crouch = max(0.0, 1 - h * 4) * 0.0
    p = base(dy=-7.0 * air + 1.6 * (1 - min(1, h * 5)), lean=-2 + 4 * (1 - h), head=-4 * h)
    p['fN'] = (1.5, 3.8 * air, 18 * air); p['fF'] = (-2.0, 3.0 * air, 12 * air)
    p['armN'] = (-15 + 95 * air, 16); p['armF'] = (15 - 85 * air, 16)
    p['mouth'] = 1 if air > 0.3 else 0
    return p


def melambai(n, t):
    p = idle(n, t)
    p['hN'] = (7.0 + 2.2 * math.sin(TAU * t * 3), -9.5 - 1.0 * abs(math.sin(TAU * t * 3)))
    p['head'] = 3 * math.sin(TAU * t * 1.5)
    p['mouth'] = 1 if (t * 6) % 1 < 0.5 else 0
    p['dy'] = -0.4 * abs(math.sin(TAU * t * 3))
    return p


def melambai_agung(n, t):
    p = idle(n, t)
    e = sm(max(0, min(1, t / 0.2))) * (1 - sm(max(0, min(1, (t - 0.8) / 0.2))))
    s = math.sin(TAU * t * 2)
    p['hN'] = (8.5 + 1.2 * s * e, 6 - 8 * e)
    p['head'] = 1.0 + 2 * e
    p['lean'] = -1.5 * e
    p['mouth'] = 0
    return p


def pose_bangga(n, t):
    p = idle(n, t)
    p['lean'] = -2.5 + 0.5 * math.sin(TAU * t)
    p['head'] = -4 + 1.2 * math.sin(TAU * t + 0.6)
    p['hN'] = (2.5, 8.0); p['hF'] = (-1.5, 7.0)
    p['blink'] = blink_at(t, (0.5,))
    return p


GENERIC = {
    'diam': (60, idle), 'jalan': (30, walk), 'lari': (20, run), 'ngobrol': (60, talk),
}
JOBS = {
    'cangkul': (36, cangkul), 'tanam': (48, tanam), 'menabur': (36, menabur), 'memanen': (40, memanen),
    'bawa_karung': (30, walk_carry('sack', -9.5, -3.0, -4, hn=None, hf=None, lean=5)),
    'bawa_keranjang': (30, walk_carry('basket', 7.5, 10.5, 0, lean=3)),
    'menyapu': (40, menyapu), 'jaga': (60, jaga), 'tusuk': (30, tusuk), 'menempa': (30, menempa), 'berkacak': (60, berkacak),
    'membaca': (60, membaca), 'menata_buku': (48, menata_buku), 'menawarkan': (60, menawarkan), 'hitung_koin': (48, hitung_koin),
    'berdoa': (60, berdoa), 'memberkati': (48, memberkati), 'menguleni': (36, menguleni),
    'bawa_nampan': (30, walk_carry('tray', 7.0, 5.0, -2, lean=3, stride=0.9)),
    'menebang': (36, menebang), 'bawa_kayu': (30, walk_carry('log', -7.0, -3.0, -8, lean=5)),
    'memanah': (60, memanah), 'mengintai': (60, mengintai), 'melompat': (24, melompat), 'melambai': (36, melambai),
    'melambai_agung': (48, melambai_agung), 'pose_bangga': (60, pose_bangga),
}
ALL = dict(GENERIC); ALL.update(JOBS)
