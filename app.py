"""
app.py
Flask Web Server providing Web Visualizer frontend and REST APIs.
"""

import os
import sys
import glob
import re

# Ensure sufficient recursion depth for large puzzles (up to 25x25)
sys.setrecursionlimit(200000)

from flask import Flask, render_template, request, jsonify
from src.board import Board
from src.blind_search import DFSSolver
from src.heuristic_search import AStarSolver
from src.generator import generate_solvable_board

app = Flask(__name__)

INPUTS_DIR = os.path.join(os.path.dirname(__file__), "inputs")

def parse_size_key(filename: str):
    """Parses dimension (e.g. 10x10 -> 100) from filename to sort naturally by board size."""
    bname = os.path.basename(filename)
    match = re.search(r'(\d+)x(\d+)', bname)
    if match:
        r, c = int(match.group(1)), int(match.group(2))
        return (r * c, r, c, bname)
    return (9999, 0, 0, bname)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/levels", methods=["GET"])
def get_levels():
    """Returns the list of level files directly in inputs/ sorted naturally by board size."""
    files = sorted(glob.glob(os.path.join(INPUTS_DIR, "*.txt")), key=parse_size_key)
    levels = []
    for f in files:
        bname = os.path.basename(f)
        match = re.search(r'level_(\d+x\d+)_([a-zA-Z]+)', bname)
        if match:
            dim = match.group(1)
            diff = match.group(2).capitalize()
            label = f"{dim} - {diff} ({bname})"
        else:
            label = bname
        levels.append({
            "filename": bname,
            "label": label
        })
    return jsonify({"levels": levels})

@app.route("/api/load_level", methods=["POST"])
def load_level():
    """Loads a board configuration from a level file in inputs/."""
    data = request.json or {}
    filename = data.get("filename")
    if not filename:
        return jsonify({"error": "Missing filename parameter"}), 400

    bname = os.path.basename(filename)
    filepath = os.path.join(INPUTS_DIR, bname)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    board = Board.from_file(filepath)
    return jsonify({
        "filename": bname,
        "rows": board.rows,
        "cols": board.cols,
        "grid": board.to_list(),
        "conflicts": board.count_conflicts()
    })

@app.route("/api/generate", methods=["POST"])
def generate():
    """Generates a random NxN board guaranteed to be solvable."""
    data = request.json or {}
    size = int(data.get("size", 4))
    size = max(3, min(size, 25))  # Clamp supporting 3x3 to 25x25

    scrambled_board, _ = generate_solvable_board(size, size)
    return jsonify({
        "rows": size,
        "cols": size,
        "grid": scrambled_board.to_list(),
        "conflicts": scrambled_board.count_conflicts()
    })

@app.route("/api/solve", methods=["POST"])
def solve():
    """Solves the received grid using the requested algorithm (dfs / astar)."""
    data = request.json or {}
    algorithm = data.get("algorithm", "astar").lower()
    grid = data.get("grid")

    if not grid:
        return jsonify({"error": "Missing grid data"}), 400

    board = Board(grid)

    if algorithm == "dfs":
        solver = DFSSolver(board)
    else:
        solver = AStarSolver(board)

    result = solver.solve()
    result["initial_conflicts"] = Board(grid).count_conflicts()
    return jsonify(result)

@app.route("/api/compare", methods=["POST"])
def compare():
    """Executes both DFS and A* on the received grid to provide a side-by-side comparison."""
    data = request.json or {}
    grid = data.get("grid")

    if not grid:
        return jsonify({"error": "Missing grid data"}), 400

    board_dfs = Board(grid)
    dfs_solver = DFSSolver(board_dfs)
    dfs_result = dfs_solver.solve()

    board_astar = Board(grid)
    astar_solver = AStarSolver(board_astar)
    astar_result = astar_solver.solve()

    return jsonify({
        "success": dfs_result["success"] and astar_result["success"],
        "rows": len(grid),
        "cols": len(grid[0]) if len(grid) > 0 else 0,
        "initial_conflicts": Board(grid).count_conflicts(),
        "dfs": {
            "name": "DFS (Backtracking + Forward Pruning)",
            "success": dfs_result["success"],
            "time_ms": dfs_result["time_ms"],
            "memory_kb": dfs_result["memory_kb"],
            "nodes_explored": dfs_result["nodes_explored"],
            "steps_count": dfs_result["steps_count"],
        },
        "astar": {
            "name": "A* Search (Min-Heap + Admissible Heuristic)",
            "success": astar_result["success"],
            "time_ms": astar_result["time_ms"],
            "memory_kb": astar_result["memory_kb"],
            "nodes_explored": astar_result["nodes_explored"],
            "steps_count": astar_result["steps_count"],
        }
    })

if __name__ == "__main__":
    print("=" * 60)
    print(" Starting Puzzle Pipes AI Web Visualizer...")
    print(" Access at: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host="127.0.0.1", port=5000)
