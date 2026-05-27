# ══════════════════════════════════════════════════════════════════════════════
#  Helper – FIFO Queue  (no collections.deque)
# ══════════════════════════════════════════════════════════════════════════════
class _Queue:
    def __init__(self):
        self._buf  = []
        self._head = 0   # index of the logical front

    def enqueue(self, item):
        self._buf.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Dequeue from empty queue.")
        item = self._buf[self._head]
        self._head += 1
        # Compact once half the buffer has been consumed
        if self._head * 2 >= len(self._buf):
            self._buf  = self._buf[self._head:]
            self._head = 0
        return item
    
    def is_empty(self):
        return self._head >= len(self._buf)

# ══════════════════════════════════════════════════════════════════════════════
#  Graph
# ══════════════════════════════════════════════════════════════════════════════
class Graph:
    def __init__(self):
        self.nodes = []   # list[str]
        self.adj   = []   # list[ list[(int, int)] ]

    # ── internal helpers ──────────────────────────────────────────────────────
    def _index_of(self, name: str) -> int:
        """Linear scan; returns -1 if name is absent."""
        for i in range(len(self.nodes)):
            if self.nodes[i] == name:
                return i
        return -1
    def get_index(self, name: str) -> int:
        """Public lookup; raises ValueError if name is absent."""
        idx = self._index_of(name)
        if idx == -1:
            raise ValueError(f"Node '{name}' not found in graph.")
        return idx
    def get_nodes(self) -> list:
        return list(self.nodes)
    
    # ── graph construction ────────────────────────────────────────────────────
    def add_node(self, name: str):
        if not isinstance(name, str) or not name:
            raise TypeError("Node name must be a non-empty string.")
        if self._index_of(name) == -1:
            self.nodes.append(name)
            self.adj.append([])

    def add_edge(self, u: str, v: str, weight: int):
        if weight <= 0:
            raise ValueError(f"Edge weight must be positive (got {weight}).")
        ui = self.get_index(u)
        vi = self.get_index(v)
        self.adj[ui].append((vi, weight))
        self.adj[vi].append((ui, weight))

    # ── display ───────────────────────────────────────────────────────────────
    def display(self):
        """Pretty-print the adjacency list."""
        print("\n" + "═" * 62)
        print("  MODULE 1 – City Road Network (Adjacency List)")
        print("═" * 62)
        for i, name in enumerate(self.nodes):
            if self.adj[i]:
                nbrs = ", ".join(
                    f"{self.nodes[j]} ({w} min)"
                    for j, w in sorted(self.adj[i], key=lambda x: x[1])
                )
            else:
                nbrs = "(isolated – no roads)"
            print(f"  {name:<22} → {nbrs}")
        print()

    # ── BFS ───────────────────────────────────────────────────────────────────
    def bfs(self, source: str):
        src = self.get_index(source)
        n   = len(self.nodes)
        visited = [False] * n
        depth   = [-1]    * n
        visited[src] = True
        depth[src]   = 0
        queue = _Queue()
        queue.enqueue(src)
        levels = {}
        while not queue.is_empty():
            u  = queue.dequeue()
            d  = depth[u]
            if d not in levels:
                levels[d] = []
            levels[d].append(self.nodes[u])
            for v, _ in self.adj[u]:
                if not visited[v]:
                    visited[v] = True
                    depth[v]   = d + 1
                    queue.enqueue(v)
        return levels, visited

    def print_bfs(self, source: str):
        print(f"\n--- BFS traversal from '{source}' ---")
        levels, visited = self.bfs(source)
        for d in sorted(levels):
            print(f"  Level {d}: {', '.join(levels[d])}")
        unreachable = [
            self.nodes[i] for i in range(len(self.nodes)) if not visited[i]
        ]
        if unreachable:
            print(f"  ⚠  Unreachable (isolated): {', '.join(unreachable)}")
        print()

    # ── DFS / cycle detection ─────────────────────────────────────────────────
    def dfs_cycle(self, source: str):
        src = self.get_index(source)
        n   = len(self.nodes)
        visited = [False] * n
        parent  = [-1]    * n
        state   = {"found": False, "cycle": []}

        def _dfs(u: int):
            visited[u] = True
            for v, _ in self.adj[u]:
                if state["found"]:
                    return
                if not visited[v]:
                    parent[v] = u
                    _dfs(v)
                elif v != parent[u]:          # back-edge → cycle detected
                    state["found"] = True
                    # Reconstruct cycle: trace from u back to v via parents
                    path = [self.nodes[v], self.nodes[u]]
                    cur  = parent[u]
                    while cur != -1 and cur != v:
                        path.append(self.nodes[cur])
                        cur = parent[cur]
                    if cur == v:
                        path.append(self.nodes[v])
                    state["cycle"] = path
        _dfs(src)
        return state["found"], state["cycle"]

    def print_dfs(self, source: str):
        print(f"\n--- DFS cycle detection from '{source}' ---")
        found, cycle = self.dfs_cycle(source)
        if found:
            print(f"  Cycle DETECTED  →  {' → '.join(cycle)}")
        else:
            print(f"  No cycle found in the component of '{source}'.")
        print()

    # ── Dijkstra ──────────────────────────────────────────────────────────────
    def dijkstra(self, source: str, destination: str = None):

        src = self.get_index(source)
        n   = len(self.nodes)
        INF = float("inf")
        dist    = [INF]   * n   # tentative shortest distances
        prev    = [-1]    * n   # predecessor array for path reconstruction
        visited = [False] * n
        dist[src] = 0
        for _ in range(n):
            # ── Extract-Min: scan all unvisited nodes ──────────────────────
            u, min_d = -1, INF
            for i in range(n):
                if not visited[i] and dist[i] < min_d:
                    u, min_d = i, dist[i]
            if u == -1:
                break               # all remaining nodes unreachable
            visited[u] = True

            # ── Relax edges from u ────────────────────────────────────────
            for v, w in self.adj[u]:
                if not visited[v] and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    prev[v] = u

        # ── Return all distances (for Module 4 integration) ────────────────
        if destination is None:
            return {self.nodes[i]: dist[i] for i in range(n)}, []

        # ── Single-destination: reconstruct path ───────────────────────────
        dst = self.get_index(destination)
        if dist[dst] == INF:
            return INF, []
        path, cur = [], dst
        while cur != -1:
            path.append(self.nodes[cur])
            cur = prev[cur]
        path.reverse()
        return dist[dst], path

    def print_dijkstra(self, source: str, destination: str):
        print(f"\n--- Dijkstra: '{source}' → '{destination}' ---")
        d, path = self.dijkstra(source, destination)
        if d == float("inf"):
            print(f"  No path – '{destination}' is unreachable from '{source}'.")
        else:
            print(f"  Shortest driving time : {d} min")
            print(f"  Route                 : {' → '.join(path)}")
        print()

    # ── Utility: all-pairs times (used by Module 4) ───────────────────────────
    def all_pairs_times(self) -> dict:
        result = {}
        for src in self.nodes:
            dist_map, _ = self.dijkstra(src, destination=None)
            for dst, d in dist_map.items():
                if dst != src and d != float("inf"):
                    result[(src, dst)] = d
        return result