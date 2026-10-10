"""Intelligent Campus Resources Optimization System - DSA-II prototype (Review 2).
Trees (BST/AVL), Heap, Graph (adjacency list), Dynamic Programming, Backtracking + Branch and Bound.
A clash = same resource and overlapping half-open interval [start, end)."""
import random
from bisect import bisect_left, bisect_right, insort
from collections import namedtuple

# A bookable physical resource. Only id/type/capacity are required, so Resource(1, "room", 30) still works.
#   available : False = out of service     equipment : set of equipment names the resource has
#   window    : (open, close) minutes of every day, or None = always open
#   blackouts : tuple of (start, end) absolute-minute periods when it is closed (maintenance)
Resource = namedtuple("Resource", "id type capacity available equipment name window blackouts",
                      defaults=(True, frozenset(), "", None, ()))
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


def exact_colouring(g, use_bound, node_cap=5_000_000, return_colouring=False):
    """Exact minimum colouring by backtracking. use_bound=True makes it branch and bound:
    a branch is cut once it already uses as many colours as the best colouring found so far.
    Returns (k, nodes, complete); with return_colouring=True also the colour of every vertex."""
    n = g.n
    if n == 0: return (0, 0, True, []) if return_colouring else (0, 0, True)
    order, col = _order(g), [-1] * g.n
    state = {"best": n + 1, "nodes": 0, "capped": False, "col": None}

    def dfs(pos, used):
        if state["capped"]: return
        state["nodes"] += 1
        if state["nodes"] > node_cap: state["capped"] = True; return
        if use_bound and used >= state["best"]: return
        if pos == n:
            if used < state["best"]: state["best"] = used; state["col"] = col[:]
            return
        v = order[pos]
        for c in range(used + 1):
            if all(col[nb] != c for nb in g.adj[v]):
                col[v] = c
                dfs(pos + 1, max(used, c + 1))
                col[v] = -1

    dfs(0, 0)
    out = (state["best"], state["nodes"], not state["capped"])
    return out + (state["col"],) if return_colouring else out


def max_overlap(q):
    """Most simultaneous requests on one resource = rooms really needed for an interval graph.
    Intervals are half-open [start, end): at the same instant an END is processed before a START,
    so [0,5) and [5,10) are NOT simultaneous."""
    END, START = 0, 1
    ev = sorted([(r.start, START) for r in q] + [(r.end, END) for r in q])
    cur = best = 0
    for _, kind in ev:
        cur += 1 if kind == START else -1
        best = max(best, cur)
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


# =====================================================================================
#                       CAMPUS BOOKING WORKFLOW (added in Review 2, part 2)
# Everything below builds on the structures above: AVL (inventory), heap (priority order),
# conflict graph (competing requests), DP (best set per resource), colouring (room mapping).
# =====================================================================================

# ---------------------------------------------------------------- time helpers
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAY_MIN = 1440


def at(day, hhmm):
    """Absolute minute of the week: at('Tue', '14:30') or at(1, '14:30'). Monday 00:00 = 0."""
    d = DAYS.index(day) if isinstance(day, str) else int(day)
    h, m = hhmm.split(":")
    return d * DAY_MIN + int(h) * 60 + int(m)


def hhmm(m): return f"{m // 60:02d}:{m % 60:02d}"


def fmt_time(t):
    d, m = divmod(t, DAY_MIN)
    return f"{DAYS[d % 7]} {hhmm(m)}"


def fmt_span(s, e):
    return f"{fmt_time(s)}-{hhmm(e % DAY_MIN)}" if s // DAY_MIN == e // DAY_MIN else f"{fmt_time(s)}-{fmt_time(e)}"


# ---------------------------------------------------------------- booking requests
# capacity = people / seats needed; equipment = names the resource must have;
# preferred_res = a specific resource ID (None = any suitable resource of res_type).
BookingRequest = namedtuple("BookingRequest",
                            "id requester dept res_type start end priority capacity equipment preferred_res purpose",
                            defaults=(1, frozenset(), None, ""))

LABEL = {"INVALID_TIME": "Invalid time range", "NO_RESOURCE_TYPE": "No such resource type",
         "BAD_PREFERENCE": "Preferred resource not usable", "CAPACITY": "Insufficient capacity",
         "EQUIPMENT": "Required equipment not available", "UNAVAILABLE": "Resource unavailable",
         "OUTSIDE_HOURS": "Outside operating hours", "TIME_CLASH": "Time clash"}


# ---------------------------------------------------------------- inventory (AVL tree keyed by resource ID)
class Inventory:
    def __init__(self, resources):
        self.tree, self.resources = AVL(), []
        for r in resources:
            if self.tree.find(r.id) is not None: raise ValueError(f"duplicate resource id {r.id}")
            self.tree.insert(r); self.resources.append(r)

    def get(self, rid): return self.tree.find(rid)

    def by_type(self, t):
        """Resources of one type, smallest capacity first (so allocation can pick the best fit)."""
        return sorted((r for r in self.resources if r.type == t), key=lambda r: (r.capacity, str(r.id)))

    def types(self): return sorted({r.type for r in self.resources})


# ---------------------------------------------------------------- suitability checks
def check_resource(res, req):
    """Everything that stops `res` serving `req`, as a list of (code, detail). Empty list = suitable."""
    fails = []
    if not res.available:
        fails.append(("UNAVAILABLE", f"{res.id} is out of service"))
    for b0, b1 in res.blackouts:
        if req.start < b1 and b0 < req.end:
            fails.append(("UNAVAILABLE", f"{res.id} is closed for maintenance {fmt_span(b0, b1)}")); break
    if res.window is not None:
        o, c = res.window
        day0 = (req.start // DAY_MIN) * DAY_MIN
        if req.start - day0 < o or req.end - day0 > c:
            fails.append(("OUTSIDE_HOURS", f"{res.id} is open {hhmm(o)}-{hhmm(c)} only"))
    if req.capacity > res.capacity:
        fails.append(("CAPACITY", f"{res.id} holds {res.capacity}, needs {req.capacity}"))
    missing = set(req.equipment) - set(res.equipment)
    if missing:
        fails.append(("EQUIPMENT", f"{res.id} lacks {', '.join(sorted(missing))}"))
    return fails


def _nice(t): return t.replace("_", " ")


def eligibility(inv, req):
    """Resources that could serve `req` (best fit first), or a (code, message) reason if none can."""
    if req.end <= req.start:
        return [], ("INVALID_TIME", f"{LABEL['INVALID_TIME']}: end {fmt_time(req.end)} is not after start {fmt_time(req.start)}")
    if req.preferred_res is not None:
        r = inv.get(req.preferred_res)
        if r is None or r.type != req.res_type:
            return [], ("BAD_PREFERENCE", f"{LABEL['BAD_PREFERENCE']}: {req.preferred_res} is not a {_nice(req.res_type)} in the inventory")
        cands = [r]
    else:
        cands = inv.by_type(req.res_type)
        if not cands:
            return [], ("NO_RESOURCE_TYPE", f"{LABEL['NO_RESOURCE_TYPE']}: no '{_nice(req.res_type)}' in the inventory")
    good, best = [], None
    for r in cands:
        f = check_resource(r, req)
        if not f:
            good.append(r.id); continue
        # "closest" candidate: fewest permanent mismatches (capacity/equipment), then fewest failures, then biggest
        key = (sum(c in ("CAPACITY", "EQUIPMENT") for c, _ in f), len(f), -r.capacity)
        if best is None or key < best[0]: best = (key, f)
    if good: return good, None
    f = best[1]
    return [], (f[0][0], f"{LABEL[f[0][0]]}: {'; '.join(d for _, d in f)} ({len(cands)} {_nice(req.res_type)} resource{'s' if len(cands) != 1 else ''} checked)")


# ---------------------------------------------------------------- availability: one calendar per physical resource
class ResourceCalendar:
    def __init__(self): self.slots = {}                      # res id -> sorted [(start, end, req id)]

    def blocking(self, rid, s, e):
        """The existing booking that overlaps [s, e) on this resource, or None if the slot is free."""
        lst = self.slots.get(rid, [])
        i = bisect_left(lst, (s,))
        if i > 0 and lst[i - 1][1] > s: return lst[i - 1]
        if i < len(lst) and lst[i][0] < e: return lst[i]
        return None

    def book(self, rid, s, e, req_id):
        if self.blocking(rid, s, e) is not None: raise ValueError(f"{rid} is already booked in [{s}, {e})")
        insort(self.slots.setdefault(rid, []), (s, e, req_id))

    def cancel(self, rid, req_id):
        self.slots[rid] = [x for x in self.slots.get(rid, []) if x[2] != req_id]

    def copy(self):
        c = ResourceCalendar(); c.slots = {k: list(v) for k, v in self.slots.items()}; return c


class CampusBookingSystem:
    """Online use: approve or reject one request at a time against the current calendars."""
    def __init__(self, inv):
        self.inv, self.cal, self.reqs, self.where = inv, ResourceCalendar(), {}, {}

    def load(self, requests, accepted):
        for r in requests:
            if r.id in accepted:
                self.cal.book(accepted[r.id], r.start, r.end, r.id); self.reqs[r.id] = r; self.where[r.id] = accepted[r.id]

    def request(self, req):
        """Returns (accepted, resource_id, reason). Overlap on the same physical resource is never allowed."""
        elig, why = eligibility(self.inv, req)
        if not elig: return False, None, why
        blockers = []
        for rid in elig:
            b = self.cal.blocking(rid, req.start, req.end)
            if b is None:
                self.cal.book(rid, req.start, req.end, req.id); self.reqs[req.id] = req; self.where[req.id] = rid
                return True, rid, None
            blockers.append((self.reqs[b[2]], rid))
        return False, None, ("TIME_CLASH", _clash_text(req, blockers, len(elig)))

    def cancel(self, req_id):
        self.cal.cancel(self.where.pop(req_id), req_id); self.reqs.pop(req_id, None)


def _clash_text(r, blockers, n_elig):
    b, rid = max(blockers, key=lambda x: x[0].priority)
    txt = f"{LABEL['TIME_CLASH']}: {rid} is booked {fmt_span(b.start, b.end)} by #{b.id} ({b.dept}, priority {b.priority})"
    if n_elig > 1: txt += f"; all {n_elig} suitable {_nice(r.res_type)} resources are taken in this period"
    same = [x for x, res in blockers if res == rid]
    if sum(x.priority for x in same) >= r.priority > b.priority:
        txt += f"; the bookings kept there are worth more together ({sum(x.priority for x in same)} vs {r.priority})"
    return txt


# ---------------------------------------------------------------- allocation pipeline
class AllocationResult:
    pass


def _value(assign, by_id): return sum(by_id[i].priority for i, r in assign.items() if r is not None)


def _calendar(assign, by_id):
    cal = ResourceCalendar()
    for i, rid in assign.items():
        if rid is not None: cal.book(rid, by_id[i].start, by_id[i].end, i)
    return cal


def _heap_pass(reqs, elig, assign):
    """Serve unassigned requests highest priority first; take the first (best-fit) free eligible resource."""
    by_id = {r.id: r for r in reqs}
    cal = _calendar(assign, by_id)
    h = RequestHeap()
    for r in reqs:
        if assign[r.id] is None: h.push(r)
    while not h.empty():
        r = h.pop()
        for rid in elig[r.id]:
            if cal.blocking(rid, r.start, r.end) is None:
                cal.book(rid, r.start, r.end, r.id); assign[r.id] = rid; break


def _dp_improve(reqs, elig, assign, res_order):
    """Per resource, re-pick the most valuable non-clashing set among its current bookings plus any
    unplaced request that could use it. Only applied when the value strictly rises, so the result is
    never worse than the heap pass. Returns a log of (resource, value before, value after)."""
    log, changed = [], True
    while changed:
        changed = False
        for rid in res_order:
            cand = [i for i, r in enumerate(reqs) if assign[r.id] == rid or (assign[r.id] is None and rid in elig[r.id])]
            if not cand: continue
            before = sum(reqs[i].priority for i in cand if assign[reqs[i].id] == rid)
            after, chosen = weighted_interval_dp(reqs, cand, True)
            if after > before:
                keep = set(chosen)
                for i in cand:
                    if assign[reqs[i].id] == rid and i not in keep: assign[reqs[i].id] = None
                for i in chosen: assign[reqs[i].id] = rid
                log.append((rid, before, after)); changed = True
    return log


def assign_colour_classes(classes, elig, base_cal):
    """Give every colour class (requests that never overlap in time) ONE physical room.
    Valid only if the room is suitable for every member and free of other bookings. Returns
    {request id: room} or None when any class cannot be placed (then nothing may be reassigned)."""
    cal, mapping = base_cal.copy(), {}
    for cls in sorted(classes, key=lambda c: (-len(c), str(c[0].id))):
        common = set(elig[cls[0].id])
        for r in cls[1:]: common &= set(elig[r.id])
        room = next((x for x in elig[cls[0].id] if x in common
                     and all(cal.blocking(x, r.start, r.end) is None for r in cls)), None)
        if room is None: return None
        for r in cls: cal.book(room, r.start, r.end, r.id); mapping[r.id] = room
    return mapping


def _remap_with_colouring(by_id, elig, assign):
    """For each resource type: colour the accepted FLEXIBLE requests (>= 2 suitable rooms) by time overlap,
    map colours to real rooms, and adopt the mapping only if it is valid and uses no more rooms."""
    report, groups = {}, {}
    for i, rid in assign.items():
        if rid is not None and len(elig[i]) >= 2: groups.setdefault(by_id[i].res_type, []).append(by_id[i])
    for t, F in sorted(groups.items()):
        if len(F) < 2: continue
        F.sort(key=lambda r: (r.start, str(r.id)))
        g = ConflictGraph(len(F))
        for a in range(len(F)):
            for b in range(a + 1, len(F)):
                if F[b].start >= F[a].end: break
                g.add(a, b)
        g.normalise()
        k, col = welch_powell(g)
        if len(F) <= 14:
            ek, _, done, ecol = exact_colouring(g, True, return_colouring=True)
            if done and ek <= k: k, col = ek, ecol
        classes = [[F[v] for v in range(len(F)) if col[v] == c] for c in range(k)]
        in_f = {r.id for r in F}
        base = _calendar({i: rid for i, rid in assign.items() if rid is not None and i not in in_f}, by_id)
        mapping = assign_colour_classes(classes, elig, base)
        before = len({assign[r.id] for r in F})
        rep = {"requests": len(F), "rooms_needed": k, "rooms_before": before, "rooms_after": None, "applied": False}
        if mapping is None:
            rep["note"] = "no valid room for a colour class - assignments left unchanged"
        else:
            rep["rooms_after"] = len(set(mapping.values()))
            if rep["rooms_after"] <= before:
                assign.update(mapping); rep["applied"] = True; rep["note"] = "valid mapping applied"
            else:
                rep["note"] = "mapping valid but would use more rooms - unchanged"
        report[t] = rep
    return report


def allocate_campus(inv, requests):
    """Full workflow: eligibility -> conflict graph -> heap pass -> DP improvement -> colouring-based
    room mapping -> fill pass -> reasons for every rejection."""
    R = AllocationResult()
    by_id, rejected, ok, elig = {}, {}, [], {}
    for r in requests:
        if r.id in by_id: raise ValueError(f"duplicate request id {r.id}")
        by_id[r.id] = r
        e, why = eligibility(inv, r)
        if e: ok.append(r); elig[r.id] = e
        else: rejected[r.id] = why
    # conflict graph: vertices = suitable requests, edge = overlap in time AND a suitable resource in common
    pos = {r.id: i for i, r in enumerate(ok)}
    g = ConflictGraph(len(ok))
    for t in sorted({r.res_type for r in ok}):
        grp = sorted((r for r in ok if r.res_type == t), key=lambda r: (r.start, str(r.id)))
        for a in range(len(grp)):
            for b in range(a + 1, len(grp)):
                if grp[b].start >= grp[a].end: break
                if set(elig[grp[a].id]) & set(elig[grp[b].id]): g.add(pos[grp[a].id], pos[grp[b].id])
    g.normalise()
    R.graph, R.graph_ids = g, [r.id for r in ok]
    R.conflicts = sorted((ok[u].id, ok[v].id) for u in range(g.n) for v in g.adj[u] if u < v)

    assign = {r.id: None for r in ok}
    _heap_pass(ok, elig, assign)
    R.greedy_value = _value(assign, by_id)
    R.greedy_accepted = sum(v is not None for v in assign.values())
    R.dp_log = _dp_improve(ok, elig, assign, [r.id for r in inv.resources])
    R.dp_value = _value(assign, by_id)
    R.colouring = _remap_with_colouring(by_id, elig, assign)
    _heap_pass(ok, elig, assign)                           # fill any slot the remapping freed
    R.final_value = _value(assign, by_id)

    for r in ok:
        if assign[r.id] is None:
            blockers = [(ok[n], assign[ok[n].id]) for n in g.adj[pos[r.id]]
                        if assign[ok[n].id] in elig[r.id]]
            rejected[r.id] = ("TIME_CLASH", _clash_text(r, blockers, len(elig[r.id])))
    R.requests, R.eligible = by_id, elig
    R.accepted = {i: rid for i, rid in assign.items() if rid is not None}
    R.rejected = rejected
    R.total_value = sum(r.priority for r in requests)
    return R


def verify_schedule(inv, requests, accepted):
    """Independent re-check of a finished schedule. Returns a list of problems (empty = valid)."""
    problems, by_id, per = [], {r.id: r for r in requests}, {}
    for i, rid in accepted.items():
        r, res = by_id.get(i), inv.get(rid)
        if r is None or res is None: problems.append(f"#{i}: unknown request or resource {rid}"); continue
        if r.end <= r.start: problems.append(f"#{i}: end is not after start")
        if res.type != r.res_type: problems.append(f"#{i}: {rid} is a {res.type}, request wants {r.res_type}")
        problems += [f"#{i} on {rid}: {d}" for _, d in check_resource(res, r)]
        per.setdefault(rid, []).append(r)
    for rid, lst in per.items():
        for a in range(len(lst)):
            for b in range(a + 1, len(lst)):
                if lst[a].start < lst[b].end and lst[b].start < lst[a].end:
                    problems.append(f"double booking on {rid}: #{lst[a].id} and #{lst[b].id}")
    return problems
