"""Integrated command-line OS Resource Manager."""
import argparse, csv, json, sys
from pathlib import Path
from . import scheduler, memory, deadlock, disk, reporting

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processes.csv"

def load_processes(path=DATA):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    required = {"pid", "arrival", "burst", "priority", "memory"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("Process CSV must contain pid,arrival,burst,priority,memory.")
    out = []
    for r in rows:
        try:
            out.append({"pid": r["pid"].strip(), "arrival": int(r["arrival"]),
                        "burst": int(r["burst"]), "priority": int(r["priority"]),
                        "memory": int(r["memory"])})
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid numeric value in process row: {r}") from e
    return out

def show_schedule(result):
    print(f"\n{result['algorithm']}")
    print("Gantt: " + " | ".join(f"{s['pid']}[{s['start']}-{s['end']}]" for s in result["segments"]))
    print(f"{'PID':<8}{'CT':>6}{'TAT':>8}{'WT':>8}{'RT':>8}")
    for m in result["metrics"]:
        print(f"{m['pid']:<8}{m['completion']:>6}{m['turnaround']:>8}{m['waiting']:>8}{m['response']:>8}")
    print("Averages:", result["averages"])

def demo():
    ps = load_processes()
    print("OS RESOURCE MANAGER — DEMO")
    print("Loaded sample processes:", ", ".join(p["pid"] for p in ps))
    results = scheduler.compare_all(ps, quantum=2)
    for r in results:
        show_schedule(r)
    reporting.save_comparison(results)
    print("\nMemory allocation (First Fit):")
    mem = memory.allocate_memory(ps, [100, 200, 150, 250, 120], "first_fit")
    print(json.dumps(mem, indent=2))
    print("\nBanker's safety example:")
    safe = deadlock.bankers_safety([[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]],
                                   [[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]], [3,3,2])
    print(json.dumps(safe, indent=2))
    print("\nDisk scheduling example:")
    ds = [disk.fcfs([82,170,43,140,24,16,190], 50, 200),
          disk.sstf([82,170,43,140,24,16,190], 50, 200),
          disk.scan([82,170,43,140,24,16,190], 50, 200, "left"),
          disk.cscan([82,170,43,140,24,16,190], 50, 200, "right")]
    reporting.save_disk_comparison(ds)
    for r in ds:
        print(f"{r['algorithm']}: movement={r['total_movement']}, path={r['path']}")
    reporting.log_event("Demo completed successfully")
    print(f"\nSaved reports in: {ROOT / 'results'}")
    print(f"Activity log: {ROOT / 'logs' / 'app.log'}")

def menu():
    while True:
        print("\n" + "="*43 + "\n        OS RESOURCE MANAGER\n" + "="*43)
        print("1. CPU Scheduling comparison")
        print("2. Memory allocation")
        print("3. Deadlock safety example")
        print("4. Disk scheduling comparison")
        print("5. Run complete demo and generate reports")
        print("0. Exit")
        choice = input("Enter choice: ").strip()
        try:
            ps = load_processes()
            if choice == "1":
                print("1 FCFS | 2 SJF | 3 SRTF | 4 Priority | 5 Round Robin")
                alg = input("Choose algorithm: ").strip()
                if alg == "1": r = scheduler.fcfs(ps)
                elif alg == "2": r = scheduler.sjf(ps)
                elif alg == "3": r = scheduler.srtf(ps)
                elif alg == "4": r = scheduler.priority_preemptive(ps)
                elif alg == "5":
                    q = int(input("Time quantum (positive integer): "))
                    r = scheduler.round_robin(ps, q)
                else:
                    print("Invalid algorithm choice."); continue
                show_schedule(r); reporting.save_schedule(r); reporting.log_event(f"Ran {r['algorithm']}")
            elif choice == "2":
                print("1 First Fit | 2 Best Fit | 3 Worst Fit")
                alg = input("Choose strategy: ").strip()
                strategy = {"1":"first_fit","2":"best_fit","3":"worst_fit"}.get(alg)
                if not strategy: print("Invalid strategy."); continue
                sizes = input("Enter comma-separated memory block sizes [100,200,150,250,120]: ").strip()
                blocks = [int(x.strip()) for x in sizes.split(",")] if sizes else [100,200,150,250,120]
                r = memory.allocate_memory(ps, blocks, strategy)
                print(json.dumps(r, indent=2)); reporting.log_event(f"Ran memory {strategy}")
            elif choice == "3":
                r = deadlock.bankers_safety([[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]],
                    [[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]], [3,3,2])
                print(json.dumps(r, indent=2)); reporting.log_event("Ran Banker's safety example")
            elif choice == "4":
                req = [82,170,43,140,24,16,190]; head = 50; size = 200
                results = [disk.fcfs(req,head,size), disk.sstf(req,head,size),
                           disk.scan(req,head,size,"left"), disk.cscan(req,head,size,"right")]
                for r in results: print(f"{r['algorithm']}: {r['total_movement']} cylinders; {r['path']}")
                reporting.save_disk_comparison(results); reporting.log_event("Ran disk comparison")
            elif choice == "5":
                demo()
            elif choice == "0":
                print("Exiting OS Resource Manager."); return
            else:
                print("Invalid menu option. Enter 0–5.")
        except (ValueError, OSError) as exc:
            print(f"Input or execution error: {exc}")
            reporting.logging.exception("Operation failed")
        except Exception as exc:
            print(f"Unexpected error: {exc}")
            reporting.logging.exception("Unexpected application error")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Run all sample simulations without prompts.")
    args = parser.parse_args()
    if args.demo: demo()
    else: menu()

if __name__ == "__main__":
    main()
