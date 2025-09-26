import numpy as np
from sokoban.map import Map
from search_methods.solver import Solver
from sokoban.moves import BOX_LEFT
import random
import math
from search_methods.heuristics import *

class SimulatedAnnealing(Solver):
    def __init__(self, map: Map, heuristic):
        super().__init__(map)
        self.initial_temp = 700.0   # higher values permit more exploration
        self.cooling_rate = 0.9999  # very slow cooling
        self.explored_states = 0
        self.heuristic = heuristic

        # keep the best solution reached so far
        self.best_moves = []
        self.best_state = None
        self.best_energy = float('inf')
    

    def softmax(self, x: np.array) -> float:
        '''
            Convert energies to probabilities;
            Select moves probabilistically based on their energies;
            Higher values => higher probabilities.
        '''
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()


    def player_boxes_positions(self, state):
        '''
            Extracts the positions of boxes and also the player's position for a given state.
        '''
        player_position = (state.player.x, state.player.y)
        
        box_positions = []

        for box in state.boxes.values():
            box_positions.append((box.x, box.y))
            
        box_positions.sort()

        return (player_position, tuple(box_positions))


    def calculate_energy(self, current_state, current_moves):
        # count all pull moves
        pull_moves_count = 0
        
        # for move in current_moves:
        #     if move >= BOX_LEFT:
        #         pull_moves_count += 1

        # if current_state.is_solved():
        #     return pull_moves_count
        
        # distance to goal
        heuristic_value = self.heuristic(current_state)
        
        # unsolvable state
        if heuristic_value == float('inf'):
            return float('inf')
        
        # the emphasis is on the distance goal and the number of pull moves
        # rather than on the number of total moves  
        return heuristic_value + pull_moves_count + len(current_moves) * 0.1


    def solve(self):
        # start searching from the initial state
        current_state = self.map.copy()
        current_temperature = self.initial_temp
        current_moves = []
        current_energy= self.calculate_energy(current_state, current_moves)
        
        # unsolvable
        if current_energy == float('inf'):
            return None

        # initialize best solution
        self.best_state = self.map.copy()
        self.best_moves = []
        self.best_energy = current_energy
        
        alpha = 0.5    # indicates the acceptance probability
        
        final_t = 0.1  # here stops the cooling

        iteration = 0
        max_iterations = 100_000  # safeguard to prevent infinite loops

        in_worse_states = 0       # consecutive worse moves
        
        random.seed(0)            # random seed for reproductibility
        np.random.seed(0)

        while current_temperature > final_t and iteration < max_iterations:
            iteration += 1
            self.explored_states += 1
            
            possible_moves = current_state.filter_possible_moves()

            if not possible_moves:
                # no possible moves - restart from best state with higher temperature
                # escape local minima
                current_temperature = self.initial_temp * 0.7
                current_state = self.best_state.copy()
                current_moves = self.best_moves.copy()
                current_energy = self.best_energy
                in_worse_states = 0
                continue
            
            # test all possible moves with heuristic
            heuristic_moves = []

            for move in possible_moves:
                next_state = current_state.copy()
                next_state.apply_move(move)
                next_energy = self.calculate_energy(next_state, current_moves + [move])
                heuristic_moves.append((move, next_energy))

            # ascending order
            heuristic_moves.sort(key = lambda x: x[1])
            
            infinite_energy_count = 0
            for _, energy in heuristic_moves:
                if energy == float('inf'):
                    infinite_energy_count += 1
            
            # if all moves lead to infinite energy => they lead to unsolvable states => restart
            if infinite_energy_count == len(heuristic_moves) and heuristic_moves:
                current_temperature = self.initial_temp
                current_state = self.best_state.copy()
                current_moves = self.best_moves.copy()
                current_energy = self.best_energy
                in_worse_states = 0
                continue
            
            if random.random() < 0.5:
                # use softmax for biased selection - 50% of the time go to better moves
                random_index = np.random.choice(len(heuristic_moves), p = self.softmax(-np.array([x[1] for x in heuristic_moves])))
            else:
                # 50% times choose purely random
                random_index = random.choice(range(len(heuristic_moves)))

            # get and apply the selected move
            next_move, next_energy = heuristic_moves[random_index]
            next_state = current_state.copy()
            next_state.apply_move(next_move)
            next_moves = current_moves + [next_move]
            
            # calculate delta and decide whether to accept the move
            delta_energy = next_energy - current_energy
            
            # always accept better moves / probabilistically accept worse ones
            if delta_energy <= 0 or random.random() < np.exp(-delta_energy / (current_temperature * alpha)):
                # count how many worse moves we accept
                if delta_energy > 0:
                    in_worse_states += 1
                else:
                    in_worse_states = 0
            
                # if we've been accepting worse moves for too long => restart
                if in_worse_states > 200:
                    current_temperature = self.initial_temp
                    current_state = self.best_state.copy()
                    current_moves = self.best_moves.copy()
                    current_energy = self.best_energy
                    in_worse_states = 0
                    continue
                
                # accept the move
                current_state = next_state
                current_moves = next_moves
                current_energy = next_energy

                # found a better solution => update the best one
                if current_energy < self.best_energy:
                    self.best_state = current_state.copy()
                    self.best_moves = current_moves.copy()
                    self.best_energy = current_energy

                # check if we've solved the map
                if current_state.is_solved():
                    self.best_state = current_state.copy()
                    self.best_moves = current_moves.copy()
                    self.best_energy = current_energy
                    print(self.best_state)
                    break
            
            # cool down temperature
            current_temperature *= self.cooling_rate
        
        # return the solution if exists
        if self.best_state and self.best_state.is_solved():
            return self.best_moves
            
        return None
