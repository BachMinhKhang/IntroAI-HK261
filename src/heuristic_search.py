"""
heuristic_search.py
Thuật toán Heuristic Search: A* Search với Hàng đợi ưu tiên (Priority Queue - heapq).
(Phụ trách chính: Thành viên 2)
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
        Hàm Heuristic h(n):
        Ước lượng chi phí từ trạng thái hiện tại đến đích.
        Đếm số lượng cổng nối còn xung đột với láng giềng hoặc chĩa ra ngoài biên / 2.
        Tính chất: Admissible (không bao giờ đánh giá quá chi phí thực tế).
        """
        # Ước lượng số ô chưa gán còn lại
        remaining_cells = (self.board.rows * self.board.cols) - (r * self.board.cols + c + 1)
        # Cộng thêm xung đột nếu có
        conflicts = self.board.count_conflicts()
        return remaining_cells + (conflicts // 2)

    def _solve_impl(self) -> bool:
        """
        Hiện thực giải thuật A* sử dụng Min-Heap (heapq).
        Mỗi phần tử trong heap: (f_score, h_score, tie_breaker, r, c, grid_state, steps_log)
        f(n) = g(n) + h(n)
        """
        # Thứ tự duyệt các ô: (0, 0) -> (R-1, C-1)
        total_cells = self.board.rows * self.board.cols
        start_grid = tuple(tuple(row) for row in self.board.grid)
        
        # open_set: Min-Heap
        # (f_score, h_score, tie_breaker, cell_idx, grid_state, history)
        tie_breaker = 0
        open_set = []
        initial_h = self.board.count_conflicts() // 2
        heapq.heappush(open_set, (initial_h, initial_h, tie_breaker, 0, start_grid, []))

        visited_states = set()

        while open_set:
            f, h, _, cell_idx, current_grid, history = heapq.heappop(open_set)
            self.nodes_explored += 1

            # Nạp trạng thái vào board để kiểm tra
            self.board.grid = [list(row) for row in current_grid]

            # Nếu đã gán hết tất cả các ô
            if cell_idx == total_cells:
                if self.board.is_goal_state():
                    self.steps = history
                    return True
                continue

            # Tọa độ ô hiện tại
            r = cell_idx // self.board.cols
            c = cell_idx % self.board.cols

            assigned = {(i // self.board.cols, i % self.board.cols) for i in range(cell_idx)}
            original_mask = self.board.get_pipe(r, c)
            possible_rotations = get_possible_rotations(original_mask)

            for candidate_mask in possible_rotations:
                if self.board.check_local_match(r, c, candidate_mask, assigned):
                    # Tạo trạng thái lưới mới
                    new_grid = [list(row) for row in current_grid]
                    new_grid[r][c] = candidate_mask
                    state_key = (cell_idx + 1, tuple(tuple(row) for row in new_grid))

                    if state_key not in visited_states:
                        visited_states.add(state_key)
                        
                        g = cell_idx + 1
                        # Tạm thời gán để tính heuristic
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

