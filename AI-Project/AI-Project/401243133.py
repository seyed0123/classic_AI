from typing import List, Optional, Tuple
from agent_utils import get_all_valid_moves
import random
from datetime import datetime


MAX_DEPTH = 3



def agent_move(board: List[List[Optional[str]]], player_symbol: str) -> Tuple[int, int, int, int]:
    best_score = float('-inf')
    best_move = None
    random.seed(datetime.now().timestamp())
    board_size = len(board)

    valid_moves = get_all_valid_moves(board, player_symbol)
    if not valid_moves:
        return (0, 0, 0, 0)
    

    moves_played = sum(cell is not None for row in board for cell in row)
    if moves_played <= 2 and board_size==5:
        return random.choice(valid_moves)
    
    eval_func = evaluate3  if board_size == 3 else evaluate

    for move in valid_moves:
        new_board = apply_move(fast_copy_board(board), move, player_symbol)
        score = alpha_beta(new_board, MAX_DEPTH - 1, float('-inf'), float('inf'), False, player_symbol,eval_func)
        r = random.randint(1,100)
        if score > best_score or (r == 1 and score > -10):
            best_score = score
            best_move = move

    return best_move if best_move else (0, 0, 0, 0)


def alpha_beta(board, depth, alpha, beta, maximizing, player_symbol,eval_func):

    winner = check_winner(board)
    opponent = 'O' if player_symbol == 'X' else 'X'
    if winner == player_symbol:
        return 10000 + 10*depth  # Prefer faster wins
    elif winner == opponent:
        return -100000 - 10*depth  # Avoid slow losses
    elif depth == 0:
        return eval_func(board, player_symbol)

    current_player = player_symbol if maximizing else opponent
    moves = get_all_valid_moves(board, current_player)
    if not moves:
        return eval_func(board, player_symbol)

    if maximizing:
        max_eval = float('-inf')
        for move in moves:
            new_board = apply_move(fast_copy_board(board), move, current_player)
            eval = alpha_beta(new_board, depth - 1, alpha, beta, False, player_symbol,eval_func)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            new_board = apply_move(fast_copy_board(board), move, current_player)
            eval = alpha_beta(new_board, depth - 1, alpha, beta, True, player_symbol,eval_func)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def evaluate(board: List[List[Optional[str]]], player_symbol: str, weights=None) -> int:
    if weights is None:
        weights = {
            'max_line': 30,
            'threat': 100,
            'center': 2,
            'fork': 20,
            'disrupt': 5
        }

    opponent = 'O' if player_symbol == 'X' else 'X'
    threats,forks,disruption = count_metrics(board,player_symbol)
    threatso,forkso,disruptiono = count_metrics(board,opponent)
    return (
        weights['max_line'] * (max_contiguous(board, player_symbol) - 3*max_contiguous(board, opponent)) +
        weights['threat'] * (threats - 3*threatso) +
        weights['center'] * (center_density(board, player_symbol) - center_density(board, opponent)) +
        weights['fork'] * (forks - 3*forkso) +
        weights['disrupt'] * (disruption - disruptiono)
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

def center_density(board: List[List[Optional[str]]], symbol: str) -> int:
    N = len(board)
    center = N // 2
    score = 0
    for r in range(N):
        for c in range(N):
            if board[r][c] == symbol:
                dist = abs(r - center) + abs(c - center)
                score += (N - dist)
    return score

def count_metrics(board: List[List[Optional[str]]], symbol: str) -> Tuple[int,int,int]:

    N = len(board)
    lines = []

    lines.extend(board)
    lines.extend([[board[r][c] for r in range(N)] for c in range(N)])
    lines.append([board[i][i] for i in range(N)])
    lines.append([board[i][N - 1 - i] for i in range(N)])

    threats = 0
    forks = 0
    disruption = 0
    opponent = 'O' if symbol == 'X' else 'X'
    for line in lines:
        if symbol in line and opponent in line:
            disruption += 1
        if line.count(symbol) == N - 2:
            forks += 1
        if line.count(symbol) == N - 1:
            threats += 1
    return threats,forks,disruption

def evaluate3(board: List[List[Optional[str]]], player_symbol: str) -> int:
    opponent = 'O' if player_symbol == 'X' else 'X'
    return (
        max_contiguous(board, player_symbol) -
        max_contiguous(board, opponent)
    )

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