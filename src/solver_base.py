"""
solver_base.py
Lớp cơ sở trừu tượng cho tất cả các giải thuật Tìm kiếm.
Chuẩn hóa việc đo đạc Thời gian (time.perf_counter), Bộ nhớ (tracemalloc)
và ghi nhận vết các bước (step-by-step trace) phục vụ Web Visualizer.
"""

import time
import tracemalloc
from abc import ABC, abstractmethod
from src.board import Board

class SolverBase(ABC):
    def __init__(self, board: Board, name: str = "BaseSolver"):
        self.board = board.copy()
        self.name = name
        self.nodes_explored = 0
        self.steps = []
        self.success = False

    def record_step(self, r: int, c: int, action: str, old_mask: int, new_mask: int) -> None:
        """
        Ghi lại một bước thay đổi trên bàn cờ.
        - action: 'rotate', 'place', 'backtrack'
        """
        self.steps.append({
            "step": len(self.steps) + 1,
            "r": r,
            "c": c,
            "action": action,
            "old_mask": old_mask,
            "new_mask": new_mask
        })

    def solve(self) -> dict:
        """
        Hàm bao chuẩn: đo Thời gian (ms) và Bộ nhớ đỉnh (KB).
        Gọi phương thức cụ thể _solve_impl() do lớp con hiện thực.
        """
        self.nodes_explored = 0
        self.steps = []
        self.success = False

        tracemalloc.start()
        start_time = time.perf_counter()

        try:
            self.success = self._solve_impl()
        finally:
            end_time = time.perf_counter()
            current_ram, peak_ram = tracemalloc.get_traced_memory()
            tracemalloc.stop()

        time_ms = (end_time - start_time) * 1000.0
        memory_kb = peak_ram / 1024.0

        return {
            "success": self.success,
            "algorithm": self.name,
            "time_ms": round(time_ms, 2),
            "memory_kb": round(memory_kb, 2),
            "nodes_explored": self.nodes_explored,
            "steps_count": len(self.steps),
            "initial_board": self.board.initial_grid,
            "final_board": self.board.to_list(),
            "steps": self.steps
        }

    @abstractmethod
    def _solve_impl(self) -> bool:
        """Lớp con (DFS, A*) hiện thực thuật toán tìm kiếm tại đây. Trả về True nếu tìm thấy lời giải."""
        pass

