from typing import List, Optional, Tuple


class XOShiftGame:
    """
    Encapsulates the XOShift board, rules, move application, and win detection.
    """
    EMPTY = None
    PLAYERS = ['X', 'O']

    def __init__(self, size: int = 5):
        if not 3 <= size <= 5:
            raise ValueError("Board size must be between 3 and 5.")
        self.size = size
        self.board: List[List[Optional[str]]] = [
            [self.EMPTY for _ in range(size)] for _ in range(size)
        ]
        self.current_player_index = 0
        self.winner: Optional[str] = None
        self.last_move = None
        self.winning_line_coords: Optional[List[Tuple[int, int]]] = None  # Stores winning line

    @property
    def current_player(self) -> str:
        return self.PLAYERS[self.current_player_index]

    def switch_player(self) -> None:
        self.current_player_index = (self.current_player_index + 1) % len(self.PLAYERS)

    def is_valid_selection(self, row: int, col: int, player_symbol: str) -> bool:
        if not (row == 0 or row == self.size - 1 or col == 0 or col == self.size - 1):
            return False

        has_empty_rim_cell = False
        for r_idx in range(self.size):
            for c_idx in range(self.size):
                if r_idx == 0 or r_idx == self.size - 1 or c_idx == 0 or c_idx == self.size - 1:
                    if self.board[r_idx][c_idx] == self.EMPTY:
                        has_empty_rim_cell = True
                        break
            if has_empty_rim_cell:
                break

        current_cell_value = self.board[row][col]
        if has_empty_rim_cell:
            return current_cell_value == self.EMPTY
        else:
            return current_cell_value == player_symbol

    def is_valid_target(self, src_row: int, src_col: int, tgt_row: int, tgt_col: int) -> bool:
        if src_row == tgt_row and src_col == tgt_col:
            return False

        is_valid_row_target = (src_row == tgt_row) and \
                              (tgt_col == 0 or tgt_col == self.size - 1)
        is_valid_col_target = (src_col == tgt_col) and \
                              (tgt_row == 0 or tgt_row == self.size - 1)
        return is_valid_row_target or is_valid_col_target

    def get_last_move(self):
        return self.last_move

    def apply_move(self,
                   src_row: int, src_col: int,
                   tgt_row: int, tgt_col: int,
                   player_symbol: str) -> bool:
        if self.winner:
            return False

        if not self.is_valid_selection(src_row, src_col, player_symbol):
            return False
        if not self.is_valid_target(src_row, src_col, tgt_row, tgt_col):
            return False

        if src_row == tgt_row:
            if tgt_col < src_col:
                for col_idx in range(src_col, tgt_col, -1):
                    self.board[src_row][col_idx] = self.board[src_row][col_idx - 1]
            else:
                for col_idx in range(src_col, tgt_col):
                    self.board[src_row][col_idx] = self.board[src_row][col_idx + 1]
        else:
            if tgt_row < src_row:
                for row_idx in range(src_row, tgt_row, -1):
                    self.board[row_idx][src_col] = self.board[row_idx - 1][src_col]
            else:
                for row_idx in range(src_row, tgt_row):
                    self.board[row_idx][src_col] = self.board[row_idx + 1][src_col]

        self.board[tgt_row][tgt_col] = player_symbol
        self.last_move = (src_row, src_col, tgt_row, tgt_col, player_symbol)
        self.check_winner()
        return True

    def check_winner(self) -> None:
        """
        Checks for a winner. If a winner is found, sets self.winner and self.winning_line_coords.
        The win condition is N-in-a-row for an N-sized board.
        """
        self.winner = None
        self.winning_line_coords = None
        n = self.size
        needed_to_win = n

        for symbol in self.PLAYERS:
            # Check rows
            for r in range(n):
                if all(self.board[r][c] == symbol for c in range(n)):
                    self.winner = symbol
                    self.winning_line_coords = [(r, c) for c in range(n)]
                    return

            # Check columns
            for c in range(n):
                if all(self.board[r][c] == symbol for r in range(n)):
                    self.winner = symbol
                    self.winning_line_coords = [(r, c) for r in range(n)]
                    return

            # Check main diagonal (top-left to bottom-right)
            if all(self.board[i][i] == symbol for i in range(n)):
                self.winner = symbol
                self.winning_line_coords = [(i, i) for i in range(n)]
                return

            # Check anti-diagonal (top-right to bottom-left)
            if all(self.board[i][n - 1 - i] == symbol for i in range(n)):
                self.winner = symbol
                self.winning_line_coords = [(i, n - 1 - i) for i in range(n)]
                return

    def is_board_full(self) -> bool:
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == self.EMPTY:
                    return False
        return True
