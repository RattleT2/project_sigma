# Sprite Caravan Kuda – Pixel Art 2D Platformer (menghadap & berjalan ke KANAN)

Semua file PNG transparan (RGBA), tanpa background, grid frame seragam, jadi tinggal diatur
`Hframes` di Sprite2D atau di-slice di AnimatedSprite2D. Pengaturan import Godot: **Filter = Nearest**.

## Ukuran frame
| Bagian | Ukuran 1 frame | Jumlah frame | Ukuran file |
|---|---|---|---|
| Kuda diam / jalan | 96 x 64 | 8 / 12 | 768 x 64 / 1152 x 64 |
| Kuda lari / lompat / berhenti | 128 x 96 | 10 / 14 / 9 | 1280 / 1792 / 1152 x 96 |
| Harness kuda (overlay, 3 warna) | 96 x 64 | 12 / 8 | sama dengan kuda |
| Pengemudi duduk | 24 x 34 | 8 | 192 x 34 |
| Roda | 32 x 32 | 8 | 256 x 32 |
| Gerobak (badan, kanopi, kabin, aksesoris) | 128 x 96 | 1 | 128 x 96 |
| Bendera, asap cerobong | 128 x 96 | 8 | 1024 x 96 |

Gerobak 128 px lebar (sesuai permintaan) tapi dibuat 96 px tinggi supaya tidak terlihat pendek:
kanopi/atap tinggi, plus 16 px ruang kosong di atas untuk muatan atap, bendera, dan asap.

## Isi folder
- `kuda/` (V3, anatomi mengikuti referensi) – lihat bagian "KUDA V3" di bawah.
- `pengemudi/` – `pengemudi_1_pionir` (topi kowboi, kumis) dan `pengemudi_2_pedagang` (kerudung merah, kepang).
- `gerobak_A_covered_wagon/` – badan + `A_rangka_kanopi` (tanpa kain) + 5 varian kanopi
  (krem, krem_tambal, belang_merah, hijau, biru).
- `gerobak_B_karavan_dagang/` – badan + 3 varian kabin (toska, kuning, ungu) + cerobong, asap (anim), awning belang, papan dagang, tangga belakang.
- `roda/` – `roda_kayu` (A) dan `roda_merah` (B); 8 frame putar halus (12 jari-jari, loop 30 derajat).
- `aksesoris/` – tong air, tali gulung, sekop+beliung, lentera, panci+ember, roda cadangan, karung/peti atap, tuas rem, peti ayam, bendera (anim).
- `preview/` – GIF animasi A dan B, katalog semua modifikasi, preview kuda + pengemudi.

## Posisi (Sprite2D, Centered = OFF, relatif ke origin gerobak 0,0)
Semua overlay gerobak berukuran 128x96 dan **ditaruh di (0, 0)** – posisinya sudah pas.

| Node | Posisi (x, y) | Catatan |
|---|---|---|
| Badan, kanopi/kabin, aksesoris | (0, 0) | urutan: badan -> rangka -> kanopi/kabin -> aksesoris |
| Roda belakang | (7, 67) | Hframes = 8 |
| Roda depan | (69, 67) | Hframes = 8 |
| Pengemudi | (96, 32) | Hframes = 8, tepi kanan = tepi kiri kuda |
| Kuda | (120, 33) | Hframes = 8 (walk) / 4 (idle) |
| Harness | (120, 33) | tepat di atas kuda, frame sama |

Tali kekang tersambung otomatis: dari tangan pengemudi (tepi kanan sprite) ke tepi kiri sprite kuda.
Ujung tali tarik kuda menyambung ke palang tarik di ujung tongkat gerobak.

## Urutan layer (bawah -> atas)
1. `A_badan` / `B_badan`
2. `A_rangka_kanopi` (hanya jika tanpa kain) atau `A_kanopi_*` / `B_kabin_*`
3. aksesoris (tong, tali, sekop, panci, karung atap, awning, papan, tangga, cerobong, asap, bendera ...)
4. `roda_*` x2 (depan & belakang)
5. pengemudi
6. kuda, lalu harness

Catatan: `lentera`, `tuas_rem`, `roda_cadangan`, `peti_ayam` bisa dipasang di A maupun B.
Untuk B, `tong_air`, `tali_gulung`, `sekop_beliung` tidak disarankan (sudah ada kabin).

## Animasi
Kuda 12 frame (jalan) / 8 frame (diam); roda, pengemudi, bendera, asap 8 frame. Semua loop = 1 detik: pakai satu AnimationPlayer / satu timer (mis. 8 FPS) dan set `frame` yang sama
ke kuda, harness, roda, pengemudi, bendera, asap. Efek guncangan: geser node induk "Gerobak"
(badan + kanopi + aksesoris + pengemudi, TANPA roda) dengan pola y = 0,0,-1,-1,0,0,-1,-1 piksel.

## Skrip contoh (Godot 4) -> `caravan_demo.gd`
Pasang ke sebuah Node2D kosong, salin folder `caravan_sprites` ke `res://`. Ubah tiga variabel di bagian atas untuk ganti kuda/kanopi/harness.


## KUDA V3
Folder: `kuda/<warna>/<aksi>_<n>f/` berisi sheet gabungan + folder `layer/` (8 layer, semuanya beranimasi):
`01_kaki_belakang_jauh, 02_kaki_depan_jauh, 03_ekor, 04_badan, 05_leher_kepala, 06_surai, 07_kaki_belakang_dekat, 08_kaki_depan_dekat` (urutan = z-order bawah ke atas).
Harness: `kuda/harness_<coklat|hitam|merah>/<aksi>_<n>f/` berisi gabungan + `layer/`: `h1_kerah, h2_badan, h3_kepala, h4_tali`. Ditumpuk DI ATAS kuda.
Warna kuda: `kuda_1_bay`, `kuda_2_putih_abu`, bonus `kuda_3_hitam`, `kuda_4_kastanye_kaus_putih`.

| Aksi | Frame | Kanvas | Catatan |
|---|---|---|---|
| diam (berhenti/berdiri) | 8 | 96x64 | napas, kepala, ekor, telinga berkedut (loop) |
| jalan | 12 | 96x64 | langkah 4 ketukan (loop) |
| lari (galop) | 10 | 128x96 | badan memanjang, surai & ekor terurai, telinga ke belakang (loop) |
| lompat | 14 | 128x96 | jongkok, tolak, naik, puncak (kaki depan terlipat), turun, mendarat, pulih (sekali putar) |
| berhenti (rem) | 9 | 128x96 | dari lari -> kaki depan menahan, kaki belakang masuk bawah, kepala naik -> berdiri (sekali putar) |

Posisi: sprite kanvas 96x64 ditaruh di (0,0) relatif titik kuda; sprite kanvas 128x96 ditaruh di (-16,-28) dari titik yang sama
(titik tanah teracak kaki sama di semua aksi, jadi pergantian animasi tidak melompat). Untuk gerobak, kuda jalan/diam tetap di (120,33).
Pada jalan/diam, ujung tali tarik dan kekang menyambung ke gerobak/pengemudi; pada lari/lompat/berhenti tali berayun bebas mengikuti badan
(karena gerobak tidak ikut melompat).

## Kecepatan & sinkronisasi (supaya kaki tidak tergelincir)
- Kuda jalan: 12 frame @ 12 FPS (loop 1 detik). Kecepatan tanah yang cocok dengan langkah kaki = sekitar 22 px/detik (naikkan `speed_scale` animasi untuk jalan lebih cepat, naikkan kecepatan gerak dengan faktor yang sama).
- Roda: 8 frame @ 24 FPS (3 putaran loop per detik) = cocok dengan kecepatan 22 px/detik.
- Pengemudi / bendera / asap / guncangan: 8 frame @ 8 FPS.
Urutan z-order kuda penuh (bawah ke atas): 01..08 lalu h1_kerah, h2_badan, h3_kepala, h4_tali. Posisi semua layer kuda sama (120, 33).
Ujung tali tarik jatuh di (7,41) lokal kuda (nyambung ke palang tarik), ujung kekang di (0,20) lokal kuda (nyambung ke tangan pengemudi).
