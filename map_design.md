# Map Design

## 1. Konsep Utama

Game menggunakan lima titik tetap pada peta:

- Depot (tengah peta)
- Snow (timur laut)
- Forest (timur)
- Desert (selatan)
- Village & Castle (barat, satu area dan satu scene)

Empat titik adalah area yang dapat distabilkan. Depot adalah pangkalan, bukan
area yang perlu distabilkan.

Karavan tidak mengikuti perjalanan linear. Player bebas memilih area mana pun
atau depot sebagai tujuan setiap turn; tidak ada rute yang terkunci. Setiap
tujuan memiliki jarak, biaya perjalanan, dan peluang encounter sendiri.

Tujuan utama player adalah menstabilkan sedikitnya tiga dari empat area sebelum
jumlah turn habis.

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

Map menampilkan lima wilayah tetap. Player dapat memilih semua wilayah dari
posisi karavan saat ini (bebas, tanpa jaringan rute tetap):

```text
	Village & Castle        Snow
				 Depot
			Desert          Forest
```

Posisi di atas hanya menggambarkan tata letak peta, bukan pembatas rute.

Contoh struktur data per tujuan:

```text
Route
├── to_area
├── distance
├── travel_cost
└── bandit_risk
```

Aturan rute:

- Semua area dan depot selalu dapat dipilih selama biaya perjalanan tercukupi.
- Perpindahan memerlukan biaya coin.
- Semakin jauh tujuan dari posisi karavan, semakin besar biaya perjalanan.
- Semakin jauh tujuan, semakin tinggi peluang bertemu bandit.
- Jarak dapat dihitung dari jarak posisi wilayah pada peta (lalu dibulatkan)
  atau disimpan sebagai angka tetap per tujuan.
- Wilayah tempat karavan berada tidak dapat dipilih sebagai tujuan.

Contoh perhitungan sederhana:

```text
travel_cost = base_cost + (distance * cost_per_distance)
bandit_risk = base_risk + (distance * risk_per_distance)
```

Nilai tersebut sebaiknya disimpan sebagai data route agar mudah diseimbangkan,
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

Scene area (folder `scenes/map/`):

```text
scenes/map/
├── forest.tscn
├── snow.tscn
├── village.tscn   # Village & Castle, satu area
└── desert.tscn
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

## 5. Menu Map Awal Turn

Menu map ditampilkan setiap kali turn baru dimulai. Menu ini menjadi layar
pemilihan tujuan sebelum player melakukan perjalanan ke area atau depot.
Player memilih wilayah langsung pada peta: tidak ada ikon atau tombol node.
Wilayah yang diarahkan kursor akan ter-highlight.

Implementasi saat ini: `scenes/map/map_menu.tscn` (root `Control`) dengan
`scripts/map/region_button.gd` untuk hover dan klik wilayah.

### Informasi yang Ditampilkan

Menu map menampilkan:

- Lima wilayah: Depot, Snow, Forest, Desert, dan Village & Castle.
- Posisi karavan saat ini (banner di atas wilayah).
- Garis rute dari karavan ke setiap tujuan.
- Status wilayah: stabil atau belum stabil.
- Detail Iron, Diamond, dan Coin pada wilayah yang dipilih.
- Biaya perjalanan menuju wilayah yang dipilih.
- Risiko encounter bandit pada rute yang dipilih.
- Jumlah turn yang tersisa.
- Resource karavan saat ini dan kapasitas maksimumnya.
- Depot sebagai tujuan alternatif.

Gunakan tampilan resource hybrid:

- Peta menampilkan bentuk wilayah dan namanya. Hover memberi highlight dan
  garis rute tujuan menjadi emas.
- Panel detail menampilkan angka lengkap ketika player mengarahkan kursor atau
  memilih wilayah: kebutuhan Iron/Diamond/Coin, status stabil, jarak, biaya,
  risiko, dan alasan jika tujuan tidak dapat dipilih.

### Struktur Scene UI

Menu map dibuat sebagai `Control` di dalam `CanvasLayer`:

```text
MapMenu (Control)
├── SeaColor (ColorRect)
├── MapBoard (Control, gambar peta 2048x2048 yang di-scale)
│   ├── MapArt (TextureRect)
│   ├── Regions (Control)
│   │   ├── VillageCastle (RegionButton)
│   │   │   ├── Highlight (Polygon2D)
│   │   │   ├── Outline (Line2D)
│   │   │   ├── NameLabel (Label)
│   │   │   └── Anchor (Marker2D)
│   │   ├── Desert (RegionButton)
│   │   ├── Forest (RegionButton)
│   │   ├── Snow (RegionButton)
│   │   └── Depot (RegionButton)
│   ├── RouteLines (Node2D)
│   │   ├── ToVillage, ToSnow, ToForest, ToDesert, ToDepot (Line2D)
│   └── CaravanMarker (TextureRect, banner_purple.png)
├── TopBar (PanelContainer)
│   └── TurnSummary (TurnLabel, TurnsLeftLabel)
├── AreaDetailPanel (PanelContainer)
│   ├── AreaNameLabel, StableBadge
│   ├── IronRow, DiamondRow, CoinRow
│   ├── DistanceRow, CostRow, RiskRow
│   ├── ReasonLabel
│   └── ConfirmDestinationButton
└── CaravanSummary (PanelContainer)
	├── CaravanIron, CaravanDiamond, CaravanCoin
	├── CaravanCapacity (ProgressBar)
	└── CaravanEffect
```

`RegionButton` adalah `Control` dengan poligon wilayah. `_has_point()` memakai
`Geometry2D.is_point_in_polygon`, sehingga hover dan klik hanya aktif di dalam
bentuk wilayah, bukan kotak pembatasnya. Scene ini tidak menyimpan state game;
signal `region_hovered`, `region_unhovered`, dan `region_selected` diteruskan ke
`MapMenu`.

Poligon wilayah diambil dari bentuk daratan `Map.png`, lalu di-inset beberapa
piksel agar highlight tidak tumpah ke laut atau wilayah tetangga. Poligon bisa
disedit langsung di editor melalui node `Highlight` pada tiap wilayah.

`AreaDetailPanel` menampilkan detail area yang sedang dipilih. Isinya minimal
adalah jumlah Iron, Diamond, Coin, status stabilitas, biaya perjalanan, risiko
bandit, dan alasan jika tujuan tidak dapat dipilih.

`CaravanSummary` menampilkan resource karavan, kapasitas, efek sementara yang
aktif, dan posisi karavan. `TurnSummary` menampilkan nomor turn serta jumlah
turn yang tersisa.

### Alur Pemilihan Tujuan

```text
Turn dimulai
	↓
MapMenu mengambil state terbaru dari manager game
	↓
Kursor masuk ke wilayah → highlight + detail
	↓
Player mengklik wilayah → wilayah terpilih
	↓
Panel detail menampilkan biaya, risiko, dan status tujuan
	↓
Player menekan tombol konfirmasi
	↓
Tujuan dan biaya divalidasi ulang
	↓
MapMenu ditutup
	↓
TravelController memulai perjalanan atau depot action
```

Menu harus melakukan validasi ulang ketika tombol konfirmasi ditekan. Validasi
tidak boleh hanya mengandalkan tampilan node karena resource, posisi karavan,
atau efek sementara dapat berubah.

Tujuan tidak dapat dikonfirmasi jika:

- Tujuan sama dengan posisi karavan saat ini.
- Resource karavan tidak cukup untuk biaya perjalanan.
- Tujuan sedang tidak tersedia menurut aturan turn.
- Player belum memilih tujuan.

### Alur Data UI

`MapMenu` membaca data dari sistem berikut:

- `TurnManager`: turn saat ini dan jumlah turn tersisa.
- `RouteManager`: koneksi, jarak, biaya, dan risiko rute.
- `ResourceManager`: resource serta stabilitas setiap area.
- `PlayerCaravan`: posisi, resource, kapasitas, dan efek sementara.
- `Depot`: ketersediaan dan aksi depot.

Alur data yang disarankan:

```text
Game state
	↓
MapMenu.refresh()
	↓
Wilayah dan panel ringkasan diperbarui
	↓
Player memilih wilayah
	↓
MapMenu menampilkan detail dan status validasi
```

Setelah perjalanan atau aksi depot selesai, menu map tidak perlu mempertahankan
data lama. Pada turn berikutnya menu dibuat atau di-refresh dari state terbaru.

### Langkah Implementasi di Godot

1. Buat `map_menu.tscn` dengan root `Control` dan letakkan di `CanvasLayer`.
2. Buat `RegionButton` (root `Control` + `region_button.gd`) dengan poligon
   wilayah, highlight, outline, label nama, dan anchor.
3. Tempatkan lima wilayah sesuai bentuk peta: Village & Castle di barat, Snow
   di timur laut, Forest di timur, Desert di selatan, Depot di tengah.
4. Buat visual garis rute dengan `Line2D` dari banner karavan ke setiap tujuan.
5. Buat `AreaDetailPanel`, `CaravanSummary`, dan `TurnSummary`.
6. Tambahkan state visual wilayah: normal, hover, terpilih, dan tujuan tidak
   tersedia (misalnya coin kurang).
7. Hubungkan `MapMenu` ke `TurnManager`, `RouteManager`, `ResourceManager`,
   `PlayerCaravan`, dan `Depot`.
8. Implementasikan refresh saat menu dibuka dan saat wilayah dipilih.
9. Implementasikan validasi konfirmasi dan kirim tujuan valid ke
   `TravelController`.
10. Uji perubahan posisi karavan, biaya rute, resource tidak cukup, depot,
	area stabil, dan turn terakhir.

Implementasi awal cukup menggunakan node UI, poligon wilayah, panel, dan garis
rute. Animasi zoom, peta interaktif, atau efek dekoratif tambahan dapat
ditambahkan setelah alur pemilihan tujuan terbukti berfungsi.

## 6. Alur Turn

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

1. Memilih salah satu dari empat area.
2. Pergi ke depot.

Biaya perjalanan dibayar saat perjalanan dimulai. Jika resource atau coin tidak
mencukupi, tujuan tersebut tidak dapat dipilih.

## 7. Transisi Antar-Area

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

## 8. Resource Karavan dan Area

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

## 9. Depot

Depot adalah tujuan khusus yang menyediakan:

- Pengisian Iron, Diamond, dan Coin karavan.
- Upgrade kapasitas atau kemampuan karavan.
- Pengambilan income dari area yang telah dikunjungi.
- Pembelian skin kuda.
- Pembelian skin gerobak karavan.

Depot tidak dihitung sebagai area yang harus distabilkan. Aksi depot tetap
menghabiskan satu turn, dan resource area tetap diperbarui pada akhir turn.

## 10. Encounter dan Efek Sementara

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

## 11. Kondisi Menang dan Kalah

Jumlah turn terbatas. Pada akhir turn terakhir:

- **Menang** jika jumlah area dengan status stabil minimal tiga dari empat area.
- **Kalah** jika jumlah area stabil kurang dari tiga.

Pemeriksaan kondisi dilakukan setelah resource area diperbarui agar hasil turn
terakhir ikut dihitung.

```text
stable_area_count >= 3  -> Victory
stable_area_count < 3   -> Defeat
```

## 12. RNG Environment

RNG hanya digunakan untuk variasi dekorasi pada area aktif. RNG tidak boleh
mengubah:

- Layout utama.
- Jaringan rute.
- Posisi wilayah pada peta.
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

Pool lain dibuat untuk Village & Castle dan Desert. Setiap scene area dapat
memiliki `SpawnPoints` agar dekorasi tidak menutup jalur karavan.

## 13. Struktur Folder yang Disarankan

```text
scenes/
├── map/
│   ├── map_menu.tscn
│   ├── forest.tscn
│   ├── snow.tscn
│   ├── village.tscn   # Village & Castle
│   └── desert.tscn
└── depot/
	└── depot.tscn

scripts/
└── map/
	├── map_menu.gd
	└── region_button.gd

data/
├── areas/
├── routes/
├── encounters/
└── caravan/

asset/
├── assetMenuMap/
│   ├── Map.png
│   └── banner_purple.png
├── background/
│   ├── forest/
│   ├── snow/
│   ├── village/
│   └── desert/
├── ground/
├── environment/
└── caravan/
```

Data area dan rute sebaiknya dipisahkan dari scene agar balancing resource,
biaya, jarak, risiko, dan reward tidak memerlukan perubahan layout.

## 14. Checklist Map Designer

- [ ] Menu map muncul pada awal setiap turn.
- [ ] Lima wilayah terlihat: Depot, Snow, Forest, Desert, Village & Castle.
- [ ] Hover kursor menghighlight wilayah dan menampilkan detailnya.
- [ ] Klik wilayah memilih tujuan dan garis rutenya menjadi emas.
- [ ] Detail Iron, Diamond, Coin, jarak, biaya, dan risiko tampil di panel.
- [ ] Posisi karavan (banner), resource karavan, kapasitas, dan turn tersisa terlihat.
- [ ] Wilayah yang tidak bisa dipilih (coin kurang / sudah di sini) punya alasan di panel.
- [ ] Empat scene area tersedia: Forest, Snow, Village & Castle, Desert.
- [ ] Setiap area memiliki layout tetap dan collision yang aman.
- [ ] Setiap area memiliki pool dekorasi RNG sendiri.
- [ ] Semua wilayah bisa dipilih dari mana saja tanpa rute terkunci.
- [ ] Setiap tujuan memiliki jarak, biaya, dan risiko bandit.
- [ ] Transisi area menampilkan perjalanan singkat dari area asal.
- [ ] Scene area tidak menyimpan progres resource secara langsung.
- [ ] Resource area dapat berkurang setiap turn setelah masa perlindungan dua turn.
- [ ] Depot menyediakan refill, upgrade, income, dan skin.
- [ ] Efek sementara memiliki durasi turn yang jelas.
- [ ] Kondisi menang memerlukan minimal tiga area stabil.
- [ ] Kondisi kalah diperiksa setelah turn terakhir selesai.
- [ ] Jalur karavan tidak tertutup dekorasi atau landmark.

## 15. Kesimpulan

Gunakan satu `GameScene` sebagai pengatur turn, state, karavan, depot, dan
perpindahan. Gunakan satu scene mandiri untuk setiap area. Player memilih
wilayah langsung pada peta (hover memberi highlight, klik memilih tujuan),
membayar biaya berdasarkan jarak, lalu melalui transisi sebelum tiba di area
tujuan.

Layout area tetap membuat navigasi mudah dipahami, sedangkan RNG dekorasi
memberikan variasi visual. State resource dan stabilitas disimpan secara
terpisah dari scene sehingga progres area tetap ada ketika player berpindah.
