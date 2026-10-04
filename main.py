
import argparse
import sys

from campus_map import CampusMap
from agents import Pathfinder, Orbit
from experiment import run_experiments, print_summary


def ask_location(campus, prompt):
    while True:
        text = input(prompt).strip()
        name = campus.resolve(text)
        if name:
            return name
        hints = campus.suggest(text)
        print(f"  Unknown location '{text}'.", end=" ")
        print(f"Did you mean: {', '.join(hints)}?" if hints else "Type 'list' to see all locations.")
        if text.lower() == "list":
            print("  " + "\n  ".join(campus.names()))


def show(agent_name, result):
    print(f"\n{agent_name}")
    if not result.found:
        print("Route: no valid route found (check the CSE routing rule)")
    else:
        print("Route:")
        print(" → ".join(result.path))
        print(f"Cost: {result.cost:g} m")
    print(f"Nodes explored: {result.nodes_explored}")
    print(f"Time: {result.time_s:.6f} s")


def interactive(campus):
    pathfinder, orbit = Pathfinder(campus), Orbit(campus)
    print("=== AI Campus Route Navigator (CU Technology Campus) ===")
    print("Type 'list' at a prompt to see locations, Ctrl+C to quit.\n")
    while True:
        try:
            start = ask_location(campus, "Enter starting location: ")
            goal = ask_location(campus, "Enter destination: ")
            if start == goal:
                print("Start and destination are the same.\n")
                continue
            show(pathfinder.name, pathfinder.find_route(start, goal))
            show(orbit.name, orbit.find_route(start, goal))
            print()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            return


def main():
    parser = argparse.ArgumentParser(description="AI Campus Route Navigator")
    parser.add_argument("--map", default="campus.json", help="campus graph file")
    parser.add_argument("--experiments", action="store_true",
                        help="run all experiments and save results.csv")
    parser.add_argument("--out", default="results.csv", help="CSV output file")
    args = parser.parse_args()

    try:
        campus = CampusMap.from_json(args.map)
    except (OSError, ValueError, KeyError) as err:
        sys.exit(f"Could not load campus map: {err}")

    if args.experiments:
        summary = run_experiments(campus, out_path=args.out)
        print_summary(summary)
        print(f"\nResults saved to {args.out}")
    else:
        interactive(campus)


if __name__ == "__main__":
    main()
