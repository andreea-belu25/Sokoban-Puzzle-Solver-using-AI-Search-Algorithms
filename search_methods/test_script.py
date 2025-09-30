import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from sokoban.map import Map
from sokoban.moves import *
from search_methods.simulated_annealing import SimulatedAnnealing
from search_methods.ida_star import IDAStar
from search_methods.heuristics import *

def solve_map(yaml_path, algorithm = SimulatedAnnealing, heuristic = efficient_heuristic):
    print(f"Loading map from: {yaml_path}")
    game_map = Map.from_yaml(yaml_path)
    print(game_map)
    
    solver = algorithm(game_map, heuristic)

    # solve the puzzle
    print(f"Solving the puzzle...")
    start_time = time.time()
    solution_moves = solver.solve()
    end_time = time.time()
    print(f"Puzzle solved in {end_time - start_time:.2f} seconds")
    
    if solution_moves is None:
        print("No solution found for this puzzle!")
        return None
    
    total_steps = len(solution_moves)
    print(f"Solution length: {total_steps} steps")
    
    print(f"States explored: {solver.explored_states}")


def test_maps():
    maps = [
        "../tests/easy_map1.yaml",
        "../tests/easy_map2.yaml",
        "../tests/medium_map1.yaml",
        "../tests/medium_map2.yaml",
        "../tests/hard_map1.yaml",
        "../tests/hard_map2.yaml",
        "../tests/large_map1.yaml",
        "../tests/large_map2.yaml",
        "../tests/super_hard_map1.yaml",
    ]
    
    for yaml_path in maps:
        if os.path.exists(yaml_path):
            print(f"\n\n===== Testing {os.path.basename(yaml_path)} =====\n")
            result = solve_map(yaml_path, SimulatedAnnealing, efficient_heuristic)
        else:
            print(f"Map file not found: {yaml_path}")


if __name__ == "__main__":
    test_maps()
