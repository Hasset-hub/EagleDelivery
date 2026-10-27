import csv
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).parent
RESULTS = BASE / "results"
FIGURES = BASE / "report" / "figures"

BASELINE = [("baseline_SW", "S->W", 18), ("baseline_LD", "L->D", 22), ("baseline_HP", "H->P", 16)]
CUSTOM = [("custom_e005", "eps = 0.05", 12), ("custom_e020", "eps = 0.20", 12),
          ("custom_e050", "eps = 0.50", 12)]
COLORS = ["#2a6f97", "#c8553d", "#588157"]
SEEDS = [0, 1, 2]
WINDOW = 50
LATE = 500


def read_csv(filename):
    with open(filename, newline="") as source:
        return list(csv.DictReader(source))


def training_runs(folder):
    return [read_csv(RESULTS / folder / ("training_seed" + str(seed) + ".csv")) for seed in SEEDS]


def evaluation_runs(folder):
    return [read_csv(RESULTS / folder / ("evaluation_seed" + str(seed) + ".csv")) for seed in SEEDS]


def first_success_streak(run, length=20):
    streak = 0
    for row in run:
        streak = streak + 1 if row["success"] == "1" else 0
        if streak == length:
            return int(row["episode"]) - length + 1
    return "NA"


def first_optimal(run, optimal):
    for row in run:
        if row["success"] == "1" and int(row["steps"]) == optimal:
            return int(row["episode"])
    return "NA"


def metrics(folder, label, optimal):
    rows = []
    for seed, run, evaluation in zip(SEEDS, training_runs(folder), evaluation_runs(folder)):
        late = run[-LATE:]
        rows.append({
            "condition": folder,
            "label": label,
            "seed": seed,
            "optimal_steps": optimal,
            "training_success_rate": round(statistics.mean(int(r["success"]) for r in run), 4),
            "timeouts": sum(int(r["truncated"]) for r in run),
            "total_training_actions": sum(int(r["steps"]) for r in run),
            "first_optimal_episode": first_optimal(run, optimal),
            "first_20_success_streak": first_success_streak(run),
            "late_mean_steps": round(statistics.mean(int(r["steps"]) for r in late), 2),
            "late_mean_return": round(statistics.mean(int(r["return"]) for r in late), 2),
            "late_optimal_fraction": round(statistics.mean(
                int(r["success"] == "1" and int(r["steps"]) == optimal) for r in late), 4),
            "eval_success_rate": statistics.mean(int(r["success"]) for r in evaluation),
            "eval_mean_steps": statistics.mean(int(r["steps"]) for r in evaluation),
            "eval_mean_return": statistics.mean(int(r["return"]) for r in evaluation),
        })
    return rows


def smoothed(run, field):
    values = [float(r[field]) for r in run]
    return [statistics.mean(values[max(0, i - WINDOW + 1):i + 1]) for i in range(len(values))]


def mean_curve(folder, field):
    curves = [smoothed(run, field) for run in training_runs(folder)]
    return [statistics.mean(values) for values in zip(*curves)]


def plot_curves(groups, field, ylabel, title, filename, xmax=2000, ylim=None, logx=False):
    fig, ax = plt.subplots(figsize=(4.6, 2.7))
    for (folder, label, _), color in zip(groups, COLORS):
        curve = mean_curve(folder, field)
        ax.plot(range(1, len(curve) + 1), curve, label=label, color=color, linewidth=1.4)
    ax.set_xlabel("Training episode")
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=9)
    ax.set_xlim(1, xmax)
    if logx:
        ax.set_xscale("log")
    if ylim:
        ax.set_ylim(*ylim)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / filename, dpi=200)
    plt.close(fig)


def plot_late_steps(rows):
    fig, ax = plt.subplots(figsize=(4.6, 2.7))
    labels = [label for _, label, _ in CUSTOM]
    for index, (folder, label, _) in enumerate(CUSTOM):
        values = [r["late_mean_steps"] for r in rows if r["condition"] == folder]
        ax.bar(index, statistics.mean(values), color=COLORS[index], alpha=0.8, width=0.6)
        ax.scatter([index] * len(values), values, color="black", s=10, zorder=3)
        evals = [r["eval_mean_steps"] for r in rows if r["condition"] == folder]
        ax.scatter([index + 0.33], [statistics.mean(evals)], marker="D", color="white",
                   edgecolor="black", s=22, zorder=3)
    ax.axhline(12, color="gray", linestyle="--", linewidth=1)
    ax.text(-0.45, 12.6, "optimal = 12", fontsize=7, ha="left", color="gray")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Mean steps per episode")
    ax.set_xlim(-0.5, 2.6)
    ax.set_title("Custom S->W: training steps, last 500 episodes (bars, dots = seeds)\n"
                 "vs greedy evaluation steps (diamonds)", fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGURES / "custom_late_steps.png", dpi=200)
    plt.close(fig)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    rows = []
    for folder, label, optimal in BASELINE + CUSTOM:
        rows.extend(metrics(folder, label, optimal))
    with open(RESULTS / "training_metrics.csv", "w", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    plot_curves(BASELINE, "steps", "Steps per episode (50-ep mean)",
                "Baseline tasks: steps per training episode (mean of 3 seeds)",
                "baseline_steps.png", xmax=600, ylim=(0, 205))
    plot_curves(BASELINE, "success", "Success rate (50-ep mean)",
                "Baseline tasks: training success rate (mean of 3 seeds)",
                "baseline_success.png", xmax=600, ylim=(0, 1.05))
    plot_curves(CUSTOM, "steps", "Steps per episode (50-ep mean)",
                "Custom map S->W: steps per training episode (log x-axis)",
                "custom_steps.png", xmax=2000, ylim=(0, 205), logx=True)
    plot_late_steps(rows)
    for row in rows:
        print(row)
    print("Wrote", RESULTS / "training_metrics.csv", "and figures in", FIGURES)


if __name__ == "__main__":
    main()
