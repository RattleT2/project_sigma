from bio import *

# (nama, bw, bh, topH, kind, wins, icon, props, dcx, kwargs)
JOBS = [
 ('rumah_petani', 150, 72, 48, 'wide', (-48, 48), 'wheat', [('hay', -70), ('hay', 52), ('sack', -52)], -6, {}),
 ('rumah_warga1', 96, 66, 44, 'gable', (-30,), None, [('barrel', 24)], 0, {}),
 ('rumah_warga2', 124, 70, 48, 'wide', (-40, 40), None, [('jar', -44), ('crate', 38)], 0, {}),
 ('rumah_warga3', 104, 104, 44, 'gable', (-34, 34), None, [('barrel', -50)], 0, dict(win2=(-34, 34))),
 ('rumah_penjaga', 112, 76, 44, 'merlon', (-38, 38), 'shield', [('flag', 40), ('torch', -42), ('rack', 36)], 0, {}),
 ('rumah_pandai_besi', 140, 72, 46, 'wide', (-46,), 'anvil', [('chimney', 38), ('anvil', 44), ('wood', -62)], -8, {}),
 ('rumah_pustakawan', 116, 106, 50, 'steep', (-36, 36), 'book', [('flag2', 0)], 0, dict(win2=(-36, 36))),
 ('rumah_pedagang', 150, 72, 46, 'wide', (-50, 50), 'coin', [('awning', 0), ('crate2', -64), ('sack', 56)], 0, {}),
 ('rumah_pendeta', 124, 84, 62, 'steep', (-38, 38), 'sun', [('sunfinial', 0), ('lantern', 36)], 0, {}),
 ('rumah_tukang_roti', 112, 70, 46, 'gable', (-36,), 'bread', [('chimney', 28), ('sack', -50), ('awning', 0)], 0, {}),
 ('rumah_penebang_kayu', 120, 66, 44, 'gable', (36,), 'axe', [('wood', -56), ('stump', 52)], 0, {}),
 ('rumah_pemburu', 112, 68, 44, 'wide', (-36, 36), 'bow', [('pelts', -42), ('antlers', 0)], 0, {}),
 ('rumah_bangsawan', 196, 104, 56, 'wide', (-70, -34, 34, 70), 'crown', [('chimney', -50), ('chimney', 50), ('banner', -86), ('banner', 72), ('flag', 0)], 0, dict(win2=(-70, -34, 34, 70))),
 ('kedai', 176, 84, 52, 'wide', (-56, 56), 'mug', [('barrel', -78), ('barrel', -62), ('lantern', 40), ('chimney', 56), ('crate', 70)], -6, {}),
 ('barak', 210, 70, 38, 'merlon', (-80, -50, 50, 80), 'shield', [('flag', -84), ('flag', 84), ('rack', -30), ('torch', 36)], 4, {}),
 ('rumah_pencuri', 100, 66, 42, 'gable', (-32,), 'mask', [('crate', 32), ('barrel', -46)], 12, {}),
]

def build_jobs(B):
    for i, (n, bw, bh, th, kind, wins, ic, props, dcx, kw) in enumerate(JOBS):
        house(B, n, bw, bh, th, kind, wins=wins, icon_name=ic, props=props, dcx=dcx, seed=i * 7 + 3, **kw)

if __name__ == '__main__':
    build_jobs(SNOW)
    build_jobs(DESERT)
    print('ok')
