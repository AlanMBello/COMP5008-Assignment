# ══════════════════════════════════════════════════════════════════════════════
#  Constants
# ══════════════════════════════════════════════════════════════════════════════
TABLE_SIZE      = 97      # prime, supports ~67 active records at LF < 0.7
LOAD_THRESHOLD  = 0.7     # warn (and optionally resize) above this
_DELETED        = object() # unique sentinel for tombstone slots

# ══════════════════════════════════════════════════════════════════════════════
#  Record types
# ══════════════════════════════════════════════════════════════════════════════
class PassengerRecord:
    TIER_LABELS = {1: "Platinum", 2: "Gold", 3: "Silver",
                   4: "Bronze",   5: "Standard"}

    def __init__(self, passenger_id: int, name: str,
                 pickup_location: str, membership_tier: int, phone: str = ""):
        # ── Input validation ──────────────────────────────────────────────────
        if not isinstance(passenger_id, int) or passenger_id <= 0:
            raise ValueError(
                f"PassengerID must be a positive integer (got {passenger_id!r}).")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name must be a non-empty string.")
        if not isinstance(membership_tier, int) or not (1 <= membership_tier <= 5):
            raise ValueError(
                f"MembershipTier must be 1–5 (got {membership_tier!r}).")
        self.passenger_id    = passenger_id
        self.name            = name.strip()
        self.pickup_location = pickup_location
        self.membership_tier = membership_tier
        self.phone           = phone
    @property
    def record_id(self) -> int:
        return self.passenger_id
    
    def __str__(self):
        tier = self.TIER_LABELS[self.membership_tier]
        return (f"Passenger[ID={self.passenger_id:>4}, "
                f"Name={self.name:<18}, "
                f"Location={self.pickup_location:<15}, "
                f"Tier={self.membership_tier}({tier})]")

class DriverRecord:
    VALID_STATUSES = {"Available", "Busy", "Offline"}
    def __init__(self, driver_id: int, name: str,
                 current_location: str, availability_status: str,
                 rating: float = 5.0):
        
        # ── Input validation ──────────────────────────────────────────────────
        if not isinstance(driver_id, int) or driver_id <= 0:
            raise ValueError(
                f"DriverID must be a positive integer (got {driver_id!r}).")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name must be a non-empty string.")
        if availability_status not in self.VALID_STATUSES:
            raise ValueError(
                f"AvailabilityStatus must be one of {sorted(self.VALID_STATUSES)} "
                f"(got {availability_status!r}).")
        if not (1.0 <= rating <= 5.0):
            raise ValueError(f"Rating must be 1.0–5.0 (got {rating}).")
        self.driver_id           = driver_id
        self.name                = name.strip()
        self.current_location    = current_location
        self.availability_status = availability_status
        self.rating              = rating
    @property
    def record_id(self) -> int:
        return self.driver_id

    def __str__(self):
        return (f"Driver  [ID={self.driver_id:>4}, "
                f"Name={self.name:<18}, "
                f"Location={self.current_location:<15}, "
                f"Status={self.availability_status:<10}, "
                f"Rating={self.rating:.1f}]")

# ══════════════════════════════════════════════════════════════════════════════
#  Hash Table
# ══════════════════════════════════════════════════════════════════════════════
class HashTable:
    def __init__(self, size: int = TABLE_SIZE):
        self._size          = size
        self._table         = [None] * size   # None | _DELETED | record
        self._active        = 0                # live records
        self._total_inserts = 0                # cumulative, for LF tracking
        self._last_probe_count = 0             # probes used in last search (O(1) evidence)

    # ── hash & probe helpers ──────────────────────────────────────────────────
    def _h(self, key: int) -> int:
        return key % self._size

    def _probe_for_insert(self, key: int) -> int:
        h = self._h(key)
        for i in range(self._size):
            idx = (h + i) % self._size
            if self._table[idx] is None or self._table[idx] is _DELETED:
                return idx
        return -1

    def _probe_for_search(self, key: int) -> int:
        h = self._h(key)
        for i in range(self._size):
            idx = (h + i) % self._size
            slot = self._table[idx]
            if slot is None:
                self._last_probe_count = i + 1
                return -1                    # definitive miss
            if slot is not _DELETED and slot.record_id == key:
                self._last_probe_count = i + 1
                return idx
        self._last_probe_count = self._size
        return -1

    # ── properties ────────────────────────────────────────────────────────────
    @property
    def load_factor(self) -> float:
        return self._active / self._size

    @property
    def size(self) -> int:
        return self._size

    # ── core operations ───────────────────────────────────────────────────────
    def insert(self, record, verbose: bool = True) -> bool:
        key = record.record_id

        # ── Duplicate check ────────────────────────────────────────────────
        if self._probe_for_search(key) != -1:
            if verbose:
                print(f"  [INSERT REJECTED] ID={key} already exists. "
                      f"Use update() to modify.")
            return False

        # ── Load factor check ──────────────────────────────────────────────
        if self.load_factor >= LOAD_THRESHOLD and verbose:
            print(f"  [WARNING] Load factor {self.load_factor:.3f} ≥ "
                  f"{LOAD_THRESHOLD}. Consider resizing the table.")

        # ── Collision detection & reporting ────────────────────────────────
        h = self._h(key)
        if verbose and (self._table[h] is not None and
                        self._table[h] is not _DELETED):
            existing = self._table[h]
            print(f"  [COLLISION] h({key}) = h({existing.record_id}) = {h}. "
                  f"Linear probing from slot {h} …")
        slot = self._probe_for_insert(key)
        if slot == -1:
            if verbose:
                print(f"  [ERROR] Table full. Cannot insert ID={key}.")
            return False
        if verbose and slot != h and (self._table[h] is not None and
                                      self._table[h] is not _DELETED):
            print(f"  [COLLISION RESOLVED] ID={key} placed at slot {slot} "
                  f"(home slot {h} occupied).")
        self._table[slot]    = record
        self._active        += 1
        self._total_inserts += 1

        # ── Load factor log every 10 inserts ──────────────────────────────
        if verbose and self._total_inserts % 10 == 0:
            print(f"  [LOAD FACTOR] After {self._total_inserts} inserts: "
                  f"{self.load_factor:.3f}  "
                  f"({self._active}/{self._size} slots used)")
        return True

    def search(self, key: int, verbose: bool = True):
        if not isinstance(key, int):
            if verbose:
                print(f"  [SEARCH ERROR] Key must be int (got {type(key).__name__}).")
            return None
        idx = self._probe_for_search(key)
        if idx == -1:
            if verbose:
                print(f"  [SEARCH MISS] ID={key} – not found in table.")
            return None
        if verbose:
            print(f"  [SEARCH HIT]  Slot {idx:>3}: {self._table[idx]}  "
                  f"[{self._last_probe_count} probe(s) — O(1)]")
        return self._table[idx]

    def delete(self, key: int, verbose: bool = True) -> bool:
        if not isinstance(key, int):
            if verbose:
                print(f"  [DELETE ERROR] Key must be int.")
            return False
        idx = self._probe_for_search(key)
        if idx == -1:
            if verbose:
                print(f"  [DELETE MISS] ID={key} – not found. Nothing deleted.")
            return False
        record = self._table[idx]
        self._table[idx] = _DELETED          # tombstone
        self._active    -= 1
        if verbose:
            print(f"  [DELETE OK]   Slot {idx:>3}: {record}  → DELETED (tombstone set)")
        return True

    def update(self, key: int, verbose: bool = True, **kwargs) -> bool:
        idx = self._probe_for_search(key)
        if idx == -1:
            if verbose:
                print(f"  [UPDATE ERROR] ID={key} – not found.")
            return False
        record = self._table[idx]
        for field, value in kwargs.items():
            if hasattr(record, field):
                setattr(record, field, value)
            else:
                if verbose:
                    print(f"  [UPDATE WARN] Field '{field}' not found on record.")
        if verbose:
            print(f"  [UPDATE OK]   {record}")
        return True

    # ── bulk retrieval (used by Module 3 scheduler) ───────────────────────────
    def get_all_drivers(self) -> list:
        out = []
        for slot in self._table:
            if slot is not None and slot is not _DELETED:
                if isinstance(slot, DriverRecord):
                    out.append(slot)
        return out

    def get_all_passengers(self) -> list:
        out = []
        for slot in self._table:
            if slot is not None and slot is not _DELETED:
                if isinstance(slot, PassengerRecord):
                    out.append(slot)
        return out

    # ── diagnostics ───────────────────────────────────────────────────────────
    def display(self, show_empty: bool = False):
        print("\n--- Hash Table Contents ---")
        for i in range(self._size):
            slot = self._table[i]
            if slot is None:
                if show_empty:
                    print(f"  [{i:>3}] EMPTY")
            elif slot is _DELETED:
                if show_empty:
                    print(f"  [{i:>3}] DELETED (tombstone)")
            else:
                print(f"  [{i:>3}] {slot}")
        print(f"\n  Active records : {self._active}")
        print(f"  Load factor    : {self.load_factor:.3f}  "
              f"({self._active}/{self._size})\n")

    def performance_summary(self):
        filled    = sum(1 for s in self._table if s is not None and s is not _DELETED)
        tombstone = sum(1 for s in self._table if s is _DELETED)
        empty     = self._size - filled - tombstone
        print("\n--- Hash Table Performance Summary ---")
        print(f"  Table size        : {self._size}")
        print(f"  Active records    : {filled}")
        print(f"  Tombstone slots   : {tombstone}")
        print(f"  Empty slots       : {empty}")
        print(f"  Load factor       : {self.load_factor:.3f}")
        print(f"  Total inserts     : {self._total_inserts}")
        print()

    # ── optional resize ───────────────────────────────────────────────────────
    def resize(self, new_size: int):
        old_table = self._table
        self._size          = new_size
        self._table         = [None] * new_size
        self._active        = 0
        self._total_inserts = 0
        for slot in old_table:
            if slot is not None and slot is not _DELETED:
                self.insert(slot, verbose=False)
        print(f"  [RESIZE] Table rehashed to size {new_size}. "
              f"Load factor: {self.load_factor:.3f}")