"""
generator.py
Thuật toán sinh bàn cờ Puzzle Pipes ngẫu nhiên đảm bảo 100% có nghiệm
bằng phương pháp sinh Cây khung ngẫu nhiên (Randomized Spanning Tree).
"""

import random
from src.pipe_constants import (
    NORTH, EAST, SOUTH, WEST,
    DELTAS, OPPOSITE, rotate_cw
)
from src.board import Board

def generate_solvable_board(rows: int, cols: int, seed: int = None) -> tuple[Board, Board]:
    """
    Sinh một bàn cờ kích thước rows x cols đảm bảo 100% có nghiệm.
    Trả về: (scrambled_board, solution_board)
    """
    if seed is not None:
        random.seed(seed)

    # 1. Sinh Cây khung ngẫu nhiên (Randomized DFS) trên đồ thị lưới
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    solution_grid = [[0 for _ in range(cols)] for _ in range(rows)]

    def dfs(r: int, c: int):
        visited[r][c] = True
        # Lấy các hướng ngẫu nhiên
        dirs = [NORTH, EAST, SOUTH, WEST]
        random.shuffle(dirs)

        for d in dirs:
            dr, dc = DELTAS[d]
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                # Nối cổng giữa 2 ô
                solution_grid[r][c] |= d
                solution_grid[nr][nc] |= OPPOSITE[d]
                dfs(nr, nc)

    # Bắt đầu sinh cây từ ô (0, 0)
    dfs(0, 0)

    # 2. Tạo bàn cờ xáo trộn (Scramble) bằng cách xoay ngẫu nhiên từng ô
    scrambled_grid = [[0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            solved_mask = solution_grid[r][c]
            # Xoay ngẫu nhiên 0-3 lần 90 độ
            turns = random.randint(0, 3)
            scrambled_grid[r][c] = rotate_cw(solved_mask, turns)

    solution_board = Board(solution_grid)
    scrambled_board = Board(scrambled_grid)
    return scrambled_board, solution_board

def generate_and_save_level(rows: int, cols: int, filepath: str, seed: int = None) -> None:
    """Sinh bàn cờ và lưu ra file text."""
    scrambled_board, _ = generate_solvable_board(rows, cols, seed)
    scrambled_board.to_file(filepath)
    print(f"[OK] Generated level {rows}x{cols} at: {filepath}")

if __name__ == "__main__":
    # Test tạo mẫu
    board, sol = generate_solvable_board(4, 4)
    print("Scrambled:")
    for row in board.grid:
        print(row)
    print("Is solved goal state?", sol.is_goal_state())
