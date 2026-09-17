# Project Description

## Intelligent Campus Resources Optimization System

**Student:** Aarohi Yadav
**ERP ID / Roll No.:** 0251cse364 / 2501330100003 · **Section:** CSE-A · **Semester:** III
**Course:** Data Structures and Algorithms II (CCSE0301)
**Faculty:** Mr. Shamshad Ali
**Institute:** NIET Greater Noida
**Domain:** Educational Technology / Resource Management
**SDG Alignment:** SDG 4, Quality Education
**Review Stage:** Review 1 · Month 1 · **Progress: 25%**

---

## 1. Overview

Every college runs on a small set of shared things that a large number of people want at the same time. Classrooms, laboratories, projectors, seminar halls, sports equipment. There is never enough of any of them during the hours everybody wants them.

This project builds a system that decides who gets what. A request arrives naming a resource and a time window. The system has to answer three questions quickly: does that resource exist and is it free, does this request clash with anything already booked, and if two valid requests want the same thing, which one wins.

Underneath the scheduling problem, the subject of study is the data structures that make those three answers fast. A booking system that takes a minute to answer is useless, and the reason it would take a minute is almost always the structure holding the data rather than the logic on top of it.

---

## 2. Background and Motivation

### 2.1 How this is actually done now

Most departments keep bookings in a register, a shared spreadsheet, or a WhatsApp group. Somebody wants Lab 3 on Thursday afternoon, so somebody else scrolls through the sheet looking for Thursday, reads the entries for Lab 3, and decides by eye whether there is a clash.

This works while the number of bookings is small. It stops working for reasons that are worth naming precisely:

**Checking is linear.** To confirm a new request is safe, every existing booking for that resource has to be read. With 50 bookings that is 50 comparisons and takes a few seconds. With 5,000 it is 5,000 comparisons every single time, done by a human.

**Clashes get missed.** Two people can be editing the same sheet, or two departments can book the same hall through different channels. Nobody finds out until both groups arrive.

**Nothing decides priority.** When the Physics department and a student club both want the seminar hall at 2 p.m. on Friday, a register has no rule. Whoever asked the person in charge first, or whoever asked more insistently, gets it.

**Resources sit idle.** A lab booked from 10 to 11 and again from 12 to 1 has an hour free in the middle that nobody can see without reading the whole sheet.

### 2.2 The three problems underneath

Strip away the campus context and three computational problems remain.

**Finding a record.** Given a resource ID, retrieve its details and its bookings. Scanning a flat list is O(n) and gets worse every time a booking is added.

**Detecting a clash.** Two bookings clash when they want the same resource and their time windows overlap. This is a relationship between two requests, not a property of either one alone.

**Deciding priority.** When several requests are valid but compete for the same slot, something has to rank them and repeatedly produce the top one.

The first is a searching problem, which points to trees. The second is a relationship problem, which points to graphs. The third is a priority problem, which points to heaps. Those are Unit 1 and Unit 2 of this course, which is why the topic fits.

---

## 3. Why This Topic

Sorting an array of numbers is a fine way to learn a concept, but the cost of choosing badly never shows, because everything finishes instantly at the sizes used in class.

Campus booking is different in a way that is easy to feel. If the clash check is a linear scan, the system slows down in exact proportion to how successful it is. The more the college uses it, the more bookings it holds, and the slower every new request becomes. A structure that is wrong does not fail immediately; it fails later, when it matters, which is the harder failure to design against.

---

## 4. Research Work Completed

Month 1 was spent reading rather than building.

### 4.1 Paper 1 — interval storage

**Dynamic Algorithms for Interval Scheduling on a Single Machine** (arXiv preprint)

This paper treats each booking as an interval on a timeline and stores those intervals in a binary search tree. Because the tree is ordered, a new interval can be checked against the existing ones without scanning all of them, and the structure can be updated as intervals are added and removed rather than rebuilt from scratch.

**What it gave this project:** the idea that a booking is an interval, and that intervals belong in a searchable tree rather than a list.

### 4.2 Paper 2 — conflict as a graph

**Graph Coloring based Optimized Algorithm for Resource Utilization in Examination Scheduling** (*Applied Mathematics & Information Sciences*)

This paper models exam scheduling as a graph-colouring problem. Rooms, teachers and time slots become vertices, and an edge joins two things that cannot happen simultaneously. Assigning colours so that no two adjacent vertices share one is the same as assigning time slots so that no two conflicting events collide.

**What it gave this project:** the idea that a clash is an edge, and that the set of all clashes is a graph.

### 4.3 The gap

Read together, the two papers each solve half of the problem and neither solves the half the other left.

The interval-scheduling work stores bookings efficiently and finds clashes quickly, but it treats every request as equal. It answers *can this be scheduled* and never *should this one get it instead of that one*.

The graph-colouring work resolves clashes correctly, but colouring is a symmetric operation. Two adjacent vertices simply need different colours; the method has no notion that one of them matters more. In exam scheduling that is fine, because exams are not in competition with each other. In campus resource booking it is not fine, because requests genuinely compete and somebody has to lose.

**Neither joins a searchable interval store to a priority order for deciding who wins.** That join is what this project examines.

This is a modest gap and it is stated as one. Both papers are solving harder problems than this project attempts. What is missing is the combination, and the combination is exactly where a tree, a graph and a heap have to work together, which makes it a suitable subject for this course.

> **Note on the literature.** Both citations currently lack full bibliographic details, and neither paper is from 2026. If a recent base paper is required, Maliakal et al. (2026), *Automating University Course Scheduling Using Genetic Algorithm* (Springer, LNNS 1565, doi:10.1007/978-981-95-0375-9_12) is the closest fit, and a gap against it would be that genetic-algorithm timetabling optimises a whole term in one batch while a campus booking system must answer requests arriving one at a time.

---

## 5. Proposed Work

The system holds three structures that each answer one of the three questions from Section 2.2.

**A searchable resource index.** Resource records held in a balanced tree keyed on resource ID, so lookup stays fast as the number of resources and bookings grows.

**A conflict graph.** Requests as vertices, an edge between any two that want the same resource in overlapping time. Traversal over this graph answers which requests are mutually incompatible.

**A priority queue of pending requests.** A min heap keyed on deadline or priority score, so the request that should be served next is available immediately.

The comparisons to be measured:

- A flat list of bookings against a balanced tree, for clash checking as booking count grows
- An unbalanced BST against an AVL tree, on resource IDs inserted in sequential order
- A linear scan of pending requests against a heap, for repeatedly selecting the next request

**What this project does not claim.** It is not an optimisation algorithm and does not compete with genetic-algorithm timetabling. It does not produce a globally optimal timetable. It handles requests incrementally and studies the structures that make that practical.

---

## 6. System Model

### 6.1 Entities

**Resource.** Resource ID, type (classroom, lab, hall, equipment), capacity, location.

**Booking.** Booking ID, resource ID, start time, end time, requester, department.

**Request.** Request ID, resource ID or type, desired start and end time, requester, department, priority score, deadline.

### 6.2 The clash rule

Two bookings on the same resource, with intervals [s₁, e₁] and [s₂, e₂], **clash if and only if**:

```
s₁ < e₂  AND  s₂ < e₁
```

Both conditions must hold. Worked through:

| Booking A | Booking B | s₁ < e₂ | s₂ < e₁ | Clash? |
|---|---|---|---|---|
| 10:00–11:30 | 11:00–12:00 | 10:00 < 12:00 ✓ | 11:00 < 11:30 ✓ | **Yes** |
| 10:00–11:00 | 11:00–12:00 | 10:00 < 12:00 ✓ | 11:00 < 11:00 ✗ | No |
| 09:00–10:00 | 14:00–15:00 | 09:00 < 15:00 ✓ | 14:00 < 10:00 ✗ | No |

Note the second row. Bookings that touch at the boundary do not clash, because one ends exactly as the other begins. Getting this boundary right matters; using ≤ instead of < would wrongly reject back-to-back classes, which are the normal case in a timetable.

### 6.3 Workflow

1. A request arrives
2. Look up the resource in the index
3. Retrieve that resource's existing bookings
4. Apply the clash rule against each candidate
5. If no clash, confirm the booking and insert it into the index
6. If there is a clash, add an edge in the conflict graph and place the request in the priority queue
7. When a slot frees, remove the highest-priority pending request from the queue and retry it

Steps 2, 4 and 7 are the operations this project measures.

---

## 7. The DSA Concepts, Explained

### 7.1 The flat list, and why it is the baseline

The simplest booking store is a list. Adding a booking is O(1). Checking a new request means comparing it against every existing booking for that resource, which is O(n).

With 5,000 bookings, one clash check is 5,000 comparisons. If the system handles 200 requests in a day, that is a million comparisons spent on checking alone. The list is included as the control that everything else is measured against.

### 7.2 Binary search tree

A BST keeps records ordered: for any node, everything in the left subtree is smaller and everything in the right is larger. Searching compares and goes left or right, halving the remaining space each step, which gives O(log n) when the tree is balanced.

Resource records are keyed on resource ID. Searching for R104 in a balanced tree of 1,000 resources takes about 10 comparisons instead of 1,000.

**Where it breaks.** A BST does not balance itself, and resource IDs are assigned sequentially. Inserting R101 through R107 in order:

```
R101
   \
    R102
       \
        R103
           \
            R104
               \
                R105
                   \
                    R106
                       \
                        R107
```

Height 6 instead of 2. Searching for R107 takes 7 comparisons rather than 3. The tree has become a linked list carrying extra pointers.

This is not a rare worst case. IDs are almost always issued in sequence, so sorted insertion is the normal case for this project, which is precisely why the next structure is needed.

### 7.3 AVL tree

An AVL tree is a BST that keeps itself balanced. Every node tracks the height difference between its left and right subtrees. When that difference reaches 2, a rotation restores balance.

The same records inserted into an AVL tree:

- Insert R101, R102. Inserting R103 unbalances R101, rotate left, root becomes R102.
- Insert R104, R105. Imbalance at R103, rotate left, subtree becomes R104 with children R103 and R105.
- Insert R106. Imbalance at R102, rotate left, root becomes R104.
- Insert R107. Imbalance at R105, rotate left, subtree becomes R106 with children R105 and R107.

```
          R104
        /      \
     R102      R106
     /   \     /   \
  R101 R103 R105  R107
```

Height 2. Searching for R107 is now 3 comparisons. At 100,000 booking records the difference is 100,000 comparisons against about 17.

**What a rotation costs.** It relinks three pointers and takes constant time. At most two rotations are needed after any single insertion, so the balancing overhead is small compared with what it saves.

**The four cases.** LL and RR need one rotation each. LR and RL need two, because the inner child has to be rotated into position first.

### 7.4 Min heap and the priority queue

When several valid requests compete for the same resource, something has to decide the order. A min heap keyed on deadline, or on a priority score where a lower number means higher priority, answers that.

A min heap is a complete binary tree where **every parent is less than or equal to both its children**. The smallest element is therefore always at the root and readable in O(1).

It is stored as a plain array with no pointers:

```
parent(i) = (i - 1) / 2
left(i)   = 2i + 1
right(i)  = 2i + 2
```

**Insertion.** Place the new request at the end, then sift up: compare with the parent and swap while it is smaller. Inserting priority scores 5, 2, 8, 1, 6, 3:

| Step | Action | Array after |
|---|---|---|
| 1 | insert 5 | `[5]` |
| 2 | insert 2, swap with 5 | `[2, 5]` |
| 3 | insert 8, no swap | `[2, 5, 8]` |
| 4 | insert 1, swaps twice to the root | `[1, 2, 8, 5]` |
| 5 | insert 6, no swap (6 > 2) | `[1, 2, 8, 5, 6]` |
| 6 | insert 3, swaps once with 8 | `[1, 2, 3, 5, 6, 8]` |

As a tree:

```
            1
          /   \
         2     3
        / \   /
       5   6 8
```

**Extract-min.** Take the root, move the last element into its place, then sift down while a child is smaller. Removing 1: element 8 moves to the root, compares with children 2 and 3, swaps with 2; then compares with children 5 and 6, swaps with 5. Result `[2, 5, 3, 8, 6]`, new minimum 2.

**Why O(log n).** A complete binary tree of n nodes has height ⌊log₂ n⌋, and each swap moves one level, so both operations touch at most log₂ n elements. With 5,000 pending requests, that is about 12 comparisons against a linear scan's 5,000.

**Build-heap is O(n), not O(n log n).** Building a heap from n unsorted requests by sifting down from the middle of the array costs Θ(n), because most nodes sit near the leaves where sift-down has almost nowhere to travel. Only the root can travel the full height.

**Why not a max heap.** It is the same structure reversed. Which one to use depends purely on what "first" means. If priority is scored so that 1 is most urgent, a min heap is correct. If it is scored so that 10 is most urgent, a max heap is correct. The choice must follow the scoring convention, and this project uses lower-is-more-urgent.

### 7.5 Tree traversals

Using the AVL tree from 7.3:

| Traversal | Order | Result | Use here |
|---|---|---|---|
| Inorder (L, N, R) | left, node, right | R101 … R107 | Lists resources in sorted ID order for reports |
| Preorder (N, L, R) | node, left, right | R104, R102, R101, R103, R106, R105, R107 | Saving or transmitting the index structure |
| Postorder (L, R, N) | left, right, node | R101, R103, R102, R105, R107, R106, R104 | Freeing child records before the parent |
| Level order | by depth | R104, R102, R106, R101, R103, R105, R107 | Inspecting the tree shape when debugging balance |

Inorder is the one this project relies on, because a sorted list of resources and their bookings is what an administrator actually wants to read.

### 7.6 The conflict graph

A graph is a set of vertices and edges. Here each **request** is a vertex, and an edge joins two requests that want the same resource in overlapping time.

Five requests for Seminar Hall A:

| Request | Time |
|---|---|
| R1 | 09:00 – 10:00 |
| R2 | 09:30 – 10:30 |
| R3 | 10:00 – 11:00 |
| R4 | 10:45 – 11:45 |
| R5 | 09:15 – 09:45 |

Applying the clash rule to every pair gives these edges:

- R1 – R2 (09:00 < 10:30 and 09:30 < 10:00)
- R1 – R5 (09:00 < 09:45 and 09:15 < 10:00)
- R2 – R3 (09:30 < 11:00 and 10:00 < 10:30)
- R2 – R5 (09:30 < 09:45 and 09:15 < 10:30)
- R3 – R4 (10:00 < 11:45 and 10:45 < 11:00)

R1 and R3 do **not** clash, because R1 ends exactly as R3 begins.

```
   R5 ──── R1
    \      |
     \     |
      R2 ──┘
       |
      R3 ──── R4
```

Degrees: R1 = 2, R2 = 3, R3 = 2, R4 = 1, R5 = 2. Total 10, which is twice the 5 edges, as it should be.

### 7.7 Graph colouring on that example

Assigning time slots so no two clashing requests share one is exactly graph colouring, which is where Paper 2 connects.

Colouring the graph above, starting with the highest-degree vertex:

| Request | Slot |
|---|---|
| R2 (degree 3) | Slot A |
| R1 (adjacent to R2) | Slot B |
| R5 (adjacent to R1 and R2) | Slot C |
| R3 (adjacent to R2 only) | Slot B |
| R4 (adjacent to R3 only) | Slot A |

**Three slots are enough.** R1 and R3 share Slot B safely because there is no edge between them, and R2 and R4 share Slot A for the same reason. A naive approach that gave every request its own slot would use five.

This is where the gap becomes visible. Colouring tells us three slots suffice. It does not tell us which request should get the earliest slot when a department needs it most. That decision needs the priority queue from 7.4, and joining the two is the project.

### 7.8 Adjacency list against adjacency matrix

**Adjacency matrix.** A V × V table where entry [i][j] says whether an edge exists. Edge lookup is O(1). Space is O(V²) regardless of how many edges actually exist.

**Adjacency list.** Each vertex stores a list of its real neighbours. Space is O(V + E).

For the 5-request example: a matrix is 25 entries holding 5 edges. A list holds 10 directed entries. Already wasteful, and it gets worse with scale:

| Requests per term | Matrix entries | Matrix memory (1 byte each) | List entries (≈6 clashes each) |
|---|---|---|---|
| 500 | 250,000 | 0.25 MB | ~3,000 |
| 2,000 | 4,000,000 | 4 MB | ~12,000 |
| 10,000 | 100,000,000 | **100 MB** | ~60,000 |

The conflict graph is **sparse**. Most requests do not clash with most other requests, because they are for different resources or different days. A request typically conflicts with a handful of others, not with thousands. The matrix reserves space for every possible clash and stores almost nothing in it.

That is why this project uses an adjacency list. The matrix's O(1) edge lookup is real, but the access pattern here is "list everything this request conflicts with", which the list answers directly.

### 7.9 BFS and DFS

Both visit every vertex and edge once, giving O(V + E) with an adjacency list. They differ in order, and each answers a different question about the conflict graph.

**BFS** uses a queue and explores level by level. Starting from one request, it finds everything directly clashing with it, then everything clashing with those. This identifies a connected group of mutually entangled requests that must be resolved together.

**DFS** uses a stack and goes deep before backtracking. It is the natural way to find all connected components, so the full set of requests can be split into independent groups that can be scheduled separately without affecting each other.

Splitting the problem into components matters, because a hundred requests forming twenty independent groups is twenty small problems rather than one large one.

### 7.10 Summary

| DSA Topic | Best case | Worst case | Useful? | Role in this project |
|---|---|---|---|---|
| Binary Tree | O(n) | O(n) | No | Represents hierarchy; no ordering, so search stays linear |
| BST | O(log n) | O(n) | Yes | Search, insert and delete resource records by ID |
| AVL Tree | O(log n) | O(log n) | Yes | Keeps records balanced when IDs arrive in sequence |
| Min Heap | O(1) get min | O(log n) | Yes | Picks the earliest-deadline or highest-priority request |
| Priority Queue | O(1) peek | O(log n) | Yes | Holds pending requests awaiting assignment |
| Tree Traversal | O(n) | O(n) | Support | Inorder lists records sorted; used for reports |
| Graph | O(V+E)* | O(V+E)* | Yes | Requests as vertices, time overlaps as edges |
| Adjacency List | O(V+E)* | O(V+E)* | Yes | Suits the large, sparse conflict graph |
| Adjacency Matrix | O(1) edge | O(1) edge | No | O(V²) space: 100 MB at 10,000 requests, mostly empty |

\* O(V+E) refers to BFS/DFS traversal using an adjacency list. Heap costs are per operation.

Deciding what does not fit took as much work as choosing what does. Rejecting the adjacency matrix rests on a space calculation, and rejecting the plain binary tree rests on the fact that it offers no ordering to search by.

---

## 8. Expected Outcomes

- A conceptual allocation model with a searchable resource index, a conflict graph and a priority queue
- A measured comparison of flat-list clash checking against tree-based checking as booking count grows
- A measured comparison of BST against AVL on sequentially assigned resource IDs
- A demonstration of conflict-graph construction and slot assignment on sample booking data
- Complexity tables, tree and graph diagrams, and timing charts supporting the above
- Clear reporting of the limits, including that this is incremental allocation and not global optimisation

---

## 9. Progress at Review 1, 25%

| # | Activity | Status |
|---|---|---|
| 1 | Problem selection and topic approval | Complete |
| 2 | Understanding campus resource allocation and its failure modes | Complete |
| 3 | Objectives and stakeholder identification | Complete |
| 4 | Literature review, two papers | Complete |
| 5 | Research gap identification | Complete |
| 6 | DSA-II Unit 1 (Trees) study | Complete |
| 7 | DSA-II Unit 2 (Graphs) study | Complete |
| 8 | Mapping DSA concepts to project operations | Complete |
| 9 | Initial data model for resources, bookings and requests | Complete |
| 10 | Implementation | Not started |
| 11 | Testing and measurement | Not started |
| 12 | Final analysis and report | Not started |

Nothing has been implemented. The 25% covers the reading, the gap, the structure selection and the conceptual model.

---

## 10. Remaining Work

**Review 2, to approximately 55%.** Finalise the resource and booking data model. Implement BST and AVL operations for the resource index and measure the difference on sequential IDs. Implement the clash rule and the conflict-graph construction with an adjacency list. Implement the min-heap priority queue. Test searching, clash detection and priority selection on sample data.

**Review 3, to approximately 80%.** Extend into Units 3 and 4. Apply dynamic programming to maximise resource utilisation across a day, which is close to a weighted interval scheduling problem. Use backtracking or branch-and-bound for slot assignment when the conflict graph is dense enough that greedy colouring is not good enough.

**Final, 100%.** Complete the structure comparisons at varying booking volumes. Compare the binary heap against the advanced heaps from Unit 5. Produce the full complexity analysis, charts and final report.

---

## 11. Scope and Limitations

- Incremental allocation, one request at a time, not global timetable optimisation
- No genetic algorithms, no machine learning
- Simulated booking data, not live college records
- Fixed resource list; no dynamic addition of new rooms mid-term
- Priority scoring is assumed to be given, not derived from institutional policy
- The study is of data structures for allocation, not of scheduling theory

---

## 12. References

1. Dynamic Algorithms for Interval Scheduling on a Single Machine. arXiv preprint. *(complete the author, year and identifier before submission)*
2. Graph Coloring based Optimized Algorithm for Resource Utilization in Examination Scheduling. *Applied Mathematics & Information Sciences*. *(complete the author, year, volume and pages)*
3. Maliakal, J., Mustafa, M. A., Alnuaimi, N., Latif, O. A., & Almobaideen, W. (2026). Automating University Course Scheduling Using Genetic Algorithm. *Information System Design: AI and ML Applications*, LNNS vol. 1565, Springer. https://doi.org/10.1007/978-981-95-0375-9_12
4. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to Algorithms* (4th ed.). MIT Press.
5. NIET DSA-II course material, Unit 1 (Trees) and Unit 2 (Graphs).

The complete source list is in `evidence.md`.

---

*Review 1 · Month 1 · Updated at the end of each review stage.*
