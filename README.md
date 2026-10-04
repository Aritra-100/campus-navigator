# AI Campus Route Navigator — CU Technology Campus

Assignment X_03 · AI/ML Laboratory · B.Tech. 5th Semester

An AI-based campus navigation system. The satellite map is converted into a
weighted graph (`campus.json`) and solved by two agents written from scratch:

| Agent | Algorithm | Priority |
|-------|-----------|----------|
| **PATHFINDER** | Greedy Best-First Search | f(n) = h(n) |
| **ORBIT** | A* Search | f(n) = g(n) + h(n) |

No pathfinding library is used; `heapq` is only the priority queue.

## Project structure

```
campus-navigator/
├── main.py          user interface (interactive CLI, --experiments mode)
├── campus_map.py    Location + CampusMap classes: nodes, edges, weights, heuristic, JSON loading
├── search.py        Greedy Best-First, A*, and the CSE routing rule (CSERule)
├── agents.py        PATHFINDER and ORBIT (OOP agents)
├── experiment.py    route experiments, statistics, writes results.csv
├── campus.json      the campus graph (data, not code)
├── results.csv      experiment results (generated)
├── REPORT.md        brief report (also provided as REPORT.pdf)
└── README.md
```

## How to run

Requires Python 3.8+ and nothing else (standard library only).

```bash
python main.py                  # interactive: enter start and destination
python main.py --experiments    # run all experiments, write results.csv
python main.py --map other.json # use a different campus file
```

Location names are case-insensitive and accept short aliases (`Library`,
`CSE Lab`, `G1`, `Lift`, ...). Type `list` at a prompt to see every location.

Example:

```
Enter starting location: Entry Gate 1
Enter destination: CSE Laboratory

PATHFINDER
Route:
Entry Gate 1 → Auditorium Hall → Garden Area → Lift Area → Tower 2 Front Entry → Lift Area → CSE Laboratory
Cost: 573 m
Nodes explored: 10
...
ORBIT
Route:
Entry Gate 1 → Auditorium Hall → Garden Area → Lift Area → Tower 2 Rear Entry → Lift Area → CSE Laboratory
Cost: 403 m
Nodes explored: 16
```

## Design decisions

**Graph (`campus.json`).** 21 nodes — only the locations printed on the given
map (no new locations) — and 34 undirected walkable edges. Weights are my
estimated walking distances in metres. Each node also stores approximate map
coordinates (metres from the map's top-left corner).

**Entry gates.** The map labels four gate markers G1–G4 (several carry the
same printed text), so they are modelled as `Entry Gate 1` … `Entry Gate 4`
by marker letter.

**Heuristic.** h(n, goal) = straight-line distance between the two nodes'
coordinates. Every edge weight is ≥ the straight-line distance between its
endpoints, so h never overestimates (admissible and consistent) — checked
programmatically for all node pairs. Both agents use exactly the same
`CampusMap.heuristic`. Hand-assigned values per goal can be added under
`heuristic.overrides` in `campus.json`.

**CSE routing rule (`search.CSERule`).** The search state is
`(location, mode)`, and the rule is applied when neighbouring states are
generated:

| Mode | Meaning | Allowed next moves |
|------|---------|--------------------|
| `NORMAL` | ordinary campus | anything except a CSE place; entering Lift Area from a Tower 2 entry gives `LIFT_IN` |
| `LIFT_IN` | at Lift Area, arrived from a Tower 2 entry | CSE places (→ `IN_CSE`) or back out |
| `IN_CSE` | inside the CSE zone | only CSE places, or Lift Area (→ `LIFT_OUT`) |
| `LIFT_OUT` | at Lift Area, coming out of CSE | only Tower 2 Front/Rear Entry (→ `NORMAL`) |

So `Lift → CSE Laboratory → Garden → Library` is rejected, and reaching a CSE
place from Library/Garden requires going through a Tower 2 entry first.
Starting inside the zone puts the agent in `IN_CSE`; starting at Lift Area
counts as standing at the gateway (`LIFT_IN`).

**Nodes explored** = number of states expanded (popped from the frontier).
**Time** in `results.csv` is the average of 200 runs per agent per problem
(single runs take only microseconds).

## Verification

Results were cross-checked by an independent Dijkstra over the same rule:
ORBIT's cost equals the true optimum on all 18 problems, every returned path
satisfies the CSE rule, and the heuristic is admissible.

See `REPORT.md` for results and observations.
