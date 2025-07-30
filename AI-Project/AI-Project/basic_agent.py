from typing import List, Optional, Tuple
from agent_utils import get_all_valid_moves,apply_move,check_winner
import copy
import random
from datetime import datetime
random.seed(datetime.now().timestamp())

MAX_DEPTH = 2  # Adjust for performance vs. strength


def agent_move(board: List[List[Optional[str]]], player_symbol: str) -> Tuple[int, int, int, int]:
    best_score = float('-inf')
    best_move = None
    random.seed(datetime.now().timestamp())

    for move in get_all_valid_moves(board, player_symbol):
        new_board = apply_move(copy.deepcopy(board), move, player_symbol)
        score = alpha_beta(new_board, MAX_DEPTH - 1, float('-inf'), float('inf'), False, player_symbol)
        r = random.randint(1,100)
        if score > best_score or r == 1:
            best_score = score
            best_move = move

    return best_move if best_move else (0, 0, 0, 0)


def alpha_beta(board, depth, alpha, beta, maximizing, player_symbol):
    winner = check_winner(board)
    opponent = 'O' if player_symbol == 'X' else 'X'
    if winner == player_symbol:
        return 1000 + depth  # Prefer faster wins
    elif winner == opponent:
        return -1000 - depth  # Avoid slow losses
    elif depth == 0:
        return evaluate(board, player_symbol)

    current_player = player_symbol if maximizing else opponent
    moves = get_all_valid_moves(board, current_player)
    if not moves:
        return evaluate(board, player_symbol)

    if maximizing:
        max_eval = float('-inf')
        for move in moves:
            new_board = apply_move(copy.deepcopy(board), move, current_player)
            eval = alpha_beta(new_board, depth - 1, alpha, beta, False, player_symbol)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            new_board = apply_move(copy.deepcopy(board), move, current_player)
            eval = alpha_beta(new_board, depth - 1, alpha, beta, True, player_symbol)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def evaluate(board: List[List[Optional[str]]], player_symbol: str) -> int:
    opponent = 'O' if player_symbol == 'X' else 'X'
    return (
        max_contiguous(board, player_symbol) -
        max_contiguous(board, opponent)
    )


def max_contiguous(board: List[List[Optional[str]]], symbol: str) -> int:
    N = len(board)
    max_len = 0

    for row in board:
        count = 0
        for cell in row:
            count = count + 1 if cell == symbol else 0
            max_len = max(max_len, count)

    for col in range(N):
        count = 0
        for row in range(N):
            count = count + 1 if board[row][col] == symbol else 0
            max_len = max(max_len, count)

    count = 0
    for i in range(N):
        count = count + 1 if board[i][i] == symbol else 0
        max_len = max(max_len, count)

    count = 0
    for i in range(N):
        count = count + 1 if board[i][N - 1 - i] == symbol else 0
        max_len = max(max_len, count)

    return max_len
