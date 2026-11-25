# Spesifikasi Teknis & Instruksi Pembuatan Script NPC (Godot 4)

Dokumen ini berisi konteks arsitektur game, hierarki node, standar animasi, dan spesifikasi logika AI/State Machine untuk sistem NPC dan WorkProps. Gunakan dokumen ini sebagai referensi utama untuk mengeksekusi penulisan script GDScript (`.gd`).

## 1. Gambaran Umum & Konsep Game

* **Engine:** Godot 4.x (GDScript 2.0, 2D Side-Scrolling).

* **Referensi Mekanik Utama:** *Tiny Rails* (Management & Exploration).

* **Alur Permainan:**

  * Pemain mengendalikan sebuah **Karavan Kuda (`Player_Caravan`)** yang bergerak secara horizontal (kiri ke kanan) melintasi berbagai wilayah/kota pada map 2D side-scrolling.

  * Di sepanjang perjalanan atau di titik pemberhentian (kota, bengkel, depot), terdapat **14 jenis NPC** dengan berbagai profesi.

  * NPC dapat melakukan aktivitas harian secara mandiri di sekitar posnya (diam, berjalan mondar-mandir, mengobrol, melambai saat karavan mendekat, hingga berjalan mendatangi meja/alat kerjanya untuk bekerja).

  * Beberapa NPC memiliki keahlian/profesi yang memberikan *buff* pasif atau dapat diajak berinteraksi/direkrut sebagai penumpang/kru karavan (misal: bonus kecepatan, diskon dagang, regenerasi stamina kuda, atau kecepatan perbaikan gerobak).

## 2. Daftar 14 Profesi NPC & Keahliannya

Semua NPC menggunakan basis logika yang sama namun dibedakan oleh data profesi/keahliannya:

 1. `anak` (Warga - interaksi sosial/quest ringan)

 2. `bangsawan` (Bonus harga jual barang / prestise)

 3. `pedagang` (Diskon transaksi & pertukaran kargo)

 4. `pemanah` (Keamanan perjalanan / pengawalan)

 5. `pendeta` (Bonus pemulihan moral / stamina)

 6. `penebang_kayu` / `lumberjack` (Prop: Balok kayu `Log` - bonus bahan bakar/kayu perbaikan)

 7. `penjaga_gerbang` (Akses wilayah / informasi rute)

 8. `pandai_besi` / `blacksmith` (Prop: Landasan tempa - upgrade & perbaikan gerobak)

 9. `petani_pria` (Prop: Tanah olahan - suplai bahan pangan)

10. `petani_wanita` (Prop: Tanah olahan - suplai bahan pangan)

11. `pustakawan` (Prop: Rak buku - petunjuk rute & lore)

12. `tukang_roti` / `bakery` (Prop: Meja adonan - makanan penambah stamina kuda)

13. `warga_pria` (Warga umum / penumpang)

14. `warga_wanita` (Warga umum / penumpang)

## 3. Standar Hierarki Node & Titik Pivot

### A. Aturan Titik Pijakan (Pivot) & Offset Posisi

* Seluruh scene NPC dan Props menggunakan garis koordinat **`Y = 0` sebagai permukaan tanah/lantai**.

* Pada seluruh scene NPC, node `AnimatedSprite2D` diposisikan pada **`Position = Vector2(0, -25.0)`** sehingga ujung telapak kaki karakter menapak tepat di garis lantai `Y = 0`.

* Bagian bawah visual prop dan kedua node `Marker2D` (`WorkSpot`) juga disejajarkan pada `Y = 0`. Dengan demikian, saat NPC berpindah ke koordinat `global_position` milik `WorkSpot`, kaki NPC dan dasar prop langsung sejajar secara vertikal tanpa perlu koreksi offset tambahan di dalam kode.

### B. Struktur Scene Prop Kerja (`work_prop_npc_*.tscn`)

Prop dipisahkan dari `CharacterBody2D` NPC agar tidak ikut terseret saat NPC berjalan mondar-mandir, serta agar NPC dapat berjalan mendatangi prop saat waktunya bekerja. Prop **tidak menggunakan collision fisik** agar tidak menghalangi laju `Player_Caravan`.

```
WorkProp_NPC_[Profesi] (Node2D)               # Root Prop (Script: work_prop.gd)
├── [NamaSpriteProp] (Sprite2D)               # Visual prop di titik tengah (X = 0), bagian bawah di Y = 0
├── WorkSpot_for_npc_standing_facing_right (Marker2D) # Titik berdiri sisi KIRI prop (Y = 0, NPC hadap KANAN)
├── WorkSpot_for_npc_standing_facing_left (Marker2D)  # Titik berdiri sisi KANAN prop (Y = 0, NPC hadap KIRI)
└── [NamaAudioProp] (AudioStreamPlayer2D)     # Efek suara saat prop digunakan (misal: kapak/palu)

```

### C. Struktur Scene Karakter NPC (`npc_*.tscn`)

```
NPC_Root (CharacterBody2D)                    # Root NPC di Y = 0 (Script: npc_controller.gd)
├── AnimatedSprite2D                          # Position: (0, -25.0). (Catatan: beberapa scene lama masih bernama [profesi]_movement, gunakan pencarian tipe node atau fallback di script)
├── CollisionShape2D                          # Collision kaki ke tanah dengan tepi bawah rata di Y = 0 (tidak bertabrakan dengan Player_Caravan)
├── InteractionArea (Area2D)                  # Deteksi jarak dekat dengan Player_Caravan
│   └── CollisionShape2D                      # Area sensor melebar kiri-kanan
├── Label                                     # Indikator teks/ikon interaksi (Default: visible = false)
├── AudioStreamPlayer2D                       # Efek suara sapaan / aktivitas NPC
└── Timer                                     # Timer siklus pergantian aktivitas (StateTimer)

```

## 4. Standar Nama Animasi (`AnimatedSprite2D`)

Script harus mendukung pemetaan animasi standar maupun fallback jika nama animasi masih memakai prefix profesi:

* **Animasi Umum:**

  * `diam` / `idle`

  * `jalan` / `walk`

  * `lari` / `run`

  * `melambai` / `wave` (Dipicu saat `Player_Caravan` memasuki `InteractionArea`)

  * `melompat` / `jump`

  * `ngobrol` / `talk`

* **Animasi Kerja Khusus (Saat berada di `WorkSpot` Prop):**

  * `work` (atau spesifik seperti `cutting_tree`, `caryy_log`, menempa, menguleni adonan).

## 5. Instruksi Script yang Harus Dieksekusi

Buatkan **3 file script GDScript 2.0 (Godot 4)** yang bersih, modular, dan siap pakai dengan ketentuan berikut:

### Script 1: `work_prop.gd` (Dipasang pada Root `WorkProp_NPC_*`)

* Menggunakan `@onready` untuk mereferensikan dua `Marker2D` (`WorkSpot_for_npc_standing_facing_right` dan `WorkSpot_for_npc_standing_facing_left`) serta `AudioStreamPlayer2D` (opsional/aman jika nama node berbeda dengan `find_child`).

* Menyediakan fungsi publik:

  1. `get_nearest_spot(npc_global_pos: Vector2) -> Marker2D`: Mengembalikan `Marker2D` terdekat dari posisi NPC saat ini.

  2. `get_random_spot() -> Marker2D`: Memilih secara acak sisi kiri atau kanan prop agar gerakan NPC terlihat alami dan tidak monoton di satu sisi saja.

  3. `play_work_sound() -> void`: Memutar `AudioStreamPlayer2D` prop (dipanggil saat frame aksi kerja NPC mengenai prop).

### Script 2: `npc_data.gd` (`class_name NPCData extends Resource`)

* Menyimpan metadata profesi NPC agar mudah dikustomisasi via Inspector tanpa mengubah kode:

  * `@export var npc_name: String`

  * `@export var profession_id: String`

  * `@export var skill_description: String`

  * `@export_group("Caravan Buffs")`

  * `@export var speed_bonus: float = 0.0`

  * `@export var trade_discount: float = 0.0`

  * `@export var stamina_regen_bonus: float = 0.0`

  * `@export var repair_bonus: float = 0.0`

  * `@export_group("Animation Names")` -> memungkinkan override nama animasi kerja spesifik tiap profesi (default `"work"`).

### Script 3: `npc_controller.gd` (Dipasang pada `CharacterBody2D` NPC)

* **Variabel `@export` di Inspector:**

  * `@export var npc_data: NPCData`

  * `@export var target_prop: Node2D` (Opsional: jika diisi, NPC memiliki rutinitas berjalan ke prop untuk bekerja; jika kosong, NPC hanya melakukan patroli jalan santai, diam, dan interaksi).

  * `@export var walk_speed: float = 35.0`

  * `@export var patrol_range: float = 60.0` (Batas jarak jalan mondar-mandir dari titik awal spawn `start_position.x`).

  * `@export var sprite_faces_right_by_default: bool = true` (Untuk kontrol `flip_h`).

* **State Machine (`enum State`):**

  1. `IDLE`: NPC berdiri diam (`idle`/`diam`), menunggu `Timer` selesai untuk memilih state berikutnya (`PATROL` atau `WALK_TO_PROP`).

  2. `PATROL`: NPC berjalan santai ke titik acak di dalam rentang `patrol_range` dari posisi awalnya.

  3. `WALK_TO_PROP`: NPC meminta titik `Marker2D` dari `target_prop` (misal `get_random_spot()`), berjalan menuju koordinat X `Marker2D` tersebut, menyesuaikan `flip_h` sesuai arah jalan, dan ketika jaraknya `< 2.0` px langsung berhenti tepat di titik tersebut lalu masuk ke state `WORKING`.

  4. `WORKING`: NPC berdiri diam di `WorkSpot`, otomatis mengarahkan pandangan (`flip_h`) menghadap ke pusat `target_prop.global_position.x`, lalu memainkan animasi kerja selama durasi tertentu sebelum kembali ke `IDLE` atau `PATROL`.

  5. `GREET_CARAVAN`: Dipicu ketika node dalam grup `"player_caravan"` (atau bernama `"Player_Caravan"`) memasuki `InteractionArea`. NPC menghentikan aktivitasnya sejenak, menghadap ke arah karavan, memunculkan node `Label` interaksi, dan memainkan animasi melambai (`melambai` / `wave`). Ketika karavan menjauh (`body_exited`), `Label` disembunyikan dan NPC kembali ke rutinitas normal.

* **Ketentuan Tambahan:**

  * Terapkan gravitasi standar Godot 4 (`get_gravity()`) agar `CharacterBody2D` tetap menapak di atas `TileMapLayer` tanah.

  * Gunakan helper function pemutar animasi yang aman (`play_anim_safe`) yang mengecek daftar nama alternatif (misal mengecek `"idle"`, lalu `"diam"`, atau animasi yang mengandung kata `"idle"`/`"diam"`) agar tidak terjadi error jika ada perbedaan penamaan antar scene NPC.

  * Sertakan komentar penjelasan singkat di bagian atas setiap script mengenai cara menghubungkan node & sinyal di editor Godot 4.