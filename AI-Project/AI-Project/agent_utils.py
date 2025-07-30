from typing import List, Optional, Tuple

EMPTY_CELL = None


def get_possible_selections(board: List[List[Optional[str]]], player_symbol: str) -> List[Tuple[int, int]]:
    """
    Finds all valid source cells a player can select from the rim.

    Args:
        board: The current game board state.
        player_symbol: The symbol of the player ('X' or 'O').

    Returns:
        A list of (row, col) tuples representing valid cells to select.
    """
    size = len(board)
    rim_cells_coords = []
    for r_idx in range(size):
        for c_idx in range(size):
            if r_idx == 0 or r_idx == size - 1 or c_idx == 0 or c_idx == size - 1:
                rim_cells_coords.append((r_idx, c_idx))

    empty_rim_selections = []
    player_rim_selections = []

    for r, c in rim_cells_coords:
        if board[r][c] == EMPTY_CELL:
            empty_rim_selections.append((r, c))
        elif board[r][c] == player_symbol:
            player_rim_selections.append((r, c))

    # The rule is: if empty cells exist on the rim, player MUST select one of them.
    # Otherwise, they must select one of their own pieces on the rim.
    if empty_rim_selections:
        return empty_rim_selections
    else:
        return player_rim_selections


def get_all_valid_moves(board: List[List[Optional[str]]], player_symbol: str) -> List[Tuple[int, int, int, int]]:
    """
    Generates a list of all possible valid moves for a given player and board state.

    Args:
        board: The current game board state.
        player_symbol: The symbol of the player making the move.

    Returns:
        A list of valid moves, where each move is a tuple (src_r, src_c, tgt_r, tgt_c).
    """
    size = len(board)
    possible_selections = get_possible_selections(board, player_symbol)

    if not possible_selections:
        return []

    all_genuinely_valid_moves: List[Tuple[int, int, int, int]] = []

    for sr, sc in possible_selections:
        candidate_targets_for_src = [
            (sr, 0),
            (sr, size - 1),
            (0, sc),
            (size - 1, sc)
        ]

        actual_targets_for_src = set()

        for tr, tc in candidate_targets_for_src:
            if sr == tr and sc == tc:  # Target cannot be the source itself
                continue
            actual_targets_for_src.add((tr, tc))

        for tr_final, tc_final in list(actual_targets_for_src):
            all_genuinely_valid_moves.append((sr, sc, tr_final, tc_final))

    return all_genuinely_valid_moves

def apply_move(board: List[List[Optional[str]]], move: Tuple[int, int, int, int], player: str) -> List[List[Optional[str]]]:
    src_r, src_c, tgt_r, tgt_c = move
    new_board = fast_copy_board(board)

    if src_r == tgt_r:
        row = src_r
        if tgt_c < src_c:
            for c in range(src_c, tgt_c, -1):
                new_board[row][c] = new_board[row][c - 1]
        else:
            for c in range(src_c, tgt_c):
                new_board[row][c] = new_board[row][c + 1]
        new_board[row][tgt_c] = player
    else:
        col = src_c
        if tgt_r < src_r:
            for r in range(src_r, tgt_r, -1):
                new_board[r][col] = new_board[r - 1][col]
        else:
            for r in range(src_r, tgt_r):
                new_board[r][col] = new_board[r + 1][col]
        new_board[tgt_r][col] = player

    return new_board


def check_winner(board: List[List[Optional[str]]]) -> Optional[str]:
    N = len(board)
    for i in range(N):
        if board[i][0] and all(board[i][j] == board[i][0] for j in range(N)):
            return board[i][0]
        if board[0][i] and all(board[j][i] == board[0][i] for j in range(N)):
            return board[0][i]

    if board[0][0] and all(board[i][i] == board[0][0] for i in range(N)):
        return board[0][0]
    if board[0][N - 1] and all(board[i][N - 1 - i] == board[0][N - 1] for i in range(N)):
        return board[0][N - 1]
    return None

def fast_copy_board(board: List[List[Optional[str]]]) -> List[List[Optional[str]]]:
    return [row[:] for row in board]