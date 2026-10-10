# Intelligent Campus Resources Optimization System (DSA-II, CCSE0301)

A Python prototype that allocates shared campus resources (classrooms, labs, projectors, sports facilities,
halls) to booking requests **without double booking**, and explains every rejection.

> **Data warning.** All inventory and booking data in this repository is **fictional sample data**
> (`sample_data.py`). No real campus data is used. The benchmark uses random synthetic requests.

## Setup
Standard library only (no `pip install` needed). Written and run with Python 3.12.3; the code uses nothing newer than
Python 3.7 features, but only 3.12.3 has been tested.
```
python --version
python tests.py        # correctness checks
python demo.py         # complete booking workflow on the sample campus
python bench.py        # algorithm benchmark on synthetic data (takes about a minute)
```

## Files
| File | Purpose |
|---|---|
| `campus.py` | All data structures and algorithms plus the booking workflow |
| `sample_data.py` | **Sample (fictional)** inventory, 24 sample requests, and a random request generator for stress tests |
| `demo.py` | Complete workflow on the sample data; writes `sample_allocation_result.csv` |
| `tests.py` | 59 checks: algorithms and booking rules |
| `bench.py` | Algorithm benchmark on **synthetic** data; writes `benchmark_results.csv` |
| `outputs/` | Saved console output of the three scripts from the last run |

Campus results (`demo.py`, `sample_allocation_result.csv`) and benchmark results (`bench.py`,
`benchmark_results.csv`) are kept separate on purpose: the first show the booking workflow on sample data,
the second only measures how fast and how good the algorithms are on random input.

## Features
* **Inventory** (`Inventory`, stored in an AVL tree): resource ID, type, capacity, availability (in service or not,
  daily opening hours, maintenance periods) and equipment.
* **Booking requests** (`BookingRequest`): requester, department, resource type, start, end, priority,
  required capacity, required equipment, optional specific resource.
* **Availability check** (`ResourceCalendar`): one calendar per physical resource; an overlapping booking on the
  same resource is always refused. Times are half-open `[start, end)`, so 09:00-10:00 and 10:00-11:00 do not clash.
* **Conflict graph**: requests that overlap in time and could use the same resource are joined by an edge.
* **Heap** (`RequestHeap`): serves competing requests highest priority first, best-fit room first (smallest room that suits).
* **Dynamic programming**: for each resource, re-picks the set of non-clashing bookings with the highest total priority.
  It is applied only when the total value strictly rises, so it never makes the heap result worse.
* **Graph colouring -> rooms**: flexible bookings (more than one suitable room) are coloured by time overlap
  (exact branch and bound for small groups, Welch-Powell otherwise) and mapped to real rooms **only if** one
  room suits every booking in the colour class and is free. Otherwise the existing assignment is kept.
* **Reasons**: every rejection has a code and a message: `TIME_CLASH`, `CAPACITY`, `EQUIPMENT`, `UNAVAILABLE`,
  `OUTSIDE_HOURS`, `INVALID_TIME`, `NO_RESOURCE_TYPE`, `BAD_PREFERENCE`.
* **Independent verification** (`verify_schedule`): re-checks a finished schedule for double booking and rule violations.
* **Online booking** (`CampusBookingSystem`): approve or reject one request at a time against the current schedule.

## Using it in code
```python
from campus import *
inv = Inventory([Resource("CR-101", "classroom", 60, equipment=frozenset({"projector"}))])
req = BookingRequest(1, "Dr. Rao", "CSE", "classroom", at("Mon", "09:00"), at("Mon", "10:00"),
                     priority=8, capacity=50, equipment=frozenset({"projector"}))
result = allocate_campus(inv, [req])
print(result.accepted, result.rejected)       # {1: 'CR-101'} {}
print(verify_schedule(inv, [req], result.accepted))   # [] means no problems
```

## Example output (from `python demo.py`, sample data)
```
4. ALLOCATION STAGES (value = sum of request priorities)
   heap, highest priority first : value  77  (12 bookings)
   + dynamic programming        : value  81
       DP re-planned AUD-1: 6 -> 10
   + room mapping and fill      : value  81  (13 bookings)  of 141 requested in total

   #5  Prof. T. Das (Mechanical), Mon 11:00-12:00, priority 6
        [CAPACITY] Insufficient capacity: CR-201 holds 120, needs 150 (3 classroom resources checked)
   #6  Dr. L. Fernandes (Civil), Mon 10:00-11:00, priority 5
        [EQUIPMENT] Required equipment not available: CR-201 lacks smartboard (3 classroom resources checked)
   #3  Dr. P. Nair (Maths), Mon 09:30-10:30, priority 7
        [TIME_CLASH] Time clash: CR-101 is booked Mon 09:00-10:00 by #1 (CSE, priority 9); all 2 suitable classroom resources are taken in this period
```

## How to verify
1. `python tests.py` must end with `59 / 59 tests passed` (exit code 0).
2. `python demo.py`: section 8 must say the schedule is valid; compare with `outputs/demo_output.txt`.
3. Open `sample_allocation_result.csv` and spot-check: no two ACCEPTED rows with the same resource overlap in time.
4. `python bench.py`: operation counts, heights and allocation values are repeatable (seeded). Timings in milliseconds
   change from machine to machine.

## Limitations
* Sample data only; there is no CSV/database import yet. Replace `sample_inventory()` / `sample_requests()` to use real data.
* With flexible requests the DP stage is a per-resource improvement that never lowers the value, **not** a guaranteed
  global optimum (that problem is NP-hard in general). When every request is pinned to one resource it is optimal
  (tested against an independent DP).
* In the sample, the colouring step keeps the same number of rooms (3 classrooms, 2 labs); it is a validity-checked
  re-packing, not a proven improvement.
* Priority is one integer per request. There is no fairness rule between departments, no recurring bookings, no
  set-up time between bookings, and no booking of two resources together (for example a room plus a portable projector).
* Times are minutes within one week (Mon-Sun). Nothing is stored between runs and it is not safe for concurrent users.
* `max_overlap()` counts overlap among the requests it is given, so pass it the requests for one resource.
