"""agents.py - the two routing agents."""

from search import CSERule, greedy_best_first, a_star


class RoutingAgent:
    """Base class: an agent owns a campus map, the CSE rule and one search strategy."""

    name = "AGENT"
    strategy = None  # set by subclasses

    def __init__(self, campus):
        self.campus = campus
        self.rule = CSERule(campus)

    def find_route(self, start, goal):
        return self.strategy(self.campus, self.rule, start, goal)


class Pathfinder(RoutingAgent):
    """PATHFINDER - Greedy Best-First Search, f(n) = h(n)."""

    name = "PATHFINDER"
    strategy = staticmethod(greedy_best_first)


class Orbit(RoutingAgent):
    """ORBIT - A* Search, f(n) = g(n) + h(n)."""

    name = "ORBIT"
    strategy = staticmethod(a_star)
