"""Intelligent Campus Resources Optimization System - DSA-II prototype (Review 2).
Trees (BST/AVL), Heap, Graph (adjacency list), Dynamic Programming, Backtracking + Branch and Bound.
A clash = same resource and overlapping half-open interval [start, end)."""
import random
from bisect import bisect_right
from collections import namedtuple

Resource = namedtuple("Resource", "id type capacity")
Request = namedtuple("Request", "id res start end priority")


def overlaps(a, b):
    return a.res == b.res and a.start < b.end and b.start < a.end


# ---------------------------------------------------------------- BST
class BST:
    class Node:
        __slots__ = ("r", "l", "rt")
        def __init__(self, r): self.r, self.l, self.rt = r, None, None

    def __init__(self): self.root = None

    def insert(self, r):
        if self.root is None:
            self.root = BST.Node(r); return
        x = self.root
        while True:
            if r.id == x.r.id: return
            if r.id < x.r.id:
                if x.l is None: x.l = BST.Node(r); return
                x = x.l
            else:
                if x.rt is None: x.rt = BST.Node(r); return
                x = x.rt

    def find(self, rid, counter=None):
        x = self.root
        while x:
            if counter is not None: counter[0] += 1
            if rid == x.r.id: return x.r
            x = x.l if rid < x.r.id else x.rt
        return None

    def height(self):  # iterative: a degenerate BST is as deep as n
        best, stack = 0, ([(self.root, 1)] if self.root else [])
        while stack:
            x, d = stack.pop(); best = max(best, d)
            if x.l: stack.append((x.l, d + 1))
            if x.rt: stack.append((x.rt, d + 1))
        return best


# ---------------------------------------------------------------- AVL
class AVL:
    class Node:
        __slots__ = ("r", "l", "rt", "h")
        def __init__(self, r): self.r, self.l, self.rt, self.h = r, None, None, 1

    def __init__(self): self.root, self.rotations = None, 0

    @staticmethod
    def H(x): return x.h if x else 0

    def _upd(self, x): x.h = 1 + max(self.H(x.l), self.H(x.rt))

    def _rot_r(self, y):
        x = y.l; y.l = x.rt; x.rt = y; self._upd(y); self._upd(x); self.rotations += 1; return x

    def _rot_l(self, x):
        y = x.rt; x.rt = y.l; y.l = x; self._upd(x); self._upd(y); self.rotations += 1; return y

    def _ins(self, x, r):
        if x is None: return AVL.Node(r)
        if r.id < x.r.id: x.l = self._ins(x.l, r)
        elif r.id > x.r.id: x.rt = self._ins(x.rt, r)
        else: return x
        self._upd(x)
        b = self.H(x.l) - self.H(x.rt)
        if b > 1:
            if r.id > x.l.r.id: x.l = self._rot_l(x.l)
            return self._rot_r(x)
        if b < -1:
            if r.id < x.rt.r.id: x.rt = self._rot_r(x.rt)
            return self._rot_l(x)
        return x

    def insert(self, r): self.root = self._ins(self.root, r)

    def find(self, rid, counter=None):
        x = self.root
        while x:
            if counter is not None: counter[0] += 1
            if rid == x.r.id: return x.r
            x = x.l if rid < x.r.id else x.rt
        return None

    def height(self): return self.H(self.root)

    def _bal(self, x):
        return x is None or (abs(self.H(x.l) - self.H(x.rt)) <= 1 and self._bal(x.l) and self._bal(x.rt))

    def is_balanced(self): return self._bal(self.root)

    def ids(self):
        out = []
        def go(x):
            if x: go(x.l); out.append(x.r.id); go(x.rt)
        go(self.root); return out


# ---------------------------------------------------------------- Priority queue (binary max-heap)
class RequestHeap:
    def __init__(self): self.a, self.swaps = [], 0

    @staticmethod
    def better(x, y):
        if x.priority != y.priority: return x.priority > y.priority
        if x.start != y.start: return x.start < y.start
        return x.id < y.id

    def push(self, r):
        a = self.a; a.append(r); i = len(a) - 1
        while i > 0:
            p = (i - 1) // 2
            if not self.better(a[i], a[p]): break
            a[i], a[p] = a[p], a[i]; self.swaps += 1; i = p

    def pop(self):
        a = self.a; top = a[0]; last = a.pop()
        if a:
            a[0] = last; i, n = 0, len(a)
            while True:
                l, r, b = 2 * i + 1, 2 * i + 2, i
                if l < n and self.better(a[l], a[b]): b = l
                if r < n and self.better(a[r], a[b]): b = r
                if b == i: break
                a[i], a[b] = a[b], a[i]; self.swaps += 1; i = b
        return top

    def empty(self): return not self.a


# ---------------------------------------------------------------- Conflict graph (adjacency list)
class ConflictGraph:
    def __init__(self, n):
        self.n, self.adj, self.checks, self.edges = n, [[] for _ in range(n)], 0, 0

    def add(self, u, v):
        self.adj[u].append(v); self.adj[v].append(u); self.edges += 1

    def normalise(self):
        for x in self.adj: x.sort()


def build_naive(q):
    """Baseline: compare every pair of requests, O(n^2)."""
    g = ConflictGraph(len(q))
    for i in range(len(q)):
        a = q[i]
        for j in range(i + 1, len(q)):
            g.checks += 1
            if overlaps(a, q[j]): g.add(i, j)
    g.normalise(); return g


def build_sweep(q):
    """Group by resource, sort by start time, scan only while intervals still overlap."""
    g = ConflictGraph(len(q))
    idx = sorted(range(len(q)), key=lambda i: (q[i].res, q[i].start))
    for i in range(len(idx)):
        a = q[idx[i]]
        for j in range(i + 1, len(idx)):
            g.checks += 1
            b = q[idx[j]]
            if a.res != b.res or b.start >= a.end: break
            g.add(idx[i], idx[j])
    g.normalise(); return g


# ---------------------------------------------------------------- Greedy allocation using the heap
def allocate_greedy(q, g):
    """Serve in priority order; accept only if no already-accepted request clashes with it."""
    h = RequestHeap()
    for r in q: h.push(r)
    acc = [False] * len(q)
    while not h.empty():
        r = h.pop()
        if not any(acc[nb] for nb in g.adj[r.id]): acc[r.id] = True
    return acc


# ---------------------------------------------------------------- Dynamic programming
def weighted_interval_dp(q, idx, want_set=False):
    """Weighted interval scheduling on ONE resource.
    dp[j] = max(dp[j-1], w_j + dp[p(j)]), p(j) = number of bookings ending at or before start_j."""
    idx = sorted(idx, key=lambda i: q[i].end)
    ends = [q[i].end for i in idx]
    m = len(idx)
    p = [0] * (m + 1)
    for j in range(1, m + 1):
        p[j] = bisect_right(ends, q[idx[j - 1]].start, 0, j - 1)
    dp = [0] * (m + 1)
    for j in range(1, m + 1):
        dp[j] = max(dp[j - 1], q[idx[j - 1]].priority + dp[p[j]])
    chosen = []
    if want_set:
        j = m
        while j > 0:
            if q[idx[j - 1]].priority + dp[p[j]] == dp[j]:
                chosen.append(idx[j - 1]); j = p[j]
            else:
                j -= 1
    return dp[m], chosen


def allocate_dp(q):
    """Campus optimum = sum of per-resource optima (resources are independent)."""
    by = {}
    for i, r in enumerate(q): by.setdefault(r.res, []).append(i)
    total, acc = 0, [False] * len(q)
    for idx in by.values():
        t, ch = weighted_interval_dp(q, idx, True)
        total += t
        for i in ch: acc[i] = True
    return total, acc


def brute_force_best(q):
    """Control for small single-resource instances."""
    n, best = len(q), 0
    for mask in range(1 << n):
        pick = [i for i in range(n) if mask >> i & 1]
        if all(not overlaps(q[a], q[b]) for k, a in enumerate(pick) for b in pick[k + 1:]):
            best = max(best, sum(q[i].priority for i in pick))
    return best


# ---------------------------------------------------------------- Graph colouring (rooms for flexible requests)
def _order(g):
    return sorted(range(g.n), key=lambda v: (-len(g.adj[v]), v))


def welch_powell(g):
    """Colour in decreasing degree order, one colour class at a time. Returns (colours_used, colouring)."""
    col, left, c = [-1] * g.n, g.n, 0
    order = _order(g)
    while left > 0:
        for v in order:
            if col[v] == -1 and all(col[nb] != c for nb in g.adj[v]):
                col[v] = c; left -= 1
        c += 1
    return c, col


def exact_colouring(g, use_bound, node_cap=5_000_000):
    """Exact minimum colouring by backtracking. use_bound=True makes it branch and bound:
    a branch is cut once it already uses as many colours as the best colouring found so far.
    Returns (k, nodes, complete)."""
    n = g.n
    if n == 0: return 0, 0, True
    order, col = _order(g), [-1] * g.n
    state = {"best": n + 1, "nodes": 0, "capped": False}

    def dfs(pos, used):
        if state["capped"]: return
        state["nodes"] += 1
        if state["nodes"] > node_cap: state["capped"] = True; return
        if use_bound and used >= state["best"]: return
        if pos == n:
            state["best"] = min(state["best"], used); return
        v = order[pos]
        for c in range(used + 1):
            if all(col[nb] != c for nb in g.adj[v]):
                col[v] = c
                dfs(pos + 1, max(used, c + 1))
                col[v] = -1

    dfs(0, 0)
    return state["best"], state["nodes"], not state["capped"]


def max_overlap(q):
    """Most simultaneous requests on one resource = rooms really needed for an interval graph."""
    ev = sorted([(r.start, 1) for r in q] + [(r.end, -1) for r in q])
    cur = best = 0
    for _, d in ev:
        cur += d; best = max(best, cur)
    return best


# ---------------------------------------------------------------- seeded data generator
def generate_requests(n, R, horizon, seed):
    g = random.Random(seed)
    q = []
    for i in range(n):
        res = g.randint(1, R)
        s = g.randrange(horizon)
        d = g.randint(1, 4)
        e = min(horizon, s + d)
        if e <= s: e = s + 1
        q.append(Request(i, res, s, e, g.randint(1, 10)))
    return q
