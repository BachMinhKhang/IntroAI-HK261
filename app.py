"""
app.py
Flask Web Server providing Web Visualizer frontend and REST APIs.
"""

import os
import sys
import glob

# Ensure sufficient recursion depth for large puzzles (up to 25x25)
sys.setrecursionlimit(200000)
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
    """Returns the list of available level files in inputs/."""
    files = sorted(glob.glob(os.path.join(INPUTS_DIR, "*.txt")))
    levels = [os.path.basename(f) for f in files]
    return jsonify({"levels": levels})

@app.route("/api/load_level", methods=["POST"])
def load_level():
    """Loads a board configuration from a level file."""
    data = request.json or {}
    filename = data.get("filename")
    if not filename:
        return jsonify({"error": "Missing filename parameter"}), 400

    filepath = os.path.join(INPUTS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    board = Board.from_file(filepath)
    return jsonify({
        "filename": filename,
        "rows": board.rows,
        "cols": board.cols,
        "grid": board.to_list()
    })

@app.route("/api/generate", methods=["POST"])
def generate():
    """Generates a random NxN board guaranteed to be solvable."""
    data = request.json or {}
    size = int(data.get("size", 4))
    size = max(3, min(size, 25)) # Safe clamp supporting up to 25x25 (puzzle-pipes.com maximum)

    scrambled_board, _ = generate_solvable_board(size, size)
    return jsonify({
        "rows": size,
        "cols": size,
        "grid": scrambled_board.to_list()
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
    return jsonify(result)

if __name__ == "__main__":
    print("=" * 60)
    print(" Starting Puzzle Pipes AI Web Visualizer...")
    print(" Access at: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host="127.0.0.1", port=5000)
