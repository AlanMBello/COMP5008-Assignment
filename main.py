#main.py - ZipRide Dispatch System Integration
#Description:
# Integrates all four modules into a single runnable demo:
#        Module 1 – Graph-Based Route Planning
#        Module 2 – Hash-Based Passenger and Driver Lookup
#        Module 3 – Heap-Based Pickup Scheduling
#        Module 4 – Sorting Pickup Requests
# Usage:
#    python main.py
from module1_graph      import Graph
from module2_hashtable  import HashTable, PassengerRecord, DriverRecord
from module3_heap       import DispatchScheduler
from module4_sorting    import benchmark, print_benchmark_table, merge_sort, quick_sort

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION HEADER HELPER
# ══════════════════════════════════════════════════════════════════════════════
def section(title: str):
    print("\n\n" + "╔" + "═" * 66 + "╗")
    print(f"║  {title:<64}║")
    print("╚" + "═" * 66 + "╝")

# ══════════════════════════════════════════════════════════════════════════════
#  MODULE 1 – Graph construction and algorithms
# ══════════════════════════════════════════════════════════════════════════════
def build_graph() -> Graph:
    g = Graph()

    # ── Nodes ──────────────────────────────────────────────────────────────────
    for name in ["CBD", "Airport", "University", "SuburbNorth", "SuburbSouth",
                 "ShoppingMall", "Hospital", "IndustrialPark", "TechPark"]:
        g.add_node(name)

    # ── Edges ──────────────────────────────────────────────────────────────────
    edges = [
        ("CBD",           "Airport",        25),
        ("CBD",           "University",     10),
        ("CBD",           "ShoppingMall",    8),
        ("CBD",           "Hospital",       12),
        ("University",    "SuburbNorth",    15),
        ("SuburbNorth",   "ShoppingMall",   20),
        ("SuburbNorth",   "Airport",        35),
        ("ShoppingMall",  "SuburbSouth",    18),
        ("ShoppingMall",  "Hospital",       14),
        ("SuburbSouth",   "Hospital",       22),
        ("Hospital",      "IndustrialPark", 30),
        ("IndustrialPark","SuburbNorth",    25),
    ]
    for u, v, w in edges:
        g.add_edge(u, v, w)
    return g

def run_module1():
    section("MODULE 1 – Graph-Based Route Planning")

    g = build_graph()
    g.display()
    # BFS from CBD
    g.print_bfs("CBD")
    # DFS cycle detection from CBD
    g.print_dfs("CBD")
    # DFS from isolated node
    g.print_dfs("TechPark")
    # Dijkstra: various source–destination pairs
    pairs = [
        ("CBD",        "Airport"),
        ("CBD",        "IndustrialPark"),
        ("University", "SuburbSouth"),
        ("CBD",        "TechPark"),       # unreachable
    ]
    for src, dst in pairs:
        g.print_dijkstra(src, dst)
    print("  All-pairs shortest driving times (reachable pairs):")
    ap = g.all_pairs_times()
    for (u, v), d in sorted(ap.items()):
        print(f"    {u:<20} → {v:<20} : {d} min")
    return g

# ══════════════════════════════════════════════════════════════════════════════
#  MODULE 2 – Hash table: passengers and drivers
# ══════════════════════════════════════════════════════════════════════════════
def build_hash_tables():
    section("MODULE 2 – Hash-Based Passenger and Driver Lookup")

    # ── Passengers ─────────────────────────────────────────────────────────────
    passenger_data = [
        # (ID, Name, Location, Tier)
        (1001, "Alice Chen",      "CBD",            1),
        (1002, "Bob Smith",       "Airport",        2),
        (1003, "Carol Lee",       "University",     1),
        (1004, "David Kim",       "SuburbNorth",    3),
        (1005, "Emma Brown",      "ShoppingMall",   2),
        (1006, "Frank Wu",        "Hospital",       4),
        (1007, "Grace Liu",       "SuburbSouth",    1),
        (1008, "Henry Park",      "IndustrialPark", 5),
        (1009, "Iris Tang",       "CBD",            3),
        (1010, "Jack Ng",         "Airport",        2),
        (1011, "Kate Wilson",     "University",     4),
        (1012, "Leo Zhang",       "ShoppingMall",   1),
        (1013, "Mia Johnson",     "SuburbNorth",    5),
        (1014, "Noah Davis",      "Hospital",       2),
        (1015, "Olivia Martinez", "SuburbSouth",    3),
        (1016, "Peter Chen",      "CBD",            1),
        (1017, "Quinn Taylor",    "Airport",        4),
        (1018, "Rachel White",    "University",     2),
        (1019, "Sam Anderson",    "IndustrialPark", 5),
        (1020, "Tina Roberts",    "ShoppingMall",   3),
    ]
    print("\n--- Inserting 20 Passenger Records ---")
    ptable = HashTable()
    for pid, name, loc, tier in passenger_data:
        rec = PassengerRecord(pid, name, loc, tier)
        ptable.insert(rec)
   
    # ── Demonstrate collision: 1098 % 97 == 1001 % 97 == 31 ──────────────────
    print("\n--- Collision Demonstration (Passenger) ---")
    print(f"  h(1001) = 1001 % 97 = {1001 % 97}  (already inserted)")
    print(f"  h(1098) = 1098 % 97 = {1098 % 97}  (same slot → COLLISION)")
    collision_pax = PassengerRecord(1098, "Zara Collision", "CBD", 2)
    ptable.insert(collision_pax)
   
    # ── Search demos ─────────────────────────────────────────────────────────
    print("\n--- Search Operations (Passengers) ---")
    ptable.search(1001)                     # hit – Platinum, CBD
    ptable.search(1007)                     # hit – Platinum, SuburbSouth
    ptable.search(1098)                     # hit – collision record
    ptable.search(9999)                     # miss
   
    # ── Delete demo ──────────────────────────────────────────────────────────
    print("\n--- Delete Operation ---")
    ptable.delete(1098)
    ptable.search(1098)                     # should now be a miss
   
    # ── Drivers ──────────────────────────────────────────────────────────────
    driver_data = [
        # (ID, Name, Location, Status)
        (2001, "Driver Alex",   "CBD",            "Available"),
        (2002, "Driver Ben",    "Airport",        "Available"),
        (2003, "Driver Cass",   "University",     "Busy"),
        (2004, "Driver Dave",   "SuburbNorth",    "Available"),
        (2005, "Driver Eva",    "ShoppingMall",   "Offline"),
        (2006, "Driver Felix",  "Hospital",       "Available"),
        (2007, "Driver Gina",   "SuburbSouth",    "Available"),
        (2008, "Driver Hugo",   "IndustrialPark", "Busy"),
        (2009, "Driver Iris",   "CBD",            "Available"),
        (2010, "Driver Jake",   "Airport",        "Offline"),
        (2011, "Driver Kim",    "University",     "Available"),
        (2012, "Driver Leo",    "SuburbNorth",    "Busy"),
        (2013, "Driver Mia",    "ShoppingMall",   "Available"),
        (2014, "Driver Nate",   "Hospital",       "Available"),
        (2015, "Driver Olive",  "SuburbSouth",    "Offline"),
        (2016, "Driver Pete",   "CBD",            "Available"),
        (2017, "Driver Quin",   "Airport",        "Available"),
        (2018, "Driver Rosa",   "University",     "Available"),
        (2019, "Driver Sam",    "IndustrialPark", "Available"),
        (2020, "Driver Tara",   "ShoppingMall",   "Available"),
    ]
    print("\n--- Inserting 20 Driver Records ---")
    dtable = HashTable()
    for did, name, loc, status in driver_data:
        rec = DriverRecord(did, name, loc, status)
        dtable.insert(rec)
    
    # ── Driver collision: 2098 % 97 == 2001 % 97 == 61 ──────────────────────
    print("\n--- Collision Demonstration (Driver) ---")
    print(f"  h(2001) = 2001 % 97 = {2001 % 97}  (already inserted)")
    print(f"  h(2098) = 2098 % 97 = {2098 % 97}  (same slot → COLLISION)")
    collision_drv = DriverRecord(2098, "Driver Zed", "CBD", "Available")
    dtable.insert(collision_drv)
    dtable.delete(2098)                     # remove the demo record
    # ── Duplicate rejection ───────────────────────────────────────────────────
    print("\n--- Duplicate Rejection Demo ---")
    dup = PassengerRecord(1001, "Duplicate Alice", "CBD", 1)
    ptable.insert(dup)
   
    # ── Invalid input handling ────────────────────────────────────────────────
    print("\n--- Invalid Input Demos ---")
    try:
        bad = PassengerRecord(-5, "Bad Guy", "CBD", 6)
    except ValueError as e:
        print(f"  [CAUGHT] PassengerRecord ValueError: {e}")
    try:
        bad2 = DriverRecord(9999, "Bad Driver", "Nowhere", "Flying")
    except ValueError as e:
        print(f"  [CAUGHT] DriverRecord ValueError: {e}")
    # ── Performance summary ───────────────────────────────────────────────────
    ptable.performance_summary()
    dtable.performance_summary()
    return ptable, dtable

# ══════════════════════════════════════════════════════════════════════════════
#  MODULE 3 – Heap-Based Pickup Scheduling
# ══════════════════════════════════════════════════════════════════════════════
def run_module3(graph, ptable, dtable):
    section("MODULE 3 – Heap-Based Pickup Scheduling")
    scheduler = DispatchScheduler(graph, ptable, dtable)
    # ── 10 insert operations ─────────────────────────────────────────────────
    # Passengers chosen for variety in tier and location:
    #   1016 Platinum CBD, 1007 Platinum SuburbSouth, 1003 Platinum University,
    #   1012 Platinum ShoppingMall, 1002 Gold Airport,
    #   1010 Gold Airport, 1005 Gold ShoppingMall,
    #   1004 Silver SuburbNorth, 1009 Silver CBD,
    #   1006 Bronze Hospital
    insert_order = [1016, 1007, 1003, 1012, 1002,
                    1010, 1005, 1004, 1009, 1006]
    print("\n─── Submitting 10 pickup requests ───")
    for pid in insert_order:
        scheduler.submit_request(pid)
    print(f"\n\n  Heap size after 10 inserts: {scheduler.heap.size()}")
    scheduler.heap.peek()

    # ── 5 extract operations ─────────────────────────────────────────────────
    print("\n─── Dispatching 5 requests (highest priority first) ───")
    for _ in range(5):
        scheduler.dispatch_next()
    print(f"\n  Heap size after 5 extractions: {scheduler.heap.size()}")

    # ── Edge case: MembershipTier change → reinsert with new priority ─────────
    print("\n─── Edge case: MembershipTier change (reinsert) ───")
    print("  Upgrading Request 5 (Bob Smith, Gold Tier 2) → Platinum (Tier 1)")
    scheduler.heap.update_tier(5, 1)

    # ── Edge-case: no available drivers (all busy / offline) ─────────────────
    # Temporarily mark remaining available drivers offline for demo
    print("\n─── Edge case: no available drivers ───")
    avail = [d for d in dtable.get_all_drivers()
             if d.availability_status == "Available"]
    for d in avail:
        dtable.update(d.driver_id, verbose=False, availability_status="Offline")
    scheduler.submit_request(1008)   # should be queued without driver

    # Restore drivers
    for d in avail:
        dtable.update(d.driver_id, verbose=False, availability_status="Available")

    # ── Edge case: passenger not found ───────────────────────────────────────
    print("\n─── Edge case: passenger not found ───")
    scheduler.submit_request(9999)

    # ── Dispatch log ─────────────────────────────────────────────────────────
    scheduler.print_dispatch_log()
    return scheduler

# ══════════════════════════════════════════════════════════════════════════════
#  MODULE 4 – Sorting
# ══════════════════════════════════════════════════════════════════════════════
def run_module4(graph):
    section("MODULE 4 – Sorting Pickup Requests by EstimatedPickupTime")
    # ── Build T-value pool from Module 1 Dijkstra results ─────────────────────
    ap       = graph.all_pairs_times()
    t_values = list(ap.values())
    print(f"\n  T-value pool derived from all-pairs Dijkstra (Module 1):")
    print(f"  {len(t_values)} reachable pairs | "
          f"min={min(t_values):.1f} min | max={max(t_values):.1f} min | "
          f"unique={len(set(t_values))}")

    # ── Small worked example: sort 10 T values ────────────────────────────────
    import random
    rng     = random.Random(42)
    sample  = [rng.choice(t_values) for _ in range(10)]
    print(f"\n  Sample 10 T values (unsorted): {sample}")
    ms_demo = merge_sort(sample)
    qs_demo = quick_sort(sample)
    print(f"  After merge sort             : {ms_demo}")
    print(f"  After quick sort             : {qs_demo}")

    # ── Full benchmark ────────────────────────────────────────────────────────
    print("\n  Running benchmark (3 repeats per configuration)…")
    results = benchmark(t_values, sizes=[100, 500, 1000],
                        conditions=["random", "nearly_sorted", "reversed"],
                        repeats=3)
    print_benchmark_table(results)

    # ── Analysis ─────────────────────────────────────────────────────────────
    print("  Analysis")
    print("  ────────")
    print("  • Merge Sort is stable and guarantees O(n log n) regardless of")
    print("    input order.  On nearly-sorted data it performs similarly to")
    print("    random because it always divides at the midpoint.")
    print()
    print("  • Quick Sort (median-of-three) outperforms merge sort on random")
    print("    and nearly-sorted data due to better cache locality and lower")
    print("    constant factors.  On reversed data it is also fast because the")
    print("    median-of-three pivot avoids the degenerate O(n²) case that")
    print("    naive last-element pivot selection would produce.")
    print()
    print("  • For end-of-day reporting on ZipRide, Merge Sort is preferred")
    print("    when stability is required (equal T values retain submission")
    print("    order).  Quick Sort is preferred when raw throughput matters.")
    print()

# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║       ZIPRIDE DISPATCH SYSTEM – COMP5008 Final Assignment        ║")
    print("║            Curtin University  │  Semester 1, 2026               ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    # Module 1
    graph = run_module1()

    # Module 2
    ptable, dtable = build_hash_tables()

    # Module 3 (uses graph, ptable, dtable)
    scheduler = run_module3(graph, ptable, dtable)

    # Module 4 (uses graph for T-value pool)
    run_module4(graph)
    print("\n" + "═" * 68)
    print("  All modules completed successfully.")
    print("═" * 68 + "\n")
if __name__ == "__main__":
    main()