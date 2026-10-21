"""
plot_benchmark.py
Generates publication-quality comparison charts from benchmark CSV results.
Produces:
  1. outputs/benchmark_summary.png  (Combined 3-panel figure for academic report)
  2. outputs/chart_time.png         (Execution Time vs Board Size)
  3. outputs/chart_memory.png       (Peak RAM Usage vs Board Size)
  4. outputs/chart_nodes.png        (Nodes Explored vs Board Size)
"""

import os
import csv
import matplotlib.pyplot as plt
import numpy as np

def load_benchmark_data(csv_path: str = "outputs/benchmark_results.csv") -> dict:
    """Reads benchmark CSV and structures data by algorithm."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Benchmark file not found at: {csv_path}")

    data = {}
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            algo = row["algorithm"]
            size = row["size"]
            time_ms = float(row["time_ms"])
            memory_kb = float(row["memory_kb"])
            nodes = int(row["nodes_explored"])

            if algo not in data:
                data[algo] = {"sizes": [], "time_ms": [], "memory_kb": [], "nodes": []}

            data[algo]["sizes"].append(size)
            data[algo]["time_ms"].append(time_ms)
            data[algo]["memory_kb"].append(memory_kb)
            data[algo]["nodes"].append(nodes)

    return data

def plot_benchmarks(csv_path: str = "outputs/benchmark_results.csv", output_dir: str = "outputs") -> None:
    """Generates and saves modern, high-resolution charts."""
    os.makedirs(output_dir, exist_ok=True)
    data = load_benchmark_data(csv_path)

    # Styling settings
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
    plt.rcParams['axes.edgecolor'] = '#cbd5e1'
    plt.rcParams['axes.linewidth'] = 0.8

    colors = {
        "DFS (Backtracking)": "#0284c7",  # Deep Sky Blue
        "A* Search": "#ea580c"           # Bright Orange
    }
    markers = {
        "DFS (Backtracking)": "o",
        "A* Search": "s"
    }

    # Extract common sizes
    sample_algo = next(iter(data.keys()))
    sizes = data[sample_algo]["sizes"]
    x = np.arange(len(sizes))

    # =========================================================================
    # 1. Combined 3-Panel Figure (Ideal for A4 Paper Report)
    # =========================================================================
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), dpi=300)
    fig.patch.set_facecolor('#ffffff')

    metrics = [
        ("time_ms", "Execution Time (ms)", "Thời gian thực thi (ms)", axes[0]),
        ("memory_kb", "Peak Memory (KB)", "Bộ nhớ RAM đỉnh (KB)", axes[1]),
        ("nodes", "Nodes Explored", "Số lượng nút duyệt (Nodes)", axes[2])
    ]

    for metric_key, y_label_en, y_label_vn, ax in metrics:
        ax.set_facecolor('#f8fafc')
        ax.grid(True, linestyle='--', alpha=0.6, color='#94a3b8')

        for algo_name, metrics_dict in data.items():
            vals = metrics_dict[metric_key]
            color = colors.get(algo_name, "#475569")
            marker = markers.get(algo_name, "o")

            line = ax.plot(x, vals, label=algo_name, color=color, marker=marker,
                           linewidth=2.4, markersize=7, alpha=0.95)

            # Annotate values on points
            for xi, yi in zip(x, vals):
                offset = (0, 7) if algo_name == "A* Search" else (0, -12)
                ax.annotate(f"{yi:g}", (xi, yi), textcoords="offset points",
                            xytext=offset, ha='center', fontsize=8,
                            fontweight='semibold', color=color)

        ax.set_xticks(x)
        ax.set_xticklabels(sizes, fontweight='semibold', fontsize=10)
        ax.set_xlabel("Grid Size (Kích thước bàn cờ)", fontsize=11, fontweight='bold', labelpad=8)
        ax.set_ylabel(y_label_en, fontsize=11, fontweight='bold', labelpad=8)
        ax.set_title(f"{y_label_en}\n({y_label_vn})", fontsize=12, fontweight='bold', pad=10, color='#0f172a')
        ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0', fontsize=9.5)

    plt.tight_layout()
    combined_path = os.path.join(output_dir, "benchmark_summary.png")
    plt.savefig(combined_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f" [OK] Generated combined chart: {combined_path}")

    # =========================================================================
    # 2. Individual High-Res Charts (Perfect for Presentation Slides)
    # =========================================================================
    individual_configs = [
        ("time_ms", "Execution Time (ms)", "chart_time.png", False),
        ("memory_kb", "Peak Memory Consumption (KB)", "chart_memory.png", False),
        ("nodes", "Search Space Exploration (Nodes)", "chart_nodes.png", False)
    ]

    for metric_key, title, filename, use_log in individual_configs:
        plt.figure(figsize=(8, 5), dpi=300)
        ax = plt.gca()
        ax.set_facecolor('#f8fafc')
        ax.grid(True, linestyle='--', alpha=0.6, color='#94a3b8')

        width = 0.35
        for i, (algo_name, metrics_dict) in enumerate(data.items()):
            vals = metrics_dict[metric_key]
            color = colors.get(algo_name, "#475569")
            pos = x - width / 2 if i == 0 else x + width / 2

            bars = ax.bar(pos, vals, width=width, label=algo_name, color=color, alpha=0.9, edgecolor='#0f172a', linewidth=0.5)

            # Annotate bar tops
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height:g}",
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 4), textcoords="offset points",
                            ha='center', va='bottom', fontsize=8.5, fontweight='bold', color=color)

        ax.set_xticks(x)
        ax.set_xticklabels(sizes, fontweight='bold', fontsize=10)
        ax.set_xlabel("Grid Size", fontsize=11, fontweight='bold', labelpad=8)
        ax.set_ylabel(title, fontsize=11, fontweight='bold', labelpad=8)
        ax.set_title(f"Comparison: {title}", fontsize=13, fontweight='bold', pad=12, color='#0f172a')
        ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=10)

        chart_path = os.path.join(output_dir, filename)
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f" [OK] Generated individual chart: {chart_path}")

if __name__ == "__main__":
    plot_benchmarks()
