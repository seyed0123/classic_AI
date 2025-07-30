import pygame
import os
import json
import datetime
import multiprocessing
import queue
from typing import Optional, Callable, List, Dict, Any, Tuple

from ui import XOShiftUI, REPLAYS_DIR
from game import XOShiftGame
from agent_loader import load_agent

def initialize_game_environment(screen_width: int, screen_height: int) -> Tuple[pygame.Surface, pygame.time.Clock, XOShiftUI]:
    if not os.path.exists(REPLAYS_DIR):
        os.makedirs(REPLAYS_DIR, exist_ok=True)
        print(f"Created replay directory: {REPLAYS_DIR}")

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("XOShift Game")
    clock = pygame.time.Clock()
    ui = XOShiftUI(screen)
    return screen, clock, ui


def handle_ui_events(
    events: List[pygame.event.Event],
    ui: XOShiftUI,
    game: Optional[XOShiftGame],
    agent1_path: str,
    agent2_path: str,
    move_history: List[Dict[str, Any]],
    should_record: bool,
    replay_data: Dict[str, Any]
) -> Optional[Tuple[Optional[XOShiftGame], Optional[Callable], Optional[Callable], int, bool, List[Dict[str, Any]], List[Dict[str, Any]], int, Optional[str]]]:
    for event in events:
        if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
            action = ui.handle_event(event)
            if action:
                return _process_ui_action(action, ui, agent1_path, agent2_path, move_history, should_record, replay_data)
    return None


def _process_ui_action(action: Dict[str, Any], ui: XOShiftUI, agent1_path: str, agent2_path: str,
                       move_history: List[Dict[str, Any]], should_record: bool,
                       replay_data: Dict[str, Any]):
    current_replay_index = replay_data["current_index"]
    current_replay_filename = replay_data["filename"]
    loaded_replay_moves = replay_data["loaded_moves"]

    game = None
    agent1 = agent2 = None
    turn_count = 0
    should_record_game = should_record

    if action["action"] == "quit":
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        return None

    elif action["action"] == "start_game":
        size = action["size"]
        mode = action["mode"]
        should_record_game = action.get("record_replay", False) and mode != "replay-select-file"
        game = XOShiftGame(size)
        agent1 = agent2 = None

        try:
            if mode == "human-agent":
                agent2 = load_agent(agent2_path)
            elif mode == "agent-agent":
                agent1 = load_agent(agent1_path)
                agent2 = load_agent(agent2_path)
        except Exception as e:
            print(f"Error loading agents: {e}")
            mode = "human-human"

        ui.player_types = {
            'X': 'human' if mode.startswith("human") else os.path.basename(agent1_path).replace(".py", ""),
            'O': 'human' if mode == "human-human" else os.path.basename(agent2_path).replace(".py", "")
        }

        ui.set_game(game)
        ui.state = XOShiftUI.STATE_SELECT if mode != "agent-agent" else XOShiftUI.STATE_WAITING
        move_history.clear()
        turn_count = 0
        ui.selected_mode = mode

    elif action["action"] == "load_replay":
        current_replay_filename = action["filename"]
        filepath = os.path.join(REPLAYS_DIR, current_replay_filename)
        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            loaded_replay_moves = data["moves"] if isinstance(data, dict) else data
            board_size = data.get("metadata", {}).get("board_size", ui.selected_board_size) if isinstance(data, dict) else ui.selected_board_size
            game = XOShiftGame(size=board_size)
            ui.player_types = {
                'X': data.get("metadata", {}).get("player_x_type", "Player 1"),
                'O': data.get("metadata", {}).get("player_o_type", "Player 2")
            }
            ui.set_game(game)
            _apply_replay_moves_to_index(game, loaded_replay_moves, 0)
            ui.state = XOShiftUI.STATE_REPLAY
            ui.replay_finished = False
            current_replay_index = 0
        except Exception as e:
            print(f"Failed to load replay: {e}")
            ui.set_game(None)

    return (
        game, agent1, agent2, turn_count,
        should_record_game, move_history, loaded_replay_moves,
        current_replay_index, current_replay_filename
    )


def handle_agent_turn(game: XOShiftGame, ui: XOShiftUI,
                      agent1: Optional[Callable], agent2: Optional[Callable],
                      turn_count: int, move_history: List[Dict[str, Any]],
                      record: bool, time_limit: float) -> Tuple[XOShiftGame, int, List[Dict[str, Any]]]:

    agent = None
    if ui.selected_mode == "agent-agent":
        agent = agent1 if game.current_player_index == 0 else agent2
    elif ui.selected_mode == "human-agent" and game.current_player_index == 1:
        agent = agent2

    if agent:
        board_copy = [row[:] for row in game.board]
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=agent_process_wrapper,
                                          args=(agent, board_copy, game.current_player, result_queue))
        process.start()

        try:
            result = result_queue.get(timeout=time_limit)
        except queue.Empty:
            print("Agent timed out.")
            result = None
        except Exception as e:
            print(f"Agent exception: {e}")
            result = None

        if process.is_alive():
            process.terminate()
            process.join()

        if isinstance(result, tuple):
            sr, sc, tr, tc = result
            if game.apply_move(sr, sc, tr, tc, game.current_player):
                turn_count += 1
                if record:
                    move_history.append({
                        "player": game.current_player, "src_r": sr, "src_c": sc, "tgt_r": tr, "tgt_c": tc
                    })
                if not game.winner:
                    game.switch_player()
                else:
                    ui.state = XOShiftUI.STATE_GAME_OVER
        else:
            print("Agent failed or made invalid move. Switching player.")
            game.switch_player()

    return game, turn_count, move_history


def handle_replay_keys(events: List[pygame.event.Event], game: XOShiftGame,
                       moves: List[Dict[str, Any]], current_index: int, ui: XOShiftUI) -> int:
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                if current_index < len(moves):
                    _apply_replay_moves_to_index(game, moves, current_index + 1)
                    current_index += 1
                    if current_index == len(moves):
                        ui.replay_finished = True
            elif event.key == pygame.K_LEFT:
                if current_index > 0:
                    current_index -= 1
                    _apply_replay_moves_to_index(game, moves, current_index)
                    ui.replay_finished = False
    return current_index


def save_replay_if_needed(game: Optional[XOShiftGame], ui: XOShiftUI,
                          move_history: List[Dict[str, Any]], should_record: bool):
    if game and game.winner and should_record and move_history:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        mode_str = ui.selected_mode.replace("human", "H").replace("agent", "A").replace("-vs-", "-")
        filename = f"xo_{game.size}x{game.size}_{mode_str}_{timestamp}.json"
        filepath = os.path.join(REPLAYS_DIR, filename)

        replay_data = {
            "metadata": {
                "board_size": game.size,
                "game_mode": ui.selected_mode,
                "player_x_type": ui.player_types.get('X', 'unknown'),
                "player_o_type": ui.player_types.get('O', 'unknown'),
                "winner": game.winner
            },
            "moves": move_history
        }

        try:
            with open(filepath, "w") as f:
                json.dump(replay_data, f, indent=4)
            print(f"Game replay saved: {filepath}")
        except Exception as e:
            print(f"Failed to save replay: {e}")


def agent_process_wrapper(agent_fn: Callable, board_copy: List[List[Optional[str]]],
                          player_symbol: str, result_queue: multiprocessing.Queue):
    try:
        move = agent_fn(board_copy, player_symbol)
        result_queue.put(move)
    except Exception as e:
        result_queue.put(e)


def _apply_replay_moves_to_index(game_instance: XOShiftGame,
                                 moves: List[Dict[str, Any]],
                                 target_move_count: int):
    size = game_instance.size
    game_instance.board = [[None for _ in range(size)] for _ in range(size)]
    game_instance.current_player_index = 0
    game_instance.winner = None

    for i in range(target_move_count):
        move = moves[i]
        p = move["player"]
        sr, sc, tr, tc = move["src_r"], move["src_c"], move["tgt_r"], move["tgt_c"]
        try:
            game_instance.current_player_index = game_instance.PLAYERS.index(p)
        except ValueError:
            continue
        success = game_instance.apply_move(sr, sc, tr, tc, p)
        if not success:
            print(f"Invalid move during replay: {move}")
        if not game_instance.winner:
            game_instance.switch_player()