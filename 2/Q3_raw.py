#!/usr/bin/env python3

from collections import deque, defaultdict
from typing import Dict, List, Set, Optional, Tuple

# Toggle heuristics
USE_AC3 = True
USE_MRV = True
USE_LCV = True

class GraphColoringCSP:
    def __init__(self, edges: List[Tuple[int, int]], num_colors: int):
        self.nodes = set()
        for u, v in edges:
            self.nodes.add(u)
            self.nodes.add(v)

        
        self.adj = defaultdict(list)
        for u, v in edges:
            self.adj[u].append(v)
            self.adj[v].append(u)

        
        self.domains = {node: list(range(1,num_colors+1)) for node in self.nodes}
    
    def solve(self) -> Optional[Dict[int, int]]:
        if USE_AC3:
            self.ac3()

        self.solution = None
        self.backtrack({})
        return self.solution

    def ac3(self):
        queue = deque([(xi, xj) for xi in self.nodes for xj in self.adj[xi]])

        while queue:
            xi, xj = queue.popleft()
            if self.revise(xi, xj):
                if not self.domains[xi]:
                    return  
                for xk in self.adj[xi]:
                    if xk != xj:
                        queue.append((xk, xi))

    def revise(self, xi, xj):
        revised = False
        for color in list(self.domains[xi]):
            if not any(color != other_color for other_color in self.domains[xj]):
                self.domains[xi].remove(color)
                revised = True
        return revised

    def select_unassigned(self, assignment):
        unassigned = [n for n in self.nodes if n not in assignment]
        if not unassigned:
            return None
        if USE_MRV:
            return min(unassigned, key=lambda n: len(self.domains[n]))
        return unassigned[0]

    def order_values(self, node, assignment):
        if not USE_LCV:
            return self.domains[node]

        def count_conflicts(color):
            return sum(1 for neighbor in self.adj[node]
                       if neighbor not in assignment and color in self.domains[neighbor])

        return sorted(self.domains[node], key=count_conflicts)

    def is_consistent(self, node, color, assignment):
        for neighbor in self.adj[node]:
            if neighbor in assignment and assignment[neighbor] == color:
                return False
        return True

    def forward_check(self, node, color, assignment):
        removed = []
        for neighbor in self.adj[node]:
            if neighbor in assignment:
                continue
            if color in self.domains[neighbor]:
                self.domains[neighbor].remove(color)
                removed.append(neighbor)
        return removed

    def restore(self, node, changes):
        for neighbor in changes:
            self.domains[neighbor].append(node)

    def backtrack(self, assignment):
        node = self.select_unassigned(assignment)
        if node is None:
            self.solution = assignment.copy()
            return True

        for color in self.order_values(node, assignment):
            if self.is_consistent(node, color, assignment):
                assignment[node] = color
                changes = self.forward_check(node, color, assignment)

                if all(len(self.domains[n]) > 0 for n in self.adj[node]):
                    if self.backtrack(assignment):
                        return True

                del assignment[node]
                for neighbor in changes:
                    self.domains[neighbor].append(color)

        return False


def parse_input() -> Tuple[List[Tuple[int, int]], int]:
    e = int(input())
    M = int(input())
    edges = []
    for _ in range(e):
        u, v = map(int, input().split(','))
        edges.append((u, v))
    return edges, M


if __name__ == "__main__":
    edges, M = parse_input()
    csp = GraphColoringCSP(edges, M)
    solution = csp.solve()
    if solution is None:
        print("No solution found.")
    else:
       print("Solution:", dict(sorted(solution.items())))