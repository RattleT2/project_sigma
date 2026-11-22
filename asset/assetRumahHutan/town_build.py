from town import *

def pad_roof_rows(rows, x, w=12):
    ys = []
    for xx in range(x, x + w):
        ys.append(min(y for y, (l, r) in rows.items() if l <= xx < r))
    return min(ys), max(ys)

def paste_behind(img, layer):
    px = img.load()
    lp = layer.load()
    for y in range(img.height):
        for x in range(img.width):
            if px[x, y][3] == 0 and lp[x, y][3] > 0:
                px[x, y] = lp[x, y]

def townhouse(sk, name, W=112, floors=2, roof='red', rkind='tile', ground='stone', upper='timber',
              door_dx=0, gwins=(), awn=None, chim=0.28, chim_kind='brick', icon=None, props=(),
              dorm=True, shut=0, seed=1, nb=None, note='', rh_extra=0, door_on=True, uwin_kind='plain', mxr=34, extra=None, chim_up=18):
    rng = random.Random(seed * 13 + {'gurun': 3, 'hutan': 5}.get(sk.key, 0))
    mxl = 24
    gh = 58 if floors == 2 else 68
    uh = 46 if floors == 2 else 0
    rh = int(W * 0.42) + 8 + rh_extra
    topp = 30
    Hh = topp + rh + uh + gh
    Wc = W + mxl + mxr
    img = canvas(Wc, Hh)
    d = ImageDraw.Draw(img)
    x0 = mxl
    x1 = x0 + W
    cx = (x0 + x1) // 2
    gy0 = Hh - gh
    uy0 = gy0 - uh
    eave = (uy0 if floors == 2 else gy0) + 3
    ytop = eave - rh
    pal = sk.roofs[roof]
    j = 3 if (floors == 2 and upper == 'timber') else 0
    # lantai bawah
    if ground == 'stone':
        stone_wall(img, x0, gy0, x1, Hh, sk.stone, rng, sk)
    else:
        timber_wall(img, sk, x0, gy0, x1, Hh - 6, nb or max(2, round(W / 30)), rng)
        stone_wall(img, x0, Hh - 6, x1, Hh, sk.stone, rng, sk)
    # lantai atas
    xs = None
    ux0, ux1 = x0 - j, x1 + j
    if floors == 2:
        if upper == 'timber':
            nbu = nb or max(2, round((ux1 - ux0) / 28))
            xs = timber_wall(img, sk, ux0, uy0, ux1, gy0, nbu, rng)
            rect(d, ux0, gy0 - 1, ux1, gy0 + 3, sk.timber[1])
            rect(d, ux0, gy0 - 1, ux1, gy0, sk.timber[0])
            rect(d, ux0, gy0 + 3, ux1, gy0 + 5, mix(sk.stone[1], H('000000'), 0.35))
        else:
            stone_wall(img, x0, uy0, x1, gy0, sk.stone, rng, sk)
            rect(d, x0 - 2, gy0 - 2, x1 + 2, gy0 + 1, sk.stone[0])
            rect(d, x0 - 2, gy0 + 1, x1 + 2, gy0 + 3, sk.stone[2])
            nbu = nb or max(2, round(W / 28))
            bw = W / nbu
            xs = [x0 + int(round(i * bw)) for i in range(nbu + 1)]
    # atap
    rows = draw_roof(img, sk, pal, x0 - j, x1 + j, eave, ytop, over=8, ridge=6, kind=rkind, rng=rng)
    sk.roof_decor(img, rows, ytop, eave, rng, pal)
    # cerobong (di belakang atap)
    smoke = []
    if chim is not None:
        sign = 1 if chim >= 0 else -1
        xc = cx + int(W * chim) - 6
        top_y, bot_y = pad_roof_rows(rows, xc, 12)
        layer = canvas(Wc, Hh)
        chimney(layer, sk, xc, top_y - chim_up, bot_y + 6, chim_kind, rng)
        paste_behind(img, layer)
        smoke.append(dict(x=xc + 6, y=top_y - chim_up - 4))
    if dorm and rh >= 44:
        dormer(img, sk, cx, ytop + int(rh * 0.5) - 4, pal, rng)
    # jendela atas
    if floors == 2 and xs:
        for i in range(len(xs) - 1):
            wcx = (xs[i] + xs[i + 1]) // 2
            window(img, sk, wcx, uy0 + 9, 12, 16, shut=sk.shutters[(i + shut) % len(sk.shutters)], rng=rng)
    # pintu
    door_x = cx + door_dx - 13
    di = door(img, sk, door_x, Hh) if door_on else None
    for dx, kind in gwins:
        if kind == 'shop':
            shop_window(img, sk, cx + dx, Hh - 18, rng=rng)
        else:
            window(img, sk, cx + dx, Hh - 46, 12, 16, shut=sk.shutters[(abs(dx) + shut) % len(sk.shutters)], rng=rng)
    if awn:
        awning(img, sk, x0 + 3, x1 - 3, Hh - 57, Hh - 51, awn[0], awn[1])
    if extra:
        extra(img, sk, dict(x0=x0, x1=x1, cx=cx, Hh=Hh, gy0=gy0, uy0=uy0, ytop=ytop, eave=eave, rows=rows, rng=rng))
    if icon:
        hang_sign(img, sk, ux1 + 1, Hh - 56, icon)
    for p, dx in props:
        px = cx + dx
        if p == 'barrel': barrel(img, sk, px, Hh)
        elif p == 'crate': crate(img, sk, px, Hh)
        elif p == 'crate2':
            crate(img, sk, px, Hh); crate(img, sk, px + 16, Hh); crate(img, sk, px + 8, Hh - 14)
        elif p == 'sack': sack(img, px, Hh); sack(img, px + 11, Hh, 12, 11)
        elif p == 'hay': hay(img, sk, px, Hh)
        elif p == 'jar': jar(img, sk, px, Hh, 10, 14)
        elif p == 'wood': woodpile(img, sk, px, Hh)
        elif p == 'planter': planter(img, sk, px, Hh)
        elif p == 'lamp': lamp(img, sk, px, Hh - 62)
        elif p == 'banner': banner(img, px, Hh - 70, 14, 26, RED, sk)
        elif p == 'banner2': banner(img, px, Hh - 70, 14, 26, H('3f6fa8'), sk)
    # dekorasi tepi atap dan tanah
    l, r = rows[eave - 1]
    sk.eave_decor(img, l, r, eave, rng)
    sk.ground_fx(img, x0 - 14, x1 + 22, rng, skip=(door_x - 4, door_x + 30))
    return finish(sk, name, img, di, smoke, note)

# ================= daftar rumah =================
# (name, kwargs)
def jobs(sk):
    R = lambda *a: a
    return [
     ('rumah_petani', dict(W=104, floors=1, roof='thatch', rkind='thatch', ground='plaster', door_dx=-18,
                           gwins=((24, 'plain'),), chim=-0.26, chim_kind='stone', icon='wheat', dorm=False,
                           props=(('hay', -66), ('sack', 44)), seed=2, shut=2)),
     ('rumah_warga1', dict(W=92, floors=1, roof='orange', ground='plaster', door_dx=-16, gwins=((24, 'plain'),),
                           chim=0.26, dorm=False, props=(('barrel', -56),), seed=3, shut=1)),
     ('rumah_warga2', dict(W=112, floors=2, roof='red', ground='stone', door_dx=0, gwins=((-34, 'plain'), (34, 'plain')),
                           props=(('crate', -66), ('barrel', 62)), seed=4)),
     ('rumah_warga3', dict(W=136, floors=2, roof='brown', ground='plaster', door_dx=0,
                           gwins=((-48, 'plain'), (-26, 'plain'), (26, 'plain'), (48, 'plain')),
                           props=(('barrel', -78), ('barrel', -64), ('lamp', 34)), seed=5, shut=3)),
     ('rumah_penjaga', dict(W=108, floors=2, roof='slate', ground='stone', upper='stone', door_dx=0,
                            gwins=((-34, 'plain'), (34, 'plain')), icon='shield', chim=0.3, chim_kind='stone',
                            props=(('banner', -62), ('lamp', 36)), seed=6)),
     ('rumah_pustakawan', dict(W=100, floors=2, roof='blue', ground='stone', upper='timber', door_dx=0,
                               gwins=((-32, 'plain'), (32, 'plain')), icon='book', rh_extra=8,
                               props=(('crate', -60), ('lamp', 32)), seed=7, shut=0)),
     ('rumah_pedagang', dict(W=124, floors=2, roof='red', ground='plaster', door_dx=0,
                             gwins=((-40, 'shop'), (40, 'shop')), awn=(RED, CREAM), icon='coin',
                             props=(('crate2', -78), ('barrel', 66)), seed=8, shut=0)),
     ('rumah_tukang_roti', dict(W=112, floors=2, roof='orange', ground='plaster', door_dx=0,
                                gwins=((-36, 'shop'), (36, 'shop')), awn=(H('e8a040'), CREAM), icon='bread',
                                goods=None, props=(('jar', -66), ('sack', 58)), seed=9, shut=4)),
     ('rumah_penebang_kayu', dict(W=104, floors=1, roof='brown', ground='plaster', door_dx=-14,
                                  gwins=((26, 'plain'),), chim=0.26, chim_kind='stone', icon='axe', dorm=False,
                                  props=(('wood', -68), ('wood', 52)), seed=10, shut=1)),
     ('rumah_pemburu', dict(W=104, floors=1, roof='thatch', rkind='thatch', ground='plaster', door_dx=14,
                            gwins=((-28, 'plain'),), chim=-0.26, chim_kind='stone', icon='bow', dorm=False,
                            props=(('sack', -66), ('crate', 52)), seed=11, shut=2)),
     ('kedai', dict(W=148, floors=2, roof='brown', ground='plaster', door_dx=-6,
                    gwins=((-48, 'shop'), (38, 'shop'), (58, 'plain')), awn=(H('3f6fa8'), CREAM), icon='mug',
                    props=(('barrel', -86), ('barrel', -72), ('lamp', 24)), seed=13, shut=1)),
     ('rumah_pencuri', dict(W=96, floors=2, roof='slate', ground='stone', door_dx=16,
                            gwins=((-26, 'plain'),), icon='mask', props=(('crate', -60), ('barrel', 56)), seed=15, shut=3)),
    ]

def build_jobs(sk):
    for n, kw in jobs(sk):
        kw = dict(kw)
        kw.pop('goods', None)
        townhouse(sk, n, **kw)

if __name__ == '__main__':
    for sk in (SNOW, DESERT, FOREST):
        build_jobs(sk)
    print('ok')
