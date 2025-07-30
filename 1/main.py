import time

from env import Env
from plotting import Plotting

from implemented_agents import BFSAgent, BiIDDFSAgent, AStarAgent, UCSAgent


def main():
    map_name = "test"  # Choose the map file
    use_random_teleports = False  # Change to True to use random teleports
    num_pairs = 2  # Number of random teleport gates if enabled
    FPS = 200  # Frames per second for animation

    start = (5, 25)  # Start position
    goal = (45, 25)  # Goal position
    euclidean_cost = False  # True to use Euclidean distance as cost

    environment = Env(map_name, use_random_teleports, num_pairs)
    agent = BiIDDFSAgent(start, goal, environment, euclidean_cost)     # TODO: your agent herelc ;hl\d,jv
    

    start_time = time.time()
    path, visited = agent.searching()
    end_time = time.time()
    run_time = end_time - start_time
    print(f"Search completed in {run_time:.5f} seconds")

    plot = Plotting(start, goal, environment, FPS)
    plot.animation(path, visited, agent.COST)


if __name__ == "__main__":
    main()



