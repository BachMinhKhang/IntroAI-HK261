"""
board.py
Mô hình hóa bàn cờ Puzzle Pipes, kiểm tra tính hợp lệ và kiểm tra trạng thái đích (Goal Test).
"""

from collections import deque
from src.pipe_constants import (
    NORTH, EAST, SOUTH, WEST,
    DIRECTIONS, DELTAS, OPPOSITE,
    rotate_cw, get_possible_rotations
)

class Board:
    def __init__(self, grid: list[list[int]]):
        """
        Khởi tạo bảng từ ma trận 2D chứa các giá trị bitmask (0-15).
        """
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.grid = [row[:] for row in grid]
        self.initial_grid = [row[:] for row in grid]

    def copy(self) -> 'Board':
        """Tạo bản sao sâu của bàn cờ."""
        new_board = Board(self.grid)
        new_board.initial_grid = [row[:] for row in self.initial_grid]
        return new_board

    def is_valid_coord(self, r: int, c: int) -> bool:
        """Kiểm tra tọa độ (r, c) có nằm trong lưới không."""
        return 0 <= r < self.rows and 0 <= c < self.cols

    def get_pipe(self, r: int, c: int) -> int:
        return self.grid[r][c]

    def set_pipe(self, r: int, c: int, mask: int) -> None:
        self.grid[r][c] = mask

    def rotate_cell(self, r: int, c: int, times: int = 1) -> int:
        """Xoay ô tại (r, c) theo chiều kim đồng hồ 'times' lần và trả về mask mới."""
        self.grid[r][c] = rotate_cw(self.grid[r][c], times)
        return self.grid[r][c]

    def check_cell_boundary(self, r: int, c: int, mask: int = None) -> bool:
        """
        Kiểm tra xem các cổng nối của ô (r, c) có bị chĩa ra ngoài mép bàn cờ hay không.
        Trả về True nếu hợp lệ (không chĩa ra ngoài).
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
        Kiểm tra khớp cổng nối tức thời (Forward Checking) giữa ô (r, c)
        với các ô láng giềng đã được gán trước đó trong tập 'assigned'.
        """
        # 1. Không được chĩa ra biên
        if not self.check_cell_boundary(r, c, mask):
            return False

        # 2. Kiểm tra với các ô láng giềng đã gán
        for d in DIRECTIONS:
            dr, dc = DELTAS[d]
            nr, nc = r + dr, c + dc
            if (nr, nc) in assigned:
                neighbor_mask = self.grid[nr][nc]
                has_out = bool(mask & d)
                neighbor_has_in = bool(neighbor_mask & OPPOSITE[d])
                # Hai bên phải cùng nối hoặc cùng đóng
                if has_out != neighbor_has_in:
                    return False
        return True

    def is_goal_state(self) -> bool:
        """
        Kiểm tra điều kiện thắng (Goal Test):
        1. Tất cả các cổng tiếp giáp phải khớp nhau hoàn toàn.
        2. Không có cổng nào chĩa ra ngoài biên.
        3. Toàn bộ các mảnh ống tạo thành đúng 1 thành phần liên thông (Spanning Tree).
        """
        # 1 & 2: Kiểm tra biên và tính tương thích từng cạnh
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
                        # Cổng chĩa ra ngoài biên -> Sai
                        if not self.is_valid_coord(nr, nc):
                            return False
                        # Cổng láng giềng không khớp nối lại -> Sai
                        neighbor_mask = self.grid[nr][nc]
                        if not (neighbor_mask & OPPOSITE[d]):
                            return False

        if total_active_cells == 0:
            return True

        # 3. Kiểm tra tính liên thông toàn phần bằng BFS
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
        Đếm số lượng cổng nối bị lỗi (xung đột láng giềng hoặc chĩa ra ngoài tường).
        Dùng cho hàm Heuristic của A*.
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
        """Đọc bảng từ file text định dạng ma trận số bitmask."""
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Dòng đầu có thể là kích thước "R C" hoặc trực tiếp ma trận
        first_tokens = lines[0].split()
        if len(first_tokens) == 2 and first_tokens[0].isdigit() and first_tokens[1].isdigit():
            lines = lines[1:]

        grid = []
        for line in lines:
            row = [int(token) for token in line.split()]
            grid.append(row)
        return cls(grid)

    def to_file(self, filepath: str) -> None:
        """Lưu bàn cờ ra file text."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"{self.rows} {self.cols}\n")
            for row in self.grid:
                f.write(" ".join(f"{mask:2d}" for mask in row) + "\n")

    def to_list(self) -> list[list[int]]:
        """Trả về ma trận 2D dạng list để serialize ra JSON."""
        return [row[:] for row in self.grid]

