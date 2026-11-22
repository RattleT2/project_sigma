# Bangunan lengkap biome Gurun

Aturan sama dengan paket kota: rumah menghadap layar, pintu 26x44 px, titik pijak = tengah tepi bawah (`pivot` di JSON).
Posisi pintu dan titik asap ada di `data_bangunan_gurun_lengkap.json`.

## Rumah pekerjaan (16)
petani, warga1-3, penjaga, pandai_besi, pustakawan, pedagang, pendeta, tukang_roti, penebang_kayu, pemburu, bangsawan, kedai, barak, pencuri.

## Rumah fantasi (7)
pohon_elf, tabib, menara_penyihir, kuil_peramal, tambang_kurcaci, pondok_orc, menara_alkemis.

## Depot karavan
- depot_gudang, depot_kantor_pertukaran
- depot_dermaga_muat: tinggi 32 px dari tanah (deck_y di JSON), parkir gerobak dengan bagian belakang di ujung kanan
- depot_derek (+ _sheet: 24 frame, 30 fps, gerobak/peti berayun)
- depot_tumpukan_kotak / _tong / _karung, depot_timbangan, depot_papan_harga, depot_tiang_arah

## Gerbang masuk depot menghadap SAMPING
Dilalui kiri-kanan, bukan menghadap pemain. Dua lapis dengan ukuran sama (328x206, pivot tengah bawah):
1. `depot_gerbang_samping_belakang_gurun.png` digambar di BAWAH NPC/karavan
2. `depot_gerbang_samping_depan_gurun.png` digambar di ATAS NPC/karavan (pilar ujung dan jeruji)
Lorong bebas: tinggi 118 px (karavan ~96 px muat), koordinat di JSON bagian `lorong`.
`depot_gerbang_samping_gurun.png` = gabungan kedua lapis untuk pemakaian statis.

Catatan: kedua biome memakai nama file yang sama dengan akhiran `_gurun`, jadi bisa ditukar per biome lewat kode.
