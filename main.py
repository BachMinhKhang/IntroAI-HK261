"""
main.py
Main entry point for the Puzzle Pipes AI Project.

Usage:
  - Launch Web Visualizer:      python main.py
  - Run Benchmark Suite:        python main.py --benchmark
  - Generate New Random Level:  python main.py --generate 5
"""

import sys
import os
import webbrowser
from threading import Timer

def start_web():
    from app import app
    port = 5000
    url = f"http://127.0.0.1:{port}"
    print("=" * 60)
    print(f" [OK] Launching Puzzle Pipes AI Visualizer on Flask Server...")
    print(f" [->] Open browser at: {url}")
    print("=" * 60)

    # Open browser automatically after 1.2s
    def open_browser():
        webbrowser.open_new(url)
    Timer(1.2, open_browser).start()

    app.run(debug=False, host="127.0.0.1", port=port)

def start_benchmark():
    from src.benchmark import run_benchmarks
    print("=" * 60)
    print(" [OK] Running Benchmark across all test cases in inputs/...")
    print("=" * 60)
    run_benchmarks()

def start_generator(size_str: str):
    from src.generator import generate_and_save_level
    try:
        size = int(size_str)
        output_path = f"inputs/level_{size}x{size}_custom.txt"
        generate_and_save_level(size, size, output_path)
    except ValueError:
        print("[!] Size must be an integer (e.g.: python main.py --generate 5)")

def start_plotting():
    from src.plot_benchmark import plot_benchmarks
    print("=" * 60)
    print(" [OK] Generating visual benchmark comparison charts...")
    print("=" * 60)
    plot_benchmarks()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        flag = sys.argv[1].lower()
        if flag == "--benchmark":
            start_benchmark()
        elif flag == "--plot":
            start_plotting()
        elif flag == "--generate" and len(sys.argv) > 2:
            start_generator(sys.argv[2])
        else:
            print("Valid arguments:")
            print("  python main.py             : Launch Web Visualizer")
            print("  python main.py --benchmark : Run automated benchmark evaluation and plot")
            print("  python main.py --plot      : Generate visual charts from existing CSV")
            print("  python main.py --generate N: Generate a new NxN level file")
    else:
        start_web()
