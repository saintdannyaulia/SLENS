# 🖥️ StarLive Lineup Evaluation & Network Simulation

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![NumPy](https://img.shields.io/badge/NumPy-4DABCF?logo=numpy&logoColor=white)](https://numpy.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org)
[![Matplotlib](https://custom-icon-badges.demolab.com/badge/Matplotlib-71D291?logo=matplotlib&logoColor=white)](https://matplotlib.org)

---

## Directory

- [Overview](#overview)
- [Features & Tech Stack](#features--tech-stack)
- [System Workflow](#system-workflow)
- [User Guide](#user-guide)
  - [Equipment](#equipment)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Troubleshooting](#troubleshooting)
- [Development Notes](#development-notes)
  - [Limitations](#limitations)
  - [Future Development](#future-development)
- [Author](#author)

---

## Overview

Proyek ini dikembangkan sebagai solusi untuk tes seleksi **METI Government of Japan AI and Tech Internship 2025**. Tool ini dirancang untuk membantu manajer produk dan tim merchandising laptop dalam menjawab pertanyaan bisnis secara kuantitatif:

> *"Apakah penambahan RAM, peningkatan CPU, atau perluasan storage pada model entry menguntungkan — dan mana yang paling optimal?"*

Sistem bekerja dengan menelusuri dataset harga pasar laptop, memperkirakan harga jual setelah setiap opsi upgrade, lalu meranking dan merekomendasikan **2 upgrade paling menguntungkan** berdasarkan gross profit per unit.

> *Proyek ini merupakan pertanyaan pada tes seleksi METI Government of Japan — AI and Tech Internship 2025*

---

## Features & Tech Stack

### Features

- **Dual mode** — jalankan dengan dataset CSV nyata atau simulasi 1.200 baris otomatis
- **Estimasi harga hierarkis** — Median → Mean → Regresi Linear sebagai fallback
- **Gross profit per unit** — dihitung otomatis untuk setiap opsi upgrade
- **Output lengkap** — `results.csv`, scatter plot, bar chart profit, dan heatmap korelasi
- **Dapat digunakan sebagai library** — semua modul dapat diimpor langsung di Python

### Tech Stack

| Komponen | Teknologi |
|---|---|
| Bahasa | Python 3.10+ |
| Manipulasi Data | Pandas 2.0, NumPy 1.24 |
| Machine Learning | scikit-learn 1.3 (LinearRegression + StandardScaler) |
| Visualisasi | Matplotlib 3.7 |
| Runtime | Local / CLI |

---

## System Workflow

### Flowchart

```
┌──────────────────────┐     ┌─────────────────────────┐     ┌──────────────────────┐
│  Dataset CSV         │     │  Exact Match Filter     │     │  ≥ 5 baris cocok     │
│  (atau simulasi      │────▶│  toleransi layar        │────▶│  → Median price      │
│   1.200 baris)       │     │  ±0.05"                 │     │                      │
└──────────────────────┘     └─────────────────────────┘     └──────────┬───────────┘
                                                                         │
                                                                         ▼
┌──────────────────────┐     ┌─────────────────────────┐     ┌──────────────────────┐
│  Ranking &           │     │  Gross Profit =         │     │  1–4 baris cocok     │
│  Rekomendasi Top 2   │◀────│  market − (base +       │◀────│  → Mean price        │
│                      │     │  add_cost)              │     │  0 baris → Regresi   │
└──────────────────────┘     └─────────────────────────┘     └──────────────────────┘
```

### Explanation

| Langkah | Proses | Keterangan |
|---|---|---|
| 1 | Muat dataset | CSV dari path argumen, atau data simulasi jika tidak ada input |
| 2 | Exact Match Filter | Cocokkan 4 kolom spek dengan toleransi layar ±0.05" |
| 3 | Estimasi harga | Hierarki: Median (≥5 baris) → Mean (1–4) → Regresi Linear (0) |
| 4 | Hitung gross profit | `market_price − (base_selling_price + upgrade_add_cost)` |
| 5 | Ranking & output | Urutkan profit, cetak laporan, simpan CSV dan visualisasi |

---

## User Guide

### Equipment

Pastikan hal berikut tersedia sebelum memulai:

- Python **3.10** atau lebih baru
- `pip`
- Dataset CSV laptop *(opsional — tersedia mode simulasi bawaan)*

### Installation

#### 1. Clone Repositori

```bash
git clone https://github.com/username/laptop-lineup-optimizer.git
cd laptop-lineup-optimizer
```

#### 2. Buat Virtual Environment *(opsional tapi direkomendasikan)*

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows
```

#### 3. Instal Dependensi

```bash
pip install -r requirements.txt
```

| Paket | Versi Minimum | Kegunaan |
|---|---|---|
| `pandas` | 2.0 | Manipulasi DataFrame |
| `numpy` | 1.24 | Komputasi numerik |
| `scikit-learn` | 1.3 | Linear Regression + StandardScaler |
| `matplotlib` | 3.7 | Visualisasi |

#### 4. Jalankan Tool

**Mode Simulasi** *(tanpa dataset nyata)*
```bash
python main.py
```
Tool akan membuat otomatis **1.200 baris data simulasi** dengan 10 konfigurasi dan noise harga ±12%.

**Mode Dataset CSV**
```bash
python main.py data/laptops.csv
```

**Sebagai Library Python**
```python
from src.analyzer import load_dataset, PriceRegressor, analyze_upgrades, print_report
from src.visualizer import generate_all

df        = load_dataset("data/laptops.csv")   # atau load_dataset() untuk simulasi
regressor = PriceRegressor().fit(df)
results   = analyze_upgrades(df, regressor)

print_report(results)
generate_all(df, results, out_dir="outputs")
```

---

### Configuration

Seluruh konfigurasi terdapat di `src/analyzer.py`.

**Model dasar (`BASE_CONFIG`)**

```python
BASE_CONFIG = {
    "memory_gb":     16,
    "storage_gb":    512,
    "cpu_class":     1,
    "screen_inches": 14.0,
    "selling_price": 111_000,   # harga jual baseline (yen)
    "cost":          0,
}
```

**Opsi upgrade (`UPGRADE_OPTIONS`)**

```python
UPGRADE_OPTIONS = {
    "RAM 32GB":    {"memory_gb": 32,  "storage_gb": 512,  "cpu_class": 1, "screen_inches": 14.0, "add_cost": 8_500},
    "Storage 1TB": {"memory_gb": 16,  "storage_gb": 1024, "cpu_class": 1, "screen_inches": 14.0, "add_cost": 6_000},
    "CPU Kelas 2": {"memory_gb": 16,  "storage_gb": 512,  "cpu_class": 2, "screen_inches": 14.0, "add_cost": 12_000},
    'Layar 15.6"': {"memory_gb": 16,  "storage_gb": 512,  "cpu_class": 1, "screen_inches": 15.6, "add_cost": 5_500},
}
```

Untuk menambahkan opsi baru, tambahkan entri baru pada `UPGRADE_OPTIONS`:

```python
"RAM 64GB + GPU": {
    "memory_gb": 64, "storage_gb": 512, "cpu_class": 3,
    "screen_inches": 14.0, "add_cost": 28_000
}
```

**Format Dataset CSV**

File CSV harus memiliki tepat 5 kolom berikut *(nama kolom bersifat case-sensitive)*:

| Kolom | Tipe | Deskripsi | Contoh |
|---|---|---|---|
| `memory_gb` | `int` | Kapasitas RAM dalam GB | `16` |
| `storage_gb` | `int` | Kapasitas SSD/HDD dalam GB | `512` |
| `cpu_class` | `int` | Kelas CPU (1=entry, 2=mid, 3=high) | `1` |
| `screen_inches` | `float` | Ukuran layar dalam inci | `14.0` |
| `market_price_yen` | `int` | Harga pasar dalam yen | `111000` |

---

### Troubleshooting

| Masalah | Kemungkinan Penyebab | Solusi |
|---|---|---|
| `ModuleNotFoundError` | Dependensi belum terinstal | Jalankan `pip install -r requirements.txt` |
| Kolom tidak terbaca | Nama kolom CSV tidak sesuai | Pastikan 5 nama kolom persis seperti di tabel Format Dataset |
| Semua hasil pakai regresi | Dataset terlalu sedikit baris per konfigurasi | Tambah data atau gunakan mode simulasi untuk referensi |
| Output folder kosong | `outputs/` belum dibuat | Folder dibuat otomatis — pastikan izin tulis tersedia |

---

## Development Notes

### Contoh Output (Simulasi 1.200 Baris)

Berikut hasil pada dataset simulasi bawaan:

| Rank | Opsi Upgrade | Biaya Upgrade | Est. Harga Pasar | Gross Profit | Metode |
|:---:|---|---:|---:|---:|---|
| **#1** | **CPU Kelas 2** | ¥12.000 | ¥147.270 | **¥24.270** | Median (132 rows) |
| **#2** | **RAM 32GB** | ¥8.500 | ¥137.656 | **¥18.156** | Median (106 rows) |
| 3 | Storage 1TB | ¥6.000 | ¥125.145 | ¥8.145 | Median (113 rows) |
| 4 | Layar 15.6" | ¥5.500 | ¥118.533 | ¥2.033 | Median (115 rows) |

Upgrade **CPU Kelas 2** menghasilkan gross profit tertinggi karena pasar memberikan premium signifikan terhadap peningkatan performa. Upgrade **RAM 32GB** menjadi pilihan terbaik kedua dengan rasio profit/biaya ~2.1x (¥18.156 dari investasi ¥8.500).

### Metodologi Analitik

Estimasi harga pasar menggunakan tiga strategi secara hierarkis:

| Strategi | Kondisi | Metode |
|---|---|---|
| 1 | ≥ 5 baris exact match | Median — robust terhadap outlier |
| 2 | 1–4 baris exact match | Mean — ukuran sampel kecil |
| 3 | 0 baris cocok | Linear Regression + StandardScaler atas 4 fitur |

Model regresi menggunakan `sklearn.linear_model.LinearRegression` dengan evaluasi simulasi: **R² ≈ 0.925**, **MAE ≈ ¥10.084**. Gross profit yang dihitung merupakan **margin kotor per unit** — belum memperhitungkan overhead, distribusi, maupun pemasaran.

> Jika dataset nyata memiliki distribusi non-linear, pertimbangkan `GradientBoostingRegressor` sebagai pengganti langsung.

### Limitations

| Komponen | Batasan |
|---|---|
| Gross profit | Margin kotor saja — belum termasuk overhead & distribusi |
| Model regresi | Linear — kurang akurat untuk dataset dengan distribusi non-linear |
| Dataset simulasi | Noise ±12% — hasil bisa berbeda signifikan dengan data pasar nyata |
| CPU class | Skala 1–3 bersifat ordinal, bukan representasi performa aktual |

### Future Development

Beberapa pengembangan yang dapat dilakukan ke depan:

- [ ] **Non-linear model** — integrasi `GradientBoostingRegressor` atau `RandomForest` untuk dataset pasar nyata
- [ ] **Multi-market support** — dukungan mata uang selain yen (USD, IDR, EUR)
- [ ] **Web dashboard** — antarmuka Streamlit untuk analisis tanpa CLI
- [ ] **Sensitivity analysis** — simulasi pengaruh perubahan `add_cost` terhadap gross profit
- [ ] **Auto dataset scraping** — pengambilan data harga laptop dari sumber publik secara otomatis

---

<p align="center">
  <b>Pengembangan dari tim StarLive SAINT</b>
</p>

<p align="center"><i>Danny Aulia · Said Hasan Hanafiah · Noah Von Nobelius · Arvian Raveindra Pradana</i></p>
