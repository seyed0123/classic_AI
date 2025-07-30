import math
import random

import pygame


class Plotting:
    def __init__(self, xI, xG, environment, FPS=60):
        self.FPS = FPS
        self.xI, self.xG = xI, xG

        self.env = environment
        self.obs = self.env.obs
        self.teleports = self.env.teleports

        self.banner_height = 40
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.env.x_range * 20, self.env.y_range * 20 + self.banner_height)
        )
        pygame.display.set_caption("Robot Path Planning")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        # Pre-compute teleport pairs
        self.teleport_pairs = []
        visited = set()
        for k, v in self.teleports.items():
            if k not in visited and v not in visited:
                self.teleport_pairs.append((k, v))
                visited.add(k)
                visited.add(v)

        # Assign each teleport pair a unique random color
        self.teleport_colors = [
            (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
            for _ in range(len(self.teleport_pairs))
        ]

    def draw_grid(self):
        pygame.draw.rect(
            self.screen, (255, 255, 255),
            (0, 0, self.env.x_range * 20, self.banner_height)
        )
        self.screen.fill(
            (245, 245, 245),
            (0, self.banner_height, self.env.x_range * 20, self.env.y_range * 20)
        )
        self.draw_obstacles()
        self.draw_teleports(pygame.time.get_ticks() // 50)  # Pass frame count for animation
        self.draw_glow(self.xI, (0, 0, 255))
        self.draw_glow(self.xG, (0, 255, 0))

    def draw_obstacles(self):
        for (ox, oy) in self.obs:
            pygame.draw.rect(
                self.screen, (0, 0, 0),
                (ox * 20, oy * 20 + self.banner_height, 20, 20)
            )

    def draw_teleports(self, frame):
        for i, (a, b) in enumerate(self.teleport_pairs):
            color = self.teleport_colors[i]
            self.draw_teleport_circle(a, color, frame)
            self.draw_teleport_circle(b, color, frame)

    def draw_teleport_circle(self, pos, color, frame=0):
        """
        Enhanced teleport visuals:
          - Pulsating glow effect
          - Rotating particle effect
          - Inner vortex effect
          - Subtle warp ring effect
        """

        x = pos[0] * 20 + 10
        y = pos[1] * 20 + 10 + self.banner_height

        # --- PULSATING GLOW EFFECT ---
        pulse_radius = 12 + 2 * math.sin(frame * 0.1)  # Animate glow pulse
        glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, 100), (15, 15), int(pulse_radius))
        self.screen.blit(glow_surf, (x - 15, y - 15))

        # --- MAIN TELEPORT CIRCLE ---
        pygame.draw.circle(self.screen, color, (x, y), 8)

        # --- ROTATING PARTICLES (ORBITS AROUND TELEPORTER) ---
        num_particles = 6
        angle_offset = frame * 0.1

        for i in range(num_particles):
            angle = 2 * math.pi * i / num_particles + angle_offset
            px = int(x + 14 * math.cos(angle))
            py = int(y + 14 * math.sin(angle))
            pygame.draw.circle(self.screen, (*color, 180), (px, py), 2)

        # --- INNER VORTEX EFFECT ---
        for radius in range(6, 1, -2):
            alpha = 120 - (radius * 20)
            vortex_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(vortex_surf, (*color, alpha), (8, 8), radius)
            self.screen.blit(vortex_surf, (x - 8, y - 8))

        # --- WARPING EFFECT (Subtle Distortion Ring) ---
        warp_surf = pygame.Surface((34, 34), pygame.SRCALPHA)
        pygame.draw.circle(warp_surf, (*color, 60), (17, 17), 17, 2)
        self.screen.blit(warp_surf, (x - 17, y - 17))

    def draw_glow(self, pos, color):
        for radius in range(15, 0, -5):
            alpha = 50 if radius == 15 else 150
            s = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, alpha), (20, 20), radius)
            self.screen.blit(s, (pos[0] * 20 - 10, pos[1] * 20 + self.banner_height - 10))

    def draw_path(self, path, END=False):
        length = len(path)
        if END:
            for pos in path:
                pygame.draw.circle(
                    self.screen, (255, 50, 50),
                    (pos[0] * 20 + 10, pos[1] * 20 + 10 + self.banner_height),
                    10
                )
        else:
            for index, pos in enumerate(path):
                size = 10 + (index * 5 // length)
                color = (255 - (index * 200 // length), 50, 50)
                pygame.draw.circle(
                    self.screen, color,
                    (pos[0] * 20 + 10, pos[1] * 20 + 10 + self.banner_height),
                    size
                )

    def draw_visited(self, visited):
        length = len(visited)
        for index, pos in enumerate(visited):
            size = 8
            gradient = (200 - int(200 * index / length), 200, 200)
            pygame.draw.circle(
                self.screen, gradient,
                (pos[0] * 20 + 10, pos[1] * 20 + 10 + self.banner_height),
                size
            )

    def update_info_display(self, visited_count, path_cost):
        visited_label = self.font.render("Visited:", True, (0, 0, 0))
        visited_number = self.font.render(str(visited_count), True, (0, 0, 0))
        cost_label = self.font.render("Path Cost:", True, (0, 0, 0))
        cost_number = self.font.render(f"{path_cost:.2f}", True, (0, 0, 0))

        self.screen.blit(visited_label, (10, 10))
        self.screen.blit(visited_number, (10 + visited_label.get_width() + 5, 10))

        right_x = self.env.x_range * 20 - cost_label.get_width() - cost_number.get_width() - 15
        self.screen.blit(cost_label, (right_x, 10))
        self.screen.blit(cost_number, (right_x + cost_label.get_width() + 5, 10))

    def update(self):
        pygame.display.update()
        self.clock.tick(self.FPS)

    def animation(self, path, visited, cost_dict):
        running = True
        path_index = 0
        visited_index = 0
        frame = 0  # Frame counter for teleport animation

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw_grid()

            # --- Step 1: Reveal visited nodes gradually ---
            if visited_index < len(visited):
                self.draw_visited(visited[:visited_index])
                visited_index += 1
                pygame.time.delay(5)  # Slow down exploration effect

            # --- Step 2: Reveal path gradually ---
            elif path_index < len(path):
                self.draw_visited(visited)  # Keep visited nodes visible
                self.draw_path(path[:path_index])
                path_index += 1
                pygame.time.delay(30)  # Delay to show path formation

            else:
                # --- Step 3: Show the final path after completion ---
                self.draw_visited(visited)
                self.draw_path(path, END=True)
                pygame.time.delay(50)

            # Update teleport visuals dynamically
            self.draw_teleports(frame)
            frame += 1

            # Display real-time cost info
            current_cost = 0.0
            if path_index > 0:
                last_node = path[path_index - 1]
                current_cost = cost_dict.get(last_node, 0.0)

            self.update_info_display(visited_count=visited_index, path_cost=current_cost)
            self.update()

        pygame.quit()
