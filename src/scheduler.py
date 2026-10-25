"""CPU scheduling algorithms. Time units are arbitrary consistent units."""
from collections import deque
from copy import deepcopy

def _validate(processes):
    if not processes:
        raise ValueError("At least one process is required.")
    required = {"pid", "arrival", "burst", "priority"}
    seen = set()
    normalized = []
    for p in processes:
        if not required.issubset(p):
            raise ValueError(f"Each process must contain {sorted(required)}.")
        q = dict(p)
        if not isinstance(q["pid"], str) or not q["pid"].strip():
            raise ValueError("Process ID must be a non-empty string.")
        if q["pid"] in seen:
            raise ValueError(f"Duplicate process ID: {q['pid']}")
        seen.add(q["pid"])
        for key in ("arrival", "burst", "priority"):
            if not isinstance(q[key], int):
                raise ValueError(f"{key} for {q['pid']} must be an integer.")
        if q["arrival"] < 0 or q["burst"] <= 0:
            raise ValueError("Arrival must be >= 0 and burst must be > 0.")
        normalized.append(q)
    return normalized

def _finish(processes, segments, first_start):
    completion = {}
    for s in segments:
        completion[s["pid"]] = s["end"]
    metrics = []
    for p in processes:
        pid = p["pid"]
        ct = completion[pid]
        tat = ct - p["arrival"]
        wt = tat - p["burst"]
        rt = first_start[pid] - p["arrival"]
        metrics.append({"pid": pid, "arrival": p["arrival"], "burst": p["burst"],
                        "priority": p["priority"], "start": first_start[pid],
                        "completion": ct, "turnaround": tat, "waiting": wt, "response": rt})
    n = len(metrics)
    averages = {k: round(sum(m[k] for m in metrics) / n, 2)
                for k in ("waiting", "turnaround", "response")}
    return {"algorithm": "", "segments": segments, "metrics": metrics, "averages": averages}

def _segments_from_order(order):
    """Merge adjacent intervals of the same PID; order items are (pid,start,end)."""
    out = []
    for pid, start, end in order:
        if end <= start:
            continue
        if out and out[-1]["pid"] == pid and out[-1]["end"] == start:
            out[-1]["end"] = end
        else:
            out.append({"pid": pid, "start": start, "end": end})
    return out

def fcfs(processes):
    ps = _validate(processes)
    time, order, first = 0, [], {}
    for p in sorted(ps, key=lambda x: (x["arrival"], x["pid"])):
        if time < p["arrival"]:
            order.append(("IDLE", time, p["arrival"]))
            time = p["arrival"]
        first.setdefault(p["pid"], time)
        order.append((p["pid"], time, time + p["burst"]))
        time += p["burst"]
    result = _finish(ps, _segments_from_order(order), first)
    result["algorithm"] = "FCFS"
    return result

def sjf(processes):
    ps = _validate(processes)
    remaining = {p["pid"]: p["burst"] for p in ps}
    by_id = {p["pid"]: p for p in ps}
    time, done, order, first = 0, set(), [], {}
    while len(done) < len(ps):
        ready = [p for p in ps if p["pid"] not in done and p["arrival"] <= time]
        if not ready:
            nxt = min(p["arrival"] for p in ps if p["pid"] not in done)
            order.append(("IDLE", time, nxt)); time = nxt
            continue
        p = min(ready, key=lambda x: (x["burst"], x["arrival"], x["pid"]))
        first[p["pid"]] = time
        order.append((p["pid"], time, time + p["burst"]))
        time += p["burst"]; done.add(p["pid"])
    result = _finish(ps, _segments_from_order(order), first)
    result["algorithm"] = "SJF (non-preemptive)"
    return result

def srtf(processes):
    ps = _validate(processes)
    remaining = {p["pid"]: p["burst"] for p in ps}
    by_id = {p["pid"]: p for p in ps}
    time, order, first, completed = 0, [], {}, set()
    while len(completed) < len(ps):
        ready = [p for p in ps if p["pid"] not in completed and p["arrival"] <= time and remaining[p["pid"]] > 0]
        if not ready:
            nxt = min(p["arrival"] for p in ps if p["pid"] not in completed and p["arrival"] > time)
            order.append(("IDLE", time, nxt)); time = nxt
            continue
        p = min(ready, key=lambda x: (remaining[x["pid"]], x["arrival"], x["pid"]))
        pid = p["pid"]
        first.setdefault(pid, time)
        order.append((pid, time, time + 1))
        remaining[pid] -= 1; time += 1
        if remaining[pid] == 0:
            completed.add(pid)
    result = _finish(ps, _segments_from_order(order), first)
    result["algorithm"] = "SRTF"
    return result

def priority_preemptive(processes):
    ps = _validate(processes)
    remaining = {p["pid"]: p["burst"] for p in ps}
    time, order, first, completed = 0, [], {}, set()
    while len(completed) < len(ps):
        ready = [p for p in ps if p["pid"] not in completed and p["arrival"] <= time and remaining[p["pid"]] > 0]
        if not ready:
            nxt = min(p["arrival"] for p in ps if p["pid"] not in completed and p["arrival"] > time)
            order.append(("IDLE", time, nxt)); time = nxt
            continue
        p = min(ready, key=lambda x: (x["priority"], x["arrival"], x["pid"]))
        pid = p["pid"]; first.setdefault(pid, time)
        order.append((pid, time, time + 1)); remaining[pid] -= 1; time += 1
        if remaining[pid] == 0:
            completed.add(pid)
    result = _finish(ps, _segments_from_order(order), first)
    result["algorithm"] = "Priority (preemptive; lower number = higher priority)"
    return result

def round_robin(processes, quantum=2):
    ps = _validate(processes)
    if not isinstance(quantum, int) or quantum <= 0:
        raise ValueError("Round Robin quantum must be a positive integer.")
    remaining = {p["pid"]: p["burst"] for p in ps}
    arrivals = sorted(ps, key=lambda x: (x["arrival"], x["pid"]))
    queue, idx, time, order, first, completed = deque(), 0, 0, [], {}, set()
    while len(completed) < len(ps):
        while idx < len(arrivals) and arrivals[idx]["arrival"] <= time:
            queue.append(arrivals[idx]["pid"]); idx += 1
        if not queue:
            nxt = arrivals[idx]["arrival"]
            order.append(("IDLE", time, nxt)); time = nxt
            continue
        pid = queue.popleft()
        first.setdefault(pid, time)
        run_for = min(quantum, remaining[pid])
        end = time + run_for
        order.append((pid, time, end))
        # New arrivals during this time slice enter before the current process is re-queued.
        while idx < len(arrivals) and arrivals[idx]["arrival"] < end:
            queue.append(arrivals[idx]["pid"]); idx += 1
        time = end; remaining[pid] -= run_for
        while idx < len(arrivals) and arrivals[idx]["arrival"] <= time:
            queue.append(arrivals[idx]["pid"]); idx += 1
        if remaining[pid] > 0:
            queue.append(pid)
        else:
            completed.add(pid)
    result = _finish(ps, _segments_from_order(order), first)
    result["algorithm"] = f"Round Robin (q={quantum})"
    return result

def compare_all(processes, quantum=2):
    funcs = [fcfs, sjf, srtf, priority_preemptive]
    results = [f(processes) for f in funcs]
    results.append(round_robin(processes, quantum))
    return results
