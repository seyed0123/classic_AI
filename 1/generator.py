import json
import os
import random

import pygame

import env

maps_path = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)),
    "Maps"
)


class Generator:
    def __init__(self, map_name, FPS):
        self.env = env.Env(map_name, use_random_teleports=False)
        self.FPS = FPS
        self.mode = 'obstacle'  # Can be 'obstacle' or 'teleport'
        self.pending_gate = None
        pygame.init()
        self.screen = pygame.display.set_mode((self.env.x_range * 20, self.env.y_range * 20))
        pygame.display.set_caption("Map Editor")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

    def draw_grid(self, mouse_pos):
        """Draw everything: grid, elements, hover, and mode label"""
        self.screen.fill((255, 255, 255))  # White

        for x in range(self.env.x_range):
            for y in range(self.env.y_range):
                rect = pygame.Rect(x * 20, y * 20, 20, 20)
                pos = (x, y)

                if pos in self.env.obs:
                    pygame.draw.rect(self.screen, (0, 0, 0), rect)
                elif pos in self.env.teleports:
                    color = self.get_pair_color(pos)
                    pygame.draw.rect(self.screen, color, rect)
                else:
                    pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

        # Hover logic with validation
        grid_pos = (mouse_pos[0] // 20, mouse_pos[1] // 20)
        rect = pygame.Rect(grid_pos[0] * 20, grid_pos[1] * 20, 20, 20)

        valid_hover = False
        if self.mode == 'obstacle':
            valid_hover = (grid_pos in self.env.obs) or (grid_pos not in self.env.teleports)
        elif self.mode == 'teleport':
            valid_hover = (grid_pos in self.env.teleports) or (
                    grid_pos not in self.env.obs and grid_pos not in self.env.teleports)

        if valid_hover:
            if self.mode == 'teleport' and self.pending_gate and grid_pos not in self.env.teleports:
                pg = self.pending_gate
                pending_rect = pygame.Rect(pg[0] * 20, pg[1] * 20, 20, 20)
                pygame.draw.rect(self.screen, (0, 200, 255), pending_rect, 3)
                pygame.draw.rect(self.screen, (0, 255, 0), rect, 2)
            else:
                pygame.draw.rect(self.screen, (255, 0, 0), rect, 2)

        # Top-right mode label
        label = self.font.render(f"Mode: {self.mode.title()}", True, (0, 0, 0))
        label_pos = (self.env.x_range * 20 - 150, 25)
        self.screen.blit(label, label_pos)

        pygame.display.update()

    def get_pair_color(self, pos):
        """Generate consistent color for a teleporter pair"""
        pair = tuple(sorted([pos, self.env.teleports[pos]]))
        random.seed(str(pair))
        return [random.randint(100, 255) for _ in range(3)]

    def toggle_obstacle(self, grid_pos):
        """Toggle obstacle at given position"""
        if grid_pos in self.env.obs:
            self.env.obs.remove(grid_pos)
        else:
            self.env.obs.add(grid_pos)

    def toggle_teleporter(self, grid_pos):
        """Handle teleporter pairing and removal"""
        if grid_pos in self.env.teleports:
            pair = self.env.teleports.pop(grid_pos)
            self.env.teleports.pop(pair)
            self.pending_gate = None
            return

        if self.pending_gate is None:
            self.pending_gate = grid_pos
        else:
            if self.pending_gate != grid_pos:
                self.env.teleports[self.pending_gate] = grid_pos
                self.env.teleports[grid_pos] = self.pending_gate
            self.pending_gate = None

    def input_map(self):
        """Let user define the map with mouse clicks and keyboard"""
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            self.draw_grid(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    grid_pos = (mouse_pos[0] // 20, mouse_pos[1] // 20)

                    if self.mode == 'obstacle':
                        if grid_pos in self.env.obs:
                            self.toggle_obstacle(grid_pos)
                        elif grid_pos not in self.env.teleports:
                            self.toggle_obstacle(grid_pos)

                    elif self.mode == 'teleport':
                        if grid_pos in self.env.teleports:
                            self.toggle_teleporter(grid_pos)
                        elif grid_pos not in self.env.obs:
                            self.toggle_teleporter(grid_pos)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        running = False
                    elif event.key == pygame.K_t:
                        self.mode = 'teleport' if self.mode == 'obstacle' else 'obstacle'
                        print(f"Switched to {self.mode} mode.")

            self.clock.tick(self.FPS)
        pygame.quit()

    def save_map(self, file_path):
        """Save both obstacles and teleport data to JSON"""

        teleports_formatted = [
            [list(k), list(v)]
            for k, v in self.env.teleports.items()
            if list(k) < list(v)
        ]

        map_data = {
            "obstacles": list(self.env.obs),
            "teleports": teleports_formatted
        }

        with open(file_path, 'w') as f:
            json.dump(map_data, f, indent=4)

        print(f"Map saved to {file_path}.")


def main(map_name='default', FPS=30):
    file_path = os.path.join(maps_path, f"{map_name}.json")
    generator = Generator(map_name, FPS)
    generator.input_map()
    generator.save_map(file_path)


if __name__ == "__main__":
    main()
