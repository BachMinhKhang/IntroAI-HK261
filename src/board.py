"""
board.py
Models the Puzzle Pipes grid, state validation, and goal test.
"""

from collections import deque
from src.pipe_constants import (
    NORTH, EAST, SOUTH, WEST,
    DIRECTIONS, DELTAS, OPPOSITE,
    rotate_cw, get_possible_rotations
)

class Board:
    def __init__(self, grid: list[list[int]]):
        """Initializes the board from a 2D matrix of bitmask integers (0-15)."""
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.grid = [row[:] for row in grid]
        self.initial_grid = [row[:] for row in grid]

    def copy(self) -> 'Board':
        """Creates a deep copy of the board."""
        new_board = Board(self.grid)
        new_board.initial_grid = [row[:] for row in self.initial_grid]
        return new_board

    def is_valid_coord(self, r: int, c: int) -> bool:
        """Checks if coordinate (r, c) is within grid bounds."""
        return 0 <= r < self.rows and 0 <= c < self.cols

    def get_pipe(self, r: int, c: int) -> int:
        return self.grid[r][c]

    def set_pipe(self, r: int, c: int, mask: int) -> None:
        self.grid[r][c] = mask

    def rotate_cell(self, r: int, c: int, times: int = 1) -> int:
        """Rotates the cell at (r, c) clockwise 'times' times and returns the new mask."""
        self.grid[r][c] = rotate_cw(self.grid[r][c], times)
        return self.grid[r][c]

    def check_cell_boundary(self, r: int, c: int, mask: int = None) -> bool:
        """
        Verifies that no active connection ports point outside the grid boundaries.
        Returns True if valid.
        """
        if mask is None:
            mask = self.grid[r][c]

        for d in DIRECTIONS:
            if mask & d:
                dr, dc = DELTAS[d]
                nr, nc = r + dr, c + dc
                if not self.is_valid_coord(nr, nc):
                    return False
        return True

    def check_local_match(self, r: int, c: int, mask: int, assigned: set) -> bool:
        """
        Forward checking: validates connection consistency between cell (r, c)
        and already-assigned adjacent neighbor cells.
        """
        # 1. Ports must not point outside grid borders
        if not self.check_cell_boundary(r, c, mask):
            return False

        # 2. Ports must match assigned neighbors
        for d in DIRECTIONS:
            dr, dc = DELTAS[d]
            nr, nc = r + dr, c + dc
            if (nr, nc) in assigned:
                neighbor_mask = self.grid[nr][nc]
                has_out = bool(mask & d)
                neighbor_has_in = bool(neighbor_mask & OPPOSITE[d])
                if has_out != neighbor_has_in:
                    return False
        return True

    def is_goal_state(self) -> bool:
        """
        Checks the goal condition:
        1. All adjacent connection ports match perfectly.
        2. No ports face outer walls.
        3. All pipes form exactly one single connected component (Spanning Tree).
        """
        total_active_cells = 0
        start_cell = None

        for r in range(self.rows):
            for c in range(self.cols):
                mask = self.grid[r][c]
                if mask > 0:
                    total_active_cells += 1
                    if start_cell is None:
                        start_cell = (r, c)

                for d in DIRECTIONS:
                    if mask & d:
                        dr, dc = DELTAS[d]
                        nr, nc = r + dr, c + dc
                        if not self.is_valid_coord(nr, nc):
                            return False
                        neighbor_mask = self.grid[nr][nc]
                        if not (neighbor_mask & OPPOSITE[d]):
                            return False

        if total_active_cells == 0:
            return True

        # Check global connectivity using BFS
        visited = set()
        queue = deque([start_cell])
        visited.add(start_cell)

        while queue:
            cr, cc = queue.popleft()
            c_mask = self.grid[cr][cc]
            for d in DIRECTIONS:
                if c_mask & d:
                    dr, dc = DELTAS[d]
                    nr, nc = cr + dr, cc + dc
                    if (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc))

        return len(visited) == total_active_cells

    def count_conflicts(self) -> int:
        """
        Counts the number of mismatched or wall-facing connection ports.
        Used for the A* heuristic evaluation.
        """
        conflicts = 0
        for r in range(self.rows):
            for c in range(self.cols):
                mask = self.grid[r][c]
                for d in DIRECTIONS:
                    if mask & d:
                        dr, dc = DELTAS[d]
                        nr, nc = r + dr, c + dc
                        if not self.is_valid_coord(nr, nc):
                            conflicts += 1
                        else:
                            neighbor_mask = self.grid[nr][nc]
                            if not (neighbor_mask & OPPOSITE[d]):
                                conflicts += 1
        return conflicts

    @classmethod
    def from_file(cls, filepath: str) -> 'Board':
        """Loads a board configuration from a text file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        first_tokens = lines[0].split()
        if len(first_tokens) == 2 and first_tokens[0].isdigit() and first_tokens[1].isdigit():
            lines = lines[1:]

        grid = []
        for line in lines:
            row = [int(token) for token in line.split()]
            grid.append(row)
        return cls(grid)

    def to_file(self, filepath: str) -> None:
        """Saves the board configuration to a text file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"{self.rows} {self.cols}\n")
            for row in self.grid:
                f.write(" ".join(f"{mask:2d}" for mask in row) + "\n")

    def to_list(self) -> list[list[int]]:
        """Returns 2D grid matrix as a plain Python list for JSON serialization."""
        return [row[:] for row in self.grid]
