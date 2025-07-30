import random
from typing import List, Optional, Tuple

from agent_utils import get_all_valid_moves


def agent_move(board: List[List[Optional[str]]], player_symbol: str) -> Tuple[int, int, int, int]:
    """
    A purely random agent that finds all possible valid moves and chooses one.
    It relies on agent_utils to get the list of valid moves.
    """
    valid_moves = get_all_valid_moves(board, player_symbol)

    # choose a move
    if valid_moves:
        chosen_move = random.choice(valid_moves)
        return chosen_move
    else:
        # This case is reached if no valid moves are possible
        return 0, 0, 0, 0
