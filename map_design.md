# Map Design

## 1. Konsep Utama

Map adalah perjalanan lurus dari kiri ke kanan. Karavan melewati beberapa zona berdasarkan jarak perjalanan. Setiap zona memiliki tiga hal yang saling mengikuti:

1. Tema background.
2. Pool environment untuk RNG.
3. Tema ground dan collision.

Contoh pembagian zona:

| Jarak | Zona | Background | Ground | Environment RNG |
|---|---|---|---|---|
| 0 km - 10 km | Forest | Hutan hijau | Tanah dan rumput | Pohon, semak, batu, jamur |
| 10 km - 20 km | Snow | Hutan bersalju | Salju dan es | Pinus, salju, batu es |
| 20 km - 30 km | Mountain | Gunung bersalju | Jalan batu atau salju | Tebing, pinus, jembatan |
| 30 km - 40 km | Village | Desa musim dingin | Jalan desa bersalju | Rumah, pagar, lampu |
| 40 km | Castle | Benteng bersalju | Peron batu atau salju | Tembok, menara, gerbang |

Jarak menentukan zona aktif. RNG hanya memilih variasi yang tersedia di zona tersebut. Dengan begitu background, ground, dan dekorasi selalu terlihat sebagai satu tema yang konsisten.

## 2. Struktur Scene Utama

```text
MainLevel (Node2D)
├── Background (Node2D)
│   ├── ParallaxSky (Parallax2D)
│   ├── ParallaxFar (Parallax2D)
│   ├── ParallaxMid (Parallax2D)
│   └── ParallaxNear (Parallax2D)
├── World (Node2D)
│   ├── Ground (Node2D)
│   │   └── ActiveGroundChunk (Node2D)
│   ├── ActiveEnvironment (Node2D)
│   └── Landmarks (Node2D)
├── Player_Caravan (CharacterBody2D)
└── UI (CanvasLayer)
```

### Pembagian Tanggung Jawab

- `Background`: langit, awan, gunung, dan siluet jauh yang menggunakan parallax.
- `Ground`: jalan yang dipijak karavan, termasuk visual dan collision.
- `ActiveEnvironment`: pohon, batu, semak, salju, dan dekorasi hasil spawn RNG.
- `Landmarks`: depot, bengkel, desa, dan kastil pada jarak yang sudah ditentukan.
- `Player_Caravan`: karavan dan kamera.
- `UI`: HUD, quest, dan menu navigasi.

## 3. Background dan Parallax

Background perlu menggunakan `Parallax2D` agar setiap layer bergerak dengan kecepatan berbeda dan dapat melakukan looping horizontal.

| Layer | Contoh Isi | Kecepatan relatif |
|---|---|---:|
| Sky | Langit dan awan | 0.05 - 0.10 |
| Far | Gunung dan hutan jauh | 0.15 - 0.25 |
| Mid | Bukit dan pepohonan sedang | 0.40 - 0.60 |
| Near | Semak dan objek dekat | 0.80 - 1.00 |
| World | Ground, landmark, karavan | 1.00 |

Saat zona berubah pada 10 km, semua layer background diganti atau diarahkan ke aset tema baru. Contohnya, background hutan hijau diganti menjadi hutan bersalju.

Aturan background:

- Gunakan texture atau chunk yang dapat diulang secara horizontal.
- Jangan memberi collision pada layer parallax.
- Pastikan pergantian aset tidak meninggalkan garis atau celah.
- Gunakan transition chunk agar pergantian tema tidak terasa mendadak.

## 4. Ground dan Collision

Ground **bukan** parallax. Ground harus tetap berada di world space karena karavan membutuhkan collision yang stabil saat bergerak.

Ground dapat dibuat menggunakan salah satu cara berikut:

### Opsi A: Ground Chunk

Buat scene ground dengan ukuran tetap dan spawn berurutan seperti environment chunk:

```text
ForestGroundChunk (Node2D)
├── GroundVisual (TileMapLayer atau Sprite2D)
├── GroundCollision (StaticBody2D)
│   └── CollisionPolygon2D atau CollisionShape2D
└── ChunkEnd (Marker2D)
```

Saat karavan melewati 10 km, sistem berhenti membuat `ForestGroundChunk` dan mulai membuat `SnowGroundChunk`.

### Opsi B: Satu TileMapLayer dengan Pergantian TileSet

Gunakan satu `TileMapLayer`, lalu ubah tile atau TileSet saat zona berganti. Collision pada tile salju harus sudah dibuat di TileSet agar karavan tidak jatuh menembus lantai.

Untuk game jam, ground chunk biasanya lebih mudah dirawat karena setiap tema memiliki scene visual dan collision sendiri.

### Aturan Ground

- Tinggi permukaan ground harus sama pada awal dan akhir setiap chunk.
- Collision harus mengikuti permukaan visual.
- Jangan gunakan parallax untuk ground yang diinjak karavan.
- Ground zona salju menggunakan tile salju atau es, bukan hanya mengganti warna texture.
- Sisakan jalur yang cukup lebar untuk kuda, wagon, dan efek debu.

## 5. Struktur Folder

```text
assets/
├── background/
│   ├── forest/
│   ├── snow/
│   ├── mountain/
│   ├── village/
│   └── castle/
├── ground/
│   ├── forest/
│   ├── snow/
│   ├── mountain/
│   ├── village/
│   └── castle/
└── environment/
    ├── forest/
    ├── snow/
    ├── mountain/
    ├── village/
    └── castle/

scenes/
└── environment/
    ├── chunks/
    │   ├── forest_chunk.tscn
    │   ├── snow_chunk.tscn
    │   ├── mountain_chunk.tscn
    │   └── village_chunk.tscn
    ├── ground/
    │   ├── forest_ground_chunk.tscn
    │   ├── snow_ground_chunk.tscn
    │   └── mountain_ground_chunk.tscn
    └── landmarks/
        ├── depot.tscn
        ├── blacksmith.tscn
        └── castle.tscn
```

## 6. RNG Environment Berdasarkan Zona

RNG tidak memilih aset dari seluruh game. Sistem mengambil pool berdasarkan zona aktif.

```text
active_zone = SNOW

snow_environment_pool =
[
    pine_tree,
    snow_pile,
    ice_rock,
    frozen_bush
]

RNG hanya boleh memilih dari snow_environment_pool.
```

RNG boleh menentukan:

- jumlah pohon dan semak;
- posisi dekorasi di sisi jalur;
- variasi ukuran batu atau salju;
- jarak antar dekorasi;
- kombinasi dekorasi dalam satu chunk.

RNG tidak boleh menentukan posisi landmark utama, jalur ground, atau pintu masuk kastil.

## 7. Pergantian Zona Berdasarkan Jarak

Untuk prototipe, gunakan nilai pixel berikut:

```text
0 px - 10000 px       = Forest
10000 px - 20000 px   = Snow
20000 px - 30000 px   = Mountain
30000 px - 40000 px   = Village
40000 px ke atas      = Castle
```

Jika menggunakan ukuran kilometer:

```text
distance_km = player.global_position.x / PIXELS_PER_KILOMETER
```

Saat jarak melewati batas zona, `ZoneManager` harus memperbarui tiga sistem:

1. Background parallax.
2. Pool RNG environment.
3. Ground chunk atau TileSet beserta collision-nya.

Dengan demikian pada 10 km, hutan hijau berubah menjadi hutan bersalju, dekorasi baru hanya berasal dari pool salju, dan ground berubah menjadi salju atau es.

Pergantian sebaiknya memakai transition chunk. Contohnya, chunk terakhir hutan memiliki sedikit salju, lalu chunk berikutnya menjadi hutan bersalju penuh.

## 8. Sistem Spawn Chunk

```text
[chunk lama] [karavan] [chunk aktif] [chunk berikutnya] [chunk berikutnya]
```

Aturan spawn:

1. Spawn 3-5 chunk di depan karavan saat game dimulai.
2. Saat karavan mendekati chunk terakhir, spawn chunk baru.
3. Tentukan zona berdasarkan jarak spawn chunk, bukan hanya posisi karavan saat ini.
4. Spawn background, ground, dan environment dari zona yang sama.
5. Hapus atau gunakan kembali chunk yang sudah jauh di belakang.
6. Pastikan akhir chunk lama tersambung dengan awal chunk baru.

Untuk game jam, `queue_free()` sudah cukup. Object pooling dapat ditambahkan kemudian jika diperlukan.

## 9. Aturan untuk Designer Map

Setiap chunk harus memiliki ukuran lebar yang konsisten, misalnya `1024 px`.

```text
SnowChunk (Node2D)
├── BackgroundDecoration (Node2D)
├── GroundVisual (TileMapLayer)
├── GroundCollision (StaticBody2D)
├── EnvironmentProps (Node2D)
└── ChunkEnd (Marker2D)
```

Checklist:

- [ ] Semua chunk memiliki ukuran yang sama.
- [ ] Garis tanah antar-chunk tersambung.
- [ ] Collision sesuai dengan visual ground.
- [ ] Background setiap zona dapat looping horizontal.
- [ ] Ground setiap zona memiliki visual dan collision sendiri.
- [ ] Pool RNG tidak memakai aset dari zona lain.
- [ ] Landmark utama memiliki jarak tetap.
- [ ] Jalur karavan selalu aman dan tidak tertutup dekorasi.
- [ ] Layer parallax tidak memiliki collision.
- [ ] Pergantian zona memiliki transition chunk.

## 10. Kesimpulan

Gunakan `Parallax2D` hanya untuk background yang bergerak di belakang dunia. Gunakan ground chunk atau TileMapLayer biasa untuk permukaan yang diinjak karavan. Ketika jarak mencapai batas zona, ganti background, ground, collision, dan pool RNG secara bersamaan.

Dengan sistem ini, perjalanan 0 km-10 km dapat bertema hutan, lalu tepat setelah 10 km berubah ke tema salju secara konsisten tanpa membuat karavan kehilangan pijakan atau melihat dekorasi yang tidak sesuai.
