"""Disk-head scheduling algorithms."""
def _validate(requests, head, disk_size):
    if not isinstance(disk_size, int) or disk_size < 2:
        raise ValueError("Disk size must be an integer >= 2.")
    if not isinstance(head, int) or not 0 <= head < disk_size:
        raise ValueError("Initial head must be within disk boundaries.")
    if any(not isinstance(x, int) or not 0 <= x < disk_size for x in requests):
        raise ValueError("Every request must be within disk boundaries.")
def _result(name, order, head):
    pos, total, path = head, 0, [head]
    for x in order:
        total += abs(pos - x); pos = x; path.append(x)
    return {"algorithm": name, "sequence": order, "path": path, "total_movement": total}
def fcfs(requests, head, disk_size=200):
    _validate(requests, head, disk_size)
    return _result("FCFS", list(requests), head)
def sstf(requests, head, disk_size=200):
    _validate(requests, head, disk_size)
    pending, pos, order = list(requests), head, []
    while pending:
        x = min(pending, key=lambda r: (abs(r-pos), r))
        order.append(x); pending.remove(x); pos = x
    return _result("SSTF", order, head)
def scan(requests, head, disk_size=200, direction="left"):
    _validate(requests, head, disk_size)
    if direction not in {"left", "right"}:
        raise ValueError("Direction must be 'left' or 'right'.")
    left = sorted([x for x in requests if x < head], reverse=True)
    right = sorted([x for x in requests if x >= head])
    if direction == "left":
        order = left + ([0] if not left or left[-1] != 0 else []) + right
    else:
        order = right + ([disk_size-1] if not right or right[-1] != disk_size-1 else []) + left
    return _result(f"SCAN ({direction})", order, head)
def cscan(requests, head, disk_size=200, direction="right"):
    _validate(requests, head, disk_size)
    if direction not in {"left", "right"}:
        raise ValueError("Direction must be 'left' or 'right'.")
    left = sorted([x for x in requests if x < head])
    right = sorted([x for x in requests if x >= head])
    if direction == "right":
        order = right + ([disk_size-1] if not right or right[-1] != disk_size-1 else []) + ([0] if left else []) + left
    else:
        order = list(reversed(left)) + ([0] if not left or left[0] != 0 else []) + ([disk_size-1] if right else []) + list(reversed(right))
    return _result(f"C-SCAN ({direction})", order, head)
