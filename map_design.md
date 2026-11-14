# Map Design

## 1. Konsep Utama

Game menggunakan lima area tetap yang dipilih player pada awal setiap turn:

- Forest
- Snow
- Village
- Desert
- Castle

Karavan tidak mengikuti perjalanan linear. Player memilih satu area atau depot
sebagai tujuan setiap turn. Perjalanan menggunakan jaringan node dan rute
antar-node. Setiap rute memiliki jarak, biaya perjalanan, dan peluang encounter.

Tujuan utama player adalah menstabilkan sedikitnya tiga area sebelum jumlah turn
habis.

## 2. Fungsi Area

Setiap area memiliki kebutuhan resource yang sama:

- Iron
- Diamond
- Coin

Pada area yang dikunjungi, player membagikan resource yang dibawa karavan.
Area kemudian memberikan coin sebagai imbalan. Coin yang diperoleh digunakan di
depot untuk mengisi resource, membeli upgrade, dan membeli skin.

Layout area bersifat tetap. Variasi visual seperti batu, pohon, semak, dan
dekorasi lain dapat ditentukan menggunakan RNG dari pool area tersebut.

## 3. Struktur Map dan Rute

Map menggunakan graph node, bukan koordinat jarak linear:

```text
					Snow
				   /    \
			  Forest      Village
				   \    /     \
					Desert --- Castle
```

Contoh struktur data rute:

```text
Route
├── from_area
├── to_area
├── distance
├── travel_cost
└── bandit_risk
```

Aturan rute:

- Player hanya dapat memilih area yang terhubung dengan posisi karavan.
- Perpindahan area memerlukan biaya.
- Semakin jauh rute, semakin besar biaya perjalanan.
- Semakin jauh rute, semakin tinggi peluang bertemu bandit.
- Depot dapat ditempatkan sebagai node khusus yang dapat diakses dari rute
  tertentu atau dari semua area, sesuai kebutuhan level.

Contoh perhitungan sederhana:

```text
travel_cost = base_cost + (distance * cost_per_distance)
bandit_risk = base_risk + (distance * risk_per_distance)
```

Nilai tersebut sebaiknya disimpan pada data rute agar mudah diseimbangkan,
bukan ditulis terpisah di setiap scene area.

## 4. Struktur Scene Godot

Gunakan satu scene utama untuk mengatur game dan satu scene mandiri untuk setiap
area:

```text
GameScene (Node2D)
├── AreaManager
├── RouteManager
├── TurnManager
├── ResourceManager
├── CurrentArea (Node2D)
├── PlayerCaravan (CharacterBody2D)
├── Depot
└── UI (CanvasLayer)
```

Scene area:

```text
areas/
├── forest.tscn
├── snow.tscn
├── village.tscn
├── desert.tscn
└── castle.tscn
```

Contoh struktur scene area:

```text
Forest (Node2D)
├── Background
├── Ground
│   ├── GroundVisual
│   └── GroundCollision
├── EnvironmentProps
├── Landmarks
└── SpawnPoints
```

Tanggung jawab sistem:

- `AreaManager`: memuat, mengganti, dan menghapus scene area aktif.
- `RouteManager`: menyediakan node tujuan, jarak, biaya, dan risiko rute.
- `TurnManager`: mengatur fase turn dan jumlah turn yang tersisa.
- `ResourceManager`: mengatur resource karavan dan resource setiap area.
- `Depot`: menangani pengisian resource, upgrade, income, dan pembelian skin.
- `PlayerCaravan`: menjalankan perjalanan dan menyimpan efek sementara.

Hanya satu area gameplay yang perlu aktif pada satu waktu. Data progres area
disimpan oleh `ResourceManager`, bukan bergantung pada node visual scene.

## 5. Alur Turn

```text
Turn dimulai
	↓
Player memilih area atau depot
	↓
Validasi rute dan biaya perjalanan
	↓
Karavan memulai perjalanan
	↓
Encounter atau efek perjalanan diproses
	↓
Transisi ke scene tujuan
	↓
Player melakukan aksi di area atau depot
	↓
Resource area diperbarui
	↓
Kondisi menang/kalah diperiksa
	↓
Turn berikutnya
```

Player memiliki dua jenis pilihan utama:

1. Memilih salah satu dari lima area.
2. Pergi ke depot.

Biaya perjalanan dibayar saat perjalanan dimulai. Jika resource atau coin tidak
mencukupi, tujuan tersebut tidak dapat dipilih.

## 6. Transisi Antar-Area

Perpindahan tidak boleh langsung mengganti scene tanpa konteks perjalanan.
Gunakan fase transisi:

```text
Area asal
	↓
Karavan bergerak di area asal
	↓
Fade, overlay, atau transition effect
	↓
Scene area tujuan dimuat
	↓
Karavan muncul di area tujuan
	↓
Turn dilanjutkan
```

Karavan tetap terlihat berada di area asal untuk beberapa saat setelah player
memilih tujuan. Setelah itu transisi memindahkan karavan ke area tujuan.

```text
TravelController
├── origin_area
├── destination_area
├── route_distance
├── travel_cost
└── transition_duration
```

Scene asal dan tujuan tidak perlu aktif bersamaan kecuali transisi visual
memerlukannya. Untuk versi sederhana, tahan scene asal selama animasi, lalu
muat scene tujuan setelah overlay menutupinya.

## 7. Resource Karavan dan Area

### Resource Karavan

Karavan membawa:

- Iron
- Diamond
- Coin

Kapasitas setiap resource dikendalikan oleh kapasitas karavan. Resource yang
dibawa dapat berkurang karena:

- Dibagikan kepada area.
- Dibayar sebagai biaya perjalanan.
- Hilang sebagian setelah karavan kalah dari bandit.
- Digunakan di depot.

### Resource Area

Setiap area menyimpan progres kebutuhan resource dan status stabilitas.
Resource area berkurang secara acak pada setiap turn yang dimainkan.

Area yang baru saja dikunjungi mendapat perlindungan selama dua turn. Pengurangan
resource area baru dimulai setelah dua turn berlalu sejak kunjungan tersebut.

Contoh state area:

```text
AreaState
├── iron
├── diamond
├── coin
├── stability
├── turns_since_visit
└── is_stable
```

Aturan pembaruan:

1. Area menerima resource dari karavan.
2. Area mendapatkan coin sesuai resource yang berhasil dibagikan.
3. Counter kunjungan area di-reset.
4. Pada akhir turn, resource area lain berkurang secara acak.
5. Area yang counter-nya belum melewati dua turn tidak mengalami pengurangan.
6. Status `is_stable` diperbarui berdasarkan batas kebutuhan area.

Detail nilai kebutuhan, jumlah pengurangan, dan reward harus berupa data yang
mudah diubah untuk balancing.

## 8. Depot

Depot adalah tujuan khusus yang menyediakan:

- Pengisian Iron, Diamond, dan Coin karavan.
- Upgrade kapasitas atau kemampuan karavan.
- Pengambilan income dari area yang telah dikunjungi.
- Pembelian skin kuda.
- Pembelian skin gerobak karavan.

Depot tidak dihitung sebagai area yang harus distabilkan. Aksi depot tetap
menghabiskan satu turn, dan resource area tetap diperbarui pada akhir turn.

## 9. Encounter dan Efek Sementara

### Bandit

Encounter bandit dipicu berdasarkan jarak rute. Rute yang lebih jauh memiliki
peluang lebih tinggi untuk memicu encounter.

Saat encounter terjadi:

1. Game menentukan apakah karavan selamat berdasarkan peluang rute.
2. Jika selamat, perjalanan dilanjutkan tanpa kehilangan resource.
3. Jika tidak selamat, sebagian resource yang dibawa karavan berkurang.
4. Karavan tetap tiba di tujuan kecuali desain encounter menetapkan hasil lain.

Nilai peluang dan jumlah resource yang hilang harus dikonfigurasi pada data rute
atau konfigurasi encounter.

### Efek Sementara

Encounter atau kondisi tertentu dapat memberikan efek sementara kepada karavan,
misalnya:

- Kapasitas maksimum resource meningkat selama dua turn.
- Biaya perjalanan berkurang selama beberapa turn.
- Peluang selamat dari bandit meningkat selama beberapa turn.

Setiap efek memiliki:

```text
CaravanEffect
├── effect_type
├── value
└── remaining_turns
```

Efek diproses pada awal atau akhir turn secara konsisten, lalu durasinya
dikurangi. Efek dihapus saat `remaining_turns` mencapai nol.

## 10. Kondisi Menang dan Kalah

Jumlah turn terbatas. Pada akhir turn terakhir:

- **Menang** jika jumlah area dengan status stabil minimal tiga.
- **Kalah** jika jumlah area stabil kurang dari tiga.

Pemeriksaan kondisi dilakukan setelah resource area diperbarui agar hasil turn
terakhir ikut dihitung.

```text
stable_area_count >= 3  -> Victory
stable_area_count < 3   -> Defeat
```

## 11. RNG Environment

RNG hanya digunakan untuk variasi dekorasi pada area aktif. RNG tidak boleh
mengubah:

- Layout utama.
- Jaringan rute.
- Posisi landmark penting.
- Jalur aman karavan.
- Status resource atau stabilitas tanpa melalui sistem game.

Contoh pool:

```text
forest_environment_pool =
[
	tree,
	bush,
	rock,
	mushroom
]

snow_environment_pool =
[
	pine_tree,
	snow_pile,
	ice_rock
]
```

Pool lain dibuat untuk Village, Desert, dan Castle. Setiap scene area dapat
memiliki `SpawnPoints` agar dekorasi tidak menutup jalur karavan.

## 12. Struktur Folder yang Disarankan

```text
scenes/
├── game/
│   ├── game_scene.tscn
│   ├── turn_manager.gd
│   ├── area_manager.gd
│   ├── route_manager.gd
│   ├── resource_manager.gd
│   └── travel_controller.gd
├── areas/
│   ├── forest.tscn
│   ├── snow.tscn
│   ├── village.tscn
│   ├── desert.tscn
│   └── castle.tscn
└── depot/
	└── depot.tscn

data/
├── areas/
├── routes/
├── encounters/
└── caravan/

assets/
├── background/
│   ├── forest/
│   ├── snow/
│   ├── village/
│   ├── desert/
│   └── castle/
├── ground/
├── environment/
└── caravan/
```

Data area dan rute sebaiknya dipisahkan dari scene agar balancing resource,
biaya, jarak, risiko, dan reward tidak memerlukan perubahan layout.

## 13. Checklist Map Designer

- [ ] Lima scene area tersedia: Forest, Snow, Village, Desert, Castle.
- [ ] Setiap area memiliki layout tetap dan collision yang aman.
- [ ] Setiap area memiliki pool dekorasi RNG sendiri.
- [ ] Jaringan node dan rute antar-area sudah ditentukan.
- [ ] Setiap rute memiliki jarak, biaya, dan risiko bandit.
- [ ] Transisi area menampilkan perjalanan singkat dari area asal.
- [ ] Scene area tidak menyimpan progres resource secara langsung.
- [ ] Resource area dapat berkurang setiap turn setelah masa perlindungan dua turn.
- [ ] Depot menyediakan refill, upgrade, income, dan skin.
- [ ] Efek sementara memiliki durasi turn yang jelas.
- [ ] Kondisi menang memerlukan minimal tiga area stabil.
- [ ] Kondisi kalah diperiksa setelah turn terakhir selesai.
- [ ] Jalur karavan tidak tertutup dekorasi atau landmark.

## 14. Kesimpulan

Gunakan satu `GameScene` sebagai pengatur turn, state, karavan, depot, dan
perpindahan. Gunakan satu scene mandiri untuk setiap area. Player memilih
tujuan setiap turn melalui jaringan rute, membayar biaya berdasarkan jarak, lalu
melalui transisi sebelum tiba di area tujuan.

Layout area tetap membuat navigasi mudah dipahami, sedangkan RNG dekorasi
memberikan variasi visual. State resource dan stabilitas disimpan secara
terpisah dari scene sehingga progres area tetap ada ketika player berpindah.
