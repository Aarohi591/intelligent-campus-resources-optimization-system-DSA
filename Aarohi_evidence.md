# Evidence

**Project:** Intelligent Campus Resources Optimization System
**Student:** Aarohi Yadav · 0251cse364 / 2501330100003 · B.Tech CSE-A, Semester III
**Course:** Data Structures and Algorithms II (CCSE0301) · Faculty: Mr. Shamshad Ali
**SDG:** SDG 4, Quality Education
**Review:** 1 · Month 1

---

## 1. Papers Currently Cited in the Report

| # | Paper | Link | Role |
|---|---|---|---|
| 1 | Dynamic Algorithms for Interval Scheduling on a Single Machine. arXiv preprint. | https://arxiv.org/ (search the exact title) | Cited in report — interval storage in a BST |
| 2 | Graph Coloring based Optimized Algorithm for Resource Utilization in Examination Scheduling. *Applied Mathematics & Information Sciences*. | Search the title on the journal site | Cited in report — conflict graph and colouring |

**What each gave the project:**

**Paper 1** stores bookings as intervals in a binary search tree, so that clashing and compatible requests can be found and updated without rescanning everything. This is the direct source for using a tree to hold resource records.

**Paper 2** models rooms, teachers and time slots as a graph-colouring problem, where two events that cannot share a slot are joined by an edge. This is the direct source for treating clashing requests as a conflict graph.

> ⚠️ **Complete these two citations before submission.** Both are missing author names, year, volume and page numbers. Retrieve the full record from the publisher page. An incomplete citation in a reference list is an easy mark to lose.

---

## 2. Missing: a 2026 Base Paper

The report currently has no paper published in 2026. If Mr. Ali requires a recent base paper, as he did for other projects in this section, one of these fits the topic:

| Paper | Link | Note |
|---|---|---|
| Maliakal, J., Mustafa, M. A., Alnuaimi, N., Latif, O. A., & Almobaideen, W. (2026). Automating University Course Scheduling Using Genetic Algorithm. *Information System Design: AI and ML Applications*, LNNS vol. 1565, Springer. | https://doi.org/10.1007/978-981-95-0375-9_12 | **Best fit.** Explicitly about manual scheduling causing double-booked classrooms and underutilised rooms, which matches this project's problem statement. Likely paywalled — try campus wifi. |
| Balan, I., & Vlad, S. (2026). A Solution to University Course Timetabling Problem Using Genetic Algorithms. *Proceedings of IE 2025*, SIST vol. 471, Springer. | https://doi.org/10.1007/978-981-95-6136-0_32 | Room allocation by size and equipment type. Also Springer, likely paywalled. |

**A gap that would work against the Maliakal paper:** genetic-algorithm timetabling optimises an entire timetable in one batch, computed once before the semester. A campus resource system handles requests arriving one at a time, all through the term, each needing an immediate yes or no. The batch approach says nothing about the incremental case, and the incremental case is where searchable trees and a priority queue actually matter.

That is a genuine gap, it is different from the one currently in the report, and it points directly at the structures already chosen.

---

## 3. Books

| Book | Used for |
|---|---|
| Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to Algorithms* (4th ed.). MIT Press. | Heap operations, AVL rotations, graph representations |
| NIET DSA-II course material, Unit 1 (Trees) and Unit 2 (Graphs) | All base definitions |

---

## 4. Online Resources

| Resource | Link | Used for |
|---|---|---|
| | | |

> Fill this in with what was actually used, or delete the section. Do not list a resource that cannot be discussed in a viva.

---

## 5. Video Lectures

| Source | Link | Used for |
|---|---|---|
| | | |

> Same rule. Add the channels actually watched, with links, or leave it empty.

---

## 6. What Each Source Contributed

| Idea in the report | Came from |
|---|---|
| Bookings stored as intervals in a searchable tree | Paper 1 (interval scheduling) |
| Two clashing requests joined by an edge | Paper 2 (graph colouring) |
| BST ordered by resource ID for search, insert, delete | Course material Unit 1 |
| AVL keeps records balanced as bookings grow | Course material Unit 1; Cormen |
| Min Heap picks the earliest-deadline or highest-priority request | Course material Unit 1 |
| Priority queue holds requests still waiting for assignment | Course material Unit 1 |
| Inorder traversal lists records in sorted order | Course material Unit 1 |
| Adjacency List suits the sparse conflict graph | Course material Unit 2 |
| Adjacency Matrix rejected: O(V²) on sparse data | Own reasoning |
| **The research gap (interval storage and priority order never joined)** | **Own reading of Papers 1 and 2** |

---

## 7. Repository

| | |
|---|---|
| **GitHub** | `https://github.com/________/campus-resource-optimization` — fill in, then paste into Field 9 of the report |
| **Contains** | Research papers and this evidence file now; allocation code, diagrams and test outputs from Review 2 onwards |

---

## 8. Before Submission

- [ ] Complete the two citations in Section 1 with author, year, volume and pages
- [ ] Decide whether a 2026 base paper is required; if so, add one from Section 2
- [ ] Fill in or delete Sections 4 and 5
- [ ] Paste the GitHub link into Field 9 of the report
- [ ] Fill the **AI Tool Usage Declaration** (section F of the assignment brief)
- [ ] Read the report aloud once and change anything that does not sound like your own voice

---

*Last updated: Month 1 / Review 1. Extended at each review as new sources are used.*
