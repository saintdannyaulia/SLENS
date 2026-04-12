"""
laptop_lineup_optimizer/src/analyzer.py
========================================
AI Analyst untuk optimalisasi lineup produk laptop.
Menghitung gross profit dari 4 opsi upgrade terhadap model dasar,
menggunakan median/mean dari exact-match rows, atau regresi linear
sebagai fallback jika tidak ada data yang cocok.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
import warnings
warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────────
BASE_CONFIG = {
    "memory_gb":    16,
    "storage_gb":   512,
    "cpu_class":    1,
    "screen_inches": 14.0,
    "selling_price": 111_000,   # yen — harga jual baseline
    "cost":         0,          # additional cost baseline
}

UPGRADE_OPTIONS = {
    "RAM 32GB": {
        "memory_gb": 32, "storage_gb": 512, "cpu_class": 1,
        "screen_inches": 14.0, "add_cost": 8_500,
    },
    "Storage 1TB": {
        "memory_gb": 16, "storage_gb": 1024, "cpu_class": 1,
        "screen_inches": 14.0, "add_cost": 6_000,
    },
    "CPU Kelas 2": {
        "memory_gb": 16, "storage_gb": 512, "cpu_class": 2,
        "screen_inches": 14.0, "add_cost": 12_000,
    },
    'Layar 15.6"': {
        "memory_gb": 16, "storage_gb": 512, "cpu_class": 1,
        "screen_inches": 15.6, "add_cost": 5_500,
    },
}

FEATURES = ["memory_gb", "storage_gb", "cpu_class", "screen_inches"]
MIN_EXACT_MATCH = 5          # minimum rows untuk dianggap reliable
SCREEN_TOLERANCE = 0.05      # toleransi inch untuk exact match layar


# ─────────────────────────────────────────────
# DATASET SIMULATOR
# ─────────────────────────────────────────────
def simulate_dataset(n: int = 1_200, random_seed: int = 42) -> pd.DataFrame:
    """
    Generate dataset simulasi laptop jika tidak ada file CSV.
    Distribusi harga mengikuti komponen spesifikasi + noise ±12%.
    """
    np.random.seed(random_seed)

    configs = [
        # (memory, storage, cpu, screen, base_price)
        (8,   256, 1, 13.3,  65_000),
        (16,  512, 1, 14.0, 111_000),
        (32,  512, 1, 14.0, 135_000),
        (16, 1024, 1, 14.0, 125_000),
        (16,  512, 2, 14.0, 148_000),
        (16,  512, 1, 15.6, 118_000),
        (32, 1024, 2, 15.6, 185_000),
        (8,   512, 1, 14.0,  90_000),
        (64, 1024, 2, 15.6, 220_000),
        (16,  256, 1, 14.0,  98_000),
    ]

    rows = []
    for _ in range(n):
        m, s, c, sc, base = configs[np.random.randint(len(configs))]
        noise = np.random.uniform(0.88, 1.12)
        rows.append({
            "memory_gb":       m,
            "storage_gb":      s,
            "cpu_class":       c,
            "screen_inches":   sc,
            "market_price_yen": int(base * noise),
        })

    df = pd.DataFrame(rows)
    print(f"[simulate_dataset] {len(df)} baris dataset dibuat (seed={random_seed}).")
    return df


# ─────────────────────────────────────────────
# LOAD ATAU SIMULASI
# ─────────────────────────────────────────────
def load_dataset(csv_path: str | None = None) -> pd.DataFrame:
    """
    Muat dataset dari CSV, atau buat simulasi jika path None / file tidak ada.

    Kolom CSV yang diharapkan:
        memory_gb, storage_gb, cpu_class, screen_inches, market_price_yen
    """
    if csv_path:
        try:
            df = pd.read_csv(csv_path)
            required = set(FEATURES + ["market_price_yen"])
            missing = required - set(df.columns)
            if missing:
                raise ValueError(f"Kolom hilang di CSV: {missing}")
            print(f"[load_dataset] Loaded {len(df)} baris dari '{csv_path}'.")
            return df
        except FileNotFoundError:
            print(f"[load_dataset] File '{csv_path}' tidak ditemukan → menggunakan simulasi.")

    return simulate_dataset()


# ─────────────────────────────────────────────
# MODEL REGRESI
# ─────────────────────────────────────────────
class PriceRegressor:
    """
    Linear Regression dengan StandardScaler untuk estimasi harga pasar
    ketika tidak ada exact match di dataset.
    """

    def __init__(self):
        self.model  = LinearRegression()
        self.scaler = StandardScaler()
        self._fitted = False

    def fit(self, df: pd.DataFrame) -> "PriceRegressor":
        X = df[FEATURES].values
        y = df["market_price_yen"].values
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self._fitted = True

        # Evaluasi
        y_pred = self.model.predict(X_scaled)
        r2  = r2_score(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        print(f"[PriceRegressor] Fitted — R²={r2:.3f}, MAE=¥{mae:,.0f}")
        return self

    def predict(self, spec: dict) -> int:
        if not self._fitted:
            raise RuntimeError("Model belum difit. Panggil .fit(df) terlebih dahulu.")
        X = np.array([[spec[f] for f in FEATURES]])
        X_scaled = self.scaler.transform(X)
        return int(self.model.predict(X_scaled)[0])


# ─────────────────────────────────────────────
# EXACT MATCH FILTER
# ─────────────────────────────────────────────
def filter_exact_match(df: pd.DataFrame, spec: dict) -> pd.Series:
    """
    Filter baris yang persis cocok dengan spek (screen dengan toleransi ±SCREEN_TOLERANCE).
    """
    mask = (
        (df["memory_gb"]   == spec["memory_gb"])  &
        (df["storage_gb"]  == spec["storage_gb"]) &
        (df["cpu_class"]   == spec["cpu_class"])  &
        (df["screen_inches"].between(
            spec["screen_inches"] - SCREEN_TOLERANCE,
            spec["screen_inches"] + SCREEN_TOLERANCE
        ))
    )
    return df.loc[mask, "market_price_yen"]


# ─────────────────────────────────────────────
# CORE ANALYSIS
# ─────────────────────────────────────────────
def analyze_upgrades(
    df: pd.DataFrame,
    regressor: PriceRegressor,
    base_selling: int = BASE_CONFIG["selling_price"],
) -> pd.DataFrame:
    """
    Hitung gross profit untuk setiap opsi upgrade.

    Returns
    -------
    DataFrame dengan kolom:
        upgrade, market_price_yen, add_cost, total_cost,
        gross_profit, match_count, method, profitable
    """
    records = []

    for name, spec in UPGRADE_OPTIONS.items():
        add_cost = spec["add_cost"]
        spec_clean = {k: v for k, v in spec.items() if k != "add_cost"}

        matches = filter_exact_match(df, spec_clean)
        n_match = len(matches)

        if n_match >= MIN_EXACT_MATCH:
            market_price = int(matches.median())
            method = f"median ({n_match} exact matches)"
        elif n_match > 0:
            market_price = int(matches.mean())
            method = f"mean ({n_match} exact matches)"
        else:
            market_price = regressor.predict(spec_clean)
            method = "regresi linear (0 exact matches)"

        total_cost   = base_selling + add_cost
        gross_profit = market_price - total_cost

        records.append({
            "upgrade":          name,
            "add_cost":         add_cost,
            "market_price_yen": market_price,
            "total_cost":       total_cost,
            "gross_profit":     gross_profit,
            "match_count":      n_match,
            "method":           method,
            "profitable":       gross_profit > 0,
        })

    result = (
        pd.DataFrame(records)
        .sort_values("gross_profit", ascending=False)
        .reset_index(drop=True)
    )
    result.index += 1   # ranking mulai dari 1

    return result


# ─────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────
def print_report(results: pd.DataFrame, base_selling: int = BASE_CONFIG["selling_price"]) -> None:
    SEP = "─" * 72

    print(f"\n{'═'*72}")
    print("  AI ANALYST — LAPTOP LINEUP OPTIMIZATION")
    print(f"  Model dasar: ¥{base_selling:,}  |  RAM 16GB / 512GB / CPU-1 / 14.0\"")
    print(f"{'═'*72}\n")

    print("TABEL PERBANDINGAN PROFIT\n" + SEP)
    display = results[[
        "upgrade", "add_cost", "market_price_yen", "total_cost", "gross_profit", "method"
    ]].copy()
    display.columns = ["Upgrade", "Biaya Upgrade (¥)", "Harga Pasar (¥)",
                       "Total Cost (¥)", "Gross Profit (¥)", "Metode"]
    for col in ["Biaya Upgrade (¥)", "Harga Pasar (¥)", "Total Cost (¥)", "Gross Profit (¥)"]:
        display[col] = display[col].apply(lambda x: f"{x:,}")
    print(display.to_string())

    print(f"\n{SEP}")
    print("TOP 2 REKOMENDASI UPGRADE\n" + SEP)
    for rank in [1, 2]:
        row = results.loc[rank]
        flag = "✓ DIREKOMENDASIKAN" if rank == 1 else "✓ Alternatif terbaik"
        print(f"  #{rank} {row['upgrade']:15s}  Gross Profit = ¥{row['gross_profit']:>8,}  [{flag}]")
        print(f"     Metode: {row['method']}")

    print(f"\n{'═'*72}\n")


# ─────────────────────────────────────────────
# SAVE RESULTS
# ─────────────────────────────────────────────
def save_results(results: pd.DataFrame, path: str = "outputs/results.csv") -> None:
    results.to_csv(path, index_label="rank")
    print(f"[save_results] Hasil disimpan ke '{path}'.")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def run(csv_path: str | None = None, output_dir: str = "outputs") -> pd.DataFrame:
    """
    Pipeline utama. Kembalikan DataFrame hasil analisis.

    Parameters
    ----------
    csv_path   : Path ke file CSV laptop (None = simulasi)
    output_dir : Direktori untuk menyimpan hasil CSV
    """
    df = load_dataset(csv_path)

    regressor = PriceRegressor().fit(df)

    results = analyze_upgrades(df, regressor)

    print_report(results)

    import os
    os.makedirs(output_dir, exist_ok=True)
    save_results(results, f"{output_dir}/results.csv")

    return results


if __name__ == "__main__":
    import sys
    csv_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run(csv_path=csv_arg)
