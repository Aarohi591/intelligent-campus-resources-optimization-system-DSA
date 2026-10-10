"""Complete campus booking workflow on SAMPLE (fictional) data.
Run:  python demo.py      -> prints the workflow and writes sample_allocation_result.csv"""
import csv
from campus import *
from sample_data import sample_inventory, sample_requests

LINE = "-" * 100
print("=" * 100)
print("INTELLIGENT CAMPUS RESOURCES OPTIMIZATION SYSTEM - booking workflow demo")
print("DATA: clearly labelled SAMPLE data (fictional). It is NOT real campus data.")
print("=" * 100)

inv, reqs = sample_inventory(), sample_requests()

# 1. inventory ---------------------------------------------------------------------------------
print("\n1. RESOURCE INVENTORY (stored in an AVL tree keyed by resource ID)")
print(f"{'ID':<9}{'Type':<14}{'Cap':>4}  {'Status':<28}{'Equipment'}")
for rid in inv.tree.ids():
    r = inv.get(rid)
    status = "OUT OF SERVICE" if not r.available else (f"open {hhmm(r.window[0])}-{hhmm(r.window[1])}" if r.window else "open all day")
    if r.blackouts: status += " +maint."
    print(f"{r.id:<9}{r.type:<14}{r.capacity:>4}  {status:<28}{', '.join(sorted(r.equipment)) or '-'}")

# 2. requests ----------------------------------------------------------------------------------
print(f"\n2. BOOKING REQUESTS ({len(reqs)} submitted)")
print(f"{'#':<3}{'Requester / dept':<36}{'Type':<14}{'When':<20}{'Pri':>3}{'Cap':>5}  Needs")
for r in reqs:
    needs = ", ".join(sorted(r.equipment)) + (f" [only {r.preferred_res}]" if r.preferred_res else "")
    print(f"{r.id:<3}{(r.requester + ' / ' + r.dept)[:34]:<36}{r.res_type:<14}{fmt_span(r.start, r.end):<20}{r.priority:>3}{r.capacity:>5}  {needs}")

# 3. allocate ----------------------------------------------------------------------------------
R = allocate_campus(inv, reqs)

print("\n3. CONFLICT GRAPH (requests that overlap in time AND could use the same resource)")
print(f"   {len(R.graph_ids)} suitable requests, {R.graph.edges} competing pairs:")
print("   " + ", ".join(f"#{a}-#{b}" for a, b in R.conflicts))

print("\n4. ALLOCATION STAGES (value = sum of request priorities)")
print(f"   heap, highest priority first : value {R.greedy_value:>3}  ({R.greedy_accepted} bookings)")
print(f"   + dynamic programming        : value {R.dp_value:>3}")
for rid, before, after in R.dp_log:
    print(f"       DP re-planned {rid}: {before} -> {after}")
print(f"   + room mapping and fill      : value {R.final_value:>3}  ({len(R.accepted)} bookings)  of {R.total_value} requested in total")

print("\n5. GRAPH COLOURING -> ROOM MAPPING (flexible bookings only; applied only when valid)")
for t, c in R.colouring.items():
    print(f"   {t:<12} {c['requests']} flexible bookings need {c['rooms_needed']} room(s); rooms used {c['rooms_before']} -> {c['rooms_after']}; {c['note']}")

# 4. results -----------------------------------------------------------------------------------
print("\n6. ACCEPTED BOOKINGS (by resource)")
by_res = {}
for i, rid in R.accepted.items(): by_res.setdefault(rid, []).append(R.requests[i])
for rid in inv.tree.ids():
    for r in sorted(by_res.get(rid, []), key=lambda x: x.start):
        print(f"   {rid:<9}{fmt_span(r.start, r.end):<20}#{r.id:<3}{r.requester} ({r.dept}) - {r.purpose}, priority {r.priority}")

print("\n7. REJECTED BOOKINGS (with reason)")
for i in sorted(R.rejected):
    r, (code, msg) = R.requests[i], R.rejected[i]
    print(f"   #{i:<3}{r.requester} ({r.dept}), {fmt_span(r.start, r.end)}, priority {r.priority}\n        [{code}] {msg}")

problems = verify_schedule(inv, reqs, R.accepted)
print("\n8. INDEPENDENT CHECK:", "schedule is valid - no double booking, every capacity/equipment/availability rule met"
      if not problems else f"PROBLEMS FOUND: {problems}")

# 5. online booking on top of the finished schedule --------------------------------------------
print("\n9. ONLINE BOOKING ON TOP OF THE SCHEDULE (one request at a time)")
bs = CampusBookingSystem(inv); bs.load(reqs, R.accepted)
B = BookingRequest
tries = [
    B(101, "Dr. S. Gupta", "CSE", "classroom", at("Mon", "09:00"), at("Mon", "10:00"), 5, 30, frozenset(), "CR-101", "Extra class"),
    B(102, "Dr. S. Gupta", "CSE", "classroom", at("Mon", "10:00"), at("Mon", "11:00"), 5, 30, frozenset(), "CR-101", "Extra class"),
    B(103, "Robotics Club", "Student Clubs", "lab", at("Thu", "10:00"), at("Thu", "12:00"), 4, 30, frozenset({"computers"}), None, "Workshop"),
    B(104, "Drama Club", "Student Clubs", "seminar_hall", at("Fri", "10:00"), at("Fri", "12:00"), 3, 400, frozenset(), None, "Play rehearsal"),
]
for r in tries:
    ok, rid, why = bs.request(r)
    print(f"   #{r.id} {r.requester}, {r.res_type} {fmt_span(r.start, r.end)}: " + (f"ACCEPTED on {rid}" if ok else f"REJECTED [{why[0]}] {why[1]}"))

# 6. save --------------------------------------------------------------------------------------
with open("sample_allocation_result.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["request_id", "requester", "dept", "resource_type", "start", "end", "priority", "status", "resource", "reason_code", "reason"])
    for r in reqs:
        acc = r.id in R.accepted
        code, msg = ("", "") if acc else R.rejected[r.id]
        w.writerow([r.id, r.requester, r.dept, r.res_type, fmt_time(r.start), fmt_time(r.end), r.priority,
                    "ACCEPTED" if acc else "REJECTED", R.accepted.get(r.id, ""), code, msg])
print("\nWrote sample_allocation_result.csv (SAMPLE data results)")
