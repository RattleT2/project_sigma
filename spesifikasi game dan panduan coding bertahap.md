# Spesifikasi Game dan Panduan Coding Bertahap

## 1. Identitas Game

Game ini adalah game perjalanan karavan 2D dengan inspirasi dari game manajemen perjalanan seperti Tiny Rails, tetapi menggunakan satu karavan kuda dan satu gerobak.

Tema utama game adalah **pulang dan melestarikan**. Pemain melakukan perjalanan dari depot ke depot, membantu memperbaiki serta memasok depot yang masih membutuhkan bantuan, lalu berusaha membawa karavan pulang dengan kondisi dunia yang lebih baik.

Tujuan pemain bukan hanya mencapai jarak terjauh. Pemain juga harus memilih keputusan yang membantu keberlangsungan depot, kuda, kargo, dan lingkungan perjalanan.

## 2. Sistem 10 Turn Decision

Satu permainan terdiri dari maksimal 10 turn keputusan. Perjalanan karavan dapat berjalan otomatis, tetapi pada titik tertentu pemain harus memilih keputusan.

Contoh alur satu turn:

1. Karavan melakukan perjalanan menuju depot atau event berikutnya.
2. Sistem menampilkan kondisi perjalanan dan kebutuhan depot.
3. Pemain memilih satu keputusan.
4. Keputusan mengubah resource, kondisi depot, reputasi, atau rute.
5. Turn berkurang satu.
6. Sistem menyimpan hasil keputusan dan melanjutkan perjalanan.

Contoh state global:

```text
GameState
├── current_turn: int
├── max_turns: int = 10
├── distance_km: float
├── gold: int
├── cargo: Dictionary
├── reputation: int
├── caravan_condition: int
├── horse_stamina: int
├── conserved_depots: int
└── completed_quests: Array[String]
```

Aturan dasar:

- `current_turn` dimulai dari 1.
- Pemain tidak dapat melakukan keputusan baru jika turn sudah mencapai 10.
- Setiap keputusan harus memiliki konsekuensi yang terlihat.
- Keputusan yang membantu depot dapat meningkatkan `reputation` dan `conserved_depots`.
- Perjalanan pulang atau ending ditentukan dari gabungan turn, kondisi karavan, dan jumlah depot yang berhasil dibantu.

## 3. Misi Depot

Setiap depot memiliki misi utama bertema resupply dan pelestarian depot lain.

Contoh misi:

- Mengirim kayu untuk memperbaiki depot tetangga.
- Mengantar makanan untuk pekerja depot.
- Mengirim suku cadang roda atau alat pandai besi.
- Membantu membersihkan jalur yang rusak.
- Mengantar benih atau perlengkapan untuk memulihkan lingkungan.
- Memilih apakah kargo dipakai untuk kebutuhan sendiri atau diberikan kepada depot lain.

Struktur data misi yang disarankan:

```text
QuestData
├── id: String
├── title: String
├── description: String
├── source_depot_id: String
├── target_depot_id: String
├── required_cargo: Dictionary
├── reward_gold: int
├── reputation_change: int
├── conservation_change: int
├── required_turn: int
└── status: String
```

Status misi dapat berupa:

```text
available -> accepted -> in_progress -> completed
available -> declined
accepted -> failed
```

Misi harus memiliki hubungan dengan depot. Jangan membuat quest hanya sebagai teks UI tanpa efek terhadap state game.

## 4. Makna Pulang dan Pelestarian

Tema pulang harus terlihat melalui progres game, bukan hanya melalui ending text.

Contoh indikator progres:

- Depot yang dibantu menjadi lebih hidup atau memiliki dekorasi baru.
- Jalur perjalanan menjadi lebih aman.
- Reputasi karavan meningkat.
- Kebutuhan depot berikutnya menjadi lebih mudah dipenuhi.
- Kondisi karavan dan stamina kuda tetap terjaga.
- Ending berubah berdasarkan jumlah depot yang berhasil dilestarikan.

Contoh hasil akhir:

| Kondisi | Ending |
|---|---|
| Banyak depot dibantu dan karavan sehat | Pulang dengan jaringan depot yang pulih |
| Depot cukup terbantu tetapi resource rendah | Pulang dengan perjalanan yang berat |
| Sedikit depot dibantu | Pulang, tetapi wilayah masih membutuhkan bantuan |
| Turn habis sebelum tujuan tercapai | Perjalanan berakhir dengan konsekuensi berdasarkan keputusan terakhir |

## 5. Rekomendasi Struktur Scene dan Script

Gunakan scene terpisah agar sistem mudah dikerjakan oleh beberapa anggota tim:

```text
scenes/
├── player_caravan.tscn
├── levels/
│   └── main_level.tscn
├── depots/
│   ├── depot.tscn
│   └── depot_event.tscn
├── events/
│   └── decision_event.tscn
└── ui/
	├── turn_hud.tscn
	├── depot_quest_ui.tscn
	└── decision_ui.tscn

scripts/
├── player_caravan.gd
├── game_state.gd
├── turn_manager.gd
├── quest_manager.gd
├── depot_manager.gd
└── event_manager.gd

resources/
├── quests/
├── depots/
└── events/
```

`GameState` dapat dijadikan Autoload jika memang dibutuhkan oleh banyak scene. Data quest dan depot lebih baik dibuat sebagai `Resource` atau data terstruktur agar tidak seluruhnya hardcode di UI.

## 6. Urutan Implementasi yang Wajib

Pembuatan game harus dilakukan bertahap dan setiap tahap harus dapat diuji sebelum lanjut.

### Tahap 1: Player Caravan

Target scene: `player_caravan.tscn`

- Gerak karavan ke kanan.
- Collision dasar.
- Animasi kuda dan harness.
- Pantulan wagon.
- Rotasi roda.
- Debu dan audio jika aset sudah tersedia.

Jangan membuat sistem quest atau turn pada tahap ini.

### Tahap 2: Progress Map

Target scene: `main_level.tscn`

- Ground dan collision.
- Kamera.
- Background parallax.
- Jarak perjalanan.
- Pergantian zona berdasarkan jarak.
- Spawn environment dan landmark.

Pada akhir tahap ini, pemain harus dapat menguji perjalanan dari satu titik ke titik lain tanpa event quest.

### Tahap 3: Turn dan Game State

Target script: `game_state.gd` dan `turn_manager.gd`

- Turn dimulai dari 1 dan memiliki batas 10.
- Tombol atau fungsi untuk mengakhiri turn.
- Tampilan turn pada HUD.
- Penyimpanan resource dasar.
- Sinyal perubahan turn dan state.

### Tahap 4: Depot dan Resupply

Target scene: `depot.tscn` dan script `depot_manager.gd`

- Area interaksi depot.
- Data kebutuhan depot.
- Misi resupply.
- Perubahan kondisi depot setelah misi selesai.

### Tahap 5: Event dan Side Quest

Target scene: `decision_event.tscn` dan `depot_quest_ui.tscn`

- Daftar pilihan keputusan.
- Konsekuensi setiap keputusan.
- Misi membantu depot lain.
- Reward, reputasi, dan nilai pelestarian.
- Kondisi berhasil atau gagal.

### Tahap 6: Ending dan Balancing

- Kondisi pulang.
- Ending berdasarkan keputusan pemain.
- Validasi batas 10 turn.
- Balancing resource, jarak, reward, dan tingkat kesulitan.

## 7. Catatan untuk DeepSeek atau AI Coding Assistant

Gunakan aturan berikut saat meminta bantuan coding:

> Sebelum menulis kode, baca dan gunakan file `.tscn` yang disebutkan oleh user. Pastikan nama node, path node, tipe node, signal, dan struktur scene sesuai dengan isi file tersebut. Jangan mengarang path node berdasarkan asumsi.

> Kerjakan game secara bertahap. Jangan langsung membuat seluruh sistem game dalam satu jawaban. Implementasikan hanya tahap yang diminta user, mulai dari `player_caravan.tscn`, lalu `main_level.tscn` dan progress map, kemudian sistem turn, depot, event side quest, dan ending.

> Sebelum mengedit file, jelaskan file mana yang akan diubah dan mengapa. Jika struktur `.tscn` belum tersedia atau nama node belum jelas, minta user mengirimkan isi scene atau screenshot Scene Tree terlebih dahulu.

> Setelah coding, berikan langkah pengujian yang hanya berkaitan dengan tahap tersebut. Jangan menambahkan fitur yang belum diminta, jangan membuat ulang seluruh arsitektur, dan jangan mengubah scene lain tanpa persetujuan user.

Checklist untuk setiap bantuan coding:

- [ ] File `.tscn` yang diminta sudah dibaca.
- [ ] Path node sesuai dengan scene aktual.
- [ ] Nama script dan lokasi file sesuai struktur project.
- [ ] Perubahan hanya mencakup tahap yang diminta.
- [ ] Tidak ada sistem baru yang belum diperlukan.
- [ ] Ada langkah pengujian setelah perubahan.
- [ ] Error atau asumsi yang belum terverifikasi disebutkan dengan jelas.

## 8. Batasan Scope Game Jam

Prioritaskan vertical slice yang dapat dimainkan:

1. Karavan dapat bergerak.
2. Map memiliki pergantian zona.
3. Pemain memiliki 10 turn keputusan.
4. Depot memiliki satu misi resupply.
5. Pemain dapat membantu depot lain.
6. Ada konsekuensi keputusan dan ending pulang.

Fitur tambahan seperti banyak tipe wagon, multiplayer, procedural world tanpa batas, atau sistem ekonomi kompleks ditunda sampai alur utama sudah stabil.

