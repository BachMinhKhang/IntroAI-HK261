"""
heuristic_search.py
Heuristic Search Algorithm: A* Search with Priority Queue (heapq).
(Lead: Member 2)
"""

import heapq
from src.solver_base import SolverBase
from src.pipe_constants import get_possible_rotations
from src.board import Board

class AStarSolver(SolverBase):
    def __init__(self, board: Board):
        super().__init__(board, name="A* Search")

    def _heuristic(self, r: int, c: int, candidate_mask: int) -> int:
        """
        Admissible Heuristic function h(n):
        Estimates the remaining distance to goal state.
        Counts unassigned cells plus half the current port mismatch conflicts.
        Admissible property: h(n) <= h*(n), never overestimates actual cost.
        """
        remaining_cells = (self.board.rows * self.board.cols) - (r * self.board.cols + c + 1)
        conflicts = self.board.count_conflicts()
        return remaining_cells + (conflicts // 2)

    def _solve_impl(self) -> bool:
        """
        Executes A* search using a min-heap priority queue.
        Heap element: (f_score, h_score, tie_breaker, cell_idx, grid_state, steps_history)
        Evaluation function: f(n) = g(n) + h(n)
        """
        total_cells = self.board.rows * self.board.cols
        start_grid = tuple(tuple(row) for row in self.board.grid)

        tie_breaker = 0
        open_set = []
        initial_h = self.board.count_conflicts() // 2
        heapq.heappush(open_set, (initial_h, initial_h, tie_breaker, 0, start_grid, []))

        visited_states = set()

        while open_set:
            f, h, _, cell_idx, current_grid, history = heapq.heappop(open_set)
            self.nodes_explored += 1

            self.board.grid = [list(row) for row in current_grid]

            # Check if all cells have been assigned
            if cell_idx == total_cells:
                if self.board.is_goal_state():
                    self.steps = history
                    return True
                continue

            r = cell_idx // self.board.cols
            c = cell_idx % self.board.cols

            assigned = {(i // self.board.cols, i % self.board.cols) for i in range(cell_idx)}
            original_mask = self.board.get_pipe(r, c)
            possible_rotations = get_possible_rotations(original_mask)

            for candidate_mask in possible_rotations:
                if self.board.check_local_match(r, c, candidate_mask, assigned):
                    new_grid = [list(row) for row in current_grid]
                    new_grid[r][c] = candidate_mask
                    state_key = (cell_idx + 1, tuple(tuple(row) for row in new_grid))

                    if state_key not in visited_states:
                        visited_states.add(state_key)

                        g = cell_idx + 1
                        self.board.grid = new_grid
                        h_val = self._heuristic(r, c, candidate_mask)
                        f_val = g + h_val

                        step_info = {
                            "step": len(history) + 1,
                            "r": r,
                            "c": c,
                            "action": "place",
                            "old_mask": original_mask,
                            "new_mask": candidate_mask
                        }

                        tie_breaker += 1
                        heapq.heappush(open_set, (
                            f_val,
                            h_val,
                            tie_breaker,
                            cell_idx + 1,
                            tuple(tuple(row) for row in new_grid),
                            history + [step_info]
                        ))

        return False
