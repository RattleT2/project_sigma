import math
from pxlib import *
from wagon import *

SACK = H('c9a468'); SACK_D = H('9c7a45'); SACK_L = H('e2c98c')


def fin(im, strength=0.6):
    out = new(WW, WH)
    out.alpha_composite(outline(im, strength)); out.alpha_composite(im)
    return out


def a_barrel():
    im = new(WW, WH); p = PO(im)
    # body
    p.rect(47, 46, 59, 59, WOOD)
    p.rect(46, 49, 60, 56, WOOD)
    for x in range(48, 60, 3):
        p.line(x, 47, x, 58, WOOD_D)
    p.line(48, 47, 48, 58, WOOD_L)
    p.rect(58, 47, 59, 58, WOOD_D)
    # lid
    p.ell(47, 44, 59, 48, WOOD_L)
    p.ell(49, 45, 57, 47, WOOD)
    p.px(53, 46, WOOD_D)
    # iron hoops
    for y in (49, 55):
        p.line(46, y, 60, y, IRON); p.line(46, y + 1, 60, y + 1, IRON_D)
        p.px(48, y, IRON_L); p.px(49, y, IRON_L)
    # rope lashing
    p.line(46, 52, 60, 58, ROPE); p.line(46, 53, 60, 59, ROPE_D)
    p.line(46, 58, 60, 50, ROPE); p.line(46, 59, 60, 51, ROPE_D)
    return fin(im)


def a_ropes():
    im = new(WW, WH); p = PO(im)
    for (x, y) in ((31, 41), (38, 42)):
        p.px(x + 3, y - 1, IRON); p.px(x + 3, y, IRON)
        p.ell(x, y + 1, x + 6, y + 11, ROPE)
        p.ell(x + 2, y + 4, x + 4, y + 8, (0, 0, 0, 0))
        # rope strands
        for k in range(y + 2, y + 11, 2):
            p.px(x + 1, k, ROPE_D); p.px(x + 5, k, ROPE_D)
        p.px(x + 3, y + 11, ROPE_D)
        p.line(x + 1, y + 2, x + 5, y + 2, ROPE_D)
        p.rect(x + 2, y + 5, x + 4, y + 7, (0, 0, 0, 0))
        p.line(x + 3, y + 1, x + 3, y + 4, ROPE_D)
    return fin(im)


def a_tools():
    im = new(WW, WH); p = PO(im)
    # shovel (sekop)
    p.line(11, 30, 11, 52, WOOD)
    p.line(12, 30, 12, 52, WOOD_D)
    p.rect(9, 29, 12, 30, WOOD_L)                    # D-grip
    p.rect(8, 40, 8, 40, WOOD)
    p.poly([(9, 49), (14, 49), (14, 52), (12, 56), (11, 56), (9, 52)], IRON_L)
    p.line(14, 49, 14, 52, IRON); p.line(10, 51, 13, 51, IRON)
    # pickaxe (beliung)
    p.line(17, 28, 17, 52, WOOD)
    p.line(18, 28, 18, 52, WOOD_D)
    p.line(12, 29, 22, 29, IRON); p.line(12, 30, 22, 30, IRON_D)
    p.px(11, 31, IRON); p.px(23, 31, IRON); p.px(10, 32, IRON_L)
    p.px(17, 29, IRON_L); p.px(18, 29, IRON_L)
    # tied with a strap on the wall
    p.rect(10, 41, 19, 42, ROPE_D)
    p.px(15, 41, ROPE)
    return fin(im, 0.55)


def a_lantern(glow=True):
    im = new(WW, WH); p = PO(im)
    g = H('ffd45e'); gl = H('fff2b0')
    p.line(90, 24, 90, 28, IRON)                    # hanger
    p.px(89, 24, IRON); p.px(88, 25, IRON)
    p.rect(86, 29, 91, 30, IRON_D)
    p.line(87, 29, 90, 29, IRON)
    p.rect(87, 31, 90, 37, g)
    p.rect(88, 32, 89, 35, gl)
    p.line(86, 31, 86, 37, IRON); p.line(91, 31, 91, 37, IRON)
    p.line(86, 34, 91, 34, IRON_D) if False else None
    p.rect(86, 38, 91, 39, IRON_D)
    p.px(86, 38, IRON); p.px(91, 38, IRON)
    out = fin(im)
    if glow:
        gp = new(WW, WH); q = PO(gp)
        for (x, y) in [(84, 33), (84, 34), (93, 33), (93, 34), (88, 41), (89, 41), (88, 27), (89, 27)]:
            q.px(x, y, (255, 222, 120, 95))
        for (x, y) in [(83, 34), (94, 34), (85, 40), (92, 40)]:
            q.px(x, y, (255, 222, 120, 55))
        out.alpha_composite(gp)
    return out


def a_pots():
    im = new(WW, WH); p = PO(im)
    # bucket (ember kayu)
    p.poly([(17, 49), (25, 49), (24, 58), (18, 58)], WOOD)
    p.line(17, 49, 18, 58, WOOD_L)
    p.line(24, 49, 25, 49, WOOD_D)
    p.line(17, 51, 25, 51, IRON); p.line(18, 56, 24, 56, IRON)
    p.line(18, 49, 24, 49, H('3a6a8a'))            # water
    p.line(17, 47, 21, 45, IRON_L); p.line(21, 45, 25, 47, IRON_L)  # handle arc
    # cooking pot
    p.px(68, 46, IRON); p.px(68, 47, IRON)
    p.rect(65, 48, 71, 54, IRON_D)
    p.ell(65, 48, 71, 55, IRON_D)
    p.rect(65, 47, 71, 48, IRON)
    p.rect(66, 49, 66, 52, IRON_L)
    p.px(64, 50, IRON_L); p.px(72, 50, IRON_L)
    # frying pan
    p.px(78, 46, IRON); p.px(78, 47, IRON)
    p.ell(74, 48, 82, 55, IRON_D)
    p.ell(75, 49, 81, 53, H('2a2a35'))
    p.line(82, 52, 86, 48, IRON_D)
    p.px(86, 48, IRON_L)
    return fin(im, 0.55)


def a_spare_wheel(style='kayu'):
    im = new(WW, WH)
    w = spare_wheel(style)
    im.alpha_composite(w, (42, Y0 + 59))
    return im


def a_roofcargo():
    im = new(WW, WH); p = PO(im)
    # crate
    p.rect(36, -3, 48, 7, WOOD)
    p.rect(36, -3, 48, -3, WOOD_L)
    p.line(36, 2, 48, 2, WOOD_D)
    p.line(37, -2, 47, 6, WOOD_D); p.line(37, 6, 47, -2, WOOD_D)
    p.rect(36, -3, 37, 7, WOOD_D); p.rect(47, -3, 48, 7, WOOD_D)
    # sack
    p.ell(49, -4, 60, 7, SACK)
    p.rect(52, -5, 57, -3, SACK)
    p.line(51, 1, 51, 5, SACK_L); p.line(58, 2, 58, 6, SACK_D)
    p.line(52, -3, 57, -3, ROPE_D); p.px(55, -4, ROPE)
    p.px(53, -1, SACK_L); p.px(54, -1, SACK_L)
    # bedroll
    p.rect(61, 0, 74, 7, H('c8543f'))
    p.line(61, 0, 74, 0, H('e87c64'))
    for x in range(62, 74, 4):
        p.line(x, 1, x, 7, H('f3e7cf'))
    p.rect(60, 1, 61, 6, H('a63a2f')); p.rect(74, 1, 75, 6, H('a63a2f'))
    p.px(60, 3, H('7a2a24'))
    # rope lashing across
    p.line(37, 6, 74, 0, ROPE); p.line(36, 0, 60, 7, ROPE_D)
    return fin(im, 0.55)


def a_flag(frame):
    im = new(WW, WH); p = PO(im)
    p.line(4, -14, 4, 52, WOOD)
    p.line(5, -14, 5, 52, WOOD_D)
    p.rect(3, -16, 5, -15, BRASS)
    for x in range(6, 21):
        k = x - 6
        yy = int(round(math.sin((k * 0.55) - frame * 2 * math.pi / 8) * (1 + k * 0.12)))
        for y in range(-13, -4):
            c = H('d9453d')
            if y in (-9, -8):
                c = H('f3d36a')
            if k > 10 and (y + (-13)) % 9 == 0 and False:
                c = c
            p.px(x, y + yy, c)
        if k >= 11:   # swallow-tail notch
            for y in range(-9, -7):
                p.px(x, y + yy, (0, 0, 0, 0))
    return fin(im, 0.55)


def b_chimney():
    im = new(WW, WH); p = PO(im)
    p.rect(70, -3, 73, 11, IRON)
    p.line(70, -3, 70, 11, IRON_L)
    p.line(73, -3, 73, 11, IRON_D)
    p.rect(68, -6, 75, -4, IRON_D)
    p.rect(68, -6, 75, -6, IRON_L)
    p.rect(69, -4, 74, -4, IRON)
    p.rect(69, 6, 74, 7, IRON_D)       # collar
    p.px(71, 1, IRON_L); p.px(71, 4, IRON_L)
    return fin(im, 0.55)


def b_smoke(frame):
    im = new(WW, WH); p = PO(im)
    for k in range(3):
        ph = (frame / 8.0 + k / 3.0) % 1.0
        y = -7 - 9 * ph
        x = 71.5 + math.sin((ph + k) * 5.0) * 2.0 + ph * 3
        r = 1 + 2.4 * ph
        a = int(230 * (1 - ph) ** 0.9)
        col = (236, 236, 244, a)
        tmp = new(WW, WH)
        d = ImageDraw.Draw(tmp)
        cx, cy = x, y + Y0
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        im.alpha_composite(tmp)
    return im


def b_awning():
    im = new(WW, WH); p = PO(im)
    red = H('d9453d'); wh = H('f6eedc')
    for x in range(29, 60):
        c = red if ((x - 29) // 3) % 2 == 0 else wh
        top = 25 if x not in (29, 59) else 26
        for y in range(top, 31):
            lvl = 0 if y < 29 else 1
            p.px(x, y, shade(c, lvl))
        # scallop bottom
        sc = 31 if ((x - 29) % 3) != 1 else 32
        for y in range(30, sc + 1):
            p.px(x, y, shade(c, 1))
    p.line(29, 25, 59, 25, shade(wh, -1))
    return fin(im, 0.55)


def b_sign():
    im = new(WW, WH); p = PO(im)
    p.rect(14, 31, 28, 42, WOOD_D)
    p.rect(15, 32, 27, 41, WOOD)
    p.line(15, 32, 27, 32, WOOD_L)
    p.px(14, 30, IRON); p.px(28, 30, IRON)
    p.line(14, 28, 14, 31, IRON_L); p.line(28, 28, 28, 31, IRON_L)
    p.line(14, 28, 28, 28, IRON_D) if False else None
    # coin
    p.ell(18, 33, 24, 40, BRASS)
    p.ell(19, 34, 23, 39, H('d9a238'))
    p.rect(20, 35, 22, 38, BRASS)
    p.px(21, 36, H('a8741c')); p.px(21, 37, H('a8741c'))
    p.px(19, 34, H('fff1a8'))
    return fin(im, 0.55)


def b_steps():
    im = new(WW, WH); p = PO(im)
    for i in range(3):
        y = 53 + i * 4
        p.rect(1 + i, y, 7, y + 1, WOOD_L)
        p.rect(1 + i, y + 2, 7, y + 2, WOOD_D)
    p.line(7, 52, 7, 63, WOOD_D)
    p.line(2, 62, 2, 64, WOOD_D)
    return fin(im, 0.55)


def a_brake():
    im = new(WW, WH); p = PO(im)
    p.line(113, 49, 108, 33, WOOD_D, 2)
    p.line(114, 49, 109, 33, WOOD)
    p.rect(106, 31, 109, 33, IRON)
    p.px(107, 31, IRON_L)
    p.rect(111, 48, 115, 50, IRON_D)
    return fin(im, 0.55)


def a_crate_under():
    """Peti ayam di bawah bak"""
    im = new(WW, WH); p = PO(im)
    p.rect(40, 62, 62, 76, WOOD)
    p.rect(40, 62, 62, 63, WOOD_L)
    for x in range(42, 62, 4):
        p.line(x, 64, x, 75, WOOD_DD)
    p.rect(40, 62, 41, 76, WOOD_D); p.rect(61, 62, 62, 76, WOOD_D)
    p.rect(40, 75, 62, 76, WOOD_D)
    # chicken
    p.ell(46, 66, 55, 73, H('f6eedc'))
    p.ell(53, 64, 57, 68, H('f6eedc'))
    p.px(56, 65, BRASS); p.px(57, 66, H('e0a030'))
    p.px(55, 63, H('d9453d')); p.px(54, 63, H('d9453d'))
    p.px(56, 64, H('1b1116'))
    p.line(47, 69, 51, 71, H('cdbf9f'))
    return fin(im, 0.55)


if __name__ == '__main__':
    pass
