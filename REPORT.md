---
title: "AI Campus Route Navigator — Brief Report"
subtitle: "Assignment X_03 · AI/ML Laboratory · B.Tech. 5th Semester"
---

## 1. Approach

The CU Technology Campus map was converted into a weighted graph stored in `campus.json` (21 locations taken only from the map, 34 walkable edges, weights = estimated walking distance in metres, plus approximate coordinates). Two agents search this graph:

- **PATHFINDER** — Greedy Best-First Search, f(n) = h(n)
- **ORBIT** — A* Search, f(n) = g(n) + h(n)

Both share one heuristic: straight-line distance between node coordinates. Since every edge weight is at least the straight-line distance of its endpoints, h is admissible and consistent (verified for all node pairs). The special CSE rule (Tower 2 entry → Lift Area → CSE places, and the reverse on exit) is enforced while generating neighbours: the search state is (location, mode), so the same location can be reached in different modes. The code is split into `campus_map.py`, `search.py`, `agents.py`, `experiment.py` and `main.py`; the graph and results live in `campus.json` and `results.csv`.

## 2. Experiment

18 source–destination pairs (10 ordinary, 8 CSE-related) were run on both agents (full table in `results.csv`). Each result was verified against an independent Dijkstra search under the same rule.

| Route | PATHFINDER cost / explored | ORBIT cost / explored | Same route? |
|---|---|---|---|
| Reception → Library | 265 m / 4 | 265 m / 6 | Yes |
| Canteen → New Building 2 | 230 m / 4 | 230 m / 5 | Yes |
| Library → Canteen | 300 m / 5 | 300 m / 15 | Yes |
| Playground → New Building 1 | 405 m / 6 | **348 m** / 10 | No |
| New Building 2 → Parking Area | 288 m / 6 | **233 m** / 6 | No |
| Entry Gate 1 → CSE Laboratory | 573 m / 10 | **403 m** / 16 | No |
| Auditorium Hall → CSE_AKC Seminar Hall | 316 m / 9 | 316 m / 13 | Yes |
| Library → CSE_AKC Seminar Hall | 153 m / 7 | 153 m / 6 | Yes |
| Parking Area → CSE_Reflxon Room | 273 m / 11 | **218 m** / 7 | No |
| CSE Laboratory → Canteen | 435 m / 9 | **428 m** / 17 | No |
| CSE_Reflxon Room → Library | 205 m / 5 | **193 m** / 6 | No |
| CSE_AKC Seminar Hall → Entry Gate 2 | 441 m / 8 | **411 m** / 12 | No |

(Rows where both agents agree and nothing differs — e.g. Garden Area → Power Area, Entry Gate 2 → Playground — are in `results.csv`.)

**Summary over all 18 problems:** the routes differ in 7; Greedy was costlier than A* in exactly those 7 (by 7 m to 170 m, i.e. 1.6 % to 42 %); A* was never worse. Total nodes explored: PATHFINDER 110, ORBIT 168. Average runtime per query: PATHFINDER about 13 µs, ORBIT about 22 µs.

## 3. Observations

**1. Does Greedy Best-First always find the shortest route?** No. It found the shortest route in 11 of 18 problems, but in 7 it returned a longer one — for example 573 m instead of 403 m for Entry Gate 1 → CSE Laboratory. It always finds *a* route here, but optimality is not guaranteed.

**2. How does A\* use the distance already travelled?** A* ranks each node by g(n) + h(n), so a node that looks close to the goal but was expensive to reach is penalised. It can also replace a stored route to a node when it finds a cheaper one. Because h is admissible, this made ORBIT optimal in all 18 experiments.

**3. When do the two agents choose different paths?** When the node that *looks* closest is reached by an expensive edge. The clearest case is Tower 2 Front Entry vs Rear Entry: the Front Entry is geometrically closer to the CSE rooms and to the Playground/Parking side, so Greedy picks it — but the Front Entry → Lift Area link is a long 125 m corridor, whereas the Rear Entry → Lift Area link is only 40 m. This one effect explains the different routes in Entry Gate 1 → CSE Laboratory, Parking Area → CSE_Reflxon Room and New Building 2 → Parking Area. Playground → New Building 1 is the opposite mistake: Greedy walks round via Parking, Rear Entry and Library (405 m) while A* takes the shorter Front Entry–Lift–Garden line (348 m).

**4. How does the heuristic affect their behaviour?** Straight-line distance ignores walls, buildings and winding paths. Greedy trusts it completely, so it is fast (fewest expansions overall) but is misled whenever the real path bends. A* is protected by g(n) but pays for it by expanding more nodes (168 vs 110 in total): it keeps checking alternatives whose f-value is still lower. A* was occasionally cheaper to run too (Library → CSE_AKC: 6 vs 7; Parking → CSE_Reflxon: 7 vs 11 expansions), when Greedy chased a misleading node. So a good heuristic speeds up both; a misleading one hurts Greedy's *answer*, not just its speed.

**5. What happens when the CSE constraint restricts possible routes?** The agents disagreed far more often on CSE routes (5 of 8 problems) than on ordinary ones (2 of 10), because the rule removes shortcuts and creates forced detours: an agent must pass Tower 2 Front/Rear Entry → Lift Area to get in, and Lift Area → Tower 2 Entry on the way out. Coming from Garden or Library, the shortest legal route can even pass Lift Area twice (Garden → Lift → Tower 2 Rear → Lift → CSE), since Lift Area entered from Garden does not count as an entry. In such cases the straight-line heuristic is further from the real cost (it ignores the forced detour), so Greedy is misled more easily — it chose the 125 m Front Entry corridor — while A* corrects for it. Tight restrictions (e.g. CSE Laboratory → CSE_Reflxon Room, 45 m) leave one sensible route and both agents agree.

## 4. Answer to the central question

*Does the path that looks closest to the destination also produce the best route?* **Not reliably.** In 7 of 18 trials the node that looked closest led to a longer overall walk. Looking closest (h) is only part of the story; the cost already paid (g) matters too, and A* — which uses both — found the best route every time.

## 5. Limitations

Edge weights and coordinates are estimates read from the satellite map and my understanding of the layout, not surveyed distances, and different weights could change which problems show a difference. Runtimes are micro-second scale on a 21-node graph, so the node counts are a more meaningful measure of effort than time.
