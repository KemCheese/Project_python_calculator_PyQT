import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, 
    QLineEdit, QPushButton, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class SimpleCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        # 1. Khởi tạo UI (Giao diện) - UX tách biệt, không đè nhau
        self.setWindowTitle("Máy tính code tay ")
        self.setFixedSize(400, 500) # Cố định kích thước để đảm bảo UI luôn hiển thị tốt
        self.setup_ui()

    def setup_ui(self):
        # Widget trung tâm chứa toàn bộ layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        # Layout chính dạng dọc (Dọc: Màn hình ở trên, bàn phím ở dưới)
        main_layout = QVBoxLayout(central_widget)
        
        # --- PHẦN MÀN HÌNH HIỂN THỊ (INPUT VÔ HẠN) ---
        # QLineEdit cho phép nhập chuỗi dài vô hạn, tự động cuộn ngang (scroll) mượt mà
        self.display = QLineEdit()
        self.display.returnPressed.connect(lambda: self.calculate_result(self.display.text())) # Kích hoạt tính khi gõ phím Enter
        # (Không cài read-only nữa để cho phép người dùng gõ từ bàn phím cứng)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight) # Căn phải giống máy tính thật
        self.display.setFont(QFont("Arial", 24))
        self.display.setStyleSheet("background-color: #f0f0f0; color: black; padding: 10px; border-radius: 5px;")
        main_layout.addWidget(self.display)
        
        # --- PHẦN BÀN PHÍM (BUTTONS) ---
        grid_layout = QGridLayout()
        
        # Bố cục lưới: hiển thị đúng các nút được yêu cầu
        # Thêm nút C (Clear) để xóa toàn bộ, ⌫ (Backspace) để xóa từng chữ
        buttons = [
            ('C', 0, 0, 1, 2), ('⌫', 0, 2, 1, 2), # Hàng 0: Nút chức năng (chia đều 4 cột)
            ('1/x', 1, 0), ('√', 1, 1), ('^', 1, 2), ('/', 1, 3),  # Hàng 1: Các phép tính đặc biệt
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('*', 2, 3),     # Hàng 2: Số và nhân
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3),     # Hàng 3: Số và trừ
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('+', 4, 3),     # Hàng 4: Số và cộng
            ('%', 5, 0), ('0', 5, 1), ('.', 5, 2), ('=', 5, 3),     # Hàng 5: Số và các dấu còn lại
        ]
        
        # Vòng lặp tạo nút UI
        for btn_data in buttons:
            text = btn_data[0]
            btn = QPushButton(text)
            btn.setFont(QFont("Arial", 16))
            btn.setStyleSheet("color: black;")
            # Cho phép nút giãn nở và chia đều kích thước bởi Grid (thay vì fixed dễ bị lệch margin)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setMinimumHeight(60)
            
            if len(btn_data) == 3:
                grid_layout.addWidget(btn, btn_data[1], btn_data[2])
            else:
                grid_layout.addWidget(btn, btn_data[1], btn_data[2], btn_data[3], btn_data[4])
                
            # Gắn sự kiện (Event) vào nút bấm
            # Dùng lambda với x=text để bind (ràng buộc) giá trị của mỗi nút vào sự kiện click
            btn.clicked.connect(lambda checked, x=text: self.on_button_click(x))
                
        main_layout.addLayout(grid_layout)

    def on_button_click(self, char):
        """
        Xử lý khi người dùng nhấn nút.
        Tại sao dùng cái này: Giúp cập nhật màn hình hiển thị ngay lập tức khi bấm nút.
        """
        current_text = self.display.text()
        
        if char == 'C':
            self.display.clear() # Xóa hết
        elif char == '⌫':
            self.display.setText(current_text[:-1]) # Xóa 1 ký tự cuối
        elif char == '=':
            # Bắt đầu tính toán
            self.calculate_result(current_text)
        elif char == '1/x':
            self.display.setText(current_text + '1/')
        elif char == '√':
            self.display.setText(current_text + 'sqrt(')
        else:
            # Cứ nối chuỗi các nút khác (+, -, số, dấu chấm...)
            self.display.setText(current_text + char)

    def calculate_result(self, expression):
        """
        Lõi tính toán và bắt lỗi.
        Giải thích thuật toán: Chuyển biểu thức chuỗi sang dạng hiểu được của Python
        và tính toán an toàn bằng hàm eval bị giới hạn.
        Tránh được việc viết thuật toán parser phức tạp nhưng vẫn đảm bảo tính an toàn
        vì đã chặn các thư viện tích hợp (__builtins__).
        Không gây kẹt luồng vì các phép tính này O(1) hoặc cực kỳ nhanh.
        """
        if not expression:
            return

        # 1. BẮT LỖI INPUT
        # Xử lý các phép toán đặc biệt thành dạng Python hiểu được
        safe_expression = expression.replace('^', '**') # Lũy thừa trong Python là **
        
        # Bắt lỗi người dùng quên đóng ngoặc cho hàm căn bậc (sqrt)
        open_brackets = safe_expression.count('(')
        close_brackets = safe_expression.count(')')
        if open_brackets > close_brackets:
            safe_expression += ')' * (open_brackets - close_brackets)

        # 2. TÍNH TOÁN VÀ BẮT LỖI TÍNH TOÁN
        try:
            # Vô hiệu hóa __builtins__ để chặn injection (bảo mật), chỉ cho phép xài math.sqrt
            allowed_names = {
                "__builtins__": None, 
                "sqrt": math.sqrt
            }
            
            # Tính bằng eval
            result = eval(safe_expression, allowed_names)
            
            # Format kết quả
            self.display.setText(self.format_result(result))
            
        except ZeroDivisionError:
            self.show_error("Lỗi tính toán: Không thể chia cho 0!")
        except ValueError:
            self.show_error("Lỗi tính toán: Phép tính không hợp lệ (Ví dụ: căn bậc số âm)!")
        except SyntaxError:
            self.show_error("Lỗi Input: Sai cú pháp biểu thức!")
        except TypeError:
            self.show_error("Lỗi Input: Dữ liệu nhập sai kiểu!")
        except NameError:
            self.show_error("Lỗi Input: Có chứa ký tự chữ cái không hợp lệ từ bàn phím!")
        except Exception as e:
            # Bắt tất cả lỗi còn lại để app không bao giờ kẹt hay văng
            self.show_error(f"Lỗi không xác định: {str(e)}")

    def format_result(self, number):
        """
        Định dạng kết quả mô phỏng chuẩn logic của Windows Calculator:
        - Số nguyên hiển thị bình thường.
        - Số quá lớn (>= 1e16) hoặc quá nhỏ (khác 0 và < 1e-15) dùng dạng e.
        - Lược bỏ số 0 thừa và căn chỉnh số mũ.
        - Xử lý được các lỗi sai số dấu phẩy động (như 0.1 + 0.2 = 0.3).
        """
        if number == 0:
            return "0"
            
        abs_num = abs(number)
        
        # Windows Calc chuyển dạng 'e' khi >= 1e16 hoặc số rất nhỏ để không mất hiển thị
        if abs_num >= 1e16 or abs_num < 1e-15:
            # Định dạng số e với 15 chữ số sau phẩy để lấy max độ chính xác
            formatted = f"{number:.15e}"
            mantissa, exponent = formatted.split('e')
            
            # Cắt bỏ các số 0 thừa ở đuôi (ví dụ: 1.23000 -> 1.23)
            if '.' in mantissa:
                mantissa = mantissa.rstrip('0').rstrip('.')
                
            # Chuẩn hóa phần số mũ (ví dụ e+06 -> e+6 giống hệt Windows)
            exp_sign = exponent[0]
            exp_val = str(int(exponent[1:]))
            
            return f"{mantissa}e{exp_sign}{exp_val}"
        else:
            # Nếu là số nguyên nằm trong giới hạn
            if isinstance(number, float) and number.is_integer():
                return str(int(number))
                
            # Định dạng thập phân, cố định max 15 chữ số để triệt tiêu lỗi floating point
            formatted = f"{number:.15f}"
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
                
            # Nếu cắt hết số 0 mà trở thành trống trơn ở phần thập phân thì nó là nguyên
            if not formatted:
                return "0"
            return formatted
            
    def show_error(self, message):
        """
        Tách biệt logic hiển thị lỗi ra hàm riêng để đảm bảo UX không đè lên UI nhập liệu.
        Sử dụng hộp thoại QMessageBox.
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Phát hiện lỗi")
        msg_box.setText(message)
        msg_box.exec()
        # Không xóa màn hình (self.display.clear()) để user có thể nhấn ⌫ và sửa lại chỗ nhập sai

if __name__ == "__main__":
    # QApplication quản lý vòng đời ứng dụng và event loop.
    # Event Loop giúp bắt các sự kiện (click) và render mượt mà, ngăn kẹt RAM
    app = QApplication(sys.argv)
    window = SimpleCalculator()
    window.show()
    sys.exit(app.exec())
