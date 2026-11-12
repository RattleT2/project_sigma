from PIL import Image, ImageDraw
import math

def H(s):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)

def new(w, h):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))

def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3)) + (255,)

def darker(c, t=0.35, tint=(28, 14, 24)):
    return mix(c, tint, t)

class P:
    """Pixel painter: no antialiasing, everything snaps to the grid."""
    def __init__(self, img):
        self.im = img
        self.d = ImageDraw.Draw(img)
        self.w, self.h = img.size

    def px(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.im.putpixel((x, y), c)

    def pxs(self, pts, c):
        for x, y in pts:
            self.px(x, y, c)

    def rect(self, x0, y0, x1, y1, c):  # inclusive
        self.d.rectangle([int(x0), int(y0), int(x1), int(y1)], fill=c)

    def line(self, x0, y0, x1, y1, c, w=1):
        self.d.line([(round(x0), round(y0)), (round(x1), round(y1))], fill=c, width=w)

    def poly(self, pts, c):
        self.d.polygon([(round(x), round(y)) for x, y in pts], fill=c)

    def ell(self, x0, y0, x1, y1, c):
        self.d.ellipse([round(x0), round(y0), round(x1), round(y1)], fill=c)

    def thick(self, x0, y0, x1, y1, w, c):
        """Capsule-ish thick segment, pixel-snapped."""
        self.d.line([(round(x0), round(y0)), (round(x1), round(y1))], fill=c, width=w)
        r = w / 2.0
        if w >= 3:
            for (x, y) in ((x0, y0), (x1, y1)):
                self.d.ellipse([round(x - r + .5), round(y - r + .5), round(x + r - .5), round(y + r - .5)], fill=c)


def alpha_mask(img):
    return img.getchannel('A').point(lambda v: 255 if v > 0 else 0)


def outline(img, strength=0.62, fixed=None, skip_above=None, diag=False):
    """Colored outline: outside pixels touching the sprite take a darkened version of the
    neighbouring colour (or a fixed colour). Returns new image (same size)."""
    w, h = img.size
    src = img.load()
    out = img.copy()
    o = out.load()
    nbrs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if diag:
        nbrs += [(1, 1), (-1, 1), (1, -1), (-1, -1)]
    for y in range(h):
        for x in range(w):
            if src[x, y][3] != 0:
                continue
            if skip_above is not None and y < skip_above:
                continue
            for dx, dy in nbrs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3] != 0:
                    c = src[nx, ny]
                    o[x, y] = fixed if fixed else darker(c, strength)
                    break
    return out


def comp(*layers):
    base = layers[0].copy()
    for l in layers[1:]:
        base.alpha_composite(l)
    return base


def shift(img, dx, dy):
    out = new(*img.size)
    out.alpha_composite(img, (dx, dy)) if (dx >= 0 and dy >= 0) else out.paste(img, (dx, dy))
    return out


def sheet(frames):
    w, h = frames[0].size
    s = new(w * len(frames), h)
    for i, f in enumerate(frames):
        s.paste(f, (i * w, 0))
    return s


def up(img, k=4, bg=None):
    r = img.resize((img.width * k, img.height * k), Image.NEAREST)
    if bg:
        b = Image.new('RGBA', r.size, bg)
        b.alpha_composite(r)
        return b
    return r


def checker_bg(size, k=8, c1=(70, 74, 86, 255), c2=(78, 82, 94, 255)):
    im = Image.new('RGBA', size, c1)
    d = ImageDraw.Draw(im)
    for y in range(0, size[1], k):
        for x in range(0, size[0], k):
            if ((x // k) + (y // k)) % 2:
                d.rectangle([x, y, x + k - 1, y + k - 1], fill=c2)
    return im
