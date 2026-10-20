"""
app.py
Flask Web Server phục vụ giao diện Web Visualizer và các REST APIs.
"""

import os
import glob
from flask import Flask, render_template, request, jsonify
from src.board import Board
from src.blind_search import DFSSolver
from src.heuristic_search import AStarSolver
from src.generator import generate_solvable_board

app = Flask(__name__)

INPUTS_DIR = os.path.join(os.path.dirname(__file__), "inputs")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/levels", methods=["GET"])
def get_levels():
    """Lấy danh sách các file level có sẵn trong thư mục inputs/."""
    files = sorted(glob.glob(os.path.join(INPUTS_DIR, "*.txt")))
    levels = [os.path.basename(f) for f in files]
    return jsonify({"levels": levels})

@app.route("/api/load_level", methods=["POST"])
def load_level():
    """Nạp ma trận bàn cờ từ file level được chọn."""
    data = request.json or {}
    filename = data.get("filename")
    if not filename:
        return jsonify({"error": "Thieu ten file level"}), 400

    filepath = os.path.join(INPUTS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File khong ton tai"}), 404

    board = Board.from_file(filepath)
    return jsonify({
        "filename": filename,
        "rows": board.rows,
        "cols": board.cols,
        "grid": board.to_list()
    })

@app.route("/api/generate", methods=["POST"])
def generate():
    """Sinh bàn cờ ngẫu nhiên kích thước NxN đảm bảo 100% có nghiệm."""
    data = request.json or {}
    size = int(data.get("size", 4))
    size = max(3, min(size, 8)) # Giới hạn kích thước an toàn 3x3 đến 8x8

    scrambled_board, _ = generate_solvable_board(size, size)
    return jsonify({
        "rows": size,
        "cols": size,
        "grid": scrambled_board.to_list()
    })

@app.route("/api/solve", methods=["POST"])
def solve():
    """Nhận cấu hình bàn cờ và thuật toán (dfs / astar) để giải."""
    data = request.json or {}
    algorithm = data.get("algorithm", "astar").lower()
    grid = data.get("grid")

    if not grid:
        return jsonify({"error": "Thieu du lieu grid"}), 400

    board = Board(grid)

    if algorithm == "dfs":
        solver = DFSSolver(board)
    else:
        solver = AStarSolver(board)

    result = solver.solve()
    return jsonify(result)

if __name__ == "__main__":
    print("=" * 60)
    print(" Khởi động Puzzle Pipes Web Visualizer...")
    print(" Truy cập tại: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host="127.0.0.1", port=5000)

