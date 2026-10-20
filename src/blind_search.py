"""
blind_search.py
Thuật toán Blind Search: Depth-First Search (DFS) kết hợp Backtracking và Forward Pruning.
(Phụ trách chính: Thành viên 1)
"""

from src.solver_base import SolverBase
from src.pipe_constants import get_possible_rotations
from src.board import Board

class DFSSolver(SolverBase):
    def __init__(self, board: Board):
        super().__init__(board, name="DFS (Backtracking)")

    def _solve_impl(self) -> bool:
        """
        Duyệt theo thứ tự ô (0, 0) -> (R-1, C-1).
        Tại mỗi ô, thử các góc xoay hợp lệ.
        Áp dụng Forward Pruning: kiểm tra tương thích tức thì với các ô kề đã gán.
        """
        assigned = set()
        return self._backtrack(0, 0, assigned)

    def _backtrack(self, r: int, c: int, assigned: set) -> bool:
        # Nếu đã đi hết bảng, kiểm tra tính liên thông toàn phần
        if r >= self.board.rows:
            return self.board.is_goal_state()

        next_r = r if c + 1 < self.board.cols else r + 1
        next_c = c + 1 if c + 1 < self.board.cols else 0

        original_mask = self.board.get_pipe(r, c)
        possible_rotations = get_possible_rotations(original_mask)

        for candidate_mask in possible_rotations:
            self.nodes_explored += 1

            # Kỹ thuật Cắt tỉa nhánh chết (Forward Pruning)
            if self.board.check_local_match(r, c, candidate_mask, assigned):
                # 1. Gán trạng thái thử nghiệm
                old_val = self.board.get_pipe(r, c)
                self.board.set_pipe(r, c, candidate_mask)
                assigned.add((r, c))
                self.record_step(r, c, "place", old_val, candidate_mask)

                # 2. Đệ quy tới ô kế tiếp
                if self._backtrack(next_r, next_c, assigned):
                    return True

                # 3. Quay lui (Backtrack)
                assigned.remove((r, c))
                self.board.set_pipe(r, c, old_val)
                self.record_step(r, c, "backtrack", candidate_mask, old_val)

        return False

