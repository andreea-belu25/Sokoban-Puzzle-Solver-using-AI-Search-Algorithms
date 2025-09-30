# Sokoban Puzzle Solver using IDA* and Simulated Annealing
---

## Executive Summary

This project implements and analyzes two artificial intelligence algorithms for solving Sokoban puzzles: IDA* (Iterative Deepening A*) and Simulated Annealing. The implementation began with the IDA* algorithm, followed by iterative development and testing of various heuristics until achieving the final optimized versions: `deadlock_hungarian_heuristic`, `efficient_heuristic`, and `deadlock_efficient_heuristic`, which successfully solved all provided test maps.

Among these three heuristics, `deadlock_efficient_heuristic` is considered the highest quality, achieving fewer pull moves for half of the test cases. Subsequently, the Simulated Annealing algorithm was implemented with specific optimizations, analyzing different behaviors across all implemented heuristics. The final objective was perfecting this algorithm to utilize the same optimal heuristic for efficiently solving all map types.

---

## I. IDA* Implementation (`ida_star.py`)

### Architecture

The implementation uses a constructor to initialize essential variables including those for maintaining the current solution and tracking the best solution found. Key components include:

- Helper function to extract box positions requiring movement and player position
- Core `ida_star` function implementing the algorithm
- `solve` function inherited from the Solver class

### Core Algorithm: `ida_star(path, moves, g, threshold, current_pull_moves)`

This recursive function employs backtracking with the following logic:

1. **State Extraction**: Retrieves the last state from the path and increments the explored states counter
2. **Goal Check**: Verifies if all boxes have reached their targets; if so, marks this as the best solution
3. **Cycle Detection**: Checks if the current state was previously visited to avoid potential cycles
4. **State Validation**: Marks current state as visited if the path remains viable
5. **Heuristic Application**: Applies the selected heuristic; infinite results indicate the state cannot lead to a valid solution
6. **Cost Calculation**: Computes the total estimated function value to determine if informed search can continue on this branch
7. **Move Generation**: Considers each possible move from the current state
8. **Recursive Exploration**: Adds promising moves to the path and continues recursion
9. **Backtracking**: Maintains the minimum cost encountered and backtracks when necessary

### Solve Function

Initialization begins from the initial state with zero moves and explored states, no solution discovered yet. The selected heuristic is applied to this state. Some heuristics may return infinite results, indicating no solution exists for that state. The threshold is initialized with the initial heuristic value.

The algorithm applies `ida_star` for a specified number of iterations, checking at each step whether a solution has been found. Execution terminates when the iteration limit is reached or a solution is discovered. An infinite threshold indicates no solution exists; otherwise, the threshold updates for the next iteration.

### Implementation Considerations

The algorithm implementation was relatively straightforward despite lacking a standard reference implementation. The primary challenge involved setting iteration limits—initially, too few iterations caused the algorithm to stall on large test cases, resolved by increasing the limit.

**Optimizations beyond standard pseudocode:**
- Consideration and minimization of pull moves
- Continuous tracking of the best solution
- Dictionary-based cycle detection

**Resources:**
- GeeksForGeeks documentation for algorithm understanding
- Various forum discussions about Sokoban and search space optimization (Stack Overflow, Computer Science Stack Exchange)

---

## II. Simulated Annealing Implementation (`simulated_annealing.py`)

### Architecture

Similar to IDA*, the constructor initializes essential variables for saving the current and best solutions. Key parameter choices:

- **Initial Temperature**: High value to enable broad exploration of the state space
- **Cooling Rate**: Extremely slow for gradual convergence
- **Helper Functions**: 
  - Position extraction for boxes and player
  - `softmax` function converting energies to probabilities (higher values yield higher probabilities)
  - Energy calculation function for current state

### Energy Calculation Strategy

The energy function considers:
- Minimization of pull moves
- Heuristic function for estimating distance to solution
- Penalty for total move count (favoring shorter solutions)

### Advanced Implementation Strategy

The algorithm required iterative implementation of multiple advanced strategies to achieve desired behavior:

**Basic Implementation Steps:**
1. Initialization and checking if initial state is solvable
2. Parameter selection for acceptance probability
3. Final temperature setting (very small to favor space exploration)
4. Maximum iteration count
5. Counter for consecutive poor moves accepted

**Key Challenges and Solutions:**

**Problem 1: Local Optima Trapping**
- **Solution**: State reinitialization with best-found parameters and higher temperature
- Also applied when all possible moves lead to infinite energies

**Problem 2: Large Map Performance**
- **Observation**: Simple alpha-based random selection struggles with very large maps
- **Solution**: Integrated softmax technique for guided state selection
  - 50% of cases: algorithm returns to known good states
  - 50% of cases: explores new possibilities for potentially better states

**Acceptance Mechanism:**
- Accepts better moves deterministically
- Accepts worse moves probabilistically
- Tracks consecutive poor choices; triggers reinitialization after threshold

**Continuous Operations:**
- Testing all possible states with given heuristic
- Tracking and saving best solution
- Transitioning to better or worse states
- Solution verification
- Gradual cooling

### Implementation Experience

Unlike IDA* where understanding and implementation was straightforward, Simulated Annealing development was highly experimental. Each optimization solved one problem but often revealed another, requiring iterative refinement.

The final behavior successfully avoids prolonged stagnation through reinitialization and guided state selection, ensuring eventual return to promising states.

**Resources:**
- Course laboratory implementation of Simulated Annealing with probabilistic conditional selection
- Lecture materials on local minima escape through reinitialization
- Various Internet sources (GeeksForGeeks, YouTube) for visual understanding and game-specific implementations

---

## III. Heuristic Development and Analysis (`heuristics.py`)

### 3.1 Direct Path Heuristic (Initial Attempt)

**Concept**: Detect possible direct paths where boxes can reach targets without obstruction.

**Logic**: A box on the same row/column as an available target (unoccupied) with no blocking boxes or walls constitutes a direct path. This greedy approach proved highly inefficient (Θ(n³) complexity).

**Functions:**
- `direct_path_heuristic(state)`
- `is_direct_path_column(target_pos, box_pos, state)`
- `is_direct_path_row(target_pos, box_pos, state)`

**Results**: No maps solved due to map configurations. This heuristic was not viable for either algorithm.

### 3.2 Direct Path with Deadlock Detection

**Enhancement**: Added early deadlock detection:
- Horizontal/vertical blockage by boxes and walls
- Corner blockage detection (box stuck in map corner)

**Functions:**
- `deadlock_direct_path_heuristic(state)`
- `is_box_deadlock(state)`
- `is_corner_deadlock(state)`
- `is_there_a_box(box_pos_x, box_pos_y, boxes_not_on_targets)`

**Results**: No improvement due to map configurations. However, deadlock detection logic was preserved for future heuristics.

**Decision**: No comparative graphs generated, as non-functional heuristics cannot provide meaningful comparisons.

---

### 3.3 Manhattan Distance Heuristic

**Concept**: Calculates minimum Manhattan distance for each box to nearest target, summing these distances as the heuristic value. Does not account for obstacles or box interactions.

**Function:** `manhattan_dist_heuristic(state)`

**Performance Analysis:**

**IDA* Behavior:**
- Efficient solution finding for simple maps
- Confusion on complex maps with multiple boxes regarding optimal placement order
- Significantly increased explored states and execution time on difficult maps
- **Cause**: Heuristic ignores potential deadlocks

**Simulated Annealing Behavior:**
- More efficient than IDA* on complex maps due to local minima escape through reinitialization
- Cannot solve all map types
- Reduced pull moves (IDA* explores extensively, requiring fewer pulls)

### 3.4 Deadlock Manhattan Heuristic

**Enhancement**: Integrated corner and box-wall blockage detection.

**Function:** `deadlock_manhattan_heuristic(state)`

**Performance Improvements:**
- Significantly fewer explored states, especially for medium and difficult maps
- Improved execution times compared to basic Manhattan
- Fewer pull moves on certain tests by avoiding costly blocked states

**Algorithm Comparison:**
- **IDA***: Dramatic improvement by eliminating useless state exploration
- **Simulated Annealing**: More visible improvement; algorithm was already relatively efficient but benefits from early deadlock pruning

Both algorithms benefit from deadlock integration, with more visible improvement for IDA*.

---

### 3.5 Euclidean Distance Heuristic

**Concept**: Calculates minimum Euclidean distance (straight line) for each box to nearest target. Results rounded up to maintain optimistic admissibility for informed search algorithms. Euclidean distance is always ≤ Manhattan distance.

**Function:** `euclidean_dist_heuristic(state)`

**Performance Analysis:**

**IDA* Behavior:**
- Fewer explored states on large tests compared to Manhattan
- Improved results on small and medium tests
- Still ignores box interactions

**Simulated Annealing Behavior:**
- Broader state space exploration with 50% probability of returning to known efficient states
- Progress on difficult tests
- Generally fewer pull moves than Manhattan (due to optimistic nature)

### 3.6 Deadlock Euclidean Heuristic

**Enhancement**: Integrated deadlock detection functions.

**Function:** `deadlock_euclidean_heuristic(state)`

**Performance Improvements:**
- Rapid abandonment of blocked paths
- More efficient exploration of valid state space
- Progress achieved, though not dramatically significant

**Algorithm Comparison:**
- Both algorithms benefit from early invalid state detection
- Reduced explored states
- Euclidean heuristic's optimistic nature generates fewer pull moves overall
- Effect more visible in Simulated Annealing due to broader exploration

---

### 3.7 Hungarian Distance Heuristic

**Concept**: Unlike Manhattan and Euclidean that simply find the nearest box (potentially underestimating cost when multiple boxes have the same minimum distance), Hungarian distance focuses on optimal box-to-target assignment minimizing total distance.

**Implementation**: Boxes sorted by minimum distances and assigned to nearest available target.

**Function:** `hungarian_dist_heuristic(state)`

**Performance Analysis:**

**IDA* Behavior:**
- Through optimal assignment, real cost is better estimated
- More informed heuristic
- Considerably fewer explored states
- Improved execution time for most maps

### 3.8 Deadlock Hungarian Heuristic

**Enhancement**: Combined with deadlock detection (implemented out of curiosity for potential additional benefits).

**Function:** `deadlock_hungarian_heuristic(state)`

**Results:**
- Higher efficiency
- Faster abandonment of unsuccessful paths

**Algorithm Comparison:**

Both algorithms benefit significantly:
- **Simulated Annealing**: Easier solution finding in complex spaces with fewer reinitializations
- Both show progress in detecting and abandoning impossible paths
- Number of explored states remains high

**Pull Moves Analysis:**
- Combination of optimal assignment and deadlock path elimination enables finding much more efficient solutions from pull move perspective
- Improvement visible in both algorithms

**Conclusion:** Hungarian distance offers the best performance among the three analyzed heuristics (Manhattan, Euclidean, Hungarian), with the deadlock version providing substantial improvements, especially for Simulated Annealing.

---

### 3.9 Efficient Heuristic

**Concept**: Add penalties for boxes blocked by other boxes and/or walls.

**Implementation:**
- Helper function: `compute_penalties_mobility(state, boxes_positions)`
- Calculates number of blocked directions and assigns penalty accordingly
- **Return Value**: (2 × Hungarian distance cost) + penalty
- Factor of 2 gives greater influence to box-target distances (the actual game objective)

**Function:** `efficient_heuristic(state)`

**IDA* Influence:**
- Boxes becoming difficult to move are avoided when possible
- Boxes maintaining mobility for other boxes are preferred

**Performance Analysis:**

**IDA* Behavior:**
- Drastic reduction in explored states
- Improved execution time for most maps
- Solution efficiency determined by reduced total moves

**Simulated Annealing Behavior:**
- Highly informed cost calculation
- Rapid identification of potentially good paths
- Rapid elimination of deceptive paths
- Successfully reduced pull moves—best quality achieved
- Algorithm guided toward solutions maintaining boxes in high-mobility positions, reducing need for corrective pull moves

**Results:** This heuristic achieved significant progress for both algorithms.

### 3.10 Deadlock Efficient Heuristic

**Enhancement**: Combined efficient heuristic with deadlock detection.

**Function:** `deadlock_efficient_heuristic(state)`

**Results:**
- Maximum efficiency achieved
- Significantly reduced explored states
- Previously intractable problems now solvable
- Reduced pull moves

**Consideration:** While pull moves remain high for Simulated Annealing, and assignment quality focuses on minimizing pull moves, **`efficient_heuristic(state)` is considered the highest quality** overall.

---

*This document represents an exploration of informed search algorithms applied to the Sokoban puzzle domain, demonstrating the iterative development of increasingly sophisticated heuristics and the comparative strengths of systematic search (IDA*) versus stochastic optimization (Simulated Annealing).*
