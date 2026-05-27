from module1_graph      import Graph
from module2_hashtable  import HashTable, PassengerRecord, DriverRecord
# ══════════════════════════════════════════════════════════════════════════════
#  PickupRequest
# ══════════════════════════════════════════════════════════════════════════════
class PickupRequest:
    SAME_LOCATION_TIME = 0.5   # minutes – driver already at pickup location

    def __init__(self,
                 request_id:          int,
                 passenger_id:        int,
                 passenger_name:      str,
                 pickup_location:     str,
                 membership_tier:     int,
                 assigned_driver_id:  int   = None,
                 assigned_driver_name: str  = None,
                 estimated_pickup_time: float = None):

        # ── Validation ────────────────────────────────────────────────────────
        if not isinstance(request_id, int) or request_id <= 0:
            raise ValueError("request_id must be a positive integer.")
        if not isinstance(passenger_id, int) or passenger_id <= 0:
            raise ValueError("passenger_id must be a positive integer.")
        if not isinstance(membership_tier, int) or not (1 <= membership_tier <= 5):
            raise ValueError("membership_tier must be between 1 and 5.")
        if estimated_pickup_time is not None and estimated_pickup_time < 0:
            raise ValueError("estimated_pickup_time cannot be negative.")
        self.request_id           = request_id
        self.passenger_id         = passenger_id
        self.passenger_name       = passenger_name
        self.pickup_location      = pickup_location
        self.membership_tier      = membership_tier
        self.assigned_driver_id   = assigned_driver_id
        self.assigned_driver_name = assigned_driver_name
        self.estimated_pickup_time = estimated_pickup_time
        self.priority             = self._compute_priority()

    def _compute_priority(self) -> float:
        if self.estimated_pickup_time is None:
            return float("-inf")
        t = max(self.estimated_pickup_time, self.SAME_LOCATION_TIME)
        return (6 - self.membership_tier) + (1000.0 / t)

    def __str__(self):
        tier_label = {1:"Platinum",2:"Gold",3:"Silver",4:"Bronze",5:"Standard"}
        t_str = (f"{self.estimated_pickup_time} min"
                 if self.estimated_pickup_time is not None else "N/A")
        return (f"Request[ID={self.request_id:>3}, "
                f"Pax={self.passenger_name:<15}(T{self.membership_tier}/"
                f"{tier_label[self.membership_tier]}), "
                f"Loc={self.pickup_location:<15}, "
                f"Driver={str(self.assigned_driver_id):<5}, "
                f"ETA={t_str:<8}, "
                f"Priority={self.priority:>8.2f}]")

# ══════════════════════════════════════════════════════════════════════════════
#  MaxHeap
# ══════════════════════════════════════════════════════════════════════════════
class MaxHeap:
    def __init__(self):
        self._data = []     # heap array; index 0 = root (highest priority)

    # ── index helpers ─────────────────────────────────────────────────────────
    @staticmethod
    def _parent(i): return (i - 1) // 2

    @staticmethod
    def _left(i): return 2 * i + 1

    @staticmethod
    def _right(i): return 2 * i + 2

    def size(self) -> int:  return len(self._data)
    def is_empty(self) -> bool: return len(self._data) == 0

    def _swap(self, i: int, j: int):
        self._data[i], self._data[j] = self._data[j], self._data[i]

    # ── heap maintenance ──────────────────────────────────────────────────────
    def _percolate_up(self, i: int):
        while i > 0:
            p = self._parent(i)
            if self._data[i].priority > self._data[p].priority:
                self._swap(i, p)
                i = p
            else:
                break

    def _percolate_down(self, i: int):
        n = len(self._data)
        while True:
            largest = i
            l = self._left(i)
            r = self._right(i)
            if l < n and self._data[l].priority > self._data[largest].priority:
                largest = l
            if r < n and self._data[r].priority > self._data[largest].priority:
                largest = r
            if largest != i:
                self._swap(i, largest)
                i = largest
            else:
                break

    # ── public interface ──────────────────────────────────────────────────────
    def insert(self, request: PickupRequest):
        if not isinstance(request, PickupRequest):
            raise TypeError("Only PickupRequest objects may be inserted.")
        self._data.append(request)
        self._percolate_up(len(self._data) - 1)
        print(f"  ┌ INSERT → {request}")
        self._print_heap()

    def peek(self) -> PickupRequest:
        if self.is_empty():
            print("  [PEEK] Heap is empty.")
            return None
        top = self._data[0]
        print(f"  [PEEK] Highest priority: {top}")
        return top

    def extract_priority(self) -> PickupRequest:
        if self.is_empty():
            print("  [EXTRACT] Heap is empty – nothing to dispatch.")
            return None
        top = self._data[0]

        # Move last element to root, shrink array
        self._data[0] = self._data[-1]
        self._data.pop()
        if not self.is_empty():
            self._percolate_down(0)
        print(f"  └ EXTRACT (dispatched) → {top}")
        self._print_heap()
        return top

    def update_tier(self, request_id: int, new_tier: int):
        if not (1 <= new_tier <= 5):
            print(f"  [TIER UPDATE ERROR] new_tier must be 1–5 (got {new_tier}).")
            return False

        # Find the request by scanning the array
        idx = -1
        for i in range(len(self._data)):
            if self._data[i].request_id == request_id:
                idx = i
                break
        if idx == -1:
            print(f"  [TIER UPDATE MISS] Request ID={request_id} not in heap.")
            return False
        old_req = self._data[idx]
        old_tier = old_req.membership_tier
        old_priority = old_req.priority

        # Remove by swapping with last element and percolating
        self._data[idx] = self._data[-1]
        self._data.pop()
        if idx < len(self._data):
            self._percolate_down(idx)
            self._percolate_up(idx)

        # Rebuild request with updated tier
        new_req = PickupRequest(
            request_id=old_req.request_id,
            passenger_id=old_req.passenger_id,
            passenger_name=old_req.passenger_name,
            pickup_location=old_req.pickup_location,
            membership_tier=new_tier,
            assigned_driver_id=old_req.assigned_driver_id,
            assigned_driver_name=old_req.assigned_driver_name,
            estimated_pickup_time=old_req.estimated_pickup_time
        )
        print(f"  [TIER UPDATE] Request {request_id}: "
              f"Tier {old_tier} → {new_tier} | "
              f"Priority {old_priority:.2f} → {new_req.priority:.2f}")
        self.insert(new_req)
        return True

    def _print_heap(self):
        if self.is_empty():
            print("    Heap: [EMPTY]")
            return
        entries = " | ".join(
            f"R{r.request_id}(P={r.priority:.1f})" for r in self._data
        )
        print(f"    Heap [{self.size():>2} items]: {entries}")

# ══════════════════════════════════════════════════════════════════════════════
#  DispatchScheduler  (integration layer)
# ══════════════════════════════════════════════════════════════════════════════
class DispatchScheduler:
    def __init__(self,
                 graph:           Graph,
                 passenger_table: HashTable,
                 driver_table:    HashTable):
        self.graph           = graph
        self.passenger_table = passenger_table
        self.driver_table    = driver_table
        self.heap            = MaxHeap()
        self._req_counter    = 0
        self.dispatch_log    = []   # list[PickupRequest] – completed dispatches

    # ── submit ────────────────────────────────────────────────────────────────
    def submit_request(self, passenger_id: int) -> PickupRequest:
        print(f"\n{'─'*62}")
        print(f"  NEW REQUEST  │  Passenger ID = {passenger_id}")
        print(f"{'─'*62}")

        # ── Step 1: Retrieve passenger ────────────────────────────────────────
        passenger = self.passenger_table.search(passenger_id, verbose=False)
        if passenger is None:
            print(f"  [REJECTED] Passenger ID={passenger_id} not found.")
            return None
        if not isinstance(passenger, PassengerRecord):
            print(f"  [REJECTED] ID={passenger_id} is a driver record, not a passenger.")
            return None
        M   = passenger.membership_tier
        loc = passenger.pickup_location
        print(f"  Passenger : {passenger.name}  |  Tier {M}  |  Pickup → {loc}")

        # ── Step 2: Find available drivers ────────────────────────────────────
        all_drivers = self.driver_table.get_all_drivers()
        available   = [d for d in all_drivers
                       if d.availability_status == "Available"]
        if not available:
            print(f"  [QUEUED] No drivers available. Request added without driver.")
            self._req_counter += 1
            try:
                req = PickupRequest(
                    request_id=self._req_counter,
                    passenger_id=passenger_id,
                    passenger_name=passenger.name,
                    pickup_location=loc,
                    membership_tier=M)
            except ValueError as e:
                print(f"  [ERROR] {e}")
                return None
            self.heap.insert(req)
            return req

        # ── Step 3: Dijkstra to find nearest driver ───────────────────────────
        print(f"  Computing Dijkstra distances to '{loc}' for each available driver:")
        best_driver = None
        best_T      = float("inf")
        for driver in available:
            if driver.current_location == loc:
                T = PickupRequest.SAME_LOCATION_TIME
            else:
                T, _ = self.graph.dijkstra(driver.current_location, loc)
            T_display = f"{T} min" if T != float("inf") else "unreachable"
            print(f"    Driver {driver.driver_id:<4} ({driver.name:<14}) "
                  f"@ {driver.current_location:<15} → ETA = {T_display}")
            if T < best_T:
                best_T      = T
                best_driver = driver
        if best_driver is None or best_T == float("inf"):
            print(f"  [REJECTED] No driver can reach '{loc}'.")
            return None

        # ── Step 4: Compute priority ──────────────────────────────────────────
        T_eff     = max(best_T, PickupRequest.SAME_LOCATION_TIME)
        priority  = (6 - M) + (1000.0 / T_eff)
        print(f"\n  ✓ Best driver  : {best_driver.name} (ID={best_driver.driver_id})"
              f"  ETA={best_T} min")
        print(f"  Priority       : (6−{M}) + 1000/{T_eff} = {priority:.2f}")

        # ── Step 5: Mark driver busy ──────────────────────────────────────────
        self.driver_table.update(
            best_driver.driver_id, verbose=False,
            availability_status="Busy")

        # ── Step 6: Build request and insert into heap ────────────────────────
        self._req_counter += 1
        try:
            req = PickupRequest(
                request_id=self._req_counter,
                passenger_id=passenger_id,
                passenger_name=passenger.name,
                pickup_location=loc,
                membership_tier=M,
                assigned_driver_id=best_driver.driver_id,
                assigned_driver_name=best_driver.name,
                estimated_pickup_time=best_T)
        except ValueError as e:
            print(f"  [ERROR] {e}")
            return None
        self.heap.insert(req)
        return req

    # ── dispatch ──────────────────────────────────────────────────────────────
    def dispatch_next(self) -> PickupRequest:
        print(f"\n{'─'*62}")
        print(f"  DISPATCHING next request from heap …")
        print(f"{'─'*62}")
        req = self.heap.extract_priority()
        if req is None:
            return None
        self.dispatch_log.append(req)

        # Free the driver
        if req.assigned_driver_id is not None:
            self.driver_table.update(
                req.assigned_driver_id, verbose=False,
                availability_status="Available")
            print(f"  Driver {req.assigned_driver_id} ({req.assigned_driver_name}) "
                  f"→ status reset to Available.")
        return req

    def print_dispatch_log(self):
        print("\n═══════════════ DISPATCH LOG ═══════════════")
        if not self.dispatch_log:
            print("  (No requests dispatched yet.)")
            return
        for i, req in enumerate(self.dispatch_log, 1):
            print(f"  {i:>2}. {req}")
        print()