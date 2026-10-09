"""Small demo of the campus allocation workflow on a hand-made day."""
from campus import *

records = AVL()
for r in [Resource(101, "classroom", 60), Resource(102, "classroom", 60), Resource(201, "lab", 40),
          Resource(301, "projector", 1), Resource(401, "ground", 200)]:
    records.insert(r)
# slots = hours of the day starting at 8:00, interval is [start, end)
q = [Request(0, 201, 0, 3, 8), Request(1, 201, 2, 4, 9), Request(2, 201, 4, 6, 5), Request(3, 201, 3, 5, 6),
     Request(4, 101, 1, 3, 7), Request(5, 101, 2, 5, 4), Request(6, 401, 0, 4, 10), Request(7, 401, 3, 6, 3)]
g = build_sweep(q)
print("Clashing pairs found:", g.edges)
for u in range(g.n):
    for v in g.adj[u]:
        if u < v: print(f"  request {u} (res {q[u].res}) clashes with request {v}")
acc = allocate_greedy(q, g)
print("Heap-greedy accepted:", [i for i in range(len(q)) if acc[i]], "(priority total", sum(q[i].priority for i in range(len(q)) if acc[i]), ")")
tot, dacc = allocate_dp(q)
print("DP-optimal accepted: ", [i for i in range(len(q)) if dacc[i]], "(priority total", tot, ")")
for rid in (201, 999):
    r = records.find(rid)
    print(f"Lookup {rid} ->", f"{r.type}, capacity {r.capacity}" if r else "not found")
