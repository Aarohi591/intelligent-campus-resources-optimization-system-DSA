from campus import *

passed = total = 0
def check(name, cond):
    global passed, total
    total += 1; passed += bool(cond)
    print(("PASS  " if cond else "FAIL  ") + name)

# 1. AVL stays balanced and sorted for sorted (worst-case) input
t = AVL()
for i in range(1, 1001): t.insert(Resource(i, "room", 30))
ids = t.ids()
check("AVL balanced + inorder sorted (1000 sorted inserts)", t.is_balanced() and ids == sorted(ids) and len(ids) == 1000 and t.height() <= 11)

# 2. BST degenerates on the same input, AVL does not
b, a = BST(), AVL()
for i in range(1, 501): b.insert(Resource(i, "lab", 40)); a.insert(Resource(i, "lab", 40))
check("BST height n vs AVL height log n on sorted input", b.height() == 500 and a.height() <= 9)

# 3. search finds present ids and rejects absent ones
t = AVL()
for i in range(2, 201, 2): t.insert(Resource(i, "hall", 100))
check("AVL find hit / miss", t.find(100) and t.find(100).capacity == 100 and t.find(101) is None)

# 4. heap pops in priority order
h = RequestHeap()
for r in generate_requests(200, 5, 100, 7): h.push(r)
last, ok = 11, True
while not h.empty():
    p = h.pop().priority
    if p > last: ok = False
    last = p
check("Heap pops in non-increasing priority", ok)

# 5. sweep and naive give identical conflict graphs
same = all(build_naive(q).adj == build_sweep(q).adj for q in (generate_requests(300, 10, 150, s) for s in range(1, 21)))
check("Sweep graph == naive graph on 20 seeds", same)

# 6. greedy allocation never accepts two clashing requests
ok = True
for s in range(1, 21):
    q = generate_requests(400, 8, 120, s); g = build_sweep(q); acc = allocate_greedy(q, g)
    if any(acc[u] and acc[v] for u in range(g.n) for v in g.adj[u]): ok = False
check("Greedy result is clash-free on 20 seeds", ok)

# 7. DP equals brute force and is never worse than greedy
okb = True
for s in range(1, 61):
    q = generate_requests(12, 1, 25, s)
    if weighted_interval_dp(q, list(range(len(q))))[0] != brute_force_best(q): okb = False
okg = True
for s in range(1, 31):
    q = generate_requests(500, 6, 150, s); g = build_sweep(q); acc = allocate_greedy(q, g)
    if allocate_dp(q)[0] < sum(q[i].priority for i in range(len(q)) if acc[i]): okg = False
check("DP == brute force on 60 small cases", okb)
check("DP total >= greedy total on 30 campuses", okg)

# 8. DP selection is itself clash-free and matches its reported total
ok = True
for s in range(1, 21):
    q = generate_requests(400, 7, 100, s); tot, acc = allocate_dp(q); g = build_sweep(q)
    if sum(q[i].priority for i in range(len(q)) if acc[i]) != tot: ok = False
    if any(acc[u] and acc[v] for u in range(g.n) for v in g.adj[u]): ok = False
check("DP selection clash-free and total matches", ok)

# 9. exact colouring (B&B) matches max overlap and plain backtracking; Welch-Powell never below optimum
okx = okw = True
for s in range(1, 61):
    q = generate_requests(11, 1, 20, s); g = build_sweep(q)
    kb = exact_colouring(g, True)[0]; kp = exact_colouring(g, False)[0]
    if kb != max_overlap(q) or kp != kb: okx = False
    if welch_powell(g)[0] < kb: okw = False
check("B&B colouring == max overlap == plain backtracking (60 cases)", okx)
check("Welch-Powell colours >= optimum (60 cases)", okw)

# 10. Welch-Powell output is a proper colouring
q = generate_requests(60, 1, 40, 3); g = build_sweep(q); _, col = welch_powell(g)
check("Welch-Powell colouring is proper", all(col[u] != col[v] for u in range(g.n) for v in g.adj[u]))

print(f"\n{passed} / {total} tests passed")
raise SystemExit(0 if passed == total else 1)
