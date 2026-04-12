"""
laptop_lineup_optimizer/main.py
================================
Titik masuk utama — jalankan pipeline lengkap:
  1. Load / simulasi dataset
  2. Analisis profit 4 opsi upgrade
  3. Generate semua visualisasi
  4. Simpan hasil ke outputs/

Penggunaan:
    python main.py                    # simulasi dataset
    python main.py data/laptops.csv   # dataset CSV nyata
"""

import sys
import os

# Pastikan src/ ada di path
sys.path.insert(0, os.path.dirname(__file__))

from src.analyzer  import load_dataset, PriceRegressor, analyze_upgrades, print_report, save_results
from src.visualizer import generate_all


def main(csv_path: str | None = None, output_dir: str = "outputs"):
    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║       LAPTOP LINEUP OPTIMIZER — AI Profit Analysis Tool         ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    # 1. Dataset
    df = load_dataset(csv_path)

    # 2. Model regresi (fallback jika tidak ada exact match)
    regressor = PriceRegressor().fit(df)

    # 3. Analisis
    results = analyze_upgrades(df, regressor)

    # 4. Report ke terminal
    print_report(results)

    # 5. Simpan CSV
    os.makedirs(output_dir, exist_ok=True)
    save_results(results, f"{output_dir}/results.csv")

    # 6. Visualisasi
    print("\n[main] Membuat visualisasi...")
    chart_paths = generate_all(df, results, output_dir)

    print(f"\n[main] Selesai. Output tersimpan di '{output_dir}/':")
    for p in [f"{output_dir}/results.csv"] + chart_paths:
        print(f"       • {p}")

    return results


if __name__ == "__main__":
    csv_arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(csv_path=csv_arg)
