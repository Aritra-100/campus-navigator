"""search.py - Greedy Best-First Search and A*, plus the CSE-zone routing rule.

"""

import heapq
import time
from dataclasses import dataclass, field

NORMAL = "NORMAL"      
LIFT_IN = "LIFT_IN"    
IN_CSE = "IN_CSE"      
LIFT_OUT = "LIFT_OUT"  


class CSERule:
    """Generates only the moves allowed by the special CSE routing rule.

    """

    def __init__(self, campus):
        self.zone = campus.cse_zone
        self.lift = campus.lift
        self.entries = campus.tower_entries

    def start_mode(self, node):
        if node in self.zone:
            return IN_CSE
        if node == self.lift:
            return LIFT_IN     
        return NORMAL

    def move(self, mode, u, v):
        """Return the new mode if walking u -> v is allowed, else None."""
        if mode == IN_CSE:
            if v in self.zone:
                return IN_CSE
            if v == self.lift:
                return LIFT_OUT
            return None
        if mode == LIFT_OUT:
            return NORMAL if v in self.entries else None
        if mode == LIFT_IN:
            return IN_CSE if v in self.zone else NORMAL
        
        if v in self.zone:
            return None
        if v == self.lift and u in self.entries:
            return LIFT_IN
        return NORMAL


class NoRule:
    """Used only to switch the CSE rule off for comparison; the agents use CSERule."""

    def start_mode(self, node):
        return NORMAL

    def move(self, mode, u, v):
        return NORMAL


@dataclass
class SearchResult:
    algorithm: str
    start: str
    goal: str
    found: bool
    path: list = field(default_factory=list)
    cost: float = 0.0
    nodes_explored: int = 0
    time_s: float = 0.0
    max_frontier: int = 0


def _successors(campus, rule, state):
    node, mode = state
    for nbr, w in campus.neighbors(node):
        new_mode = rule.move(mode, node, nbr)
        if new_mode is not None:
            yield (nbr, new_mode), w


def _build_path(parent, state):
    path = []
    while state is not None:
        path.append(state[0])
        state = parent[state]
    return path[::-1]


def _path_cost(campus, path):
    return sum(campus.edge_weight(a, b) for a, b in zip(path, path[1:]))


def greedy_best_first(campus, rule, start, goal):
    """Greedy Best-First Search: always expand the node with the smallest h(n)."""
    t0 = time.perf_counter()
    start_state = (start, rule.start_mode(start))
    counter = 0                                   
    frontier = [(campus.heuristic(start, goal), counter, start_state)]
    parent = {start_state: None}                  
    explored = 0
    max_frontier = 1
    result = SearchResult("Greedy Best-First", start, goal, False)

    while frontier:
        _, _, state = heapq.heappop(frontier)
        explored += 1
        if state[0] == goal:
            path = _build_path(parent, state)
            result.found, result.path = True, path
            result.cost = _path_cost(campus, path)
            break
        for nxt, _w in _successors(campus, rule, state):
            if nxt not in parent:
                parent[nxt] = state
                counter += 1
                heapq.heappush(frontier, (campus.heuristic(nxt[0], goal), counter, nxt))
        max_frontier = max(max_frontier, len(frontier))

    result.nodes_explored = explored
    result.max_frontier = max_frontier
    result.time_s = time.perf_counter() - t0
    return result


def a_star(campus, rule, start, goal):
    """A* Search: always expand the node with the smallest f(n) = g(n) + h(n)."""
    t0 = time.perf_counter()
    start_state = (start, rule.start_mode(start))
    counter = 0
    h0 = campus.heuristic(start, goal)
    frontier = [(h0, h0, counter, start_state)]   # (f, h, tie-breaker, state)
    g_cost = {start_state: 0}
    parent = {start_state: None}
    closed = set()
    explored = 0
    max_frontier = 1
    result = SearchResult("A*", start, goal, False)

    while frontier:
        f, _h, _, state = heapq.heappop(frontier)
        if state in closed:
            continue                             
        closed.add(state)
        explored += 1
        if state[0] == goal:
            path = _build_path(parent, state)
            result.found, result.path = True, path
            result.cost = g_cost[state]
            break
        for nxt, w in _successors(campus, rule, state):
            new_g = g_cost[state] + w
            if nxt not in g_cost or new_g < g_cost[nxt]:
                g_cost[nxt] = new_g
                parent[nxt] = state
                counter += 1
                h = campus.heuristic(nxt[0], goal)
                heapq.heappush(frontier, (new_g + h, h, counter, nxt))
        max_frontier = max(max_frontier, len(frontier))

    result.nodes_explored = explored
    result.max_frontier = max_frontier
    result.time_s = time.perf_counter() - t0
    return result
