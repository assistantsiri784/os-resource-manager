"""Contiguous partition allocation simulations."""
def allocate_memory(processes, blocks, strategy="first_fit"):
    if strategy not in {"first_fit", "best_fit", "worst_fit"}:
        raise ValueError("Strategy must be first_fit, best_fit, or worst_fit.")
    if any(not isinstance(b, int) or b <= 0 for b in blocks):
        raise ValueError("Memory block sizes must be positive integers.")
    normalized = []
    for p in processes:
        pid, size = p.get("pid"), p.get("memory")
        if not pid or not isinstance(size, int) or size <= 0:
            raise ValueError("Each process needs a PID and positive integer memory size.")
        normalized.append({"pid": pid, "memory": size})
    remaining = list(blocks)
    allocations, unallocated = [], []
    for p in normalized:
        candidates = [i for i, size in enumerate(remaining) if size >= p["memory"]]
        if not candidates:
            unallocated.append(p["pid"])
            continue
        if strategy == "first_fit":
            chosen = candidates[0]
        elif strategy == "best_fit":
            chosen = min(candidates, key=lambda i: remaining[i])
        else:
            chosen = max(candidates, key=lambda i: remaining[i])
        before = remaining[chosen]
        remaining[chosen] -= p["memory"]  # Blocks can be split; leftover stays available.
        allocations.append({"pid": p["pid"], "requested": p["memory"],
                            "block_index": chosen, "block_before": before,
                            "remaining_in_block": remaining[chosen]})
    return {"strategy": strategy, "allocations": allocations,
            "unallocated": unallocated, "remaining_blocks": remaining,
            "total_free_remaining": sum(remaining)}
