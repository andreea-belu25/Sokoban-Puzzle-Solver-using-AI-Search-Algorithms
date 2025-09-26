from sokoban.map import Map
from search_methods.solver import Solver
from sokoban.moves import BOX_LEFT

class IDAStar(Solver):
    def __init__(self, map: Map, heuristic):
        super().__init__(map)
        self.heuristic = heuristic
        self.explored_states = 0
        self.solution = None
        self.moves = None
        self.visited_states = {}  # used to detect cycles in each iteration

        # keep the best solution reached so far
        self.best_solution = None
        self.best_moves = None
        self.best_explored_states = 0
       # self.best_pull_count = float('inf')


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


    def ida_star(self, path, moves, g, threshold, current_pull_count = 0):
        current_state = path[len(path) - 1] #  extract the last state from the path
        self.explored_states += 1

        # check if it's a goal state
        if current_state.is_solved():
            self.best_solution = path.copy()
            self.best_moves = moves.copy()
            self.best_explored_states = self.explored_states
            # self.best_pull_count = current_pull_count
            return True, 0 # a solution was found

        state_key = self.player_boxes_positions(current_state)
        
        # check if this was already visited so as to avoid cycles in path
        if state_key in self.visited_states:
            return False, float('inf')
        
        # otherwise, mark it as visited
        self.visited_states[state_key] = 1

        heuristic_value = self.heuristic(current_state)

        # if the heuristic value is infinity => this can't lead to a valid solution
        if heuristic_value == float('inf'):
            return False, float('inf')

        f = g + heuristic_value

        # return f as the minimum threshold for the next iteration 
        if f > threshold:
            return False, f

        min_cost = float('inf')

        possible_moves = current_state.filter_possible_moves()

        # try all possible moves
        for move in possible_moves:

            # count all pull moves
            # new_pull_count = current_pull_count
            # if move >= BOX_LEFT:
            #     new_pull_count += 1

            # go to the next state
            next_state = current_state.copy()
            next_state.apply_move(move)

            # check if the next state is promising
            next_heuristic = self.heuristic(next_state)
            if next_heuristic == float('inf'):
                continue

            path.append(next_state)
            moves.append(move)

            # search from the new state
            is_solution, new_threshold = self.ida_star(path, moves, g + 1, threshold)

            if is_solution:
                return True, 0

            # update min_cost for the next iteration
            if new_threshold < min_cost:
                min_cost = new_threshold
            
            # backtracking
            path.pop()
            moves.pop()
        
        # if nothing was found, return the min_cost for the next iteration
        return False, min_cost 


    def solve(self):
        # start with the initial state
        path = [self.map]
        moves = []
        self.explored_states = 0
        self.best_solution = None
        self.best_moves = None
        self.best_explored_states = 0
        #self.best_pull_count = float('inf')

        # initialize the heuristic value considering the initial state
        initial_heuristic = self.heuristic(self.map)

        # the initial state is unsolvable
        if initial_heuristic == float('inf'):
            return None

        threshold = initial_heuristic

        iteration = 0
        # safeguard against infinite loops
        max_iterations = 200  
        
        while iteration < max_iterations:
            iteration += 1
            self.visited_states = {} # reset this for each iteration

            is_solution, new_threshold = self.ida_star(path, moves, 0, threshold)
            
            # a solution was found
            if is_solution:
                self.solution = self.best_solution[-1] # final state
                self.moves = self.best_moves
                print(self.solution)
                return moves

            # the map is without solution            
            if new_threshold == float('inf'):
                return None

            # for the next iteration
            threshold = new_threshold
            
        return None
