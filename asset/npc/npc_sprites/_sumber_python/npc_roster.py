from npc_rig import Npc, H

SK = dict(pucat=H('f5d0b0'), terang=H('f0b98d'), sawo=H('e9b08a'), zaitun=H('c99a6a'), coklat=H('a8683a'), gelap=H('7a4a2e'))

R = {}
def add(key, label, jobs, **kw):
    R[key] = dict(npc=Npc(key, **kw), label=label, jobs=jobs)

add('petani_pria', 'Petani (laki-laki)', ['cangkul', 'tanam'], hf=0.95, skin=SK['sawo'], hair='short', hair_c=H('6a4528'), top='tunic',
    top_c=H('a9835a'), trim_c=H('e8d8a0'), pants_c=H('6b5a48'), boots_c=H('4b2f20'), hat='straw', hat_c=H('e2c470'), stache=True, pouch=True)
add('petani_wanita', 'Petani (perempuan)', ['menabur', 'memanen'], hf=0.92, wf=0.95, skin=SK['zaitun'], hair='braid', hair_c=H('4a2e1e'), top='dress',
    top_c=H('6f9a58'), trim_c=H('f3ead8'), apron_c=H('efe4c4'), hat='headscarf', hat_c=H('d9584c'), blush=True, boots_c=H('5a3a28'), belt_c=H('7a5a3a'))
add('warga_pria', 'Warga biasa (laki-laki)', ['bawa_karung', 'melambai'], hf=1.08, wf=0.9, skin=SK['pucat'], hair='short', hair_c=H('2a2024'), top='longtunic',
    top_c=H('5f9a58'), trim_c=H('e8d8a0'), pants_c=H('4a4a58'), boots_c=H('3a2a20'), hat='cap', hat_c=H('6a7a9a'), belt_c=H('4a3020'))
add('warga_wanita', 'Warga biasa (perempuan)', ['bawa_keranjang', 'menyapu'], hf=0.97, wf=0.92, skin=SK['terang'], hair='long', hair_c=H('d9a84a'), top='dress',
    top_c=H('4f80c0'), trim_c=H('f3ead8'), blush=True, boots_c=H('4b2f20'), belt_c=H('f3ead8'))
add('penjaga_gerbang', 'Penjaga gerbang', ['jaga', 'tusuk'], hf=1.13, wf=1.15, bulk=0.6, skin=SK['terang'], hair='short', hair_c=H('4a3020'), top='armor',
    top_c=H('8d93a3'), tabard_c=H('3f6fb0'), emblem_c=H('f0c455'), hat='helmet', pants_c=H('4a4552'), boots_c=H('3a2a20'), stache=True, idle_style='normal')
add('pandai_besi', 'Pandai besi', ['menempa', 'berkacak'], hf=0.9, wf=1.28, bulk=1.4, skin=SK['coklat'], hair='bald', hair_c=H('1e1612'), beard='long',
    top='tunic', top_c=H('7a7f8e'), apron_c=H('5a3a22'), pants_c=H('3a3744'), boots_c=H('2a1a12'), sleeve='rolled', belt_c=H('2a1a12'))
add('pustakawan', 'Penjaga perpustakaan', ['membaca', 'menata_buku'], hf=0.97, wf=0.95, skin=SK['pucat'], hair='sidebald', hair_c=H('e2ddd6'), beard='long',
    top='robe', top_c=H('5a4a8a'), trim_c=H('f0c455'), glasses=True, hat='scholar', hat_c=H('3a2f5e'), belt_c=H('f0c455'), boots_c=H('3a2a20'), idle_style='hunch')
add('pedagang', 'Pedagang', ['menawarkan', 'hitung_koin'], hf=0.9, wf=1.18, bulk=1.0, skin=SK['zaitun'], hair='short', hair_c=H('1e1612'), stache=True,
    top='tunic', top_c=H('c8433a'), trim_c=H('f0c455'), hat='feather', hat_c=H('7a2a3a'), pouch=True, belt_c=H('f0c455'), pants_c=H('3f4a6a'), boots_c=H('4b2f20'))
add('pendeta', 'Pendeta / biarawan', ['berdoa', 'memberkati'], hf=1.0, skin=SK['terang'], hair='tonsure', hair_c=H('6a4528'), top='robe', top_c=H('7a5a3a'),
    trim_c=H('e8d8a0'), belt_c=H('efe4c4'), bare_feet=True, boots_c=H('6a4a30'))
add('tukang_roti', 'Tukang roti', ['menguleni', 'bawa_nampan'], hf=0.93, wf=1.1, bulk=0.6, skin=SK['terang'], hair='bun', hair_c=H('8a4a2a'), top='tunic',
    top_c=H('f0ece0'), apron_c=H('8fb8d8'), hat='chef', hat_c=H('fbf8f0'), blush=True, sleeve='rolled', pants_c=H('6b5a48'), boots_c=H('4b2f20'), belt_c=H('8fb8d8'))
add('penebang_kayu', 'Penebang kayu', ['menebang', 'bawa_kayu'], hf=1.04, wf=1.2, bulk=0.8, skin=SK['sawo'], hair='short', hair_c=H('c9662a'), beard='short',
    top='tunic', top_c=H('b8503f'), trim_c=H('3a2a20'), hat='cap', hat_c=H('7a8a7a'), pants_c=H('5a4a3a'), boots_c=H('3a2a20'), sleeve='rolled')
add('pemanah', 'Pemanah / pemburu', ['memanah', 'mengintai'], hf=1.06, wf=0.9, skin=SK['zaitun'], hair='short', hair_c=H('2a2024'), top='tunic',
    top_c=H('4a7a50'), trim_c=H('c9a74a'), hat='hood', hat_c=H('3f6a48'), cape_c=H('6a4a30'), quiver=True, pants_c=H('5a4a3a'), boots_c=H('3a2a20'))
add('anak', 'Anak-anak', ['melompat', 'melambai'], hf=0.64, hs=1.1, wf=0.85, skin=SK['terang'], hair='short', hair_c=H('c9803a'), top='tunic',
    top_c=H('d9584c'), pants_c=H('6b5a48'), boots_c=H('4b2f20'), blush=True, belt_c=H('f3ead8'))
add('bangsawan', 'Bangsawan', ['melambai_agung', 'pose_bangga'], hf=1.1, wf=0.98, skin=SK['pucat'], hair='long', hair_c=H('7a4a2a'), top='dress',
    top_c=H('8a2f5a'), trim_c=H('f0c455'), hat='crown', cape_c=H('3f3a7a'), blush=True, belt_c=H('f0c455'), boots_c=H('3a2a20'))
