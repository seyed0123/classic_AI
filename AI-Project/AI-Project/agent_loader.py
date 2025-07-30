import importlib.util
from typing import Callable


def load_agent(agent_path: str) -> Callable:
    """
    Dynamically load a Python file at `agent_path` which defines:
       def agent_move():
       ...
    Returns a reference to that function.
    """
    spec = importlib.util.spec_from_file_location("agent_module", agent_path)
    agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_module)

    if not hasattr(agent_module, 'agent_move'):
        raise ValueError(f"Agent file '{agent_path}' does not define 'agent_move' function.")

    return getattr(agent_module, 'agent_move')
