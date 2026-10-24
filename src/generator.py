"""
generator.py
Generates 100% solvable Puzzle Pipes boards using Randomized Spanning Tree on a grid graph.
"""

import random
import sys

# Support spanning tree generation for large grids up to 25x25 (625 cells)
sys.setrecursionlimit(200000)
from src.pipe_constants import (
    NORTH, EAST, SOUTH, WEST,
    DELTAS, OPPOSITE, rotate_cw
)
from src.board import Board

def generate_solvable_board(rows: int, cols: int, seed: int = None) -> tuple[Board, Board]:
    """
    Generates a solvable board of size rows x cols.
    Returns: (scrambled_board, solution_board)
    """
    if seed is not None:
        random.seed(seed)

    # 1. Generate a randomized spanning tree via DFS on grid graph
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    solution_grid = [[0 for _ in range(cols)] for _ in range(rows)]

    def dfs(r: int, c: int):
        visited[r][c] = True
        dirs = [NORTH, EAST, SOUTH, WEST]
        random.shuffle(dirs)

        for d in dirs:
            dr, dc = DELTAS[d]
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                solution_grid[r][c] |= d
                solution_grid[nr][nc] |= OPPOSITE[d]
                dfs(nr, nc)

    dfs(0, 0)

    # 2. Scramble the board by applying random rotations
    scrambled_grid = [[0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            solved_mask = solution_grid[r][c]
            turns = random.randint(0, 3)
            scrambled_grid[r][c] = rotate_cw(solved_mask, turns)

    solution_board = Board(solution_grid)
    scrambled_board = Board(scrambled_grid)
    return scrambled_board, solution_board

def generate_and_save_level(rows: int, cols: int, filepath: str, seed: int = None) -> None:
    """Generates a solvable board and saves it to a text file."""
    scrambled_board, _ = generate_solvable_board(rows, cols, seed)
    scrambled_board.to_file(filepath)
    print(f"[OK] Generated level {rows}x{cols} at: {filepath}")

if __name__ == "__main__":
    board, sol = generate_solvable_board(4, 4)
    print("Scrambled:")
    for row in board.grid:
        print(row)
    print("Is solved goal state?", sol.is_goal_state())
