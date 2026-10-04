"""experiment.py - run both agents on many source/destination pairs and save results.csv."""

import csv

from agents import Pathfinder, Orbit

ORDINARY_PROBLEMS = [
    ("Reception", "Library"),
    ("Canteen", "New Building 2"),
    ("Library", "Canteen"),
    ("Entry Gate 1", "Library"),
    ("Entry Gate 4", "Canteen"),
    ("Playground", "New Building 1"),
    ("Entry Gate 3", "Reception"),
    ("New Building 2", "Parking Area"),
    ("Garden Area", "Power Area"),
    ("Entry Gate 2", "Playground"),
]
CSE_PROBLEMS = [
    ("Entry Gate 1", "CSE Laboratory"),
    ("Auditorium Hall", "CSE_AKC Seminar Hall"),
    ("Library", "CSE_AKC Seminar Hall"),
    ("Parking Area", "CSE_Reflxon Room"),
    ("CSE Laboratory", "Canteen"),
    ("CSE_Reflxon Room", "Library"),
    ("CSE_AKC Seminar Hall", "Entry Gate 2"),
    ("CSE Laboratory", "CSE_Reflxon Room"),
]
PROBLEMS = ORDINARY_PROBLEMS + CSE_PROBLEMS

FIELDS = ["Route", "Type", "Agent", "Path", "Cost (m)", "Nodes Explored",
          "Time (s)", "Max Frontier", "Same Path As Other Agent"]


def run_pair(campus, start, goal, repeats=200):
    """Run both agents once for the answer, then average the time over `repeats` runs."""
    results = {}
    for agent in (Pathfinder(campus), Orbit(campus)):
        res = agent.find_route(start, goal)
        total = 0.0
        for _ in range(repeats):
            total += agent.find_route(start, goal).time_s
        res.time_s = total / repeats
        results[agent.name] = res
    return results


def run_experiments(campus, problems=PROBLEMS, out_path="results.csv", repeats=200):
    cse_set = set(campus.cse_zone)
    rows, summary = [], []
    for start, goal in problems:
        pair = run_pair(campus, start, goal, repeats)
        kind = "CSE" if (start in cse_set or goal in cse_set) else "Ordinary"
        same = pair["PATHFINDER"].path == pair["ORBIT"].path
        for name in ("PATHFINDER", "ORBIT"):
            r = pair[name]
            rows.append({
                "Route": f"{start} -> {goal}",
                "Type": kind,
                "Agent": name,
                "Path": " > ".join(r.path) if r.found else "NO ROUTE",
                "Cost (m)": r.cost if r.found else "",
                "Nodes Explored": r.nodes_explored,
                "Time (s)": f"{r.time_s:.6f}",
                "Max Frontier": r.max_frontier,
                "Same Path As Other Agent": "Yes" if same else "No",
            })
        summary.append((start, goal, kind, pair, same))

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return summary


def print_summary(summary):
    """Compact comparison table on the console."""
    print(f"{'Route':<52}{'Type':<9}{'PF cost':>8}{'OR cost':>8}{'PF exp':>7}{'OR exp':>7}  Same?")
    print("-" * 100)
    for start, goal, kind, pair, same in summary:
        pf, orb = pair["PATHFINDER"], pair["ORBIT"]
        label = f"{start} -> {goal}"
        print(f"{label:<52}{kind:<9}{pf.cost:>8.0f}{orb.cost:>8.0f}"
              f"{pf.nodes_explored:>7}{orb.nodes_explored:>7}  {'Yes' if same else 'NO'}")

    diff = [s for s in summary if not s[4]]
    worse = [s for s in summary if s[3]["PATHFINDER"].cost > s[3]["ORBIT"].cost]
    total_pf = sum(s[3]["PATHFINDER"].nodes_explored for s in summary)
    total_or = sum(s[3]["ORBIT"].nodes_explored for s in summary)
    print("-" * 100)
    print(f"Problems: {len(summary)} | different routes: {len(diff)} | "
          f"Greedy costlier than A*: {len(worse)}")
    print(f"Total nodes explored  PATHFINDER: {total_pf}   ORBIT: {total_or}")
