from campus import *
from sample_data import sample_inventory, sample_requests, random_requests

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


# =============================== campus booking workflow tests ===============================
# (checks 1-10 above test the algorithms; everything below tests the booking rules)
F = frozenset
def mini_inv():
    return Inventory([Resource("R1", "room", 30, equipment=F({"projector"})), Resource("R2", "room", 60),
                      Resource("H1", "hall", 100, window=(8 * 60, 20 * 60), blackouts=((at(1, "10:00"), at(1, "12:00")),)),
                      Resource("L1", "lab", 20, available=False)])
def rq(i, typ, s, e, prio=5, cap=1, eq=(), pref=None, day=0):
    return BookingRequest(i, f"user{i}", "TestDept", typ, at(day, s), at(day, e), prio, cap, F(eq), pref)

# 11. time helpers and backward compatibility
check("at()/fmt_time() round trip", at("Tue", "14:30") == 1440 + 14 * 60 + 30 and fmt_time(at("Tue", "14:30")) == "Tue 14:30" and fmt_span(at(0, "09:00"), at(0, "10:30")) == "Mon 09:00-10:30")
check("Old Resource(id, type, capacity) still works", Resource(1, "room", 30).available is True and Resource(1, "room", 30).equipment == F())

# 12. inventory
inv = mini_inv()
check("Inventory lookup via AVL + by_type sorted by capacity", inv.get("R2").capacity == 60 and inv.get("nope") is None and [r.id for r in inv.by_type("room")] == ["R1", "R2"])
try: Inventory([Resource("X", "room", 1), Resource("X", "room", 2)]); dup = False
except ValueError: dup = True
check("Inventory rejects duplicate resource IDs", dup)

# 13. overlapping / non-overlapping bookings on the same physical resource
bs = CampusBookingSystem(mini_inv())
a1 = bs.request(rq(1, "room", "09:00", "10:00", pref="R1"))
a2 = bs.request(rq(2, "room", "09:30", "10:30", pref="R1"))
check("Overlapping booking on the same resource is rejected (TIME_CLASH)", a1[0] and a1[1] == "R1" and not a2[0] and a2[2][0] == "TIME_CLASH")
a3 = bs.request(rq(3, "room", "10:00", "11:00", pref="R1"))
a4 = bs.request(rq(4, "room", "08:00", "09:00", pref="R1"))
a5 = bs.request(rq(5, "room", "12:00", "13:00", pref="R1"))
check("Touching / non-overlapping bookings on the same resource are accepted ([9,10) then [10,11))", a3[0] and a4[0] and a5[0])
bs2 = CampusBookingSystem(mini_inv())
b1, b2, b3 = (bs2.request(rq(i, "room", "09:00", "10:00")) for i in (1, 2, 3))
check("Same time on different physical rooms is fine; a third request has no room left",
      b1[0] and b2[0] and {b1[1], b2[1]} == {"R1", "R2"} and not b3[0] and b3[2][0] == "TIME_CLASH")
bs2.cancel(1)
check("Cancelling a booking frees the slot", bs2.request(rq(9, "room", "09:00", "10:00"))[0])
cal = ResourceCalendar(); cal.book("X", 0, 5, 1)
check("Calendar boundaries follow [start, end)", cal.blocking("X", 5, 10) is None and cal.blocking("X", -3, 0) is None
      and cal.blocking("X", 4, 6) is not None and cal.blocking("X", -1, 1) is not None)
try: cal.book("X", 3, 4, 2); raised = False
except ValueError: raised = True
check("Calendar refuses a double booking", raised)

# 14. capacity
inv = mini_inv()
e30, w30 = eligibility(inv, rq(1, "room", "09:00", "10:00", cap=30))
e31, w31 = eligibility(inv, rq(1, "room", "09:00", "10:00", cap=31))
e61, w61 = eligibility(inv, rq(1, "room", "09:00", "10:00", cap=61))
check("Capacity: exact fit allowed, best-fit order, too large goes to the bigger room", e30 == ["R1", "R2"] and e31 == ["R2"])
check("Capacity: demand above every room is rejected with CAPACITY", e61 == [] and w61[0] == "CAPACITY" and "holds 60, needs 61" in w61[1])

# 15. equipment
e, w = eligibility(inv, rq(1, "room", "09:00", "10:00", eq=["projector"]))
e2, w2 = eligibility(inv, rq(1, "room", "09:00", "10:00", eq=["projector", "microphone"]))
check("Equipment: only rooms that have it are suitable", e == ["R1"])
check("Equipment: missing equipment is rejected with EQUIPMENT and names the item", e2 == [] and w2[0] == "EQUIPMENT" and "microphone" in w2[1])

# 16. availability and validity
check("Out-of-service resource -> UNAVAILABLE", eligibility(inv, rq(1, "lab", "09:00", "10:00"))[1][0] == "UNAVAILABLE")
check("Before opening time -> OUTSIDE_HOURS", eligibility(inv, rq(1, "hall", "07:00", "09:00"))[1][0] == "OUTSIDE_HOURS")
check("Ending after closing time -> OUTSIDE_HOURS", eligibility(inv, rq(1, "hall", "19:00", "20:30"))[1][0] == "OUTSIDE_HOURS")
check("Booking until exactly closing time is allowed", eligibility(inv, rq(1, "hall", "19:00", "20:00"))[0] == ["H1"])
check("Maintenance blackout -> UNAVAILABLE", eligibility(inv, rq(1, "hall", "11:00", "13:00", day=1))[1][0] == "UNAVAILABLE"
      and eligibility(inv, rq(1, "hall", "12:00", "13:00", day=1))[0] == ["H1"])
check("End not after start -> INVALID_TIME", eligibility(inv, rq(1, "room", "10:00", "10:00"))[1][0] == "INVALID_TIME")
check("Unknown type -> NO_RESOURCE_TYPE", eligibility(inv, rq(1, "pool", "09:00", "10:00"))[1][0] == "NO_RESOURCE_TYPE")
check("Preferred resource of the wrong type -> BAD_PREFERENCE", eligibility(inv, rq(1, "room", "09:00", "10:00", pref="H1"))[1][0] == "BAD_PREFERENCE")

# 17. allocation correctness on small hand-made cases
inv = mini_inv()
R = allocate_campus(inv, [rq(1, "hall", "09:00", "11:00", prio=3), rq(2, "hall", "10:00", "12:00", prio=8)])
check("Higher-priority request wins a contested resource", list(R.accepted) == [2] and R.rejected[1][0] == "TIME_CLASH")
R = allocate_campus(inv, [rq(1, "hall", "09:00", "13:00", prio=6), rq(2, "hall", "09:00", "11:00", prio=5), rq(3, "hall", "11:00", "13:00", prio=5)])
check("DP beats heap-greedy: two 5s (10) kept instead of one 6", set(R.accepted) == {2, 3} and R.greedy_value == 6 and R.final_value == 10 and R.rejected[1][0] == "TIME_CLASH")
check("Rejection reason explains why the bigger single booking lost", "worth more together" in R.rejected[1][1])
R = allocate_campus(inv, [rq(1, "room", "09:00", "10:00", cap=50), rq(2, "room", "09:00", "10:00", cap=20)])
check("Large request takes the large room, small one the small room", R.accepted == {1: "R2", 2: "R1"})
R = allocate_campus(inv, [rq(1, "room", "09:00", "10:00", cap=100), rq(2, "lab", "09:00", "10:00")])
check("Every request is accepted or rejected, never both, never lost", len(R.accepted) + len(R.rejected) == 2 and not set(R.accepted) & set(R.rejected))
try: allocate_campus(inv, [rq(1, "room", "09:00", "10:00"), rq(1, "room", "11:00", "12:00")]); dupreq = False
except ValueError: dupreq = True
check("Duplicate request IDs are refused", dupreq)

# 18. sample campus: exact expected outcome (snapshot of the fictional sample data) + independent verification
inv, reqs = sample_inventory(), sample_requests()
R = allocate_campus(inv, reqs)
want_rej = {3: "TIME_CLASH", 5: "CAPACITY", 6: "EQUIPMENT", 9: "TIME_CLASH", 11: "UNAVAILABLE", 12: "UNAVAILABLE", 13: "TIME_CLASH",
            18: "TIME_CLASH", 20: "TIME_CLASH", 21: "OUTSIDE_HOURS", 22: "TIME_CLASH"}
check("Sample campus: expected rejections and reason codes", {i: c for i, (c, _) in R.rejected.items()} == want_rej)
check("Sample campus: expected accepted set", set(R.accepted) == {1, 2, 4, 7, 8, 10, 14, 15, 16, 17, 19, 23, 24})
check("Sample campus: schedule passes independent verification (no double booking, all rules met)", verify_schedule(inv, reqs, R.accepted) == [])
check("Sample campus: every rejection has a reason from the known list", all(c in LABEL and len(m) > 10 for c, m in R.rejected.values()))
check("Sample campus: DP stage lifted value above heap-only value", R.dp_value > R.greedy_value and R.final_value >= R.dp_value)
ids = R.graph_ids
check("Conflict graph lists the competing requests (e.g. 1-2 on classrooms, 13-14 on the auditorium)", (1, 2) in R.conflicts and (13, 14) in R.conflicts and (1, 5) not in R.conflicts)
check("Verifier catches a deliberately broken schedule", len(verify_schedule(inv, reqs, {1: "CR-101", 3: "CR-101"})) >= 1 and len(verify_schedule(inv, reqs, {5: "CR-201"})) >= 1)

# 19. DP = per-resource optimum when every request is pinned to a resource
ok = True
inv = Inventory([Resource(f"P{k}", "room", 100) for k in range(4)])
for s in range(1, 21):
    g = random.Random(s)
    rs = [BookingRequest(i, "u", "d", "room", g.randrange(0, 200), 0, g.randint(1, 10), 5, F(), f"P{g.randrange(4)}") for i in range(60)]
    rs = [r._replace(end=r.start + g.randint(10, 60)) for r in rs]
    got = allocate_campus(inv, rs).final_value
    best = 0
    for k in range(4):
        idx = [i for i, r in enumerate(rs) if r.preferred_res == f"P{k}"]
        best += weighted_interval_dp(rs, idx)[0]
    if got != best: ok = False
check("All-pinned requests: final value equals the per-resource DP optimum (20 seeds)", ok)

# 20. stress: random requests on the sample inventory
ok_v = ok_val = ok_all = ok_reason = True
inv = sample_inventory()
for s in range(1, 41):
    rs = random_requests(inv, 60, s); R = allocate_campus(inv, rs)
    if verify_schedule(inv, rs, R.accepted): ok_v = False
    if R.final_value < R.greedy_value: ok_val = False
    if set(R.accepted) | set(R.rejected) != {r.id for r in rs} or set(R.accepted) & set(R.rejected): ok_all = False
    if any(c not in LABEL or not m for c, m in R.rejected.values()): ok_reason = False
check("Stress (40 random campuses): schedule always valid", ok_v)
check("Stress: final value never below heap-only value", ok_val)
check("Stress: every request accepted xor rejected, every rejection explained", ok_all and ok_reason)

# 21. colouring -> room mapping validity
A, B2, C = rq(1, "room", "09:00", "11:00"), rq(2, "room", "09:00", "11:00"), rq(3, "room", "11:00", "13:00")
m = assign_colour_classes([[A, C], [B2]], {1: ["X", "Y"], 2: ["X", "Y"], 3: ["X"]}, ResourceCalendar())
check("Colour classes map to valid rooms when a common suitable free room exists", m == {1: "X", 3: "X", 2: "Y"})
check("Mapping refused when a class has no common suitable room", assign_colour_classes([[A, C]], {1: ["X"], 3: ["Y"]}, ResourceCalendar()) is None)
base = ResourceCalendar(); base.book("X", A.start, A.end, 99)
check("Mapping refused when the only suitable room is already taken", assign_colour_classes([[A]], {1: ["X"]}, base) is None)
R = allocate_campus(sample_inventory(), sample_requests())
check("Sample campus: colouring report only applies mappings that use no extra rooms",
      all(not x["applied"] or x["rooms_after"] <= x["rooms_before"] for x in R.colouring.values()) and R.colouring["classroom"]["rooms_needed"] == 3)

# 22. max_overlap follows the half-open rule
def Q(s, e): return Request(0, 1, s, e, 1)
check("max_overlap: [0,5) and [5,10) are not simultaneous", max_overlap([Q(0, 5), Q(5, 10)]) == 1)
check("max_overlap: overlap by one slot counts", max_overlap([Q(0, 6), Q(5, 10)]) == 2)
check("max_overlap: touching chain = 1, three at once = 3", max_overlap([Q(0, 2), Q(2, 4), Q(4, 6)]) == 1 and max_overlap([Q(0, 5)] * 3) == 3)
check("max_overlap: [0,5) then two starting at 5 = 2", max_overlap([Q(0, 5), Q(5, 10), Q(5, 10)]) == 2)

print(f"\n{passed} / {total} tests passed")
raise SystemExit(0 if passed == total else 1)
