from sokoban.map import Map
import math

def get_targets_boxes_pos(state):
    '''
        Extracts the positions of the targets and boxes from the given state.
    '''
    targets_positions = state.targets
    
    boxes_positions = []

    for box in state.boxes.values():
        boxes_positions.append((box.x, box.y))

    return targets_positions, boxes_positions


def manhattan_dist_heuristic(state):
    '''
        For each box finds the closest distance using Manhattan distance
        and sums all these distances => total_dist.
    '''
    targets_positions, boxes_positions = get_targets_boxes_pos(state)

    total_dist = 0

    for box_pos in boxes_positions:
        min_dist = float('inf')
        for target_position in targets_positions:
            current_dist = abs(box_pos[0] - target_position[0]) + abs(box_pos[1] - target_position[1])
            if current_dist < min_dist:
                min_dist = current_dist
        total_dist += min_dist

    return total_dist


def euclidian_dist_heuristic(state):
    '''
        For each box finds the closest distance using Euclidian distance
        and sums all these distances => total_dist.
    '''
    targets_positions, boxes_positions = get_targets_boxes_pos(state)

    total_dist = 0

    for box_pos in boxes_positions:
        min_dist = float('inf')
        for target_position in targets_positions:
            current_dist = math.sqrt((box_pos[0] - target_position[0])**2 + (box_pos[1] - target_position[1])**2)
            if current_dist < min_dist:
                min_dist = current_dist
        total_dist += min_dist

    # ensure the heuristic is admissible (never overestimates)
    return math.ceil(total_dist)


def not_on_right_place_boxes(state):
    '''
        Identifies boxes that are not place on targets.
    '''
    targets_positions, boxes_positions = get_targets_boxes_pos(state)

    boxes_not_on_right_place = []

    for box_pos in boxes_positions:
        if box_pos not in targets_positions:
            boxes_not_on_right_place.append(box_pos)

    return boxes_not_on_right_place


def is_direct_path_row(target_pos, box_pos, state):
    '''
        Determinates whether a box can reach a target in the same row,
        without encountering any obstacle or any box.
    '''
    obstacles = state.obstacles
    boxes_not_on_targets = not_on_right_place_boxes(state)
    
    if box_pos[0] == target_pos[0]:  # in the same row
        for col in range(min(box_pos[1], target_pos[1]), max(box_pos[1], target_pos[1]) + 1):
            # skip the box position itself
            if (box_pos[0], col) == box_pos:
                continue
                
            # there's an obstacle or another box in the path
            if (box_pos[0], col) in obstacles or (box_pos[0], col) in boxes_not_on_targets:
                return False

        return True
    
    return False  # not in the same row

    
def is_direct_path_column(target_pos, box_pos, state):
    '''
        Determinates whether a box can reach a target in the same column,
        without encountering any obstacle or any box.
    '''
    obstacles = state.obstacles
    boxes_not_on_targets = not_on_right_place_boxes(state)
    
    if box_pos[1] == target_pos[1]:  # in the same column
        for row in range(min(box_pos[0], target_pos[0]), max(box_pos[0], target_pos[0]) + 1):
            # skip the box position itself
            if (row, box_pos[1]) == box_pos:
                continue
                
            # there's an obstacle or another box in the path
            if (row, box_pos[1]) in obstacles or (row, box_pos[1]) in boxes_not_on_targets:
                return False

        return True
    
    return False  # not in the same column


def direct_path_heuristic(state):
    '''
        For each box tries to find an available target that can be reached on the same row / column.
        Returns the sum of Manhattan distances considering all pairs (box, target) or infinity if the heuristic
        cannot find a solution for all boxes. 
    '''
    targets_positions, boxes_positions = get_targets_boxes_pos(state)

    # find all targets that are still not assigned to a box
    available_targets_pos = {}

    for target_position in targets_positions:
        if target_position not in boxes_positions:
            available_targets_pos[target_position] = True
        else:
            available_targets_pos[target_position] = False

    boxes_not_on_right_place = not_on_right_place_boxes(state)
    
    total_dist = 0

    # try to find a direct path to any available target
    for box_pos in boxes_not_on_right_place:
        exists_direct_path = False

        for target_pos, available_target in available_targets_pos.items():
            if available_target == True:
                if is_direct_path_row(target_pos, box_pos, state) or is_direct_path_column(target_pos, box_pos, state):
                    exists_direct_path = True
                    available_targets_pos[target_pos] = False
                    total_dist += abs(box_pos[0] - target_pos[0]) + abs(box_pos[1] - target_pos[1])
                    break
        
        #  exists a box for which there is not a direct path to a target
        if not exists_direct_path:
            return float('inf')
    
    return total_dist


def hungarian_dist_heuristic(state):
    '''
        Assigns each box to a target so as to minimize the total cost
        using a greedy approach of a simplified version of Hungarian alg.
    '''
    targets_positions, boxes_positions = get_targets_boxes_pos(state)
    
    # calculate the minimum distance from each box to any target
    box_distances = []
    count_boxes = 0

    for box_pos in boxes_positions:
        min_dist = float('inf')
        closest_target_idx = -1
        
        count_targets = 0
        for target_pos in targets_positions:
            dist = abs(box_pos[0] - target_pos[0]) + abs(box_pos[1] - target_pos[1])
            if dist < min_dist:
                min_dist = dist
                closest_target_idx = count_targets
            
            count_targets += 1

        box_distances.append((count_boxes, closest_target_idx, min_dist))
        count_boxes += 1

    # sort boxes by their minimum distance to any target
    box_distances.sort(key = lambda x: x[2])

    # initially, all the targets are unused
    used_targets = []
    for _ in range(len(targets_positions)):
        used_targets.append(False)
    
    total_cost = 0

    # assigns each box to its closest available target
    for (box_idx, target_idx, min_dist) in box_distances:
        box_pos = boxes_positions[box_idx]
        best_dist = float('inf')
        found_best_target = False

        count_targets = 0
        best_target_idx = -1
        
        for target_pos in targets_positions:
            if not used_targets[count_targets]:
                dist = abs(box_pos[0] - target_pos[0]) + abs(box_pos[1] - target_pos[1])
                
                if dist < best_dist:
                    best_dist = dist
                    best_target_idx = count_targets
                    found_best_target = True
            
            count_targets += 1

        if found_best_target:
            # assigns the current box to the best available target found
            used_targets[best_target_idx] = True
            total_cost += best_dist
        else:
            # no target available => use the minimum cost to any target
            total_cost += min_dist
        
    return total_cost


def compute_penalties_mobility(state, boxes_positions):
    '''
        Boxes that are blocked by walls or other boxes are penalized.
    '''
    obstacles = state.obstacles
    height = state.length
    width = state.width

    penalty = 0
    
    for box_pos in boxes_positions:
        count = 0

        # up direction
        if (box_pos[0] + 1, box_pos[1]) in obstacles or box_pos[0] + 1 >= height or (box_pos[0] + 1, box_pos[1]) in boxes_positions:
            count += 1

        # down direction
        if (box_pos[0] - 1, box_pos[1]) in obstacles or box_pos[0] - 1 < 0 or (box_pos[0] - 1, box_pos[1]) in boxes_positions:
            count += 1

        # right direction
        if (box_pos[0], box_pos[1] + 1) in obstacles or box_pos[1] + 1 >= width or (box_pos[0], box_pos[1] + 1) in boxes_positions:
            count += 1

        # left direction
        if (box_pos[0], box_pos[1] - 1) in obstacles or box_pos[1] - 1 < 0 or (box_pos[0], box_pos[1] - 1) in boxes_positions:
            count += 1

        # compute a penalty based on how many directions are blocked
        penalty += count * 0.6

    return penalty



def efficient_heuristic(state):
    targets_positions, boxes_positions = get_targets_boxes_pos(state)
    total_cost = hungarian_dist_heuristic(state)
    penalties_boxes = compute_penalties_mobility(state, boxes_positions)
    
    return 2 * total_cost + penalties_boxes


def is_corner_deadlock(state):
    '''
        Detects any box that is in a corner deadlock position.
        (it cannot be moved from this position)
    '''
    obstacles = state.obstacles
    height = state.length
    width = state.width

    boxes_not_on_targets = not_on_right_place_boxes(state)

    for box_pos in boxes_not_on_targets:
        wall_right = False
        wall_left = False
        wall_up = False
        wall_down = False

        # check if there exists walls in each direction
        if (box_pos[0], box_pos[1] + 1) in obstacles or box_pos[1] + 1 >= width:
            wall_right = True
        
        if (box_pos[0], box_pos[1] - 1) in obstacles or box_pos[1] - 1 < 0:
            wall_left = True
        
        if (box_pos[0] + 1, box_pos[1]) in obstacles or box_pos[0] + 1 >= height:
            wall_up = True
        
        if (box_pos[0] - 1, box_pos[1]) in obstacles or box_pos[0] - 1 < 0:
            wall_down = True

        # check for each corner deadlock for each box that is not already placed to a target
        if wall_left and wall_down:
            return True

        if wall_left and wall_up:
            return True

        if wall_right and wall_down:
            return True

        if wall_right and wall_up:
            return True

    # no boxes are blocked
    return False


def is_there_a_box(box_pos_x, box_pos_y, boxes_not_on_targets):
    '''
        Checks if there is a box at a specific position.
    '''
    for box in boxes_not_on_targets:
        if box == (box_pos_x, box_pos_y):
            return True

    return False


def is_box_deadlock(state):
    '''
        Detects any box that is blocked by a wall and other boxes to reach a target. 
    '''
    obstacles = state.obstacles
    height = state.length
    width = state.width

    targets_positions, _ = get_targets_boxes_pos(state)
    boxes_not_on_targets = not_on_right_place_boxes(state)

    for box_pos in boxes_not_on_targets:
        # for a box to be blocked by other boxes it should also touch a wall
        already_box_up = False
        already_box_down = False
        already_box_right = False
        already_box_left = False

        touches_wall_up = False
        touches_wall_down = False
        touches_wall_right = False
        touches_wall_left = False

        # check for boxes and walls in up direction
        if is_there_a_box(box_pos[0] + 1, box_pos[1], boxes_not_on_targets):
            already_box_up = True

        if box_pos[0] + 1 >= height or (box_pos[0] + 1, box_pos[1]) in obstacles:
            touches_wall_up = True
        
        # check for boxes and walls in down direction
        if is_there_a_box(box_pos[0] - 1, box_pos[1], boxes_not_on_targets):
            already_box_down = True

        if box_pos[0] - 1 < 0 or (box_pos[0] - 1, box_pos[1]) in obstacles:
            touches_wall_down = True

        # check for boxes and walls in left direction
        if is_there_a_box(box_pos[0], box_pos[1] - 1, boxes_not_on_targets):
            already_box_left = True

        if box_pos[1] - 1 < 0 or (box_pos[0], box_pos[1] - 1) in obstacles:
            touches_wall_left = True

        # check for boxes and walls in right direction
        if is_there_a_box(box_pos[0], box_pos[1] + 1, boxes_not_on_targets):
            already_box_right = True

        if box_pos[1] + 1 >= width or (box_pos[0], box_pos[1] + 1) in obstacles:
            touches_wall_right = True

        # box blocked horizontally
        if already_box_left and already_box_right and (touches_wall_left or touches_wall_right):
            return True
        
        # box blocked vertically
        if already_box_up and already_box_down and (touches_wall_up or touches_wall_down):
            return True

    return False


#  Combine deadlock detection with the above heuristics

def deadlock_direct_path_heuristic(state):
    if is_corner_deadlock(state) or is_box_deadlock(state):
        return float('inf')
    
    direct_path = direct_path_heuristic(state)
    if direct_path == float('inf'):
        return float('inf')

    return direct_path


def deadlock_manhattan_heuristic(state):
    if is_corner_deadlock(state) or is_box_deadlock(state):
        return float('inf')
    
    return manhattan_dist_heuristic(state)


def deadlock_euclidian_heuristic(state):
    if is_corner_deadlock(state) or is_box_deadlock(state):
        return float('inf')
    
    return euclidian_dist_heuristic(state)


def deadlock_hungarian_heuristic(state):
    if is_corner_deadlock(state) or is_box_deadlock(state):
        return float('inf')
    
    return hungarian_dist_heuristic(state)


def deadlock_efficient_heuristic(state):
    if is_corner_deadlock(state) or is_box_deadlock(state):
        return float('inf')
    
    return efficient_heuristic(state)

