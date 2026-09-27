# 🧮 PyQt6 Calculator - Bài tập nhóm 8 - Nhóm Python_CT02

Dự án này bao gồm 2 phiên bản máy tính:
- **`vibe_code_calculator`**: Phiên bản nâng cao, chia module MVC rõ ràng, hỗ trợ nhiều chế độ và tính năng phức tạp.
- **`brute_code_calculator`**: Phiên bản code tay cơ bản, xử lý logic gọn nhẹ trong 1 file duy nhất.

---

## 📦 Cài đặt (Dành cho cả 2 phiên bản)

### 1. Clone dự án

```bash
git clone https://github.com/KemCheese/Project_python_calculator_PyQT.git
cd Project_python_calculator_PyQT
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

> **Lưu ý:** Cả 2 ứng dụng đều sử dụng PyQt6. Nếu hệ thống không cài được PyQt6 (ví dụ thiếu Qt6), bạn có thể fallback bằng PyQt5:
> ```bash
> pip install PyQt5==5.15.11 pytest==8.3.3 pytest-qt==4.4.0
> ```

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

## ✨ Tính năng

### Phép tính cơ bản & Mở rộng
- ✅ Cộng, Trừ, Nhân, Chia, Lũy thừa `x^y`, Phần trăm `%`, Căn bậc hai `√x`, Bình phương `x²`, Nghịch đảo `¹/x`, Đổi dấu `±`, Giai thừa `n!`.
- ✅ Biểu thức liên tiếp nhiều phép tính với **thứ tự ưu tiên đúng** và hỗ trợ dấu ngoặc `( )`.
- ✅ Bộ nhớ: `MC`, `MR`, `M+`, `M−`, `MS`.
- ✅ Lịch sử phép tính (panel ẩn/hiện).

### Chế độ Scientific
- ✅ Lượng giác (`sin`, `cos`, `tan`, `asin`, `acos`, `atan` - nhận độ).
- ✅ Logarit (`log`, `ln`) và Hằng số `π`, `e`.

### Hiển thị số & Xử lý lỗi
- ✅ KHÔNG GIỚI HẠN chữ số nhập vào, tự động cuộn ngang.
- ✅ Tối đa 12 chữ số thập phân, tự động chuyển sang ký hiệu khoa học (VD: 1.23e+15).
- ✅ Tránh lỗi floating point kinh điển (0.1 + 0.2 = 0.3).
- ✅ Bắt lỗi đầy đủ: Chia 0, tràn số (overflow), căn số âm, v.v. và thông báo thân thiện.

## ▶️ Chạy ứng dụng

```bash
# Từ thư mục gốc
python run.py
```

## 🧪 Chạy Tests

```bash
pytest tests/ -v
```

## ⌨️ Phím tắt

| Phím | Chức năng |
|---|---|
| `0`-`9`, `.`, `+`, `-`, `*`, `/`, `%`, `(`, `)` | Nhập liệu cơ bản |
| `Enter` hoặc `=` | Tính kết quả |
| `Backspace` / `Escape` / `Delete` | Xóa (⌫ / C / CE) |
| `Ctrl+C` | Copy kết quả vào clipboard |
| `Ctrl+H` / `Ctrl+S` | Ẩn/hiện Lịch sử / Chế độ Scientific |

## 🏗️ Kiến trúc

```
Input (Button/Keyboard)
        │
        ▼
InputValidator (utils/validators.py)
        │
        ▼
CalculatorEngine (core/calculator_engine.py)
  - Tokenize → Shunting-Yard → RPN Evaluator
  - KHÔNG dùng eval() - an toàn tuyệt đối
        │
        ▼
HistoryManager (core/history_manager.py)
        │
        ▼
MainWindow + HistoryPanel (ui/)
```

---

# brute_code_calculator

## 📸 Giao diện

Ứng dụng được thiết kế tối giản trong một cửa sổ cố định, tập trung vào trải nghiệm nhập liệu:
- **Màn hình hiển thị (Top):** Căn lề phải, hỗ trợ cuộn ngang mượt mà khi biểu thức dài.
- **Bàn phím (Bottom):** Bố cục lưới (Grid) tràn viền tự động giãn nở (Auto-Expanding) cân đối, không bao giờ bị lệch UI.
- Có đầy đủ các nút từ `0-9`, toán tử cơ bản, cùng 2 nút chức năng mở rộng `C` (Xóa tất cả) và `⌫` (Backspace).

## ✨ Tính năng

### Phép tính được hỗ trợ
- ✅ **Cơ bản:** Cộng `+`, Trừ `-`, Nhân `*`, Chia `/`, Modulo `%`.
- ✅ **Mở rộng:** Lũy thừa `^`, Căn bậc hai `√`, Nghịch đảo `1/x`.
- ✅ **Nhập liệu linh hoạt:** Chấp nhận input từ click chuột hoặc gõ trực tiếp từ **bàn phím cứng** máy tính.

### Hiển thị số 
- ✅ Số nguyên hoặc thập phân phổ thông hiển thị bình thường.
- ✅ Tự động cắt gọt (trim) các số `0` dư thừa ở đuôi (ví dụ `1.200` thành `1.2`).
- ✅ Giải quyết triệt để lỗi floating point của Python (`0.1 + 0.2 = 0.3`).
- ✅ **Tự động chuyển dạng số e (Scientific Notation)** nếu kết quả quá lớn (`>= 1e16`) hoặc cực kỳ nhỏ (`< 1e-15`), giữ giao diện luôn gọn gàng và không bị mất độ chính xác.

## ▶️ Chạy ứng dụng

```bash
# Từ thư mục gốc (đảm bảo đã kích hoạt .venv)
python "brute_code_calculator/simple_calculator.py"
```

## ⌨️ Phím tắt

| Phím | Chức năng |
|---|---|
| `0`-`9`, `.`, `+`, `-`, `*`, `/`, `%`, `^` | Nhập liệu cơ bản từ bàn phím |
| `Enter` | Tính kết quả |
| `Backspace` | Xóa ký tự cuối (⌫) |

## 🏗️ Kiến trúc

```
Input (Nút bấm hoặc Bàn phím cứng)
        │
        ▼
Sự kiện textEdited / clicked
  - Tự động khôi phục biểu thức nếu màn hình đang báo lỗi
        │
        ▼
Calculator (simple_calculator.py)
  - Thay thế chuỗi hiển thị thành cú pháp Python (^ thành **)
  - Tự động bù dấu ngoặc đóng nếu người dùng quên đóng ngoặc cho hàm căn
        │
        ▼
Evaluator
  - Chạy eval() trong môi trường cách ly an toàn
  - Xử lý trực tiếp trên Main Thread (luồng UI) với chi phí O(1), không kẹt RAM
        │
        ▼
Formatter
  - Căn chỉnh dạng số e, loại bỏ các số vô nghĩa
  - Cập nhật kết quả cuối cùng hoặc log lỗi lên UI
```
