"""
laptop_lineup_optimizer/src/visualizer.py
==========================================
Membuat visualisasi hasil analisis:
  1. Scatter plot  — market price vs spesifikasi per opsi upgrade
  2. Bar chart     — perbandingan gross profit
  3. Heatmap       — korelasi spesifikasi vs harga pasar
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter

PALETTE = ["#1D9E75", "#378ADD", "#BA7517", "#D4537E"]
PALETTE_LIGHT = ["#9FE1CB", "#B5D4F4", "#FAC775", "#F4C0D1"]

FEATURES = ["memory_gb", "storage_gb", "cpu_class", "screen_inches"]

plt.rcParams.update({
    "font.family":  "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "grid.alpha":        0.3,
    "grid.linestyle":    "--",
})


def _yen(x, pos=None):
    return f"¥{int(x):,}"


# ─────────────────────────────────────────────
# 1. SCATTER — price vs spec
# ─────────────────────────────────────────────
def plot_scatter(df: pd.DataFrame, results: pd.DataFrame, out_dir: str = "outputs") -> str:
    """
    Scatter: market_price_yen vs composite spec score.
    Titik dataset di background (transparan), estimated price di foreground.
    """
    from src.analyzer import UPGRADE_OPTIONS, SCREEN_TOLERANCE

    fig, ax = plt.subplots(figsize=(10, 5))

    for i, (_, row) in enumerate(results.iterrows()):
        spec = {k: v for k, v in UPGRADE_OPTIONS[row["upgrade"]].items() if k != "add_cost"}
        mask = (
            (df["memory_gb"]  == spec["memory_gb"]) &
            (df["storage_gb"] == spec["storage_gb"]) &
            (df["cpu_class"]  == spec["cpu_class"]) &
            (df["screen_inches"].between(
                spec["screen_inches"] - SCREEN_TOLERANCE,
                spec["screen_inches"] + SCREEN_TOLERANCE,
            ))
        )
        subset = df[mask]
        x_vals = subset["memory_gb"] + subset["storage_gb"] / 100

        ax.scatter(
            x_vals, subset["market_price_yen"],
            color=PALETTE_LIGHT[i], alpha=0.5, s=20, zorder=2,
        )
        est_x = spec["memory_gb"] + spec["storage_gb"] / 100
        ax.scatter(
            est_x, row["market_price_yen"],
            color=PALETTE[i], marker="^", s=140, zorder=5,
            label=f"{row['upgrade']} (est. ¥{row['market_price_yen']:,})",
        )

    ax.yaxis.set_major_formatter(FuncFormatter(_yen))
    ax.set_xlabel("Composite Spec Index  (memory + storage/100)", fontsize=10)
    ax.set_ylabel("Harga Pasar (¥)", fontsize=10)
    ax.set_title("Scatter: Harga Pasar vs Spesifikasi per Opsi Upgrade", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, loc="upper left")

    fig.tight_layout()
    path = os.path.join(out_dir, "scatter_price_vs_spec.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[visualizer] Scatter saved → {path}")
    return path


# ─────────────────────────────────────────────
# 2. BAR — gross profit comparison
# ─────────────────────────────────────────────
def plot_profit_bar(results: pd.DataFrame, out_dir: str = "outputs") -> str:
    """Bar chart gross profit untuk setiap opsi upgrade."""
    fig, ax = plt.subplots(figsize=(8, 4.5))

    upgrades = results["upgrade"].tolist()
    profits  = results["gross_profit"].tolist()
    colors   = [PALETTE[i] for i in range(len(upgrades))]

    bars = ax.bar(upgrades, profits, color=colors, width=0.55, zorder=3)

    # Label nilai di atas/bawah bar
    for bar, val in zip(bars, profits):
        offset = 500 if val >= 0 else -2000
        va = "bottom" if val >= 0 else "top"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + offset, f"¥{val:,}",
            ha="center", va=va, fontsize=9, fontweight="bold",
        )

    ax.axhline(0, color="#888", linewidth=0.8, linestyle="--")
    ax.yaxis.set_major_formatter(FuncFormatter(_yen))
    ax.set_ylabel("Gross Profit (¥)", fontsize=10)
    ax.set_title("Perbandingan Gross Profit per Opsi Upgrade", fontsize=12, fontweight="bold")

    # Badge ranking
    for i, (bar, upgrade) in enumerate(zip(bars, upgrades)):
        if i == 0:
            ax.text(bar.get_x() + bar.get_width() / 2, max(profits) * 0.05,
                    "#1", ha="center", va="bottom", fontsize=11,
                    color="white", fontweight="bold")

    fig.tight_layout()
    path = os.path.join(out_dir, "profit_bar.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[visualizer] Bar chart saved → {path}")
    return path


# ─────────────────────────────────────────────
# 3. HEATMAP — spec correlation
# ─────────────────────────────────────────────
def plot_correlation_heatmap(df: pd.DataFrame, out_dir: str = "outputs") -> str:
    """Heatmap korelasi antara fitur spesifikasi dan harga pasar."""
    corr_cols = FEATURES + ["market_price_yen"]
    corr = df[corr_cols].corr()

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(corr.values, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")

    labels = ["Memory", "Storage", "CPU Class", "Screen", "Price"]
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_yticklabels(labels, fontsize=9)

    for i in range(len(labels)):
        for j in range(len(labels)):
            val = corr.values[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    fontsize=8, color="black" if abs(val) < 0.7 else "white")

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title("Korelasi Spesifikasi ↔ Harga Pasar", fontsize=11, fontweight="bold")
    fig.tight_layout()

    path = os.path.join(out_dir, "correlation_heatmap.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[visualizer] Heatmap saved → {path}")
    return path


# ─────────────────────────────────────────────
# COMBINED — semua chart sekaligus
# ─────────────────────────────────────────────
def generate_all(df: pd.DataFrame, results: pd.DataFrame, out_dir: str = "outputs") -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    paths = [
        plot_scatter(df, results, out_dir),
        plot_profit_bar(results, out_dir),
        plot_correlation_heatmap(df, out_dir),
    ]
    return paths
