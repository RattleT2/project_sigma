import sys, os, math, random, json
sys.path.insert(0, '/home/claude')
from PIL import Image, ImageDraw
from bio import ICONS

def H(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (255,)

def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3)) + (255,)

def canvas(w, h):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))

def rect(d, x0, y0, x1, y1, c):
    if x1 > x0 and y1 > y0:
        d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=c)

def put(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), c)

def getp(img, x, y):
    if 0 <= x < img.width and 0 <= y < img.height:
        return img.getpixel((x, y))
    return (0, 0, 0, 0)

def outline(img, col):
    px = img.load()
    w, h = img.size
    new = img.copy()
    n = new.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] > 0:
                        n[x, y] = col
                        break
    return new

GOLD = (H('f5c542'), H('c9962a'))
GLOW = (H('ffe9a0'), H('f6b84a'), H('d98a2e'))
RED, CREAM = H('c8463a'), H('f6ecd0')
GRN = (H('6cc24a'), H('3f8a30'))

# ================= KULIT BIOME =================
class Skin:
    cover = None
    key = ''
    label = ''
    def ground_fx(self, img, x0, x1, rng, skip=None): pass
    def roof_decor(self, img, rows, ytop, ybot, rng, pal): pass
    def eave_decor(self, img, l, r, ybot, rng): pass
    def cap(self, img, x0, x1, y): pass
    def box(self, img, x, y, w, rng, col): pass
    def stone_fx(self, img, x0, y0, x1, y1, rng): pass
    def post(self, img, rng): pass

class SnowSkin(Skin):
    key = 'salju'; label = 'Salju'
    cover = H('f6faff')
    OL = H('2a2438')
    timber = (H('7a5844'), H('54382c'), H('33221c'))
    plaster = (H('f6f3ee'), H('e4e1dc'), H('c8cad2'))
    stone = (H('c8ccd8'), H('a2a8ba'), H('7c8398'))
    roofs = dict(red=(H('c4685a'), H('a24c42'), H('7e342c')), blue=(H('6c80c0'), H('5068a8'), H('38508a')),
                 brown=(H('9c6a50'), H('7c5040'), H('5a3a2c')), orange=(H('dc9c48'), H('c08434'), H('96622a')),
                 slate=(H('7c8294'), H('626878'), H('484e5c')), thatch=(H('e6c46c'), H('cfa650'), H('a88436')),
                 teal=(H('5aa6a8'), H('428688'), H('2e6468')), green=(H('5a9068'), H('447452'), H('305840')))
    shutters = [H('4a64b8'), H('b04a4a'), H('4a8a5a'), H('8a4a8a'), H('d08a3a')]
    sky = (160, 196, 228); ground = (236, 244, 252)
    SN = (H('f6faff'), H('dbe8f5'), H('b7cde4'))
    IC = (H('d3ecfa'), H('a9d3ec'), H('7db3d8'))
    def cap(self, img, x0, x1, y):
        d = ImageDraw.Draw(img)
        rect(d, x0, y - 2, x1, y, self.SN[0])
        rect(d, x0, y, x1, y + 1, self.SN[2])
    def ground_fx(self, img, x0, x1, rng, skip=None):
        Hh = img.height
        for x in range(max(0, x0), min(img.width, x1)):
            if skip and skip[0] <= x < skip[1]:
                continue
            h = int(2 + 1.5 * math.sin(x * 0.3) + rng.random() * 1.2)
            for k in range(h):
                put(img, x, Hh - 1 - k, self.SN[2] if k == 0 else self.SN[0] if k == h - 1 else self.SN[1])
    def roof_decor(self, img, rows, ytop, ybot, rng, pal):
        hgt = ybot - ytop
        xs = [r for r in rows.values()]
        xmin = min(l for l, r in xs); xmax = max(r for l, r in xs)
        for x in range(xmin, xmax + 1):
            dep = int(hgt * 0.5 + 4 * math.sin(x * 0.21) + 3 * math.sin(x * 0.53 + 1) + rng.random() * 1.5)
            for y in range(ytop, min(ybot - 3, ytop + dep)):
                l, r = rows[y]
                if l + 1 <= x < r - 1:
                    e = ytop + dep - y
                    put(img, x, y, self.SN[2] if e <= 1 else self.SN[1] if e <= 3 else self.SN[0])
        l, r = rows[ybot - 1]
        for x in range(l, r):
            lip = 2 + int(1.5 + 1.5 * math.sin(x * 0.4))
            for k in range(lip):
                y = ybot - lip + k
                put(img, x, y, self.SN[0] if k < lip - 2 else self.SN[1] if k < lip - 1 else self.SN[2])
    def eave_decor(self, img, l, r, ybot, rng):
        x = l + 3
        while x < r - 3:
            ln = rng.randint(4, 10)
            for k in range(ln):
                c = self.IC[0] if k < ln - 3 else self.IC[1]
                put(img, x, ybot + k, c)
                if k < ln - 3:
                    put(img, x + 1, ybot + k, self.IC[1])
            put(img, x, ybot + ln - 1, self.IC[2])
            x += rng.randint(6, 11)
    def box(self, img, x, y, w, rng, col):
        d = ImageDraw.Draw(img)
        rect(d, x, y, x + w, y + 4, H('5a3a28'))
        rect(d, x, y, x + w, y + 1, H('7a5a40'))
        rect(d, x - 1, y - 3, x + w + 1, y, self.SN[0])
        rect(d, x - 1, y, x + w + 1, y + 1, self.SN[2])
        for i in range(2, w - 2, 5):
            put(img, x + i, y - 4, H('3f7a4a')); put(img, x + i, y - 5, H('3f7a4a'))
            put(img, x + i + 1, y - 4, RED)
    def stone_fx(self, img, x0, y0, x1, y1, rng):
        pass

class DesertSkin(Skin):
    key = 'gurun'; label = 'Gurun'
    OL = H('4a2c28')
    timber = (H('b0703c'), H('8a5230'), H('5e3620'))
    plaster = (H('fbefd0'), H('f0dcae'), H('d8bc86'))
    stone = (H('ecd6a8'), H('cfae7c'), H('a8865a'))
    roofs = dict(red=(H('e08048'), H('c4602e'), H('98441e')), blue=(H('4cc0b4'), H('2ea09c'), H('1e7a7c')),
                 brown=(H('b8805a'), H('966040'), H('6e442c')), orange=(H('eab852'), H('ce9a3a'), H('a27226')),
                 slate=(H('b8a488'), H('978264'), H('6e5c44')), thatch=(H('ecd284'), H('d2b45e'), H('a88e40')),
                 teal=(H('4cc0b4'), H('2ea09c'), H('1e7a7c')), green=(H('76aa68'), H('568a4c'), H('3c6a38')))
    shutters = [H('2fb0a8'), H('c24a3a'), H('e08a2a'), H('3a5a9a'), H('4a8a4a')]
    sky = (150, 205, 230); ground = (244, 226, 176)
    SD = (H('f2dca2'), H('dfbd7c'), H('c79e60'))
    def ground_fx(self, img, x0, x1, rng, skip=None):
        Hh = img.height
        for x in range(max(0, x0), min(img.width, x1)):
            if skip and skip[0] <= x < skip[1]:
                continue
            h = int(2 + 1.5 * math.sin(x * 0.27) + rng.random() * 1.2)
            for k in range(h):
                put(img, x, Hh - 1 - k, self.SD[2] if k == 0 else self.SD[0] if k == h - 1 else self.SD[1])
    def roof_decor(self, img, rows, ytop, ybot, rng, pal):
        for y in range(ytop, ybot - 2):
            l, r = rows[y]
            for x in range(l + 1, r - 1):
                if rng.random() < 0.02 and y < ytop + (ybot - ytop) * 0.6:
                    put(img, x, y, mix(pal[0], H('fff0c8'), 0.5))
    def box(self, img, x, y, w, rng, col):
        d = ImageDraw.Draw(img)
        rect(d, x, y, x + w, y + 4, H('9a5a34'))
        rect(d, x, y, x + w, y + 1, H('c07a48'))
        for i in range(3, w - 2, 7):
            rect(d, x + i, y - 6, x + i + 3, y, H('4f8a3c'))
            rect(d, x + i + 2, y - 6, x + i + 3, y, H('2f5f2c'))
            put(img, x + i + 1, y - 7, RED)
    def stone_fx(self, img, x0, y0, x1, y1, rng):
        for _ in range((x1 - x0) // 4):
            put(img, rng.randint(x0, x1 - 1), rng.randint(y1 - 8, y1 - 1), self.SD[1])

class ForestSkin(Skin):
    key = 'hutan'; label = 'Hutan'
    cover = H('82b04c')
    OL = H('1d2a1c')
    timber = (H('8a6a42'), H('64482c'), H('3e2c1a'))
    plaster = (H('efe8c8'), H('ddd6ae'), H('bfbd90'))
    stone = (H('a8b4a4'), H('84928a'), H('5e6e64'))
    roofs = dict(red=(H('b8604c'), H('9a4a3a'), H('783428')), blue=(H('5a7aa8'), H('486290'), H('364a70')),
                 brown=(H('94694a'), H('7a5638'), H('5c4028')), orange=(H('c88c48'), H('aa7438'), H('86582a')),
                 slate=(H('7a8a8c'), H('5e6c70'), H('444e52')), thatch=(H('d8b868'), H('bc9a4c'), H('94762f')),
                 teal=(H('5a9a90'), H('46796f'), H('335a52')), green=(H('5a8a64'), H('466f50'), H('33543c')))
    shutters = [H('3f8a5a'), H('b04a4a'), H('4a7ab0'), H('8a5a9a'), H('c88a3a')]
    sky = (150, 196, 184); ground = (95, 138, 69)
    MS = (H('a8d062'), H('82b04c'), H('5f8a38'))
    VN = (H('4f8c3e'), H('376a2e'))
    def cap(self, img, x0, x1, y):
        d = ImageDraw.Draw(img)
        for x in range(x0, x1):
            put(img, x, y - 1, self.MS[1]); put(img, x, y - 2, self.MS[0] if x % 3 else self.MS[1])
            put(img, x, y, self.MS[2] if x % 2 else self.MS[1])
    def ground_fx(self, img, x0, x1, rng, skip=None):
        Hh = img.height
        for x in range(max(0, x0), min(img.width, x1)):
            if skip and skip[0] <= x < skip[1]:
                continue
            if rng.random() < 0.6:
                h = rng.randint(2, 5)
                col = rng.choice(self.MS)
                for k in range(h):
                    put(img, x + (rng.choice((-1, 1)) if k >= h - 1 and h > 3 else 0), Hh - 1 - k, col)
            put(img, x, Hh - 1, self.MS[2])
        d = ImageDraw.Draw(img)
        for _ in range(max(1, (x1 - x0) // 50)):
            mx = rng.randint(max(0, x0) + 2, min(img.width, x1) - 8)
            if skip and skip[0] - 6 <= mx < skip[1]:
                continue
            capc = rng.choice((H('c8402e'), H('e0a030')))
            rect(d, mx + 2, Hh - 5, mx + 4, Hh - 1, CREAM)
            rect(d, mx, Hh - 8, mx + 6, Hh - 5, capc)
            put(img, mx + 2, Hh - 7, CREAM); put(img, mx + 4, Hh - 6, CREAM)
    def roof_decor(self, img, rows, ytop, ybot, rng, pal):
        hgt = ybot - ytop
        for x in range(min(l for l, r in rows.values()), max(r for l, r in rows.values())):
            n = math.sin(x * 0.17) + math.sin(x * 0.43 + 2) + rng.random() * 0.6
            dep = int(hgt * 0.16 + n * 5)
            for y in range(ytop, min(ybot - 3, ytop + max(0, dep))):
                l, r = rows[y]
                if l + 1 <= x < r - 1:
                    e = ytop + dep - y
                    put(img, x, y, self.MS[2] if e <= 1 else self.MS[1] if e <= 3 else self.MS[0])
        xmin = min(l for l, r in rows.values()); xmax = max(r for l, r in rows.values())
        for _ in range(5):
            cx_ = rng.randint(xmin + 8, xmax - 8)
            cy_ = rng.randint(ytop + 8, ybot - 8)
            rx_, ry_ = rng.randint(5, 9), rng.randint(2, 3)
            for yy in range(cy_ - ry_, cy_ + ry_ + 1):
                for xx in range(cx_ - rx_, cx_ + rx_ + 1):
                    if ((xx - cx_) / rx_) ** 2 + ((yy - cy_) / ry_) ** 2 <= 1 and yy in rows and rows[yy][0] + 1 <= xx < rows[yy][1] - 1:
                        put(img, xx, yy, self.MS[0] if yy < cy_ else self.MS[1] if (xx + yy) % 3 else self.MS[2])
        l, r = rows[ybot - 1]
        for x in range(l + 1, r - 1):
            if rng.random() < 0.35:
                put(img, x, ybot - 3, self.MS[1]); put(img, x, ybot - 4, self.MS[0]) if rng.random() < 0.5 else None
    def eave_decor(self, img, l, r, ybot, rng):
        x = l + 4
        while x < r - 4:
            ln = rng.randint(3, 9)
            for k in range(ln):
                put(img, x, ybot + k, self.VN[k % 2])
                if k % 3 == 1:
                    put(img, x + 1, ybot + k, self.VN[0])
            x += rng.randint(8, 14)
    def box(self, img, x, y, w, rng, col):
        d = ImageDraw.Draw(img)
        rect(d, x, y, x + w, y + 4, H('5a3a28'))
        rect(d, x, y, x + w, y + 1, H('7a5a40'))
        for i in range(1, w - 1, 3):
            put(img, x + i, y - 1, GRN[1]); put(img, x + i, y - 2, GRN[0])
            if i % 2 == 1:
                put(img, x + i, y - 3, rng.choice((H('f06a8a'), H('f5d84a'), H('ffffff'))))
    def stone_fx(self, img, x0, y0, x1, y1, rng):
        for _ in range((x1 - x0) // 2):
            x = rng.randint(x0, x1 - 1)
            y = rng.randint(y1 - 10, y1 - 1)
            if getp(img, x, y)[3]:
                put(img, x, y, rng.choice(self.MS))
    def post(self, img, rng):
        w, h = img.size
        px = img.load()
        tm = set(self.timber)
        tops = []
        for y in range(1, h):
            for x in range(w):
                if px[x, y] in tm and px[x, y - 1][3] == 0 and rng.random() < 0.8:
                    tops.append((x, y))
        for (x, y) in tops:
            put(img, x, y, rng.choice(self.MS))
            if rng.random() < 0.05:
                for k in range(1, rng.randint(3, 7)):
                    if getp(img, x, y + k) in tm:
                        put(img, x, y + k, self.VN[k % 2])
                    else:
                        break

SNOW, DESERT, FOREST = SnowSkin(), DesertSkin(), ForestSkin()
META = {}

# ================= PRIMITIF BANGUNAN =================
def draw_roof(img, sk, pal, x0, x1, ybot, ytop, over=8, ridge=6, kind='tile', rng=None, tw=6, th=5):
    cx = (x0 + x1) / 2
    hgt = ybot - ytop
    rows = {}
    for y in range(ytop, ybot):
        t = (y + 0.5 - ytop) / hgt
        l = int(round(cx - ridge / 2 - (cx - ridge / 2 - (x0 - over)) * t))
        r = int(round(cx + ridge / 2 + ((x1 + over) - (cx + ridge / 2)) * t))
        rows[y] = (l, r)
        ri = (y - ytop) // th
        yy = (y - ytop) % th
        off = (ri % 2) * (tw // 2)
        for x in range(l, r):
            if kind == 'thatch':
                c = pal[1]
                hsh = (x * 7 + ri * 13) % 7
                if hsh == 0:
                    c = pal[2]
                elif hsh == 3 and yy < 3:
                    c = pal[0]
                if (y - ytop) % 9 == 8:
                    c = pal[2]
            else:
                col = (x + off) // tw
                xx = (x + off) % tw
                hs = (col * 31 + ri * 17) % 5
                base = pal[1]
                if hs == 0:
                    base = mix(pal[1], pal[0], 0.35)
                elif hs == 1:
                    base = mix(pal[1], pal[2], 0.25)
                if yy == th - 1:
                    c = pal[2]
                elif yy == 0:
                    c = mix(base, pal[0], 0.5)
                elif xx == tw - 1:
                    c = mix(base, pal[2], 0.5)
                else:
                    c = base
            img.putpixel((x, y), c)
        put(img, l, y, pal[2]); put(img, r - 1, y, pal[2])
    l, r = rows[ybot - 1]
    d = ImageDraw.Draw(img)
    rect(d, l, ybot - 2, r, ybot, pal[2])
    rect(d, l, ybot - 3, r, ybot - 2, pal[0]) if kind != 'thatch' else None
    if kind == 'thatch' and rng:
        for x in range(l, r):
            ext = rng.randint(0, 3)
            for k in range(ext):
                put(img, x, ybot + k, pal[1] if k < ext - 1 else pal[2])
    return rows

def stone_wall(img, x0, y0, x1, y1, pal, rng, sk=None):
    d = ImageDraw.Draw(img)
    hi, mid, lo = pal
    rect(d, x0, y0, x1, y1, mid)
    y = y0
    r = 0
    while y < y1:
        h = min(7, y1 - y)
        rect(d, x0, y, x1, y + 1, lo)
        x = x0 - (r % 2) * 8
        while x < x1:
            w = rng.choice((14, 16, 18, 20))
            for yy in range(y, y + h):
                put(img, x, yy, lo) if x0 <= x < x1 else None
            xa, xb = max(x0, x + 1), min(x1, x + w)
            tone = rng.random()
            if tone < 0.25:
                rect(d, xa, y + 1, xb, y + h, mix(mid, hi, 0.3))
            elif tone > 0.8:
                rect(d, xa, y + 1, xb, y + h, mix(mid, lo, 0.25))
            rect(d, xa, y + 1, xb, y + 2, mix(mid, hi, 0.6))
            x += w
        y += h
        r += 1
    rect(d, x0, y0, x0 + 1, y1, hi)
    rect(d, x1 - 2, y0, x1, y1, lo)
    if sk:
        sk.stone_fx(img, x0, y0, x1, y1, rng)

def timber_wall(img, sk, x0, y0, x1, y1, nb, rng, braces=True, pal_p=None):
    d = ImageDraw.Draw(img)
    pl = pal_p or sk.plaster
    ti = sk.timber
    rect(d, x0, y0, x1, y1, pl[1])
    for _ in range((x1 - x0) * (y1 - y0) // 60):
        put(img, rng.randint(x0, x1 - 1), rng.randint(y0, y1 - 1), pl[0] if rng.random() < .5 else pl[2])
    bw = (x1 - x0) / nb
    xs = [x0 + int(round(i * bw)) for i in range(nb + 1)]
    if braces:
        for i in range(nb):
            xl, xr = xs[i], xs[i + 1]
            for k in range(2):
                d.line([(xl + 2, y0 + 3 + k), (xr - 3, y1 - 4 - 1 + k)], fill=ti[1])
                d.line([(xr - 3, y0 + 3 + k), (xl + 2, y1 - 4 - 1 + k)], fill=ti[1])
    for i, xp in enumerate(xs):
        xa = x0 if i == 0 else (x1 - 3 if i == nb else xp - 1)
        rect(d, xa, y0, xa + 3, y1, ti[1])
        rect(d, xa, y0, xa + 1, y1, ti[0])
        rect(d, xa + 2, y0, xa + 3, y1, ti[2])
    rect(d, x0, y0, x1, y0 + 3, ti[1])
    rect(d, x0, y0, x1, y0 + 1, ti[0])
    rect(d, x0, y1 - 4, x1, y1, ti[1])
    rect(d, x0, y1 - 4, x1, y1 - 3, ti[0])
    rect(d, x0, y1 - 1, x1, y1, ti[2])
    return xs

def fill_arch(img, x, ytop, ybot, w, colf, pad=0):
    r = w / 2 + pad
    cxm = x + w / 2
    arc_c = ytop + w / 2
    for y in range(ytop - pad, ybot):
        for xx in range(x - pad, x + w + pad):
            if y < arc_c:
                dx = xx + 0.5 - cxm
                ok = dx * dx + (y + 0.5 - arc_c) ** 2 <= r * r
            else:
                ok = True
            if ok:
                put(img, xx, y, colf(xx, y))

def door(img, sk, x, ybot, w=26, h=44, surround=None):
    sp = surround or sk.stone
    ytop = ybot - h
    ti = sk.timber
    wood = (mix(ti[1], H('c89a64'), 0.35), ti[1], ti[2])
    fill_arch(img, x, ytop, ybot, w, lambda a, b: sp[2], pad=4)
    fill_arch(img, x, ytop, ybot, w, lambda a, b: sp[1], pad=3)
    fill_arch(img, x, ytop, ybot, w, lambda a, b: sp[0], pad=2)

    def plank(a, b):
        k = (a - x) % 5
        if a == x:
            return wood[0]
        if k == 4:
            return wood[2]
        if abs((b - ytop) - 16) <= 0 or abs((b - ytop) - 34) <= 0:
            return H('3a3438')
        return wood[1]
    fill_arch(img, x, ytop, ybot, w, plank)
    put(img, x + w - 6, ytop + 26, GOLD[0]); put(img, x + w - 5, ytop + 26, GOLD[0]); put(img, x + w - 6, ytop + 27, GOLD[1])
    d = ImageDraw.Draw(img)
    rect(d, x - 5, ybot - 2, x + w + 5, ybot, sp[0])
    rect(d, x - 5, ybot - 1, x + w + 5, ybot, sp[2])
    put(img, x + w // 2, ytop - 5, sp[2]); put(img, x + w // 2 - 1, ytop - 5, sp[2]); put(img, x + w // 2 + 1, ytop - 5, sp[2])
    return dict(x=x, y=ytop, w=w, h=h, cx=x + w // 2)

def window(img, sk, cx, y, w=12, h=16, shut=None, box=True, rng=None, glow=False, glass=None):
    d = ImageDraw.Draw(img)
    ti = sk.timber
    sh = shut or sk.shutters[0]
    rect(d, cx - w // 2 - 1, y - 1, cx + w // 2 + 1, y + h + 1, ti[2])
    g0, g1 = (GLOW[0], GLOW[1]) if glow else (glass or (H('b8dcec'), H('86b6d4')))
    rect(d, cx - w // 2, y, cx + w // 2, y + h, g1)
    rect(d, cx - w // 2, y, cx + w // 2, y + h // 2, g0)
    rect(d, cx - 1, y, cx + 1, y + h, sk.plaster[0])
    rect(d, cx - w // 2, y + h // 2 - 1, cx + w // 2, y + h // 2 + 1, sk.plaster[0])
    put(img, cx - w // 2 + 1, y + 1, H('ffffff'))
    if shut is not False:
        for sx in (cx - w // 2 - 5, cx + w // 2 + 1):
            rect(d, sx, y - 1, sx + 4, y + h + 1, sh)
            rect(d, sx, y - 1, sx + 1, y + h + 1, mix(sh, H('ffffff'), 0.3))
            rect(d, sx + 3, y - 1, sx + 4, y + h + 1, mix(sh, H('000000'), 0.3))
            for yy in range(y + 2, y + h, 3):
                rect(d, sx + 1, yy, sx + 3, yy + 1, mix(sh, H('000000'), 0.25))
    if box:
        sk.box(img, cx - w // 2 - 3, y + h + 2, w + 6, rng or random.Random(1), sh)

def shop_window(img, sk, cx, ybot, w=22, h=22, goods=None, rng=None):
    d = ImageDraw.Draw(img)
    ti = sk.timber
    y = ybot - h
    rect(d, cx - w // 2 - 2, y - 2, cx + w // 2 + 2, ybot + 1, ti[2])
    rect(d, cx - w // 2, y, cx + w // 2, ybot, GLOW[1])
    rect(d, cx - w // 2, y, cx + w // 2, y + h // 2, GLOW[0])
    rect(d, cx - w // 2, ybot - 8, cx + w // 2, ybot - 6, ti[1])
    cols = goods or [H('e0603a'), H('3aa0e0'), H('e0c03a'), H('6cc24a')]
    for i, c in enumerate(cols):
        gx = cx - w // 2 + 2 + i * (w - 4) // len(cols)
        rect(d, gx, ybot - 12, gx + 3, ybot - 8, c)
        put(img, gx + 1, ybot - 13, mix(c, H('ffffff'), 0.5))
    rect(d, cx - w // 2 - 3, ybot, cx + w // 2 + 3, ybot + 3, ti[1])
    rect(d, cx - w // 2 - 3, ybot, cx + w // 2 + 3, ybot + 1, ti[0])
    rect(d, cx - 1, y, cx + 1, ybot - 8, ti[1])

def awning(img, sk, x0, x1, y0, y1, c1, c2, sw=6):
    d = ImageDraw.Draw(img)
    for x in range(x0, x1):
        idx = (x - x0) // sw
        col = c1 if idx % 2 == 0 else c2
        shade = mix(col, H('000000'), 0.25)
        for y in range(y0, y1):
            put(img, x, y, col)
        rel = (x - x0) % sw - (sw - 1) / 2
        ext = int(3 * math.sqrt(max(0, 1 - (rel / (sw / 2)) ** 2)))
        for y in range(y1, y1 + ext):
            put(img, x, y, col)
        put(img, x, y1 + ext - 1 if ext else y1 - 1, shade)
    rect(d, x0, y0, x1, y0 + 2, mix(c1, H('000000'), 0.2))
    sk.cap(img, x0, x1, y0)

def hang_sign(img, sk, x, y, icon):
    d = ImageDraw.Draw(img)
    rect(d, x, y, x + 15, y + 2, H('2e2a30'))
    rect(d, x, y - 2, x + 2, y + 4, H('2e2a30'))
    rect(d, x + 3, y + 2, x + 4, y + 5, H('2e2a30')); rect(d, x + 12, y + 2, x + 13, y + 5, H('2e2a30'))
    rect(d, x + 1, y + 5, x + 16, y + 19, sk.timber[2])
    rect(d, x + 2, y + 6, x + 15, y + 18, H('d8a050'))
    rect(d, x + 3, y + 7, x + 14, y + 17, H('c08838'))
    ic = ICONS[icon]
    for j, row in enumerate(ic):
        for i, ch in enumerate(row):
            if ch == '#':
                put(img, x + 4 + i, y + 8 + j, H('3a2418'))
            elif ch == 'o':
                put(img, x + 4 + i, y + 8 + j, H('f6e2a8'))
    sk.cap(img, x + 1, x + 16, y + 5)

def chimney(img, sk, x, ytop, ybot, kind, rng):
    d = ImageDraw.Draw(img)
    pal = (H('b0705c'), H('8e5444'), H('6a3c30')) if kind == 'brick' else sk.stone
    if sk.key == 'gurun' and kind == 'brick':
        pal = (H('d8a068'), H('b8804c'), H('8e5c34'))
    rect(d, x, ytop, x + 12, ybot, pal[1])
    rect(d, x, ytop, x + 2, ybot, pal[0])
    rect(d, x + 10, ytop, x + 12, ybot, pal[2])
    for yy in range(ytop + 4, ybot, 4):
        rect(d, x, yy, x + 12, yy + 1, pal[2])
        for xx in range(x + 2 + ((yy // 4) % 2) * 3, x + 12, 6):
            put(img, xx, yy - 2, pal[2])
    rect(d, x - 2, ytop - 3, x + 14, ytop, pal[0])
    rect(d, x - 2, ytop, x + 14, ytop + 1, pal[2])
    sk.cap(img, x - 2, x + 14, ytop - 3)

def dormer(img, sk, cx, y, pal, rng):
    d = ImageDraw.Draw(img)
    rect(d, cx - 8, y, cx + 8, y + 12, sk.plaster[1])
    rect(d, cx - 8, y, cx + 8, y + 1, sk.timber[1])
    rect(d, cx - 7, y + 2, cx + 7, y + 11, sk.timber[2])
    rect(d, cx - 6, y + 3, cx + 6, y + 10, H('86b6d4'))
    rect(d, cx - 6, y + 3, cx + 6, y + 6, H('b8dcec'))
    rect(d, cx - 1, y + 3, cx + 1, y + 10, sk.plaster[0])
    for k in range(6):
        rect(d, cx - 10 + k, y - 1 - k, cx + 10 - k, y - k, pal[1] if k % 2 == 0 else pal[0])
    rect(d, cx - 10, y - 1, cx + 10, y, pal[2])
    sk.cap(img, cx - 4, cx + 4, y - 6)

# ---------- props ----------
def barrel(img, sk, x, yb, w=13, h=17):
    d = ImageDraw.Draw(img)
    ti = sk.timber
    rect(d, x, yb - h, x + w, yb, ti[1])
    rect(d, x, yb - h, x + 2, yb, ti[0])
    rect(d, x + w - 2, yb - h, x + w, yb, ti[2])
    for by in (yb - h + 3, yb - 5):
        rect(d, x, by, x + w, by + 2, H('4a4a52'))
    rect(d, x + 1, yb - h - 1, x + w - 1, yb - h, ti[0])
    sk.cap(img, x, x + w, yb - h)

def crate(img, sk, x, yb, w=16, h=14):
    d = ImageDraw.Draw(img)
    ti = sk.timber
    y0 = yb - h
    rect(d, x, y0, x + w, yb, mix(ti[1], H('c89a64'), 0.3))
    rect(d, x, y0, x + w, y0 + 2, ti[0])
    rect(d, x, yb - 2, x + w, yb, ti[2])
    rect(d, x, y0, x + 2, yb, ti[2]); rect(d, x + w - 2, y0, x + w, yb, ti[2])
    d.line([(x + 2, y0 + 2), (x + w - 3, yb - 3)], fill=ti[2])
    sk.cap(img, x, x + w, y0)

def sack(img, x, yb, w=13, h=13, col=H('dcc596')):
    d = ImageDraw.Draw(img)
    y0 = yb - h
    c2 = mix(col, H('000000'), 0.25)
    d.ellipse([x, y0 + 2, x + w - 1, yb - 1], fill=col)
    rect(d, x + 3, y0, x + w - 3, y0 + 4, col)
    rect(d, x + 4, y0 + 2, x + w - 4, y0 + 3, c2)
    d.arc([x, y0 + 2, x + w - 1, yb - 1], 0, 180, fill=c2)

def hay(img, sk, x, yb, w=22, h=15):
    d = ImageDraw.Draw(img)
    y0 = yb - h
    rect(d, x, y0, x + w, yb, H('cfa23c'))
    rect(d, x, y0, x + w, y0 + 2, H('ecc75a'))
    for xx in range(x + 3, x + w, 4):
        rect(d, xx, y0 + 2, xx + 1, yb - 1, H('9a7424'))
    rect(d, x, y0 + h // 2, x + w, y0 + h // 2 + 1, sk.timber[2])
    sk.cap(img, x, x + w, y0)

def jar(img, sk, x, yb, w=10, h=14, col=None):
    col = col or mix(sk.stone[1], H('c06838'), 0.5)
    d = ImageDraw.Draw(img)
    y0 = yb - h
    for y in range(y0, yb):
        t = (y - y0) / h
        hw = w / 2 * (0.55 + 0.45 * math.sin(math.pi * min(1, t * 1.15 + 0.1)))
        c = x + w / 2
        for xx in range(int(c - hw), int(c + hw) + 1):
            put(img, xx, y, col)
        put(img, int(c - hw), y, mix(col, H('ffffff'), 0.3))
        put(img, int(c + hw), y, mix(col, H('000000'), 0.3))
    rect(d, x + 2, y0, x + w - 2, y0 + 2, mix(col, H('000000'), 0.3))
    sk.cap(img, x + 2, x + w - 2, y0)

def woodpile(img, sk, x, yb, w=24, h=18):
    d = ImageDraw.Draw(img)
    ti = sk.timber
    rect(d, x, yb - h, x + w, yb, ti[2])
    for yy in range(yb - h + 1, yb - 1, 5):
        for xx in range(x + 1, x + w - 4, 5):
            rect(d, xx, yy, xx + 4, yy + 4, ti[1])
            rect(d, xx + 1, yy + 1, xx + 3, yy + 3, ti[0])
            put(img, xx + 2, yy + 2, ti[2])
    sk.cap(img, x - 1, x + w + 1, yb - h)

def lamp(img, sk, x, y):
    d = ImageDraw.Draw(img)
    rect(d, x + 2, y - 4, x + 3, y, H('3a3438'))
    rect(d, x, y, x + 6, y + 8, H('3a3438'))
    rect(d, x + 1, y + 1, x + 5, y + 7, GLOW[1])
    rect(d, x + 2, y + 2, x + 4, y + 5, GLOW[0])

def banner(img, x, y, w, h, col, sk):
    d = ImageDraw.Draw(img)
    d.polygon([(x, y), (x + w, y), (x + w, y + h), (x + w // 2, y + h - 5), (x, y + h)], fill=col)
    rect(d, x, y, x + w, y + 2, sk.timber[2])
    d.ellipse([x + w // 2 - 3, y + 6, x + w // 2 + 3, y + 12], fill=GOLD[0])

def planter(img, sk, x, yb):
    d = ImageDraw.Draw(img)
    rect(d, x, yb - 8, x + 12, yb, sk.timber[1])
    rect(d, x, yb - 8, x + 12, yb - 7, sk.timber[0])
    sk.box(img, x, yb - 8, 12, random.Random(3), RED)

# ---------- penyimpan ----------
def finish(sk, name, img, door_info=None, smoke=None, note='', out=None):
    rng = random.Random(len(name) * 7 + 1)
    sk.post(img, rng)
    img = outline(img, sk.OL)
    full = f'{name}_{sk.key}'
    od = out or f'/home/claude/kota2_{sk.key}'
    os.makedirs(od, exist_ok=True)
    img.save(os.path.join(od, full + '.png'))
    m = dict(file=full + '.png', w=img.width, h=img.height, pivot=[img.width // 2, img.height], note=note)
    if door_info:
        m['pintu'] = door_info
    if smoke:
        m['asap'] = smoke
    META.setdefault(sk.key, {})[full] = m
    return img
