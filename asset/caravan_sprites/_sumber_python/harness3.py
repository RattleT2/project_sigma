import math
from horse3 import *

HARN = {
 'coklat': dict(L=H('6a3f24'), Ld=H('45281a'), Ll=H('8f5a36'), brass=H('f0c455'), brass_d=H('b8892c'), acc=H('9a5a34'), rein=H('3b2217')),
 'hitam':  dict(L=H('37323d'), Ld=H('1f1c24'), Ll=H('554f5e'), brass=H('d9dde6'), brass_d=H('9096a4'), acc=H('a02e3a'), rein=H('1f1c24')),
 'merah':  dict(L=H('8a3030'), Ld=H('552022'), Ll=H('b24a45'), brass=H('f7d35c'), brass_d=H('c19a2a'), acc=H('2f6a8a'), rein=H('552022')),
}
HITCH = (7.0, 41.0)

def line(c, pts, w, col):
    for i in range(len(pts) - 1):
        c.cap(pts[i], pts[i + 1], max(w, 1.1), max(w, 1.1), col, rnd=False)

def chaikin_open(pts, it=2):
    return chaikin(pts, it, closed=False)

def h_kerah(spec, p, hc):
    R = Rig(p); c = Cv(spec)
    path = R.Bs([(58, 22.5), (62.6, 24.5), (65.4, 29.5), (65.0, 34.5), (62.2, 38.5)])
    line(c, path, 4.0, hc['L'])
    line(c, [(x - 0.6, y - 0.4) for x, y in path], 1.2, hc['Ll'])
    o = c.out()
    for q in R.Bs([(60.2, 20.8), (60.8, 21.8)]):
        put(o, spec, q[0], q[1], hc['brass'])
    c2 = Cv(spec); line(c2, R.Bs([(61.0, 22.8), (64.2, 26), (65.8, 30.5), (65.0, 36)]), 1.1, hc['brass']); o.alpha_composite(c2.out())
    q = R.B((65.9, 32.5)); put(o, spec, q[0], q[1], hc['brass_d'])
    return o

def h_badan(spec, p, hc):
    R = Rig(p); c = Cv(spec)
    c.poly(R.Bs([(43, 20.8), (51.5, 20.6), (52, 25.0), (43.5, 25.2)]), hc['Ld'])
    c.poly(R.Bs([(43.6, 20.8), (51, 20.8), (51, 22.2), (43.6, 22.2)]), hc['acc'])
    line(c, R.Bs([(47.6, 25), (47.9, 41.4)]), 2.6, hc['L'])
    line(c, R.Bs([(42, 22.6), (30, 22.8), (21.5, 24.2), (18.2, 29.5), (18.4, 35.2)]), 1.8, hc['L'])
    line(c, R.Bs([(25, 23.0), (24.6, 29), (22.6, 36)]), 1.4, hc['Ld'])
    o = c.out()
    for q in R.Bs([(47, 19.7), (48, 19.7), (47.6, 32), (18.2, 32)]):
        put(o, spec, q[0], q[1], hc['brass'])
    return o

def h_kepala(spec, p, hc):
    R = Rig(p); c = Cv(spec)
    line(c, R.Hs([(77.0, 8.8), (81.4, 10.4)]), 1.3, hc['Ld'])
    line(c, R.Hs([(77.6, 9.2), (77.9, 16.8), (84.4, 23.6)]), 1.3, hc['L'])
    line(c, R.Hs([(84.2, 18.8), (89.0, 21.2), (90.2, 24.2)]), 1.3, hc['L'])
    line(c, R.Hs([(76.0, 10.2), (76.1, 17.4)]), 1.1, hc['Ld'])
    o = c.out()
    bx, by = R.Hd((87.0, 25.0)); put(o, spec, round(bx), round(by), hc['brass']); put(o, spec, round(bx) + 1, round(by), hc['brass_d'])
    jx, jy = R.Hd((77.6, 9.6)); put(o, spec, round(jx), round(jy), hc['brass'])
    return o

def h_tali(spec, p, hc, anchored):
    """traces + kekang. anchored=True (jalan/diam): ujung tetap di palang tarik (7,41) & tangan pengemudi (0,20).
    anchored=False (lari/lompat/berhenti): ujung ikut badan & berayun bebas."""
    R = Rig(p); c = Cv(spec)
    b = p['dy']
    if anchored:
        end_t = HITCH; end_r = (0.0, 20.0)
    else:
        sw = math.sin(p['mane']) * 1.2
        end_t = R.B((5.0 + sw, 42.0)); end_r = R.B((0.0 + sw, 21.5))
    tr_pts = [R.B((65.4, 33.0)), R.B((52, 36.0)), R.B((34, 38.4)), (end_t[0] + 2, end_t[1] - 0.6) if anchored else R.B((12, 40.5)), end_t]
    line(c, tr_pts, 1.3, hc['L'])
    bit = R.Hd((87.0, 25.0))
    sag = 1.2 * math.sin(p['mane'] - 1.0)
    mid = [R.Hd((80, 21.5)), R.Ns([(73, 18.5)])[0], R.B((60, 17.0)), R.B((47.6, 18.6)), R.B((34, 17.6 + sag * 0.5)), R.B((18, 18.4 + sag)), R.B((8, 19.4)), end_r]
    line(c, chaikin_open([bit] + mid), 1.1, hc['rein'])
    o = c.out()
    put(o, spec, end_t[0], end_t[1], hc['brass'])
    return o

HLAYERS = [('h1_kerah', h_kerah), ('h2_badan', h_badan), ('h3_kepala', h_kepala), ('h4_tali', None)]

def render_harness_frame(spec, p, hc, anchored):
    return {'h1_kerah': h_kerah(spec, p, hc), 'h2_badan': h_badan(spec, p, hc), 'h3_kepala': h_kepala(spec, p, hc),
            'h4_tali': h_tali(spec, p, hc, anchored)}
