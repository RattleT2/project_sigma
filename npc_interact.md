# NPC Interaction Specification

## 1. Tujuan Dokumen

Dokumen ini adalah acuan implementasi untuk sistem NPC dan prop di Godot 4. Gunakan nama animasi, path asset, ukuran frame, dan aturan node yang tertulis di sini. Jangan menebak nama node atau membuat ulang seluruh sistem sekaligus.

Implementasi harus dilakukan bertahap:

1. Pastikan satu scene NPC dapat menampilkan animasi.
2. Tambahkan prop kerja untuk NPC yang membutuhkannya.
3. Tambahkan state machine aktivitas NPC.
4. Tambahkan interaksi player atau karavan.
5. Tambahkan konsekuensi turn, resource, quest, dan depot.

Sebelum menulis kode, baca scene `.tscn` yang diminta user. Gunakan struktur node aktual dari scene tersebut, bukan path contoh yang belum diverifikasi.

## 2. Sumber Asset dan Aturan Sprite

Asset NPC berada di:

```text
res://asset/npc/npc_sprites/
```

Script pemuat NPC yang sudah tersedia berada di:

```text
res://asset/npc/npc_sprites/npc_player.gd
```

Catatan: script tersebut memiliki default folder `res://npc_sprites/`, sedangkan asset project berada di `res://asset/npc/npc_sprites/`. Saat dipakai di project ini, pastikan property `folder` atau path script disesuaikan dengan path aktual. Jangan mengubah path secara asumsi.

Aturan umum asset:

- Ukuran satu frame: `56 x 56 px`.
- Titik pijak kaki: `y = 52`.
- Titik pusat badan: `x = 28`.
- Semua sprite menghadap kanan secara default.
- Gunakan `flip_h` untuk menghadap kiri.
- Texture filter: `Nearest`.
- Animasi berjalan pada `30 FPS`.
- Gerakan posisi NPC dilakukan oleh game, bukan oleh sprite sheet.
- Animasi kerja umumnya loop sampai aktivitas dihentikan oleh state machine.

Node dasar NPC:

```text
NPC (Node2D atau CharacterBody2D)
├── AnimatedSprite2D
├── CollisionShape2D
├── InteractionArea (Area2D)
│   └── CollisionShape2D
├── WorkPoint (Marker2D, jika NPC bekerja)
├── PropAnchor (Marker2D, jika memakai prop)
└── Timer atau ActivityTimer
```

Scene yang sudah ada menggunakan variasi nama node. DeepSeek wajib membaca `.tscn` aktual sebelum memakai path seperti `$AnimatedSprite2D` atau `$InteractionArea`.

## 3. Animasi Umum Semua NPC

| Animasi | Frame | Fungsi |
|---|---:|---|
| `diam` | 60 | Idle, napas, kedip, perubahan tumpuan |
| `jalan` | 30 | Perpindahan NPC |
| `lari` | 20 | Perpindahan cepat atau keadaan darurat |
| `ngobrol` | 60 | Dialog dan gestur berbicara |

Fungsi minimum yang diharapkan dari pemutar NPC:

```text
play_anim(animation_name)
face(is_facing_right)
move_to(target_position)
start_activity(activity_name)
stop_activity()
```

Jangan mengandalkan nama fungsi tersebut jika scene atau script aktual memakai nama berbeda. Sesuaikan implementasi dengan file yang benar.

## 4. Roster NPC dan Aktivitas

### 4.1 Petani Pria

Folder asset:

```text
res://asset/npc/npc_sprites/petani_pria/
```

Animasi kerja:

- `cangkul`
- `tanam`

Prop:

- `prop_tanah_olahan.png`
- Posisi prop relatif terhadap sudut kiri atas frame: `(33, 49)`.
- Letakkan prop di belakang NPC.

Interaksi gameplay:

- `cangkul`: menyiapkan tanah dan meningkatkan kesiapan lahan.
- `tanam`: memakai benih dan membuat tanaman tumbuh.
- Pada turn berikutnya, lahan dapat berubah menjadi lahan produktif.

### 4.2 Petani Wanita

Folder asset:

```text
res://asset/npc/npc_sprites/petani_wanita/
```

Animasi kerja:

- `menabur`
- `memanen`

Prop khusus tidak tersedia dalam daftar prop saat ini.

Interaksi gameplay:

- `menabur`: menambah progres tanaman.
- `memanen`: menghasilkan makanan atau resource depot.
- Jika tidak ada tanaman siap panen, aktivitas `memanen` harus gagal dengan pesan yang jelas.

### 4.3 Warga Pria

Folder asset:

```text
res://asset/npc/npc_sprites/warga_pria/
```

Animasi aktivitas:

- `bawa_karung`
- `melambai`

Interaksi gameplay:

- `bawa_karung`: menunjukkan aktivitas pengangkutan barang.
- `melambai`: idle sosial atau respons ketika karavan tiba.
- Warga dapat menjadi pemberi informasi atau saksi kondisi depot.

### 4.4 Warga Wanita

Folder asset:

```text
res://asset/npc/npc_sprites/warga_wanita/
```

Animasi aktivitas:

- `bawa_keranjang`
- `menyapu`

Interaksi gameplay:

- `bawa_keranjang`: aktivitas membawa suplai.
- `menyapu`: dekorasi aktivitas desa dan indikator depot yang mulai pulih.

### 4.5 Penjaga Gerbang

Folder asset:

```text
res://asset/npc/npc_sprites/penjaga_gerbang/
```

Animasi kerja:

- `jaga`
- `tusuk`

Interaksi gameplay:

- `jaga`: memeriksa karavan atau menjaga pintu masuk.
- `tusuk`: hanya dipakai jika ada ancaman atau event keamanan.
- Penjaga dapat membuka atau menutup akses ke depot berdasarkan reputasi atau quest.

### 4.6 Pandai Besi

Folder asset:

```text
res://asset/npc/npc_sprites/pandai_besi/
```

Animasi kerja:

- `menempa`
- `berkacak`

Prop:

- `prop_landasan.png`
- Posisi prop: `(33, 42)`.
- Letakkan prop di belakang NPC.

Interaksi gameplay:

- `menempa`: memperbaiki wagon, roda, harness, atau perlengkapan.
- `berkacak`: idle ketika tidak ada pekerjaan.
- Upgrade membutuhkan gold, material, atau hasil quest.

### 4.7 Pustakawan

Folder asset:

```text
res://asset/npc/npc_sprites/pustakawan/
```

Animasi kerja:

- `membaca`
- `menata_buku`

Prop:

- `prop_rak_buku.png`
- Posisi prop: `(40, 7)`.
- Letakkan prop di belakang NPC.

Interaksi gameplay:

- Memberikan informasi tentang rute, depot, dan event.
- Dapat membuka quest pengetahuan atau memberi petunjuk zona berikutnya.

### 4.8 Pedagang

Folder asset:

```text
res://asset/npc/npc_sprites/pedagang/
```

Animasi kerja:

- `menawarkan`
- `hitung_koin`

Interaksi gameplay:

- `menawarkan`: membuka daftar barang atau suplai.
- `hitung_koin`: idle setelah transaksi.
- Jangan membuat transaksi hanya dari animasi; transaksi harus mengubah resource game state.

### 4.9 Pendeta

Folder asset:

```text
res://asset/npc/npc_sprites/pendeta/
```

Animasi kerja:

- `berdoa`
- `memberkati`

Interaksi gameplay:

- `memberkati`: memberikan buff sementara pada karavan, kuda, atau reputasi.
- `berdoa`: aktivitas idle atau persiapan event.
- Efek buff harus tercatat di game state dan memiliki durasi atau batas yang jelas.

### 4.10 Tukang Roti

Folder asset:

```text
res://asset/npc/npc_sprites/tukang_roti/
```

Animasi kerja:

- `menguleni`
- `bawa_nampan`

Prop:

- `prop_meja_adonan.png`
- Posisi prop: `(32, 36)`.
- Letakkan prop di belakang NPC.

Interaksi gameplay:

- `menguleni`: memproses bahan menjadi makanan.
- `bawa_nampan`: menunjukkan makanan siap dikirim.
- Makanan dapat memulihkan stamina kuda atau menjadi suplai depot.

### 4.11 Penebang Kayu atau Lumberjack

Folder asset:

```text
res://asset/npc/npc_sprites/penebang_kayu/
```

Scene yang sudah tersedia:

```text
res://scenes/npc_lumberjack_men.tscn
```

Animasi kerja:

- `menebang`
- `bawa_kayu`

Prop:

- `prop_balok_kayu.png`
- Posisi prop: `(37, 45)`.
- Letakkan prop di belakang NPC.

#### Alur Menebang Pohon

```text
idle
  -> move_to_tree
  -> align_to_tree
  -> chopping
  -> tree_final_shake
  -> tree_felled
  -> collect_log
  -> carry_log
  -> return_or_idle
```

#### Perilaku Visual Pohon

Setiap tebasan harus memiliki urutan berikut:

1. NPC memainkan animasi `menebang`.
2. Pada waktu hit yang ditentukan, pohon bergetar singkat.
3. Pohon kembali ke posisi normal.
4. Hit count bertambah.
5. Jika hit count belum mencapai batas, NPC mengulang tebasan.
6. Jika hit count sudah mencapai batas, pohon memainkan `final_shake` yang lebih kuat atau lebih lama.
7. Setelah `final_shake` selesai, pohon disembunyikan atau dihapus.
8. Particle ditebarkan dari posisi batang atau dasar pohon.
9. Prop log dibuat atau diaktifkan.
10. NPC memainkan `bawa_kayu` setelah log berhasil dikumpulkan.

Struktur prop pohon yang disarankan:

```text
TreeProp (Node2D)
├── TreeSprite (AnimatedSprite2D atau Sprite2D)
├── InteractionArea (Area2D)
│   └── CollisionShape2D
├── LumberjackPoint (Marker2D)
├── HitPoint (Marker2D)
├── FallingLog (Sprite2D, hidden by default)
└── ChoppingParticles (GPUParticles2D, one_shot)
```

Kontrak fungsi pohon:

```text
can_be_chopped() -> bool
register_chop() -> void
play_hit_shake() -> void
play_final_shake() -> void
fell() -> void
spawn_log() -> void
```

Aturan penting:

- Jangan langsung menghilangkan pohon saat NPC memainkan animasi.
- Particle hanya muncul sekali setelah `final_shake` selesai.
- Particle tidak boleh muncul pada setiap frame animasi.
- `register_chop()` harus dipanggil pada hit frame yang sama setiap siklus.
- Jika NPC pergi atau aktivitas dibatalkan, pohon tidak boleh dianggap tumbang.
- Jika sistem turn dipakai, status `hit_count`, `is_felled`, dan `regrow_turns` harus disimpan di data pohon.

Contoh state pohon:

```text
TreeState
├── hit_count: int
├── required_hits: int
├── is_being_chopped: bool
├── is_felled: bool
├── wood_amount: int
└── regrow_turns: int
```

Tema pelestarian:

- Menebang pohon menghasilkan kayu untuk perbaikan depot.
- Menebang terlalu banyak pohon menurunkan `conservation_score`.
- Pemain dapat memiliki quest menanam kembali atau menjaga jumlah pohon minimum.
- Pohon yang tumbang dapat tumbuh kembali setelah beberapa turn jika sistem regrowth diaktifkan.

### 4.12 Pemanah

Folder asset:

```text
res://asset/npc/npc_sprites/pemanah/
```

Animasi kerja:

- `memanah`
- `mengintai`

Interaksi gameplay:

- `mengintai`: mendeteksi ancaman atau event di depan rute.
- `memanah`: dipakai hanya pada event ancaman yang memang aktif.
- Jangan membuat pemanah menyerang NPC lain secara otomatis tanpa event gameplay.

### 4.13 Anak-anak

Folder asset:

```text
res://asset/npc/npc_sprites/anak/
```

Animasi aktivitas:

- `melompat`
- `melambai`

Interaksi gameplay:

- Aktivitas sosial dan dekorasi hidup di area depot.
- Dapat memberi respons visual ketika karavan datang.
- Tidak boleh memiliki interaksi berbahaya atau resource penting tanpa desain quest khusus.

### 4.14 Bangsawan

Folder asset:

```text
res://asset/npc/npc_sprites/bangsawan/
```

Animasi aktivitas:

- `melambai_agung`
- `pose_bangga`

Interaksi gameplay:

- Pemberi quest besar, sponsor depot, atau pemicu keputusan reputasi.
- `melambai_agung`: menyambut karavan setelah reputasi cukup.
- `pose_bangga`: idle setelah interaksi atau event selesai.

## 5. Pola Interaksi NPC dan Prop

NPC yang memakai prop tidak menjadikan prop sebagai child dari AnimatedSprite2D jika prop harus tetap stabil di dunia. Gunakan struktur berikut:

```text
WorkStation (Node2D)
├── NPC
├── Prop (Sprite2D)
├── WorkPoint (Marker2D)
└── InteractionArea (Area2D)
```

Jika NPC bergerak bersama prop, parent keduanya ke `WorkStation`, bukan membuat prop menjadi child dari frame sprite.

Alasan:

- Prop tidak ikut berputar atau bergeser saat frame sprite berubah.
- Posisi prop dapat diatur dengan marker.
- NPC dapat diganti tanpa merusak prop.
- Satu prop dapat dipakai untuk beberapa NPC secara terkontrol.

Untuk prop yang hanya merupakan bagian visual tangan dan sudah menyatu di sprite sheet, jangan menambahkan sprite alat kedua.

## 6. State Machine Umum NPC

Gunakan state yang sama untuk semua NPC, lalu isi aktivitas sesuai role:

```text
IDLE
  -> WANDER
  -> MOVE_TO_WORKPOINT
  -> WORKING
  -> TALKING
  -> RESPONDING
  -> RETURNING
  -> IDLE
```

Aturan state:

- `IDLE`: memainkan `diam`.
- `WANDER`: memilih titik aman dan memainkan `jalan`.
- `MOVE_TO_WORKPOINT`: bergerak ke marker prop atau station.
- `WORKING`: memainkan animasi role seperti `cangkul`, `menempa`, atau `menebang`.
- `TALKING`: memainkan `ngobrol` dan membuka dialog jika player berinteraksi.
- `RESPONDING`: memainkan animasi khusus seperti `melambai` atau `memberkati`.
- `RETURNING`: kembali ke posisi kerja, rumah, atau depot.

Jangan membuat semua NPC berjalan setiap frame secara acak. Aktivitas NPC sebaiknya dipicu oleh jadwal, event, depot, quest, atau turn.

## 7. Interaksi Player dengan NPC

Setiap NPC interaktif dapat memiliki `InteractionArea`.

Alur:

```text
Player masuk InteractionArea
  -> tampilkan prompt interaksi
  -> player menekan tombol interaksi
  -> NPC memainkan ngobrol atau animasi respons
  -> dialog atau menu quest terbuka
  -> keputusan mengubah GameState
```

Data interaksi minimum:

```text
NPCInteractionData
├── npc_id: String
├── role: String
├── available_dialogue: Array[String]
├── available_quests: Array[String]
├── required_reputation: int
├── required_turn: int
└── activity_result: Dictionary
```

NPC tidak boleh langsung mengubah gold, cargo, reputasi, atau turn hanya karena player menyentuh area. Perubahan harus terjadi setelah pilihan atau aktivitas selesai.

## 8. Hubungan dengan Sistem Turn

Aktivitas kerja dapat memakai dua model:

### Model A: Animasi Real-time, Hasil per Turn

NPC memainkan animasi selama perjalanan. Saat turn selesai, sistem menghitung hasil kerja.

Contoh:

```text
Turn 2: petani bekerja
Turn 3: tanaman selesai tumbuh
Turn 4: hasil panen tersedia
```

### Model B: Satu Aktivitas Menghabiskan Satu Turn

Player memilih aktivitas, animasi dimainkan, lalu satu turn berkurang setelah aktivitas selesai.

Contoh:

```text
Pilih menebang pohon
  -> animasi menebang
  -> pohon tumbang
  -> kayu +5
  -> conservation_score -1
  -> turn +1
```

Untuk game jam, gunakan Model B pada interaksi penting karena lebih mudah diuji dan lebih jelas bagi pemain.

## 9. Particle dan Animasi Prop

Particle hanya dipakai pada event visual yang jelas:

- Pohon tumbang: particle debu/daun setelah final shake.
- Pandai besi: particle percikan api ketika hit menempa.
- Tukang roti: particle tepung saat menguleni.
- Petani: particle tanah saat mencangkul.
- Penjaga gerbang: particle hanya jika ada event benturan atau serangan.

Semua particle harus:

- menggunakan `one_shot` untuk efek sekali jalan;
- dipicu dari event gameplay atau hit frame;
- tidak aktif terus-menerus tanpa alasan;
- memakai filter `Nearest` untuk pixel art;
- memiliki posisi marker yang stabil.

## 10. Checklist Implementasi DeepSeek

Sebelum membuat kode:

- [ ] Baca scene `.tscn` yang diminta user.
- [ ] Verifikasi nama root node dan child node.
- [ ] Verifikasi lokasi asset NPC dan prop.
- [ ] Verifikasi nama animasi dari SpriteFrames.
- [ ] Verifikasi apakah prop sudah child scene atau harus dibuat instance.
- [ ] Tanyakan scene atau path jika informasi belum cukup.

Saat membuat kode:

- [ ] Kerjakan satu NPC atau satu sistem kecil per tahap.
- [ ] Mulai dari lumberjack dan pohon sebelum NPC lain.
- [ ] Jangan mengubah semua `.tscn` sekaligus.
- [ ] Jangan membuat nama animasi baru jika animasi aktual sudah tersedia.
- [ ] Jangan menghapus perubahan user pada scene atau script.
- [ ] Jangan mencampurkan sistem turn, quest, dan dialog sebelum aktivitas dasar berhasil.

Setelah membuat kode:

- [ ] Uji NPC dapat idle.
- [ ] Uji NPC dapat bergerak ke WorkPoint.
- [ ] Uji animasi kerja sesuai role.
- [ ] Uji prop berada di belakang NPC dan tidak ikut bergeser.
- [ ] Uji particle hanya muncul pada event yang benar.
- [ ] Uji pohon bergetar setiap tebasan.
- [ ] Uji final shake, pohon menghilang, dan particle keluar.
- [ ] Uji hasil resource dan perubahan turn.
- [ ] Laporkan file yang diubah dan test yang dilakukan.

## 11. Urutan Implementasi yang Disarankan

1. `npc_lumberjack_men.tscn` + `prop_balok_kayu.png` + pohon dummy.
2. State `MOVE_TO_WORKPOINT` dan `WORKING`.
3. Hit timing, shake pohon, final shake, hide, dan particle.
4. Resource kayu dan perubahan turn.
5. `npc_blacksmith.tscn` + `prop_landasan.png`.
6. `npc_bakery.tscn` + `prop_meja_adonan.png`.
7. `npc_farmer_men.tscn` + `prop_tanah_olahan.png`.
8. `npc_librarian.tscn` + `prop_rak_buku.png`.
9. NPC sosial dan NPC tanpa prop.
10. Dialog, quest depot, reputasi, dan sistem pelestarian.

DeepSeek harus berhenti setelah tahap yang diminta user selesai dan tidak langsung mengimplementasikan seluruh daftar di atas.
