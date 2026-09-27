# 🧮 PyQt6 Calculator - Bài tập nhóm 8 - Nhóm Python_CT02

Dự án này bao gồm 2 phần chính:
- **`vibe_code_calculator`**: Chứa toàn bộ source code của ứng dụng máy tính desktop đầy đủ tính năng, được xây dựng bằng **Python 3.10+** và **PyQt6**, với kiến trúc MVC rõ ràng, hỗ trợ Dark/Light Mode, lịch sử phép tính, chế độ Scientific và bộ test pytest toàn diện.
- **`brute_code_calculator`**: Thư mục trống để chuẩn bị cho phần code thuật toán/tính toán mới sau này.

> **Lưu ý:** Ứng dụng trong `vibe_code_calculator` sử dụng PyQt6. Nếu hệ thống không cài được PyQt6, bạn có thể thay bằng PyQt5 (xem mục Cài đặt).

---

# vibe_code_calculator

## 📸 Giao diện

```
┌─────────────────────────────────────┐
│  STANDARD    SCI  🕐  🌙           │  ← Toolbar
│  MC  MR  M+  M−  MS                │  ← Memory row
│  ┌─────────────────────────────┐   │
│  │  12 + 8 × 2 - 5 / 2        │   │  ← Biểu thức (nhỏ)
│  │                      25.5   │   │  ← Kết quả (to, đậm)
│  └─────────────────────────────┘   │
│  [ % ]  [CE]  [C]   [⌫]             │
│  [¹/x]  [x²]  [√x]  [÷]             │
│  [ 7 ]  [ 8 ] [ 9 ] [×]             │
│  [ 4 ]  [ 5 ] [ 6 ] [−]             │
│  [ 1 ]  [ 2 ] [ 3 ] [+]             │
│  [ ± ]  [ 0 ] [ . ] [=]             │
└─────────────────────────────────────┘
```

**Dark Mode (mặc định):** Nền tối #1C1C1E, số trắng, nút = xanh accent #0A84FF  
**Light Mode:** Nền trắng/xám nhạt, thiết kế tối giản kiểu macOS

---

## ✨ Tính năng

### Phép tính cơ bản
- ✅ Cộng, Trừ, Nhân, Chia
- ✅ Biểu thức liên tiếp nhiều phép tính với **thứ tự ưu tiên đúng** (nhân/chia trước cộng/trừ)
- ✅ Dấu ngoặc `( )` để override thứ tự ưu tiên
- ✅ Lũy thừa `x^y` (kết hợp phải)

### Phép tính mở rộng
- ✅ Phần trăm `%`
- ✅ Căn bậc hai `√x`
- ✅ Bình phương `x²`
- ✅ Nghịch đảo `¹/x`
- ✅ Đổi dấu `±`
- ✅ Giai thừa `n!` (số nguyên không âm ≤ 170)
- ✅ Nút `C` (Clear all), `CE` (Clear entry), `⌫` (Backspace)
- ✅ Bộ nhớ: `MC`, `MR`, `M+`, `M−`, `MS`
- ✅ Lịch sử phép tính (panel ẩn/hiện)

### Chế độ Scientific
- ✅ `sin`, `cos`, `tan` (nhận độ, không phải radian)
- ✅ `asin`, `acos`, `atan`
- ✅ `log` (log₁₀), `ln` (log tự nhiên)
- ✅ Hằng số `π` và `e`

### Hiển thị số
- ✅ **KHÔNG GIỚI HẠN số lượng chữ số nhập vào**, màn hình tự động trượt/cuộn ngang (horizontal scroll) mượt mà khi số quá dài.
- ✅ Tối đa 12 chữ số thập phân cho phần thập phân, làm tròn hợp lý
- ✅ Tránh lỗi floating point kinh điển (0.1 + 0.2 = 0.3, không phải 0.30000000000000004)
- ✅ Tự động chuyển sang ký hiệu khoa học (VD: 1.23e+15) đối với kết quả siêu lớn
- ✅ Dấu phân cách hàng nghìn khi hiển thị (1,234,567)

### Xử lý lỗi
- ✅ Chia cho 0 → thông báo thân thiện
- ✅ √ số âm → lỗi rõ ràng
- ✅ Overflow → bắt và hiển thị thông báo
- ✅ Giai thừa số âm/thập phân → báo lỗi
- ✅ Biểu thức không hợp lệ → không crash
- ✅ Sau lỗi, nhập số tiếp theo → tự động reset

### UI/UX
- ✅ Dark Mode / Light Mode (toggle button)
- ✅ Resize cửa sổ, font co giãn tự động
- ✅ Phím tắt bàn phím đầy đủ
- ✅ History panel slide in/out với animation
- ✅ Copy kết quả: `Ctrl+C`
- ✅ Kích thước mặc định: 400×600, tối thiểu 360×520

---

## 🖥️ Yêu cầu hệ thống

| Thành phần | Yêu cầu |
|---|---|
| Python | 3.10 hoặc mới hơn |
| PyQt | PyQt6 6.7+ (hoặc PyQt5 5.15+) |
| OS | Windows 10/11, macOS 11+, Linux (Ubuntu 20.04+) |
| RAM | Tối thiểu 256 MB |

---

## 📦 Cài đặt

### 1. Clone dự án

```bash
git clone https://github.com/KemCheese/Project_python_calculator_PyQT.git
```

### 2. Tạo Virtual Environment (khuyến nghị)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

> **Nếu PyQt6 không cài được** (do thiếu Qt6 trên hệ thống):
> ```bash
> pip install PyQt5==5.15.11 pytest==8.3.3 pytest-qt==4.4.0
> ```
> Ứng dụng hỗ trợ cả PyQt5 và PyQt6 với `try/except import` tự động.

---

## ▶️ Chạy ứng dụng

```bash
# Từ thư mục gốc
python run.py

# Với debug logging
set CALC_DEBUG=1 && python run.py    # Windows
CALC_DEBUG=1 python run.py           # macOS/Linux

# Hoặc chạy trực tiếp module
python -m src.main
```

---

## 🧪 Chạy Tests

```bash
# Chạy toàn bộ test suite
pytest tests/ -v

# Chạy từng file test riêng
pytest tests/test_calculator_engine.py -v
pytest tests/test_validators.py -v

# Với coverage report
pip install pytest-cov
pytest tests/ -v --cov=src --cov-report=html
# Mở htmlcov/index.html để xem báo cáo
```

**Kết quả mong đợi:**
```
tests/test_calculator_engine.py::TestBasicOperations::test_addition_simple PASSED
tests/test_calculator_engine.py::TestOperatorPrecedence::test_multiplication_before_addition PASSED
...
========================= 85 passed in 0.45s =========================
```

---

## 📦 Build file thực thi (PyInstaller)

### Cài đặt PyInstaller

```bash
pip install pyinstaller
```

### Build

```bash
# Windows (.exe)
pyinstaller --onefile --windowed --name "Calculator" --icon resources/icon.png run.py

# macOS (.app)
pyinstaller --onefile --windowed --name "Calculator" --icon resources/icon.icns run.py

# Linux (binary)
pyinstaller --onefile --name "Calculator" run.py
```

### Thêm resources vào bundle

Tạo file `calculator.spec` (sau khi chạy pyinstaller lần đầu) và thêm:

```python
# Trong calculator.spec
a = Analysis(
    ['run.py'],
    ...
    datas=[
        ('src/ui/styles.qss', 'src/ui'),
        ('resources/', 'resources'),
    ],
    ...
)
```

Sau đó build:
```bash
pyinstaller calculator.spec
```

File thực thi xuất hiện trong thư mục `dist/`.

---

## 📁 Cấu trúc dự án

```
prj_python/
├── README.md                    # Tài liệu chính của dự án
├── .gitignore                   # Cấu hình git
├── brute_code_calculator/       # Thư mục trống dành cho code tương lai
└── vibe_code_calculator/        # Source code máy tính PyQt6
    ├── src/
    │   ├── main.py                  # Entry point (QApplication, logging, font setup)
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── calculator_engine.py # Shunting-Yard parser, evaluator, formatter
    │   │   └── history_manager.py   # Lịch sử phép tính, callback pattern
    │   ├── ui/
    │   │   ├── __init__.py
    │   │   ├── main_window.py       # QMainWindow, button grid, keyboard handling
    │   │   ├── styles.qss           # Dark/Light theme stylesheet (placeholder-based)
    │   │   └── widgets/
    │   │       ├── __init__.py
    │   │       └── history_panel.py # QWidget lịch sử, slide animation
    │   └── utils/
    │       ├── __init__.py
    │       └── validators.py        # Input validation, display↔compute conversion
    ├── tests/
    │   ├── __init__.py
    │   ├── test_calculator_engine.py  # 85+ test cases
    │   └── test_validators.py         # 40+ test cases
    ├── resources/
    │   └── icon.png                 # (tùy chọn) Icon ứng dụng
    ├── requirements.txt
    ├── LICENSE
    └── run.py                       # Script chạy nhanh từ thư mục này
```

---

## ⌨️ Phím tắt

| Phím | Chức năng |
|---|---|
| `0` - `9` | Nhập số |
| `.` | Dấu chấm thập phân |
| `+` | Cộng |
| `-` | Trừ |
| `*` | Nhân |
| `/` | Chia |
| `%` | Phần trăm |
| `(` `)` | Dấu ngoặc |
| `Enter` hoặc `=` | Tính kết quả |
| `Backspace` | Xóa ký tự cuối |
| `Escape` | Xóa tất cả (C) |
| `Delete` | Xóa entry (CE) |
| `Ctrl+C` | Copy kết quả vào clipboard |
| `Ctrl+H` | Ẩn/hiện lịch sử phép tính |
| `Ctrl+S` | Ẩn/hiện chế độ Scientific |

---

## 🏗️ Kiến trúc

```
Input (Button/Keyboard)
        │
        ▼
InputValidator (utils/validators.py)
  - Chặn ký tự không hợp lệ
  - Validate dấu ngoặc
  - Chuyển display ↔ compute
        │
        ▼
CalculatorEngine (core/calculator_engine.py)
  1. Tokenize → danh sách Token
  2. Shunting-Yard → RPN (Reverse Polish Notation)
  3. Evaluate RPN bằng stack
  ✗ KHÔNG dùng eval() - an toàn hoàn toàn
        │
        ▼
HistoryManager (core/history_manager.py)
  - Lưu HistoryEntry (expression, result, timestamp)
  - Callback pattern thông báo UI
        │
        ▼
MainWindow + HistoryPanel (ui/)
  - Hiển thị kết quả
  - Dark/Light theme qua QSS
```

---

## 🔐 Bảo mật

Ứng dụng **KHÔNG sử dụng `eval()`** trên input của người dùng. Thay vào đó:
1. **Tokenizer** tách biểu thức thành danh sách token an toàn
2. **Shunting-Yard** chuyển sang RPN (chỉ xử lý số và toán tử đã được xác thực)
3. **RPN Evaluator** tính kết quả theo stack, không thực thi code Python tùy ý

---


## 📄 License

Dự án sử dụng **MIT License** - xem file [LICENSE](LICENSE).

---

# brute_code_calculator

## 📌 Tổng quan: Simple Calculator (Máy tính code tay)

Dự án này là một phiên bản máy tính siêu gọn nhẹ, đáp ứng các tiêu chuẩn tối ưu về UX/UI và xử lý thuật toán an toàn.

**1. Mục tiêu & Tính năng:**
- Gói gọn toàn bộ mã nguồn trong **1 file duy nhất**.
- Hỗ trợ đầy đủ các phép tính cơ bản: `+`, `-`, `*`, `/`, `%`, `luỹ thừa (^)`, `căn bậc (√)`, `1/x`, phím thập phân (`.`) cùng các số 0-9.
- Hỗ trợ nhập liệu linh hoạt qua **nút bấm trên UI** và gõ trực tiếp từ **bàn phím cứng** (nhấn `Enter` để tính).

**2. Giao diện & Trải nghiệm (UI/UX):**
- Sử dụng **PyQt6**, giao diện được tách biệt rõ ràng giữa màn hình nhập liệu và lưới bàn phím.
- **Tự động giãn nở (Auto-Expanding):** Các nút bấm tự động chia đều khoảng cách lấp đầy màn hình nhờ `QSizePolicy`, đảm bảo không bao giờ bị lệch. Cửa sổ được cố định kích thước (Fixed Size).
- **Mô phỏng chuẩn Windows Calculator:** 
  - Số nguyên hoặc thập phân phổ thông hiển thị bình thường.
  - Tự động cắt gọt (trim) các số `0` dư thừa ở đuôi (ví dụ `1.200` thành `1.2`).
  - Triệt tiêu lỗi floating point kinh điển của Python (`0.1 + 0.2` sẽ bằng `0.3` thay vì `0.30000000000000004`).
  - **Tự động chuyển dạng số e (Scientific Notation)** nếu số quá lớn (`>= 1e16`) hoặc quá nhỏ (`< 1e-15`). Số mũ của dạng `e` cũng được căn chỉnh gọn gàng y hệt Windows (ví dụ `e+6` thay vì `e+06`).

**3. Quản lý luồng, Bắt lỗi & Hiệu năng (RAM/Threads):**
- **Bảo mật tuyệt đối với `eval()`:** Vô hiệu hóa `__builtins__`, chỉ cấp quyền truy cập `math.sqrt` để tránh mọi nguy cơ Injection mà không cần phải tự viết Parser cồng kềnh.
- **Bắt lỗi Input thân thiện:** Nếu người dùng gõ sai các ký tự lạ (gây `NameError`), quên đóng ngoặc (app tự động bù), tính căn số âm (`ValueError`), hoặc chia cho 0, hệ thống sẽ bật hộp thoại log lỗi. Đặc biệt, **nội dung bị nhập sai vẫn giữ nguyên trên màn hình** để người dùng có thể tự dùng Backspace (`⌫`) sửa lại, không làm gián đoạn trải nghiệm (không xóa sạch).
- **Luồng & RAM:** Mọi phép tính cực kỳ nhẹ, thực thi trực tiếp trên Main Thread mà không hề gây treo/kẹt luồng giao diện. Trình dọn rác (GC) của Python hoàn toàn làm chủ việc giải phóng các biến tạm nên không rò rỉ bộ nhớ.

*Thư mục chứa mã nguồn: `brute_code_calculator/simple_calculator.py`*
