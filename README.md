# OS Resource Manager — Python + Bash Capstone

## Overview
A single command-line application that simulates CPU scheduling, contiguous memory allocation, deadlock safety/detection, and disk scheduling. Python implements the algorithms and analysis; Bash checks the environment and launches the same application.

## Requirements
- Ubuntu Linux
- Python 3.10 or newer (3.8+ may work, depending on Matplotlib version)
- `python3-venv`
- VS Code (recommended)

On Ubuntu, install the environment tools if needed:
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

## Run
From the project directory:
```bash
chmod +x run.sh
./run.sh
```
The launcher creates `.venv`, installs requirements on the first normal launch, and opens the menu.

Run all sample simulations and generate files:
```bash
./run.sh --demo
```

Run automated tests:
```bash
./run.sh --test
```

## Modules
- `src/scheduler.py`: FCFS, SJF (non-preemptive), SRTF, preemptive Priority (lower number means higher priority), Round Robin.
- `src/memory.py`: First Fit, Best Fit, Worst Fit. Blocks can be split; leftover space remains available.
- `src/deadlock.py`: Banker's safety algorithm and a separate deadlock detection routine.
- `src/disk.py`: FCFS, SSTF, SCAN, C-SCAN. Disk cylinder range is `0` through `disk_size - 1`.
- `src/reporting.py`: CSV reports, comparison chart, logging.
- `src/main.py`: common menu/controller and demo workflow.

## Input
`data/processes.csv` uses:
`pid,arrival,burst,priority,memory`
- `arrival`: non-negative integer
- `burst`: positive integer
- `priority`: integer; lower value means higher priority
- `memory`: positive integer

Disk sample data is in `data/disk_requests.json`. The demo uses the request sequence and matrix examples embedded in `src/main.py`.

## Output
Generated files are saved in `results/`; activity and error logs go to `logs/app.log`. The chart is generated when Matplotlib is installed.

## Testing
The `tests/` directory includes algorithm and validation tests. Use `./run.sh --test` after creating the virtual environment. The `--test` option runs tests without installing Matplotlib; chart generation requires Matplotlib.

## Important algorithm assumptions
- CPU times use consistent integer time units.
- Round Robin uses the selected positive time quantum.
- Priority scheduling is preemptive in this implementation; a lower numeric priority is higher priority.
- Memory blocks are split, so remaining space in an allocated block is reusable.
- Banker's algorithm checks safety against maximum claims. Deadlock detection uses current outstanding requests.
- SCAN/C-SCAN include disk-boundary movement according to the implementation; this assumption should be stated when comparing totals.

## Suggested screenshots for submission
Capture actual output after running the program:
1. Menu at launch.
2. CPU scheduling Gantt trace and metrics.
3. `results/scheduling_comparison.png`.
4. Memory allocation output.
5. Banker's safe-state result and a deadlock-detection test.
6. Disk scheduling totals.
7. `./run.sh --test` output.
8. Generated CSV files and `logs/app.log`.

## Report outline
1. Abstract
2. Problem statement and objectives
3. System architecture and data flow
4. Algorithms and implementation
5. Results and comparative analysis
6. Testing and reliability
7. Limitations and future work
8. Conclusion and references

## Limitations
This is an educational simulator, not a kernel or live resource manager. CPU scheduling metrics ignore context-switch overhead. The memory model is simplified contiguous allocation. The sample menu demonstrates Banker's safety; call `detect_deadlock()` with custom matrices or extend the menu to accept matrix input for interactive detection.
