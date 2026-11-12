import math
from pxlib import *

WW, WH = 128, 96
Y0 = 16            # y offset: headroom for roof cargo / flag / smoke
GROUND_Y = Y0 + 79  # = 95, last row of wheels


class PO(P):
    """Painter with offset so that code can use 'local' coordinates (wheel bottom = 79)."""
    def __init__(self, img, ox=0, oy=Y0):
        super().__init__(img)
        self.ox, self.oy = ox, oy

    def px(self, x, y, c): super().px(x + self.ox, y + self.oy, c)
    def rect(self, x0, y0, x1, y1, c): super().rect(x0 + self.ox, y0 + self.oy, x1 + self.ox, y1 + self.oy, c)
    def line(self, x0, y0, x1, y1, c, w=1): super().line(x0 + self.ox, y0 + self.oy, x1 + self.ox, y1 + self.oy, c, w)
    def poly(self, pts, c): super().poly([(x + self.ox, y + self.oy) for x, y in pts], c)
    def ell(self, x0, y0, x1, y1, c): super().ell(x0 + self.ox, y0 + self.oy, x1 + self.ox, y1 + self.oy, c)
    def thick(self, x0, y0, x1, y1, w, c): super().thick(x0 + self.ox, y0 + self.oy, x1 + self.ox, y1 + self.oy, w, c)


# ---------- palette
WOOD_L = H('c9955c'); WOOD = H('a06b3b'); WOOD_D = H('774b2c'); WOOD_DD = H('4f301d')
IRON = H('50525f'); IRON_L = H('858898'); IRON_D = H('353642')
ROPE = H('eadcae'); ROPE_D = H('c2aa72')
BRASS = H('f0c455')

REAR_WHEEL_X, FRONT_WHEEL_X, WHEEL_CY = 22, 84, 66   # local coords (before Y0)


def shade(c, lvl):
    if lvl < 0: return mix(c, (255, 250, 235), 0.28 * -lvl)
    if lvl == 0: return c
    return mix(c, (48, 28, 46), 0.2 * lvl)


# ======================================================================  BODY
def _pole_layer():
    im = new(WW, WH); p = PO(im)
    p.rect(84, 58, 126, 60, WOOD)
    p.line(84, 58, 126, 58, WOOD_L)
    p.line(84, 60, 126, 60, WOOD_D)
    # singletree (palang tarik) at the tip
    p.rect(124, 53, 126, 64, WOOD_D)
    p.line(124, 53, 124, 64, WOOD)
    p.rect(124, 52, 126, 53, IRON); p.rect(124, 64, 126, 65, IRON)
    p.px(127, 58, IRON_L); p.px(127, 59, IRON)       # hook / ring
    # chains
    for i, x in enumerate(range(100, 118, 2)):
        p.px(x, 61 + (i % 2), IRON_L)
    # reach (kayu penghubung) along the bottom
    p.rect(12, 62, 90, 64, WOOD_D)
    p.line(12, 62, 90, 62, WOOD)
    p.pxs([(30, 63), (31, 63), (60, 63), (61, 63)], WOOD_DD)
    return outline(im)


def _front_block(kind):
    """Seat + front box + footboard + backrest (shared by both wagons)."""
    im = new(WW, WH); p = PO(im)
    # front box
    p.rect(94, 44, 108, 61, WOOD)
    p.rect(94, 44, 108, 45, WOOD_L)
    p.line(94, 50, 108, 50, WOOD_D); p.line(94, 56, 108, 56, WOOD_D)
    p.rect(105, 44, 106, 61, IRON); p.px(105, 47, IRON_L); p.px(105, 58, IRON_L)
    p.rect(98, 51, 101, 54, IRON_D); p.px(99, 52, BRASS)          # lock plate
    # seat plank
    p.rect(93, 42, 111, 43, WOOD_L)
    p.line(93, 43, 111, 43, WOOD)
    p.px(111, 42, WOOD_L)
    # backrest (leaning back)
    p.poly([(95, 42), (97, 42), (94, 29), (92, 29)], WOOD)
    p.line(96, 41, 93, 30, WOOD_L)
    p.rect(93, 34, 96, 35, WOOD_D)
    p.rect(92, 29, 95, 29, WOOD_L)
    # footboard + brace
    p.rect(108, 50, 123, 52, WOOD)
    p.line(108, 50, 123, 50, WOOD_L)
    p.line(108, 52, 123, 52, WOOD_D)
    p.line(110, 53, 106, 60, WOOD_D)
    p.pxs([(122, 51), (116, 51)], IRON_L)
    return outline(im)


def body_layer(kind):
    out = new(WW, WH)
    out.alpha_composite(_pole_layer())
    im = new(WW, WH); p = PO(im)
    if kind == 'A':
        # open wagon bed with planks + iron straps (bak kayu bersabuk besi)
        p.rect(6, 46, 92, 61, WOOD)
        for y in (50, 54, 58):
            p.line(6, y, 92, y, WOOD_D)
        p.line(6, 46, 92, 46, WOOD_L); p.line(6, 47, 92, 47, WOOD_L)
        # plank joints
        for (x, y) in [(19, 48), (31, 52), (55, 48), (70, 52), (44, 56), (80, 56), (14, 60), (62, 60), (86, 48), (40, 48), (26, 56)]:
            p.px(x, y, WOOD_DD); p.px(x, y + 1, WOOD_DD)
        for (x, y) in [(10, 49), (23, 53), (48, 49), (66, 53), (76, 57), (34, 57), (88, 53)]:
            p.px(x, y, WOOD_L)
        p.rect(6, 46, 7, 61, WOOD_D)                           # rear end cap
        for x in (14, 38, 62, 86):
            p.rect(x, 46, x + 1, 61, IRON)
            p.line(x, 46, x, 61, IRON_L)
            p.px(x, 48, BRASS); p.px(x, 59, BRASS)
        p.rect(88, 46, 92, 48, IRON_D)
        p.rect(6, 59, 12, 61, IRON); p.px(8, 60, IRON_L)       # rear corner bracket
        p.rect(9, 46, 12, 47, WOOD_D)
    else:
        # skirt of the wooden house-wagon: painted panels with scallop trim
        p.rect(6, 50, 92, 61, WOOD_D)
        p.rect(6, 50, 92, 51, WOOD)
        for x in range(8, 92, 6):
            p.rect(x, 52, x + 3, 59, WOOD)
            p.rect(x, 52, x + 3, 52, WOOD_L)
            p.px(x + 1, 55, WOOD_DD)
        p.line(6, 61, 92, 61, WOOD_DD)
    # chassis / undercarriage visible bottom
    p.rect(6, 61, 92, 62, WOOD_DD)
    out.alpha_composite(outline(im)); out.alpha_composite(im)
    out.alpha_composite(_front_block(kind))
    # drop the second outline's heavy overdraw by re-compositing fills
    fb = new(WW, WH)
    return out


# ======================================================================  CANOPY  (kanopi, wagon A)
def canopy_top(x):
    if x < 14:
        r = 8
        return 6 + r - math.sqrt(max(r * r - (14 - x) ** 2, 0))
    if x > 85:
        r = 7
        return 6 + r - math.sqrt(max(r * r - (x - 85) ** 2, 0))
    hump = (1 + math.cos(2 * math.pi * (x - 9) / 21.0)) / 2
    return 5 + 3.2 * (1 - hump)


def canopy_layer(base, stripe=None, patches=False, rope=ROPE):
    im = new(WW, WH); p = PO(im)
    SAGS = [30, 51, 72]
    for x in range(7, 93):
        t = int(round(canopy_top(x)))
        sag = min(abs(x - s) for s in SAGS)
        for y in range(t, 46):
            col = base
            if stripe and ((x - 7) // 5) % 2 == 0:
                col = stripe
            lvl = 0
            h = y - t
            if h <= 1 and sag > 2:
                lvl = -2 if h == 0 else -1
            elif sag <= 1:
                lvl = 1
            elif sag == 2:
                lvl = 1 if (x + y) % 2 == 0 else 0
            # broad light on hump centres in upper part
            hc = min(abs(x - c) for c in (19, 40, 61, 82))
            if hc <= 3 and h < 22 and lvl == 0:
                lvl = -1
            if y >= 38 and lvl < 1:
                lvl += 1
            if y >= 43:
                lvl = max(lvl, 2)
            if x <= 11:
                lvl = max(lvl, 1)
            if x >= 86:
                lvl = max(lvl, 1)
            p.px(x, y, shade(col, lvl))
    # fold stitches
    for s in SAGS:
        for y in range(11, 40, 4):
            p.px(s + (1 if (y // 4) % 2 else -1), y, shade(base, 2))
    # front opening shading (bagian depan kanopi)
    for y in range(13, 44):
        p.px(90, y, shade(base, 2)); p.px(91, y, shade(base, 2)); p.px(92, y, shade(base, 3))
    p.line(89, 15, 89, 42, shade(base, 2))
    # rope hem + loops at bottom
    p.line(7, 45, 92, 45, rope)
    p.line(7, 46, 92, 46, ROPE_D)
    for x in range(10, 92, 9):
        p.px(x, 44, ROPE_D); p.px(x, 43, ROPE)
    # rear edge cord
    p.line(8, 14, 9, 44, ROPE_D)
    if patches:
        for (x, y, w, h, col) in [(20, 22, 7, 6, H('8aa0c8')), (58, 16, 6, 7, H('c8795a')), (76, 30, 7, 6, H('9fbf88')), (36, 34, 5, 5, H('c8795a'))]:
            p.rect(x, y, x + w - 1, y + h - 1, col)
            p.rect(x, y, x + w - 1, y, shade(col, -1))
            for i in range(x, x + w, 2):
                p.px(i, y + h - 1, shade(col, 2))
            p.px(x, y + 1, shade(col, 2)); p.px(x + w - 1, y + 1, shade(col, 2))
    return outline(im, 0.55, fixed=None), im


def canopy_png(base, stripe=None, patches=False):
    o, im = canopy_layer(base, stripe, patches)
    out = new(WW, WH); out.alpha_composite(o); out.alpha_composite(im)
    return out


def hoops_layer():
    """Wooden bows (rangka kanopi) for the wagon without cloth."""
    im = new(WW, WH); p = PO(im)
    xs = [9, 25, 41, 57, 73, 89]
    for x in xs:
        t = int(round(canopy_top(x))) + 1
        p.line(x, t, x, 45, WOOD)
        p.line(x + 1, t + 1, x + 1, 45, WOOD_D)
        p.px(x, t - 0, WOOD_L)
    # ridge poles (pole memanjang)
    for x in range(9, 90):
        t = int(round(canopy_top(x))) + 1
        p.px(x, t, WOOD_L); p.px(x, t + 1, WOOD_D)
    p.line(9, 28, 89, 28, WOOD_D)
    p.line(9, 29, 89, 29, WOOD)
    # rope lashing
    for x in xs:
        p.px(x - 1, 28, ROPE); p.px(x - 1, 29, ROPE_D)
    p.rect(7, 45, 92, 45, WOOD_L)
    return outline(im, 0.5), im


def hoops_png():
    o, im = hoops_layer()
    out = new(WW, WH); out.alpha_composite(o); out.alpha_composite(im)
    return out


# ======================================================================  CABIN (wagon B: karavan rumah-kayu)
def cabin_layer(wall, trim, roof, accent, glass=H('ffe7a0')):
    im = new(WW, WH); p = PO(im)
    W_L = shade(wall, -1); W_D = shade(wall, 1); W_DD = shade(wall, 2)
    T_L = shade(trim, -1); T_D = shade(trim, 1)
    R_L = shade(roof, -1); R_D = shade(roof, 1); R_DD = shade(roof, 2)
    # walls
    p.rect(8, 22, 91, 50, wall)
    p.rect(8, 22, 91, 24, W_D)                    # shadow under eave
    p.rect(8, 22, 9, 50, W_D); p.rect(90, 22, 91, 50, W_D)
    for x in range(12, 90, 4):                    # vertical boards
        p.line(x, 26, x, 49, W_D)
    p.line(8, 49, 91, 49, W_DD)
    # painted panels
    for (x0, x1) in [(12, 30), (64, 88)]:
        p.rect(x0, 28, x1, 46, trim)
        p.rect(x0 + 1, 29, x1 - 1, 45, wall)
        p.line(x0 + 1, 29, x1 - 1, 29, W_L)
        for x in range(x0 + 3, x1 - 2, 4):
            p.line(x, 31, x, 44, W_D)
    # flower motif on panels
    for (fx, fy) in [(21, 37), (76, 37)]:
        p.px(fx, fy, accent); p.px(fx - 1, fy, BRASS); p.px(fx + 1, fy, BRASS)
        p.px(fx, fy - 1, BRASS); p.px(fx, fy + 1, BRASS)
        p.pxs([(fx - 2, fy + 3), (fx - 1, fy + 2), (fx + 1, fy + 2), (fx + 2, fy + 3)], H('4fa05a'))
    # window with shutters + curtains
    p.rect(33, 27, 55, 44, trim)
    p.rect(35, 29, 53, 42, glass)
    p.rect(35, 29, 53, 30, shade(glass, -1))
    p.line(44, 29, 44, 42, trim); p.line(35, 35, 53, 35, trim)
    p.pxs([(37, 31), (38, 31), (37, 32), (51, 39), (50, 40)], H('ffffff'))
    p.poly([(35, 29), (40, 29), (36, 38), (35, 38)], accent)
    p.poly([(53, 29), (48, 29), (52, 38), (53, 38)], accent)
    p.px(36, 31, shade(accent, -1)); p.px(52, 31, shade(accent, -1))
    p.rect(28, 28, 32, 43, T_D); p.rect(56, 28, 60, 43, T_D)     # shutters
    p.line(29, 29, 29, 42, trim); p.line(31, 29, 31, 42, trim)
    p.line(57, 29, 57, 42, trim); p.line(59, 29, 59, 42, trim)
    # flower box
    p.rect(32, 45, 56, 47, WOOD_D)
    p.line(32, 45, 56, 45, WOOD)
    for x in range(33, 56, 3):
        p.px(x, 44, H('4fa05a')); p.px(x + 1, 43, accent if (x // 3) % 2 else BRASS)
    # eave trim with scallops
    p.rect(6, 22, 93, 24, trim)
    p.line(6, 22, 93, 22, T_L)
    for x in range(7, 93, 4):
        p.rect(x, 25, x + 2, 25, trim); p.px(x + 1, 26, trim)
    # bottom board
    p.rect(8, 47, 91, 50, trim); p.line(8, 47, 91, 47, T_L); p.line(8, 50, 91, 50, T_D)
    # roof (barrel vault, shingled)
    for x in range(3, 97):
        u = (x - 49.5) / 47.0
        t = 22 - 15 * math.sqrt(max(1 - u * u, 0))
        t = int(round(t))
        for y in range(t, 22):
            row = (y - t)
            c = roof
            if (y + x // 3) % 3 == 0:
                c = R_D
            if row <= 1: c = R_L
            if y >= 20: c = R_DD if x % 2 else R_D
            if x <= 5 or x >= 94: c = R_D
            p.px(x, y, c)
    # shingle ticks
    for y in range(12, 21, 3):
        for x in range(5, 94, 6):
            xx = x + (y % 2) * 3
            if im.getpixel((xx, y + Y0))[3]:
                p.px(xx, y, R_DD)
    p.line(48, 7, 51, 7, shade(roof, -2))
    # roof edge boards
    p.line(3, 21, 96, 21, R_DD)
    return im


def cabin_png(wall, trim, roof, accent):
    im = cabin_layer(wall, trim, roof, accent)
    out = new(WW, WH); out.alpha_composite(outline(im)); out.alpha_composite(im)
    return out


# ======================================================================  WHEELS (roda)
def wheel_frame(angle_deg, wood, wood_l, wood_d, rim, rim_l, hub, spokes=12):
    S = 32
    im = new(S, S); p = P(im)
    c = 15
    # felloe ring (kayu) + iron tyre
    p.ell(c - 13, c - 13, c + 13, c + 13, rim)
    p.ell(c - 12, c - 12, c + 12, c + 12, wood)
    p.ell(c - 10, c - 10, c + 10, c + 10, (0, 0, 0, 0))
    # transparent interior carve (ImageDraw ellipse with transparent paints black, so redo via mask)
    return im


def wheel_png(angle_deg, wood, wood_l, wood_d, rim, rim_l, hub, spokes=12):
    S = 32
    c = 15
    im = new(S, S)
    # ring via per-pixel distance (no antialias, crisp)
    px = im.load()
    for y in range(S):
        for x in range(S):
            d = math.hypot(x - c, y - c)
            if d <= 13.4 and d > 12.4:
                px[x, y] = rim
            elif d <= 12.4 and d > 10.3:
                px[x, y] = wood if (x + y) % 5 else wood_d
    p = P(im)
    # spokes
    for i in range(spokes):
        a = math.radians(angle_deg + i * 360.0 / spokes)
        x1, y1 = c + 11 * math.cos(a), c + 11 * math.sin(a)
        x0, y0 = c + 3 * math.cos(a), c + 3 * math.sin(a)
        col = wood_l if math.sin(a) < 0.2 else wood
        p.line(x0, y0, x1, y1, col)
    # rim highlights (iron) top-left
    for y in range(S):
        for x in range(S):
            d = math.hypot(x - c, y - c)
            if 12.4 < d <= 13.4 and (x - c) + (y - c) < -12:
                px[x, y] = rim_l
    # hub
    p.ell(c - 3, c - 3, c + 3, c + 3, wood_d)
    p.ell(c - 2, c - 2, c + 2, c + 2, hub)
    p.px(c - 1, c - 1, wood_l)
    p.px(c, c, rim)
    # outline hub only slightly
    return im


def wheel_sheet(style):
    st = {
        'kayu': dict(wood=H('a8733f'), wood_l=H('d29c5e'), wood_d=H('7a4d2b'), rim=H('3e3f4b'), rim_l=H('8a8d9d'), hub=H('6b4426')),
        'merah': dict(wood=H('c4483f'), wood_l=H('f07a5e'), wood_d=H('8e2a2e'), rim=H('2d2530'), rim_l=H('f2c85b'), hub=H('f2c85b')),
    }[style]
    frames = [wheel_png(f * (30.0 / 8), **st) for f in range(8)]
    # add outline to the dark rim for a crisp edge
    out = []
    for f in frames:
        o = outline(f, 0.6, diag=False)
        out.append(o)
    return out


def spare_wheel(style='kayu'):
    """smaller wheel hung under the bed (roda cadangan), overlay on wagon canvas"""
    f = wheel_sheet(style)[0]
    small = f.resize((20, 20), Image.NEAREST)
    return small


if __name__ == '__main__':
    A = body_layer('A')
    cp = canopy_png(H('efe4c4'))
    out = comp(A, cp)
    whs = wheel_sheet('kayu')
    for cx in (REAR_WHEEL_X, FRONT_WHEEL_X):
        out.alpha_composite(whs[0], (cx - 15, Y0 + WHEEL_CY - 15))
    up(out, 6, (110, 150, 190, 255)).save('/home/claude/work/wA.png')
    B = body_layer('B')
    cb = cabin_png(H('3f8f93'), H('f2e3b8'), H('a63a3a'), H('d85a50'))
    ob = comp(B, cb)
    whs = wheel_sheet('merah')
    for cx in (REAR_WHEEL_X, FRONT_WHEEL_X):
        ob.alpha_composite(whs[0], (cx - 15, Y0 + WHEEL_CY - 15))
    up(ob, 6, (110, 150, 190, 255)).save('/home/claude/work/wB.png')
