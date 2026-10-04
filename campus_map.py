"""campus_map.py - the campus graph: locations, connections, weights, coordinates."""

import json
import math
import os
from difflib import get_close_matches


class Location:
    """A node of the graph (one named place on the satellite map)."""

    def __init__(self, name, x, y, aliases=None):
        self.name = name
        self.x = x
        self.y = y
        self.aliases = aliases or []

    def distance_to(self, other):
        """Straight-line distance in metres."""
        return math.hypot(self.x - other.x, self.y - other.y)

    def __repr__(self):
        return f"Location({self.name!r})"


class CampusMap:
    """Weighted, undirected graph of campus locations."""

    def __init__(self, locations, edges, cse_zone, lift, tower_entries,
                 h_scale=1.0, h_overrides=None):
        self.locations = {loc.name: loc for loc in locations}
        self.adjacency = {name: [] for name in self.locations}

        for a, b, w in edges:
            if a not in self.locations or b not in self.locations:
                raise ValueError(f"Edge uses an unknown location: {a} - {b}")

            self.adjacency[a].append((b, w))
            self.adjacency[b].append((a, w))

        self.cse_zone = set(cse_zone)
        self.lift = lift
        self.tower_entries = set(tower_entries)

        for name in self.cse_zone | self.tower_entries | {lift}:
            if name not in self.locations:
                raise ValueError(f"CSE rule uses an unknown location: {name}")

        self.h_scale = h_scale
        self.h_overrides = h_overrides or {}

        self._lookup = {}

        for loc in locations:
            self._lookup[loc.name.lower()] = loc.name

            for alias in loc.aliases:
                self._lookup[alias.lower()] = loc.name

    @classmethod
    def from_json(cls, path=None):
        if path is None:
            path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "campus.json"
            )

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        locations = [
            Location(
                n["name"],
                n["x"],
                n["y"],
                n.get("aliases")
            )
            for n in data["nodes"]
        ]

        rule = data["cse_rule"]
        heur = data.get("heuristic", {})

        return cls(
            locations,
            data["edges"],
            rule["zone"],
            rule["lift"],
            rule["tower_entries"],
            heur.get("scale", 1.0),
            heur.get("overrides", {})
        )

    def neighbors(self, name):
        """List of (neighbour, edge_weight)."""
        return self.adjacency[name]

    def edge_weight(self, a, b):
        for nbr, w in self.adjacency[a]:
            if nbr == b:
                return w

        raise KeyError(f"No edge between {a} and {b}")

    def heuristic(self, node, goal):
        """Estimated remaining cost h(node -> goal), identical for both agents."""
        manual = self.h_overrides.get(goal, {})

        if node in manual:
            return manual[node]

        return self.h_scale * self.locations[node].distance_to(
            self.locations[goal]
        )

    def resolve(self, text):
        """Map user text to a canonical location name (or None)."""
        return self._lookup.get(text.strip().lower())

    def suggest(self, text, n=3):
        return get_close_matches(
            text.strip().lower(),
            list(self._lookup),
            n=n,
            cutoff=0.5
        )

    def names(self):
        return sorted(self.locations)