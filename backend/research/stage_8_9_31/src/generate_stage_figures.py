"""
Stage 8.9.31 - Visualization Generator.
Generates high-resolution diagnostic plots for Stage 8.9.31:
1. dual_resolution_window_alignment.png
2. latency_concurrency_scaling.png
3. continuous_simulation_timeline.png
"""

from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BACKEND_DIR = Path("backend").resolve()
STAGE_31_DIR = BACKEND_DIR / "research" / "stage_8_9_31"
FIG_DIR = STAGE_31_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def generate_figures():
    print("=" * 70)
    print("STAGE 8.9.31 - GENERATING VISUALIZATION FIGURES")
    print("=" * 70)

    # 1. Plot Dual-Resolution Window Alignment vs Legacy Underflow
    fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    durations = [0.395, 0.421, 0.499, 0.650, 0.719, 0.766]
    labels = ["FS_686340\n(0.395s)", "FS_382990\n(0.421s)", "NIGENS_15246\n(0.499s)",
              "FS_788867\n(0.650s)", "FS_222582\n(0.719s)", "FS_547188\n(0.766s)"]

    x = np.arange(len(durations))
    width = 0.28

    legacy_wins = [0, 0, 0, 0, 0, 0]
    micro_wins = [2, 2, 3, 4, 5, 5]
    macro_wins = [1, 1, 1, 1, 1, 1]

    ax.bar(x - width, legacy_wins, width, label="Legacy Buffer (0.975s, No Flush)", color="#d62728", alpha=0.8)
    ax.bar(x, micro_wins, width, label="Stage 8.9.31 Micro Branch (375ms / 100ms)", color="#2ca02c", alpha=0.85)
    ax.bar(x + width, macro_wins, width, label="Stage 8.9.31 Macro Branch (975ms + Flush)", color="#1f77b4", alpha=0.85)

    ax.set_ylabel("Extracted Windows Count", fontsize=11, fontweight="bold")
    ax.set_title("Stage 8.9.31: Resolution of Ring-Buffer Underflow Across 6 Short Screams", fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.legend(fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5, axis="y")

    p1 = FIG_DIR / "dual_resolution_window_alignment.png"
    plt.savefig(str(p1), dpi=200)
    plt.close()
    print(f"[Generated Figure] {p1}")

    # 2. Plot Latency and Concurrency Scaling
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    conc_csv = STAGE_31_DIR / "concurrency_benchmark.csv"
    with open(conc_csv, "r", encoding="utf-8") as f:
        c_rows = list(csv.DictReader(f))

    streams = [int(r["concurrent_streams"]) for r in c_rows]
    p50_lat = [float(r["p50_latency_ms"]) for r in c_rows]
    p95_lat = [float(r["p95_latency_ms"]) for r in c_rows]
    throughput = [float(r["throughput_hops_per_sec"]) for r in c_rows]

    # Latency curve
    ax1.plot(streams, p50_lat, "o-", color="#1f77b4", lw=2, label="Median P50 Latency")
    ax1.plot(streams, p95_lat, "s--", color="#d62728", lw=2, label="P95 Latency")
    ax1.axhline(25.0, color="gray", linestyle=":", label="P95 Engineering Target (25ms)")
    ax1.axhline(100.0, color="orange", linestyle="--", label="100ms Micro-Hop Deadline")
    ax1.set_xlabel("Concurrent Ingestion Streams", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Latency (ms)", fontsize=10, fontweight="bold")
    ax1.set_title("Computational Latency Scaling", fontsize=11, fontweight="bold")
    ax1.set_xticks(streams)
    ax1.legend(fontsize=9)
    ax1.grid(True, linestyle="--", alpha=0.5)

    # Throughput curve
    ax2.plot(streams, throughput, "^-", color="#2ca02c", lw=2, label="Throughput (hops/sec)")
    ax2.set_xlabel("Concurrent Ingestion Streams", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Aggregate Hops / Sec", fontsize=10, fontweight="bold")
    ax2.set_title("System Processing Throughput", fontsize=11, fontweight="bold")
    ax2.set_xticks(streams)
    ax2.legend(fontsize=9)
    ax2.grid(True, linestyle="--", alpha=0.5)

    p2 = FIG_DIR / "latency_concurrency_scaling.png"
    plt.savefig(str(p2), dpi=200)
    plt.close()
    print(f"[Generated Figure] {p2}")

    # 3. Plot Continuous Simulation Timeline
    fig, ax = plt.subplots(figsize=(12, 4.5), constrained_layout=True)
    sim_csv = STAGE_31_DIR / "continuous_simulation_results.csv"
    with open(sim_csv, "r", encoding="utf-8") as f:
        s_rows = list(csv.DictReader(f))

    timestamps = [float(r["timestamp_sec"]) for r in s_rows]
    scores = [float(r["primary_score"]) for r in s_rows]

    ax.plot(timestamps, scores, color="#1f77b4", lw=1.5, label="Duration-Aware Fusion Score")
    ax.axhline(0.3500, color="#d62728", linestyle="--", lw=1.5, label="Decision Threshold (0.3500)")

    # Ground truth event spans
    ax.axvspan(4.0, 4.4, color="green", alpha=0.25, label="Short Scream 1 (0.395s)")
    ax.axvspan(8.0, 12.0, color="gray", alpha=0.15, label="Normal Speech")
    ax.axvspan(16.0, 16.65, color="green", alpha=0.25, label="Short Scream 2 (0.650s)")
    ax.axvspan(20.0, 23.0, color="orange", alpha=0.2, label="Shouted Command")
    ax.axvspan(26.0, 31.0, color="red", alpha=0.15, label="Stadium Cheering")
    ax.axvspan(35.0, 35.42, color="green", alpha=0.25, label="Short Scream 3 (0.421s)")
    ax.axvspan(40.0, 44.0, color="purple", alpha=0.15, label="Infant Crying")
    ax.axvspan(48.0, 51.0, color="green", alpha=0.25, label="Sustained Scream (3.0s)")

    ax.set_xlabel("Timeline Position (Seconds)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Inference Probability Score", fontsize=10, fontweight="bold")
    ax.set_title("Stage 8.9.31: 60-Second Multi-Event Continuous Streaming Simulation", fontsize=11, fontweight="bold")
    ax.set_xlim([0, 60])
    ax.set_ylim([0, 1.05])
    ax.grid(True, linestyle="--", alpha=0.5)

    p3 = FIG_DIR / "continuous_simulation_timeline.png"
    plt.savefig(str(p3), dpi=200)
    plt.close()
    print(f"[Generated Figure] {p3}")


if __name__ == "__main__":
    generate_figures()
