import math
from horse3 import smooth

IDLE_L = {'HN': (23.3, 58.0, 0), 'HF': (26.7, 58.0, 0), 'FN': (60.7, 58.0, 0), 'FF': (57.7, 58.0, 0)}
BASE = dict(dy=0.0, dx=0.0, pitch=0.0, neck=0.0, head=0.0, ear=0.0, tailbase=12.0, tailsway=0.0, tailcurve=2.2,
            wind=0.0, mane=0.0)
SCALARS = ['dy', 'dx', 'pitch', 'neck', 'head', 'ear', 'tailbase', 'tailsway', 'wind']
LKEYS = ['HN', 'HF', 'FN', 'FF']


def mk(legs=None, **kw):
    p = dict(BASE); p.update(kw)
    L = dict(IDLE_L)
    if legs:
        L.update(legs)
    p['legs'] = L
    return p

# ------------------------------------------------------------------ idle (berdiri) 8f
def pose_idle(f, n=8):
    t = f / float(n)
    flick = max(0.0, math.sin(2 * math.pi * (t - 0.55) * 1.0)) ** 3
    p = mk(dy=0.5 * math.sin(2 * math.pi * t), neck=1.6 * math.sin(2 * math.pi * t + 0.4), head=0.8 * math.sin(2 * math.pi * t + 1.2),
           ear=-16 * flick, tailbase=11, tailsway=1.2 * math.sin(2 * math.pi * t - 0.5), mane=2 * math.pi * t)
    return p

# ------------------------------------------------------------------ walk 12f
WALK_OFF = {'HN': 0.0, 'FN': 0.25, 'HF': 0.5, 'FF': 0.75}
WALK_NAT = {'HN': 24.5, 'HF': 25.5, 'FN': 59.5, 'FF': 58.5}


def pose_walk(f, n=12):
    t = f / float(n)
    S = 6.4
    legs = {}
    for k in LKEYS:
        q = (t - WALK_OFF[k]) % 1.0
        front = k[0] == 'F'
        th = 0.0
        if q < 0.60:
            x = S - 2 * S * (q / 0.60); lift = 0.0
            th = -10 * smooth((q - 0.50) / 0.10)
        else:
            s = (q - 0.60) / 0.40
            x = -S + 2 * S * smooth(s)
            lift = (5.6 if front else 4.6) * (math.sin(math.pi * s) ** 0.85)
            th = 30 * math.sin(math.pi * s) - 10 * (1 - smooth(min(1, s * 3)))
        legs[k] = (WALK_NAT[k] + x, 58.0 - lift, th)
    return mk(legs, dy=0.6 * math.sin(2 * math.pi * 2 * t + 0.5), pitch=0.6 * math.sin(2 * math.pi * t + 0.2),
              neck=2.6 * math.sin(2 * math.pi * t + 1.0), head=0.8 * math.sin(2 * math.pi * t - 0.4),
              tailbase=12, tailsway=math.sin(2 * math.pi * t - 0.9), mane=2 * math.pi * t)

# ------------------------------------------------------------------ gallop 10f
GAL_OFF = {'HN': 0.00, 'HF': 0.14, 'FN': 0.18, 'FF': 0.31}
GAL_NAT = {'HN': 24.0, 'HF': 25.5, 'FN': 58.0, 'FF': 57.0}


def pose_gallop(f, n=10):
    t = f / float(n)
    st = 0.27
    legs = {}
    for k in LKEYS:
        q = (t - GAL_OFF[k]) % 1.0
        front = k[0] == 'F'
        xa, xb = (8.0, -9.0) if front else (8.0, -10.0)       # depan / belakang relatif nominal
        if q < st:
            u = q / st
            x = xa + (xb - xa) * u; lift = 0.0
            th = -8 * smooth((u - 0.8) / 0.2)
        else:
            s = (q - st) / (1 - st)
            x = xb + (xa - xb) * smooth(s) + (3.0 * math.sin(math.pi * s) ** 2 if front else 0.0)
            lift = (14.0 if front else 10.5) * (math.sin(math.pi * s) ** (0.85 if front else 1.0))
            th = (58 if front else 40) * (math.sin(math.pi * s) ** 0.8)
        legs[k] = (GAL_NAT[k] + x, 58.0 - lift, th)
    dy = 0.6 - 3.6 * max(0.0, math.cos(2 * math.pi * (t - 0.78))) ** 1.2
    pitch = 4.5 * math.cos(2 * math.pi * (t - 0.38))
    return mk(legs, dy=dy, pitch=pitch, neck=10 + 4 * math.sin(2 * math.pi * (t - 0.1)), head=-8 + 3 * math.sin(2 * math.pi * t),
              ear=-38, tailbase=58, tailcurve=1.0, tailsway=0.5 * math.sin(2 * math.pi * t - 1.0), wind=1.7, mane=4 * math.pi * t)

# ------------------------------------------------------------------ keyframe machinery
def flat(p):
    v = [p[k] for k in SCALARS]
    for k in LKEYS:
        v += list(p['legs'][k])
    return v


def unflat(v, mane):
    p = dict(BASE)
    for i, k in enumerate(SCALARS):
        p[k] = v[i]
    off = len(SCALARS)
    p['legs'] = {}
    for j, k in enumerate(LKEYS):
        p['legs'][k] = tuple(v[off + j * 3: off + j * 3 + 3])
    p['mane'] = mane
    return p


def cr(p0, p1, p2, p3, t):
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)


def sample_keys(keys, u):
    n = len(keys)
    i = min(int(math.floor(u)), n - 2)
    t = u - i
    ks = [flat(keys[max(i - 1, 0)]), flat(keys[i]), flat(keys[i + 1]), flat(keys[min(i + 2, n - 1)])]
    return [cr(ks[0][j], ks[1][j], ks[2][j], ks[3][j], t) for j in range(len(ks[0]))]


def from_keys(keys, n, mane_speed=0.9, tail_follow=True):
    out = []
    for f in range(n):
        u = f * (len(keys) - 1) / float(n - 1)
        out.append(unflat(sample_keys(keys, u), f * mane_speed))
    return out

# ------------------------------------------------------------------ jump 14f
JUMP_KEYS = [
    mk(dict(HN=(22, 58, 0), HF=(26, 58, 0), FN=(59.5, 58, 0), FF=(57, 58, 0)), dy=2.0, pitch=-3, neck=-6, head=-2, tailbase=10),
    mk(dict(HN=(17, 58, -8), HF=(21, 58, -8), FN=(66, 49, 40), FF=(62, 51, 45)), dy=-2.5, pitch=-11, neck=-4, ear=-10, tailbase=16),
    mk(dict(HN=(13, 57, 20), HF=(18, 57.5, 20), FN=(63, 37, 60), FF=(59, 39, 62)), dy=-9, pitch=-10, neck=2, head=-2, ear=-18, tailbase=24),
    mk(dict(HN=(11, 46, 40), HF=(16, 49, 40), FN=(61, 28, 70), FF=(57, 30, 72)), dy=-18, pitch=-5, neck=8, head=-3, ear=-24, tailbase=30, wind=0.6),
    mk(dict(HN=(9, 24, 50), HF=(14, 27, 50), FN=(59, 21, 76), FF=(55, 23, 78)), dy=-24, pitch=2, neck=13, head=-6, ear=-28, tailbase=38, wind=0.9),
    mk(dict(HN=(12, 36, 42), HF=(17, 38, 40), FN=(68, 36, 30), FF=(64, 37, 32)), dy=-16, pitch=7, neck=16, head=-8, ear=-20, tailbase=34, wind=0.7),
    mk(dict(HN=(17, 48, 24), HF=(22, 50, 22), FN=(69, 48, 10), FF=(65, 49, 12)), dy=-7, pitch=9, neck=14, head=-8, ear=-12, tailbase=28, wind=0.4),
    mk(dict(HN=(22, 50, 18), HF=(27, 53, 15), FN=(66, 58, 0), FF=(62, 58, 0)), dy=1.2, pitch=7, neck=12, head=-6, ear=-6, tailbase=22),
    mk(dict(HN=(26, 58, 0), HF=(31, 58, 0), FN=(63, 58, 0), FF=(60, 58, 0)), dy=3.0, pitch=3, neck=6, head=-2, tailbase=16),
    mk(dict(HN=(24.5, 58, 0), HF=(27.5, 58, 0), FN=(59.5, 58, 0), FF=(56.5, 58, 0)), dy=0.5, pitch=-1, neck=0, tailbase=12),
]


def jump_poses(n=14):
    return from_keys(JUMP_KEYS, n, 0.9)

# ------------------------------------------------------------------ stop 9f
STOP_KEYS = [
    mk(dict(HN=(30, 54, 25), HF=(24, 55, 25), FN=(69, 52, 40), FF=(65, 54, 38)), dy=-2.5, pitch=3, neck=8, head=-5, ear=-30, tailbase=45, wind=1.2),
    mk(dict(HN=(34, 58, 0), HF=(31, 58, 0), FN=(66.5, 58, -5), FF=(63, 58, -5)), dy=1.5, pitch=-5, neck=-5, head=-6, ear=-5, tailbase=20, wind=-0.8),
    mk(dict(HN=(36, 58, 0), HF=(33, 58, 0), FN=(68, 58, -8), FF=(64.5, 58, -8)), dy=3.5, pitch=-9, neck=-10, head=-8, ear=5, tailbase=8, wind=-1.0),
    mk(dict(HN=(34, 58, 0), HF=(31, 58, 0), FN=(66, 58, -4), FF=(62.5, 58, -4)), dy=2.6, pitch=-7, neck=-9, head=-6, ear=2, tailbase=8, wind=-0.5),
    mk(dict(HN=(30, 58, 0), HF=(28, 58, 0), FN=(64, 58, 0), FF=(60.5, 58, 0)), dy=1.6, pitch=-4, neck=-5, head=-3, tailbase=10, wind=-0.2),
    mk(dict(HN=(27, 58, 0), HF=(29, 58, 0), FN=(62, 58, 0), FF=(58.5, 58, 0)), dy=0.8, pitch=-2, neck=-2, head=-1, tailbase=11),
    mk(None, dy=0.0, pitch=0.0, neck=0.0, tailbase=11),
]


def stop_poses(n=9):
    return from_keys(STOP_KEYS, n, 0.9)


ACTIONS = {
    'diam': (8, pose_idle, 'std'),
    'jalan': (12, pose_walk, 'std'),
    'lari': (10, pose_gallop, 'big'),
    'lompat': (14, None, 'big'),
    'berhenti': (9, None, 'big'),
}


def poses_for(action):
    n, fn, canvas = ACTIONS[action]
    if action == 'lompat':
        return jump_poses(n)
    if action == 'berhenti':
        return stop_poses(n)
    return [fn(f, n) for f in range(n)]
