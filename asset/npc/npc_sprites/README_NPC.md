# Sprite NPC Medieval – gaya kusir, 30 FPS

Semua NPC menghadap **KANAN** (flip horizontal di Godot untuk menghadap kiri). PNG transparan, grid frame seragam,
satu animasi = satu sheet horizontal. Filter di Godot: **Nearest**.

- Ukuran 1 frame: **56 x 56** px
- Titik pijak kaki (ground): **y = 52**, pusat badan **x = 28** (taruh node di titik kaki, geser sprite -28 x, -52 y)
- Kecepatan putar: **30 FPS**, semua loop mulus (loop terus-menerus)
- Alat yang dipegang (cangkul, palu, busur, tombak, buku, dll) sudah menyatu di dalam frame

## Animasi umum (semua NPC)
| Animasi | Frame | Keterangan |
|---|---|---|
| `diam` | 60 | berdiri, napas, kedip, bergeser tumpuan |
| `jalan` | 30 | langkah jalan (gerak maju dilakukan oleh game, kecepatan sekitar 18-20 px/detik) |
| `lari` | 20 | berlari condong ke depan |
| `ngobrol` | 60 | bicara dengan gestur tangan dan mulut bergerak |

## Daftar NPC dan kegiatan pekerjaannya
| Folder | Peran | Animasi kerja |
|---|---|---|
| `petani_pria` | Petani (laki-laki) | `cangkul` (36f), `tanam` (48f) |
| `petani_wanita` | Petani (perempuan) | `menabur` (36f), `memanen` (40f) |
| `warga_pria` | Warga biasa (laki-laki) | `bawa_karung` (30f), `melambai` (36f) |
| `warga_wanita` | Warga biasa (perempuan) | `bawa_keranjang` (30f), `menyapu` (40f) |
| `penjaga_gerbang` | Penjaga gerbang | `jaga` (60f), `tusuk` (30f) |
| `pandai_besi` | Pandai besi | `menempa` (30f), `berkacak` (60f) |
| `pustakawan` | Penjaga perpustakaan | `membaca` (60f), `menata_buku` (48f) |
| `pedagang` | Pedagang | `menawarkan` (60f), `hitung_koin` (48f) |
| `pendeta` | Pendeta / biarawan | `berdoa` (60f), `memberkati` (48f) |
| `tukang_roti` | Tukang roti | `menguleni` (36f), `bawa_nampan` (30f) |
| `penebang_kayu` | Penebang kayu | `menebang` (36f), `bawa_kayu` (30f) |
| `pemanah` | Pemanah / pemburu | `memanah` (60f), `mengintai` (60f) |
| `anak` | Anak-anak | `melompat` (24f), `melambai` (36f) |
| `bangsawan` | Bangsawan | `melambai_agung` (48f), `pose_bangga` (60f) |

Nama file: `<npc>/<npc>_<animasi>_<jumlah_frame>f.png`, contoh `pandai_besi/pandai_besi_menempa_30f.png` -> `Hframes = 30`.

Perbedaan antar NPC: tinggi badan (anak 0,64x sampai penjaga 1,13x), lebar/gemuk badan, ukuran kepala, 6 warna kulit,
gaya rambut dan jenggot, pakaian (tunik, gaun, jubah, baju zirah), topi (jerami, topi pet, tudung, helm, topi koki, bulu, mahkota),
celemek, jubah, kacamata, kantong, tabung panah, postur (bungkuk untuk yang tua).

## Prop (aset terpisah, folder `props/`)
Beberapa gerakan butuh benda diam. Taruh prop di posisi (x, y) relatif sudut kiri-atas frame NPC (file `props/posisi_prop.json`):
| Prop | Dipakai oleh | Posisi (x, y) | Letakkan |
|---|---|---|---|
| `prop_landasan.png` | pandai_besi `menempa` | (33, 42) | di belakang NPC |
| `prop_meja_adonan.png` | tukang_roti `menguleni` | (32, 36) | di belakang NPC |
| `prop_balok_kayu.png` | penebang_kayu `menebang` | (37, 45) | di belakang NPC |
| `prop_tanah_olahan.png` | petani_pria `tanam` / `cangkul` | (33, 49) | di belakang NPC |
| `prop_rak_buku.png` | pustakawan `menata_buku` | (40, 7) | di belakang NPC |

## Pakai di Godot 4
Salin folder `npc_sprites` ke `res://`. Tambahkan `npc_player.gd` ke node `Node2D`, isi `npc_name` (mis. `pandai_besi`),
lalu panggil `play_anim("menempa")`. Skrip membaca semua sheet NPC itu dan membuat `SpriteFrames` otomatis (30 FPS, loop).
Gerak berpindah tempat (jalan/lari) digerakkan oleh game; sprite tetap di tengah frame.

## Preview
- `preview/adegan_desa_medieval.gif` – 11 NPC bekerja berdampingan dengan prop
- `preview/roster_semua_npc.png` – semua 14 NPC
- `preview/peragaan_<npc>.gif` – semua animasi satu NPC berurutan

## Catatan
- Sprite tidak dipisah per layer (badan/pakaian/alat menyatu), sama seperti sprite kusir.
- Sumber Python pembuat sprite ada di `_sumber_python/` bila ingin menambah NPC atau warna baru (`npc_roster.py`).
