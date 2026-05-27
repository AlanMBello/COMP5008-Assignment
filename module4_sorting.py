import random
import time
# ══════════════════════════════════════════════════════════════════════════════
#  Merge Sort  (top-down, stable)
# ══════════════════════════════════════════════════════════════════════════════
def merge_sort(arr: list, key=None) -> list:
    if key is None:
        key = lambda x: x
    if len(arr) <= 1:
        return list(arr)
    mid   = len(arr) // 2
    left  = merge_sort(arr[:mid],  key)
    right = merge_sort(arr[mid:], key)
    return _merge(left, right, key)

def _merge(left: list, right: list, key) -> list:
    result = []
    i = j  = 0
    while i < len(left) and j < len(right):
        # Stable: prefer left when keys are equal
        if key(left[i]) <= key(right[j]):
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    while i < len(left):
        result.append(left[i]); i += 1
    while j < len(right):
        result.append(right[j]); j += 1
    return result

# ══════════════════════════════════════════════════════════════════════════════
#  Quick Sort  (median-of-three Lomuto partition, in-place)
# ══════════════════════════════════════════════════════════════════════════════
def quick_sort(arr: list, key=None) -> list:
    if key is None:
        key = lambda x: x
    arr_copy = list(arr)
    _qs(arr_copy, 0, len(arr_copy) - 1, key)
    return arr_copy

def _median_of_three_idx(arr: list, low: int, high: int, key) -> int:
    mid = (low + high) // 2
    # Sort the three candidates
    if key(arr[low]) > key(arr[mid]):
        arr[low], arr[mid] = arr[mid], arr[low]
    if key(arr[low]) > key(arr[high]):
        arr[low], arr[high] = arr[high], arr[low]
    if key(arr[mid]) > key(arr[high]):
        arr[mid], arr[high] = arr[high], arr[mid]
    # arr[low] ≤ arr[mid] ≤ arr[high]; median is arr[mid]
    return mid

def _partition(arr: list, low: int, high: int, key) -> int:
    pivot_idx = _median_of_three_idx(arr, low, high, key)
    # Move pivot to the end
    arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]
    pivot = key(arr[high])
    i = low - 1
    for j in range(low, high):
        if key(arr[j]) <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    # Restore pivot to its correct sorted position
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

def _qs(arr: list, low: int, high: int, key):
    """Recursive quick-sort driver."""
    if low >= high:
        return
    p = _partition(arr, low, high, key)
    _qs(arr, low, p - 1, key)
    _qs(arr, p + 1, high, key)

# ══════════════════════════════════════════════════════════════════════════════
#  Dataset generation  (integrated with Module 1 T values)
# ══════════════════════════════════════════════════════════════════════════════
def generate_dataset(n: int, condition: str, t_pool: list, seed: int = 42) -> list:
    rng = random.Random(seed)
    if not t_pool:
        # Fallback if graph has no reachable pairs
        t_pool = [float(x) for x in range(1, 61)]

    # Sample n T values from the pool (with replacement)
    data = [rng.choice(t_pool) for _ in range(n)]
    if condition == "random":
        rng.shuffle(data)
    elif condition == "nearly_sorted":
        data = merge_sort(data)          # start sorted
        num_swaps = max(1, n // 10)      # displace ≤ 10 %
        for _ in range(num_swaps):
            i = rng.randint(0, n - 1)
            j = rng.randint(0, n - 1)
            data[i], data[j] = data[j], data[i]
    elif condition == "reversed":
        data = merge_sort(data)[::-1]    # descending
    else:
        raise ValueError(f"Unknown condition '{condition}'. "
                         f"Choose from: random, nearly_sorted, reversed.")
    return data

def _is_sorted(arr: list, key) -> bool:
    """Verification helper – returns True iff arr is non-decreasing by key."""
    for i in range(len(arr) - 1):
        if key(arr[i]) > key(arr[i + 1]):
            return False
    return True

# ══════════════════════════════════════════════════════════════════════════════
#  Benchmark
# ══════════════════════════════════════════════════════════════════════════════
def benchmark(t_pool: list,
              sizes:      list = None,
              conditions: list = None,
              seed:       int  = 42,
              repeats:    int  = 3) -> list:
    if sizes is None:
        sizes = [100, 500, 1000]
    if conditions is None:
        conditions = ["random", "nearly_sorted", "reversed"]
    key_fn = lambda x: x    # sort by T directly (floats)
    results = []
    for n in sizes:
        for cond in conditions:
            data = generate_dataset(n, cond, t_pool, seed)

            # ── Merge sort ────────────────────────────────────────────────
            ms_best = float("inf")
            for _ in range(repeats):
                t0     = time.perf_counter()
                ms_out = merge_sort(data, key=key_fn)
                ms_best = min(ms_best, time.perf_counter() - t0)

            # ── Quick sort ────────────────────────────────────────────────
            qs_best = float("inf")
            for _ in range(repeats):
                t0     = time.perf_counter()
                qs_out = quick_sort(data, key=key_fn)
                qs_best = min(qs_best, time.perf_counter() - t0)

            # ── Correctness verification ──────────────────────────────────
            ms_ok = _is_sorted(ms_out, key_fn)
            qs_ok = _is_sorted(qs_out, key_fn)
            assert ms_ok, f"Merge sort FAILED for n={n}, cond={cond}"
            assert qs_ok, f"Quick sort FAILED for n={n}, cond={cond}"
            results.append({
                "n":         n,
                "condition": cond,
                "ms_ms":     ms_best * 1000,    # convert to milliseconds
                "qs_ms":     qs_best * 1000,
                "ms_ok":     ms_ok,
                "qs_ok":     qs_ok,
            })
    return results

def print_benchmark_table(results: list):
    """Pretty-print benchmark results as a table."""
    print("\n" + "═" * 72)
    print("  MODULE 4 – Benchmark Results")
    print("  (best-of-3 runs; times in milliseconds; sorted by T ascending)")
    print("═" * 72)
    print(f"  {'n':>6}  {'Condition':<15}  "
          f"{'Merge Sort (ms)':>15}  {'Quick Sort (ms)':>15}  "
          f"{'Faster':>8}")
    print("  " + "─" * 68)
    for r in results:
        ms   = r["ms_ms"]
        qs   = r["qs_ms"]
        faster = "MergeSort" if ms < qs else ("QuickSort" if qs < ms else "Tie")
        print(f"  {r['n']:>6}  {r['condition']:<15}  "
              f"{ms:>15.4f}  {qs:>15.4f}  {faster:>8}")
    print()