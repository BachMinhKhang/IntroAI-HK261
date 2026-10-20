# 💧 Puzzle Pipes AI Solver & Visualizer

> **Đồ án môn học:** BÀI TẬP LỚN 1 - TÌM KIẾM TRONG TRÍ TUỆ NHÂN TẠO  
> **Trường Đại học Bách Khoa - ĐHQG TP.HCM (BKU)**  
> **Khoa Khoa học và Kỹ thuật Máy tính**  
> **Game:** Logic Puzzle - Pipes ([puzzle-pipes.com](https://www.puzzle-pipes.com/))  
> **Ngôn ngữ:** Python 3.10+ (Framework: Flask; Frontend: HTML5 / CSS3 / Vanilla JS)

---

## 📌 1. Giới thiệu bài toán & Mục tiêu

Dự án hiện thực và so sánh hai trường phái giải thuật Tìm kiếm trong AI để giải trò chơi **Puzzle Pipes**:
1. **Blind Search (Tìm kiếm mù):** Giải thuật **Depth-First Search (DFS)** kết hợp **Backtracking** và kỹ thuật cắt tỉa tức thời (**Forward Pruning**).
2. **Heuristic Search (Tìm kiếm có thông tin):** Giải thuật **$A^*$ Search** với cấu trúc dữ liệu Hàng đợi ưu tiên (**Min-Heap**) và hàm Heuristic $h(n)$ ước lượng số cổng xung đột (được chứng minh là **Admissible**).

### ✨ Các tính năng nổi bật:
- **Giao diện Web Visualizer hiện đại:** Hiển thị trực quan bàn cờ, animation xoay mượt mà, hiệu ứng đổi màu khi mạng ống nước được nối thông.
- **Điều khiển Step-by-Step:** Cho phép chạy từng bước (Next / Previous), Auto Play, Pause, và thanh trượt tùy chỉnh tốc độ tìm kiếm.
- **Trình sinh bàn cờ ngẫu nhiên (100% Solvable):** Ứng dụng thuật toán Cây khung ngẫu nhiên (**Randomized Spanning Tree**) sinh map bất kỳ kích thước $3 \times 3 \to 8 \times 8$ đảm bảo luôn có lời giải.
- **Bộ đo đạc thực nghiệm tự động:** Sử dụng `time.perf_counter` (đo thời gian ms) và `tracemalloc` (đo bộ nhớ RAM đỉnh KB), xuất kết quả ra file `benchmark_results.csv` phục vụ báo cáo.

---

## 📁 2. Cấu trúc thư mục

```text
puzzle-pipes-ai/
├── inputs/                         # Chứa các file đề bài mẫu (.txt)
│   ├── level_3x3_easy.txt
│   ├── level_4x4_easy.txt
│   ├── level_5x5_medium.txt
│   ├── level_6x6_medium.txt
│   ├── level_7x7_hard.txt
│   └── level_8x8_hard.txt
├── outputs/                        # Chứa kết quả đo đạc thực nghiệm
│   └── benchmark_results.csv
├── src/
│   ├── __init__.py
│   ├── pipe_constants.py           # Bitmask 4 hướng (N, E, S, W) và phép xoay tròn bit
│   ├── board.py                    # Mô hình hóa bàn cờ, kiểm tra hợp lệ và kiểm tra đích (Goal Test)
│   ├── solver_base.py              # Lớp cơ sở trừu tượng: đo time & RAM, ghi vết steps
│   ├── blind_search.py             # Hiện thực DFS Backtracking (Thành viên 1)
│   ├── heuristic_search.py         # Hiện thực A* Search (Thành viên 2)
│   ├── generator.py                # Sinh bàn cờ ngẫu nhiên có nghiệm (Spanning Tree)
│   └── benchmark.py                # Script chạy tự động tất cả test cases xuất CSV
├── templates/
│   └── index.html                  # Giao diện Web Visualizer
├── static/
│   ├── css/style.css               # Giao diện hiện đại & Animation xoay mượt
│   └── js/app.js                   # Logic render bàn cờ, animation step-by-step
├── app.py                          # Flask Web Server
├── main.py                         # Entry point chính của chương trình
├── requirements.txt                # Danh sách thư viện (chỉ cần Flask)
├── README.md                       # Tài liệu hướng dẫn
└── plan.md                         # Kế hoạch chi tiết và tiến độ dự án
```

---

## 🚀 3. Hướng dẫn Cài đặt & Sử dụng

### 3.1. Cài đặt môi trường
Yêu cầu máy tính đã cài đặt **Python 3.10** trở lên. Mở terminal tại thư mục dự án và chạy:

```bash
# Cài đặt thư viện Flask siêu nhẹ
pip install -r requirements.txt
```

### 3.2. Khởi chạy Giao diện Web Visualizer
Chỉ cần chạy lệnh sau, chương trình sẽ tự động bật server và mở trình duyệt:

```bash
python main.py
```
*(Hoặc truy cập trực tiếp bằng trình duyệt tại: `http://localhost:5000`)*

### 3.3. Chạy Benchmark đo đạc thời gian & bộ nhớ
Để chạy kiểm thử tự động toàn bộ các file trong thư mục `inputs/` và xuất kết quả ra file CSV:

```bash
python main.py --benchmark
```

### 3.4. Sinh thêm file testcase mới
```bash
# Sinh bàn cờ kích thước 5x5 mới vào inputs/
python main.py --generate 5
```

---

## 👥 4. Phân công công việc (Team Work Division: 50% - 50%)

| Nhiệm vụ | Thành viên 1 | Thành viên 2 |
| :--- | :--- | :--- |
| **Họ và tên / MSSV** | *(Điền thông tin TV1)* | *(Điền thông tin TV2)* |
| **Trọng tâm phụ trách** | **Backend AI & Core Benchmark** | **Heuristic AI & Web Visualizer** |
| **Modules mã nguồn** | - `src/pipe_constants.py`<br>- `src/board.py`<br>- `src/solver_base.py`<br>- `src/blind_search.py` (DFS)<br>- `src/generator.py`<br>- `src/benchmark.py` | - `src/heuristic_search.py` (A*)<br>- `app.py` (Flask server)<br>- `templates/index.html`<br>- `static/css/style.css`<br>- `static/js/app.js` |
| **Nội dung Báo cáo PDF** | - **Phần 1:** Mô hình hóa bài toán (State, Actions, Goal Test, Bitmask)<br>- **Phần 4:** Bảng số liệu thực nghiệm, vẽ biểu đồ & nhận xét chuyên sâu | - **Phần 2:** Cấu trúc mã nguồn, phân tích nguyên lý $A^*$ vs DFS, chứng minh $h(n)$ Admissible<br>- **Phần 3:** Chụp ảnh demo step-by-step & giao diện Web |
| **Thuyết trình** | Soạn nội dung phần Mô hình hóa & Đánh giá thực nghiệm | Thiết kế **Slide thuyết trình** (.pptx / .pdf), chuẩn bị kịch bản demo |

---

## 🤝 5. Hướng dẫn phối hợp qua Git

1. **Khởi tạo và đẩy lên GitHub:**
   ```bash
   git init
   git add .
   git commit -m "feat: initialize Puzzle Pipes AI skeleton with Flask and Solvers"
   git branch -M main
   git remote add origin <URL_REPO_CUA_BAN>
   git push -u origin main
   ```
2. **Quy tắc làm việc theo nhánh:**
   - Thành viên 1 làm việc trên nhánh: `git checkout -b feature/tv1-blind-benchmark`
   - Thành viên 2 làm việc trên nhánh: `git checkout -b feature/tv2-heuristic-ui`
   - Khi hoàn thành tính năng, tạo Pull Request để review và merge vào `main`.

---

## 📄 6. Cấu trúc Báo cáo PDF & Hồ sơ nộp bài
Theo đúng quy định đề bài, nhóm cần chuẩn bị:
1. **1 File Báo cáo `.pdf`** gồm đủ 4 phần:
   - *Phần 1:* Mô tả bài toán và mô hình hóa bài toán.
   - *Phần 2:* Cấu trúc code và hiện thực giải thuật (DFS, $A^*$, đo đạc).
   - *Phần 3:* Demo trực quan (ảnh chụp Web Visualizer từng bước).
   - *Phần 4:* Bảng số liệu thực nghiệm (Thời gian ms, RAM KB, Nodes) và nhận xét.
2. **1 File Slide thuyết trình** (`.pptx` hoặc `.pdf`) để bảo vệ trước lớp.
3. **Mã nguồn hoàn chỉnh** đóng gói trong file `.zip`.

