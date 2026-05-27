# ZipRide Dispatch System – COMP5008 Final Assignment
**Curtin University | Semester 1, 2026**

---

## System Overview

A backend dispatch system for a ride-hailing service, demonstrating four core data structures and algorithms working as an integrated pipeline:

| Module | File | Topic |
|--------|------|-------|
| 1 | `module1_graph.py` | Weighted undirected graph; BFS, DFS, Dijkstra |
| 2 | `module2_hashtable.py` | Open-addressing hash table; passenger & driver records |
| 3 | `module3_heap.py` | Array-based max-heap; priority dispatch scheduler |
| 4 | `module4_sorting.py` | Merge sort & quick sort; benchmarking |

---

## Requirements

- **Python 3.8 or higher** (no third-party libraries required)
- Standard library only

---

## Running the System

### Full integrated demo (all four modules)

```bash
cd zipride
python main.py
```

### Individual modules (for testing each in isolation)

```bash
# Module 1 – Graph
python -c "
from module1_graph import Graph
g = Graph()
g.add_node('A'); g.add_node('B'); g.add_node('C')
g.add_edge('A','B',5); g.add_edge('B','C',3)
g.display()
g.print_bfs('A')
g.print_dijkstra('A','C')
"

# Module 2 – Hash Table
python -c "
from module2_hashtable import HashTable, PassengerRecord
t = HashTable()
t.insert(PassengerRecord(1001,'Alice','CBD',1))
t.search(1001)
t.delete(1001)
t.search(1001)
"

# Module 3 – Heap only (without dispatcher)
python -c "
from module3_heap import MaxHeap, PickupRequest
h = MaxHeap()
h.insert(PickupRequest(1,101,'Alice','CBD',1,2001,'Bob',8))
h.insert(PickupRequest(2,102,'Carol','Airport',3,2002,'Dave',25))
h.peek()
h.extract_priority()
"

# Module 4 – Sorting
python -c "
from module4_sorting import merge_sort, quick_sort
data = [30, 8, 25, 12, 18]
print('Merge sort:', merge_sort(data))
print('Quick sort:', quick_sort(data))
"
```

---

## File Structure

```
zipride/
├── module1_graph.py        # Graph, BFS, DFS, Dijkstra
├── module2_hashtable.py    # PassengerRecord, DriverRecord, HashTable
├── module3_heap.py         # PickupRequest, MaxHeap, DispatchScheduler
├── module4_sorting.py      # merge_sort, quick_sort, benchmark
├── main.py                 # Full system integration demo
└── README.md               # This file
```

---

## Test City Road Network

```
Nodes (9):  CBD, Airport, University, SuburbNorth, SuburbSouth,
            ShoppingMall, Hospital, IndustrialPark, TechPark (isolated)

Edges (12, driving time in minutes):
  CBD ↔ Airport        25    CBD ↔ University     10
  CBD ↔ ShoppingMall    8    CBD ↔ Hospital       12
  University ↔ SuburbNorth      15
  SuburbNorth ↔ ShoppingMall    20    SuburbNorth ↔ Airport  35
  ShoppingMall ↔ SuburbSouth    18    ShoppingMall ↔ Hospital 14
  SuburbSouth ↔ Hospital        22
  Hospital ↔ IndustrialPark     30    IndustrialPark ↔ SuburbNorth 25
```

---

## Sample Output (truncated)

```
MODULE 1 – BFS from 'CBD'
  Level 0: CBD
  Level 1: Airport, University, ShoppingMall, Hospital
  Level 2: SuburbNorth, SuburbSouth, IndustrialPark
  ⚠  Unreachable (isolated): TechPark

MODULE 1 – DFS cycle detection from 'CBD'
  Cycle DETECTED → CBD → University → SuburbNorth → Airport → CBD

MODULE 1 – Dijkstra 'CBD' → 'IndustrialPark'
  Shortest time: 42 min  |  Path: CBD → Hospital → IndustrialPark

MODULE 2 – Collision demonstration
  h(1001) = h(1098) = 31  →  COLLISION → probed to slot 51

MODULE 4 – Benchmark (best of 3 runs)
  n=1000 random:    Merge Sort 1.64 ms | Quick Sort 3.12 ms
```

---

## Key Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Graph representation | Adjacency list | O(V+E) space vs O(V²) for matrix; city road networks are sparse |
| Hash collision strategy | Open addressing (linear probing) | Cache-friendly; avoids pointer overhead of chaining |
| Hash table size | 97 (prime) | Prime reduces clustering in modulo hash functions |
| Heap type | Max-heap | Root always holds highest-priority request; natural for dispatch |
| Merge sort variant | Top-down (recursive) | Clean implementation; stable sort preserves submission order |
| Quick sort pivot | Median-of-three | Avoids O(n²) on sorted/reversed input |

---

## Academic Integrity

All code is original work. No external data-structure libraries are used for core logic:
- No `heapq`, `collections.deque`, `dict` (for hash table), `sorted()`, `list.sort()` in core modules.
- Module-to-module integration follows the assignment specification.

**References:** Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to Algorithms* (4th ed.). MIT Press.