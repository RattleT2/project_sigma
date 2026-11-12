from pxlib import *

DW, DH = 24, 32
DHP = 34  # padded canvas height

def pad(im):
    o = new(DW, DHP)
    o.paste(im, (0, 2))
    return o

EYE = H('1b1116')

D1 = dict(  # pionir berhat
    kind='man', skin=H('f0b98d'), skin_d=H('cf8e68'), hair=H('6a4528'),
    hat=H('8f5d36'), hat_d=H('5d3820'), hat_l=H('b27b4a'), band=H('2f1d14'),
    shirt=H('5b86c7'), shirt_d=H('3f64a0'), shirt_l=H('86abdf'),
    pants=H('7b6349'), pants_d=H('564330'), boots=H('4b2f20'), boots_d=H('2c190f'),
    scarf=H('c8433a'), sus=H('6a3d22'), stache=H('5a3520'), rein=H('3a2014'),
)
D2 = dict(  # wanita pedagang berkerudung
    kind='woman', skin=H('eab38e'), skin_d=H('c98a68'), hair=H('7a4a2a'),
    hat=H('de4f58'), hat_d=H('a42e3d'), hat_l=H('f07a78'), band=H('f6e3a1'),
    shirt=H('f3ead8'), shirt_d=H('cdc1aa'), shirt_l=H('ffffff'),
    pants=H('2f9c93'), pants_d=H('1d6f6c'), boots=H('3d2a30'), boots_d=H('231519'),
    scarf=H('f6e3a1'), sus=H('55bdb0'), stache=None, rein=H('3a2014'),
)


def draw_driver(c, f):
    dy = [0, 0, 1, 1, 0, 0, 1, 1][f]
    hy = [0, 1, 1, 0, 0, 1, 1, 0][f]  # head nod
    sway = [0, 1, 1, 0, 0, 1, 1, 0][f]
    legs = new(DW, DH)
    body = new(DW, DH)
    arm = new(DW, DH)
    head = new(DW, DH)
    pl, pb, pa, ph = P(legs), P(body), P(arm), P(head)

    # ---- legs (sitting): thigh horizontal, shin down
    pl.rect(6, 21, 17, 24, c['pants'])
    pl.rect(6, 21, 17, 21, c['pants'])
    pl.rect(6, 24, 16, 24, c['pants_d'])
    pl.rect(15, 22, 18, 29, c['pants'])
    pl.rect(18, 22, 18, 29, c['pants_d'])
    pl.rect(14, 29, 21, 31, c['boots'])
    pl.rect(14, 31, 21, 31, c['boots_d'])
    pl.px(21, 31, c['boots_d'])
    pl.px(15, 29, c['boots_d'])
    pl.line(15, 24, 15, 28, c['pants_d'])   # knee fold
    if c['kind'] == 'woman':
        # long skirt covering thigh & part of shin
        pl.poly([(5, 20), (18, 20), (19, 26), (19, 29), (14, 29), (13, 25), (5, 25)], c['pants'])
        pl.rect(14, 26, 19, 29, c['pants'])
        pl.line(8, 25, 13, 25, c['pants_d'])
        pl.line(16, 27, 19, 27, c['pants_d'])
        pl.rect(15, 29, 21, 31, c['boots'])
        pl.rect(15, 31, 21, 31, c['boots_d'])
        pl.px(20, 22, c['pants_d']); pl.px(18, 22, c['pants_d'])
        pl.pxs([(8, 23), (10, 22), (12, 23)], c['pants_d'])

    # ---- torso
    t0 = dy
    if c['kind'] == 'man':
        pb.rect(4, 11 + t0, 11, 22, c['shirt'])
        pb.rect(4, 11 + t0, 5, 22, c['shirt_d'])
        pb.rect(8, 12 + t0, 10, 13 + t0, c['shirt_l'])
        pb.rect(4, 19 + t0, 11, 22, c['pants'])      # belt + trousers waist
        pb.rect(4, 19 + t0, 11, 19 + t0, c['band'])
        pb.px(8, 19 + t0, H('f0c455'))
        # suspenders
        pb.line(8, 11 + t0, 8, 19 + t0, c['sus'])
        pb.line(10, 11 + t0, 10, 19 + t0, c['sus'])
        # neckerchief
        pb.rect(8, 10 + t0, 11, 11 + t0, c['scarf'])
        pb.px(11, 12 + t0, c['scarf'])
    else:
        pb.rect(4, 11 + t0, 11, 22, c['pants'])      # dress bodice (teal)
        pb.rect(4, 11 + t0, 5, 22, c['pants_d'])
        pb.rect(8, 12 + t0, 10, 13 + t0, H('55bdb0'))
        pb.rect(7, 15 + t0, 11, 22, c['shirt'])       # apron
        pb.rect(7, 15 + t0, 7, 22, c['shirt_d'])
        pb.rect(7, 15 + t0, 11, 15 + t0, c['shirt_d'])
        pb.line(5, 17 + t0, 4, 20 + t0, c['pants_d'])
        pb.rect(8, 10 + t0, 11, 11 + t0, c['shirt'])  # collar
        pb.px(5, 19 + t0, c['hat'])                   # bow
        pb.px(4, 20 + t0, c['hat'])
    body_o = body

    # ---- head
    y0 = hy + dy
    ph.ell(6, 3 + y0, 14, 11 + y0, c['skin'])
    ph.rect(8, 9 + y0, 12, 11 + y0, c['skin'])
    ph.px(14, 8 + y0, c['skin'])        # nose
    ph.px(15, 8 + y0, c['skin'])
    ph.px(14, 9 + y0, c['skin_d'])
    ph.px(11, 11 + y0, c['skin_d']); ph.px(12, 11 + y0, c['skin_d'])
    ph.px(7, 9 + y0, c['skin_d'])
    # ear
    ph.px(7, 7 + y0, c['skin_d'])
    # eye (visible)
    ph.rect(12, 6 + y0, 12, 7 + y0, EYE)
    ph.px(13, 6 + y0, H('ffffff')) if False else None
    ph.px(11, 5 + y0, c['skin_d'])  # brow shadow
    ph.px(12, 5 + y0, c['skin_d'])
    # mouth / cheek
    ph.px(13, 10 + y0, c['skin_d'])
    if c['kind'] == 'man':
        ph.rect(12, 9 + y0, 15, 9 + y0, c['stache'])
        ph.px(11, 9 + y0, c['stache'])
        ph.rect(6, 8 + y0, 8, 11 + y0, c['hair'])     # sideburn / hair back
        ph.rect(8, 11 + y0, 10, 11 + y0, c['stache'])
        # hat: crown + brim
        ph.rect(6, 0 + y0, 13, 4 + y0, c['hat'])
        ph.rect(6, 0 + y0, 13, 0 + y0, c['hat_l'])
        ph.rect(6, 3 + y0, 13, 3 + y0, c['band'])
        ph.rect(2, 4 + y0, 18, 5 + y0, c['hat'])
        ph.rect(2, 5 + y0, 18, 5 + y0, c['hat_d'])
        ph.px(18, 4 + y0, c['hat_l']); ph.px(17, 4 + y0, c['hat_l'])
        ph.px(9, 1 + y0, c['hat_l'])
        ph.px(10, 0 + y0, c['hat_d']) if False else None
    else:
        # hair + headscarf, braid at back
        ph.rect(5, 6 + y0, 8, 11 + y0, c['hair'])
        ph.rect(4, 11 + y0, 6, 17 + y0, c['hair'])       # braid down the back
        ph.px(5, 18 + y0, c['hat']); ph.px(4, 17 + y0, c['hair'])
        ph.pxs([(5, 13 + y0), (5, 15 + y0)], H('5a3320'))
        ph.rect(5, 1 + y0, 14, 5 + y0, c['hat'])         # headscarf (kerudung)
        ph.rect(6, 0 + y0, 12, 1 + y0, c['hat'])
        ph.rect(6, 0 + y0, 11, 0 + y0, c['hat_l'])
        ph.line(5, 5 + y0, 14, 5 + y0, c['hat_d'])
        ph.rect(5, 3 + y0, 6, 8 + y0, c['hat'])          # tail of scarf
        ph.rect(4, 6 + y0, 5, 9 + y0, c['hat_d'])
        ph.pxs([(8, 2 + y0), (11, 3 + y0), (9, 4 + y0)], c['band'])   # polka dots
        ph.px(13, 9 + y0, H('e08a80'))    # blush/lip

    # ---- arm holding the reins
    hx, hyy = 18, 18 + (0 if dy == 0 else 0)
    ay = dy
    pa.thick(9, 13 + ay, 11, 19, 3, c['shirt'] if c['kind'] == 'man' else c['shirt'])
    pa.thick(11, 19, 16, 18, 3, c['shirt'] if c['kind'] == 'man' else c['shirt'])
    pa.px(10, 14 + ay, c['shirt_l'])
    pa.rect(16, 17, 19, 19, c['skin'])       # hand
    pa.px(19, 17, c['skin_d'])
    # reins -> right edge (y=19 at x=23)
    ry = 18 + sway
    pa.line(19, 18, 23, 19, c['rein'])
    pa.px(20, ry + 1 if sway else 19, c['rein'])
    pa.line(17, 19, 17, 21, c['rein'])   # loop hanging
    pa.px(18, 21, c['rein'])
    legs, body, head, arm = pad(legs), pad(body), pad(head), pad(arm)
    arm_o = outline(arm, 0.5)

    # compose
    base = new(DW, DHP)
    lo = outline(legs)
    base.alpha_composite(lo); base.alpha_composite(legs)
    bo = outline(body)
    base.alpha_composite(bo); base.alpha_composite(body)
    ho = outline(head)
    base.alpha_composite(ho); base.alpha_composite(head)
    base.alpha_composite(arm_o); base.alpha_composite(arm)
    return base


def render_driver(c):
    return [draw_driver(c, f) for f in range(8)]


if __name__ == '__main__':
    a = render_driver(D1); b = render_driver(D2)
    s = sheet([a[0], a[2], b[0], b[2]])
    up(s, 12, (120, 160, 120, 255)).save('/home/claude/work/d_test.png')
