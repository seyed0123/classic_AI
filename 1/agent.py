import math
import random
from abc import ABC, abstractmethod


class AbstractSearchAgent(ABC):
    """
    Abstract base class for an agent that can do path planning using search trees.
    """

    def __init__(self, s_start, s_goal, environment, euclidean_cost=True):
        self.s_start = s_start
        self.s_goal = s_goal
        self.Env = environment
        self.obs = self.Env.obs
        self.teleports = self.Env.teleports
        self.u_set = self.Env.motions

        # Cost function selection
        self.euclidean_cost = euclidean_cost
        self.teleport_cost = self.teleport_cost_quadratic
        self.NEIGHBOR_COSTS = self.precompute_neighbor_costs()  # use this attribute for your agents

        self.PARENT = {}
        self.COST = {}
        self.VISITED = set()

    @abstractmethod
    def searching(self):
        pass

    def get_neighbors(self, s):
        """
        Returns valid neighbors for normal movement + teleporter exit.
        """
        neighbors = []
        # 8-direction movement
        for dx, dy in self.u_set:
            nx, ny = s[0] + dx, s[1] + dy
            if 0 <= nx < self.Env.x_range and 0 <= ny < self.Env.y_range:
                if (nx, ny) not in self.obs:
                    neighbors.append((nx, ny))

        # If s is a teleport entrance, also add the exit location
        if s in self.teleports:
            exit_cell = self.teleports[s]
            neighbors.append(exit_cell)

        return neighbors

    def teleport_cost_quadratic(self, s_from, s_to):
        """
        Teleportation cost based on squared Euclidean distance.
        """
        dx = s_to[0] - s_from[0]
        dy = s_to[1] - s_from[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        distance = distance * random.uniform(.5, 1.3)  # added noise
        rounded_distance = round(distance, 2)
        return rounded_distance

    def get_cost(self, s_from, s_to):
        """
        Movement cost logic:
        - BFS/DFS → cost = 1 for all types
        - Other algorithms:
            - Straight: 1.0
            - Diagonal: 1.4
            - Teleport: quadratic cost
        """
        if not self.euclidean_cost:
            return 1.0

        if s_from in self.teleports and self.teleports[s_from] == s_to:
            return self.teleport_cost(s_from, s_to)

        dx = abs(s_to[0] - s_from[0])
        dy = abs(s_to[1] - s_from[1])
        if dx == 1 and dy == 1:
            return 1.4
        return 1.0

    def precompute_neighbor_costs(self):
        """
        For each cell, compute the cost to all its neighbors (including teleport exits).
        """
        neighbor_costs = {}

        for x in range(self.Env.x_range):
            for y in range(self.Env.y_range):
                s = (x, y)
                if s in self.obs:
                    continue

                neighbors = self.get_neighbors(s)
                cost_map = {}

                for s_next in neighbors:
                    cost_map[s_next] = self.get_cost(s, s_next)

                neighbor_costs[s] = cost_map

        return neighbor_costs

    def extract_path(self):
        """
        Reconstruct the final path from goal to start.
        """
        path = []
        s = self.s_goal
        while s != self.s_start:
            path.append(s)
            s = self.PARENT[s]
        path.append(self.s_start)
        path.reverse()
        return path
