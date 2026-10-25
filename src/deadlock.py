"""Banker's safety check and deadlock detection."""
def bankers_safety(allocation, maximum, available):
    if len(allocation) != len(maximum):
        raise ValueError("Allocation and maximum matrices must have equal row counts.")
    resources = len(available)
    if any(len(row) != resources for row in allocation + maximum):
        raise ValueError("Every matrix row must match the available vector length.")
    if any(x < 0 for row in allocation + maximum for x in row) or any(x < 0 for x in available):
        raise ValueError("Resource counts cannot be negative.")
    if any(maximum[i][j] < allocation[i][j] for i in range(len(allocation)) for j in range(resources)):
        raise ValueError("Maximum claim cannot be less than current allocation.")
    need = [[maximum[i][j] - allocation[i][j] for j in range(resources)]
            for i in range(len(allocation))]
    work = list(available)
    finish = [False] * len(allocation)
    sequence = []
    while True:
        progress = False
        for i in range(len(allocation)):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(resources)):
                work = [work[j] + allocation[i][j] for j in range(resources)]
                finish[i] = True; sequence.append(f"P{i}"); progress = True
        if not progress:
            break
    return {"safe": all(finish), "sequence": sequence if all(finish) else [],
            "unfinished": [f"P{i}" for i, done in enumerate(finish) if not done], "need": need}

def detect_deadlock(allocation, request, available):
    if len(allocation) != len(request):
        raise ValueError("Allocation and request matrices must have equal row counts.")
    resources = len(available)
    if any(len(row) != resources for row in allocation + request):
        raise ValueError("Every matrix row must match the available vector length.")
    if any(x < 0 for row in allocation + request for x in row) or any(x < 0 for x in available):
        raise ValueError("Resource counts cannot be negative.")
    work = list(available)
    # A process holding no resources can be treated as finishable for detection.
    finish = [all(x == 0 for x in row) for row in allocation]
    progress = True
    while progress:
        progress = False
        for i in range(len(allocation)):
            if not finish[i] and all(request[i][j] <= work[j] for j in range(resources)):
                work = [work[j] + allocation[i][j] for j in range(resources)]
                finish[i] = True; progress = True
    return {"deadlocked": [f"P{i}" for i, done in enumerate(finish) if not done],
            "deadlock_detected": not all(finish), "finish": finish}
