"""
main.py
Điểm khởi chạy chính (Entry Point) của đồ án Puzzle Pipes AI.

Cách sử dụng:
  - Khởi chạy Web Visualizer:  python main.py
  - Chạy Benchmark đo số liệu: python main.py --benchmark
  - Sinh thêm màn chơi mới:   python main.py --generate 5
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
    print(f" [OK] Khoi chay Puzzle Pipes AI Visualizer tren Flask Server...")
    print(f" [->] Mo trinh duyet tai: {url}")
    print("=" * 60)

    # Tự động mở trình duyệt sau 1.2 giây
    def open_browser():
        webbrowser.open_new(url)
    Timer(1.2, open_browser).start()

    app.run(debug=False, host="127.0.0.1", port=port)

def start_benchmark():
    from src.benchmark import run_benchmarks
    print("=" * 60)
    print(" [OK] Dang chay Benchmark tren toan bo cac test cases trong inputs/...")
    print("=" * 60)
    run_benchmarks()

def start_generator(size_str: str):
    from src.generator import generate_and_save_level
    try:
        size = int(size_str)
        output_path = f"inputs/level_{size}x{size}_custom.txt"
        generate_and_save_level(size, size, output_path)
    except ValueError:
        print("[!] Kich thuoc phai la mot so nguyen (vi du: python main.py --generate 5)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        flag = sys.argv[1].lower()
        if flag == "--benchmark":
            start_benchmark()
        elif flag == "--generate" and len(sys.argv) > 2:
            start_generator(sys.argv[2])
        else:
            print("Cac tham so hop le:")
            print("  python main.py             : Khoi chay giao dien Web Visualizer")
            print("  python main.py --benchmark : Chay thu nghiem lay so lieu CSV")
            print("  python main.py --generate N: Sinh file testcase NxN moi")
    else:
        start_web()

