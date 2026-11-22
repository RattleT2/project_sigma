import sys, os, math, random, json
sys.path.insert(0, '/home/claude')
import gen_salju as S
import gen_gurun as G
from PIL import Image, ImageDraw

canvas, rect, put, outline = S.canvas, S.rect, S.put, S.outline
H_ = S.H

NAVY = H_('2b2a3a')
HAY = (H_('ecc75a'), H_('cfa23c'), H_('9a7424'))
SACK = (H_('dcc596'), H_('b99d6c'), H_('8a7248'))
PURPLE = (H_('d9a8ff'), H_('a064e0'), H_('6a3aa0'))
GREEN = (H_('b6f07a'), H_('6cc24a'), H_('3f8a30'))

ICONS = {
 'anvil': ["........", ".######.", "#######.", "..####..", "...##...", "..####..", ".######.", "........"],
 'bread': ["........", "..oooo..", ".o####o.", "o######o", "o######o", ".o####o.", "..oooo..", "........"],
 'book': [".######.", "#oooooo#", "#o####o#", "#oooooo#", "#o####o#", "#oooooo#", ".######.", "........"],
 'coin': ["..####..", ".#oooo#.", "#oo##oo#", "#oo##oo#", "#oo##oo#", "#oooooo#", ".#oooo#.", "..####.."],
 'sun': ["#..#..#.", ".#.##.#.", "..####..", "########", "########", "..####..", ".#.##.#.", "#..#..#."],
 'axe': ["..###...", ".####o..", "#####o..", ".###.o..", "....o...", "...o....", "..o.....", ".o......"],
 'bow': [".##.....", "#..#....", "#...#..o", "#....#o.", "#...#.o.", "#..#..o.", ".##...o.", "........"],
 'shield': ["########", "#oooooo#", "#oo##oo#", "#oo##oo#", ".#oooo#.", ".#oooo#.", "..####..", "...##..."],
 'crown': ["#..#..#.", "##.##.##", "########", "#oooooo#", "########", "........", "........", "........"],
 'mug': ["######..", "#oooo###", "#oooo#.#", "#oooo#.#", "#oooo###", "######..", "........", "........"],
 'wheat': ["...#....", "..#o#...", "...#o#..", "..#o#...", "...#o#..", "....#...", "....#...", "....#..."],
 'mask': [".######.", "########", "#o##o###", "########", ".######.", "..####..", "........", "........"],
 'leaf': ["....###.", "..#####.", ".#####o.", "#####o..", "####o...", "##o.....", "#.......", "........"],
 'star': ["...##...", "...##...", "########", ".######.", "..####..", ".##..##.", "##....##", "........"],
 'flask': ["..####..", "...##...", "...##...", "..#oo#..", ".#oooo#.", "#oooooo#", "#oooooo#", ".######."],
 'pick': [".######.", "#......#", "...##...", "...##...", "...##...", "...##...", "...##...", "........"],
 'eye': ["........", ".######.", "#oo##oo#", "#o####o#", "#oo##oo#", ".######.", "........", "........"],
 'box': ["########", "#o#oo#o#", "#oo##oo#", "########", "#oo##oo#", "#o#oo#o#", "########", "........"],
}

def icon(img, x, y, name, c1, c2):
    for j, row in enumerate(ICONS[name]):
        for i, ch in enumerate(row):
            if ch == '#':
                put(img, x + i, y + j, c1)
            elif ch == 'o':
                put(img, x + i, y + j, c2)

# ================= BIOME =================
class Snow:
    key = 'salju'
    label = 'Salju'
    OL = S.OL
    W = (S.W0, S.W1, S.W2, S.W3)
    GROUND = (H_('e4eef8'), S.SN0)
    SKY = (150, 190, 225)
    def compose(self, img, x0, x1, H, bh, topH, kind, rng):
        d = ImageDraw.Draw(img)
        wy = H - bh
        S.log_wall(img, x0, wy, x1, H - 6, rng)
        S.corner_post(img, x0 - 2, wy, H - 6)
        S.corner_post(img, x1 - 4, wy, H - 6)
        S.stone_base(img, x0 - 2, x1 + 2, H - 6, H, rng)
        rect(d, x0 - 2, wy + 4, x1 + 2, wy + 8, S.W3)
        w = x1 - x0
        inset = {'gable': .22, 'wide': .14, 'steep': .36, 'flat': .2, 'merlon': .14}[kind] * w
        if topH > 0:
            S.snow_roof(img, x0, x1, wy + 4, wy + 4 - topH, int(inset), 10, rng)
        return dict(use_y0=wy + 16, roof_top=wy + 4 - topH)
    def door(self, img, x, H):
        return S.door(img, x, H)
    def win(self, img, cx, y):
        S.window(img, cx - 6, y, 12, 14)
    def ground(self, img, x0, x1, rng, skip=None):
        S.drift(img, max(0, x0), min(img.width, x1), rng, skip)
    def cap(self, img, x0, x1, y):
        d = ImageDraw.Draw(img)
        rect(d, x0, y - 2, x1, y, S.SN0)
        rect(d, x0, y, x1, y + 1, S.SN2)
    def chimney(self, img, x, ytop, ybot, rng):
        S.chimney(img, x, ytop, ybot, rng)
    def barrel(self, img, x, H, w=14, h=18):
        S.barrel(img, x, H - h, w, h)
    def wood_pile(self, img, x, H, w=26, h=22, rng=None):
        S.firewood(img, x, H - h, w, h, rng or random.Random(1))
    def tower_body(self, img, x0, y0, x1, y1, rng):
        stone_body(img, x0, y0, x1, y1, rng, (S.ST0, S.ST1, S.ST2))
    def wall_col(self):
        return (S.W1, S.W0, S.W2)

class Desert:
    key = 'gurun'
    label = 'Gurun'
    OL = G.OL
    W = (G.WD0, G.WD1, G.WD2, G.WD3)
    GROUND = (H_('f3dfa6'), G.SD0)
    SKY = (150, 205, 230)
    def compose(self, img, x0, x1, H, bh, topH, kind, rng):
        wy = H - bh
        w = x1 - x0
        rt = wy - 8
        if topH > 0:
            if kind == 'steep':
                cx = (x0 + x1) // 2
                rx = min(w // 2 - 6, int(topH * 1.15))
                G.dome(img, cx, wy - 6, rx, topH, G.CLAY, seed=3)
                d = ImageDraw.Draw(img)
                rect(d, cx - 1, wy - 6 - topH - 8, cx + 1, wy - 6 - topH + 4, G.C3)
                d.ellipse([cx - 4, wy - 6 - topH - 14, cx + 4, wy - 6 - topH - 6], fill=G.T1)
                rt = wy - 6 - topH - 14
            elif kind in ('gable', 'wide'):
                if kind == 'wide':
                    ux0, ux1 = x0 + int(w * .2), x0 + int(w * .8)
                else:
                    ux0, ux1 = x0 + int(w * .38), x1 - 12
                G.mud_wall(img, ux0, wy - topH, ux1, wy, rng)
                G.parapet(img, ux0, ux1, wy - topH, rng, vigas=False)
                if topH >= 36:
                    G.arch_window(img, (ux0 + ux1) // 2 - 5, wy - topH + 16, 10, 14)
                rt = wy - topH
            elif kind == 'merlon':
                G.merlons(img, x0, x1, wy - 16, 8, 16, 10, 3)
                rt = wy - 16
        G.mud_wall(img, x0, wy, x1, H, rng)
        G.parapet(img, x0, x1, wy - 8, rng)
        G.tile_band(img, x0, x1, wy + 14, 3)
        return dict(use_y0=wy + 20, roof_top=rt)
    def door(self, img, x, H):
        return G.arch_door(img, x, H)
    def win(self, img, cx, y):
        G.arch_window(img, cx - 5, y, 10, 14)
    def ground(self, img, x0, x1, rng, skip=None):
        G.sand(img, max(0, x0), min(img.width, x1), rng, skip)
    def cap(self, img, x0, x1, y):
        pass
    def chimney(self, img, x, ytop, ybot, rng):
        G.mud_wall(img, x, ytop, x + 14, ybot, rng, sides=False)
        d = ImageDraw.Draw(img)
        rect(d, x - 2, ytop - 5, x + 16, ytop, G.C0)
        rect(d, x - 2, ytop, x + 16, ytop + 2, G.C3)
    def barrel(self, img, x, H, w=14, h=18):
        G.jar(img, x, H, w - 2, h)
    def wood_pile(self, img, x, H, w=26, h=22, rng=None):
        d = ImageDraw.Draw(img)
        y = H - h
        rect(d, x, y, x + w, H, G.WD3)
        for yy in range(y + 1, H - 1, 5):
            for xx in range(x + 1, x + w - 4, 5):
                rect(d, xx, yy, xx + 4, yy + 4, G.WD1)
                rect(d, xx + 1, yy + 1, xx + 3, yy + 3, G.WD0)
    def tower_body(self, img, x0, y0, x1, y1, rng):
        G.mud_wall(img, x0, y0, x1, y1, rng)
    def wall_col(self):
        return (G.C1, G.C0, G.C2)

SNOW, DESERT = Snow(), Desert()

def stone_body(img, x0, y0, x1, y1, rng, pal):
    d = ImageDraw.Draw(img)
    rect(d, x0, y0, x1, y1, pal[1])
    y = y0
    r = 0
    while y < y1:
        rect(d, x0, y, x1, y + 1, pal[2])
        x = x0 + (r % 2) * 7
        while x < x1:
            rect(d, x, y, x + 1, min(y + 7, y1), pal[2])
            if rng.random() < 0.25:
                rect(d, x + 2, y + 2, x + 8, y + 3, pal[0])
            x += 14
        y += 7
        r += 1
    rect(d, x0, y0, x0 + 2, y1, pal[0])
    rect(d, x1 - 3, y0, x1, y1, pal[2])

# ================= PROPS =================
def sack(img, x, ybot, w=14, h=14, col=SACK):
    d = ImageDraw.Draw(img)
    y0 = ybot - h
    d.ellipse([x, y0 + 2, x + w - 1, ybot - 1], fill=col[1])
    rect(d, x + 3, y0, x + w - 3, y0 + 4, col[1])
    d.ellipse([x + 2, y0 + 3, x + w // 2, y0 + h // 2 + 2], fill=col[0])
    rect(d, x + 4, y0 + 2, x + w - 4, y0 + 3, col[2])
    d.arc([x, y0 + 2, x + w - 1, ybot - 1], 0, 180, fill=col[2])

def crate(B, img, x, ybot, w=18, h=16, cap=False):
    d = ImageDraw.Draw(img)
    y0 = ybot - h
    W = B.W
    rect(d, x, y0, x + w, ybot, W[1])
    rect(d, x, y0, x + w, y0 + 2, W[0])
    rect(d, x, ybot - 2, x + w, ybot, W[2])
    rect(d, x, y0, x + 2, ybot, W[2])
    rect(d, x + w - 2, y0, x + w, ybot, W[2])
    d.line([(x + 2, y0 + 2), (x + w - 3, ybot - 3)], fill=W[2])
    d.line([(x + w - 3, y0 + 2), (x + 2, ybot - 3)], fill=W[2])
    if cap:
        B.cap(img, x - 1, x + w + 1, y0)

def bale(B, img, x, ybot, w=24, h=16):
    d = ImageDraw.Draw(img)
    y0 = ybot - h
    rect(d, x, y0, x + w, ybot, HAY[1])
    rect(d, x, y0, x + w, y0 + 2, HAY[0])
    for xx in range(x + 3, x + w, 4):
        rect(d, xx, y0 + 2, xx + 1, ybot - 1, HAY[2])
    rect(d, x, y0 + h // 3, x + w, y0 + h // 3 + 1, B.W[2])
    rect(d, x, y0 + 2 * h // 3, x + w, y0 + 2 * h // 3 + 1, B.W[2])
    B.cap(img, x, x + w, y0)

def anvil(B, img, x, ybot):
    d = ImageDraw.Draw(img)
    rect(d, x + 4, ybot - 12, x + 12, ybot, B.W[1])
    rect(d, x + 4, ybot - 12, x + 5, ybot, B.W[0])
    rect(d, x, ybot - 18, x + 16, ybot - 12, S.IRON)
    rect(d, x, ybot - 18, x + 16, ybot - 17, S.ST0)
    rect(d, x - 3, ybot - 16, x, ybot - 14, S.IRON)

def stump_axe(B, img, x, ybot):
    d = ImageDraw.Draw(img)
    rect(d, x, ybot - 12, x + 14, ybot, B.W[1])
    rect(d, x, ybot - 12, x + 14, ybot - 10, B.W[0])
    rect(d, x, ybot - 10, x + 2, ybot, B.W[0])
    rect(d, x + 12, ybot - 10, x + 14, ybot, B.W[2])
    rect(d, x + 7, ybot - 24, x + 9, ybot - 12, B.W[2])
    d.polygon([(x + 3, ybot - 26), (x + 9, ybot - 26), (x + 9, ybot - 18), (x + 3, ybot - 20)], fill=S.ST0)
    B.cap(img, x, x + 14, ybot - 12)

def pelts(B, img, x, y):
    d = ImageDraw.Draw(img)
    rect(d, x, y, x + 30, y + 2, B.W[2])
    for i, (c1, c2) in enumerate(((H_('b88a5a'), H_('8a6238')), (H_('e8e0d0'), H_('b8ad98')), (H_('9a7248'), H_('6e4e2c')))):
        px = x + 2 + i * 10
        d.polygon([(px, y + 2), (px + 8, y + 2), (px + 8, y + 16), (px + 4, y + 20), (px, y + 16)], fill=c1)
        rect(d, px + 5, y + 4, px + 8, y + 15, c2)
        put(img, px + 2, y + 8, c2)

def antlers(B, img, cx, y):
    d = ImageDraw.Draw(img)
    c = H_('d8c8a0')
    for sgn in (-1, 1):
        d.line([(cx + sgn * 2, y + 8), (cx + sgn * 8, y + 2), (cx + sgn * 10, y - 6)], fill=c, width=2)
        d.line([(cx + sgn * 8, y + 2), (cx + sgn * 14, y)], fill=c, width=1)
        d.line([(cx + sgn * 9, y - 3), (cx + sgn * 13, y - 8)], fill=c, width=1)
    rect(d, cx - 4, y + 7, cx + 4, y + 11, H_('b8a880'))

def weapon_rack(B, img, x, ybot):
    d = ImageDraw.Draw(img)
    rect(d, x, ybot - 24, x + 30, ybot - 22, B.W[2])
    rect(d, x, ybot - 24, x + 2, ybot, B.W[2])
    rect(d, x + 28, ybot - 24, x + 30, ybot, B.W[2])
    rect(d, x, ybot - 10, x + 30, ybot - 8, B.W[2])
    for i, px in enumerate((x + 6, x + 12, x + 18, x + 24)):
        rect(d, px, ybot - 34, px + 1, ybot - 2, B.W[1])
        d.polygon([(px - 1, ybot - 34), (px + 2, ybot - 34), (px, ybot - 40)], fill=S.ST0)

def flag_pole(B, img, x, ytop, col=G.RD0):
    d = ImageDraw.Draw(img)
    rect(d, x, ytop - 22, x + 2, ytop + 4, B.W[1])
    d.polygon([(x + 2, ytop - 22), (x + 16, ytop - 18), (x + 2, ytop - 13)], fill=col)

def lantern(B, img, x, y):
    d = ImageDraw.Draw(img)
    rect(d, x + 2, y - 4, x + 3, y, S.IRON)
    rect(d, x, y, x + 6, y + 8, S.IRON)
    rect(d, x + 1, y + 1, x + 5, y + 7, S.GL1)
    rect(d, x + 2, y + 2, x + 4, y + 5, S.GL0)

def cactus(B, img, x, ybot, h=24):
    d = ImageDraw.Draw(img)
    c, c2 = G.GRN0, G.GRN1
    rect(d, x + 4, ybot - h, x + 10, ybot, c)
    rect(d, x + 8, ybot - h, x + 10, ybot, c2)
    rect(d, x, ybot - h + 8, x + 4, ybot - h + 10, c)
    rect(d, x, ybot - h + 4, x + 2, ybot - h + 10, c)
    rect(d, x + 10, ybot - h + 12, x + 14, ybot - h + 14, c)
    rect(d, x + 12, ybot - h + 7, x + 14, ybot - h + 14, c2)
    put(img, x + 6, ybot - h - 1, G.RD0)

def herbs(B, img, x, y):
    d = ImageDraw.Draw(img)
    rect(d, x, y, x + 36, y + 2, B.W[2])
    for i in range(5):
        px = x + 3 + i * 7
        rect(d, px, y + 2, px + 1, y + 6, B.W[2])
        d.polygon([(px - 2, y + 6), (px + 3, y + 6), (px + 1, y + 16)], fill=GREEN[(i % 2) + 1])
        put(img, px, y + 10, GREEN[0])

def counterwin(B, img, x, y):
    d = ImageDraw.Draw(img)
    rect(d, x - 2, y - 2, x + 36, y + 24, B.W[3])
    rect(d, x, y, x + 34, y + 20, S.GL1)
    rect(d, x, y, x + 34, y + 8, S.GL0)
    for bx in range(x + 4, x + 34, 7):
        rect(d, bx, y, bx + 1, y + 20, S.IRON)
    rect(d, x - 4, y + 20, x + 38, y + 24, B.W[1])
    rect(d, x - 4, y + 20, x + 38, y + 21, B.W[0])
    icon(d._image, x + 13, y + 4, 'coin', G.GO0, G.GO1) if False else None

def bigdoor(B, img, x, ybot):
    d = ImageDraw.Draw(img)
    w, h = 44, 58
    y0 = ybot - h
    rect(d, x - 3, y0 - 3, x + w + 3, ybot, B.W[3])
    rect(d, x, y0, x + w, ybot, B.W[1])
    for px in range(x + 11, x + w, 11):
        rect(d, px, y0, px + 1, ybot, B.W[2])
    rect(d, x + w // 2 - 1, y0, x + w // 2 + 1, ybot, B.W[3])
    for by in (y0 + 10, ybot - 14):
        rect(d, x, by, x + w, by + 3, S.IRON)
    d.line([(x + 2, y0 + 2), (x + w // 2 - 3, ybot - 3)], fill=B.W[2])
    d.line([(x + w - 3, y0 + 2), (x + w // 2 + 2, ybot - 3)], fill=B.W[2])
    B.cap(img, x - 3, x + w + 3, y0 - 3)

def signpost(B, c, dx, name):
    img = c['img']
    x = c['cx'] + dx
    H = c['H']
    d = ImageDraw.Draw(img)
    rect(d, x, H - 40, x + 3, H, B.W[2])
    rect(d, x, H - 40, x + 1, H, B.W[0])
    rect(d, x - 10, H - 48, x + 14, H - 30, B.W[3])
    rect(d, x - 9, H - 47, x + 13, H - 31, NAVY)
    icon(img, x - 5, H - 44, name, G.GO0, G.GO1)
    B.cap(img, x - 10, x + 14, H - 48)

# ================= HOUSE BUILDER =================
PRE = {'chimney'}

def house(B, name, bw, bh, topH, kind, wins=(), icon_name=None, props=(), dcx=0, seed=0, mx=18, win2=(),
          dpad=0, meta_note='', door_on=True, sign_dx=None, out=None, wins_y=None):
    pad = 30 if kind != 'steep' or B is SNOW else 40
    H = bh + topH + pad
    W = bw + 2 * mx
    img = canvas(W, H)
    rng = random.Random(seed + (1 if B is DESERT else 0) * 100)
    x0, x1 = mx, mx + bw
    cx = W // 2
    ctx = dict(img=img, cx=cx, H=H, x0=x0, x1=x1, B=B, rng=rng, bh=bh)
    smoke = []
    for p, dx in props:
        if p == 'chimney':
            ytop = H - bh - topH - 12
            B.chimney(img, cx + dx - 8, ytop, H - bh - topH + 28, rng)
            smoke.append(dict(x=cx + dx - 4, y=ytop - 12))
    info = B.compose(img, x0, x1, H, bh, topH, kind, rng)
    ctx.update(info)
    use = info['use_y0']
    door_x = cx + dcx - 13
    di = B.door(img, door_x, H) if door_on else None
    ctx['door_x'] = door_x
    wy = wins_y if wins_y is not None else max(use, H - 46)
    for wdx in wins:
        B.win(img, cx + wdx, wy)
    for wdx in win2:
        B.win(img, cx + wdx, max(use, H - bh + 20) - 0 if False else use)
    for p, dx in props:
        if p in PRE:
            continue
        fn = PROPS.get(p)
        if fn:
            fn(B, ctx, dx)
    if icon_name:
        sd = sign_dx if sign_dx is not None else (dcx + 34)
        signpost(B, ctx, sd, icon_name)
    B.ground(img, x0 - 10, x1 + 10, rng, skip=(door_x - 2, door_x + 28))
    return finish(B, name, img, di, smoke, meta_note, out)

def finish(B, name, img, door_info=None, smoke=None, note='', out=None):
    img = outline(img, B.OL)
    full = f'{name}_{B.key}'
    od = out or os.path.join('/home/claude', 'kota_' + B.key)
    os.makedirs(od, exist_ok=True)
    img.save(os.path.join(od, full + '.png'))
    m = dict(file=full + '.png', w=img.width, h=img.height, pivot=[img.width // 2, img.height], note=note)
    if door_info:
        m['pintu'] = door_info
    if smoke:
        m['asap'] = smoke
    META.setdefault(B.key, {})[full] = m
    return img

META = {}

# prop adapter: (B, ctx, dx)
def _hay(B, c, dx): bale(B, c['img'], c['cx'] + dx, c['H'])
def _crate(B, c, dx):
    crate(B, c['img'], c['cx'] + dx, c['H'], cap=True)
def _crate2(B, c, dx):
    x = c['cx'] + dx
    crate(B, c['img'], x, c['H'])
    crate(B, c['img'], x + 18, c['H'])
    crate(B, c['img'], x + 9, c['H'] - 16, cap=True)
def _barrel(B, c, dx): B.barrel(c['img'], c['cx'] + dx, c['H'])
def _wood(B, c, dx): B.wood_pile(c['img'], c['cx'] + dx, c['H'], rng=c['rng'])
def _anvil(B, c, dx): anvil(B, c['img'], c['cx'] + dx, c['H'])
def _stump(B, c, dx): stump_axe(B, c['img'], c['cx'] + dx, c['H'])
def _pelts(B, c, dx): pelts(B, c['img'], c['cx'] + dx, c['H'] - 62)
def _antlers(B, c, dx): antlers(B, c['img'], c['door_x'] + 13 + dx, c['H'] - 66)
def _rack(B, c, dx): weapon_rack(B, c['img'], c['cx'] + dx, c['H'])
def _flag(B, c, dx): flag_pole(B, c['img'], c['cx'] + dx, c['roof_top'])
def _flag2(B, c, dx): flag_pole(B, c['img'], c['cx'] + dx, c['roof_top'] + 6, G.T1)
def _torch(B, c, dx): S.torch(c['img'], c['cx'] + dx, c['H'] - 34)
def _lantern(B, c, dx): lantern(B, c['img'], c['door_x'] + 13 + dx, c['H'] - 58)
def _awning(B, c, dx):
    x = c['door_x']
    G.awning(c['img'], x - 14 + dx, x + 40 + dx, c['H'] - 58, c['H'] - 52)
    B.cap(c['img'], x - 14 + dx, x + 40 + dx, c['H'] - 59)
def _sack(B, c, dx):
    x = c['cx'] + dx
    sack(c['img'], x, c['H'])
    sack(c['img'], x + 12, c['H'], 12, 11)
def _cactus(B, c, dx): cactus(B, c['img'], c['cx'] + dx, c['H'])
def _herbs(B, c, dx): herbs(B, c['img'], c['cx'] + dx, c['H'] - 62)
def _counter(B, c, dx): counterwin(B, c['img'], c['cx'] + dx, c['H'] - 56)
def _bigdoor(B, c, dx): bigdoor(B, c['img'], c['cx'] + dx, c['H'])
def _banner(B, c, dx): G.banner(c['img'], c['cx'] + dx, c['H'] - 62, 14, 24)
def _jar(B, c, dx): G.jar(c['img'], c['cx'] + dx, c['H'], 11, 16)
def _sunfinial(B, c, dx):
    img = c['img']
    d = ImageDraw.Draw(img)
    x = c['cx'] + dx
    y = c['roof_top']
    rect(d, x - 1, y - 18, x + 1, y + 2, G.GO1)
    rect(d, x - 5, y - 13, x + 5, y - 11, G.GO1)
    rect(d, x - 5, y - 13, x + 5, y - 12, G.GO0)
def _mask(B, c, dx):
    pass

PROPS = dict(hay=_hay, crate=_crate, crate2=_crate2, barrel=_barrel, wood=_wood, anvil=_anvil, stump=_stump,
             pelts=_pelts, antlers=_antlers, rack=_rack, flag=_flag, flag2=_flag2, torch=_torch,
             lantern=_lantern, awning=_awning, sack=_sack, cactus=_cactus, herbs=_herbs, counter=_counter,
             bigdoor=_bigdoor, banner=_banner, jar=_jar, sunfinial=_sunfinial)
