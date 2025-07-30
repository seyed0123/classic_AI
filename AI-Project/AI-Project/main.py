import datetime
import json
import multiprocessing
import os
import queue
import sys
from typing import Optional, Callable, List, Dict, Any

import pygame

from agent_loader import load_agent
from game import XOShiftGame
from ui import XOShiftUI, REPLAYS_DIR

AGENT_TIME_LIMIT = 2.0
MAX_TURNS = 250
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 850
import random

def agent_process_wrapper(agent_fn: Callable, board_copy: List[List[Optional[str]]],
                          player_symbol: str, result_queue: multiprocessing.Queue):
    try:
        move = agent_fn(board_copy, player_symbol)
        result_queue.put(move)
    except Exception as e:
        result_queue.put(e)


def main_loop():
    pygame.init()
    multiprocessing.freeze_support()

    if not os.path.exists(REPLAYS_DIR):
        try:
            os.makedirs(REPLAYS_DIR)
            print(f"Created directory: {REPLAYS_DIR}")
        except OSError as e:
            print(f"Error creating directory {REPLAYS_DIR}: {e}. Replays may not save.")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("XOShift Game")
    clock = pygame.time.Clock()

    ui = XOShiftUI(screen)
    game: Optional[XOShiftGame] = None

    agent1: Optional[Callable] = None
    agent2: Optional[Callable] = None
    agents = ["AI-Project/AI-Project/basic_agent.py","AI-Project/AI-Project/401243133.py"]
    

    current_move_history: List[Dict[str, Any]] = []
    should_record_current_game = False
    turn_count = 0

    loaded_replay_moves: List[Dict[str, Any]] = []
    current_replay_index = 0
    current_replay_filename: Optional[str] = None

    running = True
    while running:
        
        random.shuffle(agents)
        agent1_path_config = agents[0]
        agent2_path_config = agents[1]

        if game and not game.winner and turn_count >= MAX_TURNS:
            game.winner = "Draw"
            ui.state = XOShiftUI.STATE_GAME_OVER
            print(f"Game ended in a draw after reaching the maximum of {MAX_TURNS} turns.")

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                break
        if not running:
            continue

        ui_event_to_process = pygame.event.Event(pygame.NOEVENT)
        if events:
            mouse_down_events = [e for e in events if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1]
            if mouse_down_events:
                ui_event_to_process = mouse_down_events[0]
            else:
                key_down_events = [e for e in events if e.type == pygame.KEYDOWN]
                if key_down_events:
                    ui_event_to_process = key_down_events[0]

        action = ui.handle_event(ui_event_to_process)

        if action:
            if action["action"] == "quit":
                running = False
            elif action["action"] == "start_game":
                board_size = action["size"]
                game_mode = action["mode"]
                should_record_current_game = action.get("record_replay", False) and game_mode != "replay-select-file"

                try:
                    game = XOShiftGame(size=board_size)
                    turn_count = 0
                except ValueError as e:
                    print(f"Error initializing game: {e}. Returning to menu.")
                    game = None
                    ui.set_game(None)
                    continue

                agent1_name = os.path.basename(agent1_path_config).replace(".py", "")
                agent2_name = os.path.basename(agent2_path_config).replace(".py", "")

                if game_mode == "human-human":
                    ui.player_types = {'X': 'human', 'O': 'human'}
                elif game_mode == "human-agent":
                    ui.player_types = {'X': 'human', 'O': agent2_name}
                elif game_mode == "agent-agent":
                    ui.player_types = {'X': agent1_name, 'O': agent2_name}

                ui.set_game(game)
                current_move_history = []
                ui.replay_finished = False

                agent1, agent2 = None, None
                if game_mode == "human-agent":
                    try:
                        agent2 = load_agent(agent2_path_config)
                    except Exception as e:
                        print(f"Error loading agent 2: {e}. Mode to human-human.")
                elif game_mode == "agent-agent":
                    try:
                        agent1 = load_agent(agent1_path_config)
                        agent2 = load_agent(agent2_path_config)
                    except Exception as e:
                        print(f"Error loading agents: {e}. Mode to human-human.")

                if game:
                    ui.state = XOShiftUI.STATE_SELECT
                    if game_mode == "agent-agent" and agent1:
                        ui.state = XOShiftUI.STATE_WAITING

            elif action["action"] == "load_replay":
                current_replay_filename = action["filename"]
                replay_filepath = os.path.join(REPLAYS_DIR, current_replay_filename)
                try:
                    with open(replay_filepath, "r") as f:
                        replay_data = json.load(f)

                    if isinstance(replay_data, list):
                        loaded_replay_moves = replay_data
                        board_size_for_replay = loaded_replay_moves[0].get("board_size", ui.selected_board_size)
                        ui.player_types = {'X': 'Player 1', 'O': 'Player 2'}
                    elif isinstance(replay_data, dict):
                        metadata = replay_data.get("metadata", {})
                        loaded_replay_moves = replay_data.get("moves", [])
                        board_size_for_replay = metadata.get("board_size", ui.selected_board_size)
                        ui.player_types = {
                            'X': metadata.get('player_x_type', 'Player 1'),
                            'O': metadata.get('player_o_type', 'Player 2')
                        }
                    else:
                        raise ValueError("Replay file has invalid format.")

                    if not loaded_replay_moves:
                        raise ValueError("Replay file contains no moves.")

                    game = XOShiftGame(size=board_size_for_replay)
                    ui.set_game(game)
                    ui.state = XOShiftUI.STATE_REPLAY
                    current_replay_index = 0
                    ui.replay_finished = False
                    _apply_replay_moves_to_index(game, loaded_replay_moves, 0)
                except Exception as e:
                    print(f"Error loading replay file '{replay_filepath}': {e}. Returning to menu.")
                    ui.set_game(None)

            elif action["action"] == "apply_move" and game and ui.state != XOShiftUI.STATE_WAITING:
                sr, sc, tr, tc = action["move"]
                player_making_move = game.current_player
                if game.apply_move(sr, sc, tr, tc, player_making_move):
                    turn_count += 1
                    if should_record_current_game:
                        current_move_history.append({
                            "player": player_making_move, "src_r": sr, "src_c": sc,
                            "tgt_r": tr, "tgt_c": tc
                        })
                    if not game.winner:
                        game.switch_player()
                        is_next_player_human = not ((ui.selected_mode == "agent-agent") or (
                                ui.selected_mode == "human-agent" and game.current_player_index == 1 and agent2))
                        ui.state = XOShiftUI.STATE_SELECT if is_next_player_human else XOShiftUI.STATE_WAITING
                    else:
                        ui.state = XOShiftUI.STATE_GAME_OVER
                    ui.selected_cell = None

            elif action["action"] == "return_to_menu_ingame":
                game = None
                ui.set_game(None)
                current_move_history = []
                loaded_replay_moves = []
                current_replay_filename = None

            elif action["action"] == "return_to_menu":
                if game and ui.state == XOShiftUI.STATE_GAME_OVER and should_record_current_game and current_move_history:
                    mode_str = ui.selected_mode.replace("human", "H").replace("agent", "A").replace("-vs-", "-")
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"xo_{game.size}x{game.size}_{mode_str}_{timestamp}.json"
                    filepath = os.path.join(REPLAYS_DIR, filename)

                    metadata = {
                        "board_size": game.size,
                        "game_mode": ui.selected_mode,
                        "player_x_type": ui.player_types.get('X', 'unknown'),
                        "player_o_type": ui.player_types.get('O', 'unknown'),
                        "winner": game.winner
                    }
                    replay_data = {"metadata": metadata, "moves": current_move_history}

                    try:
                        with open(filepath, "w") as f:
                            json.dump(replay_data, f, indent=4)
                        print(f"Game history saved: {filepath}")
                    except Exception as e:
                        print(f"Error saving game history to {filepath}: {e}")

                game = None
                ui.set_game(None)
                current_move_history = []
                loaded_replay_moves = []
                current_replay_filename = None

            elif action["action"] == "replay_again" and game and loaded_replay_moves:
                ui.state = XOShiftUI.STATE_REPLAY
                current_replay_index = 0
                ui.replay_finished = False
                _apply_replay_moves_to_index(game, loaded_replay_moves, 0)

        if game and not game.winner and ui.state == XOShiftUI.STATE_WAITING:
            active_agent: Optional[Callable] = None
            player_whose_turn_is_it = game.current_player

            if ui.selected_mode == "human-agent" and game.current_player_index == 1 and agent2:
                active_agent = agent2
            elif ui.selected_mode == "agent-agent":
                active_agent = agent1 if game.current_player_index == 0 else agent2

            if active_agent:
                ui.draw()
                pygame.display.flip()

                board_copy = [[cell for cell in row] for row in game.board]
                result_queue = multiprocessing.Queue()
                agent_process = multiprocessing.Process(target=agent_process_wrapper,
                                                        args=(active_agent, board_copy, player_whose_turn_is_it,
                                                              result_queue))
                agent_process.start()
                agent_move_coords, agent_exception, timed_out = None, None, False

                try:
                    agent_output = result_queue.get(timeout=AGENT_TIME_LIMIT)
                    if isinstance(agent_output, Exception):
                        agent_exception = agent_output
                    else:
                        agent_move_coords = agent_output
                except queue.Empty:
                    timed_out = True
                except Exception as e:
                    agent_exception = e

                if agent_process.is_alive():
                    agent_process.terminate()
                agent_process.join(timeout=0.5)
                if agent_process.is_alive():
                    agent_process.kill()
                    agent_process.join()

                if agent_exception:
                    print(
                        f"Agent {player_whose_turn_is_it} crashed: {agent_exception}. Opponent's turn.")
                    game.switch_player()
                elif timed_out:
                    print(f"Agent {player_whose_turn_is_it} timed out. Opponent's turn.")
                    turn_count += 1
                    game.switch_player()
                elif agent_move_coords:
                    sr, sc, tr, tc = agent_move_coords
                    if game.apply_move(sr, sc, tr, tc, player_whose_turn_is_it):
                        turn_count += 1
                        if should_record_current_game:
                            current_move_history.append({"player": player_whose_turn_is_it, "src_r": sr, "src_c": sc,
                                                         "tgt_r": tr, "tgt_c": tc})
                        if not game.winner:
                            game.switch_player()
                    else:
                        print(
                            f"Agent {player_whose_turn_is_it} invalid move: {agent_move_coords}. Opponent's turn.")
                        game.switch_player()
                else:
                    print(f"Agent {player_whose_turn_is_it} no move/error. Opponent's turn.")
                    game.switch_player()

                if game.winner:
                    ui.state = XOShiftUI.STATE_GAME_OVER
                else:
                    is_next_human = not ((ui.selected_mode == "agent-agent") or (
                            ui.selected_mode == "human-agent" and game.current_player_index == 1 and agent2))
                    ui.state = XOShiftUI.STATE_SELECT if is_next_human else XOShiftUI.STATE_WAITING

        if ui.state == XOShiftUI.STATE_REPLAY and game and not ui.replay_finished:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        if current_replay_index < len(loaded_replay_moves):
                            _apply_replay_moves_to_index(game, loaded_replay_moves, current_replay_index + 1)
                            current_replay_index += 1
                        if current_replay_index == len(loaded_replay_moves):
                            ui.replay_finished = True
                    elif event.key == pygame.K_LEFT:
                        if current_replay_index > 0:
                            current_replay_index -= 1
                            _apply_replay_moves_to_index(game, loaded_replay_moves, current_replay_index)
                            ui.replay_finished = False
                    break

        ui.draw()
        clock.tick(30)

    if game and game.winner and should_record_current_game and current_move_history:
        mode_str = ui.selected_mode.replace("human", "H").replace("agent", "A").replace("-vs-", "-")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"xo_{game.size}x{game.size}_{mode_str}_{timestamp}.json"
        filepath = os.path.join(REPLAYS_DIR, filename)

        metadata = {
            "board_size": game.size,
            "game_mode": ui.selected_mode,
            "player_x_type": ui.player_types.get('X', 'unknown'),
            "player_o_type": ui.player_types.get('O', 'unknown'),
            "winner": game.winner
        }
        replay_data = {"metadata": metadata, "moves": current_move_history}
        try:
            with open(filepath, "w") as f:
                json.dump(replay_data, f, indent=4)
            print(f"Game history (on quit) saved to {filepath}")
        except Exception as e:
            print(f"Error saving game history (on quit) to {filepath}: {e}")

    pygame.quit()
    sys.exit()


def _apply_replay_moves_to_index(game_instance: XOShiftGame, moves: List[Dict[str, Any]],
                                 target_move_count: int):
    # Reset the game board to a clean state
    board_size = game_instance.size
    game_instance.board = [[game_instance.EMPTY for _ in range(board_size)] for _ in range(board_size)]
    game_instance.winner = None
    game_instance.winning_line_coords = None
    game_instance.current_player_index = 0

    # Apply moves one by one up to the target index
    for i in range(target_move_count):
        if i >= len(moves):
            break
        move_data = moves[i]
        p = move_data.get("player")
        sr, sc, tr, tc = move_data.get("src_r"), move_data.get("src_c"), move_data.get("tgt_r"), move_data.get("tgt_c")

        if None in [p, sr, sc, tr, tc]:
            print(f"Replay Warning: Move {i + 1} has incomplete data. Skipping.")
            continue

        try:
            # Ensure the correct player is set for the move
            game_instance.current_player_index = game_instance.PLAYERS.index(p)
        except ValueError:
            print(f"Replay Warning: Player symbol '{p}' in move {i + 1} is invalid. Skipping move.")
            continue

        success = game_instance.apply_move(sr, sc, tr, tc, p)
        if not success:
            print(
                f"Replay Warning: Move {i + 1} ({p}: ({sr},{sc})->({tr},{tc})) was invalid during replay application.")

        if not game_instance.winner:
            game_instance.switch_player()


if __name__ == "__main__":
    main_loop()
