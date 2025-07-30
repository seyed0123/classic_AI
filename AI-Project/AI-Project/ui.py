import os
from typing import Optional, Tuple, List, Dict, Any

import pygame

from game import XOShiftGame

REPLAYS_DIR = "replays"

def load_font(size: int, font_name: Optional[str] = "Alegreya-Regular.otf") -> pygame.font.Font:
    """
    Utility to load a font of the given size.
    If font_name is provided, it tries to load that .ttf/.otf file from an 'assets/' subdirectory.
    Otherwise, it falls back to the default system font.
    """
    if font_name:
        # Construct the full path to the font file
        # Assumes your utils.py is at the root or you adjust the path accordingly
        font_path = os.path.join("assets", font_name)
        try:
            return pygame.font.Font('/home/seyed/code/python/ai/AI-Project/AI-Project/assets/Alegreya-Regular.otf', size)
        except pygame.error as e:
            print(f"Warning: Could not load custom font '{font_path}': {e}. Falling back to default font.")

    # Fallback to default font if no name provided or custom font fails to load
    return pygame.font.Font(pygame.font.get_default_font(), size)


def draw_text_centered(surface, text, font, color, center):
    """
    Draw text on the given surface, centered at `center` (x, y).
    """
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    rect.center = center
    surface.blit(rendered, rect)

class XOShiftUI:
    STATE_MENU = "menu"
    STATE_REPLAY_FILE_SELECT = "replay_file_select"
    STATE_SELECT = "select"
    STATE_PUSH = "push"
    STATE_WAITING = "waiting"
    STATE_GAME_OVER = "game_over"
    STATE_REPLAY = "replay"

    BG_COLOR = (240, 240, 240)
    GRID_COLOR = (0, 0, 0)
    SELECT_COLOR = (255, 200, 200)
    HOVER_COLOR = (200, 255, 200)
    VALID_TARGET_HOVER_COLOR = (150, 200, 255)
    WINNING_LINE_COLOR = (0, 200, 0, 150)
    BUTTON_COLOR = (190, 190, 190)
    BUTTON_HOVER_COLOR = (210, 210, 210)
    TEXT_COLOR = (0, 0, 0)
    MENU_TEXT_COLOR = (40, 40, 40)
    MENU_HIGHLIGHT_COLOR = (0, 120, 220)
    MENU_BUTTON_TEXT_COLOR = (255, 255, 255)

    ITEM_HEIGHT = 60
    ITEM_WIDTH_NORMAL = 240
    ITEM_WIDTH_SMALL = 100

    def __init__(self, screen: pygame.Surface):
        self.game: Optional[XOShiftGame] = None
        self.screen = screen
        self.state = self.STATE_MENU
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.replay_finished = False
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.record_replays_enabled = True
        self.player_types: Dict[str, str] = {}

        self.header_height = 80
        self.cell_size = 80
        self.margin = 20

        self.font = load_font(28)
        self.large_font = load_font(40)
        self.medium_font = load_font(36)
        self.title_font = load_font(54)
        self.endgame_font = load_font(50)
        self.small_font = load_font(22)

        self.board_start_x = 0
        self.board_start_y = 0

        self.menu_options: Dict[str, Any] = {}
        self.selected_board_size = 5
        self.selected_mode = "human-human"
        self.replay_files_list: List[str] = []
        self.replay_file_buttons: List[Dict[str, Any]] = []
        self.current_replay_page = 0
        self.items_per_replay_page = 8

        self._setup_menu_rects()

        self.ingame_return_to_menu_button_rect = pygame.Rect(self.margin + 10, self.header_height // 2 - 20, 150, 40)
        self.post_game_return_to_menu_button_rect = pygame.Rect(self.screen_width // 2 - 150, self.screen_height - 100,
                                                                300, 50)
        self.replay_again_button_rect = pygame.Rect(self.screen_width // 2 - 150, self.screen_height - 160, 300, 50)

    def _setup_menu_rects(self):
        y_offset = 150
        spacing = self.ITEM_HEIGHT + 20
        group_spacing = 30

        self.menu_options = {
            "title": "XOShift Game",
            "record_replays_button": {
                "text_on": "Record Replays: ON", "text_off": "Record Replays: OFF",
                "rect": pygame.Rect(self.screen_width // 2 - (self.ITEM_WIDTH_NORMAL + 50) // 2, y_offset,
                                    self.ITEM_WIDTH_NORMAL + 50, self.ITEM_HEIGHT),
                "action": "toggle_record_replays"
            },
        }
        y_offset += spacing + group_spacing

        self.menu_options["board_size_label"] = "Board Size:"
        sizes = [3, 4, 5]
        num_size_buttons = len(sizes)
        button_spacing_h = 15
        total_width_sizes_group = num_size_buttons * (self.ITEM_WIDTH_SMALL + 5) + (
                num_size_buttons - 1) * button_spacing_h
        start_x_sizes = self.screen_width // 2 - total_width_sizes_group // 2

        self.menu_options["board_size_buttons_y_offset"] = y_offset
        y_offset_for_size_buttons = y_offset + 40

        self.menu_options["board_size_buttons"] = []
        for i, size_val in enumerate(sizes):
            rect = pygame.Rect(start_x_sizes + i * (self.ITEM_WIDTH_SMALL + 5 + button_spacing_h),
                               y_offset_for_size_buttons, self.ITEM_WIDTH_SMALL + 5, self.ITEM_HEIGHT)
            self.menu_options["board_size_buttons"].append(
                {"text": f"{size_val}x{size_val}", "rect": rect, "action": "set_size", "value": size_val})
        y_offset = y_offset_for_size_buttons + spacing + group_spacing

        self.menu_options["mode_label"] = "Game Mode:"
        self.menu_options["mode_buttons_y_offset"] = y_offset
        y_offset_for_mode_buttons = y_offset + 40

        modes = [
            ("Human vs Human", "human-human", self.ITEM_WIDTH_NORMAL + 20),
            ("Human vs Agent", "human-agent", self.ITEM_WIDTH_NORMAL + 20),
            ("Agent vs Agent", "agent-agent", self.ITEM_WIDTH_NORMAL + 20),
            ("Replay a Game", "replay-select-file", self.ITEM_WIDTH_NORMAL + 20)
        ]
        self.menu_options["mode_buttons"] = []

        button_h_spacing_modes = 20
        col0_x = self.screen_width // 2 - (self.ITEM_WIDTH_NORMAL + 20) - button_h_spacing_modes // 2
        col1_x = self.screen_width // 2 + button_h_spacing_modes // 2

        for i, (text, mode_val, width) in enumerate(modes):
            row_index = i // 2
            col_index = i % 2
            current_x = col0_x if col_index == 0 else col1_x
            current_y = y_offset_for_mode_buttons + row_index * spacing

            rect = pygame.Rect(current_x, current_y, width, self.ITEM_HEIGHT)
            self.menu_options["mode_buttons"].append(
                {"text": text, "rect": rect, "action": "set_mode", "value": mode_val})

        y_offset = y_offset_for_mode_buttons + 2 * spacing + group_spacing

        self.menu_options["start_button"] = {"text": "Start Selected Game", "rect": pygame.Rect(
            self.screen_width // 2 - (self.ITEM_WIDTH_NORMAL + 40) // 2, y_offset, self.ITEM_WIDTH_NORMAL + 40,
            self.ITEM_HEIGHT), "action": "start_game"}
        y_offset += spacing
        self.menu_options["quit_button"] = {"text": "Quit Game", "rect": pygame.Rect(
            self.screen_width // 2 - (self.ITEM_WIDTH_NORMAL + 40) // 2, y_offset, self.ITEM_WIDTH_NORMAL + 40,
            self.ITEM_HEIGHT), "action": "quit"}

    def _populate_replay_file_buttons(self):
        self.replay_file_buttons = []
        if not os.path.exists(REPLAYS_DIR):
            try:
                os.makedirs(REPLAYS_DIR)
                print(f"Created directory: {REPLAYS_DIR}")
            except OSError as e:
                print(f"Error creating directory {REPLAYS_DIR}: {e}. Cannot list replays.")
                self.replay_file_buttons.append({"text": "Back to Menu",
                                                 "rect": pygame.Rect(self.screen_width // 2 - 120,
                                                                     self.screen_height - 140, 240, 50),
                                                 "action": "return_to_menu"})
                return

        self.replay_files_list = sorted([f for f in os.listdir(REPLAYS_DIR) if f.endswith(".json")], reverse=True)
        start_index = self.current_replay_page * self.items_per_replay_page
        end_index = start_index + self.items_per_replay_page
        files_to_display = self.replay_files_list[start_index:end_index]
        y_offset = 150
        button_width = 550
        button_height = 50
        for i, filename in enumerate(files_to_display):
            rect = pygame.Rect(self.screen_width // 2 - button_width // 2, y_offset + i * (button_height + 10),
                               button_width, button_height)
            self.replay_file_buttons.append(
                {"text": filename, "rect": rect, "action": "select_replay_file", "value": filename})
        nav_button_y = self.screen_height - 80
        nav_button_width = 120
        nav_button_height = 45
        if self.current_replay_page > 0:
            self.replay_file_buttons.append({"text": "< Prev",
                                             "rect": pygame.Rect(self.screen_width // 2 - 200 - nav_button_width // 2,
                                                                 nav_button_y, nav_button_width, nav_button_height),
                                             "action": "prev_replay_page"})
        if end_index < len(self.replay_files_list):
            self.replay_file_buttons.append({"text": "Next >",
                                             "rect": pygame.Rect(self.screen_width // 2 + 200 - nav_button_width // 2,
                                                                 nav_button_y, nav_button_width, nav_button_height),
                                             "action": "next_replay_page"})
        self.replay_file_buttons.append({"text": "Back to Menu",
                                         "rect": pygame.Rect(self.screen_width // 2 - 120, self.screen_height - 140,
                                                             240, 50), "action": "return_to_menu"})

    def set_game(self, game: Optional[XOShiftGame]):
        self.game = game
        if self.game:
            self.update_board_layout()
            if self.state != self.STATE_REPLAY:
                self.state = self.STATE_SELECT
            self.selected_cell = None
            self.replay_finished = False
        else:
            self.state = self.STATE_MENU
            self.player_types = {}

    def update_board_layout(self):
        if not self.game:
            return
        board_total_width = self.game.size * self.cell_size
        board_total_height = self.game.size * self.cell_size
        self.board_start_x = (self.screen_width - board_total_width) // 2
        self.board_start_y = self.header_height + (self.screen_height - self.header_height - board_total_height) // 2

    def handle_event(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        if self.state == self.STATE_MENU:
            return self._handle_menu_event(event)
        elif self.state == self.STATE_REPLAY_FILE_SELECT:
            return self._handle_replay_file_select_event(event)
        elif self.game and self.state in [self.STATE_SELECT, self.STATE_PUSH, self.STATE_WAITING]:
            return self._handle_game_event(event)
        elif self.state == self.STATE_GAME_OVER:
            return self._handle_post_game_event(event, is_replay_end=False)
        elif self.state == self.STATE_REPLAY:
            return self._handle_replay_event(event)
        return None

    def _handle_menu_event(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            button = self.menu_options["record_replays_button"]
            if button["rect"].collidepoint(mouse_pos):
                self.record_replays_enabled = not self.record_replays_enabled
                return None
            for button_info in self.menu_options["board_size_buttons"]:
                if button_info["rect"].collidepoint(mouse_pos):
                    self.selected_board_size = button_info["value"]
                    return None
            for button_info in self.menu_options["mode_buttons"]:
                if button_info["rect"].collidepoint(mouse_pos):
                    self.selected_mode = button_info["value"]
                    if self.selected_mode == "replay-select-file":
                        self.current_replay_page = 0
                        self._populate_replay_file_buttons()
                        self.state = self.STATE_REPLAY_FILE_SELECT
                    return None
            if self.menu_options["start_button"]["rect"].collidepoint(mouse_pos):
                if self.selected_mode == "replay-select-file":
                    self.current_replay_page = 0
                    self._populate_replay_file_buttons()
                    self.state = self.STATE_REPLAY_FILE_SELECT
                    return None
                return {"action": "start_game", "size": self.selected_board_size, "mode": self.selected_mode,
                        "record_replay": self.record_replays_enabled}
            if self.menu_options["quit_button"]["rect"].collidepoint(mouse_pos):
                return {"action": "quit"}
        return None

    def _handle_replay_file_select_event(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for button in self.replay_file_buttons:
                if button["rect"].collidepoint(mouse_pos):
                    if button["action"] == "select_replay_file":
                        return {"action": "load_replay", "filename": button["value"]}
                    elif button["action"] == "return_to_menu":
                        self.state = self.STATE_MENU
                        return None
                    elif button["action"] == "prev_replay_page":
                        if self.current_replay_page > 0:
                            self.current_replay_page -= 1
                            self._populate_replay_file_buttons()
                        return None
                    elif button["action"] == "next_replay_page":
                        if (self.current_replay_page + 1) * self.items_per_replay_page < len(self.replay_files_list):
                            self.current_replay_page += 1
                            self._populate_replay_file_buttons()
                        return None
        return None

    def _handle_game_event(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        if not self.game or self.game.winner:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if self.ingame_return_to_menu_button_rect.collidepoint(mouse_pos):
                return {"action": "return_to_menu_ingame"}
            grid_pos = self.pixel_to_cell(mouse_pos)
            if self.state == self.STATE_SELECT:
                if grid_pos:
                    row, col = grid_pos
                    if self.game.is_valid_selection(row, col, self.game.current_player):
                        self.selected_cell = (row, col)
                        self.state = self.STATE_PUSH
            elif self.state == self.STATE_PUSH:
                if grid_pos and self.selected_cell:
                    sr_sel, sc_sel = self.selected_cell
                    if grid_pos == self.selected_cell:
                        self.selected_cell = None
                        self.state = self.STATE_SELECT
                        return None
                    tr, tc = grid_pos
                    if self.game.is_valid_target(sr_sel, sc_sel, tr, tc):
                        return {"action": "apply_move", "move": (sr_sel, sc_sel, tr, tc)}
        return None

    def _handle_post_game_event(self, event: pygame.event.Event, is_replay_end: bool) -> Optional[Dict[str, Any]]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if self.post_game_return_to_menu_button_rect.collidepoint(mouse_pos):
                return {"action": "return_to_menu"}
            if is_replay_end and self.replay_again_button_rect.collidepoint(mouse_pos):
                return {"action": "replay_again"}
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                return {"action": "return_to_menu"}
        return None

    def _handle_replay_event(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        if self.replay_finished:
            return self._handle_post_game_event(event, is_replay_end=True)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.ingame_return_to_menu_button_rect.collidepoint(event.pos):
                return {"action": "return_to_menu_ingame"}
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return {"action": "return_to_menu_ingame"}
        return None

    def pixel_to_cell(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        if not self.game:
            return None
        x, y = pos
        board_width = self.game.size * self.cell_size
        board_height = self.game.size * self.cell_size
        if not (
                self.board_start_x <= x < self.board_start_x + board_width and self.board_start_y <= y < self.board_start_y + board_height):
            return None
        board_x = x - self.board_start_x
        board_y = y - self.board_start_y
        col = board_x // self.cell_size
        row = board_y // self.cell_size
        if 0 <= row < self.game.size and 0 <= col < self.game.size:
            return row, col
        return None

    def draw(self) -> None:
        self.screen.fill(self.BG_COLOR)
        if self.state == self.STATE_MENU:
            self._draw_menu()
        elif self.state == self.STATE_REPLAY_FILE_SELECT:
            self._draw_replay_file_list()
        elif self.game and self.state in [self.STATE_SELECT, self.STATE_PUSH, self.STATE_WAITING, self.STATE_GAME_OVER,
                                          self.STATE_REPLAY]:
            self._draw_board_and_game_ui()
            if self.state == self.STATE_GAME_OVER:
                self._draw_game_over_screen()
            elif self.state == self.STATE_REPLAY and self.replay_finished:
                self._draw_replay_finished_screen()
        pygame.display.flip()

    def _draw_menu_button(self, button_info: Dict, is_selected: bool = False):
        text_to_display = ""
        if "text_on" in button_info and "text_off" in button_info:
            text_to_display = button_info["text_on"] if self.record_replays_enabled else button_info["text_off"]
        elif "text" in button_info:
            text_to_display = button_info["text"]
        else:
            text_to_display = "Error"
        rect = button_info["rect"]
        mouse_pos = pygame.mouse.get_pos()
        color = self.BUTTON_COLOR
        text_color = self.TEXT_COLOR
        if is_selected:
            color = self.MENU_HIGHLIGHT_COLOR
            text_color = self.MENU_BUTTON_TEXT_COLOR
        elif rect.collidepoint(mouse_pos):
            color = self.BUTTON_HOVER_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        draw_text_centered(self.screen, text_to_display, self.font, text_color, rect.center)

    def _draw_menu(self):
        draw_text_centered(self.screen, self.menu_options["title"], self.title_font, self.MENU_TEXT_COLOR,
                           (self.screen_width // 2, 80))
        self._draw_menu_button(self.menu_options["record_replays_button"])
        draw_text_centered(self.screen, self.menu_options["board_size_label"], self.large_font, self.MENU_TEXT_COLOR,
                           (self.screen_width // 2, self.menu_options["board_size_buttons_y_offset"]))
        for button in self.menu_options["board_size_buttons"]:
            self._draw_menu_button(button, button["value"] == self.selected_board_size)
        draw_text_centered(self.screen, self.menu_options["mode_label"], self.large_font, self.MENU_TEXT_COLOR,
                           (self.screen_width // 2, self.menu_options["mode_buttons_y_offset"]))
        for button in self.menu_options["mode_buttons"]:
            self._draw_menu_button(button, button["value"] == self.selected_mode)
        self._draw_menu_button(self.menu_options["start_button"])
        self._draw_menu_button(self.menu_options["quit_button"])

    def _draw_replay_file_list(self):
        draw_text_centered(self.screen, "Select a Replay File", self.title_font, self.MENU_TEXT_COLOR,
                           (self.screen_width // 2, 80))
        if not self.replay_file_buttons and not self.replay_files_list:
            draw_text_centered(self.screen, "No replay files found in 'replays' directory.", self.font, self.TEXT_COLOR,
                               (self.screen_width // 2, 250))
            back_button_info = next((b for b in self.replay_file_buttons if b["action"] == "return_to_menu"), None)
            if back_button_info:
                self._draw_menu_button(back_button_info)
            return
        for button_info in self.replay_file_buttons:
            rect = button_info["rect"]
            text = button_info["text"]
            color = self.BUTTON_COLOR
            text_c = self.TEXT_COLOR
            font_to_use = self.small_font if button_info["action"] == "select_replay_file" else self.font
            if rect.collidepoint(pygame.mouse.get_pos()):
                color = self.BUTTON_HOVER_COLOR
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            draw_text_centered(self.screen, text, font_to_use, text_c, rect.center)

    def _draw_board_and_game_ui(self):
        if not self.game:
            return
        show_ingame_return = self.state in [self.STATE_SELECT, self.STATE_PUSH, self.STATE_WAITING] or (
                self.state == self.STATE_REPLAY and not self.replay_finished)
        if show_ingame_return:
            btn_color = self.BUTTON_COLOR
            if self.ingame_return_to_menu_button_rect.collidepoint(pygame.mouse.get_pos()):
                btn_color = self.BUTTON_HOVER_COLOR
            pygame.draw.rect(self.screen, btn_color, self.ingame_return_to_menu_button_rect, border_radius=5)
            draw_text_centered(self.screen, "Leave", self.font, self.TEXT_COLOR,
                               self.ingame_return_to_menu_button_rect.center)
        header_text = ""
        current_player_symbol = self.game.current_player
        player_info = self.player_types.get(current_player_symbol, 'human')

        if self.state == self.STATE_WAITING:
            header_text = f"Player {current_player_symbol} ({player_info}) thinking..."
        elif self.state == self.STATE_REPLAY:
            header_text = "Replay (left/right arrows)" if not self.replay_finished else "Replay Finished"
        else:
            header_text = f"Turn: {current_player_symbol} ({player_info})"
        draw_text_centered(self.screen, header_text, self.medium_font, self.TEXT_COLOR,
                           (self.screen_width // 2, self.header_height // 2))
        mouse_pos = pygame.mouse.get_pos()
        for r in range(self.game.size):
            for c in range(self.game.size):
                cell_rect = pygame.Rect(self.board_start_x + c * self.cell_size,
                                        self.board_start_y + r * self.cell_size, self.cell_size, self.cell_size)
                if self.game.winner and self.game.winning_line_coords and (r, c) in self.game.winning_line_coords:
                    highlight_surface = pygame.Surface((self.cell_size - 4, self.cell_size - 4), pygame.SRCALPHA)
                    highlight_surface.fill(self.WINNING_LINE_COLOR)
                    self.screen.blit(highlight_surface, (cell_rect.left + 2, cell_rect.top + 2))
                current_highlight_color = None
                is_interactive_state = self.state in [self.STATE_SELECT, self.STATE_PUSH]
                if is_interactive_state and cell_rect.collidepoint(mouse_pos):
                    if self.state == self.STATE_SELECT:
                        if self.game.is_valid_selection(r, c, self.game.current_player):
                            current_highlight_color = self.HOVER_COLOR
                    elif self.state == self.STATE_PUSH and self.selected_cell:
                        sr_sel, sc_sel = self.selected_cell
                        if grid_pos_tuple := self.pixel_to_cell(mouse_pos):
                            if grid_pos_tuple == self.selected_cell:
                                current_highlight_color = self.SELECT_COLOR
                            elif self.game.is_valid_target(sr_sel, sc_sel, r, c):
                                current_highlight_color = self.VALID_TARGET_HOVER_COLOR
                if self.selected_cell == (r, c):
                    current_highlight_color = self.SELECT_COLOR
                if current_highlight_color:
                    pygame.draw.rect(self.screen, current_highlight_color, cell_rect)
                piece = self.game.board[r][c]
                if piece:
                    draw_text_centered(self.screen, piece, self.large_font, self.TEXT_COLOR, cell_rect.center)
                pygame.draw.rect(self.screen, self.GRID_COLOR, cell_rect, 3)

    def _draw_game_over_screen(self):
        if not self.game or not self.game.winner:
            return

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        winner_symbol = self.game.winner
        winner_info = self.player_types.get(winner_symbol, 'human')

        if winner_symbol == "Draw":
            end_text = "It's a Draw!"
        else:
            end_text = f"Player {winner_symbol} ({winner_info}) Wins!"

        draw_text_centered(self.screen, end_text, self.endgame_font, (220, 220, 50),
                           (self.screen_width // 2, self.screen_height // 2 - 120))

        btn_color = self.BUTTON_COLOR
        if self.post_game_return_to_menu_button_rect.collidepoint(pygame.mouse.get_pos()):
            btn_color = self.BUTTON_HOVER_COLOR
        pygame.draw.rect(self.screen, btn_color, self.post_game_return_to_menu_button_rect, border_radius=8)
        draw_text_centered(self.screen, "Return to Main Menu", self.font, self.TEXT_COLOR,
                           self.post_game_return_to_menu_button_rect.center)

    def _draw_replay_finished_screen(self):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        finish_text = "Replay Finished!"
        draw_text_centered(self.screen, finish_text, self.endgame_font, (200, 200, 255),
                           (self.screen_width // 2, self.screen_height // 2 - 180))
        replay_btn_color = self.BUTTON_COLOR
        if self.replay_again_button_rect.collidepoint(pygame.mouse.get_pos()):
            replay_btn_color = self.BUTTON_HOVER_COLOR
        pygame.draw.rect(self.screen, replay_btn_color, self.replay_again_button_rect, border_radius=8)
        draw_text_centered(self.screen, "Replay This Game", self.font, self.TEXT_COLOR,
                           self.replay_again_button_rect.center)
        menu_btn_color = self.BUTTON_COLOR
        if self.post_game_return_to_menu_button_rect.collidepoint(pygame.mouse.get_pos()):
            menu_btn_color = self.BUTTON_HOVER_COLOR
        pygame.draw.rect(self.screen, menu_btn_color, self.post_game_return_to_menu_button_rect, border_radius=8)
        draw_text_centered(self.screen, "Return to Main Menu", self.font, self.TEXT_COLOR,
                           self.post_game_return_to_menu_button_rect.center)
