import random
from typing import List, Optional, Tuple
import basic_agent
import random_agent
import deep_agent
from multiprocessing import Pool, cpu_count
import your_agent  
from agent_utils import apply_move,check_winner
def play_game(agent_x, agent_o, board_size=3) -> float:
    """
    Plays one game between agent_x as 'X' and agent_o as 'O'.
    Returns 1.0 if X wins, 0.0 if O wins, 0.5 on draw.
    """
    # start with a fresh board
    board: List[List[Optional[str]]] = [[None]*board_size for _ in range(board_size)]
    turn = 0
    while True:
        symbol = 'X' if turn % 2 == 0 else 'O'
        agent = agent_x if symbol == 'X' else agent_o

        # deep‑copy the board before passing to avoid side effects
        board_copy = [row[:] for row in board]
        move = agent(board_copy, symbol)

        # if agent returns the “no‑move” sentinel, treat as resignation/draw
        if move == (0, 0, 0, 0):
            continue

        # apply the move to the real board
        board = apply_move(board, move, symbol)
        winner = check_winner(board)
        if winner:
            return 1.0 if winner == 'X' else 0.0

        turn += 1
        if turn >= 250:
            return 0.5


def evaluate_agent(agent_fn, opponent_fn, games: int = 100, board_size: int = 3) -> float:
    """
    Plays `games` matches between agent_fn vs opponent_fn,
    returns percentage of points scored by agent_fn.
    """
    total_points = 0.0
    for i in range(games):
        r = random.randint(0,1)
        
        if r:
            result = play_game(agent_fn, opponent_fn, board_size)
            total_points += result
            winner = 'my_agent' if result == 1 else 'opponent'
            winner = 'draw' if result == 0.5 else winner
        else:
            result = play_game(opponent_fn,agent_fn, board_size)
            total_points+= -result + 1
            winner = 'my_agent' if result == 0 else 'opponent' 
            winner = 'draw' if result == 0.5 else winner

        print(f"Game {i+1}/{games}: result = {winner}")

    return 100.0 * total_points / games


if __name__ == "__main__":

    win_pct = evaluate_agent(your_agent.agent_move, deep_agent.agent_move, games=30,board_size=5)
    print(f"\nYour agent scored {win_pct:.2f}% points")
