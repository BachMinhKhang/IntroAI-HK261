"""
benchmark.py
Automated benchmarking script evaluating all test files in the inputs/ directory.
Profiles: Execution Time (ms), Peak Memory (KB), and Nodes Explored.
Outputs formatted table to console and writes results to outputs/benchmark_results.csv.
"""

import os
import glob
import csv
from src.board import Board
from src.blind_search import DFSSolver
from src.heuristic_search import AStarSolver

def run_benchmarks(input_dir: str = "inputs", output_csv: str = "outputs/benchmark_results.csv"):
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    test_files = sorted(glob.glob(os.path.join(input_dir, "*.txt")))

    if not test_files:
        print(f"[!] No testcase files found in directory '{input_dir}'")
        return

    print("=" * 90)
    print(f"{'Input File':<25} | {'Algorithm':<18} | {'Status':<8} | {'Time (ms)':<10} | {'RAM (KB)':<10} | {'Nodes':<8}")
    print("=" * 90)

    results = []

    for filepath in test_files:
        filename = os.path.basename(filepath)
        board = Board.from_file(filepath)
        size_str = f"{board.rows}x{board.cols}"

        # 1. Run DFS
        dfs_solver = DFSSolver(board)
        res_dfs = dfs_solver.solve()
        print(f"{filename:<25} | {res_dfs['algorithm']:<18} | {'PASS' if res_dfs['success'] else 'FAIL':<8} | {res_dfs['time_ms']:<10.2f} | {res_dfs['memory_kb']:<10.2f} | {res_dfs['nodes_explored']:<8}")

        # 2. Run A*
        astar_solver = AStarSolver(board)
        res_astar = astar_solver.solve()
        print(f"{filename:<25} | {res_astar['algorithm']:<18} | {'PASS' if res_astar['success'] else 'FAIL':<8} | {res_astar['time_ms']:<10.2f} | {res_astar['memory_kb']:<10.2f} | {res_astar['nodes_explored']:<8}")
        print("-" * 90)

        results.append({
            "filename": filename,
            "size": size_str,
            "algorithm": res_dfs["algorithm"],
            "success": res_dfs["success"],
            "time_ms": res_dfs["time_ms"],
            "memory_kb": res_dfs["memory_kb"],
            "nodes_explored": res_dfs["nodes_explored"],
            "steps_count": res_dfs["steps_count"]
        })

        results.append({
            "filename": filename,
            "size": size_str,
            "algorithm": res_astar["algorithm"],
            "success": res_astar["success"],
            "time_ms": res_astar["time_ms"],
            "memory_kb": res_astar["memory_kb"],
            "nodes_explored": res_astar["nodes_explored"],
            "steps_count": res_astar["steps_count"]
        })

    # Save to CSV
    fieldnames = ["filename", "size", "algorithm", "success", "time_ms", "memory_kb", "nodes_explored", "steps_count"]
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n[OK] Benchmark results successfully saved to: {output_csv}")

    # Generate visual charts automatically
    try:
        from src.plot_benchmark import plot_benchmarks
        plot_benchmarks(output_csv, os.path.dirname(output_csv))
    except Exception as e:
        print(f"[!] Warning: Could not generate plots ({e})")

if __name__ == "__main__":
    run_benchmarks()
