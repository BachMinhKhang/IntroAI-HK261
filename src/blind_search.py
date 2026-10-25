"""
blind_search.py
Blind Search Algorithm: Depth-First Search (DFS) with Backtracking and Forward Pruning.
(Lead: Member 1)
"""

import sys
from src.solver_base import SolverBase
from src.pipe_constants import get_possible_rotations
from src.board import Board

# Support deep recursion up to 25x25 (625 levels)
sys.setrecursionlimit(200000)

class DFSSolver(SolverBase):
    def __init__(self, board: Board):
        super().__init__(board, name="DFS (Backtracking)")

    def _solve_impl(self) -> bool:
        """
        Iterates through cells in scanline order (0, 0) -> (R-1, C-1).
        At each cell, tests candidate rotations.
        Applies forward pruning against previously assigned adjacent cells.
        """
        assigned = set()
        return self._backtrack(0, 0, assigned)

    def _backtrack(self, r: int, c: int, assigned: set) -> bool:
        # If all cells have been assigned, perform global goal verification
        if r >= self.board.rows:
            return self.board.is_goal_state()

        next_r = r if c + 1 < self.board.cols else r + 1
        next_c = c + 1 if c + 1 < self.board.cols else 0

        original_mask = self.board.get_pipe(r, c)
        possible_rotations = get_possible_rotations(original_mask)

        for candidate_mask in possible_rotations:
            self.nodes_explored += 1

            # Forward Pruning: prune branches violating local constraints immediately
            if self.board.check_local_match(r, c, candidate_mask, assigned):
                # 1. Apply tentative assignment
                old_val = self.board.get_pipe(r, c)
                self.board.set_pipe(r, c, candidate_mask)
                assigned.add((r, c))
                self.record_step(r, c, "place", old_val, candidate_mask)

                # 2. Recurse to next cell
                if self._backtrack(next_r, next_c, assigned):
                    return True

                # 3. Backtrack
                assigned.remove((r, c))
                self.board.set_pipe(r, c, old_val)
                self.record_step(r, c, "backtrack", candidate_mask, old_val)

        return False
