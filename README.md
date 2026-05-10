# 🖥️ StarLive Lineup Evaluation & Network Simulation

> **AI Analyst untuk optimalisasi lineup produk laptop** — menghitung gross profit dari opsi upgrade spesifikasi menggunakan analisis pasar berbasis data nyata atau simulasi.
> *Merupakan pertanyaan pada tes METI Government of Japan for AI and Tech Internship tahun 2025*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange?logo=scikit-learn)](https://scikit-learn.org)

---

## Daftar Isi

- [Latar Belakang](#latar-belakang)
- [Cara Kerja](#cara-kerja)
- [Struktur Proyek](#struktur-proyek)
- [Instalasi](#instalasi)
- [Penggunaan](#penggunaan)
- [Format Dataset CSV](#format-dataset-csv)
- [Konfigurasi Model Dasar & Upgrade](#konfigurasi-model-dasar--upgrade)
- [Output yang Dihasilkan](#output-yang-dihasilkan)
- [Metodologi Analitik](#metodologi-analitik)
- [Hasil Rekomendasi (Simulasi)](#hasil-rekomendasi-simulasi)
- [Kontribusi](#kontribusi)
- [Lisensi](#lisensi)

---

## Latar Belakang

Manajer produk dan tim merchandising laptop sering dihadapkan pada pertanyaan:

> *"Apakah worth it menambah RAM, meningkatkan CPU, atau memperluas storage pada model entry kami — dan mana yang paling menguntungkan?"*

Tool ini menjawab pertanyaan tersebut secara kuantitatif dengan:

1. Menelusuri dataset harga pasar laptop serupa.
2. Memperkirakan **harga jual pasar** setelah setiap upgrade.
3. Menghitung **gross profit** = estimasi harga pasar − (harga jual baseline + biaya upgrade).
4. Meranking opsi dan merekomendasikan **top 2 upgrade paling menguntungkan**.

---

## Cara Kerja

```
Dataset CSV (atau simulasi)
         │
         ▼
┌─────────────────────────┐
│  Exact Match Filter     │  ← cocokkan semua 4 kolom spek
│  (toleransi layar ±0.05")│
└────────────┬────────────┘
             │
     ┌───────┴────────┐
     │ Match ≥ 5 baris│──► Median market price
     │ Match 1–4 baris│──► Mean market price
     │ Match = 0 baris│──► Regresi Linear (fallback)
     └───────┬────────┘
             │
             ▼
  Gross Profit = market_price − (base_selling + add_cost)
             │
             ▼
     Ranking & Rekomendasi Top 2
```

Pipeline dikontrol dari `main.py` dan dieksekusi dalam dua modul:

| Modul | Tanggung Jawab |
|---|---|
| `src/analyzer.py` | Load data, exact match, regresi, hitung profit, cetak laporan |
| `src/visualizer.py` | Scatter plot, bar chart gross profit, heatmap korelasi |

---

## Struktur Proyek

```
laptop-lineup-optimizer/
│
├── main.py                  # Titik masuk utama
├── requirements.txt         # Dependensi Python
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── analyzer.py          # Pipeline analisis & regresi
│   └── visualizer.py        # Visualisasi matplotlib
│
├── data/
│   └── laptops.csv          # Dataset Anda (opsional — ada simulasi bawaan)
│
├── outputs/                 # Hasil analisis (auto-dibuat)
│   ├── results.csv
│   ├── scatter_price_vs_spec.png
│   ├── profit_bar.png
│   └── correlation_heatmap.png
│
└── notebooks/               # Eksplorasi interaktif (opsional)
    └── exploration.ipynb
```

---

## Instalasi

### Prasyarat

- Python **3.10** atau lebih baru
- `pip`

### Langkah

```bash
# 1. Clone repositori
git clone https://github.com/username/laptop-lineup-optimizer.git
cd laptop-lineup-optimizer

# 2. (Opsional) Buat virtual environment
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows

# 3. Instal dependensi
pip install -r requirements.txt
```

### Dependensi

| Paket | Versi Minimum | Kegunaan |
|---|---|---|
| `pandas` | 2.0 | Manipulasi DataFrame |
| `numpy` | 1.24 | Komputasi numerik |
| `scikit-learn` | 1.3 | Linear Regression + StandardScaler |
| `matplotlib` | 3.7 | Visualisasi |

---

## Penggunaan

### Mode 1 — Simulasi (tanpa dataset nyata)

```bash
python main.py
```

Tool akan otomatis men-generate **1.200 baris data laptop simulasi** dengan 10 konfigurasi berbeda dan noise harga ±12%.

### Mode 2 — Dataset CSV nyata

```bash
python main.py data/laptops.csv
```

Ganti `data/laptops.csv` dengan path ke dataset Anda. Lihat [Format Dataset CSV](#format-dataset-csv) untuk spesifikasi kolom.

### Menggunakan sebagai library Python

```python
from src.analyzer import load_dataset, PriceRegressor, analyze_upgrades, print_report
from src.visualizer import generate_all

# Load data
df = load_dataset("data/laptops.csv")   # atau load_dataset() untuk simulasi

# Analisis
regressor = PriceRegressor().fit(df)
results   = analyze_upgrades(df, regressor)

# Output
print_report(results)
generate_all(df, results, out_dir="outputs")
```

---

## Format Dataset CSV

File CSV harus memiliki **tepat 5 kolom** berikut (nama kolom case-sensitive):

| Kolom | Tipe | Deskripsi | Contoh |
|---|---|---|---|
| `memory_gb` | `int` | Kapasitas RAM dalam GB | `16` |
| `storage_gb` | `int` | Kapasitas SSD/HDD dalam GB | `512` |
| `cpu_class` | `int` | Kelas CPU (1 = entry, 2 = mid, 3 = high) | `1` |
| `screen_inches` | `float` | Ukuran layar dalam inci | `14.0` |
| `market_price_yen` | `int` | Harga pasar dalam yen Jepang | `111000` |

**Contoh baris CSV:**

```csv
memory_gb,storage_gb,cpu_class,screen_inches,market_price_yen
8,256,1,13.3,68500
16,512,1,14.0,112300
32,512,1,14.0,138000
16,1024,1,14.0,127500
16,512,2,14.0,151000
```

> **Catatan:** Kolom `market_price_yen` adalah harga jual di pasaran (bukan harga produksi). Semakin banyak baris per konfigurasi, semakin akurat estimasi median-nya.

---

## Konfigurasi Model Dasar & Upgrade

Semua konfigurasi ada di `src/analyzer.py`. Edit sesuai kebutuhan bisnis Anda.

### Model dasar (`BASE_CONFIG`)

```python
BASE_CONFIG = {
    "memory_gb":     16,
    "storage_gb":    512,
    "cpu_class":     1,
    "screen_inches": 14.0,
    "selling_price": 111_000,  # harga jual baseline (yen)
    "cost":          0,
}
```

### Opsi upgrade (`UPGRADE_OPTIONS`)

```python
UPGRADE_OPTIONS = {
    "RAM 32GB":    {"memory_gb": 32,  "storage_gb": 512,  "cpu_class": 1, "screen_inches": 14.0, "add_cost": 8_500},
    "Storage 1TB": {"memory_gb": 16,  "storage_gb": 1024, "cpu_class": 1, "screen_inches": 14.0, "add_cost": 6_000},
    "CPU Kelas 2": {"memory_gb": 16,  "storage_gb": 512,  "cpu_class": 2, "screen_inches": 14.0, "add_cost": 12_000},
    'Layar 15.6"': {"memory_gb": 16,  "storage_gb": 512,  "cpu_class": 1, "screen_inches": 15.6, "add_cost": 5_500},
}
```

Untuk menambah opsi baru, cukup tambah entri di `UPGRADE_OPTIONS`:

```python
"RAM 64GB + GPU": {
    "memory_gb": 64, "storage_gb": 512, "cpu_class": 3,
    "screen_inches": 14.0, "add_cost": 28_000
}
```

---

## Output yang Dihasilkan

Setelah menjalankan `main.py`, folder `outputs/` akan berisi:

### `results.csv` — Tabel perbandingan lengkap

```
rank,upgrade,add_cost,market_price_yen,total_cost,gross_profit,match_count,method,profitable
1,CPU Kelas 2,12000,147270,123000,24270,132,median (132 exact matches),True
2,RAM 32GB,8500,137656,119500,18156,106,median (106 exact matches),True
3,Storage 1TB,6000,125145,117000,8145,113,median (113 exact matches),True
4,Layar 15.6",5500,118533,116500,2033,115,median (115 exact matches),True
```

### `scatter_price_vs_spec.png`

Scatter plot harga pasar vs indeks spesifikasi komposit. Titik kecil = data pasar mentah; segitiga besar = estimasi harga setelah upgrade.

### `profit_bar.png`

Bar chart horizontal membandingkan gross profit (¥) untuk keempat opsi, dengan label nilai di setiap bar.

### `correlation_heatmap.png`

Heatmap korelasi antara keempat fitur spesifikasi dan harga pasar, membantu memahami driver harga utama.

---

## Metodologi Analitik

### Estimasi Harga Pasar

Tool menggunakan **tiga strategi secara hierarkis**:

```
Strategi 1: Exact Match + Median
  → Jika ≥ 5 baris di dataset cocok persis dengan spek upgrade
  → Gunakan median (robust terhadap outlier)

Strategi 2: Exact Match + Mean
  → Jika 1–4 baris cocok
  → Gunakan mean (ukuran sampel terlalu kecil untuk median)

Strategi 3: Regresi Linear (Fallback)
  → Jika 0 baris cocok
  → Linear Regression dengan StandardScaler atas 4 fitur
  → Dilatih atas seluruh dataset
```

### Definisi Gross Profit

```
gross_profit = market_price_estimated − (base_selling_price + upgrade_add_cost)
```

Ini adalah **margin kotor per unit** — belum memperhitungkan biaya overhead, distribusi, atau marketing.

### Model Regresi

- **Algoritma:** `sklearn.linear_model.LinearRegression`
- **Preprocessing:** `StandardScaler` (z-score normalization per fitur)
- **Fitur:** `memory_gb`, `storage_gb`, `cpu_class`, `screen_inches`
- **Target:** `market_price_yen`
- **Evaluasi (simulasi):** R² ≈ 0.925, MAE ≈ ¥10.084

> Regresi linear dipilih karena interpretable, deterministik, dan cukup akurat untuk spek numerik laptop. Jika dataset nyata Anda memiliki distribusi non-linear, pertimbangkan `GradientBoostingRegressor` sebagai drop-in replacement.

---

## Hasil Rekomendasi (Simulasi)

Berikut hasil pada dataset simulasi 1.200 baris:

| Rank | Opsi Upgrade | Biaya Upgrade | Est. Harga Pasar | Gross Profit | Metode |
|:---:|---|---:|---:|---:|---|
| **#1** | **CPU Kelas 2** | ¥12.000 | ¥147.270 | **¥24.270** | Median (132 rows) |
| **#2** | **RAM 32GB** | ¥8.500 | ¥137.656 | **¥18.156** | Median (106 rows) |
| 3 | Storage 1TB | ¥6.000 | ¥125.145 | ¥8.145 | Median (113 rows) |
| 4 | Layar 15.6" | ¥5.500 | ¥118.533 | ¥2.033 | Median (115 rows) |

**Kesimpulan:**
- Upgrade **CPU Kelas 2** menghasilkan gross profit tertinggi (¥24.270/unit) meskipun biaya upgradenya paling mahal, karena pasar memberi premium besar pada peningkatan performa CPU.
- Upgrade **RAM 32GB** adalah pilihan kedua terbaik dengan rasio profit/biaya yang efisien: ¥18.156 profit dari ¥8.500 investasi (~2.1x).

---

## Kontribusi

Pull request dan issue sangat disambut! Untuk perubahan besar, harap buka issue terlebih dahulu untuk mendiskusikan apa yang ingin Anda ubah.

```bash
# Fork → clone → buat branch
git checkout -b feature/nama-fitur

# Commit dengan pesan deskriptif
git commit -m "feat: tambah dukungan gradient boosting regressor"

# Push & buat PR
git push origin feature/nama-fitur
```


---

<p align="center">Dibuat dengan Python · pandas · scikit-learn · matplotlib</p>
