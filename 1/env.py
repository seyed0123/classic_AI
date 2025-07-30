import json
import os
import random

maps_path = os.path.join(
    os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
    ),
    '1',
    "Maps",
)


class Env:
    def __init__(self, map_name, use_random_teleports=True, num_pairs=2):
        self.x_range = 51
        self.y_range = 31
        self.motions = [
            (-1, 0), (-1, 1), (0, 1), (1, 1),
            (1, 0), (1, -1), (0, -1), (-1, -1)
        ]

        self.obs = self.load_obstacles(map_name)
        self.teleports = self.load_teleports(map_name)

        if use_random_teleports:
            self.teleports = self.generate_random_teleports(num_pairs)

    def load_obstacles(self, map_name="default"):
        """Load obstacles from the map file correctly."""
        file_path = os.path.join(maps_path, map_name + '.json')
        obs = set()

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

                if "obstacles" in data:
                    obs = set(tuple(ob) for ob in data["obstacles"])

                print(f"Obstacles loaded from {file_path}.")
        except FileNotFoundError:
            print(f"File {file_path} not found. No obstacles loaded.")

        return obs

    def load_teleports(self, map_name="default"):
        """Load teleport pairs from the map file if they exist."""
        file_path = os.path.join(maps_path, map_name + '.json')
        teleports = {}

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if "teleports" in data:
                    for pair in data["teleports"]:
                        if len(pair) == 2:
                            a, b = tuple(pair[0]), tuple(pair[1])
                            teleports[a] = b
                            teleports[b] = a  # Ensure bidirectional teleporting
            print(f"Teleports loaded from {file_path}: {teleports}")
        except FileNotFoundError:
            print(f"File {file_path} not found. No predefined teleports.")
        return teleports

    def generate_random_teleports(self, num_pairs=2):
        """Generate random teleport pairs on non-obstacle cells."""
        empty_cells = [
            (x, y) for x in range(self.x_range)
            for y in range(self.y_range)
            if (x, y) not in self.obs
        ]
        random.shuffle(empty_cells)

        teleports = {}
        for _ in range(num_pairs):
            if len(empty_cells) < 2:
                break
            a = empty_cells.pop()
            b = empty_cells.pop()
            teleports[a] = b
            teleports[b] = a  # Bidirectional linking

        print(f"Generated random teleport pairs: {teleports}")
        return teleports
