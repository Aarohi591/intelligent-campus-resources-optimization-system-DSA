import csv, statistics, time
from campus import *

def time_ms(f, reps):
    ts = []
    for _ in range(reps):
        a = time.perf_counter(); r = f(); ts.append((time.perf_counter() - a) * 1000)
    return statistics.median(ts), r

rows = []
def rec(exp, n, metric, val): rows.append((exp, n, metric, val))

print("== 1. Resource records: BST vs AVL (ids inserted in sorted order, every id searched) ==")
print("n      BST_height  AVL_height  BST_avg_cmp  AVL_avg_cmp  AVL_rotations")
for n in (1000, 2000, 4000, 8000):
    b, a = BST(), AVL()
    for i in range(1, n + 1): b.insert(Resource(i, "room", 30)); a.insert(Resource(i, "room", 30))
    cb, ca = [0], [0]
    for i in range(1, n + 1): b.find(i, cb); a.find(i, ca)
    print(f"{n:<6} {b.height():<11} {a.height():<11} {cb[0]/n:<12.1f} {ca[0]/n:<12.1f} {a.rotations}")
    rec("tree", n, "bst_height", b.height()); rec("tree", n, "avl_height", a.height())
    rec("tree", n, "bst_avg_cmp", round(cb[0]/n, 2)); rec("tree", n, "avl_avg_cmp", round(ca[0]/n, 2))

print("\n== 2. Clash detection: all-pairs vs sort-and-sweep (40 resources, 400 slots) ==")
print("requests  edges    naive_checks  sweep_checks  naive_ms   sweep_ms")
for n in (1000, 2000, 4000, 8000):
    q = generate_requests(n, 40, 400, 11)
    tn, gn = time_ms(lambda: build_naive(q), 1)
    ts, gs = time_ms(lambda: build_sweep(q), 3)
    print(f"{n:<9} {gn.edges:<8} {gn.checks:<13} {gs.checks:<13} {tn:<10.2f} {ts:<9.2f} {'same-graph' if gn.adj == gs.adj else 'MISMATCH'}")
    rec("conflict", n, "edges", gn.edges); rec("conflict", n, "naive_checks", gn.checks); rec("conflict", n, "sweep_checks", gs.checks)
    rec("conflict", n, "naive_ms", round(tn, 2)); rec("conflict", n, "sweep_ms", round(ts, 2))

print("\n== 3. Allocation: heap-greedy vs DP (avg of 20 seeds, 40 resources) ==")
print("requests  slots  greedy_accepted  dp_accepted  greedy_weight  dp_weight  dp_gain_%")
for n, H in ((1000, 300), (2000, 300), (4000, 300), (4000, 100), (8000, 100)):
    ga = da = gw = dw = 0
    for s in range(1, 21):
        q = generate_requests(n, 40, H, s); g = build_sweep(q); acc = allocate_greedy(q, g)
        tot, dacc = allocate_dp(q)
        ga += sum(acc); da += sum(dacc); gw += sum(q[i].priority for i in range(n) if acc[i]); dw += tot
    ga, da, gw, dw = ga / 20, da / 20, gw / 20, dw / 20
    gain = 100 * (dw - gw) / gw
    print(f"{n:<9} {H:<6} {ga:<16.1f} {da:<12.1f} {gw:<14.1f} {dw:<10.1f} {gain:.2f}")
    rec(f"alloc_h{H}", n, "greedy_weight", round(gw, 1)); rec(f"alloc_h{H}", n, "dp_weight", round(dw, 1)); rec(f"alloc_h{H}", n, "dp_gain_pct", round(gain, 2))

print("\n== 4. Colouring one resource's requests: Welch-Powell vs exact (avg over 30 seeds) ==")
print("requests  optimum(avg)  WelchPowell(avg)  WP_not_optimal  plain_nodes  BnB_nodes  node_cut_%")
S = 30
for n in (8, 10, 12):
    opt = wp = pn = bn = worse = 0
    for s in range(1, S + 1):
        q = generate_requests(n, 1, n * 2, s); g = build_sweep(q)
        kb, nb, _ = exact_colouring(g, True); kp, npl, _ = exact_colouring(g, False)
        w = welch_powell(g)[0]
        opt += kb; wp += w; bn += nb; pn += npl; worse += w > kb
    print(f"{n:<9} {opt/S:<13.2f} {wp/S:<17.2f} {worse:<15} {pn/S:<12.0f} {bn/S:<10.0f} {100*(pn-bn)/pn:.1f}")
    rec("colour", n, "plain_nodes", round(pn / S)); rec("colour", n, "bnb_nodes", round(bn / S)); rec("colour", n, "wp_not_optimal", worse)

print("\n== 5. Larger single-resource cases, exact B&B only (100 seeds) ==")
print("requests  optimum(avg)  WelchPowell(avg)  WP_not_optimal  BnB_nodes(avg)  all_complete")
for n in (20, 30, 40):
    opt = wp = bn = worse = 0; done = True
    for s in range(1, 101):
        q = generate_requests(n, 1, n * 2, s); g = build_sweep(q)
        kb, nb, ok = exact_colouring(g, True); w = welch_powell(g)[0]
        done &= ok; opt += kb; wp += w; bn += nb; worse += w > kb
    print(f"{n:<9} {opt/100:<13.2f} {wp/100:<17.2f} {worse:<15} {bn/100:<15.0f} {'yes' if done else 'no'}")
    rec("colour_large", n, "wp_not_optimal", worse); rec("colour_large", n, "bnb_nodes", round(bn / 100))

with open("results.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["experiment", "n", "metric", "value"]); w.writerows(rows)
