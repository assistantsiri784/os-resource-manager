"""CSV, text summaries, charts, and application logging."""
import csv, logging
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
LOGS = ROOT / "logs"
RESULTS.mkdir(exist_ok=True); LOGS.mkdir(exist_ok=True)
logging.basicConfig(filename=LOGS / "app.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

def log_event(message):
    logging.info(message)

def save_schedule(result):
    path = RESULTS / "scheduling_metrics.csv"
    fields = ["algorithm", "pid", "arrival", "burst", "priority", "start",
              "completion", "turnaround", "waiting", "response"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in result["metrics"]:
            writer.writerow({"algorithm": result["algorithm"], **row})
    return path

def save_comparison(results):
    path = RESULTS / "scheduling_comparison.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        fields = ["algorithm", "avg_waiting", "avg_turnaround", "avg_response"]
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        for r in results:
            writer.writerow({"algorithm": r["algorithm"],
                "avg_waiting": r["averages"]["waiting"],
                "avg_turnaround": r["averages"]["turnaround"],
                "avg_response": r["averages"]["response"]})
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        labels = [r["algorithm"] for r in results]
        x = list(range(len(labels)))
        fig, ax = plt.subplots(figsize=(10, 5))
        width = 0.25
        for offset, metric, label in [(-width, "waiting", "Average waiting"),
                                      (0, "turnaround", "Average turnaround"),
                                      (width, "response", "Average response")]:
            ax.bar([i + offset for i in x], [r["averages"][metric] for r in results],
                   width=width, label=label)
        ax.set_xticks(x); ax.set_xticklabels(labels, rotation=20, ha="right")
        ax.set_ylabel("Time units"); ax.set_title("CPU Scheduling Algorithm Comparison")
        ax.legend(); ax.grid(axis="y", alpha=0.25); fig.tight_layout()
        fig.savefig(RESULTS / "scheduling_comparison.png", dpi=160)
        plt.close(fig)
    except ImportError:
        logging.warning("matplotlib unavailable; chart generation skipped.")
    return path

def save_disk_comparison(results):
    path = RESULTS / "disk_comparison.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["algorithm", "sequence", "total_movement"])
        writer.writeheader()
        for r in results:
            writer.writerow({"algorithm": r["algorithm"], "sequence": " -> ".join(map(str, r["sequence"])),
                             "total_movement": r["total_movement"]})
    return path
