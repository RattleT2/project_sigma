# Bangunan Kota Medieval – gaya pixel sama dengan gerobak & NPC

**Aturan arah:** semua rumah dan bangunan **menghadap layar/pemain** (tampak depan). Hanya **gerbang kota, pagar, dan tembok**
yang boleh dipasang memanjang menyamping mengikuti jalan.

Versi ini adalah **versi KOTA** (batu, kayu-plester, bata, atap genteng/batu tulis). Versi lain (desa, hutan, gurun, dll) bisa menyusul dengan struktur yang sama.

## Aturan teknis
- PNG transparan. **Titik pijak = tepi bawah sprite** (taruh sprite dengan bawahnya di garis tanah). Semua bangunan berdiri di lantai yang sama.
- Skala mengikuti NPC (tinggi ~38 px): **pintu 26x44 px** (kedai/depot lebih lebar), jadi NPC bisa berdiri di depan pintu.
- Posisi tiap pintu (x tengah, y atas, lebar, tinggi) dan cerobong ada di `data_bangunan.json`. Titik berdiri NPC = (x pintu, tepi bawah sprite).
- Urutan layer disarankan: bangunan -> animasi asap/api -> prop -> NPC -> karavan.
- Papan nama gantung menonjol ke kanan; kanvas sudah diberi ruang tambahan.

## Kesesuaian dengan karavan (depot)
- **Dermaga muat** (`depot_dermaga_muat`) tingginya 32 px = tinggi lantai bak gerobak, jadi muatan bisa digeser rata dari dermaga ke gerobak.
  Parkirkan karavan dengan bagian belakang gerobak (kiri) menempel di ujung kanan dermaga, menghadap kanan.
- **Gerbang kota**: lubang 90x118 px, lebih tinggi dari karavan (tinggi ~96 px termasuk tiang bendera).
- **Depot** terdiri dari: gudang (pintu muat + katrol), kantor pertukaran (loket berjeruji), dermaga, derek (anim 30 frame), 3 tumpukan barang,
  timbangan, papan harga, dan tiang penunjuk arah. Lihat `preview/area_depot_dengan_karavan.png`.

## Animasi (folder `animasi/`, 30 FPS)
| File | Isi | Posisi |
|---|---|---|
| `*_asap_30f.png` | asap cerobong, loop 30 frame | kanvas lebih tinggi 44 px, taruh di (0, -44) relatif sprite |
| `bengkel_pandai_besi_api_30f.png` | nyala api tungku | ukuran sama dengan sprite, taruh di (0, 0) |
| `depot_derek_30f.png` | derek dengan peti berayun | 96x156 per frame |
| `menara_alkemis_asap_30f.png` | asap hijau alkemis | seperti asap lain |

## Rumah manusia
| File | NPC / pengguna | Keterangan | Ukuran |
|---|---|---|---|
| `rumah_petani` | petani_pria, petani_wanita | pondok beratap jerami, tumpukan jerami, garpu | 128x121 |
| `rumah_warga_kayu` | warga_pria | rumah kayu 2 lantai atap genteng merah | 120x169 |
| `rumah_warga_plester` | warga_wanita | rumah plester + kayu, atap batu tulis biru | 128x165 |
| `rumah_warga_bata` | warga (umum) | rumah bata, atap sirap | 122x163 |
| `pos_penjaga` | penjaga_gerbang | pos jaga batu dengan benteng dan panji | 100x159 |
| `bengkel_pandai_besi` | pandai_besi, beruang_pandai_besi | bengkel tempa dengan tungku, landasan, cerobong besar | 150x143 |
| `perpustakaan` | pustakawan | perpustakaan batu bertiang dengan pedimen buku | 164x177 |
| `toko_pedagang` | pedagang | toko dengan etalase, kanopi belang, peti dagangan | 146x169 |
| `gereja_kapel` | pendeta | kapel batu dengan menara lonceng dan jendela mawar | 140x209 |
| `toko_roti` | tukang_roti | toko roti dengan oven bata dan kanopi | 134x169 |
| `penggergajian_kayu` | penebang_kayu | pondok kayu gelondongan dengan tumpukan kayu | 152x121 |
| `pondok_pemburu` | pemanah, elf_pemanah | pondok pemburu dengan tanduk, kulit, sasaran panah | 142x121 |
| `rumah_bangsawan` | bangsawan | rumah besar dengan dua menara, balkon, dan lambang | 214x225 |
| `kedai_penginapan` | kucing_bard, kelinci_pelayan | kedai dan penginapan, pintu ganda lebar, papan cangkir | 178x167 |
| `barak_serigala` | serigala_penjaga | barak penjaga besar, panji ungu | 170x159 |
| `rumah_pencuri` | rubah_pencuri | rumah sempit gelap tempat persembunyian | 104x161 |

## Rumah fantasi
| File | NPC / pengguna | Keterangan | Ukuran |
|---|---|---|---|
| `rumah_pohon_elf` | elf_pemanah, elf_tabib | rumah pohon raksasa dengan tangga tali | 156x256 |
| `pondok_tabib` | elf_tabib | pondok herbal dengan tanaman obat digantung | 128x121 |
| `menara_penyihir` | elf_penyihir | menara batu biru bertabur bintang dan bola cahaya | 84x233 |
| `kuil_peramal` | rubah_peramal | kuil merah dengan patung rubah dan bola kristal | 150x150 |
| `tambang_kurcaci` | kurcaci_penambang | pintu tambang di bukit batu, rel dan gerobak | 170x172 |
| `pondok_orc` | orc_prajurit | tenda kulit dengan pagar kayu runcing dan panji | 190x150 |
| `menara_alkemis` | kadal_alkemis | menara alkemis dengan balkon kuali dan atap ungu | 84x233 |

## Depot karavan (versi kota)
| File | NPC / pengguna | Keterangan | Ukuran |
|---|---|---|---|
| `depot_gudang` | MC karavan (muat/bongkar barang) | gudang besar dengan pintu muat, katrol, panji peti | 226x179 |
| `depot_kantor_tukar` | MC karavan (pertukaran barang/koin) | kantor pertukaran dengan loket berjeruji dan papan tukar | 142x167 |
| `depot_dermaga_muat` | MC karavan | dermaga muat setinggi dasar gerobak (32 px) | 116x44 |
| `depot_tumpukan_a` | - | tumpukan peti dan tong | 76x58 |
| `depot_tumpukan_b` | - | tumpukan karung dan peti | 76x58 |
| `depot_tumpukan_c` | - | campuran peti, tong, karung | 76x58 |
| `depot_timbangan` | - | timbangan dagang | 52x50 |
| `depot_papan_harga` | - | papan harga barang | 70x70 |
| `depot_tanda_arah` | - | tiang penunjuk arah ke depot dan pertukaran | 48x74 |
| `depot_derek` | - | derek kayu dengan peti berayun (30 frame) | 96x156 |

## Gerbang, pagar, tembok (boleh tampak samping)
| File | NPC / pengguna | Keterangan | Ukuran |
|---|---|---|---|
| `gerbang_kota` | - | gerbang kota, lubang 90x118 px (karavan bisa lewat) | 250x214 |
| `pagar_kayu` | - | pagar kayu 32 px (ubin sambung ke kanan) | 36x38 |
| `pagar_kayu_gerbang` | - | pintu pagar kayu | 50x44 |
| `pagar_batu` | - | pagar batu rendah 32 px | 36x30 |
| `pagar_besi` | - | pagar besi 32 px | 36x46 |
| `tembok_kota` | - | segmen tembok kota 64 px | 68x124 |

## Preview
- `preview/peta_kota_skala.png` – jalan kota dengan gerbang, rumah, depot + karavan, dan NPC (uji skala)
- `preview/area_depot_dengan_karavan.png` – depot dengan karavan parkir di dermaga
- `preview/katalog_*.png` – katalog semua bangunan
