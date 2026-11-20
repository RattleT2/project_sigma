# Alur Plot Game

Game 2D pixel platformer berbasis turn (Godot). Pemain mengendalikan caravan kuda sebagai pengantar resource untuk menstabilkan 4 wilayah.

---

## 1. Konsep Utama

- Pemain bertugas sebagai **pengantar barang resource** untuk **menstabilkan 4 wilayah**.
- Permainan berjalan **berdasarkan turn**. Di setiap turn, resource di 4 wilayah **berkurang**.
- Di awal permainan, pemain diberi **5 turn** untuk menstabilkan **1 dari 4 wilayah**.
- Pemain membawa perlengkapan sesuai **level kuda caravan**, sehingga harus **resupply** kembali ke depot persediaan sebelum mengantar ke wilayah tujuan.
- Ketika turn habis dan wilayah dalam kondisi stabil, pemain **menang** dan mendapat **score**.
- Game bersifat **endless**: setelah menang, tingkat kesulitan naik di putaran berikutnya.

---

## 2. Sistem Putaran dan Turn

| Aspek | Aturan |
|---|---|
| Jumlah putaran | 10 putaran (dapat disesuaikan) |
| Turn awal | 5 turn pada putaran pertama |
| Penambahan turn | +1 turn setiap selesai satu putaran |
| Wilayah yang distabilkan | Awalnya 1 wilayah, bertambah hingga 2 wilayah dan seterusnya sesuai kesulitan |
| Kenaikan permintaan | Permintaan resource wilayah naik tiap putaran, misalnya dari `0/12` menjadi `0/18` |
| Wilayah yang sudah di-resupply | Resource-nya berkurang sedikit saja per turn |

### Setelah 5 Turn Selesai dan Wilayah Stabil

Pemain diberi dua opsi:

1. **Selesai (Withdraw)**: uang dari perjalanan diakumulasi menjadi uang menu, lalu game kembali ke *new game*.
2. **Lanjut**: turn bertambah (kelipatan 1), tingkat kesulitan naik (jumlah wilayah yang harus distabilkan bertambah dan permintaan resource meningkat).

### Mode Endless

- Total ada 10 putaran.
- Pada putaran terakhir (paling tidak putaran ke-10), saat pemain sudah **full gear**, permintaan dari desa **tidak bertambah lagi dan menetap**, sehingga pemain bisa merasakan mode endless.

---

## 3. Wilayah dan Permintaan Resource

Terdapat **4 wilayah** dan **3 jenis resource**. Setiap wilayah memiliki kecenderungan permintaan berbeda.

| Wilayah | Permintaan Resource |
|---|---|
| Salju | Lebih condong ke **Diamond** |
| Forest (Hutan) | Lebih condong ke **Koin Emas Kecil** |
| Dessert (Gurun) | Lebih condong ke **Iron** |
| Village (Desa) | **Merata** (rata ketiga resource) |

### Resource

1. **Diamond**
2. **Koin Emas Kecil**
3. **Iron**

Harga satuan di Depot Utama berbeda-beda:

- Diamond: **30** coin per satuan
- Koin Emas Kecil: **10** coin per satuan
- Iron: *(harga perlu ditentukan, lihat bagian "Poin yang Perlu Dipastikan")*

Ketika resource diantar ke wilayah yang membutuhkannya, pemain mendapat **20% per satuan**.

---

## 4. Alur Perjalanan dalam Satu Turn

1. Pemain berada di **Depot Utama / depot persediaan**.
2. Pemain melakukan **resupply** resource menggunakan **slider** untuk ketiga resource, menyesuaikan **kapasitas maksimum caravan**.
3. Pemain bisa membeli **buff** di Depot Utama untuk persediaan perjalanan.
4. Pemain berangkat mengantar resource ke **wilayah tujuan misi**.
5. Selama perjalanan, bisa muncul **bandit** (lihat bagian 7).
6. Resource diantar dan wilayah mendapat resource, pemain menerima reward.
7. Turn berakhir: resource di 4 wilayah berkurang. Wilayah yang sudah di-resupply berkurang sedikit saja.

### Depot Utama

- Harga resupply **lebih murah** di Depot Utama.
- Reward yang didapat dari wilayah yang diantar **lebih banyak**.

---

## 5. Sistem Ekonomi (Dua Jenis Koin)

Koin dipisah menjadi dua sistem yang tidak boleh tercampur.

### Koin In-Game
- Pemain dimodali **500 gold coin** setiap memulai game.
- Dipakai untuk resupply dan membeli buff selama perjalanan.

### Koin Menu
- Didapat dari **akumulasi koin in-game** ketika pemain menyelesaikan putaran dan memilih **withdraw**.
- Dipakai untuk membeli **aksesoris dan upgrade** di main menu (di luar in-game).
- **Tidak dapat dibawa ke in-game.**

### Contoh Alur
Pemain mengakhiri game di putaran kedua, lalu koin diakumulasi menjadi koin menu, dan game kembali menjadi *new game* dengan modal **500 coin**. Koin hasil akumulasi tidak ikut terbawa.

---

## 6. Upgrade dan Perlengkapan

- **Kapasitas caravan tidak bisa ditambah** selama in-game, kecuali dengan **upgrade aksesoris di main menu**.
- Efek aksesoris:
  - Meningkatkan **kapasitas bawaan**.
  - Mengurangi **waktu perjalanan**.
- **Buff** dibeli di Depot Utama dan **hilang setelah 2 turn**.
- Terdapat fitur **save game di tengah perjalanan**.

---

## 7. Bandit

- Bandit dapat muncul dan **merampas resource secara acak** dengan nominal yang **sangat sedikit**.
- Pemain bisa mengatasinya dengan **membayar bandit** agar resource tidak dicuri.

---

## 8. Kondisi Menang dan Score

- Pemain **menang** ketika turn habis dan wilayah dalam kondisi **stabil**.
- Pemain mendapat **score** saat menang.
- Setelah menang, pemain memilih **selesai** atau **lanjut** ke putaran berikutnya yang lebih sulit.

---

## 9. Ringkasan Alur Besar

```
Main Menu (upgrade aksesoris pakai koin menu)
        |
        v
New Game (modal 500 coin in-game)
        |
        v
Putaran 1: 5 turn, stabilkan 1 wilayah
        |
        v
Depot Utama -> Resupply (slider) + Beli buff
        |
        v
Antar resource ke wilayah (waspada bandit)
        |
        v
Turn habis & wilayah stabil? -- Ya --> Menang + Score
        |
        v
Pilih: Selesai (withdraw ke koin menu) atau Lanjut
        |
        v
Lanjut: +1 turn, wilayah bertambah, permintaan naik
        |
        v
Putaran ke-10: full gear -> permintaan desa menetap (Mode Endless)
```

---

## 10. Poin yang Perlu Dipastikan

- Harga satuan **Iron** di Depot Utama belum disebutkan.
- Makna "mendapat **20% per satuan**": apakah 20% keuntungan dari harga satuan, atau bonus lain.
- Jumlah maksimal wilayah yang distabilkan bersamaan (disebut naik dari 1 menjadi 2, dan total wilayah ada 4).
- Besaran pasti kenaikan turn dan permintaan per putaran (contoh `0/12` menjadi `0/18` baru sebagai ilustrasi).
